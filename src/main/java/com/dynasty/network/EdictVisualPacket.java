package com.dynasty.network;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.NetworkEvent;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import java.util.*;
import java.util.function.Supplier;
public record EdictVisualPacket(UUID id,int kind,long born,Vec3 origin,Vec3 end) {
    public static void encode(EdictVisualPacket p,FriendlyByteBuf b){b.writeUUID(p.id);b.writeByte(p.kind);b.writeLong(p.born);b.writeDouble(p.origin.x);b.writeDouble(p.origin.y);b.writeDouble(p.origin.z);b.writeDouble(p.end.x);b.writeDouble(p.end.y);b.writeDouble(p.end.z);}
    public static EdictVisualPacket decode(FriendlyByteBuf b){return new EdictVisualPacket(b.readUUID(),b.readByte(),b.readLong(),new Vec3(b.readDouble(),b.readDouble(),b.readDouble()),new Vec3(b.readDouble(),b.readDouble(),b.readDouble()));}
    public static void handle(EdictVisualPacket p,Supplier<NetworkEvent.Context> s){var c=s.get();c.enqueueWork(()->DistExecutor.unsafeRunWhenOn(Dist.CLIENT,()->()->com.dynasty.client.EdictRenderer.receive(p)));c.setPacketHandled(true);}
}
