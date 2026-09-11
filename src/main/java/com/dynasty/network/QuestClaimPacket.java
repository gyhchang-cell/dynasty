package com.dynasty.network;

import com.dynasty.DynastyQuestManager;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;
import net.minecraftforge.network.PacketDistributor;

import java.util.function.Supplier;

/** 客户端 → 服务端：领取任务奖励。 */
public class QuestClaimPacket {

    private final int index;

    public QuestClaimPacket(int index) {
        this.index = index;
    }

    public static void encode(QuestClaimPacket pkt, FriendlyByteBuf buf) {
        buf.writeVarInt(pkt.index);
    }

    public static QuestClaimPacket decode(FriendlyByteBuf buf) {
        return new QuestClaimPacket(buf.readVarInt());
    }

    public static void handle(QuestClaimPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() -> {
            ServerPlayer player = ctx.get().getSender();
            if (player != null) {
                DynastyQuestManager.claim(player, pkt.index);
                QuestRequestPacket.sendTo(player);
            }
        });
        ctx.get().setPacketHandled(true);
    }
}
