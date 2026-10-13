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
            int[] palette=com.dynasty.item.DynastyEggPalette.colors(role);
            EGGS.add(ITEMS.register("npc_"+role+"_spawn_egg",()->new ForgeSpawnEggItem(entity,palette[0],palette[1],new Item.Properties())));
        }
    }
    @SubscribeEvent public static void attributes(EntityAttributeCreationEvent e){for(var entity:NPCS.values())e.put(entity.get(),DynastyNpcEntity.attributes().build());}
    public static boolean wandering(String role){return Set.of("baibao_jin","sai_banxian","hong_ling").contains(role);}
    @Mod.EventBusSubscriber(modid=Dynasty.MODID)
    public static final class Lifecycle {
        @SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST)
        public static void death(net.minecraftforge.event.entity.living.LivingDeathEvent event){
            if(event.isCanceled()||!(event.getEntity() instanceof DynastyNpcEntity npc)||!wandering(npc.role)
                    ||!(npc.level() instanceof net.minecraft.server.level.ServerLevel level))return;
            var home=npc.getPersistentData().contains("cod3_home_anchor")?net.minecraft.core.BlockPos.of(npc.getPersistentData().getLong("cod3_home_anchor")):npc.home().below();
            if(level.hasChunkAt(home)&&level.getBlockEntity(home) instanceof StoryAnchor.Anchor anchor&&anchor.getBlockState().getValue(StoryAnchor.KIND)==StoryAnchor.npcState(npc.role).getValue(StoryAnchor.KIND))
                anchor.scheduleRespawn(level.getGameTime()+24000);
        }
    }
    private NpcContent(){}
}
