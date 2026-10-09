package com.dynasty.network;

import com.dynasty.Dynasty;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.network.NetworkDirection;

/** Fixed wire IDs; registration and handshake schema are identical on both physical sides. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID, bus=Mod.EventBusSubscriber.Bus.MOD)
public final class Cod3NetworkRegistration {
    @SubscribeEvent public static void setup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> {
            DynastyNetwork.registerExtension(12, com.dynasty.cod3.Cod3VisualPacket.class,
                    com.dynasty.cod3.Cod3VisualPacket::encode, com.dynasty.cod3.Cod3VisualPacket::decode,
                    com.dynasty.cod3.Cod3VisualPacket::handle, NetworkDirection.PLAY_TO_CLIENT, 1);
        });
    }
    private Cod3NetworkRegistration() {}
}
