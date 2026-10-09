package com.dynasty.network;

import com.dynasty.Dynasty;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.network.NetworkDirection;

/** Fixed wire IDs; registration and handshake schema are identical on both physical sides. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID, bus=Mod.EventBusSubscriber.Bus.MOD)
public final class EdictNetworkRegistration {
    @SubscribeEvent public static void setup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> {
            DynastyNetwork.registerExtension(13, EdictCastPacket.class, EdictCastPacket::encode,
                    EdictCastPacket::decode, EdictCastPacket::handle, NetworkDirection.PLAY_TO_SERVER, 1);
            DynastyNetwork.registerExtension(14, EdictVisualPacket.class, EdictVisualPacket::encode,
                    EdictVisualPacket::decode, EdictVisualPacket::handle, NetworkDirection.PLAY_TO_CLIENT, EdictVisualPacket.WIRE_REVISION);
        });
    }
    private EdictNetworkRegistration() {}
}
