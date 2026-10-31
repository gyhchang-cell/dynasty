package dev.melix.damagenumbers.client;

import dev.melix.damagenumbers.ShowDamagePayload;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.world.phys.Vec3;

final class ShowDamageClientNetworking {
    private ShowDamageClientNetworking() {
    }

    static void register() {
        ClientPlayNetworking.registerGlobalReceiver(ShowDamagePayload.TYPE, (payload, context) ->
                context.client().execute(() -> DamageNumbersClient.showDamage(payload.presetName(),
                        new Vec3(payload.x(), payload.y(), payload.z()), payload.value())));
    }
}
