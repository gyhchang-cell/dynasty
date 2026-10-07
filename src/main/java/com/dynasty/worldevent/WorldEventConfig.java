package com.dynasty.worldevent;

import net.minecraftforge.common.ForgeConfigSpec;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.config.ModConfig;

/** Server-owned frequency controls; debug commands remain available when natural events are disabled. */
public final class WorldEventConfig {
    public static final ForgeConfigSpec SPEC;
    private static final ForgeConfigSpec.BooleanValue ENABLED,TERRAIN;
    private static final ForgeConfigSpec.IntValue INTERVAL;
    private static final ForgeConfigSpec.DoubleValue FREQUENCY;
    static {
        var b=new ForgeConfigSpec.Builder();b.push("worldEvents");
        ENABLED=b.comment("Evaluate natural world events near survival players.").define("enabled",true);
        INTERVAL=b.comment("Ticks between staggered batches of at most six definitions.").defineInRange("evaluationInterval",300,200,400);
        FREQUENCY=b.comment("Chance multiplier. Cooldown floors are unchanged; 1.0 preserves the design cadence.").defineInRange("frequencyMultiplier",1.0,0.05,10.0);
        TERRAIN=b.comment("Permit future event-authored terrain edits. Player builds and landmarks still require protection checks.").define("allowTerrainChanges",false);
        b.pop();SPEC=b.build();
    }
    public static void register(){ModLoadingContext.get().registerConfig(ModConfig.Type.SERVER,SPEC,"dynasty-world-events.toml");}
    public static boolean enabled(){return !SPEC.isLoaded()||ENABLED.get();}
    public static int interval(){return SPEC.isLoaded()?INTERVAL.get():300;}
    public static double chance(int rarity){return Math.min(1.0,(SPEC.isLoaded()?FREQUENCY.get():1.0)/rarity);}
    public static boolean terrainChanges(){return SPEC.isLoaded()&&TERRAIN.get();}
    private WorldEventConfig(){}
}
