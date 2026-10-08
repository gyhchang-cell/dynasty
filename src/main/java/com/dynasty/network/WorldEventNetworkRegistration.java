package com.dynasty.network;

import com.dynasty.Dynasty;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.network.NetworkDirection;

/** Fixed wire IDs; registration and handshake schema are identical on both physical sides. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID, bus=Mod.EventBusSubscriber.Bus.MOD)
public final class WorldEventNetworkRegistration {
    @SubscribeEvent public static void setup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> {
            DynastyNetwork.registerExtension(15, com.dynasty.worldevent.WorldEventStatePacket.class,
                    com.dynasty.worldevent.WorldEventStatePacket::encode, com.dynasty.worldevent.WorldEventStatePacket::decode,
                    com.dynasty.worldevent.WorldEventStatePacket::handle, NetworkDirection.PLAY_TO_CLIENT, 1);
        });
    }
    private WorldEventNetworkRegistration() {}
}
