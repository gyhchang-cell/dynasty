package dev.melix.damagenumbers.client.render;

import net.fabricmc.fabric.api.client.rendering.v1.world.WorldRenderEvents;

public final class WorldRenderHook {
    private WorldRenderHook() {
    }

    public static void register(DamageNumberManager manager) {
        WorldRenderEvents.END_MAIN.register(context ->
                manager.render(context.matrices(), context.gameRenderer().getMainCamera()));
    }

    public static void renderFromMixin() {
    }
}
