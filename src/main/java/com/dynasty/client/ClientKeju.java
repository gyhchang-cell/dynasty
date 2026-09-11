package com.dynasty.client;

import net.minecraft.client.Minecraft;

/**
 * 客户端打开科举界面。
 * Client-side helper to open the Keju screen.
 */
public final class ClientKeju {

    private ClientKeju() {
    }

    public static void open(int index, String question, String[] options) {
        Minecraft.getInstance().setScreen(new KejuScreen(index, question, options));
    }
}
