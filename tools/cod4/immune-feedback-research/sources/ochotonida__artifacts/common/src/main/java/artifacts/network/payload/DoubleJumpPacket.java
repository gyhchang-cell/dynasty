package artifacts.network.payload;

import artifacts.Artifacts;
import artifacts.component.ability.DoubleJump;
import artifacts.network.PayloadContext;
import artifacts.registry.ModDataComponents;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.server.level.ServerPlayer;

public record DoubleJumpPacket() implements CustomPacketPayload {

    public static final Type<DoubleJumpPacket> TYPE = new Type<>(Artifacts.id("double_jump"));

    public static final StreamCodec<FriendlyByteBuf, DoubleJumpPacket> CODEC = StreamCodec.unit(new DoubleJumpPacket());

    public void apply(PayloadContext context) {
        if (context.player() instanceof ServerPlayer player && ModDataComponents.DOUBLE_JUMP.on(player).findAny()) {
            context.queue(() -> {
                DoubleJump.jump(player);

                for (int i = 0; i < 20; ++i) {
                    double motionX = player.getRandom().nextGaussian() * 0.02;
                    double motionY = player.getRandom().nextGaussian() * 0.02 + 0.20;
                    double motionZ = player.getRandom().nextGaussian() * 0.02;
                    ParticleOptions particleType = player.isInWater() ? ParticleTypes.BUBBLE : ParticleTypes.POOF;
                    player.level().sendParticles(particleType, player.getX(), player.getY(), player.getZ(), 1, motionX, motionY, motionZ, 0.15);
                }
            });
        }
    }

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }
}
