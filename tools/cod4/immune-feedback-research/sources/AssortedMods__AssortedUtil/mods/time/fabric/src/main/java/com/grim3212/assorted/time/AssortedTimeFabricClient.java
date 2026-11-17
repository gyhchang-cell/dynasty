package com.grim3212.assorted.time;

import com.grim3212.assorted.time.client.TimeClient;
import net.fabricmc.api.ClientModInitializer;

public class AssortedTimeFabricClient implements ClientModInitializer {

    @Override
    public void onInitializeClient() {
        TimeClient.init();
    }
}
