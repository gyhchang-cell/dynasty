package artifacts.component.ability;

import artifacts.component.ability.mobeffect.PostEatingEffect;
import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import artifacts.equipment.EquipmentSlotAccess;
import artifacts.network.payload.PlaySoundAtPlayerPacket;
import artifacts.registry.ModTags;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.LivingEntity;

public record ReplenishHungerOnGrass(
        Value<Boolean> enabled,
        Value<Integer> replenishingDuration,
        Value<Integer> itemDamage
) implements EquipmentAbility {

    public static final Codec<ReplenishHungerOnGrass> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            ValueTypes.enabledField().forGetter(ReplenishHungerOnGrass::enabled),
            ValueTypes.DURATION.codec().fieldOf("duration").forGetter(ReplenishHungerOnGrass::replenishingDuration),
            ValueTypes.itemDamageField().forGetter(ReplenishHungerOnGrass::itemDamage)
    ).apply(instance, ReplenishHungerOnGrass::new));

    public static final StreamCodec<ByteBuf, ReplenishHungerOnGrass> STREAM_CODEC = StreamCodec.composite(
            ValueTypes.BOOLEAN.streamCodec(),
            ReplenishHungerOnGrass::enabled,
            ValueTypes.DURATION.streamCodec(),
            ReplenishHungerOnGrass::replenishingDuration,
            ValueTypes.NON_NEGATIVE_INT.streamCodec(),
            ReplenishHungerOnGrass::itemDamage,
            ReplenishHungerOnGrass::new
    );

    @Override
    public boolean isNonCosmetic() {
        return enabled().get();
    }

    public record Ticker() implements AbilityTicker<ReplenishHungerOnGrass> {

        @Override
        public void wornTick(ReplenishHungerOnGrass ability, EquipmentSlotAccess slot, LivingEntity entity, boolean isOnCooldown, boolean isDisabled) {
            if (!isDisabled && !isOnCooldown && ability.isNonCosmetic() && entity instanceof ServerPlayer player
                    && player.onGround()
                    && player.getFoodData().needsFood()
                    && entity.tickCount % (Math.max(1, ability.replenishingDuration().get()) * 20) == 0
                    && entity.getBlockStateOn().is(ModTags.ROOTED_BOOTS_GRASS)
            ) {
                player.getFoodData().eat(1, 0.5F);
                PostEatingEffect.applyEffects(entity, 1);
                PlaySoundAtPlayerPacket.sendSound(player, SoundEvents.GENERIC_EAT, 0.5F, 0.8F + entity.getRandom().nextFloat() * 0.4F);
                slot.hurtAndBreak(ability.itemDamage.get());
            }
        }
    }
}
