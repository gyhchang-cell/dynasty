package com.sammy.malum.config;

import net.neoforged.neoforge.common.*;
import org.apache.commons.lang3.tuple.Pair;
import team.lodestar.lodestone.modules.core.config.LodestoneConfig;

import static com.sammy.malum.MalumMod.MALUM;

public class CommonConfig extends LodestoneConfig {


    public static ConfigValueHolder<Boolean> HIDE_RECIPES = new ConfigValueHolder<>(MALUM, "common/progression", (builder ->
            builder.comment("If set to true, malum will hide some of it's content related to a certain feature. This is the intended way to play the mod.")
                    .define("hide_recipes", true)));


    public static ConfigValueHolder<Boolean> AWARD_CODEX_ON_KILL = new ConfigValueHolder<>(MALUM, "common/codex", (builder ->
            builder.comment("If set to true, one of the first undead enemies a player slays will drop the encyclopedia arcana.")
                    .define("enableCodexDrop", true)));

    public static ConfigValueHolder<Boolean> NO_FANCY_SPIRITS = new ConfigValueHolder<>(MALUM, "common/spirit", (builder ->
            builder.comment("If set to true, any spirits dropped will simply take the form of an item.")
                    .define("noFancySpirits", false)));

    public static ConfigValueHolder<Boolean> SOULLESS_SPAWNERS = new ConfigValueHolder<>(MALUM, "common/spirit/spawner", (builder ->
            builder.comment("If set to true, mob spawners will create soulless mobs instead.")
                    .define("lameSpawners", false)));

    public static ConfigValueHolder<Boolean> USE_DEFAULT_SPIRIT_VALUES = new ConfigValueHolder<>(MALUM, "common/spirit/defaults", (builder ->
            builder.comment("Whether entities without spirit jsons will use the default spirit data for their category.")
                    .define("defaultSpiritValues", true)));

    public static ConfigValueHolder<Boolean> MAGIC_DAMAGE_REDUCED_ARMOR_PIERCING = new ConfigValueHolder<>(MALUM, "common/magic_damage", (builder ->
            builder.comment("If set to true, damage types tagged under malum:bypasses_half_armor will pierce only half of the player's armor stat, as opposed to piercing it entirely. In addition, armor will not take durability damage.")
                    .define("magicDamageReducedArmorPiercing", true)));

    public static ConfigValueHolder<Double> SOUL_WARD_PHYSICAL = new ConfigValueHolder<>(MALUM, "common/soul_ward", (builder ->
            builder.comment("Multiplier for physical damage taken while soul ward is active.")
                    .defineInRange("soulWardPhysical", 0.7f, 0, 1)));
    public static ConfigValueHolder<Double> SOUL_WARD_MAGIC = new ConfigValueHolder<>(MALUM, "common/soul_ward", (builder ->
            builder.comment("Multiplier for magic damage taken while soul ward is active.")
                    .defineInRange("soulWardMagic", 0.1f, 0, 1)));
    public static ConfigValueHolder<Integer> SOUL_WARD_RATE = new ConfigValueHolder<>(MALUM, "common/soul_ward", (builder ->
            builder.comment("Base time in ticks it takes for one point of soul ward to recover.")
                    .define("soulWardRate", 100)));

    public static ConfigValueHolder<Integer> MALIGNANT_AEGIS_RATE = new ConfigValueHolder<>(MALUM, "common/malignant_aegis", (builder ->
            builder.comment("Base time in ticks it takes for one point of malignant aegis to recover.")
                    .define("malignantAegisRate", 200)));

    public static ConfigValueHolder<Integer> STAFF_CHARGE_RATE = new ConfigValueHolder<>(MALUM, "common/staff_charge", (builder ->
            builder.comment("Base time in ticks it takes for one segment of a staff charge to recover.")
                    .define("staffChargeRate", 100)));

    public CommonConfig(ModConfigSpec.Builder builder) {
        super(MALUM, "common", builder);
    }

    public static final CommonConfig INSTANCE;
    public static final ModConfigSpec SPEC;

    static {
        final Pair<CommonConfig, ModConfigSpec> specPair = new ModConfigSpec.Builder().configure(CommonConfig::new);
        SPEC = specPair.getRight();
        INSTANCE = specPair.getLeft();
    }
}
