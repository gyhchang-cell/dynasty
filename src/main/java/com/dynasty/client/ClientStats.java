package com.dynasty.client;

import com.dynasty.network.StatsRequestPacket;
import com.dynasty.network.DynastyNetwork;
import net.minecraft.client.Minecraft;

/** 客户端：请求并显示王朝档案。/ Client: request and show dynasty stats. */
public final class ClientStats {

    private ClientStats() {
    }

    private static int rank, merit, loyalty, rebellion;

    public static void requestAndOpen() {
        DynastyNetwork.CHANNEL.sendToServer(new StatsRequestPacket());
        Minecraft.getInstance().setScreen(new StatsScreen());
    }

    public static void receive(int rankIn, int meritIn, int loyaltyIn, int rebellionIn) {
        rank = rankIn;
        merit = meritIn;
        loyalty = loyaltyIn;
        rebellion = rebellionIn;
        if (Minecraft.getInstance().screen instanceof StatsScreen screen) {
            screen.refresh(rank, merit, loyalty, rebellion);
        } else {
            Minecraft.getInstance().setScreen(new StatsScreen());
        }
    }

    public static int rank() {
        return rank;
    }

    public static int merit() {
        return merit;
    }

    public static int loyalty() {
        return loyalty;
    }

    public static int rebellion() {
        return rebellion;
    }
}
