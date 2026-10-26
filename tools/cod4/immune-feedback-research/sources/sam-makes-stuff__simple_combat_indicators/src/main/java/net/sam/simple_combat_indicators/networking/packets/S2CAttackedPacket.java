package net.sam.simple_combat_indicators.networking.packets;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;
import net.sam.simple_combat_indicators.networking.ClientPacketHandler;

import java.util.function.Supplier;

public class S2CAttackedPacket {
    private final int attackerId;
    private final int receiverId;
    private final float damage;


    public S2CAttackedPacket(int attackerId, int receiverId, float damage) {
        this.attackerId = attackerId;
        this.receiverId = receiverId;
        this.damage = damage;
    }

    public static void encode(S2CAttackedPacket pkt, FriendlyByteBuf buf) {
        buf.writeInt(pkt.attackerId);
        buf.writeInt(pkt.receiverId);
        buf.writeFloat(pkt.damage);
    }

    public static S2CAttackedPacket decode(FriendlyByteBuf buf) {
        return new S2CAttackedPacket(buf.readInt(), buf.readInt(), buf.readFloat());
    }

    public static void handle(S2CAttackedPacket pkt, Supplier<NetworkEvent.Context> ctx) {

        ctx.get().enqueueWork(() -> {
            DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () ->
                    ClientPacketHandler.handleS2CAttackedPacket(pkt.attackerId, pkt.receiverId, pkt.damage)
            );
        });
        ctx.get().setPacketHandled(true);
    }
}