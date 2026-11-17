package artifacts.component.ability;

import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import artifacts.equipment.EquipmentSlotAccess;
import artifacts.registry.ModTags;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.core.Holder;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.LivingEntity;

import java.util.HashMap;
import java.util.Map;

public record CureEffects(Value<Boolean> enabled, Value<Integer> maxEffectDuration, Value<Integer> itemDamage) implements EquipmentAbility {

    public static final Codec<CureEffects> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            ValueTypes.enabledField().forGetter(CureEffects::enabled),
            ValueTypes.DURATION.codec().fieldOf("duration").forGetter(CureEffects::maxEffectDuration),
            ValueTypes.itemDamageField().forGetter(CureEffects::itemDamage)
    ).apply(instance, CureEffects::new));

    public static final StreamCodec<ByteBuf, CureEffects> STREAM_CODEC = StreamCodec.composite(
            ValueTypes.BOOLEAN.streamCodec(),
            CureEffects::enabled,
            ValueTypes.DURATION.streamCodec(),
            CureEffects::maxEffectDuration,
            ValueTypes.NON_NEGATIVE_INT.streamCodec(),
            CureEffects::itemDamage,
            CureEffects::new
    );

    @Override
    public boolean isNonCosmetic() {
        return enabled().get();
    }

    public record Ticker() implements AbilityTicker<CureEffects> {

        @Override
        public void wornTick(CureEffects ability, EquipmentSlotAccess slot, LivingEntity entity, boolean isOnCooldown, boolean isDisabled) {
            if (isDisabled || isOnCooldown || !ability.isNonCosmetic()) {
                return;
            }
            Map<Holder<MobEffect>, MobEffectInstance> effects = new HashMap<>();

            int maxEffectDuration = ability.maxEffectDuration().get() * 20;
            entity.getActiveEffectsMap().forEach((effect, instance) -> {
                if (effect.is(ModTags.ANTIDOTE_VESSEL_CANCELLABLE) && !instance.endsWithin(maxEffectDuration) && !instance.isInfiniteDuration()) {
                    effects.put(effect, instance);
                }
            });

            effects.forEach((effect, instance) -> {
                entity.removeEffectNoUpdate(effect);
                if (maxEffectDuration > 0) {
                    entity.addEffect(new MobEffectInstance(effect, maxEffectDuration, instance.getAmplifier(), instance.isAmbient(), instance.isVisible(), instance.showIcon()));
                }
            });

            if (!effects.isEmpty()) {
                slot.hurtAndBreak(ability.itemDamage.get());
                slot.addCooldown(2 * 20);
            }
        }
    }
}
