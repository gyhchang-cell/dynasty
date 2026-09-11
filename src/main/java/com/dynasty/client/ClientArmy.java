package com.dynasty.client;

import com.dynasty.network.ArmyFormPacket;
import com.dynasty.network.DynastyNetwork;
import net.minecraft.client.Minecraft;

/** 客户端：虎符调兵界面。/ Client: army formation screen opener. */
public final class ClientArmy {

    private ClientArmy() {
    }

    public static void open() {
        Minecraft.getInstance().setScreen(new ArmyScreen());
    }

    public static void send(int formation, int count) {
        DynastyNetwork.CHANNEL.sendToServer(new ArmyFormPacket(formation, count));
    }
}
