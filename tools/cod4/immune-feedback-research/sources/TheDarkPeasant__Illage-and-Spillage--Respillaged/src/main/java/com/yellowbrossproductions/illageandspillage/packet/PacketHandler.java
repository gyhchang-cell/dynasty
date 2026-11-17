package com.yellowbrossproductions.illageandspillage.packet;

import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.simple.SimpleChannel;

public class PacketHandler {
    private static final String PROTOCOL_VERSION = "2";
    public static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(
            new ResourceLocation("illageandspillage", "main"),
            () -> PROTOCOL_VERSION,
            PROTOCOL_VERSION::equals,
            PROTOCOL_VERSION::equals
    );

    public static void init() {
        int id = 0;
        CHANNEL.registerMessage(id++, ParticlePacket.class, ParticlePacket::encode, ParticlePacket::new, ParticlePacket.Handler::onMessage);
        CHANNEL.registerMessage(id++, JumpscareSyncPacket.class, JumpscareSyncPacket::encode, JumpscareSyncPacket::decode, JumpscareSyncPacket::handle);
        CHANNEL.registerMessage(id++, MobFollowingSoundPacket.class, MobFollowingSoundPacket::encode, MobFollowingSoundPacket::decode, MobFollowingSoundPacket::handle);
    }
}
