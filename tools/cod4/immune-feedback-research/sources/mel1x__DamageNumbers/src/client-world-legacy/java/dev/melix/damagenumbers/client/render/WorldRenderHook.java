package dev.melix.damagenumbers.client.render;

import net.fabricmc.fabric.api.client.rendering.v1.WorldRenderEvents;

public final class WorldRenderHook {
    private WorldRenderHook() {
    }

    public static void register(DamageNumberManager manager) {
        WorldRenderEvents.LAST.register(context ->
                manager.render(context.matrixStack(), context.camera()));
    }

    public static void renderFromMixin() {
    }
}
