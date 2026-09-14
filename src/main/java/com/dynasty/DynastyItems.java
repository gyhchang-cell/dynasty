package com.dynasty;

import com.dynasty.Dynasty;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * Dynasty 普通物品：货币、材料、文书、食物。
 * Dynasty basic items: coins, materials, documents, food.
 */
@SuppressWarnings("null")
public class DynastyItems {

    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, Dynasty.MODID);

    private static RegistryObject<Item> basic(String name) {
        return ITEMS.register(name, () -> new Item(new Item.Properties()));
    }

    // ---- 货币 / Currency ----
    public static final RegistryObject<Item> COPPER_COIN = basic("copper_coin");
    public static final RegistryObject<Item> SILVER_COIN = basic("silver_coin");
    public static final RegistryObject<Item> GOLD_COIN = basic("gold_coin");
    public static final RegistryObject<Item> JADE_COIN = basic("jade_coin");
    public static final RegistryObject<Item> DRAGON_COIN = basic("dragon_coin");

    // ---- 材料 / Materials ----
    public static final RegistryObject<Item> BRONZE_INGOT = basic("bronze_ingot");
    public static final RegistryObject<Item> SILVER_INGOT = basic("silver_ingot");
    public static final RegistryObject<Item> JADE = basic("jade");
    public static final RegistryObject<Item> DRAGON_SCALE = basic("dragon_scale");
    public static final RegistryObject<Item> DRAGON_CRYSTAL = basic("dragon_crystal");
    public static final RegistryObject<Item> CINNABAR = basic("cinnabar");
    public static final RegistryObject<Item> TALISMAN_PAPER = ITEMS.register("talisman_paper",
            () -> new DynastyUsables.TalismanItem(new Item.Properties().stacksTo(16)));

    // ---- 玺印与文书 / Seals & documents ----
    public static final RegistryObject<Item> JADE_SEAL = ITEMS.register("jade_seal",
            () -> new DynastyUsables.SealItem(new Item.Properties().stacksTo(1)));
    public static final RegistryObject<Item> OFFICIAL_SEAL = basic("official_seal");
    public static final RegistryObject<Item> EDICT = ITEMS.register("edict",
            () -> new DynastyUsables.EdictItem(new Item.Properties().stacksTo(16)));
    public static final RegistryObject<Item> TIGER_TALLY = ITEMS.register("tiger_tally",
            () -> new DynastyUsables.TallyItem(new Item.Properties().stacksTo(1)));
    public static final RegistryObject<Item> EXAM_PAPER = ITEMS.register("exam_paper",
            () -> new DynastyUsables.ExamPaperItem(new Item.Properties().stacksTo(16)));

    public static final RegistryObject<Item> DYNASTY_GUIDE = ITEMS.register("dynasty_guide",
            () -> new DynastyUsables.GuideItem(new Item.Properties().stacksTo(1)));

    // ---- 食物 / Food ----
    public static final RegistryObject<Item> MOONCAKE = ITEMS.register("mooncake",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder()
                    .nutrition(6).saturationMod(0.6F).build())));

    public static final RegistryObject<Item> DUMPLING = ITEMS.register("dumpling",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder()
                    .nutrition(5).saturationMod(0.6F).build())));

    public static final RegistryObject<Item> TEA = ITEMS.register("tea",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder()
                    .nutrition(3).saturationMod(0.3F).fast().build())));

    public static final RegistryObject<Item> CANDIED_HAWTHORN = ITEMS.register("candied_hawthorn",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder()
                    .nutrition(4).saturationMod(0.5F).build())));

    public static final RegistryObject<Item> DRAGON_BEARD_CANDY = ITEMS.register("dragon_beard_candy",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder()
                    .nutrition(3).saturationMod(0.4F).fast().build())));

    public static final RegistryObject<Item> HOTPOT = ITEMS.register("hotpot",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder()
                    .nutrition(10).saturationMod(1.0F).build())));

    public static final RegistryObject<Item> WINE = ITEMS.register("wine",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder()
                    .nutrition(2).saturationMod(0.2F).alwaysEat().build())));

    public static final RegistryObject<Item> IMMORTAL_PEACH = ITEMS.register("immortal_peach",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder()
                    .nutrition(8).saturationMod(1.2F).alwaysEat().build())));

    // ---- 丹药 / Pills ----
    public static final RegistryObject<Item> PILL_LONGEVITY = ITEMS.register("pill_longevity",
            () -> new DynastyUsables.PillItem(new Item.Properties().stacksTo(16),
                    net.minecraft.world.effect.MobEffects.REGENERATION, 30, 1));

    public static final RegistryObject<Item> PILL_FOCUS = ITEMS.register("pill_focus",
            () -> new DynastyUsables.PillItem(new Item.Properties().stacksTo(16),
                    net.minecraft.world.effect.MobEffects.DIG_SPEED, 45, 0));

    public static final RegistryObject<Item> HEALING_SALVE = ITEMS.register("healing_salve",
            () -> new DynastyUsables.PillItem(new Item.Properties().stacksTo(16),
                    net.minecraft.world.effect.MobEffects.HEAL, 1, 1));

    // ---- 药水（酿造台）/ Potions (brewing stand) ----
    public static final RegistryObject<Item> DYNASTY_POTION = ITEMS.register("dynasty_potion",
            () -> new net.minecraft.world.item.PotionItem(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> DYNASTY_SPLASH_POTION = ITEMS.register("dynasty_splash_potion",
            () -> new net.minecraft.world.item.SplashPotionItem(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> DYNASTY_LINGERING_POTION = ITEMS.register("dynasty_lingering_potion",
            () -> new net.minecraft.world.item.LingeringPotionItem(new Item.Properties().stacksTo(1)));

    // ---- 神兽材料 / Mythical beast materials ----
    public static final RegistryObject<Item> QILIN_HORN = basic("qilin_horn");
    public static final RegistryObject<Item> PHOENIX_FEATHER = basic("phoenix_feather");
    public static final RegistryObject<Item> FOX_TAIL = basic("fox_tail");

    // ---- 刷怪蛋 / Spawn eggs ----
    public static final RegistryObject<Item> TERRACOTTA_WARRIOR_SPAWN_EGG = ITEMS.register("terracotta_warrior_spawn_egg",
            () -> new net.minecraftforge.common.ForgeSpawnEggItem(
                    com.dynasty.entity.DynastyEntities.TERRACOTTA_WARRIOR,
                    0x9E6B3A, 0x4A2E14, new Item.Properties()));

    public static final RegistryObject<Item> IMPERIAL_SOLDIER_SPAWN_EGG = ITEMS.register("imperial_soldier_spawn_egg",
            () -> new net.minecraftforge.common.ForgeSpawnEggItem(
                    com.dynasty.entity.DynastyEntities.IMPERIAL_SOLDIER,
                    0xB03A2E, 0xE8C86A, new Item.Properties()));

    public static final RegistryObject<Item> UNDEAD_FIRST_EMPEROR_SPAWN_EGG = ITEMS.register("undead_first_emperor_spawn_egg",
            () -> new net.minecraftforge.common.ForgeSpawnEggItem(
                    com.dynasty.entity.DynastyEntities.UNDEAD_FIRST_EMPEROR,
                    0x5B1F86, 0xE8B94E, new Item.Properties()));

    private static RegistryObject<Item> egg(String name,
                                            java.util.function.Supplier<? extends net.minecraft.world.entity.EntityType<? extends net.minecraft.world.entity.Mob>> type,
                                            int primary, int secondary) {
        return ITEMS.register(name, () -> new net.minecraftforge.common.ForgeSpawnEggItem(
                type, primary, secondary, new Item.Properties()));
    }

    public static final RegistryObject<Item> JADE_GUARD_SPAWN_EGG = egg("jade_guard_spawn_egg",
            com.dynasty.entity.DynastyEntities.JADE_GUARD, 0x3E6B52, 0xE8C86A);
    public static final RegistryObject<Item> SOUL_SOLDIER_SPAWN_EGG = egg("soul_soldier_spawn_egg",
            com.dynasty.entity.DynastyEntities.SOUL_SOLDIER, 0x2E2E3A, 0x6B6BC0);
    public static final RegistryObject<Item> THUNDER_ENVOY_SPAWN_EGG = egg("thunder_envoy_spawn_egg",
            com.dynasty.entity.DynastyEntities.THUNDER_ENVOY, 0x2E3E8B, 0x7FE8F0);
    public static final RegistryObject<Item> MERFOLK_SPAWN_EGG = egg("merfolk_spawn_egg",
            com.dynasty.entity.DynastyEntities.MERFOLK, 0x1E5E6B, 0xE8E0B0);
    public static final RegistryObject<Item> MINISTER_SPAWN_EGG = egg("minister_spawn_egg",
            com.dynasty.entity.DynastyEntities.MINISTER, 0x2E4A8B, 0xE8D9A0);
    public static final RegistryObject<Item> ASSASSIN_SPAWN_EGG = egg("assassin_spawn_egg",
            com.dynasty.entity.DynastyEntities.ASSASSIN, 0x1B1B22, 0x8B1F1F);
    public static final RegistryObject<Item> ARCHER_SPAWN_EGG = egg("archer_spawn_egg",
            com.dynasty.entity.DynastyEntities.ARCHER, 0x3F6B3F, 0xD9C08B);
    public static final RegistryObject<Item> ROYAL_GUARD_SPAWN_EGG = egg("royal_guard_spawn_egg",
            com.dynasty.entity.DynastyEntities.ROYAL_GUARD, 0x7A1F2B, 0xE8C86A);
    public static final RegistryObject<Item> REBEL_SOLDIER_SPAWN_EGG = egg("rebel_soldier_spawn_egg",
            com.dynasty.entity.DynastyEntities.REBEL_SOLDIER, 0x6B5B3A, 0xB03A2E);
    public static final RegistryObject<Item> NIAN_BEAST_SPAWN_EGG = egg("nian_beast_spawn_egg",
            com.dynasty.entity.DynastyEntities.NIAN_BEAST, 0xB01F1F, 0xF5D76E);
    public static final RegistryObject<Item> QILIN_SPAWN_EGG = egg("qilin_spawn_egg",
            com.dynasty.entity.DynastyEntities.QILIN, 0x2E8B57, 0xE8D46A);
    public static final RegistryObject<Item> PHOENIX_SPAWN_EGG = egg("phoenix_spawn_egg",
            com.dynasty.entity.DynastyEntities.PHOENIX, 0xD9481F, 0xFFD75E);
    public static final RegistryObject<Item> NINE_TAILED_FOX_SPAWN_EGG = egg("nine_tailed_fox_spawn_egg",
            com.dynasty.entity.DynastyEntities.NINE_TAILED_FOX, 0xE8A24E, 0xF5EDE0);
    public static final RegistryObject<Item> DRAGON_EMPEROR_SPAWN_EGG = egg("dragon_emperor_spawn_egg",
            com.dynasty.entity.DynastyEntities.DRAGON_EMPEROR, 0x8B0000, 0xFFD700);
    public static final RegistryObject<Item> REBEL_GENERAL_SPAWN_EGG = egg("rebel_general_spawn_egg",
            com.dynasty.entity.DynastyEntities.REBEL_GENERAL, 0x4A3A2A, 0xC0392B);
    public static final RegistryObject<Item> EUNUCH_MASTERMIND_SPAWN_EGG = egg("eunuch_mastermind_spawn_egg",
            com.dynasty.entity.DynastyEntities.EUNUCH_MASTERMIND, 0x4B2A5A, 0xC2A0E0);
    public static final RegistryObject<Item> NINE_HEAVEN_GENERAL_SPAWN_EGG = egg("nine_heaven_general_spawn_egg",
            com.dynasty.entity.DynastyEntities.NINE_HEAVEN_GENERAL, 0x2E6B8B, 0xFFF3B0);

    /** 天将令：九霄天将的信物（可到法阵·祭坛重复召唤）/ the Nine-Heaven token */
    public static final RegistryObject<Item> SKY_TOKEN = basic("sky_token");

    /** 龙宫玉印：东海龙王的信物 / the Dragon King's seal */
    public static final RegistryObject<Item> SEA_TOKEN = basic("sea_token");
    public static final RegistryObject<Item> DRAGON_KING_SPAWN_EGG = egg("dragon_king_spawn_egg",
            com.dynasty.entity.DynastyEntities.DRAGON_KING, 0x1B3A6B, 0x7BE3C8);
}
