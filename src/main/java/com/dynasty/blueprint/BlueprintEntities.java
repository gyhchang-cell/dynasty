package com.dynasty.blueprint;

import com.dynasty.Dynasty;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.item.Item;
import net.minecraftforge.common.ForgeSpawnEggItem;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class BlueprintEntities {
    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, Dynasty.MODID);
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, Dynasty.MODID);
    public static final DeferredRegister<MobEffect> EFFECTS = DeferredRegister.create(ForgeRegistries.MOB_EFFECTS, Dynasty.MODID);
    public static final RegistryObject<MobEffect> BINGSHA_POSSESSION = EFFECTS.register("bingsha_possession", TemplateSupportEffect::new);

    public static final RegistryObject<EntityType<TemplateMob>> ZUWU_DAOSHOU = mob("zuwu_daoshou", TemplateMob.Kind.SWORD, .65F, 1.85F);
    public static final RegistryObject<EntityType<TemplateMob>> LUDUN_JIASHI = mob("ludun_jiashi", TemplateMob.Kind.SHIELD, .95F, 2.05F);
    public static final RegistryObject<EntityType<TemplateMob>> FUFA_JIJIU = mob("fufa_jijiu", TemplateMob.Kind.PRIEST, .65F, 1.80F);
    public static final RegistryObject<EntityType<TemplateMob>> SHANJING_SHANXIAO = mob("shanjing_shanxiao", TemplateMob.Kind.BEAST, .95F, .9F);
    public static final RegistryObject<EntityType<TemplateProjectile>> TEMPLATE_PROJECTILE = ENTITIES.register("template_projectile",
            () -> EntityType.Builder.<TemplateProjectile>of(TemplateProjectile::new, MobCategory.MISC)
                    .sized(.3F, .3F).clientTrackingRange(8).updateInterval(2).build("template_projectile"));

    public static final RegistryObject<Item> ZUWU_DAOSHOU_EGG = egg("zuwu_daoshou", ZUWU_DAOSHOU, 0x563E2A, 0xA94234);
    public static final RegistryObject<Item> LUDUN_JIASHI_EGG = egg("ludun_jiashi", LUDUN_JIASHI, 0x333D43, 0xA2864B);
    public static final RegistryObject<Item> FUFA_JIJIU_EGG = egg("fufa_jijiu", FUFA_JIJIU, 0x5F2033, 0xE6C66A);
    public static final RegistryObject<Item> SHANJING_SHANXIAO_EGG = egg("shanjing_shanxiao", SHANJING_SHANXIAO, 0x493F33, 0x468982);

    private BlueprintEntities() { }
    private static RegistryObject<EntityType<TemplateMob>> mob(String id, TemplateMob.Kind kind, float width, float height) {
        return ENTITIES.register(id, () -> EntityType.Builder.<TemplateMob>of((type, level) -> new TemplateMob(type, level, kind), MobCategory.MONSTER)
                .sized(width, height).clientTrackingRange(10).updateInterval(3).build(id));
    }
    private static RegistryObject<Item> egg(String id, RegistryObject<EntityType<TemplateMob>> type, int base, int spot) {
        return ITEMS.register(id + "_spawn_egg", () -> new ForgeSpawnEggItem(type, base, spot, new Item.Properties()));
    }
    public static void register(IEventBus bus) {
        ENTITIES.register(bus);
        ITEMS.register(bus);
        EFFECTS.register(bus);
        bus.addListener((EntityAttributeCreationEvent event) -> attributes(event));
    }
    private static AttributeSupplier attributes(double health, double damage, double speed, double armor, double resistance) {
        // Early Dynasty weapons deal 5/9/14/20 damage: ordinary mobs take a few contemporary hits.
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, health).add(Attributes.ATTACK_DAMAGE, damage)
                .add(Attributes.MOVEMENT_SPEED, speed).add(Attributes.ARMOR, armor).add(Attributes.FOLLOW_RANGE, 28)
                .add(Attributes.KNOCKBACK_RESISTANCE, resistance).add(Attributes.ATTACK_SPEED, 1).build();
    }
    private static void attributes(EntityAttributeCreationEvent event) {
        event.put(ZUWU_DAOSHOU.get(), attributes(48, 5, .25, 3, .05));
        event.put(LUDUN_JIASHI.get(), attributes(80, 7, .18, 8, .5));
        event.put(FUFA_JIJIU.get(), attributes(40, 4, .23, 1, 0));
        event.put(SHANJING_SHANXIAO.get(), attributes(44, 5, .31, 2, .05));
    }
}
