package artifacts.component.ability;

import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import artifacts.event.ArtifactHooks;
import artifacts.registry.ModDataComponents;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

public record DoubleJump(
        Value<Boolean> enabled,
        Value<Double> fallDamageMultiplier,
        Value<Double> sprintHorizontalVelocity,
        Value<Double> sprintVerticalVelocity,
        Value<Integer> itemDamage
) implements EquipmentAbility {

    public static final Codec<DoubleJump> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            ValueTypes.enabledField().forGetter(DoubleJump::enabled),
            ValueTypes.FRACTION.codec().optionalFieldOf("fall_damage_multiplier", Value.of(0D)).forGetter(DoubleJump::fallDamageMultiplier),
            ValueTypes.NON_NEGATIVE_DOUBLE.codec().optionalFieldOf("sprint_jump_horizontal_velocity", Value.of(0D)).forGetter(DoubleJump::sprintHorizontalVelocity),
            ValueTypes.NON_NEGATIVE_DOUBLE.codec().optionalFieldOf("sprint_jump_vertical_velocity", Value.of(0D)).forGetter(DoubleJump::sprintVerticalVelocity),
            ValueTypes.itemDamageField().forGetter(DoubleJump::itemDamage)
    ).apply(instance, DoubleJump::new));

    public static final StreamCodec<ByteBuf, DoubleJump> STREAM_CODEC = StreamCodec.composite(
            ValueTypes.BOOLEAN.streamCodec(),
            DoubleJump::enabled,
            ValueTypes.FRACTION.streamCodec(),
            DoubleJump::fallDamageMultiplier,
            ValueTypes.NON_NEGATIVE_DOUBLE.streamCodec(),
            DoubleJump::sprintHorizontalVelocity,
            ValueTypes.NON_NEGATIVE_DOUBLE.streamCodec(),
            DoubleJump::sprintVerticalVelocity,
            ValueTypes.NON_NEGATIVE_INT.streamCodec(),
            DoubleJump::itemDamage,
            DoubleJump::new
    );

    // TODO: cleanup (see vanilla jump logic)
    public static void jump(Player player) {
        double fallDamageMultiplier = ModDataComponents.DOUBLE_JUMP.on(player)
                .minDouble(1D, ability -> ability.fallDamageMultiplier.get());
        if (player.fallDistance > 0 && fallDamageMultiplier > 0) {
            player.causeFallDamage(player.fallDistance, (float) fallDamageMultiplier, player.damageSources().fall());
        }

        player.fallDistance = 0;

        double upwardsMotion = 0.5;
        if (player.hasEffect(MobEffects.JUMP_BOOST)) {
            // noinspection ConstantConditions
            upwardsMotion += 0.1 * (player.getEffect(MobEffects.JUMP_BOOST).getAmplifier() + 1);
        }
        if (player.isSprinting()) {
            upwardsMotion *= 1 + ModDataComponents.DOUBLE_JUMP.on(player)
                    .maxDouble(ability -> ability.sprintVerticalVelocity.get());
        }

        Vec3 motion = player.getDeltaMovement();
        double motionMultiplier = 0;
        if (player.isSprinting()) {
            motionMultiplier = ModDataComponents.DOUBLE_JUMP.on(player)
                    .maxDouble(ability -> ability.sprintHorizontalVelocity.get());
        }
        float direction = (float) (player.getYRot() * Math.PI / 180);
        player.setDeltaMovement(player.getDeltaMovement().add(
                -Mth.sin(direction) * motionMultiplier,
                upwardsMotion - motion.y,
                Mth.cos(direction) * motionMultiplier)
        );

        player.needsSync = true;

        if (!player.level().isClientSide()) {
            player.awardStat(Stats.JUMP);
            if (player.isSprinting()) {
                player.causeFoodExhaustion(0.2F);
            } else {
                player.causeFoodExhaustion(0.05F);
            }

            ModDataComponents.DOUBLE_JUMP.on(player)
                    .iterate((component, slot) -> slot.hurtAndBreak(component.itemDamage.get()));

            if (!ArtifactHooks.fart(player)) {
                player.level().playSound(null, player, SoundEvents.WOOL_FALL, SoundSource.PLAYERS, 1, 0.9F + player.getRandom().nextFloat() * 0.2F);
            }
        }
    }

    @Override
    public boolean isNonCosmetic() {
        return enabled().get();
    }
}
