package com.dynasty;

import com.dynasty.Dynasty;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.PickaxeItem;
import net.minecraft.world.item.SwordItem;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.ArrayList;
import java.util.List;

/**
 * Dynasty 装备：武器、工具、盔甲。
 * Dynasty gear: weapons, tools, armor.
 */
@SuppressWarnings("null")
public class DynastyGear {

    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, Dynasty.MODID);

    private static RegistryObject<Item> sword(String name, net.minecraft.world.item.Tier tier, int dmg, float speed) {
        return ITEMS.register(name, () -> new SwordItem(tier, dmg, speed, new Item.Properties()));
    }

    private static RegistryObject<Item> pickaxe(String name, net.minecraft.world.item.Tier tier, int dmg, float speed) {
        return ITEMS.register(name, () -> new PickaxeItem(tier, dmg, speed, new Item.Properties()));
    }

    private static RegistryObject<Item> armor(String name, net.minecraft.world.item.ArmorMaterial material, ArmorItem.Type type) {
        return ITEMS.register(name, () -> new ArmorItem(material, type, new Item.Properties()));
    }

    // ---- 剑 / Swords（总攻击力 = 基础1 + 材质加成 + 参数）----
    public static final RegistryObject<Item> SWORD_BRONZE = sword("sword_bronze", DynastyTiers.BRONZE, 11, -2.4F);       // 34
    public static final RegistryObject<Item> SWORD_SILVER = sword("sword_silver", DynastyTiers.OFFICIAL_SILVER, 91, -2.2F); // 132
    public static final RegistryObject<Item> SWORD_JADE = sword("sword_jade", DynastyTiers.JADE, 99, -2.0F);            // 170
    public static final RegistryObject<Item> SWORD_DRAGON_CRYSTAL = sword("sword_dragon_crystal", DynastyTiers.DRAGON_CRYSTAL, 1259, -1.8F); // 1000

    /** 方天画戟 / Fangtian Halberd：无双神兵（横扫）1400 / the sweeping halberd */
    public static final RegistryObject<Item> HALBERD_FANGTIAN =
            ITEMS.register("halberd_fangtian", () -> new SwordItem(DynastyTiers.DRAGON_CRYSTAL, 1759, -2.6F, new Item.Properties()));

    /** 分水三叉戟 / Sea-Parting Trident：龙宫神器 1500，水下额外加成在 DynastyCombatEvents 里结算 */
    public static final RegistryObject<Item> SEA_TRIDENT =
            ITEMS.register("sea_trident", () -> new SwordItem(DynastyTiers.DRAGON_CRYSTAL, 1959, -2.2F, new Item.Properties()));

    // ---- 工具 / Tools ----
    public static final RegistryObject<Item> PICKAXE_JADE = pickaxe("pickaxe_jade", DynastyTiers.JADE, 99, -2.8F);       // 170
    public static final RegistryObject<Item> PICKAXE_DRAGON_CRYSTAL =
            pickaxe("pickaxe_dragon_crystal", DynastyTiers.DRAGON_CRYSTAL, 279, -2.8F);                                 // 420

    // ---- 布衣 / Cloth armor（开局套，丝绸可做）----
    public static final RegistryObject<Item> CLOTH_HELMET = armor("cloth_helmet", DynastyArmorMaterials.CLOTH, ArmorItem.Type.HELMET);
    public static final RegistryObject<Item> CLOTH_CHESTPLATE = armor("cloth_chestplate", DynastyArmorMaterials.CLOTH, ArmorItem.Type.CHESTPLATE);
    public static final RegistryObject<Item> CLOTH_LEGGINGS = armor("cloth_leggings", DynastyArmorMaterials.CLOTH, ArmorItem.Type.LEGGINGS);
    public static final RegistryObject<Item> CLOTH_BOOTS = armor("cloth_boots", DynastyArmorMaterials.CLOTH, ArmorItem.Type.BOOTS);

    // ---- 玉甲 / Jade armor ----
    public static final RegistryObject<Item> JADE_HELMET = armor("jade_helmet", DynastyArmorMaterials.JADE, ArmorItem.Type.HELMET);
    public static final RegistryObject<Item> JADE_CHESTPLATE = armor("jade_chestplate", DynastyArmorMaterials.JADE, ArmorItem.Type.CHESTPLATE);
    public static final RegistryObject<Item> JADE_LEGGINGS = armor("jade_leggings", DynastyArmorMaterials.JADE, ArmorItem.Type.LEGGINGS);
    public static final RegistryObject<Item> JADE_BOOTS = armor("jade_boots", DynastyArmorMaterials.JADE, ArmorItem.Type.BOOTS);

    // ---- 龙鳞甲 / Dragon scale armor ----
    public static final RegistryObject<Item> DRAGON_SCALE_HELMET = armor("dragon_scale_helmet", DynastyArmorMaterials.DRAGON_SCALE, ArmorItem.Type.HELMET);
    public static final RegistryObject<Item> DRAGON_SCALE_CHESTPLATE = armor("dragon_scale_chestplate", DynastyArmorMaterials.DRAGON_SCALE, ArmorItem.Type.CHESTPLATE);
    public static final RegistryObject<Item> DRAGON_SCALE_LEGGINGS = armor("dragon_scale_leggings", DynastyArmorMaterials.DRAGON_SCALE, ArmorItem.Type.LEGGINGS);
    public static final RegistryObject<Item> DRAGON_SCALE_BOOTS = armor("dragon_scale_boots", DynastyArmorMaterials.DRAGON_SCALE, ArmorItem.Type.BOOTS);

    // ---- 将军铠 / General armor ----
    public static final RegistryObject<Item> GENERAL_HELMET = armor("general_helmet", DynastyArmorMaterials.GENERAL, ArmorItem.Type.HELMET);
    public static final RegistryObject<Item> GENERAL_CHESTPLATE = armor("general_chestplate", DynastyArmorMaterials.GENERAL, ArmorItem.Type.CHESTPLATE);
    public static final RegistryObject<Item> GENERAL_LEGGINGS = armor("general_leggings", DynastyArmorMaterials.GENERAL, ArmorItem.Type.LEGGINGS);
    public static final RegistryObject<Item> GENERAL_BOOTS = armor("general_boots", DynastyArmorMaterials.GENERAL, ArmorItem.Type.BOOTS);

    // ---- 玄天真龙甲 / Xuantian true dragon armor（终盘，需龙帝玉玺）----
    public static final RegistryObject<Item> XUANTIAN_HELMET = armor("xuantian_helmet", DynastyArmorMaterials.XUANTIAN, ArmorItem.Type.HELMET);
    public static final RegistryObject<Item> XUANTIAN_CHESTPLATE = armor("xuantian_chestplate", DynastyArmorMaterials.XUANTIAN, ArmorItem.Type.CHESTPLATE);
    public static final RegistryObject<Item> XUANTIAN_LEGGINGS = armor("xuantian_leggings", DynastyArmorMaterials.XUANTIAN, ArmorItem.Type.LEGGINGS);
    public static final RegistryObject<Item> XUANTIAN_BOOTS = armor("xuantian_boots", DynastyArmorMaterials.XUANTIAN, ArmorItem.Type.BOOTS);

    // ---- 鲛绡甲 / Sea Silk（龙鳞套 → 鲛绡套，水战轻甲）----
    public static final RegistryObject<Item> SEA_SILK_HELMET = armor("sea_silk_helmet", DynastyArmorMaterials.SEA_SILK, ArmorItem.Type.HELMET);
    public static final RegistryObject<Item> SEA_SILK_CHESTPLATE = armor("sea_silk_chestplate", DynastyArmorMaterials.SEA_SILK, ArmorItem.Type.CHESTPLATE);
    public static final RegistryObject<Item> SEA_SILK_LEGGINGS = armor("sea_silk_leggings", DynastyArmorMaterials.SEA_SILK, ArmorItem.Type.LEGGINGS);
    public static final RegistryObject<Item> SEA_SILK_BOOTS = armor("sea_silk_boots", DynastyArmorMaterials.SEA_SILK, ArmorItem.Type.BOOTS);

    // ---- 玄铁重铠 / Dark Iron（鲛绡套 → 玄铁重铠，护甲最高）----
    public static final RegistryObject<Item> DARK_IRON_HELMET = armor("dark_iron_helmet", DynastyArmorMaterials.DARK_IRON, ArmorItem.Type.HELMET);
    public static final RegistryObject<Item> DARK_IRON_CHESTPLATE = armor("dark_iron_chestplate", DynastyArmorMaterials.DARK_IRON, ArmorItem.Type.CHESTPLATE);
    public static final RegistryObject<Item> DARK_IRON_LEGGINGS = armor("dark_iron_leggings", DynastyArmorMaterials.DARK_IRON, ArmorItem.Type.LEGGINGS);
    public static final RegistryObject<Item> DARK_IRON_BOOTS = armor("dark_iron_boots", DynastyArmorMaterials.DARK_IRON, ArmorItem.Type.BOOTS);

    // ------------------------------------------------------------------
    // 第二十轮扩充：10 套新盔甲（竹 / 皮 / 织锦 / 青铜 / 白银 / 朱砂 / 凤凰 / 麒麟 / 天将 / 龙王）
    // 用表格注册 —— 以后加一套只要在 EXTRA_SET_TABLE 里加一行，
    // 物品、贴图名、配方（gen_armor2.py 的 SETS 表）三处名字一致即可。
    // Ten extra sets registered from a table; add one line per new set.
    // ------------------------------------------------------------------
    private static final Object[][] EXTRA_SET_TABLE = {
            {"bamboo", DynastyArmorMaterials.BAMBOO},
            {"leather", DynastyArmorMaterials.LEATHER},
            {"brocade", DynastyArmorMaterials.BROCADE},
            {"bronze", DynastyArmorMaterials.BRONZE},
            {"silver", DynastyArmorMaterials.SILVER},
            {"cinnabar", DynastyArmorMaterials.CINNABAR},
            {"phoenix", DynastyArmorMaterials.PHOENIX},
            {"qilin", DynastyArmorMaterials.QILIN},
            {"sky", DynastyArmorMaterials.SKY},
            {"draco_king", DynastyArmorMaterials.DRACO_KING},
            // ---- 第三十一轮：10 套终盘甲（四象 / 星斗 / 道门）----
            {"xuanwu", DynastyArmorMaterials.XUANWU},
            {"zhuque", DynastyArmorMaterials.ZHUQUE},
            {"qinglong", DynastyArmorMaterials.QINGLONG},
            {"baihu", DynastyArmorMaterials.BAIHU},
            {"beidou", DynastyArmorMaterials.BEIDOU},
            {"tiangang", DynastyArmorMaterials.TIANGANG},
            {"disha", DynastyArmorMaterials.DISHA},
            {"taiyi", DynastyArmorMaterials.TAIYI},
            {"ziwei", DynastyArmorMaterials.ZIWEI},
            {"hunyuan", DynastyArmorMaterials.HUNYUAN},
            // ---- 第三十二轮：毕业甲（两条流派线终点合体）----
            {"hongmeng", DynastyArmorMaterials.HONGMENG},
    };

    /** 扩展套装的 40 件物品（头/胸/腿/靴 顺序）/ every item of the ten extra sets */
    public static final List<RegistryObject<Item>> EXTRA_ARMOR = registerExtraSets();

    private static List<RegistryObject<Item>> registerExtraSets() {
        List<RegistryObject<Item>> out = new ArrayList<>();
        for (Object[] entry : EXTRA_SET_TABLE) {
            String id = (String) entry[0];
            ArmorMaterial material = (ArmorMaterial) entry[1];
            out.add(armor(id + "_helmet", material, ArmorItem.Type.HELMET));
            out.add(armor(id + "_chestplate", material, ArmorItem.Type.CHESTPLATE));
            out.add(armor(id + "_leggings", material, ArmorItem.Type.LEGGINGS));
            out.add(armor(id + "_boots", material, ArmorItem.Type.BOOTS));
        }
        return out;
    }
}
