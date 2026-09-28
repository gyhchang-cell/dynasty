package com.dynasty.client;

import com.dynasty.Dynasty;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.server.packs.resources.ResourceManagerReloadListener;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterClientReloadListenersEvent;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** A client-only title replacement; world selection, authentication and multiplayer stay vanilla. */
@Mod.EventBusSubscriber(modid = Dynasty.MODID, value = Dist.CLIENT)
public final class DynastyTitleMenu {
    private DynastyTitleMenu() { }

    @SubscribeEvent
    public static void opening(ScreenEvent.Opening event) {
        Screen next = event.getNewScreen();
        if (next != null && next.getClass() == TitleScreen.class
                && !Boolean.getBoolean("dynasty.vanillaMenu") && !Screen.hasShiftDown()) {
            event.setNewScreen(new DynastyTitleScreen());
        }
    }

    /** A distinct class deliberately bypasses the exact-class replacement above. */
    static final class VanillaTitleScreen extends TitleScreen { }

    @Mod.EventBusSubscriber(modid = Dynasty.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.MOD)
    public static final class Resources {
        @SubscribeEvent
        public static void register(RegisterClientReloadListenersEvent event) {
            event.registerReloadListener((ResourceManagerReloadListener) manager -> DynastyTitleScreen.invalidateBackground());
        }
    }
}
