package com.dynasty.ritual;

import com.dynasty.Dynasty;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

@Mod.EventBusSubscriber(modid = Dynasty.MODID, bus = Mod.EventBusSubscriber.Bus.MOD)
public final class ZhenyuanBosses {
    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, Dynasty.MODID);
    public static final RegistryObject<EntityType<ZhenyuanSovereign>> FINAL_BOSS = ENTITIES.register("zhenyuan_sovereign",
            () -> EntityType.Builder.of(ZhenyuanSovereign::new, MobCategory.MONSTER)
                    .sized(1.8F, 4.2F).clientTrackingRange(12).fireImmune().build("zhenyuan_sovereign"));
    private ZhenyuanBosses() {}
    @SubscribeEvent public static void attributes(EntityAttributeCreationEvent event) {
        event.put(FINAL_BOSS.get(), ZhenyuanSovereign.attributes().build());
    }
}
