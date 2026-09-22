package com.dynasty.client;

import com.dynasty.Dynasty;
import net.minecraft.client.Minecraft;

/**
 * 客户端打开科举界面。
 * Client-side helper to open the Keju screen.
 */
public final class ClientKeju {

    private ClientKeju() {
    }

    /**
     * 打开答题界面；字段不合法（题干为空 / 选项不是三个）时直接忽略，
     * 不做静默修补，也不让界面渲染出空按钮。
     */
    public static void open(int index, String question, String[] options) {
        if (question == null || options == null || options.length != 3) {
            Dynasty.LOGGER.warn("[Dynasty] 科举打开包字段不合法，已忽略（题干={} 选项数={}）",
                    question == null ? "null" : "ok", options == null ? -1 : options.length);
            return;
        }
        Minecraft.getInstance().setScreen(new KejuScreen(index, question, options));
    }
}
