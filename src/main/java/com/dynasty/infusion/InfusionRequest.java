package com.dynasty.infusion;
import java.util.function.Supplier;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkEvent;
public record InfusionRequest(int containerId,int action,int slot,int revision){
    public static void encode(InfusionRequest p,FriendlyByteBuf b){b.writeVarInt(p.containerId);b.writeVarInt(p.action);b.writeInt(p.slot);b.writeInt(p.revision);}
    public static InfusionRequest decode(FriendlyByteBuf b){return new InfusionRequest(b.readVarInt(),b.readVarInt(),b.readInt(),b.readInt());}
    public static void handle(InfusionRequest p,Supplier<NetworkEvent.Context> supplier){var ctx=supplier.get();ctx.enqueueWork(()->{var player=ctx.getSender();if(player!=null&&player.containerMenu instanceof InfusionMenu menu&&menu.containerId==p.containerId)menu.request(player,p.action,p.slot,p.revision);});ctx.setPacketHandled(true);}
}
