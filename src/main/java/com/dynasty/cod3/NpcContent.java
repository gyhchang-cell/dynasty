package com.dynasty.cod3;

import com.dynasty.Dynasty;
import net.minecraft.world.entity.*;
import net.minecraft.world.item.*;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.*;
import java.util.*;

@Mod.EventBusSubscriber(modid=Dynasty.MODID,bus=Mod.EventBusSubscriber.Bus.MOD)
public final class NpcContent {
    public static final DeferredRegister<EntityType<?>> ENTITIES=DeferredRegister.create(ForgeRegistries.ENTITY_TYPES,Dynasty.MODID);
    public static final DeferredRegister<Item> ITEMS=DeferredRegister.create(ForgeRegistries.ITEMS,Dynasty.MODID);
    public static final Map<String,RegistryObject<EntityType<DynastyNpcEntity>>> NPCS=new LinkedHashMap<>();
    public static final List<RegistryObject<Item>> EGGS=new ArrayList<>();
    static {
        for(var row:Cod3Catalog.entries("npcs")){String role=row.getAsJsonObject().get("id").getAsString();
            var entity=ENTITIES.register("npc_"+role,()->EntityType.Builder.<DynastyNpcEntity>of((type,level)->new DynastyNpcEntity(type,level,role),MobCategory.CREATURE).sized(.65f,role.equals("xiaoyuanzi")?1.4f:1.9f).clientTrackingRange(6).build("npc_"+role));NPCS.put(role,entity);
            EGGS.add(ITEMS.register("npc_"+role+"_spawn_egg",()->new ForgeSpawnEggItem(entity,0x586b55,0xbb9870,new Item.Properties())));
        }
    }
    @SubscribeEvent public static void attributes(EntityAttributeCreationEvent e){for(var entity:NPCS.values())e.put(entity.get(),DynastyNpcEntity.attributes().build());}
    private NpcContent(){}
}
