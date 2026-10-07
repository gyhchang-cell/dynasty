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
    public static final RegistryObject<MobEffect> SPIRIT_CHILL = EFFECTS.register("spirit_chill", SpiritChillEffect::new);

    public static final RegistryObject<EntityType<TemplateMob>> MINGSHA_SHIXIE=mob("mingsha_shixie",TemplateMob.Kind.SCORPION,1.5F,.9F);
    public static final RegistryObject<Item> MINGSHA_SHIXIE_EGG=egg("mingsha_shixie",MINGSHA_SHIXIE,0xB39456,0xD9C27C);
    public static final RegistryObject<MobEffect> SAND_RESONANCE=EFFECTS.register("sand_resonance",SandResonanceEffect::new);
    public static final RegistryObject<MobEffect> ROOT_GRIP=EFFECTS.register("root_grip",()->new SoulBindEffect("805d1817-a544-456e-b70d-cb58e676fcf1"));
    public static final RegistryObject<MobEffect> SOUL_BIND = EFFECTS.register("soul_bind",SoulBindEffect::new);
    public static final RegistryObject<MobEffect> LANTERN_GLARE = EFFECTS.register("lantern_glare",()->new MobEffect(net.minecraft.world.effect.MobEffectCategory.HARMFUL,0xE9E4CF){});
    public static final RegistryObject<EntityType<TemplateMob>> KUMU_SHUJING=mob("kumu_shujing",TemplateMob.Kind.TREE,1.2F,2.8F);
    public static final RegistryObject<EntityType<RootSnare>> ROOT_SNARE=ENTITIES.register("root_snare",
        ()->EntityType.Builder.<RootSnare>of(RootSnare::new,MobCategory.MISC).sized(2.4F,2F).clientTrackingRange(8).updateInterval(10).build("root_snare"));
    public static final RegistryObject<Item> KUMU_SHUJING_EGG=egg("kumu_shujing",KUMU_SHUJING,0x342F26,0xAD9F47);
    public static final RegistryObject<EntityType<TemplateMob>> CHIMU_ZHUHA=mob("chimu_zhuha",TemplateMob.Kind.TOAD,1.4F,1F);
    public static final RegistryObject<EntityType<CorpseMiasma>> TOAD_VENOM_POOL=ENTITIES.register("toad_venom_pool",
        ()->EntityType.Builder.<CorpseMiasma>of(CorpseMiasma::new,MobCategory.MISC).sized(2.2F,.5F).clientTrackingRange(8).updateInterval(10).build("toad_venom_pool"));
    public static final RegistryObject<Item> CHIMU_ZHUHA_EGG=egg("chimu_zhuha",CHIMU_ZHUHA,0x682A24,0xCE7837);
    public static final RegistryObject<EntityType<TemplateMob>> MUXUE_FEILU = mob("muxue_feilu",TemplateMob.Kind.SKULL,.85F,1.7F);
    public static final RegistryObject<EntityType<SkullBloodPool>> SKULL_BLOOD_POOL = ENTITIES.register("skull_blood_pool",
        ()->EntityType.Builder.<SkullBloodPool>of(SkullBloodPool::new,MobCategory.MISC).sized(2.4F,.5F).clientTrackingRange(8).updateInterval(10).build("skull_blood_pool"));
    public static final RegistryObject<EntityType<TemplateMob>> ZHIREN_JIANKE = mob("zhiren_jianke",TemplateMob.Kind.PAPER,.6F,1.85F);
    public static final RegistryObject<EntityType<TemplateMob>> FUHUN_BAIBU_TONGZI = mob("fuhun_baibu_tongzi",TemplateMob.Kind.CHILD,.55F,1.2F);
    public static final RegistryObject<EntityType<TemplateMob>> ZUWU_DAOSHOU = mob("zuwu_daoshou", TemplateMob.Kind.SWORD, .65F, 1.85F);
    public static final RegistryObject<EntityType<TemplateMob>> LUDUN_JIASHI = mob("ludun_jiashi", TemplateMob.Kind.SHIELD, .95F, 2.05F);
    public static final RegistryObject<EntityType<TemplateMob>> FUFA_JIJIU = mob("fufa_jijiu", TemplateMob.Kind.PRIEST, .65F, 1.80F);
    public static final RegistryObject<EntityType<TemplateMob>> SHANJING_SHANXIAO = mob("shanjing_shanxiao", TemplateMob.Kind.BEAST, .95F, .9F);
    public static final RegistryObject<EntityType<TemplateMob>> JUMA_CHANGQIANGBING = mob("juma_changqiangbing", TemplateMob.Kind.SPEAR, .65F, 1.95F);
    public static final RegistryObject<EntityType<TemplateMob>> LIANNU_ZHENZU = mob("liannu_zhenzu", TemplateMob.Kind.CROSSBOW, .65F, 1.75F);
    public static final RegistryObject<EntityType<TemplateMob>> TIESUO_CHIHOU = mob("tiesuo_chihou", TemplateMob.Kind.SCOUT, .6F, 1.78F);
    public static final RegistryObject<EntityType<TemplateMob>> KUIJUN_SISHI = mob("kuijun_sishi", TemplateMob.Kind.POWDER, .65F, 1.82F);
    public static final RegistryObject<EntityType<TemplateMob>> ZHENWANG_ZHANGQIGUAN = mob("zhenwang_zhangqiguan", TemplateMob.Kind.FLAG, .8F, 2.1F);
    public static final RegistryObject<EntityType<TemplateMob>> PIJIA_PANJIANG_HUWEI = mob("pijia_panjiang_huwei", TemplateMob.Kind.AXE_GUARD, 1.1F, 2.15F);
    public static final RegistryObject<EntityType<TemplateMob>> YINBING_GUIZU = mob("yinbing_guizu", TemplateMob.Kind.GHOST, .65F, 1.8F);
    public static final RegistryObject<EntityType<TemplateMob>> SHIBIAN_LISHI = mob("shibian_lishi", TemplateMob.Kind.CORPSE, 1.25F, 2.3F);
    public static final RegistryObject<EntityType<CorpseMiasma>> CORPSE_MIASMA = ENTITIES.register("corpse_miasma",
        () -> EntityType.Builder.<CorpseMiasma>of(CorpseMiasma::new,MobCategory.MISC).sized(2.6F,.5F).clientTrackingRange(8).updateInterval(10).build("corpse_miasma"));
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
    public static final RegistryObject<Item> PIJIA_PANJIANG_HUWEI_EGG = egg("pijia_panjiang_huwei", PIJIA_PANJIANG_HUWEI, 0x313C39, 0xB78C45);
    public static final RegistryObject<Item> YINBING_GUIZU_EGG = egg("yinbing_guizu", YINBING_GUIZU, 0x32434C, 0x7DD9E8);

    public static final RegistryObject<Item> SHIBIAN_LISHI_EGG = egg("shibian_lishi", SHIBIAN_LISHI, 0x26332E, 0x713C80);

    public static final RegistryObject<Item> FUHUN_BAIBU_TONGZI_EGG = egg("fuhun_baibu_tongzi", FUHUN_BAIBU_TONGZI, 0xDDD3B5, 0x252420);

    public static final RegistryObject<Item> ZHIREN_JIANKE_EGG = egg("zhiren_jianke", ZHIREN_JIANKE, 0xDED4BB, 0xAF403C);

    public static final RegistryObject<Item> MUXUE_FEILU_EGG = egg("muxue_feilu", MUXUE_FEILU, 0x514A40, 0x702A31);

    public static final RegistryObject<EntityType<TemplateMob>> BISHUI_XUANJIAO_YOUZI=mob("bishui_xuanjiao_youzi",TemplateMob.Kind.SERPENT,.7F,1.1F);
    public static final RegistryObject<Item> BISHUI_XUANJIAO_YOUZI_EGG=egg("bishui_xuanjiao_youzi",BISHUI_XUANJIAO_YOUZI,0x285F58,0x18292C);
    public static final RegistryObject<MobEffect> COLD_POOL_COIL=EFFECTS.register("cold_pool_coil",ColdPoolCoilEffect::new);

    public static final RegistryObject<EntityType<TemplateMob>> JUBI_SHIGANDANG=mob("jubi_shigandang",TemplateMob.Kind.STONE_GUARD,1.2F,2.4F);
    public static final RegistryObject<Item> JUBI_SHIGANDANG_EGG=egg("jubi_shigandang",JUBI_SHIGANDANG,0x646F69,0x917B42);

    public static final RegistryObject<EntityType<TemplateMob>> XUNSHAN_MUJIAQUAN=mob("xunshan_mujiaquan",TemplateMob.Kind.CLOCKWORK_DOG,.8F,.85F);
    public static final RegistryObject<Item> XUNSHAN_MUJIAQUAN_EGG=egg("xunshan_mujiaquan",XUNSHAN_MUJIAQUAN,0x79552F,0xBC8A41);
    public static final RegistryObject<EntityType<TemplateMob>> QINGTONG_SHUANGTOUSHEKUI=mob("qingtong_shuangtoushekui",TemplateMob.Kind.BRONZE_SNAKE,.9F,.9F);
    public static final RegistryObject<Item> QINGTONG_SHUANGTOUSHEKUI_EGG=egg("qingtong_shuangtoushekui",QINGTONG_SHUANGTOUSHEKUI,0x987A47,0x437065);
    public static final RegistryObject<EntityType<TemplateMob>> BAZU_DIGONGZHU=mob("bazu_digongzhu",TemplateMob.Kind.MINING_SPIDER,2.5F,1.4F);
    public static final RegistryObject<Item> BAZU_DIGONGZHU_EGG=egg("bazu_digongzhu",BAZU_DIGONGZHU,0x927238,0x394650);
    private BlueprintEntities() { }
    public static final RegistryObject<EntityType<TemplateMob>> YOUDENG_GUIMIANFU=mob("youdeng_guimianfu",TemplateMob.Kind.LANTERN_BAT,.85F,1.2F);
    public static final RegistryObject<Item> YOUDENG_GUIMIANFU_EGG=egg("youdeng_guimianfu",YOUDENG_GUIMIANFU,0x332E25,0x65C67E);
    public static final RegistryObject<EntityType<TemplateMob>> XUEJU_MANGGUYU=mob("xueju_mangguyu",TemplateMob.Kind.BLIND_FISH,1.2F,1.3F);
    public static final RegistryObject<Item> XUEJU_MANGGUYU_EGG=egg("xueju_mangguyu",XUEJU_MANGGUYU,0xD0D1BB,0x8BE4DA);
    public static final RegistryObject<EntityType<TemplateMob>> SHASHUI_FUNIGUI=mob("shashui_funigui",TemplateMob.Kind.DROWNER,.8F,1.9F);
    public static final RegistryObject<Item> SHASHUI_FUNIGUI_EGG=egg("shashui_funigui",SHASHUI_FUNIGUI,0x152A30,0x5C6A63);
    public static final RegistryObject<MobEffect> DROWNING_BIND=EFFECTS.register("drowning_bind",DrowningBindEffect::new);
    private static RegistryObject<EntityType<TemplateMob>> mob(String id, TemplateMob.Kind kind, float width, float height) {
        return ENTITIES.register(id, () -> EntityType.Builder.<TemplateMob>of((type, level) -> new TemplateMob(type, level, kind), MobCategory.MONSTER)
                .sized(width, height).clientTrackingRange(10).updateInterval(3).build(id));
    }
    private static RegistryObject<Item> egg(String id, RegistryObject<EntityType<TemplateMob>> type, int base, int spot) {
        return ITEMS.register(id + "_spawn_egg", () -> new ForgeSpawnEggItem(type, base, spot, new Item.Properties()));
    }
    public static void register(IEventBus bus) {
        BlueprintSalvage.bootstrap();
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
        event.put(SHASHUI_FUNIGUI.get(),attributes(48,5,.23,3,.1));
        event.put(XUEJU_MANGGUYU.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,54).add(Attributes.ATTACK_DAMAGE,6)
            .add(Attributes.MOVEMENT_SPEED,.18).add(Attributes.FLYING_SPEED,.22).add(Attributes.FOLLOW_RANGE,24).build());
        event.put(YOUDENG_GUIMIANFU.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,32).add(Attributes.ATTACK_DAMAGE,5)
            .add(Attributes.MOVEMENT_SPEED,.3).add(Attributes.FLYING_SPEED,.4).add(Attributes.FOLLOW_RANGE,28).build());
        event.put(BAZU_DIGONGZHU.get(),attributes(76,7,.23,8,.5));
        event.put(QINGTONG_SHUANGTOUSHEKUI.get(),attributes(60,6,.24,8,.3));
        event.put(XUNSHAN_MUJIAQUAN.get(),attributes(38,5,.31,5,.15));
        event.put(JUBI_SHIGANDANG.get(),attributes(90,8,.18,9,.6));
        event.put(BISHUI_XUANJIAO_YOUZI.get(),attributes(62,6,.32,4,.15));
        event.put(ZUWU_DAOSHOU.get(), attributes(48, 5, .25, 3, .05));
        event.put(LUDUN_JIASHI.get(), attributes(80, 7, .18, 8, .5));
        event.put(FUFA_JIJIU.get(), attributes(40, 4, .23, 1, 0));
        event.put(SHANJING_SHANXIAO.get(), attributes(44, 5, .31, 2, .05));
        event.put(JUMA_CHANGQIANGBING.get(), attributes(52, 5, .25, 5, .1));
        event.put(LIANNU_ZHENZU.get(), attributes(38, 4, .24, 2, 0));
        event.put(TIESUO_CHIHOU.get(), attributes(36, 4, .32, 1, 0));
        event.put(KUIJUN_SISHI.get(), attributes(34, 4, .28, 0, 0));
        event.put(ZHENWANG_ZHANGQIGUAN.get(), attributes(64, 6, .16, 6, .4));
        event.put(PIJIA_PANJIANG_HUWEI.get(), attributes(100, 8, .19, 10, .6));
        event.put(YINBING_GUIZU.get(), attributes(42, 5, .25, 2, .1));
        event.put(SHIBIAN_LISHI.get(), attributes(84, 7, .19, 3, .5));
        event.put(FUHUN_BAIBU_TONGZI.get(), attributes(28, 2, .24, 0, 0));
        event.put(ZHIREN_JIANKE.get(), attributes(32, 5, .34, 0, 0));
        event.put(CHIMU_ZHUHA.get(),attributes(52,6,.25,2,.1));
        event.put(MINGSHA_SHIXIE.get(),attributes(48,5,.27,8,.35));
        event.put(KUMU_SHUJING.get(),attributes(70,8,.18,6,.4));
        event.put(MUXUE_FEILU.get(),Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH,30).add(Attributes.ATTACK_DAMAGE,5)
            .add(Attributes.MOVEMENT_SPEED,.3).add(Attributes.FLYING_SPEED,.35).add(Attributes.FOLLOW_RANGE,28).build());
    }
}
