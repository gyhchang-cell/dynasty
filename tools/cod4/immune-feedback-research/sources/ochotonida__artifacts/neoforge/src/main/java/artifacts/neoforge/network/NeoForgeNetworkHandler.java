package artifacts.neoforge.network;

import artifacts.network.ConfigurationNetworkHandler;
import artifacts.network.NetworkHandler;
import artifacts.network.PayloadContext;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import net.neoforged.neoforge.network.handling.IPayloadHandler;
import net.neoforged.neoforge.network.registration.PayloadRegistrar;

public class NeoForgeNetworkHandler {

    public static void registerPayloadHandlers(RegisterPayloadHandlersEvent event) {
        PayloadRegistrar registrar = event.registrar("1");
        // register serverbound payloads
        for (NetworkHandler.PayloadHandler<?> payloadHandler : NetworkHandler.SERVERBOUND_HANDLERS) {
            // bidirectional payloads can't be registered separately to playToServer and playToClient (as the same type),
            // they need to be registered using registrar#playBidirectional
            if (NetworkHandler.CLIENTBOUND_HANDLERS.stream().anyMatch(p -> p.type() == payloadHandler.type())) {
                // this cast is needed to get the 4-argument playBidirectional overload,
                // the 3-argument overload passes null as the client-side payload handler
                register((BidirectionalPayloadRegistration) registrar::playBidirectional, payloadHandler);
            } else {
                // register serverbound payloads that aren't bidirectional
                register(registrar::playToServer, payloadHandler);
            }
        }
        // register clientbound payloads
        for (NetworkHandler.PayloadHandler<?> payloadHandler : NetworkHandler.CLIENTBOUND_HANDLERS) {
            // make sure we don't re-register a payload that was already registered as a bidirectional payload above
            if (NetworkHandler.SERVERBOUND_HANDLERS.stream().noneMatch(p -> p.type() == payloadHandler.type())) {
                register(registrar::playToClient, payloadHandler);
            }
        }
        // register clientbound configuration payloads
        for (ConfigurationNetworkHandler.PayloadHandler<?> payloadHandler : ConfigurationNetworkHandler.CLIENTBOUND_HANDLERS) {
            register(registrar::configurationToClient, payloadHandler);
        }
    }

    // A bunch of nonsense that I don't want to repeat for every packet
    private static <T extends CustomPacketPayload> void register(PayloadRegistration registration, NetworkHandler.PayloadHandler<T> payloadHandler) {
        @SuppressWarnings("unchecked")
        StreamCodec<? super FriendlyByteBuf, T> codec = ((StreamCodec<? super FriendlyByteBuf, T>) payloadHandler.codec());
        registration.register(
                payloadHandler.type(), codec,
                (arg, context) -> payloadHandler.receiver().receive(arg, PayloadContext.of(context.player(), context::enqueueWork))
        );
    }

    // Same thing but for configuration phase payloads
    private static <T extends CustomPacketPayload> void register(PayloadRegistration registration, ConfigurationNetworkHandler.PayloadHandler<T> payloadHandler) {
        registration.register(payloadHandler.type(), payloadHandler.codec(), (payload, context) ->
                payloadHandler.receiver().receive(payload, PayloadContext.of(context::enqueueWork))
        );
    }

    @FunctionalInterface
    private interface PayloadRegistration {

        <T extends CustomPacketPayload> void register(
                CustomPacketPayload.Type<T> type,
                StreamCodec<? super FriendlyByteBuf, T> reader,
                IPayloadHandler<T> handler
        );
    }

    @FunctionalInterface
    private interface BidirectionalPayloadRegistration extends PayloadRegistration {
        default <T extends CustomPacketPayload> void register(
                CustomPacketPayload.Type<T> type,
                StreamCodec<? super FriendlyByteBuf, T> reader,
                IPayloadHandler<T> handler
        ) {
            register(type, reader, handler, handler);
        }

        <T extends CustomPacketPayload> void register(
                CustomPacketPayload.Type<T> type,
                StreamCodec<? super FriendlyByteBuf, T> reader,
                IPayloadHandler<T> serverHandler,
                IPayloadHandler<T> clientHandler
        );
    }
}
