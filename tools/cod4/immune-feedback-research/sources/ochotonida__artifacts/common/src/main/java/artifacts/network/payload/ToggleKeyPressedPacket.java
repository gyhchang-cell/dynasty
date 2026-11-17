package artifacts.network.payload;

import artifacts.Artifacts;
import artifacts.component.ToggleIdentifier;
import artifacts.equipment.EquipmentSlotManager;
import artifacts.network.PayloadContext;
import artifacts.registry.ModDataComponents;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.util.Unit;
import net.minecraft.world.entity.player.Player;

public record ToggleKeyPressedPacket(ToggleIdentifier identifier) implements CustomPacketPayload {

    public static final Type<ToggleKeyPressedPacket> TYPE = new Type<>(Artifacts.id("toggle_key_pressed"));

    public static final StreamCodec<ByteBuf, ToggleKeyPressedPacket> CODEC =
            ToggleIdentifier.STREAM_CODEC.map(ToggleKeyPressedPacket::new, ToggleKeyPressedPacket::identifier);

    public void apply(PayloadContext context) {
        Player player = context.player();
        context.queue(() -> EquipmentSlotManager.iterateEquipment(player, false, false, stack -> {
            if (stack.get(ModDataComponents.TOGGLE_KEY.get()) instanceof ToggleIdentifier id && id == identifier) {
                if (stack.has(ModDataComponents.DISABLED_BY_TOGGLE.get())) {
                    stack.remove(ModDataComponents.DISABLED_BY_TOGGLE.get());
                } else {
                    stack.set(ModDataComponents.DISABLED_BY_TOGGLE.get(), Unit.INSTANCE);
                }
            }
        }));
    }

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }
}
