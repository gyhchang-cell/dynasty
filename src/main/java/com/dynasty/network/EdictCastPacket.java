package com.dynasty.network;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;
/** No client supplied cooldown, coordinates, damage or victim. */
public record EdictCastPacket() {
    public static void encode(EdictCastPacket p,FriendlyByteBuf b){}
    public static EdictCastPacket decode(FriendlyByteBuf b){return new EdictCastPacket();}
    public static void handle(EdictCastPacket p,Supplier<NetworkEvent.Context> s){var c=s.get();c.enqueueWork(()->{if(c.getSender()!=null)com.dynasty.EdictSpells.cast(c.getSender(),0);});c.setPacketHandled(true);}
}
