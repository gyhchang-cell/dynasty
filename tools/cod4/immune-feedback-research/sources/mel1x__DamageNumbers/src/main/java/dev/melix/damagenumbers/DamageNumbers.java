package dev.melix.damagenumbers;

import net.fabricmc.api.ModInitializer;

public final class DamageNumbers implements ModInitializer {
    public static final String MOD_ID = "damage-numbers";

    @Override
    public void onInitialize() {
        ShowDamageNetworking.register();
    }
}
