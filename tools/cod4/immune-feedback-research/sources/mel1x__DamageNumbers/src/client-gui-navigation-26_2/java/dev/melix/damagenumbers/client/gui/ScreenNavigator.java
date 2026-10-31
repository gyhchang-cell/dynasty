package dev.melix.damagenumbers.client.gui;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.Screen;

final class ScreenNavigator {
    private ScreenNavigator() {
    }

    static void open(Minecraft minecraft, Screen screen) {
        minecraft.setScreenAndShow(screen);
    }
}
