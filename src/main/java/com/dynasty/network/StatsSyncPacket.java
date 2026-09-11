package com.dynasty.network;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** 服务端 → 客户端：同步王朝档案并打开界面。 */
public class StatsSyncPacket {

    private final int rank;
    private final int merit;
    private final int loyalty;
    private final int rebellion;

    public StatsSyncPacket(int rank, int merit, int loyalty, int rebellion) {
        this.rank = rank;
        this.merit = merit;
        this.loyalty = loyalty;
        this.rebellion = rebellion;
    }

    public static void encode(StatsSyncPacket pkt, FriendlyByteBuf buf) {
        buf.writeVarInt(pkt.rank);
        buf.writeVarInt(pkt.merit);
        buf.writeVarInt(pkt.loyalty);
        buf.writeVarInt(pkt.rebellion);
    }

    public static StatsSyncPacket decode(FriendlyByteBuf buf) {
        return new StatsSyncPacket(buf.readVarInt(), buf.readVarInt(), buf.readVarInt(), buf.readVarInt());
    }

    public static void handle(StatsSyncPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                () -> () -> com.dynasty.client.ClientStats.receive(pkt.rank, pkt.merit, pkt.loyalty, pkt.rebellion)));
        ctx.get().setPacketHandled(true);
    }
}
