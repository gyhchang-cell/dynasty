package com.dynasty.network;

import com.dynasty.DynastyArmy;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** 客户端 → 服务端：以指定阵型调兵（虎符界面）。 */
public class ArmyFormPacket {

    private final int formation;
    private final int count;

    public ArmyFormPacket(int formation, int count) {
        this.formation = formation;
        this.count = count;
    }

    public static void encode(ArmyFormPacket pkt, FriendlyByteBuf buf) {
        buf.writeVarInt(pkt.formation);
        buf.writeVarInt(pkt.count);
    }

    public static ArmyFormPacket decode(FriendlyByteBuf buf) {
        return new ArmyFormPacket(buf.readVarInt(), buf.readVarInt());
    }

    public static void handle(ArmyFormPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() -> {
            ServerPlayer player = ctx.get().getSender();
            if (player != null) {
                int idx = Math.max(0, Math.min(DynastyArmy.FORMATIONS.length - 1, pkt.formation));
                DynastyArmy.formUp(player, DynastyArmy.FORMATIONS[idx], pkt.count);
            }
        });
        ctx.get().setPacketHandled(true);
    }
}
