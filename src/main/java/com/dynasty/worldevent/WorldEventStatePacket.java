package com.dynasty.worldevent;
import net.minecraft.core.BlockPos;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.network.NetworkEvent;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.api.distmarker.Dist;
import java.util.UUID;
import java.util.function.Supplier;
public record WorldEventStatePacket(UUID uuid,ResourceLocation definition,ResourceLocation dimension,BlockPos center,long started,long expires,int phase,long seed){
    public static void encode(WorldEventStatePacket p,FriendlyByteBuf b){b.writeUUID(p.uuid);b.writeResourceLocation(p.definition);b.writeResourceLocation(p.dimension);b.writeBlockPos(p.center);b.writeLong(p.started);b.writeLong(p.expires);b.writeVarInt(p.phase);b.writeLong(p.seed);}
    public static WorldEventStatePacket decode(FriendlyByteBuf b){return new WorldEventStatePacket(b.readUUID(),b.readResourceLocation(),b.readResourceLocation(),b.readBlockPos(),b.readLong(),b.readLong(),b.readVarInt(),b.readLong());}
    public static void handle(WorldEventStatePacket p,Supplier<NetworkEvent.Context> s){var c=s.get();if(c.getDirection().getReceptionSide().isClient())c.enqueueWork(()->DistExecutor.unsafeRunWhenOn(Dist.CLIENT,()->()->com.dynasty.worldevent.client.WorldEventVisuals.receive(p)));c.setPacketHandled(true);}
}
