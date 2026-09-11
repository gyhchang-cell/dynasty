package com.dynasty.network;

import com.dynasty.Dynasty;
import com.dynasty.DynastyTrinketSync;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.simple.SimpleChannel;

/**
 * Dynasty 网络通道（科举 GUI 用）。
 * Dynasty network channel (used by the Keju GUI).
 */
public class DynastyNetwork {

    private static final String PROTOCOL = "1";

    @SuppressWarnings("removal")
    public static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(
            new ResourceLocation(Dynasty.MODID, "dynasty"),
            () -> PROTOCOL,
            PROTOCOL::equals,
            PROTOCOL::equals);

    private static int id = 0;

    public static void register() {
        CHANNEL.registerMessage(id++, OpenKejuPacket.class,
                OpenKejuPacket::encode, OpenKejuPacket::decode, OpenKejuPacket::handle);
        CHANNEL.registerMessage(id++, AnswerKejuPacket.class,
                AnswerKejuPacket::encode, AnswerKejuPacket::decode, AnswerKejuPacket::handle);
        CHANNEL.registerMessage(id++, QuestRequestPacket.class,
                QuestRequestPacket::encode, QuestRequestPacket::decode, QuestRequestPacket::handle);
        CHANNEL.registerMessage(id++, QuestSyncPacket.class,
                QuestSyncPacket::encode, QuestSyncPacket::decode, QuestSyncPacket::handle);
        CHANNEL.registerMessage(id++, QuestClaimPacket.class,
                QuestClaimPacket::encode, QuestClaimPacket::decode, QuestClaimPacket::handle);
        CHANNEL.registerMessage(id++, ArmyFormPacket.class,
                ArmyFormPacket::encode, ArmyFormPacket::decode, ArmyFormPacket::handle);
        CHANNEL.registerMessage(id++, StatsRequestPacket.class,
                StatsRequestPacket::encode, StatsRequestPacket::decode, StatsRequestPacket::handle);
        CHANNEL.registerMessage(id++, StatsSyncPacket.class,
                StatsSyncPacket::encode, StatsSyncPacket::decode, StatsSyncPacket::handle);
        CHANNEL.registerMessage(id++, DynastyTrinketSync.class,
                DynastyTrinketSync::encode, DynastyTrinketSync::decode, DynastyTrinketSync::handle);
    }
}
