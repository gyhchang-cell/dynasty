package artifacts.neoforge.client;

import artifacts.ArtifactsClient;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Gui;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.world.entity.player.Player;

public class HeliumFlamingoOverlayRenderer {

    public static void render(GuiGraphicsExtractor guiGraphics, DeltaTracker ignored) {
        if (Minecraft.getInstance().getCameraEntity() instanceof Player player) {
            Gui gui = Minecraft.getInstance().gui;

            if (!Minecraft.getInstance().options.hideGui) {
                if (ArtifactsClient.getHeliumFlamingoOverlay().renderOverlay(guiGraphics, player, gui.rightHeight)) {
                    gui.rightHeight += 10;
                }
            }
        }
    }
}
