package com.dynasty.network;

import com.dynasty.Dynasty;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.network.NetworkDirection;

/** Fixed wire IDs; registration and handshake schema are identical on both physical sides. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID, bus=Mod.EventBusSubscriber.Bus.MOD)
public final class CombatFeedbackNetworkRegistration {
    @SubscribeEvent public static void setup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> {
            DynastyNetwork.registerExtension(16, com.dynasty.expansion.CombatFeedback.class,
                    com.dynasty.expansion.CombatFeedback::encode, com.dynasty.expansion.CombatFeedback::decode,
                    com.dynasty.expansion.CombatFeedback::handle, NetworkDirection.PLAY_TO_CLIENT, 2);
        });
    }
    private CombatFeedbackNetworkRegistration() {}
}
