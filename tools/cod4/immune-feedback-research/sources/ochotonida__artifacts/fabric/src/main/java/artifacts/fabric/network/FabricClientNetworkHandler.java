package artifacts.fabric.network;

import artifacts.network.ConfigurationNetworkHandler;
import artifacts.network.NetworkHandler;
import artifacts.network.PayloadContext;
import net.fabricmc.fabric.api.client.networking.v1.ClientConfigurationNetworking;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;

public class FabricClientNetworkHandler {

    public static void register() {
        // clientbound receivers
        for (NetworkHandler.PayloadHandler<?> payloadHandler : NetworkHandler.CLIENTBOUND_HANDLERS) {
            registerClientboundReceiver(payloadHandler);
        }
        // clientbound configuration receivers
        for (ConfigurationNetworkHandler.PayloadHandler<?> payloadHandler : ConfigurationNetworkHandler.CLIENTBOUND_HANDLERS) {
            registerClientboundReceiver(payloadHandler);
        }
    }

    private static <T extends CustomPacketPayload> void registerClientboundReceiver(NetworkHandler.PayloadHandler<T> payloadHandler) {
        ClientPlayNetworking.registerGlobalReceiver(payloadHandler.type(), (payload, context) ->
                payloadHandler.receiver().receive(payload, PayloadContext.of(context.player(), context.client()::execute))
        );
    }

    private static <T extends CustomPacketPayload> void registerClientboundReceiver(ConfigurationNetworkHandler.PayloadHandler<T> payloadHandler) {
        ClientConfigurationNetworking.registerGlobalReceiver(payloadHandler.type(), (payload, context) ->
                payloadHandler.receiver().receive(payload, PayloadContext.of(context.client()::execute))
        );
    }
}
