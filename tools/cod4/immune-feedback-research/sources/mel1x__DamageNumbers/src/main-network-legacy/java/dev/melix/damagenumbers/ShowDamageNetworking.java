package dev.melix.damagenumbers;

import net.fabricmc.fabric.api.networking.v1.PacketByteBufs;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;

public final class ShowDamageNetworking {
    public static final ResourceLocation ID = new ResourceLocation(DamageNumbers.MOD_ID, "show_damage");

    private ShowDamageNetworking() {
    }

    static void register() {
        ShowDamageCommand.register();
    }

    static void send(ServerPlayer player, String presetName, Vec3 position, float value) {
        FriendlyByteBuf buffer = PacketByteBufs.create();
        buffer.writeUtf(presetName, 64);
        buffer.writeDouble(position.x);
        buffer.writeDouble(position.y);
        buffer.writeDouble(position.z);
        buffer.writeFloat(value);
        ServerPlayNetworking.send(player, ID, buffer);
    }
}
