package com.dynasty.cod3;

import com.dynasty.Dynasty;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.event.entity.*;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.*;

/** Secret 12 is independent of the combat and NPC quest registries. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID,bus=Mod.EventBusSubscriber.Bus.MOD)
public final class WhiteDeerContent {
    public static final DeferredRegister<EntityType<?>> ENTITIES=DeferredRegister.create(ForgeRegistries.ENTITY_TYPES,Dynasty.MODID);
    public static final DeferredRegister<Item> ITEMS=DeferredRegister.create(ForgeRegistries.ITEMS,Dynasty.MODID);
    public static final RegistryObject<EntityType<WhiteDeerEntity>> DEER=ENTITIES.register("white_deer",()->EntityType.Builder.of(WhiteDeerEntity::new,MobCategory.CREATURE).sized(.65f,1.55f).clientTrackingRange(8).build("white_deer"));
    public static final RegistryObject<Item> EGG=ITEMS.register("white_deer_spawn_egg",()->new ForgeSpawnEggItem(DEER,0xffffff,0x81956d,new Item.Properties()));
    public static final RegistryObject<Item> TOKEN=ITEMS.register("white_deer_token",()->new WhiteDeerSanctuary.Pass(new Item.Properties().stacksTo(1)));
    public static final ResourceKey<Level> SANCTUARY=ResourceKey.create(Registries.DIMENSION,new ResourceLocation(Dynasty.MODID,"white_deer_grotto"));
    @SubscribeEvent public static void attributes(EntityAttributeCreationEvent e){e.put(DEER.get(),WhiteDeerEntity.attributes().build());}
    @SubscribeEvent public static void placements(SpawnPlacementRegisterEvent e){e.register(DEER.get(),SpawnPlacements.Type.ON_GROUND,Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
            (t,l,reason,pos,r)->reason!=MobSpawnType.CHUNK_GENERATION&&(reason!=MobSpawnType.NATURAL||l instanceof net.minecraft.server.level.ServerLevel s&&WhiteDeerEntity.habitat(s,pos)),SpawnPlacementRegisterEvent.Operation.REPLACE);}
    private WhiteDeerContent(){}
}
