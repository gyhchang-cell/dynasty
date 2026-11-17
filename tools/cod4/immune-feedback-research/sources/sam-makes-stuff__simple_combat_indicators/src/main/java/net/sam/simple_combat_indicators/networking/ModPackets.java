package net.sam.simple_combat_indicators.networking;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.network.simple.SimpleChannel;
import net.sam.simple_combat_indicators.SimpleCombatIndicators;
import net.sam.simple_combat_indicators.networking.packets.S2CAttackedPacket;


public class ModPackets {

    private static int id = 0;

    private static final SimpleChannel INSTANCE = NetworkRegistry.ChannelBuilder
            .named(new ResourceLocation(SimpleCombatIndicators.MOD_ID, "main"))
            .networkProtocolVersion(() -> "1.0")
            .clientAcceptedVersions(s -> true)
            .serverAcceptedVersions(s -> true)
            .simpleChannel();

    public static void registerClient(){

        INSTANCE.registerMessage(id, S2CAttackedPacket.class,
                S2CAttackedPacket::encode,
                S2CAttackedPacket::decode,
                S2CAttackedPacket::handle);
        id++;
    }


    public static void sendToServer(Object msg){
        INSTANCE.send(PacketDistributor.SERVER.noArg(), msg);
    }

    public static void sendToAllClients(Object msg){
        INSTANCE.send(PacketDistributor.ALL.noArg(), msg);
    }

    public static void sendToTracking(Entity entity, Object packet) {
        if (entity.level() instanceof ServerLevel serverLevel) {
            for (ServerPlayer player : serverLevel.getChunkSource().chunkMap.getPlayers(entity.chunkPosition(), false)) {
                INSTANCE.send(PacketDistributor.PLAYER.with(() -> player), packet);
            }
        }
    }
}


