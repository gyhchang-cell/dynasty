package net.sam.simple_combat_indicators.util;

import net.minecraftforge.common.ForgeConfigSpec;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.config.ModConfigEvent;
import net.sam.simple_combat_indicators.SimpleCombatIndicators;
import net.sam.simple_combat_indicators.config.ClientConfig;
import net.sam.simple_combat_indicators.render.DamageIndicatorRenderer;


@Mod.EventBusSubscriber(modid = SimpleCombatIndicators.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)
public class ConfigUtils {

    public static <T> T getOrDefault(ForgeConfigSpec.ConfigValue<T> configValue) {
        try {
            T value = configValue.get();
            if (value == null) {
                return configValue.getDefault();
            }
            return value;
        } catch (Exception e) {
            System.err.println("Invalid config value: " + e.getMessage());
            return configValue.getDefault();
        }
    }

    @SubscribeEvent
    public static void onModConfigLoaded(ModConfigEvent event) {
        if (event.getConfig().getSpec() == ClientConfig.SPEC) {

            DamageIndicatorRenderer.initFromConfig();
            DamageDealtIndicator.initFromConfig();
            DamageTakenIndicator.initFromConfig();
        }
    }
}
