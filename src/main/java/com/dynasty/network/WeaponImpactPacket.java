package com.dynasty.network;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;

/** Visual only, sent after a successful direct melee hit. */
public record WeaponImpactPacket(int style, double x, double y, double z, float yaw) {
    public static void encode(WeaponImpactPacket p, FriendlyByteBuf b) {
        b.writeVarInt(p.style); b.writeDouble(p.x); b.writeDouble(p.y); b.writeDouble(p.z); b.writeFloat(p.yaw);
    }
    public static WeaponImpactPacket decode(FriendlyByteBuf b) {
        return new WeaponImpactPacket(b.readVarInt(), b.readDouble(), b.readDouble(), b.readDouble(), b.readFloat());
    }
    public static void handle(WeaponImpactPacket p, Supplier<NetworkEvent.Context> supplier) {
        var context = supplier.get();
        if (context.getDirection().getReceptionSide().isClient()) {
            context.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                    () -> () -> com.dynasty.client.ImperialWeaponRenderer.receive(p)));
        }
        context.setPacketHandled(true);
    }
}
