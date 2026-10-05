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
    public static final RegistryObject<MobEffect> JUNHUN_AURA = EFFECTS.register("junhun_aura", ArmyAuraEffect::new);

    public static final RegistryObject<EntityType<TemplateMob>> ZUWU_DAOSHOU = mob("zuwu_daoshou", TemplateMob.Kind.SWORD, .65F, 1.85F);
    public static final RegistryObject<EntityType<TemplateMob>> LUDUN_JIASHI = mob("ludun_jiashi", TemplateMob.Kind.SHIELD, .95F, 2.05F);
    public static final RegistryObject<EntityType<TemplateMob>> FUFA_JIJIU = mob("fufa_jijiu", TemplateMob.Kind.PRIEST, .65F, 1.80F);
    public static final RegistryObject<EntityType<TemplateMob>> SHANJING_SHANXIAO = mob("shanjing_shanxiao", TemplateMob.Kind.BEAST, .95F, .9F);
    public static final RegistryObject<EntityType<TemplateMob>> JUMA_CHANGQIANGBING = mob("juma_changqiangbing", TemplateMob.Kind.SPEAR, .65F, 1.95F);
    public static final RegistryObject<EntityType<TemplateMob>> LIANNU_ZHENZU = mob("liannu_zhenzu", TemplateMob.Kind.CROSSBOW, .65F, 1.75F);
    public static final RegistryObject<EntityType<TemplateMob>> TIESUO_CHIHOU = mob("tiesuo_chihou", TemplateMob.Kind.SCOUT, .6F, 1.78F);
    public static final RegistryObject<EntityType<TemplateMob>> KUIJUN_SISHI = mob("kuijun_sishi", TemplateMob.Kind.POWDER, .65F, 1.82F);
    public static final RegistryObject<EntityType<TemplateMob>> ZHENWANG_ZHANGQIGUAN = mob("zhenwang_zhangqiguan", TemplateMob.Kind.FLAG, .8F, 2.1F);
    public static final RegistryObject<EntityType<ArmyCaltrop>> ARMY_CALTROP = ENTITIES.register("army_caltrop",
            () -> EntityType.Builder.<ArmyCaltrop>of(ArmyCaltrop::new, MobCategory.MISC)
                    .sized(.4F, .15F).clientTrackingRange(6).updateInterval(10).build("army_caltrop"));
    public static final RegistryObject<EntityType<TemplateProjectile>> TEMPLATE_PROJECTILE = ENTITIES.register("template_projectile",
            () -> EntityType.Builder.<TemplateProjectile>of(TemplateProjectile::new, MobCategory.MISC)
                    .sized(.3F, .3F).clientTrackingRange(8).updateInterval(2).build("template_projectile"));

    public static final RegistryObject<Item> ZUWU_DAOSHOU_EGG = egg("zuwu_daoshou", ZUWU_DAOSHOU, 0x563E2A, 0xA94234);
    public static final RegistryObject<Item> LUDUN_JIASHI_EGG = egg("ludun_jiashi", LUDUN_JIASHI, 0x333D43, 0xA2864B);
    public static final RegistryObject<Item> FUFA_JIJIU_EGG = egg("fufa_jijiu", FUFA_JIJIU, 0x5F2033, 0xE6C66A);
    public static final RegistryObject<Item> SHANJING_SHANXIAO_EGG = egg("shanjing_shanxiao", SHANJING_SHANXIAO, 0x493F33, 0x468982);
    public static final RegistryObject<Item> JUMA_CHANGQIANGBING_EGG = egg("juma_changqiangbing", JUMA_CHANGQIANGBING, 0x45544F, 0x7B806C);
    public static final RegistryObject<Item> LIANNU_ZHENZU_EGG = egg("liannu_zhenzu", LIANNU_ZHENZU, 0x65533A, 0x9C7745);
    public static final RegistryObject<Item> TIESUO_CHIHOU_EGG = egg("tiesuo_chihou", TIESUO_CHIHOU, 0x20272B, 0x728087);
    public static final RegistryObject<Item> KUIJUN_SISHI_EGG = egg("kuijun_sishi", KUIJUN_SISHI, 0x6B5E55, 0x985645);
    public static final RegistryObject<Item> ZHENWANG_ZHANGQIGUAN_EGG = egg("zhenwang_zhangqiguan", ZHENWANG_ZHANGQIGUAN, 0x182D30, 0xBA8047);

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
        event.put(JUMA_CHANGQIANGBING.get(), attributes(52, 5, .25, 5, .1));
        event.put(LIANNU_ZHENZU.get(), attributes(38, 4, .24, 2, 0));
        event.put(TIESUO_CHIHOU.get(), attributes(36, 4, .32, 1, 0));
        event.put(KUIJUN_SISHI.get(), attributes(34, 4, .28, 0, 0));
        event.put(ZHENWANG_ZHANGQIGUAN.get(), attributes(64, 6, .16, 6, .4));
    }
}
