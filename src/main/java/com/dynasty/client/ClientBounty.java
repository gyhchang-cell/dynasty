package com.dynasty.client;

import com.dynasty.bounty.BountyView;
import net.minecraft.client.Minecraft;

/**
 * 客户端持有最近一次告示板数据，并负责打开/刷新界面。
 * Client-side holder for the latest board view.
 */
public final class ClientBounty {

    private static BountyView latest;

    private ClientBounty() {
    }

    public static void accept(BountyView view) {
        latest = view;
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft.screen instanceof BountyBoardScreen screen) {
            screen.update(view);
        } else {
            minecraft.setScreen(new BountyBoardScreen(view));
        }
    }

    public static BountyView latest() {
        return latest;
    }
}
