package dev.melix.damagenumbers.client.render;

import net.fabricmc.fabric.api.client.rendering.v1.level.LevelRenderEvents;
import net.minecraft.client.Minecraft;

public final class WorldRenderHook {
    private WorldRenderHook() {
    }

    public static void register(DamageNumberManager manager) {
        LevelRenderEvents.COLLECT_SUBMITS.register(context -> manager.render(
                context.poseStack(), Minecraft.getInstance().gameRenderer.mainCamera(),
                context.submitNodeCollector()));
    }

    public static void renderFromMixin() {
    }
}
