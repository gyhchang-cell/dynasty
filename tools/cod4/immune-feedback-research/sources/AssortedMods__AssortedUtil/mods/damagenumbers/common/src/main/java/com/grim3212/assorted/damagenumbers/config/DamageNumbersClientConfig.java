package com.grim3212.assorted.damagenumbers.config;

import com.grim3212.assorted.lib.config.ConfigurationType;
import com.grim3212.assorted.lib.config.IConfigurationBuilder;
import com.grim3212.assorted.lib.platform.Services;
import com.grim3212.assorted.damagenumbers.Constants;

import java.util.function.Supplier;

/** Only changes what one player sees, so each player decides for themselves. */
public class DamageNumbersClientConfig {

    public final Supplier<Boolean> damageNumbersShowSource;
    public final Supplier<Boolean> damageNumbersShowHealing;
    public final Supplier<Integer> damageNumbersRange;
    public final Supplier<Integer> damageNumbersLifetime;

    public DamageNumbersClientConfig() {
        final IConfigurationBuilder builder = Services.CONFIG.createBuilder(ConfigurationType.CLIENT_ONLY, Constants.MOD_ID + "-client");

        damageNumbersShowSource = builder.defineBoolean("damageNumbers.showSource", true, "Show what did the damage beside the number, as in -3 (Fire).");
        damageNumbersShowHealing = builder.defineBoolean("damageNumbers.showHealing", true, "Show healing as well as damage.");
        damageNumbersRange = builder.defineInteger("damageNumbers.range", 24, 4, 64, "How far away, in blocks, damage numbers are shown.");
        damageNumbersLifetime = builder.defineInteger("damageNumbers.lifetime", 40, 10, 200, "How long a damage number stays, in ticks. There are 20 ticks a second.");

        builder.setup();
    }
}
