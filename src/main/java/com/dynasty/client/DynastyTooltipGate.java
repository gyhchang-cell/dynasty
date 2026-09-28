package com.dynasty.client;

import net.minecraft.client.Minecraft;
import org.lwjgl.glfw.GLFW;

/**
 * 悬停说明里的 Shift 状态（唯一允许触碰 GLFW 的地方）。
 *
 * 单独一层的原因：{@code appendHoverText} 被共享物品类复用，而共享类在**专用服务器**上也会加载；
 * 把客户端按键检查集中在这里、并由调用方用 {@code DistExecutor} 包一层，
 * 服务器就永远不会加载客户端类。
 *
 * Client-only Shift state, kept in one place so the dedicated server never loads
 * client classes (callers wrap it in DistExecutor).
 */
public final class DynastyTooltipGate {

    private DynastyTooltipGate() {
    }

    /** 是否按住 Shift。/ is either Shift key held down. */
    public static boolean shiftDown() {
        try {
            long handle = Minecraft.getInstance().getWindow().getWindow();
            return GLFW.glfwGetKey(handle, GLFW.GLFW_KEY_LEFT_SHIFT) == GLFW.GLFW_PRESS
                    || GLFW.glfwGetKey(handle, GLFW.GLFW_KEY_RIGHT_SHIFT) == GLFW.GLFW_PRESS;
        } catch (Exception ignored) {
            return false;
        }
    }

    /** 「按住 Shift 查看详情」提示（与界面语言一致）。/ the hint, in the client's language. */
    public static net.minecraft.network.chat.Component holdShiftHint() {
        return DynastyTooltipText.holdShift(DynastyItemInfo.chinese());
    }
}
