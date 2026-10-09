package com.dynasty.expansion;

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
        new Spec("famished_refugee","human",40.0,60.0,0.22,0.0,0.6F,1.8F,true,false,false),
        new Spec("bandit_thug","human",80.0,200.0,0.28,6.0,0.6F,1.8F,false,false,false),
        new Spec("night_watchman","human",90.0,160.0,0.25,8.0,0.6F,1.8F,true,false,false),
        new Spec("swindler","human",50.0,80.0,0.24,0.0,0.6F,1.8F,true,false,false),
        new Spec("herb_picker","human",60.0,70.0,0.24,0.0,0.6F,1.8F,true,false,false),
        new Spec("red_fox","beast",70.0,150.0,0.34,4.0,0.9F,0.85F,false,false,false),
        new Spec("gray_wolf","beast",90.0,180.0,0.32,6.0,0.9F,0.85F,false,false,false),
        new Spec("wild_boar","beast",120.0,220.0,0.3,8.0,0.9F,0.85F,false,false,false),
        new Spec("giant_python","beast",140.0,240.0,0.26,10.0,1.4F,0.55F,false,false,false),
        new Spec("golden_leopard","beast",110.0,260.0,0.4,6.0,0.9F,0.85F,false,false,false),
        new Spec("tree_spirit","beast",160.0,260.0,0.22,14.0,1.2F,2.2F,false,false,false),
        new Spec("stone_sprite","beast",180.0,240.0,0.2,18.0,0.9F,0.85F,false,false,false),
        new Spec("lantern_ghost","ghost",80.0,180.0,0.28,2.0,0.65F,1.5F,false,true,false),
        new Spec("paper_cut_child","human",60.0,120.0,0.3,0.0,0.6F,1.8F,false,false,false),
        new Spec("river_imp","water",90.0,180.0,0.26,6.0,0.8F,1.1F,false,false,true),
        new Spec("drowning_ghost","water",100.0,200.0,0.24,4.0,0.8F,1.1F,false,false,true),
        new Spec("carp_spirit","water",80.0,160.0,0.28,4.0,0.8F,1.1F,false,false,true),
        new Spec("snail_maiden","water",70.0,70.0,0.2,6.0,0.8F,1.1F,true,false,true),
        new Spec("crab_soldier","water",130.0,220.0,0.24,16.0,0.8F,1.1F,false,false,true),
        new Spec("bat_demon","fly",70.0,160.0,0.34,2.0,0.7F,0.6F,false,true,false),
        new Spec("jingwei_bird","fly",40.0,60.0,0.36,0.0,0.7F,0.6F,true,true,false),
        new Spec("gray_falcon","fly",60.0,140.0,0.42,2.0,0.7F,0.6F,false,true,false),
        new Spec("locust_swarm","fly",50.0,80.0,0.3,0.0,1.3F,1.1F,false,true,false),
        new Spec("corpse_beetle","bug",60.0,140.0,0.26,8.0,0.9F,0.5F,false,false,false),
        new Spec("venom_scorpion","bug",110.0,200.0,0.26,10.0,0.9F,0.5F,false,false,false),
        new Spec("stone_worm","bug",160.0,240.0,0.2,14.0,1.4F,0.55F,false,false,false),
        new Spec("paper_money_ghost","ghost",60.0,120.0,0.26,0.0,0.65F,1.5F,false,true,false),
        new Spec("wandering_spirit","ghost",70.0,140.0,0.24,0.0,0.65F,1.5F,false,true,false),
        new Spec("wooden_magpie","fly",80.0,150.0,0.32,8.0,0.7F,0.6F,false,true,false),
        new Spec("clockwork_rat","beast",60.0,100.0,0.34,6.0,0.6F,0.45F,false,false,false));
    public static final DeferredRegister<EntityType<?>> ENTITIES=DeferredRegister.create(ForgeRegistries.ENTITY_TYPES,Dynasty.MODID);
    public static final RegistryObject<EntityType<SecondaryProjectile>> PROJECTILE=ENTITIES.register("secondary_skill_projectile",()->
        EntityType.Builder.<SecondaryProjectile>of(SecondaryProjectile::new,MobCategory.MISC).sized(.3F,.3F).clientTrackingRange(6).updateInterval(1).build("secondary_skill_projectile"));
    private static final Spec SHRIMP_SPEC=new Spec("shrimp_soldier","water",120,180,.26,12,.65F,1.25F,false,false,true);
    public static final RegistryObject<EntityType<SecondaryMob>> SHRIMP=ENTITIES.register("shrimp_soldier",()->
        EntityType.Builder.<SecondaryMob>of((type,level)->new SecondaryMob.Hostile(type,level,SHRIMP_SPEC),MobCategory.MISC)
            .sized(SHRIMP_SPEC.width(),SHRIMP_SPEC.height()).clientTrackingRange(8).updateInterval(3).build("shrimp_soldier"));
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
        bus.addListener((EntityAttributeCreationEvent e)->e.put(SHRIMP.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,SHRIMP_SPEC.health())
            .add(Attributes.ATTACK_DAMAGE,SHRIMP_SPEC.damage()).add(Attributes.MOVEMENT_SPEED,SHRIMP_SPEC.speed()).add(Attributes.ARMOR,SHRIMP_SPEC.armor()).add(Attributes.FOLLOW_RANGE,16).build()));
    }
    private SecondaryMobs() { }
}
