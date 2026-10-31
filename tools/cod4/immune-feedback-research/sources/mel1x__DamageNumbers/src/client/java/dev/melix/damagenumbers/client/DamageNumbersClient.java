package dev.melix.damagenumbers.client;

import dev.melix.damagenumbers.client.config.DamageNumbersConfig;
import dev.melix.damagenumbers.client.config.CustomFontManager;
import dev.melix.damagenumbers.client.render.DamageNumberManager;
import dev.melix.damagenumbers.client.render.WorldRenderHook;
import net.fabricmc.api.ClientModInitializer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

public final class DamageNumbersClient implements ClientModInitializer {
    private static DamageNumberManager manager;

    @Override
    public void onInitializeClient() {
        DamageNumbersConfig.get().load();
        CustomFontManager.initialize(net.minecraft.client.Minecraft.getInstance());
        manager = new DamageNumberManager();
        manager.registerDamageTracking();
        ShowDamageClientNetworking.register();
        WorldRenderHook.register(manager);
    }

    public static void onClientAttack(Player player, Entity target) {
        if (manager != null) {
            manager.onClientAttack(player, target);
        }
    }

    public static void showDamage(String presetName, Vec3 position, float value) {
        if (manager != null) {
            manager.showDamage(presetName, position, value);
        }
    }
}
