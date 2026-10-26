package net.sam.simple_combat_indicators.config;

import net.minecraftforge.common.ForgeConfigSpec;

public class ClientConfig {

    public static final ForgeConfigSpec.Builder BUILDER = new ForgeConfigSpec.Builder();
    public static final ForgeConfigSpec SPEC;

    public static final ForgeConfigSpec.ConfigValue<Boolean> ENABLE_DAMAGE_NUMBERS;
    public static final ForgeConfigSpec.ConfigValue<Boolean> ENABLE_DAMAGE_TAKEN_INDICATOR;

    public static final ForgeConfigSpec.ConfigValue<Integer> NUMBER_DURATION;

    public static final ForgeConfigSpec.ConfigValue<Integer> INITIAL_HIT_TIME;

    public static final ForgeConfigSpec.ConfigValue<Integer> START_NUMBER_COLOR_R;
    public static final ForgeConfigSpec.ConfigValue<Integer> START_NUMBER_COLOR_G;
    public static final ForgeConfigSpec.ConfigValue<Integer> START_NUMBER_COLOR_B;

    public static final ForgeConfigSpec.ConfigValue<Integer> END_NUMBER_COLOR_R;
    public static final ForgeConfigSpec.ConfigValue<Integer> END_NUMBER_COLOR_G;
    public static final ForgeConfigSpec.ConfigValue<Integer> END_NUMBER_COLOR_B;

    public static final ForgeConfigSpec.ConfigValue<Boolean> SHOULD_SEPARATE_KILL_COLOR;

    public static final ForgeConfigSpec.ConfigValue<Integer> KILL_COLOR_R;
    public static final ForgeConfigSpec.ConfigValue<Integer> KILL_COLOR_G;
    public static final ForgeConfigSpec.ConfigValue<Integer> KILL_COLOR_B;

    public static final ForgeConfigSpec.ConfigValue<Double> NUMBER_BASE_SCALE;
    public static final ForgeConfigSpec.ConfigValue<Double> NUMBER_INCREMENT_SCALE;
    public static final ForgeConfigSpec.ConfigValue<Double> NUMBER_DECREMENT_SPEED;

    public static final ForgeConfigSpec.ConfigValue<Boolean> STACKING_NUMBERS;
    public static final ForgeConfigSpec.ConfigValue<Boolean> SPRAY_NUMBERS;
    public static final ForgeConfigSpec.ConfigValue<Double> SPRAY_ANGLE_RANGE;
    public static final ForgeConfigSpec.ConfigValue<Double> SPRAY_ANGLE_OFFSET;
    public static final ForgeConfigSpec.ConfigValue<Double> SPRAY_VELOCITY;
    public static final ForgeConfigSpec.ConfigValue<Double> NUMBER_FRICTION;
    public static final ForgeConfigSpec.ConfigValue<Double> NUMBER_GRAVITY;

    public static final ForgeConfigSpec.ConfigValue<Integer> ROTATE_RANGE;

    public static final ForgeConfigSpec.ConfigValue<Integer> DAMAGE_TAKEN_INDICATOR_DURATION;
    public static final ForgeConfigSpec.ConfigValue<Integer> DAMAGE_TAKEN_INDICATOR_BIG_DURATION;

    public static final ForgeConfigSpec.ConfigValue<Double> DAMAGE_TAKEN_INDICATOR_BASE_SIZE_SCALE;
    public static final ForgeConfigSpec.ConfigValue<Double> DAMAGE_TAKEN_INDICATOR_MAX_SIZE_SCALE_MULT;

    public static final ForgeConfigSpec.ConfigValue<Integer> DAMAGE_TAKEN_INDICATOR_DISTANCE;

    public static final ForgeConfigSpec.ConfigValue<Integer> BIG_HIT_INDICATOR_COLOR_R;
    public static final ForgeConfigSpec.ConfigValue<Integer> BIG_HIT_INDICATOR_COLOR_G;
    public static final ForgeConfigSpec.ConfigValue<Integer> BIG_HIT_INDICATOR_COLOR_B;

    public static final ForgeConfigSpec.ConfigValue<Integer> SMALL_HIT_INDICATOR_COLOR_R;
    public static final ForgeConfigSpec.ConfigValue<Integer> SMALL_HIT_INDICATOR_COLOR_G;
    public static final ForgeConfigSpec.ConfigValue<Integer> SMALL_HIT_INDICATOR_COLOR_B;

    static {
        BUILDER.push("Config for Sam's Combat Indicators");


        // DAMAGE NUMBER SETTINGS
        ENABLE_DAMAGE_NUMBERS = BUILDER.comment("Should damage numbers show DEFAULT: true").define("enable_damage_numbers", true);
        NUMBER_DURATION = BUILDER.comment("Damage number duration (in ticks) DEFAULT: 30").define("number_duration", 30);
        INITIAL_HIT_TIME = BUILDER.comment("Duration damage numbers flash a different color initially (set to 0 to disable) (in ticks) DEFAULT: 10").define("initial_hit_time", 10);
        START_NUMBER_COLOR_R = BUILDER.comment("Start damage number color red value (0-255) DEFAULT: 255").define("start_number_color_r", 255);
        START_NUMBER_COLOR_G = BUILDER.comment("Start damage number color green value (0-255) DEFAULT: 102").define("start_number_color_g", 102);
        START_NUMBER_COLOR_B = BUILDER.comment("Start damage number color blue value (0-255) DEFAULT: 0").define("start_number_color_b", 0);
        END_NUMBER_COLOR_R = BUILDER.comment("End damage number color red value (0-255) DEFAULT: 255").define("end_number_color_r", 255);
        END_NUMBER_COLOR_G = BUILDER.comment("End damage number color green (0-255) DEFAULT: 255").define("end_number_color_g", 255);
        END_NUMBER_COLOR_B = BUILDER.comment("End damage number color blue value (0-255) DEFAULT: 0").define("end_number_color_b", 0);
        SHOULD_SEPARATE_KILL_COLOR = BUILDER.comment("Should damage that kills be a different color DEFAULT: true").define("separate_kill_color", true);
        KILL_COLOR_R = BUILDER.comment("Kill damage number color red value (0-255) DEFAULT: 255").define("kill_number_color_r", 255);
        KILL_COLOR_G = BUILDER.comment("Kill damage number color green (0-255) DEFAULT: 0").define("kill_number_color_g", 0);
        KILL_COLOR_B = BUILDER.comment("Kill damage number color blue value (0-255) DEFAULT: 0").define("kill_number_color_b", 0);
        NUMBER_BASE_SCALE = BUILDER.comment("Number base scale DEFAULT: 3.0").define("number_base_scale", 3.0);
        NUMBER_INCREMENT_SCALE = BUILDER.comment("Scale increase per successive hit (only applies when stacking numbers is on) DEFAULT: 1.0").define("number_increment_scale", 1.0);
        NUMBER_DECREMENT_SPEED = BUILDER.comment("How fast numbers decrease in scale (unit per second) (DEFAULT: 1.5)").define("number_decrement_speed", 1.5);
        STACKING_NUMBERS = BUILDER.comment("Should damage numbers on a target sum up?").define("stack_damage_numbers", true);
        SPRAY_NUMBERS = BUILDER.comment("Should damage numbers spray in a random direction?").define("spray_damage_numbers", false);
        SPRAY_VELOCITY = BUILDER.comment("Initial spray velocity of numbers (in pixels per second) DEFAULT: 150.0").define("spray_velocity", 150.0);
        NUMBER_FRICTION = BUILDER.comment("How fast numbers slow down (Loss in % of velocity per second e.g. 0.27 = 27% velocity lost per second) DEFAULT: 0.27").define("number_friction", 0.27);
        NUMBER_GRAVITY = BUILDER.comment("How fast numbers accelerate down (pixels/s^2) DEFAULT: 0.0").define("number_gravity", 0.0);
        SPRAY_ANGLE_RANGE = BUILDER.comment("Range from -angle to +angle that numbers will spray (in degrees) DEFAULT: 180.0").define("spray_angle_range", 180.0);
        SPRAY_ANGLE_OFFSET = BUILDER.comment("Range angle offset applied to all numbers (in degrees) DEFAULT: 0.0").define("spray_angle_offset", 0.0);

        ROTATE_RANGE = BUILDER.comment("Range in degrees (-rotate_range to +rotate_range) between which damage numbers will randomly rotate (set to zero to disable)").define("rotate_range", 15);

        //DAMAGE TAKEN INDICATOR SETTINGS
        ENABLE_DAMAGE_TAKEN_INDICATOR = BUILDER.comment("Should damage taken indicators show DEFAULT: true").define("enable_damage_taken_indicator", true);
        DAMAGE_TAKEN_INDICATOR_DURATION = BUILDER.comment("How long damage taken indicator lasts (in ticks) DEFAULT: 60").define("damage_taken_indicator_duration", 60);
        DAMAGE_TAKEN_INDICATOR_BIG_DURATION = BUILDER.comment("How long damage taken is big on initial hit (in ticks) DEFAULT: 20").define("damage_taken_indicator_big_duration", 20);

        DAMAGE_TAKEN_INDICATOR_BASE_SIZE_SCALE = BUILDER.comment("Base scale size for damage taken indicator (DEFAULT : 1.0)").define("damage_taken_indicator_min_size_scale", 1.0);
        DAMAGE_TAKEN_INDICATOR_MAX_SIZE_SCALE_MULT = BUILDER.comment("Maximum scale size multiplier for damage taken indicator (DEFAULT : 2.0)").define("damage_taken_indicator_max_size_scale", 2.0);

        DAMAGE_TAKEN_INDICATOR_DISTANCE = BUILDER.comment("Damage taken indicator base distance from center of screen (in pixels) (DEFAULT : 220)").define("damage_taken_indicator_distance", 220);

        BIG_HIT_INDICATOR_COLOR_R = BUILDER.comment("Biggest hit (damage that deals 100% max health) color red value (0-255) DEFAULT: 255").define("big_hit_indicator_color_r", 255);
        BIG_HIT_INDICATOR_COLOR_G = BUILDER.comment("Biggest hit (damage that deals 100% max health) color green value (0-255) DEFAULT: 0").define("big_hit_indicator_color_g", 0);
        BIG_HIT_INDICATOR_COLOR_B = BUILDER.comment("Biggest hit (damage that deals 100% max health) color blue value (0-255) DEFAULT: 0").define("big_hit_indicator_color_b", 0);
        SMALL_HIT_INDICATOR_COLOR_R = BUILDER.comment("Smallest hit (damage that deals 0% max health) color red value (0-255) DEFAULT: 255").define("small_hit_indicator_color_r", 255);
        SMALL_HIT_INDICATOR_COLOR_G = BUILDER.comment("Smallest hit (damage that deals 0% max health) color green value (0-255) DEFAULT: 242").define("small_hit_indicator_color_g", 242);
        SMALL_HIT_INDICATOR_COLOR_B = BUILDER.comment("Smallest hit (damage that deals 0% max health) color blue value (0-255) DEFAULT: 0").define("small_hit_indicator_color_b", 0);

        BUILDER.pop();
        SPEC = BUILDER.build();
    }

}
