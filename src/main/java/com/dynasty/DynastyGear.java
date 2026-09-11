package com.dynasty;

import com.dynasty.Dynasty;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.PickaxeItem;
import net.minecraft.world.item.SwordItem;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

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
    public static final RegistryObject<Item> SWORD_BRONZE = sword("sword_bronze", DynastyTiers.BRONZE, 499, -2.4F);      // 1000
    public static final RegistryObject<Item> SWORD_SILVER = sword("sword_silver", DynastyTiers.OFFICIAL_SILVER, 499, -2.2F); // 1200
    public static final RegistryObject<Item> SWORD_JADE = sword("sword_jade", DynastyTiers.JADE, 599, -2.0F);           // 1500
    public static final RegistryObject<Item> SWORD_DRAGON_CRYSTAL = sword("sword_dragon_crystal", DynastyTiers.DRAGON_CRYSTAL, 599, -1.8F); // 1900

    /** 方天画戟 / Fangtian Halberd：全模组最强单手 |
     *  the strongest weapon of the mod (2048 = 原版攻击力上限) */
    public static final RegistryObject<Item> HALBERD_FANGTIAN =
            ITEMS.register("halberd_fangtian", () -> new SwordItem(DynastyTiers.DRAGON_CRYSTAL, 747, -2.6F, new Item.Properties()));

    // ---- 工具 / Tools ----
    public static final RegistryObject<Item> PICKAXE_JADE = pickaxe("pickaxe_jade", DynastyTiers.JADE, 1099, -2.8F);    // 2000
    public static final RegistryObject<Item> PICKAXE_DRAGON_CRYSTAL =
            pickaxe("pickaxe_dragon_crystal", DynastyTiers.DRAGON_CRYSTAL, 747, -2.8F);                                 // 2048

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
}
