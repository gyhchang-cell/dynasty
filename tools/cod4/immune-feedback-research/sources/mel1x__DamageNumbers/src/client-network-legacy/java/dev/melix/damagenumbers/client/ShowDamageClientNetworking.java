package dev.melix.damagenumbers.client;

import dev.melix.damagenumbers.ShowDamageNetworking;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.world.phys.Vec3;

final class ShowDamageClientNetworking {
    private ShowDamageClientNetworking() {
    }

    static void register() {
        ClientPlayNetworking.registerGlobalReceiver(ShowDamageNetworking.ID,
                (client, handler, buffer, responseSender) -> {
                    String presetName = buffer.readUtf(64);
                    Vec3 position = new Vec3(buffer.readDouble(), buffer.readDouble(), buffer.readDouble());
                    float value = buffer.readFloat();
                    client.execute(() -> DamageNumbersClient.showDamage(presetName, position, value));
                });
    }
}
