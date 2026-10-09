package com.dynasty.network;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.NetworkEvent;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import java.util.*;
import java.util.function.Supplier;
public record EdictVisualPacket(UUID id,int kind,long born,Vec3 origin,Vec3 end,String dimension,int ownerId,UUID ownerUuid) {
    public static final int WIRE_REVISION=2;
    public EdictVisualPacket(UUID id,int kind,long born,Vec3 origin,Vec3 end){this(id,kind,born,origin,end,"minecraft:overworld",-1,new UUID(0,0));}
    public boolean valid(){return id!=null&&ownerUuid!=null&&ownerId>=-1&&kind>=-1&&kind<=5&&dimension!=null&&dimension.length()<=128
            &&net.minecraft.resources.ResourceLocation.tryParse(dimension)!=null&&origin!=null&&end!=null
            &&Double.isFinite(origin.lengthSqr()+end.lengthSqr())&&origin.distanceToSqr(end)<=1024;}
    public static void encode(EdictVisualPacket p,FriendlyByteBuf b){b.writeUUID(p.id);b.writeByte(p.kind);b.writeLong(p.born);b.writeDouble(p.origin.x);b.writeDouble(p.origin.y);b.writeDouble(p.origin.z);b.writeDouble(p.end.x);b.writeDouble(p.end.y);b.writeDouble(p.end.z);b.writeUtf(p.dimension,128);b.writeInt(p.ownerId);b.writeUUID(p.ownerUuid);}
    public static EdictVisualPacket decode(FriendlyByteBuf b){return new EdictVisualPacket(b.readUUID(),b.readByte(),b.readLong(),new Vec3(b.readDouble(),b.readDouble(),b.readDouble()),new Vec3(b.readDouble(),b.readDouble(),b.readDouble()),b.readUtf(128),b.readInt(),b.readUUID());}
    public static void handle(EdictVisualPacket p,Supplier<NetworkEvent.Context> s){var c=s.get();if(p.valid()&&c.getDirection().getReceptionSide().isClient())c.enqueueWork(()->DistExecutor.unsafeRunWhenOn(Dist.CLIENT,()->()->com.dynasty.client.EdictRenderer.receive(p)));c.setPacketHandled(true);}
}
