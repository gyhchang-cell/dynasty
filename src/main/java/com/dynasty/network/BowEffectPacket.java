package com.dynasty.network;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;

/** Server-authoritative projectile identity and impact position. */
public record BowEffectPacket(int kind, int entityId, int tier, boolean phoenix, double x, double y, double z) {
    public static void encode(BowEffectPacket p, FriendlyByteBuf b) {
        b.writeVarInt(p.kind); b.writeVarInt(p.entityId); b.writeVarInt(p.tier); b.writeBoolean(p.phoenix);
        b.writeDouble(p.x); b.writeDouble(p.y); b.writeDouble(p.z);
    }
    public static BowEffectPacket decode(FriendlyByteBuf b) {
        return new BowEffectPacket(b.readVarInt(), b.readVarInt(), b.readVarInt(), b.readBoolean(),
                b.readDouble(), b.readDouble(), b.readDouble());
    }
    public static void handle(BowEffectPacket p, Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        if (context.getDirection().getReceptionSide().isClient()) {
            context.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                    () -> () -> com.dynasty.client.ClientBowEffects.receive(p)));
        }
        context.setPacketHandled(true);
    }
}
