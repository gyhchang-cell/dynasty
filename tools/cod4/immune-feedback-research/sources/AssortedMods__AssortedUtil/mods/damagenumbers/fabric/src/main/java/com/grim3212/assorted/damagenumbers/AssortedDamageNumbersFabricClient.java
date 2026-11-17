package com.grim3212.assorted.damagenumbers;

import com.grim3212.assorted.damagenumbers.client.DamageNumbersClient;
import net.fabricmc.api.ClientModInitializer;

public class AssortedDamageNumbersFabricClient implements ClientModInitializer {

    @Override
    public void onInitializeClient() {
        DamageNumbersClient.init();
    }
}
