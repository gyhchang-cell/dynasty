package artifacts.network;

import artifacts.network.payload.UpdateConfigValuePacket;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;

import java.util.ArrayList;
import java.util.List;

public class ConfigurationNetworkHandler {

    public static final List<PayloadHandler<?>> CLIENTBOUND_HANDLERS = new ArrayList<>();

    public static void registerPayloads() {
        registerClientbound(UpdateConfigValuePacket.TYPE, UpdateConfigValuePacket.CODEC, UpdateConfigValuePacket::apply);
    }

    private static <T extends CustomPacketPayload> void registerClientbound(CustomPacketPayload.Type<T> type, StreamCodec<? super FriendlyByteBuf, T> codec, Receiver<T> receiver) {
        CLIENTBOUND_HANDLERS.add(new PayloadHandler<>(type, codec, receiver));
    }

    // Configuration phase uses a FriendlyByteBuf, registries aren't loaded yet
    public record PayloadHandler<T extends CustomPacketPayload>(
            CustomPacketPayload.Type<T> type,
            StreamCodec<? super FriendlyByteBuf, T> codec,
            Receiver<T> receiver
    ) { }

    @FunctionalInterface
    public interface Receiver<T extends CustomPacketPayload> {
        void receive(T value, PayloadContext context);
    }
}
