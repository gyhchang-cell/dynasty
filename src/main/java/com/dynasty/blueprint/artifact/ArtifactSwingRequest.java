package com.dynasty.blueprint.artifact;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;
/** Empty swing request for left clicks in air. The server resolves the actual hand and targets. */
public record ArtifactSwingRequest() {
    public static void encode(ArtifactSwingRequest p,FriendlyByteBuf b){}
    public static ArtifactSwingRequest decode(FriendlyByteBuf b){return com.dynasty.network.NetworkIntent.complete(b,new ArtifactSwingRequest());}
    public static void handle(ArtifactSwingRequest p,Supplier<NetworkEvent.Context> supplier){var c=supplier.get();c.enqueueWork(()->{var player=c.getSender();if(player!=null)ArtifactCombat.swing(player);});c.setPacketHandled(true);}
}
