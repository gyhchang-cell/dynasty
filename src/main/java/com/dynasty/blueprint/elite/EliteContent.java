package com.dynasty.blueprint.elite;

import com.dynasty.Dynasty;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.item.*;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.*;

public final class EliteContent {
    public static final DeferredRegister<EntityType<?>> ENTITIES=DeferredRegister.create(ForgeRegistries.ENTITY_TYPES,Dynasty.MODID);
    public static final DeferredRegister<Item> ITEMS=DeferredRegister.create(ForgeRegistries.ITEMS,Dynasty.MODID);
    public static final RegistryObject<EntityType<HeadlessGeneral>> HEADLESS=ENTITIES.register(HeadlessGeneral.ID,()->EntityType.Builder.<HeadlessGeneral>of(HeadlessGeneral::new,MobCategory.MONSTER).sized(1.1F,2.6F).clientTrackingRange(10).updateInterval(2).build(HeadlessGeneral.ID));
    public static final RegistryObject<Item> HEADLESS_EGG=ITEMS.register(HeadlessGeneral.ID+"_spawn_egg",()->new ForgeSpawnEggItem(HEADLESS,0x242C30,0x9FDCD3,new Item.Properties()));
    public static void register(IEventBus bus){ENTITIES.register(bus);ITEMS.register(bus);bus.addListener(EliteContent::attributes);}
    private static void attributes(EntityAttributeCreationEvent e){e.put(HEADLESS.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,180).add(Attributes.ATTACK_DAMAGE,9).add(Attributes.MOVEMENT_SPEED,.23).add(Attributes.ARMOR,12).add(Attributes.KNOCKBACK_RESISTANCE,.65).add(Attributes.FOLLOW_RANGE,28).build());}
    private EliteContent(){}
}
