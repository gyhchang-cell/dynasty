package dev.melix.damagenumbers.client.render;

import net.fabricmc.fabric.api.client.rendering.v1.level.LevelRenderEvents;

public final class WorldRenderHook {
    private WorldRenderHook() {
    }

    public static void register(DamageNumberManager manager) {
        LevelRenderEvents.END_MAIN.register(context ->
                manager.render(context.poseStack(), context.gameRenderer().getMainCamera()));
    }

    public static void renderFromMixin() {
    }
}
