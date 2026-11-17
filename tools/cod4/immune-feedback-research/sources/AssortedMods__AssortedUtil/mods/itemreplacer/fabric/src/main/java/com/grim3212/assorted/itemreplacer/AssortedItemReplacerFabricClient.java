package com.grim3212.assorted.itemreplacer;

import com.grim3212.assorted.itemreplacer.client.ItemReplacerClient;
import net.fabricmc.api.ClientModInitializer;

public class AssortedItemReplacerFabricClient implements ClientModInitializer {

    @Override
    public void onInitializeClient() {
        ItemReplacerClient.init();
    }
}
