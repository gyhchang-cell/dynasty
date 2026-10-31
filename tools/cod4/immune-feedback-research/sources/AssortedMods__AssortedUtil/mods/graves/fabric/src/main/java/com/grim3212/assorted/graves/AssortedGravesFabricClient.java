package com.grim3212.assorted.graves;

import com.grim3212.assorted.graves.client.GravesClient;
import net.fabricmc.api.ClientModInitializer;

public class AssortedGravesFabricClient implements ClientModInitializer {

    @Override
    public void onInitializeClient() {
        GravesClient.init();
    }
}
