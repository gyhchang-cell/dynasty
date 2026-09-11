package com.dynasty.client;

import net.minecraft.client.Minecraft;

/**
 * 客户端打开王朝图鉴。
 * Client helper to open the Dynasty Codex screen.
 */
public final class ClientGuide {

    private ClientGuide() {
    }

    public static void open() {
        Minecraft.getInstance().setScreen(new GuideScreen());
    }
}
