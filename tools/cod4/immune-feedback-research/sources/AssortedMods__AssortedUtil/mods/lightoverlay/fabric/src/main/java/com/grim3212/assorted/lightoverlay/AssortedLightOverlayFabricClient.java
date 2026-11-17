package com.grim3212.assorted.lightoverlay;

import com.grim3212.assorted.lightoverlay.client.LightOverlayClient;
import net.fabricmc.api.ClientModInitializer;

public class AssortedLightOverlayFabricClient implements ClientModInitializer {

    @Override
    public void onInitializeClient() {
        LightOverlayClient.init();
    }
}
