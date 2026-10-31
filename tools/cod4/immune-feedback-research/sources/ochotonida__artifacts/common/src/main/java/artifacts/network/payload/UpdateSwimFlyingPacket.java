package artifacts.network.payload;

import artifacts.Artifacts;
import artifacts.component.SwimData;
import artifacts.network.PayloadContext;
import artifacts.platform.PlatformServices;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.world.entity.player.Player;

public record UpdateSwimFlyingPacket(boolean shouldSwim) implements CustomPacketPayload {

    public static final Type<UpdateSwimFlyingPacket> TYPE = new Type<>(Artifacts.id("update_swim_flying"));

    public static final StreamCodec<FriendlyByteBuf, UpdateSwimFlyingPacket> CODEC = StreamCodec.composite(
            ByteBufCodecs.BOOL,
            UpdateSwimFlyingPacket::shouldSwim,
            UpdateSwimFlyingPacket::new
    );

    public void apply(PayloadContext context) {
        Player player = context.player();
        if (player != null) {
            context.queue(() -> {
                SwimData swimData = PlatformServices.getPlatformHelper().getSwimData(player);
                if (swimData != null && swimData.isSwimFlying() ^ shouldSwim()) {
                    swimData.toggleSwimFlying(player);
                }
            });
        }
    }

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }
}
