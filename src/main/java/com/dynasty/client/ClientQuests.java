package com.dynasty.client;

import net.minecraft.client.Minecraft;

/**
 * 客户端任务状态缓存与界面打开。
 * Client-side quest state cache and screen opener.
 */
public final class ClientQuests {

    private ClientQuests() {
    }

    private static int[] progress = new int[0];
    private static boolean[] claimed = new boolean[0];
    private static boolean openRequested;

    public static void receive(int[] newProgress, boolean[] newClaimed) {
        progress = newProgress;
        claimed = newClaimed;
        Minecraft.getInstance().setScreen(new QuestScreen());
    }

    public static int progress(int index) {
        return index >= 0 && index < progress.length ? progress[index] : 0;
    }

    public static boolean claimed(int index) {
        return index >= 0 && index < claimed.length && claimed[index];
    }

    public static boolean hasData() {
        return progress.length > 0;
    }
}
