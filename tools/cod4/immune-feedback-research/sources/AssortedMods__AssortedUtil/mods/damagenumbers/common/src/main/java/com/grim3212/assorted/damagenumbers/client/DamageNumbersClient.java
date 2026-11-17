package com.grim3212.assorted.damagenumbers.client;

import com.grim3212.assorted.damagenumbers.Constants;
import com.grim3212.assorted.damagenumbers.client.damage.DamageNumbers;
import com.grim3212.assorted.damagenumbers.config.DamageNumbersClientConfig;
import com.grim3212.assorted.lib.family.Families;
import com.grim3212.assorted.lib.platform.ClientServices;
import net.minecraft.resources.Identifier;

/** Client-only startup, called by both loaders' client entry points. */
public class DamageNumbersClient {

    public static final DamageNumbersClientConfig CONFIG = new DamageNumbersClientConfig();

    public static void init() {
        Families.join(Constants.MOD_ID, Constants.FAMILY_ID)
                .icon(Identifier.withDefaultNamespace("clock"), 10)
                .manualOrder(160);

        ClientServices.CLIENT.registerClientTickEnd(DamageNumbers::tick);
        ClientServices.CLIENT.registerLevelSubmit(DamageNumbers::submit);
    }
}
