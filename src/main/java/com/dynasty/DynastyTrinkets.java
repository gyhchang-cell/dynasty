package com.dynasty;

import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 饰品系统：全部走 Curios 槽位。
 *
 * 1) 饰品物品通过 Curios 物品标签（data/curios/tags/items/*.json）放进 Curios 的
 *    标准分类槽或任务成长的 curio 万能槽，不再创建本模组专属槽；
 * 2) 效果统一由 DynastyTrinkets 每秒结算；安装 Curios 时必须装备。
 *    独立运行本体、未安装 Curios 时才启用背包和副手兼容。
 *
 * Trinket system: Curios-only slots; effects are recalculated once per second.
 */
@SuppressWarnings("null")
public final class DynastyTrinkets {

    private DynastyTrinkets() {
    }

    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, Dynasty.MODID);

    // ---- 饰品 / accessories ----
    public static final RegistryObject<Item> JADE_PENDANT = charm("jade_pendant");
    public static final RegistryObject<Item> JADE_BI_DISC = charm("jade_bi_disc");
    public static final RegistryObject<Item> GOLD_SEAL_CHARM = charm("gold_seal_charm");
    public static final RegistryObject<Item> DRAGON_SCALE_CHARM = charm("dragon_scale_charm");
    public static final RegistryObject<Item> PHOENIX_FEATHER_CHARM = charm("phoenix_feather_charm");
    public static final RegistryObject<Item> QILIN_HORN_CHARM = charm("qilin_horn_charm");
    public static final RegistryObject<Item> FOX_TAIL_CHARM = charm("fox_tail_charm");
    public static final RegistryObject<Item> SILK_POUCH = charm("silk_pouch");
    public static final RegistryObject<Item> SOUTH_POINTING_COMPASS = charm("south_pointing_compass");
    /** 护心镜：+8 护甲、额外 4% 减伤 / Heart Mirror */
    public static final RegistryObject<Item> HEART_MIRROR = charm("heart_mirror");
    /** 玉冠：头饰，生命上限 +220 / Jade Crown */
    public static final RegistryObject<Item> JADE_CROWN = charm("jade_crown");
    /** 玉蝉：残血保命（抗性 + 速度，不回血）/ Jade Cicada */
    public static final RegistryObject<Item> JADE_CICADA = charm("jade_cicada");
    /** 龙珠：攻击 +25%、抗击退 / Dragon Pearl */
    public static final RegistryObject<Item> DRAGON_PEARL = charm("dragon_pearl");
    /** 凤凰指环：常驻抗火，着火即灭火并加速 / Phoenix Ring */
    public static final RegistryObject<Item> PHOENIX_RING = charm("phoenix_ring");
    /** 雷纹护符：雷雨天力量 II / Storm Charm */
    public static final RegistryObject<Item> STORM_CHARM = charm("storm_charm");
    /** 明月佩：夜间夜视 + 幸运 + 攻击 / Moon Pendant */
    public static final RegistryObject<Item> MOON_PENDANT = charm("moon_pendant");
    /** 虎符残片：周期性威慑周围敌人 / Tiger Crest */
    public static final RegistryObject<Item> TIGER_CREST = charm("tiger_crest");
    /** 玉龟符：水下呼吸 + 海豚恩惠 + 抗性 / Jade Tortoise (water) */
    public static final RegistryObject<Item> JADE_TORTOISE = charm("jade_tortoise");
    /** 战鼓坠：常驻力量 I，并给周围友军加力量 / War Drum (support) */
    public static final RegistryObject<Item> WAR_DRUM_CHARM = charm("war_drum_charm");
    /** 朱砂囊：定期净化中毒/凋零/失明/饥饿 / Cinnabar Pouch (cleanses) */
    public static final RegistryObject<Item> CINNABAR_POUCH = charm("cinnabar_pouch");
    /** 龙须穗：攻速 +15%、击退 +0.5 / Dragon Whisker (speed & knockback) */
    public static final RegistryObject<Item> DRAGON_WHISKER = charm("dragon_whisker");
    /** 虎头令：移速 +8%、跳跃提升 / Tiger Token (mobility) */
    public static final RegistryObject<Item> TIGER_TOKEN = charm("tiger_token");
    /** 金乌翎：白天攻击 +15% 幸运 +1，夜里给抗性 / Sun Feather (day/night) */
    public static final RegistryObject<Item> SUN_FEATHER = charm("sun_feather");
    /** 战马铃：骑乘时坐骑获得速度与抗性 / War Horse Bell (mounted) */
    public static final RegistryObject<Item> WAR_HORSE_BELL = charm("war_horse_bell");
    /** 玄铁腰牌：护甲 +6、抗击退 +0.2、生命 +150 / Iron Waist Token */
    public static final RegistryObject<Item> IRON_WAIST_TOKEN = charm("iron_waist_token");
    /** 瑞兽铃：幸运 +3 / Auspicious Bell (luck) */
    public static final RegistryObject<Item> AUSPICIOUS_BELL = charm("auspicious_bell");
    /** 避水珠：水下呼吸 + 海豚 + 水下战斗强化 / Water-Repelling Pearl */
    public static final RegistryObject<Item> SEA_PEARL = charm("sea_pearl");
    /** 龙骨戒：护甲 + 抗击退 + 攻击 / Dragon Bone Ring */
    public static final RegistryObject<Item> DRAGON_BONE_RING = charm("dragon_bone_ring");

    // ---- 第二十轮扩充：10 件新饰品（29 → 39）----
    // 贴图/模型/配方由 tools/art/gen_trinkets2.py 生成，两边名字必须一致。
    // Ten extra accessories; keep in sync with gen_trinkets2.py.
    public static final RegistryObject<Item> CLOUD_BROCADE = charm("cloud_brocade");
    public static final RegistryObject<Item> STAR_COMPASS = charm("star_compass");
    public static final RegistryObject<Item> DRAGON_KING_SCALE = charm("dragon_king_scale");
    public static final RegistryObject<Item> SKY_FEATHER = charm("sky_feather");
    public static final RegistryObject<Item> IMPERIAL_SEAL_CHARM = charm("imperial_seal_charm");
    public static final RegistryObject<Item> TOMB_CANDLE = charm("tomb_candle");
    public static final RegistryObject<Item> INKSTONE = charm("inkstone");
    public static final RegistryObject<Item> BAMBOO_FLUTE = charm("bamboo_flute");
    public static final RegistryObject<Item> MERIT_BADGE = charm("merit_badge");
    public static final RegistryObject<Item> SEA_CONCH = charm("sea_conch");

    // ---------------------------------------------------------------- 第三十一轮：50 件新饰品（表驱动）
    /**
     * {id, 属性1, 值1, 属性2, 值2, 效果, 等级, 条件}
     *
     * 属性编码：0 生命 1 护甲 2 抗击退 3 移速% 4 攻击% 5 攻速% 6 击退 7 距离 11 幸运（-1 = 没有）
     * 效果编码：1 夜视 2 水下呼吸 3 抗火 4 抗性 5 再生 8 缓降 11 幸运 12 生命恢复
     * 条件编码：0 常驻 1 白天 2 夜晚 3 水下 4 残血 5 骑乘
     *
     * 与 tools/art/gen_trinkets3.py 的 TRINKETS 表一一对应（tools/art/verify_gear.py 会核对），
     * 改一边就要改另一边 —— 注册、贴图、Curios 标签都由这张表带出来。
     *
     * Fifty extra accessories, driven from one table (five classes of ten).
     */
    /**
     * 百宝妆匣：右键随机开出一件王朝饰品（消耗品）。
     * Trinket Box: rolls one random accessory; consumed on use.
     */
    public static final RegistryObject<Item> TRINKET_BOX = ITEMS.register("trinket_box",
            () -> new DynastyUsables.TrinketBoxItem(new Item.Properties().stacksTo(16)));

    private static final Object[][] EXTRA_TABLE = {
            {"jade_marrow_charm", 0, 180D, 1, 5D, 0, 0, 0},
            {"jade_ruyi", 11, 2D, -1, 0D, 11, 0, 0},
            {"jade_ring", 5, 0.1D, 7, 1D, 0, 0, 0},
            {"jade_belt_hook", 1, 8D, 2, 0.3D, 0, 0, 0},
            {"jade_flying_apsara", 3, 0.08D, -1, 0D, 8, 0, 0},
            {"jade_bixie", 6, 0.4D, 4, 0.08D, 0, 0, 0},
            {"jade_kylin", 0, 220D, 4, 0.1D, 0, 0, 0},
            {"jade_silkworm", 0, 120D, -1, 0D, 12, 0, 4},
            {"jade_cong", 1, 12D, 2, 0.4D, 0, 0, 0},
            {"jade_zhang", 4, 0.12D, 5, 0.08D, 0, 0, 0},
            {"saber_tassel", 4, 0.07D, 5, 0.05D, 0, 0, 0},
            {"sword_tassel", 4, 0.06D, 7, 1D, 0, 0, 0},
            {"arrow_quiver", 4, 0.08D, 3, 0.04D, 0, 0, 0},
            {"bow_string", 5, 0.12D, 4, 0.05D, 0, 0, 0},
            {"wrist_guard", 1, 10D, 2, 0.3D, 0, 0, 0},
            {"knee_guard", 3, 0.05D, 2, 0.2D, 0, 0, 0},
            {"belt_buckle", 1, 6D, 0, 120D, 0, 0, 0},
            {"scale_plate", 1, 9D, 2, 0.25D, 0, 0, 0},
            {"iron_pauldron", 1, 14D, 4, 0.05D, 0, 0, 0},
            {"horse_stirrup", 3, 0.1D, -1, 0D, 0, 0, 5},
            {"crane_feather", 3, 0.1D, -1, 0D, 8, 0, 0},
            {"tiger_claw", 4, 0.12D, 6, 0.4D, 0, 0, 0},
            {"leopard_tail", 3, 0.12D, 5, 0.06D, 0, 0, 0},
            {"deer_antler", 0, 260D, -1, 0D, 5, 0, 0},
            {"snake_gall", 4, 0.1D, -1, 0D, 0, 0, 3},
            {"bear_paw", 0, 300D, 4, 0.08D, 0, 0, 0},
            {"turtle_shell", 1, 16D, 2, 0.5D, 0, 0, 0},
            {"rhino_horn", 4, 0.14D, 1, 6D, 0, 0, 0},
            {"ivory_tusk", 7, 2D, 4, 0.06D, 0, 0, 0},
            {"hawk_eye", 4, 0.1D, 7, 2D, 0, 0, 0},
            {"poem_scroll", 11, 2D, -1, 0D, 11, 0, 0},
            {"seal_charm", 0, 100D, 11, 1D, 0, 0, 0},
            {"go_board", 5, 0.1D, -1, 0D, 0, 0, 0},
            {"guqin_string", 5, 0.08D, -1, 0D, 0, 0, 0},
            {"tea_cup", 0, 200D, -1, 0D, 12, 0, 0},
            {"wine_gourd", 0, 240D, 6, 0.3D, 0, 0, 0},
            {"incense_sachet", 0, 160D, -1, 0D, 5, 0, 0},
            {"folding_fan", 3, 0.06D, 5, 0.08D, 0, 0, 0},
            {"mirror_pouch", 1, 10D, -1, 0D, 4, 0, 0},
            {"brush_rack", 5, 0.14D, 4, 0.06D, 0, 0, 0},
            {"bagua_mirror", 1, 14D, -1, 0D, 4, 0, 0},
            {"peach_sword", 4, 0.16D, -1, 0D, 0, 0, 0},
            {"talisman_pouch", 11, 3D, -1, 0D, 11, 0, 0},
            {"alchemy_pendant", 0, 200D, -1, 0D, 5, 1, 0},
            {"golden_pill", 0, 400D, -1, 0D, 5, 2, 0},
            {"cloud_pattern", 3, 0.12D, 2, 0.3D, 0, 0, 0},
            {"star_dial", 4, 0.12D, 5, 0.1D, 0, 0, 0},
            {"tiangang_talisman", 4, 0.18D, 2, 0.4D, 0, 0, 0},
            {"disha_talisman", 1, 18D, 6, 0.4D, 0, 0, 0},
            {"purple_qi_pearl", 0, 320D, 4, 0.14D, 0, 0, 0},
            // ---- 第三十二轮：+30 件（六类各 5 件，宫廷 / 战阵 / 灵兽 / 文房 / 道法 / 海事）----
            {"phoenix_hairpin", 0, 240D, 11, 1D, 0, 0, 0},
            {"dragon_robe_sash", 1, 14D, 0, 200D, 0, 0, 0},
            {"mandarin_rank_badge", 11, 2D, 0, 180D, 0, 0, 0},
            {"imperial_pearl_earring", 0, 200D, 11, 1D, 0, 0, 0},
            {"gilded_lotus_crown", 4, 0.1D, 3, 0.05D, 0, 0, 0},
            {"war_banner_charm", 4, 0.12D, 5, 0.06D, 0, 0, 0},
            {"iron_helmet_plume", 1, 12D, 3, 0.06D, 0, 0, 0},
            {"pike_tassel", 4, 0.1D, 7, 1D, 0, 0, 0},
            {"drum_beater", 5, 0.15D, 4, 0.05D, 0, 0, 0},
            {"armor_piercer_token", 4, 0.16D, 6, 0.35D, 0, 0, 0},
            {"phoenix_wing_charm", 3, 0.1D, -1, 0D, 8, 0, 0},
            {"qilin_hoof_charm", 0, 260D, 5, 0.08D, 0, 0, 0},
            {"turtle_blood_charm", 0, 300D, 1, 16D, 4, 0, 4},
            {"fox_spirit_pendant", 3, 0.12D, 11, 2D, 0, 0, 0},
            {"dragon_blood_pearl", 0, 360D, 4, 0.14D, 0, 0, 0},
            {"jade_brush_holder", 5, 0.12D, 4, 0.06D, 0, 0, 0},
            {"ink_slab_charm", 11, 2D, 0, 160D, 0, 0, 0},
            {"scroll_case_charm", 5, 0.1D, 11, 1D, 0, 0, 0},
            {"guqin_tassel", 5, 0.08D, 0, 120D, 0, 0, 0},
            {"scholar_ink_badge", 0, 180D, 11, 1D, 0, 0, 0},
            {"thunder_seal_charm", 4, 0.14D, 5, 0.1D, 0, 0, 0},
            {"immortal_crane_feather", 3, 0.12D, -1, 0D, 8, 0, 0},
            {"star_diagram_charm", 11, 3D, 0, 140D, 0, 0, 0},
            {"zen_bead_string", 0, 220D, -1, 0D, 12, 0, 4},
            {"alchemy_furnace_charm", 0, 260D, -1, 0D, 5, 0, 0},
            {"conch_horn", 0, 240D, 3, 0.08D, 0, 0, 0},
            {"dragon_scale_sash", 1, 16D, 2, 0.45D, 0, 0, 0},
            {"pearl_net_charm", 0, 200D, 11, 2D, 0, 0, 0},
            {"tide_compass_charm", 7, 2D, 3, 0.06D, 0, 0, 0},
            {"storm_anchor_charm", 1, 20D, 6, 0.5D, 0, 0, 0},

            // ================= 第三十四轮：50 件「新格式」饰品 =================
            // 14 格 = {id, 属性1, 值1, 属性2, 值2, 效果, 等级, 条件, 属性3, 值3, 条件3,
            //          命中触发, 数值, 概率%}（命中触发见 DynastyTrinketOnHit）
            // 第三格属性带**自己的条件** → 一件饰品能同时「白天 +攻、夜里 +移速」。
            // 效果列 21~27 全是模组自有效果（龙威/铁壁/疾风/威慑/天命/忠诚/内伤），
            // 新饰品不再给自己上原版 buff；27 内伤兼作代价（拿命换伤害）。
            // five themed groups of ten: day/night duality, life-for-damage bargains,
            // imperial edicts (mod effects), underworld sacrifice, frontier utility.
            // ---- 一、昼夜双生 ----
            // ---- 一、昼夜双生 ----
            // ---- 一、昼夜双生（连携组 1）----
            {"dawn_blade_charm", 4, 0.22D, -1, 0D, 0, 0, 1, 3, 0.1D, 2, 4, 0.35D, 100, 1},
            {"dusk_veil_charm", 4, 0.26D, -1, 0D, 0, 0, 2, 9, -0.2D, 1, 3, 0.45D, 25, 1},
            {"noon_pendant", 0, 240D, -1, 0D, 0, 0, 1, 0, -160D, 2, 0, 0D, 0, 1},
            {"moonlit_mirror", 5, 0.14D, -1, 0D, 0, 0, 2, 11, 2D, 1, 0, 0D, 0, 1},
            {"sun_chaser_ring", 3, 0.12D, 4, 0.1D, 0, 0, 1, -1, 0D, 0, 0, 0D, 0, 1},
            {"night_heron_feather", 4, 0.18D, 6, 0.35D, 0, 0, 2, -1, 0D, 0, 4, 0.3D, 100, 1},
            {"twilight_cicada", 2, 0.4D, -1, 0D, 0, 0, 1, 7, 1D, 2, 0, 0D, 0, 1},
            {"eclipse_bead", 4, 0.3D, -1, 0D, 0, 0, 2, 1, -6D, 1, 3, 0.55D, 20, 1},
            {"dawn_drum", 5, 0.12D, 3, 0.08D, 0, 0, 1, -1, 0D, 0, 0, 0D, 0, 1},
            {"starless_night_ring", 0, 220D, -1, 0D, 0, 0, 2, 4, 0.16D, 2, 1, 0.08D, 100, 1},
            // ---- 二、生死代价（连携组 2）----
            {"blood_oath_seal", 9, -0.3D, 4, 0.35D, 0, 0, 0, -1, 0D, 0, 1, 0.15D, 100, 2},
            {"bone_reaper_tally", 9, -0.2D, 4, 0.25D, 0, 0, 0, 6, 0.5D, 0, 2, 0.2D, 100, 2},
            {"internal_injury_talisman", 4, 0.45D, -1, 0D, 27, 0, 0, -1, 0D, 0, 0, 0D, 0, 2},
            {"lifedrain_ring", 4, 0.3D, 5, 0.1D, 27, 1, 0, -1, 0D, 0, 1, 0.12D, 100, 2},
            {"crimson_pact_charm", 9, -0.4D, 4, 0.5D, 0, 0, 0, -1, 0D, 0, 1, 0.2D, 60, 2},
            {"flesh_gamble_dice", 4, 0.2D, -1, 0D, 0, 0, 0, 4, 0.4D, 4, 0, 0D, 0, 2},
            {"deathbed_talisman", 4, 0.3D, 3, 0.3D, 0, 0, 4, -1, 0D, 0, 2, 0.25D, 60, 2},
            {"scarlet_lotus", 1, 14D, 5, 0.15D, 0, 0, 4, -1, 0D, 0, 0, 0D, 0, 2},
            {"blood_iron_sash", 9, -0.15D, 1, 18D, 0, 0, 0, -1, 0D, 0, 0, 0D, 0, 2},
            {"soul_candle_charm", 9, -0.25D, -1, 0D, 0, 0, 0, 4, 0.28D, 2, 1, 0.1D, 50, 2},
            // ---- 三、天朝敕令（连携组 3）----
            {"edict_of_dragon", 4, 0.1D, -1, 0D, 21, 0, 0, -1, 0D, 0, 0, 0D, 0, 3},
            {"edict_of_iron", 1, 8D, -1, 0D, 22, 0, 0, -1, 0D, 0, 0, 0D, 0, 3},
            {"edict_of_swift", 3, 0.06D, -1, 0D, 23, 0, 0, -1, 0D, 0, 0, 0D, 0, 3},
            {"edict_of_mandate", 11, 2D, -1, 0D, 25, 0, 0, -1, 0D, 0, 0, 0D, 0, 3},
            {"edict_of_dread", 4, 0.1D, -1, 0D, 24, 0, 0, -1, 0D, 0, 2, 0.1D, 100, 3},
            {"edict_of_loyalty", 0, 180D, -1, 0D, 26, 0, 0, -1, 0D, 0, 0, 0D, 0, 3},
            {"seal_of_two_heavens", 4, 0.12D, -1, 0D, 21, 0, 0, 3, 0.06D, 1, 0, 0D, 0, 3},
            {"throne_inheritance_charm", 0, 260D, -1, 0D, 25, 0, 0, -1, 0D, 0, 0, 0D, 0, 3},
            {"war_deity_signet", 4, 0.15D, -1, 0D, 21, 1, 0, -1, 0D, 0, 3, 0.4D, 30, 3},
            {"unbroken_wall_charm", 2, 0.5D, -1, 0D, 22, 1, 0, -1, 0D, 0, 0, 0D, 0, 3},
            // ---- 四、幽冥献祭（连携组 4）----
            {"sacrificial_blade_charm", 4, 0.38D, -1, 0D, 27, 0, 0, -1, 0D, 0, 2, 0.18D, 80, 4},
            {"nether_binding_ring", 4, 0.4D, -1, 0D, 0, 0, 2, 9, -0.2D, 1, 6, 60D, 30, 4},
            {"ghost_ferry_tally", 5, 0.3D, -1, 0D, 27, 0, 0, 9, -0.25D, 0, 2, 0.15D, 60, 4},
            {"bone_chill_pendant", 4, 0.25D, -1, 0D, 27, 1, 3, -1, 0D, 0, 6, 45D, 35, 4},
            {"candle_of_the_dead", 4, 0.3D, -1, 0D, 0, 0, 2, 0, -150D, 1, 0, 0D, 0, 4},
            {"tomb_warden_seal", 1, 25D, -1, 0D, 27, 0, 0, -1, 0D, 0, 0, 0D, 0, 4},
            {"jade_shroud_charm", 0, 400D, 3, -0.1D, 27, 0, 0, -1, 0D, 0, 0, 0D, 0, 4},
            {"karma_ledger_charm", 4, 0.3D, -1, 0D, 0, 0, 0, 1, 30D, 4, 0, 0D, 0, 4},
            {"abyss_pearl", 4, 0.35D, 6, 0.4D, 0, 0, 2, -1, 0D, 0, 3, 0.5D, 30, 4},
            {"underworld_gate_key", 4, 0.45D, -1, 0D, 0, 0, 7, -1, 0D, 0, 6, 90D, 25, 4},
            // ---- 五、巧匠边塞（连携组 5）----
            {"ranging_compass_charm", 7, 2D, 4, 0.08D, 0, 0, 0, -1, 0D, 0, 0, 0D, 0, 5},
            {"quickdraw_glove", 5, 0.18D, 6, 0.6D, 0, 0, 0, -1, 0D, 0, 5, 0.05D, 100, 5},
            {"siege_hammer_charm", 4, 0.25D, -1, 0D, 0, 0, 6, -1, 0D, 0, 2, 0.12D, 80, 5},
            {"dusk_raider_badge", 4, 0.2D, 3, 0.12D, 0, 0, 2, -1, 0D, 0, 0, 0D, 0, 5},
            {"rain_prayer_knot", 5, 0.2D, 4, 0.3D, 0, 0, 7, -1, 0D, 0, 0, 0D, 0, 5},
            {"diver_signet", 1, 20D, 4, 0.25D, 0, 0, 3, -1, 0D, 0, 0, 0D, 0, 5},
            {"cavalry_sash", 4, 0.15D, 3, 0.1D, 0, 0, 5, -1, 0D, 0, 0, 0D, 0, 5},
            {"wound_binder_charm", 1, 25D, 5, 0.18D, 0, 0, 4, -1, 0D, 0, 0, 0D, 0, 5},
            {"iron_ration_charm", 0, 350D, 5, -0.08D, 0, 0, 0, -1, 0D, 0, 0, 0D, 0, 5},
            {"warlord_drum_charm", 5, 0.12D, -1, 0D, 0, 0, 6, 4, 0.4D, 4, 5, 0.06D, 100, 5},
    };

    /** 连携组的名字（组号 ↔ 主题）/ synergy group names */
    private static final Map<Integer, String> LINK_GROUP_NAMES = Map.of(
            1, "昼夜双生", 2, "生死代价", 3, "天朝敕令", 4, "幽冥献祭", 5, "巧匠边塞");

    /**
     * 连携加成：{组, 需要件数, 类型(0 属性 / 1 模组效果), 编码, 数值, 条件}。
     * 由 tools/art/gen_trinkets5.py 打印，改表请改生成器再粘回来。
     */
    private static final Object[][] LINK_TABLE = {
            {1, 2, 0, 3, 0.05D, 0},
            {1, 3, 0, 4, 0.08D, 0},
            {1, 3, 0, 3, 0.05D, 0},
            {1, 4, 0, 4, 0.12D, 0},
            {1, 4, 0, 3, 0.08D, 0},
            {2, 2, 0, 4, 0.06D, 0},
            {2, 3, 0, 4, 0.12D, 0},
            {2, 4, 0, 4, 0.16D, 0},
            {2, 4, 0, 0, 200D, 0},
            {3, 2, 0, 11, 2D, 0},
            {3, 3, 0, 11, 3D, 0},
            {3, 3, 0, 0, 200D, 0},
            {3, 4, 1, 21, 0D, 0},
            {3, 4, 0, 4, 0.1D, 0},
            {4, 2, 0, 4, 0.08D, 0},
            {4, 3, 0, 4, 0.12D, 0},
            {4, 4, 0, 4, 0.16D, 0},
            {4, 4, 0, 0, 250D, 0},
            {5, 2, 0, 5, 0.06D, 0},
            {5, 3, 0, 5, 0.1D, 0},
            {5, 3, 0, 3, 0.06D, 0},
            {5, 4, 0, 5, 0.14D, 0},
            {5, 4, 0, 7, 1D, 0},
    };

    /** 连携引擎看到的是「表里的 id」，不是物品实例 / the link engine works off table ids */
    static Object[][] linkTable() {
        return LINK_TABLE;
    }

    static Map<Integer, String> linkGroupNames() {
        return LINK_GROUP_NAMES;
    }

    /** 50 件新饰品的物品注册（表驱动，id 与贴图/配方/Curios 标签同名）/ register from the table */
    public static final List<RegistryObject<Item>> EXTRA_CHARMS = registerExtraCharms();

    static {
        // 命中触发（吸血 / 斩杀 / 会心 / 突袭 / 连击 / 雷罚）的参数同样来自这张表：
        // 建表时抽一次，之后每次命中只查那张小表。
        DynastyTrinketOnHit.index(EXTRA_TABLE);
        DynastyTrinketLink.index(EXTRA_TABLE, LINK_TABLE, LINK_GROUP_NAMES);
    }

    private static List<RegistryObject<Item>> registerExtraCharms() {
        List<RegistryObject<Item>> out = new ArrayList<>();
        for (Object[] row : EXTRA_TABLE) {
            String id = (String) row[0];
            out.add(ITEMS.register(id, () -> new DynastyTrinketTips.Charm(row)));
        }
        return out;
    }

    // 悬浮说明统一在 DynastyTrinketTips：表驱动饰品自动生成，手写饰品查 LEGACY 表。
    // Tooltip text lives in DynastyTrinketTips; check it before adding new codes.

    /** 条件是否满足（白天 / 夜晚 / 水下 / 残血 / 骑乘）/ is the accessory condition met */
    static boolean conditionMet(Player player, int condition) {
        return switch (condition) {
            case 1 -> player.level().isDay();
            case 2 -> !player.level().isDay();
            case 3 -> player.isUnderWater() || player.isInWater();
            case 4 -> player.getHealth() < player.getMaxHealth() * 0.4F;
            case 5 -> player.isPassenger();
            case 6 -> player.getHealth() >= player.getMaxHealth() - 0.01F;   // 满血 / at full health
            case 7 -> player.level().isThundering();                        // 雷雨 / thunderstorm
            default -> true;
        };
    }

    /**
     * 表驱动结算新饰品（属性 + 效果，每秒刷新一次）。
     *
     * v2 格式（第三十四轮起）：一行最多 11 格 ——
     * `{id, 属性1, 值1, 属性2, 值2, 效果, 等级, 条件, 属性3, 值3, 条件3}`
     * 前两格共用第 8 格的条件，第三格带**自己的条件**，于是可以写
     * 「白天 +25% 攻击、夜里 −120 生命」「残血再 +40% 攻击」这类双面设计。
     * 老行（8 格）照旧生效。
     *
     * v2 spec: up to 11 columns; the third attribute carries its own condition,
     * which enables day/night and low-health duality on a single accessory.
     */
    private static void applyExtra(Player player, java.util.Set<String> active) {
        for (Object[] row : EXTRA_TABLE) {
            String id = (String) row[0];
            if (!active.contains(id) || !conditionMet(player, (Integer) row[7])) {
                continue;
            }
            applySpecAttr(player, id, 0, (Integer) row[1], (Double) row[2]);
            applySpecAttr(player, id, 0, (Integer) row[3], (Double) row[4]);
            applySpecEffect(player, (Integer) row[5], (Integer) row[6]);
            if (row.length > 10 && conditionMet(player, (Integer) row[10])) {
                applySpecAttr(player, id, 1, (Integer) row[8], (Double) row[9]);
            }
        }
    }

    /**
     * 属性编码 → 原版属性（3/4/5/9 是百分比，其余是固定值）。
     *
     * slot 决定 UUID 段：第一/二格用 0~99，第三格用 100~199，
     * 这样同一件饰品用同一种属性能分两次相加（白天 +攻击、夜里 −生命）。
     *
     * attribute code to vanilla attribute; slot picks the UUID range so one
     * accessory can touch the same attribute twice under different conditions.
     */
    static void applySpecAttr(Player player, String id, int slot, int code, double value) {
        int key = slot * 100;
        switch (code) {
            case 0 -> addAttr(player, id, key + 0, 0, value);          // 生命
            case 1 -> addAttr(player, id, key + 1, 1, value);          // 护甲
            case 2 -> addAttr(player, id, key + 2, 2, value);          // 抗击退
            case 3 -> multiplyAttr(player, id, key + 3, 3, value);     // 移速 %
            case 4 -> multiplyAttr(player, id, key + 5, 5, value);     // 攻击 %
            case 5 -> multiplyAttr(player, id, key + 6, 6, value);     // 攻速 %
            case 6 -> addAttr(player, id, key + 7, 7, value);          // 击退
            case 7 -> addReach(player, id, key + 8, value);            // 攻击距离
            case 9 -> multiplyAttr(player, id, key + 9, 0, value);     // 生命上限 %
            case 11 -> addAttr(player, id, key + 4, 4, value);         // 幸运
            default -> {
                // -1 = 这一格没有属性
            }
        }
    }

    /** 「距离」= Forge 的实体触及距离 / Forge entity reach */
    private static void addReach(Player player, String id, int key, double amount) {
        AttributeInstance instance =
                player.getAttribute(net.minecraftforge.common.ForgeMod.ENTITY_REACH.get());
        if (instance != null) {
            instance.addTransientModifier(new AttributeModifier(uuid(id, key),
                    "dynasty_trinket_reach", amount, AttributeModifier.Operation.ADDITION));
        }
    }

    /**
     * 效果编码 → 效果。
     *
     * 21~27 是**模组自有效果**（龙威 / 铁壁 / 疾风 / 威慑 / 天命 / 忠诚 / 内伤），
     * 1~12 是早期批次用的原版效果（保留兼容）。新饰品只用模组效果：既不会和药水
     * 撞车，也能把「内伤」这种负面模组效果当成**代价**来写。
     *
     * 21-27 are the mod's own effects, 1-12 are legacy vanilla ones kept for the
     * older accessories. New accessories use mod effects only.
     */
    static void applySpecEffect(Player player, int code, int amplifier) {
        net.minecraft.world.effect.MobEffect mod = modEffect(code);
        if (mod != null) {
            player.addEffect(new MobEffectInstance(mod, 60, amplifier, true, false));
            return;
        }
        net.minecraft.world.effect.MobEffect effect = switch (code) {
            case 1 -> MobEffects.NIGHT_VISION;
            case 2 -> MobEffects.WATER_BREATHING;
            case 3 -> MobEffects.FIRE_RESISTANCE;
            case 4 -> MobEffects.DAMAGE_RESISTANCE;
            case 5 -> MobEffects.REGENERATION;
            case 8 -> MobEffects.SLOW_FALLING;
            case 11 -> MobEffects.LUCK;
            case 12 -> MobEffects.REGENERATION;
            default -> null;
        };
        if (effect == null) {
            return;
        }
        int level = code == 12 ? amplifier + 1 : amplifier;
        int ticks = effect == MobEffects.NIGHT_VISION ? 300 : 60;
        player.addEffect(new MobEffectInstance(effect, ticks, level, true, false));
    }

    /** 模组自有效果编码 → 效果 / mod-owned effect codes */
    private static net.minecraft.world.effect.MobEffect modEffect(int code) {
        return switch (code) {
            case 21 -> DynastyEffects.DRAGON_MIGHT.get();
            case 22 -> DynastyEffects.IRON_WALL.get();
            case 23 -> DynastyEffects.SWIFT_WIND.get();
            case 24 -> DynastyEffects.INTIMIDATION.get();
            case 25 -> DynastyEffects.MANDATE_OF_HEAVEN.get();
            case 26 -> DynastyEffects.LOYALTY.get();
            case 27 -> DynastyEffects.INTERNAL_INJURY.get();
            default -> null;
        };
    }

    /** 手写饰品：同样带悬浮说明（文案见 DynastyTrinketTips.LEGACY）/ legacy charm with tooltip */
    private static RegistryObject<Item> charm(String name) {
        return ITEMS.register(name, () -> new DynastyTrinketTips.Charm(name));
    }

    /**
     * 百宝妆匣开奖：从全部饰品里抽一件；前三分之一的「早期线」权重 3，高阶线权重 1。
     * Gift roll: early-line accessories are three times as likely as the late-game ones.
     */
    public static ItemStack randomGift(net.minecraft.util.RandomSource random) {
        List<RegistryObject<Item>> all = accessoryItems();
        List<Item> pool = new ArrayList<>();
        int early = Math.max(1, all.size() / 3);
        for (int i = 0; i < all.size(); i++) {
            Item item = all.get(i).get();
            if (item == null) {
                continue;
            }
            int weight = i < early ? 3 : 1;
            for (int w = 0; w < weight; w++) {
                pool.add(item);
            }
        }
        if (pool.isEmpty()) {
            return new ItemStack(DynastyRelics.REFINED_STEEL.get(), 3);
        }
        return new ItemStack(pool.get(random.nextInt(pool.size())));
    }

    /** 全部饰品 id / all accessory ids（含第三十一轮的 50 件）*/
    public static final List<String> IDS = buildIds();

    private static List<String> buildIds() {
        List<String> out = new ArrayList<>(List.of(
            "jade_pendant", "jade_bi_disc", "gold_seal_charm", "dragon_scale_charm",
            "phoenix_feather_charm", "qilin_horn_charm", "fox_tail_charm", "silk_pouch",
            "south_pointing_compass", "bronze_mirror", "heart_mirror", "jade_crown",
            "jade_cicada", "dragon_pearl", "phoenix_ring", "storm_charm",
            "moon_pendant", "tiger_crest", "jade_tortoise", "war_drum_charm",
            "cinnabar_pouch", "dragon_whisker", "tiger_token", "sun_feather",
            "war_horse_bell", "iron_waist_token", "auspicious_bell", "sea_pearl", "dragon_bone_ring",
            "cloud_brocade", "star_compass", "dragon_king_scale", "sky_feather",
            "imperial_seal_charm", "tomb_candle", "inkstone", "bamboo_flute",
            "merit_badge", "sea_conch"));
        for (Object[] row : EXTRA_TABLE) {
            out.add((String) row[0]);
        }
        return List.copyOf(out);
    }

    /** 需要注册进 Curios 的饰品物品 / items that get a Curios capability */
    public static List<RegistryObject<Item>> accessoryItems() {
        List<RegistryObject<Item>> list = new ArrayList<>();
        list.add(JADE_PENDANT);
        list.add(JADE_BI_DISC);
        list.add(GOLD_SEAL_CHARM);
        list.add(DRAGON_SCALE_CHARM);
        list.add(PHOENIX_FEATHER_CHARM);
        list.add(QILIN_HORN_CHARM);
        list.add(FOX_TAIL_CHARM);
        list.add(SILK_POUCH);
        list.add(SOUTH_POINTING_COMPASS);
        list.add(HEART_MIRROR);
        list.add(JADE_CROWN);
        list.add(JADE_CICADA);
        list.add(DRAGON_PEARL);
        list.add(PHOENIX_RING);
        list.add(STORM_CHARM);
        list.add(MOON_PENDANT);
        list.add(TIGER_CREST);
        list.add(JADE_TORTOISE);
        list.add(WAR_DRUM_CHARM);
        list.add(CINNABAR_POUCH);
        list.add(DRAGON_WHISKER);
        list.add(TIGER_TOKEN);
        list.add(SUN_FEATHER);
        list.add(WAR_HORSE_BELL);
        list.add(IRON_WAIST_TOKEN);
        list.add(AUSPICIOUS_BELL);
        list.add(SEA_PEARL);
        list.add(DRAGON_BONE_RING);
        list.add(DynastyFineItems.BRONZE_MIRROR);
        list.add(CLOUD_BROCADE);
        list.add(STAR_COMPASS);
        list.add(DRAGON_KING_SCALE);
        list.add(SKY_FEATHER);
        list.add(IMPERIAL_SEAL_CHARM);
        list.add(TOMB_CANDLE);
        list.add(INKSTONE);
        list.add(BAMBOO_FLUTE);
        list.add(MERIT_BADGE);
        list.add(SEA_CONCH);
        list.addAll(EXTRA_CHARMS);          // 第三十一轮的 50 件
        return list;
    }

    public static boolean isAccessory(ItemStack stack) {
        String id = idOf(stack);
        return id != null && IDS.contains(id);
    }

    public static String idOf(ItemStack stack) {
        if (stack == null || stack.isEmpty()) {
            return null;
        }
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(stack.getItem());
        if (id == null || !id.getNamespace().equals(Dynasty.MODID)) {
            return null;
        }
        return id.getPath();
    }

    // ---------------------------------------------------------------- 生效判定
    /** 饰品 id 的 Set 视图：生效判定 / 筛选是 O(1)（原先是 List.contains，O(n)）*/
    private static final java.util.Set<String> ID_SET = java.util.Set.copyOf(IDS);

    /** 同一 tick 内的扫描缓存：tick() 会连续问 6~7 次，不再重复扫背包与 Curios */
    private static final Map<UUID, java.util.Set<String>> SCAN_CACHE = new HashMap<>();
    private static final Map<UUID, Integer> SCAN_STAMP = new HashMap<>();

    /** 玩家登出时清掉缓存（由 DynastyWorldEvents 的登出事件调用）*/
    public static void forget(Player player) {
        UUID id = player.getUUID();
        SCAN_CACHE.remove(id);
        SCAN_STAMP.remove(id);
        APPLIED.remove(id);
        DynastyTrinketOnHit.forget(player);     // 连击状态也一起清
        DynastyTrinketLink.forget(player);      // 连携提示去重记录
    }

    public static boolean has(Player player, String id) {
        return activeIds(player).contains(id);
    }

    /**
     * 生效中的饰品：Curios 槽 + 副手 + 背包。
     *
     * 结果按「tickCount」缓存：同一个 tick 内重复调用直接复用。
     * 背包内容不可能在同一 tick 内改变，所以语义与原来完全一致，
     * 但每秒的扫描次数从 7 次降到 1 次（tick() 里 6 处 has(...) 都走缓存）。
     *
     * Active trinkets: equipped Curios; inventory fallback only without Curios.
     * The result is cached for the current tick, cutting 7 scans/second down to one.
     */
    public static java.util.Set<String> activeIds(Player player) {
        UUID uuid = player.getUUID();
        Integer stamp = SCAN_STAMP.get(uuid);
        if (stamp != null && stamp == player.tickCount) {
            java.util.Set<String> cached = SCAN_CACHE.get(uuid);
            if (cached != null) {
                return cached;
            }
        }
        java.util.Set<String> out = new java.util.LinkedHashSet<>();
        // 安装 Curios 时只计算真正佩戴的饰品；独立运行本体时保留背包兼容。
        if (!DynastyCuriosSetup.isLoaded()) {
            NonNullList<ItemStack> items = player.getInventory().items;
            for (ItemStack stack : items) {
                if (stack.isEmpty()) {
                    continue;
                }
                String id = idOf(stack);
                if (id != null) {
                    out.add(id);
                }
            }
            String offhand = idOf(player.getOffhandItem());
            if (offhand != null) {
                out.add(offhand);
            }
        }
        // Curios 槽位里的饰品（通过反射桥接，没有 Curios 时自动跳过）
        // trinkets worn in Curios slots (reflectively bridged; skipped when Curios is absent)
        DynastyCuriosSetup.collectEquipped(player, out);
        out.retainAll(ID_SET);
        SCAN_CACHE.put(uuid, out);
        SCAN_STAMP.put(uuid, player.tickCount);
        return out;
    }

    public static List<String> equippedIds(Player player) {
        return new ArrayList<>(activeIds(player));
    }

    /** 玉佩：额外 8% 减伤 / jade pendant: extra 8% reduction */
    public static float extraDamageReduction(Player player) {
        float reduction = has(player, "jade_pendant") ? 0.08F : 0.0F;
        if (has(player, "heart_mirror")) {
            reduction += 0.04F;
        }
        return reduction;
    }

    /** 金印 / 御玺佩：功名加成（取最高，不叠加）/ merit bonus, highest wins */
    public static float meritMultiplier(Player player) {
        float best = 1.0F;
        if (has(player, "gold_seal_charm")) {
            best = Math.max(best, 1.25F);
        }
        if (has(player, "imperial_seal_charm")) {
            best = Math.max(best, 1.40F);
        }
        return best;
    }

    // ---------------------------------------------------------------- 效果
    private static final Attribute[] ATTRS = {
            Attributes.MAX_HEALTH, Attributes.ARMOR, Attributes.KNOCKBACK_RESISTANCE,
            Attributes.MOVEMENT_SPEED, Attributes.LUCK, Attributes.ATTACK_DAMAGE,
            Attributes.ATTACK_SPEED, Attributes.ATTACK_KNOCKBACK};

    private static final String[] ATTR_NAMES = {
            "dynasty_trinket_health", "dynasty_trinket_armor", "dynasty_trinket_kb",
            "dynasty_trinket_speed", "dynasty_trinket_luck", "dynasty_trinket_attack",
            "dynasty_trinket_attack_speed", "dynasty_trinket_attack_knockback"};

    private static UUID uuid(String id, int attr) {
        return UUID.nameUUIDFromBytes(("dynasty_trinket_" + id + "_" + attr).getBytes());
    }

    private static void addAttr(Player player, String id, int key, int attr, double amount) {
        AttributeInstance instance = player.getAttribute(ATTRS[attr]);
        if (instance != null) {
            instance.addTransientModifier(new AttributeModifier(uuid(id, key),
                    ATTR_NAMES[attr], amount, AttributeModifier.Operation.ADDITION));
        }
    }

    /** 是否友军（战鼓只给友军加成）/ is the entity an ally of the player */
    private static boolean isAlly(Player player, LivingEntity entity) {
        if (entity == player || !entity.isAlive()) {
            return false;
        }
        if (entity instanceof net.minecraft.world.entity.animal.IronGolem
                || entity instanceof net.minecraft.world.entity.animal.SnowGolem) {
            return true;
        }
        if (entity instanceof net.minecraft.world.entity.TamableAnimal tameable) {
            return tameable.isOwnedBy(player);
        }
        return entity instanceof com.dynasty.entity.ImperialSoldier;
    }

    /** 百分比加成（例如龙珠 +25% 攻击）/ percentage modifier */
    private static void multiplyAttr(Player player, String id, int key, int attr, double ratio) {
        AttributeInstance instance = player.getAttribute(ATTRS[attr]);
        if (instance != null) {
            instance.addTransientModifier(new AttributeModifier(uuid(id, key),
                    ATTR_NAMES[attr], ratio, AttributeModifier.Operation.MULTIPLY_TOTAL));
        }
    }

    // 旧批次饰品（apply() 里的 39 件）仍用 4 参写法：UUID 就用属性号本身，
    // 和第一批完全一致，老存档换下饰品照样清得干净。
    // legacy accessories keep the 4-arg form: the UUID stays the attribute index,
    // byte-for-byte identical to the first batches.
    private static void addAttr(Player player, String id, int attr, double amount) {
        addAttr(player, id, attr, attr, amount);
    }

    private static void multiplyAttr(Player player, String id, int attr, double ratio) {
        multiplyAttr(player, id, attr, attr, ratio);
    }

    /**
     * 清掉一件饰品加过的全部属性：0~99（第一格）/ 100~199（第三格）/ 200~299 三段都清，
     * 换下饰品时不会留下幽灵加成。
     *
     * clear every slot of an accessory so removing it never leaves ghost modifiers.
     */
    static void clearAttrs(Player player, String id) {
        for (int slot = 0; slot < 3; slot++) {
            int key = slot * 100;
            for (int a = 0; a < ATTRS.length; a++) {
                AttributeInstance instance = player.getAttribute(ATTRS[a]);
                if (instance != null) {
                    instance.removeModifier(uuid(id, key + a));
                }
            }
            // 「距离」用的是 Forge 的触及距离属性，单独清一次 / clear the Forge reach modifier too
            AttributeInstance reach =
                    player.getAttribute(net.minecraftforge.common.ForgeMod.ENTITY_REACH.get());
            if (reach != null) {
                reach.removeModifier(uuid(id, key + 8));
            }
        }
    }

    /** 每 20 tick 刷新一次饰品效果 / refresh effects every second */
    public static void tick(ServerPlayer player) {
        apply(player);
        if (player.tickCount % 600 == 0 && has(player, "bronze_mirror")) {
            // 铜镜：每 30 秒净化一个负面效果 / mirror cleanses one debuff every 30s
            player.getActiveEffects().stream()
                    .filter(effect -> !effect.getEffect().isBeneficial())
                    .findFirst()
                    .ifPresent(effect -> {
                        player.removeEffect(effect.getEffect());
                        player.sendSystemMessage(net.minecraft.network.chat.Component.literal(
                                "§9[铜镜] §r映照心魔，净化了一个负面效果。"));
                    });
        }
        if (has(player, "gold_seal_charm") && player.tickCount % 1200 == 0) {
            DynastyStats.addLoyalty(player, 2);
        }
        // 凤凰指环：着火即灭火并加速 / phoenix ring
        if (has(player, "phoenix_ring") && player.isOnFire()) {
            player.clearFire();
            player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 200, 1, true, false));
            player.displayClientMessage(net.minecraft.network.chat.Component.literal(
                    "§6[凤凰指环] §r浴火而安。"), true);
        }
        // 朱砂囊：定期净化剧毒类负面效果 / cinnabar pouch
        if (has(player, "cinnabar_pouch") && player.tickCount % 40 == 0) {
            boolean cleansed = false;
            for (net.minecraft.world.effect.MobEffect bad : new net.minecraft.world.effect.MobEffect[]{
                    MobEffects.POISON, MobEffects.WITHER, MobEffects.BLINDNESS, MobEffects.HUNGER}) {
                if (player.hasEffect(bad)) {
                    player.removeEffect(bad);
                    cleansed = true;
                }
            }
            if (cleansed) {
                player.displayClientMessage(net.minecraft.network.chat.Component.literal(
                        "§6[朱砂囊] §r驱散了体内的毒素。"), true);
            }
        }
        // 虎符残片：周期性威慑周围敌人 / tiger crest
        if (has(player, "tiger_crest") && player.tickCount % 800 == 0) {
            int cleared = 0;
            for (net.minecraft.world.entity.Mob mob : player.level().getEntitiesOfClass(
                    net.minecraft.world.entity.Mob.class, player.getBoundingBox().inflate(8.0D),
                    m -> m.getTarget() == player)) {
                mob.setTarget(null);
                cleared++;
            }
            if (cleared > 0) {
                player.displayClientMessage(net.minecraft.network.chat.Component.literal(
                        "§6[虎符残片] §r威压八面，" + cleared + " 名敌人退避。"), true);
            }
        }
        // 竹笛：每 5 秒吹一曲，8 格内敌人缓慢 / bamboo flute
        if (has(player, "bamboo_flute") && player.tickCount % 100 == 0) {
            int slowed = 0;
            for (net.minecraft.world.entity.LivingEntity target : player.level().getEntitiesOfClass(
                    net.minecraft.world.entity.LivingEntity.class, player.getBoundingBox().inflate(8.0D),
                    e -> e != player && !isAlly(player, e))) {
                target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 0, true, false));
                slowed++;
            }
            if (slowed > 0) {
                player.displayClientMessage(net.minecraft.network.chat.Component.literal(
                        "§b[竹笛] §r笛声悠远，" + slowed + " 名敌人步伐迟滞。"), true);
            }
        }
    }

    /**
     * 上一轮真正加过属性的饰品：只清理这些。
     *
     * 原来每秒对全部 119 件饰品各清一遍 8 个属性（空手玩家也白跑约 950 次属性操作），
     * 现在只清「上一轮的」与「本轮新出现的」，仍然保留「先清再加」的幂等语义。
     *
     * Accessories that actually had attributes applied last round - only those get cleared,
     * keeping the idempotent clear-then-add behaviour while dropping the useless work.
     */
    private static final Map<UUID, java.util.Set<String>> APPLIED = new HashMap<>();

    private static java.util.Set<String> apply(ServerPlayer player) {
        java.util.Set<String> active = activeIds(player);
        java.util.Set<String> previous = APPLIED.get(player.getUUID());
        if (previous != null) {
            for (String id : previous) {
                clearAttrs(player, id);
            }
        }
        for (String id : active) {
            if (previous == null || !previous.contains(id)) {
                clearAttrs(player, id);
            }
        }
        for (String id : active) {
            switch (id) {
                case "jade_bi_disc" -> addAttr(player, id, 0, 150.0D);
                case "dragon_scale_charm" -> {
                    addAttr(player, id, 1, 12.0D);
                    addAttr(player, id, 2, 0.4D);
                }
                case "phoenix_feather_charm" -> {
                    addAttr(player, id, 3, 0.10D);
                    player.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 60, 0, true, false));
                }
                case "qilin_horn_charm" -> {
                    // 麒麟角坠：防御向 —— 再生 + 攻击 +10% + 护甲 +4
                    multiplyAttr(player, id, 5, 0.10D);
                    addAttr(player, id, 1, 4.0D);
                    player.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 60, 0, true, false));
                }
                case "fox_tail_charm" -> {
                    player.addEffect(new MobEffectInstance(MobEffects.JUMP, 60, 1, true, false));
                    addAttr(player, id, 3, 0.05D);
                }
                case "silk_pouch" -> {
                    player.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 60, 0, true, false));
                    player.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 300, 0, true, false));
                }
                case "south_pointing_compass" ->
                        player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 60, 0, true, false));
                case "heart_mirror" -> addAttr(player, id, 1, 8.0D);
                case "jade_crown" -> addAttr(player, id, 0, 220.0D);
                case "dragon_pearl" -> {
                    multiplyAttr(player, id, 5, 0.25D);      // 攻击 +25%
                    addAttr(player, id, 2, 0.3D);           // 抗击退
                }
                case "phoenix_ring" -> {
                    player.addEffect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 60, 0, true, false));
                    addAttr(player, id, 3, 0.03D);
                }
                case "storm_charm" -> {
                    boolean storm = player.level().isThundering() || player.level().isRaining();
                    player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 60, 0, true, false));
                    if (storm) {
                        player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 60, 1, true, false));
                        player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 60, 0, true, false));
                    }
                }
                case "moon_pendant" -> {
                    if (!player.level().isDay()) {
                        // 明月佩：夜战向 —— 夜视 + 攻击 +10% + 攻速 +10%
                        player.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 300, 0, true, false));
                        multiplyAttr(player, id, 6, 0.10D);
                        multiplyAttr(player, id, 5, 0.10D);
                    }
                }
                case "jade_cicada" -> {
                    // 残血保命（不是回血：只给抗性与速度）/ low-health protection
                    if (player.getHealth() <= player.getMaxHealth() * 0.3F) {
                        player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 200, 1, true, false));
                        player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 200, 0, true, false));
                    }
                }
                case "jade_tortoise" -> {
                    // 水战：呼吸 + 海豚 + 抗性 / underwater combat
                    player.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 60, 0, true, false));
                    player.addEffect(new MobEffectInstance(MobEffects.DOLPHINS_GRACE, 60, 0, true, false));
                    player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 60, 0, true, false));
                }
                case "war_drum_charm" -> {
                    player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 60, 0, true, false));
                    if (player.tickCount % 60 == 0) {
                        // 战鼓：给 12 格内的禁军 / 铁傀儡 / 已驯服宠物加力量
                        for (LivingEntity ally : player.level().getEntitiesOfClass(LivingEntity.class,
                                player.getBoundingBox().inflate(12.0D), e -> isAlly(player, e))) {
                            ally.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 120, 0, true, false));
                        }
                    }
                }
                case "dragon_whisker" -> {
                    multiplyAttr(player, id, 6, 0.15D);     // 攻速 +15%
                    addAttr(player, id, 7, 0.5D);          // 击退 +0.5
                }
                case "tiger_token" -> {
                    multiplyAttr(player, id, 3, 0.08D);    // 移速 +8%
                    player.addEffect(new MobEffectInstance(MobEffects.JUMP, 60, 0, true, false));
                }
                case "sun_feather" -> {
                    if (player.level().isDay()) {
                        // 金乌翎：白天强攻 —— 攻击 +15%、击退 +0.3
                        multiplyAttr(player, id, 5, 0.15D);
                        addAttr(player, id, 7, 0.3D);
                    } else {
                        player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 60, 0, true, false));
                    }
                }
                case "iron_waist_token" -> {
                    addAttr(player, id, 0, 150.0D);
                    addAttr(player, id, 1, 6.0D);
                    addAttr(player, id, 2, 0.2D);
                }
                case "auspicious_bell" -> {
                    // 瑞兽铃：功能向 —— 攻速 +10%，每 20 秒自动驱散虚弱/缓慢
                    multiplyAttr(player, id, 6, 0.10D);
                    if (player.tickCount % 400 == 0
                            && (player.hasEffect(MobEffects.WEAKNESS) || player.hasEffect(MobEffects.MOVEMENT_SLOWDOWN))) {
                        player.removeEffect(MobEffects.WEAKNESS);
                        player.removeEffect(MobEffects.MOVEMENT_SLOWDOWN);
                        player.displayClientMessage(net.minecraft.network.chat.Component.literal(
                                "§d[瑞兽铃] §r铃音清越，驱散了身上的虚弱与迟滞。"), true);
                    }
                }
                case "war_horse_bell" -> {
                    // 战马铃：骑乘时强化坐骑，步战时自己 +5 护甲
                    if (player.isPassenger() && player.getVehicle() instanceof LivingEntity mount) {
                        mount.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 60, 1, true, false));
                        mount.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 60, 0, true, false));
                    } else {
                        addAttr(player, id, 1, 5.0D);
                    }
                }
                case "sea_pearl" -> {
                    // 避水珠：水下呼吸 + 海豚 + 水下攻防（战斗向）
                    player.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 60, 0, true, false));
                    player.addEffect(new MobEffectInstance(MobEffects.DOLPHINS_GRACE, 60, 0, true, false));
                    if (player.isUnderWater()) {
                        multiplyAttr(player, id, 5, 0.20D);
                        addAttr(player, id, 1, 6.0D);
                    }
                }
                case "dragon_bone_ring" -> {
                    // 龙骨戒：护甲 + 抗击退 + 攻击
                    addAttr(player, id, 1, 10.0D);
                    addAttr(player, id, 2, 0.3D);
                    multiplyAttr(player, id, 5, 0.08D);
                }
                // ---- 第二十轮扩充的 10 件 / ten extra accessories ----
                case "cloud_brocade" -> {
                    // 云锦囊：生命 +160、护甲 +8（中期最舒服的一件）
                    addAttr(player, id, 0, 160.0D);
                    addAttr(player, id, 1, 8.0D);
                }
                case "star_compass" -> {
                    // 星盘：攻击 +12%、移速 +6%
                    multiplyAttr(player, id, 5, 0.12D);
                    multiplyAttr(player, id, 3, 0.06D);
                }
                case "dragon_king_scale" -> {
                    // 龙王逆鳞：攻击 +20%、抗击退 +0.5、护甲 +6（龙宫终极饰品）
                    multiplyAttr(player, id, 5, 0.20D);
                    addAttr(player, id, 2, 0.5D);
                    addAttr(player, id, 1, 6.0D);
                }
                case "sky_feather" -> {
                    // 天羽：跳跃提升 II + 移速 +8%
                    multiplyAttr(player, id, 3, 0.08D);
                    player.addEffect(new MobEffectInstance(MobEffects.JUMP, 60, 1, true, false));
                }
                case "imperial_seal_charm" -> {
                    // 御玺佩：功名 +40%（在 meritMultiplier 里）+ 生命 +100、护甲 +4
                    addAttr(player, id, 0, 100.0D);
                    addAttr(player, id, 1, 4.0D);
                }
                case "tomb_candle" -> {
                    // 长明烛：夜视 + 每 2 秒清一次凋零（地府生存）
                    player.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 400, 0, true, false));
                    if (player.tickCount % 40 == 0 && player.hasEffect(MobEffects.WITHER)) {
                        player.removeEffect(MobEffects.WITHER);
                    }
                }
                case "inkstone" -> {
                    // 砚台：攻速 +12%、攻击 +6%
                    multiplyAttr(player, id, 6, 0.12D);
                    multiplyAttr(player, id, 5, 0.06D);
                }
                case "merit_badge" -> {
                    // 功牌：生命 +200、抗击退 +0.3
                    addAttr(player, id, 0, 200.0D);
                    addAttr(player, id, 2, 0.3D);
                }
                case "sea_conch" -> {
                    // 海螺：水下呼吸；水下时攻击 +30%、护甲 +10
                    player.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 60, 0, true, false));
                    if (player.isUnderWater()) {
                        multiplyAttr(player, id, 5, 0.30D);
                        addAttr(player, id, 1, 10.0D);
                    }
                }
                default -> {
                    // 玉佩 / 金印 / 铜镜 通过事件与定时逻辑生效
                }
            }
        }
        applyExtra(player, active);          // 第三十一轮的 50 件（表驱动）
        DynastyTrinketLink.apply(player, active);   // 同系连携（2/3/4 件档位）
        if (player.getHealth() > player.getMaxHealth()) {
            player.setHealth(player.getMaxHealth());
        }
        APPLIED.put(player.getUUID(), active);   // 记下本轮，下一轮只清这些
        return active;
    }
}
