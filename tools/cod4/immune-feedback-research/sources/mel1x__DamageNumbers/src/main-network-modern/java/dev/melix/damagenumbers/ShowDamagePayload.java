package dev.melix.damagenumbers;

import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;

public record ShowDamagePayload(String presetName, double x, double y, double z, float value)
        implements CustomPacketPayload {
    public static final Type<ShowDamagePayload> TYPE = createType();
    public static final StreamCodec<RegistryFriendlyByteBuf, ShowDamagePayload> CODEC =
            CustomPacketPayload.codec(ShowDamagePayload::write, ShowDamagePayload::read);

    private static void write(ShowDamagePayload payload, RegistryFriendlyByteBuf buffer) {
        buffer.writeUtf(payload.presetName, 64);
        buffer.writeDouble(payload.x);
        buffer.writeDouble(payload.y);
        buffer.writeDouble(payload.z);
        buffer.writeFloat(payload.value);
    }

    private static ShowDamagePayload read(RegistryFriendlyByteBuf buffer) {
        return new ShowDamagePayload(buffer.readUtf(64), buffer.readDouble(), buffer.readDouble(),
                buffer.readDouble(), buffer.readFloat());
    }

    @SuppressWarnings("unchecked")
    private static Type<ShowDamagePayload> createType() {
        for (String className : new String[]{
                "net.minecraft.resources.ResourceLocation", "net.minecraft.resources.Identifier"}) {
            try {
                Class<?> identifierClass = Class.forName(className);
                Object identifier = identifierClass
                        .getMethod("fromNamespaceAndPath", String.class, String.class)
                        .invoke(null, DamageNumbers.MOD_ID, "show_damage");
                return (Type<ShowDamagePayload>) Type.class.getConstructor(identifierClass)
                        .newInstance(identifier);
            } catch (ReflectiveOperationException ignored) {
            }
        }
        throw new IllegalStateException("Unsupported Minecraft identifier API");
    }

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }
}
