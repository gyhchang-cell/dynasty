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
    public static final DeferredRegister<net.minecraft.world.effect.MobEffect> EFFECTS=DeferredRegister.create(ForgeRegistries.MOB_EFFECTS,Dynasty.MODID);
    public static final RegistryObject<net.minecraft.world.effect.MobEffect> THREAD_NET=EFFECTS.register("mechanist_thread_net",MechanistNet::new);
    public static final RegistryObject<net.minecraft.world.effect.MobEffect> FOX_HAZE=EFFECTS.register("fox_haze",FoxHaze::new);
    public static final RegistryObject<EntityType<HeadlessGeneral>> HEADLESS=ENTITIES.register(HeadlessGeneral.ID,()->EntityType.Builder.<HeadlessGeneral>of(HeadlessGeneral::new,MobCategory.MONSTER).sized(5.4F,3.5F).clientTrackingRange(10).updateInterval(2).build(HeadlessGeneral.ID));
    public static final RegistryObject<Item> HEADLESS_EGG=ITEMS.register(HeadlessGeneral.ID+"_spawn_egg",()->new ForgeSpawnEggItem(HEADLESS,0x242C30,0x9FDCD3,new Item.Properties()));
    public static final RegistryObject<EntityType<GhostCarriageBird>> BIRD=ENTITIES.register(GhostCarriageBird.ID,()->EntityType.Builder.<GhostCarriageBird>of(GhostCarriageBird::new,MobCategory.MONSTER).sized(1.8F,1.9F).clientTrackingRange(12).updateInterval(2).build(GhostCarriageBird.ID));
    public static final RegistryObject<Item> BIRD_EGG=ITEMS.register(GhostCarriageBird.ID+"_spawn_egg",()->new ForgeSpawnEggItem(BIRD,0x442A2E,0xBE9696,new Item.Properties()));
    public static final RegistryObject<EntityType<Mechanist>> MECHANIST=ENTITIES.register(Mechanist.ID,()->EntityType.Builder.<Mechanist>of(Mechanist::new,MobCategory.MONSTER).sized(4.9F,3.8F).clientTrackingRange(10).updateInterval(2).build(Mechanist.ID));
    public static final RegistryObject<Item> MECHANIST_EGG=ITEMS.register(Mechanist.ID+"_spawn_egg",()->new ForgeSpawnEggItem(MECHANIST,0x354344,0xB8934D,new Item.Properties()));
    public static final RegistryObject<EntityType<Jinwu>> JINWU=ENTITIES.register(Jinwu.ID,()->EntityType.Builder.<Jinwu>of(Jinwu::new,MobCategory.MONSTER).sized(5.6F,3.4F).clientTrackingRange(10).updateInterval(2).build(Jinwu.ID));
    public static final RegistryObject<Item> JINWU_EGG=ITEMS.register(Jinwu.ID+"_spawn_egg",()->new ForgeSpawnEggItem(JINWU,0x30353B,0xCCA34E,new Item.Properties()));
    public static final RegistryObject<EntityType<FoxMatron>> FOX=ENTITIES.register(FoxMatron.ID,()->EntityType.Builder.<FoxMatron>of(FoxMatron::new,MobCategory.MONSTER).sized(5.5F,3.5F).clientTrackingRange(10).updateInterval(2).build(FoxMatron.ID));
    public static final RegistryObject<Item> FOX_EGG=ITEMS.register(FoxMatron.ID+"_spawn_egg",()->new ForgeSpawnEggItem(FOX,0xF6EDF2,0xC985A6,new Item.Properties()));
    public static final RegistryObject<EntityType<HammerGuardian>> HAMMER=ENTITIES.register(HammerGuardian.ID,()->EntityType.Builder.<HammerGuardian>of(HammerGuardian::new,MobCategory.MONSTER).sized(5.0F,4.3F).clientTrackingRange(12).updateInterval(2).build(HammerGuardian.ID));
    public static final RegistryObject<Item> HAMMER_EGG=ITEMS.register(HammerGuardian.ID+"_spawn_egg",()->new ForgeSpawnEggItem(HAMMER,0xC49A49,0x383B36,new Item.Properties()));
    public static final RegistryObject<EntityType<HammerChain>> HAMMER_CHAIN=ENTITIES.register("guardian_hammer_chain",()->EntityType.Builder.<HammerChain>of(HammerChain::new,MobCategory.MISC).sized(.7F,.7F).clientTrackingRange(12).updateInterval(1).build("guardian_hammer_chain"));
    public static final RegistryObject<EntityType<MechanistWheel>> WHEEL=ENTITIES.register("yanshi_copper_wheel",()->EntityType.Builder.<MechanistWheel>of(MechanistWheel::new,MobCategory.MISC).sized(.8F,.25F).clientTrackingRange(10).updateInterval(1).build("yanshi_copper_wheel"));
    public static final RegistryObject<EntityType<ClockworkSpider>> SPIDER=ENTITIES.register(ClockworkSpider.ID,()->EntityType.Builder.<ClockworkSpider>of(ClockworkSpider::new,MobCategory.MONSTER).sized(.55F,.4F).clientTrackingRange(10).updateInterval(2).build(ClockworkSpider.ID));
    public static final RegistryObject<EntityType<SpiderWoman>> SPIDER_WOMAN=ENTITIES.register(SpiderWoman.ID,()->EntityType.Builder.<SpiderWoman>of(SpiderWoman::new,MobCategory.MONSTER).sized(3F,2F).clientTrackingRange(12).updateInterval(2).build(SpiderWoman.ID));
    public static final RegistryObject<Item> SPIDER_WOMAN_EGG=ITEMS.register(SpiderWoman.ID+"_spawn_egg",()->new ForgeSpawnEggItem(SPIDER_WOMAN,0x302738,0x75B54A,new Item.Properties()));
    public static final RegistryObject<EntityType<SpiderBrood>> SPIDER_BROOD=ENTITIES.register(SpiderBrood.ID,()->EntityType.Builder.<SpiderBrood>of(SpiderBrood::new,MobCategory.MONSTER).sized(.55F,.45F).clientTrackingRange(10).updateInterval(2).build(SpiderBrood.ID));
    public static final RegistryObject<EntityType<Alchemist>> ALCHEMIST=ENTITIES.register(Alchemist.ID,()->EntityType.Builder.<Alchemist>of(Alchemist::new,MobCategory.MONSTER).sized(1.6F,2F).clientTrackingRange(12).updateInterval(2).build(Alchemist.ID));
    public static final RegistryObject<Item> ALCHEMIST_EGG=ITEMS.register(Alchemist.ID+"_spawn_egg",()->new ForgeSpawnEggItem(ALCHEMIST,0x28242B,0xB66D35,new Item.Properties()));
    public static final RegistryObject<EntityType<AlchemistOrb>> ALCHEMIST_ORB=ENTITIES.register(AlchemistOrb.ID,()->EntityType.Builder.<AlchemistOrb>of(AlchemistOrb::new,MobCategory.MISC).sized(.35F,.35F).clientTrackingRange(12).updateInterval(1).build(AlchemistOrb.ID));
    public static final RegistryObject<EntityType<AlchemistZone>> ALCHEMIST_ZONE=ENTITIES.register("alchemist_finite_sea",()->EntityType.Builder.<AlchemistZone>of(AlchemistZone::new,MobCategory.MISC).sized(.1F,.1F).clientTrackingRange(12).updateInterval(10).build("alchemist_finite_sea"));
    public static void register(IEventBus bus){ENTITIES.register(bus);ITEMS.register(bus);EFFECTS.register(bus);bus.addListener(EliteContent::attributes);}
    private static void attributes(EntityAttributeCreationEvent e){e.put(HEADLESS.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,180).add(Attributes.ATTACK_DAMAGE,9).add(Attributes.MOVEMENT_SPEED,.23).add(Attributes.ARMOR,12).add(Attributes.KNOCKBACK_RESISTANCE,.65).add(Attributes.FOLLOW_RANGE,28).build());
        e.put(BIRD.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,160).add(Attributes.ATTACK_DAMAGE,8).add(Attributes.MOVEMENT_SPEED,.2).add(Attributes.FLYING_SPEED,.32).add(Attributes.ARMOR,5).add(Attributes.KNOCKBACK_RESISTANCE,.35).add(Attributes.FOLLOW_RANGE,32).build());
        e.put(MECHANIST.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,144).add(Attributes.ATTACK_DAMAGE,6).add(Attributes.MOVEMENT_SPEED,.22).add(Attributes.ARMOR,6).add(Attributes.KNOCKBACK_RESISTANCE,.25).add(Attributes.FOLLOW_RANGE,28).build());
        e.put(JINWU.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,200).add(Attributes.ATTACK_DAMAGE,10).add(Attributes.MOVEMENT_SPEED,.22).add(Attributes.ARMOR,16).add(Attributes.ARMOR_TOUGHNESS,2).add(Attributes.KNOCKBACK_RESISTANCE,.8).add(Attributes.FOLLOW_RANGE,28).build());
        e.put(FOX.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,132).add(Attributes.ATTACK_DAMAGE,7).add(Attributes.MOVEMENT_SPEED,.18).add(Attributes.FLYING_SPEED,.22).add(Attributes.ARMOR,3).add(Attributes.KNOCKBACK_RESISTANCE,.2).add(Attributes.FOLLOW_RANGE,24).build());
        e.put(HAMMER.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,208).add(Attributes.ATTACK_DAMAGE,10).add(Attributes.MOVEMENT_SPEED,.18).add(Attributes.ARMOR,20).add(Attributes.ARMOR_TOUGHNESS,4).add(Attributes.KNOCKBACK_RESISTANCE,.8).add(Attributes.FOLLOW_RANGE,28).build());
        e.put(SPIDER.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,6).add(Attributes.MOVEMENT_SPEED,.36).add(Attributes.FOLLOW_RANGE,16).build());
        e.put(SPIDER_WOMAN.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,176).add(Attributes.ATTACK_DAMAGE,8).add(Attributes.MOVEMENT_SPEED,.25).add(Attributes.ARMOR,8).add(Attributes.KNOCKBACK_RESISTANCE,.5).add(Attributes.FOLLOW_RANGE,28).build());
        e.put(SPIDER_BROOD.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,6).add(Attributes.ATTACK_DAMAGE,2).add(Attributes.MOVEMENT_SPEED,.38).add(Attributes.FOLLOW_RANGE,16).build());
        e.put(ALCHEMIST.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,160).add(Attributes.ATTACK_DAMAGE,7).add(Attributes.MOVEMENT_SPEED,.22).add(Attributes.ARMOR,6).add(Attributes.KNOCKBACK_RESISTANCE,.25).add(Attributes.FOLLOW_RANGE,28).build());}
    private EliteContent(){}
}
