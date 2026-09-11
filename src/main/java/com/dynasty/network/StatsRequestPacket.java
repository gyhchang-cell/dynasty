package com.dynasty.network;

import com.dynasty.DynastyStats;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;
import net.minecraftforge.network.PacketDistributor;

import java.util.function.Supplier;

/** 客户端 → 服务端：请求王朝档案（官阶/功名/忠诚/叛乱）。 */
public class StatsRequestPacket {

    public StatsRequestPacket() {
    }

    public static void encode(StatsRequestPacket pkt, FriendlyByteBuf buf) {
    }

    public static StatsRequestPacket decode(FriendlyByteBuf buf) {
        return new StatsRequestPacket();
    }

    public static void handle(StatsRequestPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() -> {
            ServerPlayer player = ctx.get().getSender();
            if (player != null) {
                DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(() -> player),
                        new StatsSyncPacket(DynastyStats.getRank(player), DynastyStats.getMerit(player),
                                DynastyStats.getLoyalty(player), DynastyStats.getRebellion(player)));
            }
        });
        ctx.get().setPacketHandled(true);
    }
}
