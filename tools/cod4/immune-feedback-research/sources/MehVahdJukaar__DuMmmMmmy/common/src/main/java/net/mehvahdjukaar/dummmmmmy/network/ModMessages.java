
package net.mehvahdjukaar.dummmmmmy.network;

import net.mehvahdjukaar.moonlight.api.platform.network.NetworkHelper;

public class ModMessages {

    public static void init() {
        NetworkHelper.addNetworkRegistration(ModMessages::registerMessages, 2);
    }

    private static void registerMessages(NetworkHelper.RegisterMessagesEvent event) {
        event.registerClientBound(ClientBoundDamageNumberMessage.TYPE);
        event.registerClientBound(ClientBoundUpdateAnimationMessage.TYPE);
    }
}