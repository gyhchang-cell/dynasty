package dev.melix.damagenumbers;

import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;

final class ShowDamageNetworking {
    private ShowDamageNetworking() {
    }

    @SuppressWarnings({"rawtypes", "unchecked"})
    static void register() {
        payloadRegistry().register(ShowDamagePayload.TYPE, ShowDamagePayload.CODEC);
        ShowDamageCommand.register();
    }

    @SuppressWarnings({"rawtypes", "unchecked"})
    private static PayloadTypeRegistry payloadRegistry() {
        for (String methodName : new String[]{"playS2C", "clientboundPlay"}) {
            try {
                return (PayloadTypeRegistry) PayloadTypeRegistry.class.getMethod(methodName).invoke(null);
            } catch (ReflectiveOperationException ignored) {
            }
        }
        throw new IllegalStateException("Unsupported Fabric networking registry API");
    }

    static void send(ServerPlayer player, String presetName, Vec3 position, float value) {
        ServerPlayNetworking.send(player, new ShowDamagePayload(presetName, position.x, position.y,
                position.z, value));
    }
}
