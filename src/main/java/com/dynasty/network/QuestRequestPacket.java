package com.dynasty.network;

import com.dynasty.DynastyQuestManager;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;
import net.minecraftforge.network.PacketDistributor;

import java.util.function.Supplier;

/** 客户端 → 服务端：请求任务数据（打开任务界面）。 */
public class QuestRequestPacket {

    public QuestRequestPacket() {
    }

    public static void encode(QuestRequestPacket pkt, FriendlyByteBuf buf) {
    }

    public static QuestRequestPacket decode(FriendlyByteBuf buf) {
        return new QuestRequestPacket();
    }

    public static void sendTo(ServerPlayer player) {
        DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(() -> player),
                new QuestSyncPacket(DynastyQuestManager.progressArray(player),
                        DynastyQuestManager.claimedArray(player)));
    }

    public static void handle(QuestRequestPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() -> {
            ServerPlayer player = ctx.get().getSender();
            if (player != null) {
                sendTo(player);
            }
        });
        ctx.get().setPacketHandled(true);
    }
}
