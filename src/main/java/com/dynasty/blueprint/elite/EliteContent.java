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
    public static final RegistryObject<EntityType<GhostCarriageBird>> BIRD=ENTITIES.register(GhostCarriageBird.ID,()->EntityType.Builder.<GhostCarriageBird>of(GhostCarriageBird::new,MobCategory.MONSTER).sized(1.8F,1.9F).clientTrackingRange(12).updateInterval(2).build(GhostCarriageBird.ID));
    public static final RegistryObject<Item> BIRD_EGG=ITEMS.register(GhostCarriageBird.ID+"_spawn_egg",()->new ForgeSpawnEggItem(BIRD,0x442A2E,0xBE9696,new Item.Properties()));
    public static void register(IEventBus bus){ENTITIES.register(bus);ITEMS.register(bus);bus.addListener(EliteContent::attributes);}
    private static void attributes(EntityAttributeCreationEvent e){e.put(HEADLESS.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,180).add(Attributes.ATTACK_DAMAGE,9).add(Attributes.MOVEMENT_SPEED,.23).add(Attributes.ARMOR,12).add(Attributes.KNOCKBACK_RESISTANCE,.65).add(Attributes.FOLLOW_RANGE,28).build());
        e.put(BIRD.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,160).add(Attributes.ATTACK_DAMAGE,8).add(Attributes.MOVEMENT_SPEED,.2).add(Attributes.FLYING_SPEED,.32).add(Attributes.ARMOR,5).add(Attributes.KNOCKBACK_RESISTANCE,.35).add(Attributes.FOLLOW_RANGE,32).build());}
    private EliteContent(){}
}
