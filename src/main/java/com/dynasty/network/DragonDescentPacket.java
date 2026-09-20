package com.dynasty.network;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;
import java.util.UUID;
import java.util.function.Supplier;

public record DragonDescentPacket(long id,int phase,int targetId,UUID targetUuid,long started,
                                  double x,double y,double z,float yaw) {
    public static void encode(DragonDescentPacket p,FriendlyByteBuf b) {
        b.writeLong(p.id);b.writeVarInt(p.phase);b.writeVarInt(p.targetId);b.writeUUID(p.targetUuid);b.writeLong(p.started);
        b.writeDouble(p.x);b.writeDouble(p.y);b.writeDouble(p.z);b.writeFloat(p.yaw);
    }
    public static DragonDescentPacket decode(FriendlyByteBuf b) {
        return new DragonDescentPacket(b.readLong(),b.readVarInt(),b.readVarInt(),b.readUUID(),b.readLong(),
                b.readDouble(),b.readDouble(),b.readDouble(),b.readFloat());
    }
    public static void handle(DragonDescentPacket p,Supplier<NetworkEvent.Context> supplier) {
        var context=supplier.get();
        if(context.getDirection().getReceptionSide().isClient())context.enqueueWork(()->
                DistExecutor.unsafeRunWhenOn(Dist.CLIENT,()->()->com.dynasty.client.ImperialWeaponRenderer.receive(p)));
        context.setPacketHandled(true);
    }
}
