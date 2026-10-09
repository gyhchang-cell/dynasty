"""Generate the lightweight roster from the checked-in request; no natural spawn injection."""
from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[2]
text=(root/'docs/cod4/request.txt').read_text()
rows=[]
for line in text.splitlines():
    cells=[s.strip() for s in line.split('|')]
    if len(cells)!=13 or not cells[1].isdigit() or '/' not in cells[7]: continue
    n=int(cells[1]); stats=cells[7].split('/')
    if len(stats)!=4: continue
    rows.append(dict(index=n,name=cells[2],id=cells[3],family=cells[4],role=cells[5],shape=cells[6],health=float(stats[0]),damage=float(stats[1]),speed=float(stats[2]),armor=float(stats[3]),mechanism=cells[8],spawn=cells[9],drop=cells[10]))
assert len(rows)==30
(root/'docs/cod4/secondary-roster.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
neutral={'famished_refugee','night_watchman','swindler','herb_picker','snail_maiden','jingwei_bird'}
fly={'lantern_ghost','bat_demon','jingwei_bird','gray_falcon','locust_swarm','paper_money_ghost','wandering_spirit','wooden_magpie'}
aquatic={'river_imp','drowning_ghost','carp_spirit','snail_maiden','crab_soldier'}
sizes={'human':(.6,1.8),'beast':(.9,.85),'water':(.8,1.1),'fly':(.7,.6),'bug':(.9,.5),'ghost':(.65,1.5)}
lines=[]
for r in rows:
    id=r['id'];family='human' if r['index']<=5 or id=='paper_cut_child' else 'water' if id in aquatic else 'ghost' if id in {'lantern_ghost','paper_money_ghost','wandering_spirit'} else 'fly' if id in fly else 'bug' if 24<=r['index']<=26 else 'beast'
    width,height=sizes[family]
    if id=='tree_spirit':width,height=1.2,2.2
    if id in {'giant_python','stone_worm'}:width,height=1.4,.55
    if id=='clockwork_rat':width,height=.6,.45
    if id=='locust_swarm':width,height=1.3,1.1
    values=[f'"{id}"',f'"{family}"',str(r['health']),str(r['damage']),str(r['speed']),str(r['armor']),str(width)+'F',str(height)+'F',str(id in neutral).lower(),str(id in fly).lower(),str(id in aquatic).lower()]
    lines.append('        new Spec('+','.join(values)+')')
p=root/'src/main/java/com/dynasty/expansion/SecondaryMobs.java'
p.write_text('''package com.dynasty.expansion;

import com.dynasty.Dynasty;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraftforge.registries.*;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraft.world.item.Item;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import java.util.*;

public final class SecondaryMobs {
    public record Spec(String id,String family,double health,double damage,double speed,double armor,float width,float height,boolean neutral,boolean flying,boolean aquatic) { }
    public static final List<Spec> SPECS=List.of(
'''+',\n'.join(lines)+''');
    public static final DeferredRegister<EntityType<?>> ENTITIES=DeferredRegister.create(ForgeRegistries.ENTITY_TYPES,Dynasty.MODID);
    public static final Map<String,RegistryObject<EntityType<SecondaryMob>>> TYPES=new LinkedHashMap<>();
    static {
        for(var spec:SPECS) {
            var type=ENTITIES.register(spec.id(),()->EntityType.Builder.<SecondaryMob>of((t,l)->spec.neutral()?new SecondaryMob(t,l,spec):new SecondaryMob.Hostile(t,l,spec),spec.neutral()?MobCategory.CREATURE:MobCategory.MONSTER).sized(spec.width(),spec.height()).clientTrackingRange(8).updateInterval(3).build(spec.id()));
            TYPES.put(spec.id(),type);
            ExpansionContent.ITEMS.register(spec.id()+"_spawn_egg",()->new ForgeSpawnEggItem(type,0x645D4C,0xB5AB7C,new Item.Properties()));
        }
    }
    public static void bootstrap(IEventBus bus) {
        ENTITIES.register(bus);
        bus.addListener((EntityAttributeCreationEvent e)->SPECS.forEach(s->e.put(TYPES.get(s.id()).get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,s.health()).add(Attributes.ATTACK_DAMAGE,s.damage()).add(Attributes.MOVEMENT_SPEED,s.speed()).add(Attributes.ARMOR,s.armor()).add(Attributes.FOLLOW_RANGE,16).add(Attributes.FLYING_SPEED,s.speed()).add(Attributes.KNOCKBACK_RESISTANCE,s.id().equals("paper_cut_child")?1:0).build())));
    }
    private SecondaryMobs() { }
}
''')
