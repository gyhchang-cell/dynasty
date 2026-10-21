package com.dynasty.client;

import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;


/** Coordinates supplied by the equipped south-pointing compass. Health belongs to the HUD mod. */
@Mod.EventBusSubscriber(modid = com.dynasty.Dynasty.MODID, value = Dist.CLIENT)
public class DynastyHealthHud {

    @SubscribeEvent
    public static void onOverlayPost(RenderGuiOverlayEvent.Post event) {
        if (!event.getOverlay().id().equals(VanillaGuiOverlay.HOTBAR.id())) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        if (player == null || !ClientTrinkets.has("south_pointing_compass")) {
            return;
        }
        String coords = String.format("§7司南 §fX %d §7Y §f%d §7Z §f%d",
                (int) player.getX(), (int) player.getY(), (int) player.getZ());
        event.getGuiGraphics().drawString(mc.font, coords, 4, 4, 0xFFFFFFFF, true);
    }

}
