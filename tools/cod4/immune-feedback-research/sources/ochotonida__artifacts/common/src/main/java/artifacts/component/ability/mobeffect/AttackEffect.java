package artifacts.component.ability.mobeffect;

import artifacts.component.ability.EquipmentAbility;
import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import artifacts.registry.ModDataComponents;
import artifacts.util.DamageSourceHelper;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;

import java.util.Objects;
import java.util.Set;

public record AttackEffect(MobEffectProvider provider, Value<Double> chance, Value<Integer> cooldown, Value<Integer> itemDamage) implements EquipmentAbility {

    private static final Set<Holder<MobEffect>> CUSTOM_TOOLTIP_MOB_EFFECTS = Set.of(
            MobEffects.WITHER
    );

    public static final Codec<AttackEffect> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            MobEffectProvider.codec(true).fieldOf("effect").forGetter(AttackEffect::provider),
            ValueTypes.FRACTION.codec().optionalFieldOf("chance", Value.of(1D)).forGetter(AttackEffect::chance),
            ValueTypes.DURATION.codec().optionalFieldOf("cooldown", Value.of(0)).forGetter(AttackEffect::cooldown),
            ValueTypes.itemDamageField().forGetter(AttackEffect::itemDamage)
    ).apply(instance, AttackEffect::new));

    public static final StreamCodec<RegistryFriendlyByteBuf, AttackEffect> STREAM_CODEC = StreamCodec.composite(
            MobEffectProvider.STREAM_CODEC,
            AttackEffect::provider,
            ValueTypes.FRACTION.streamCodec(),
            AttackEffect::chance,
            ValueTypes.DURATION.streamCodec(),
            AttackEffect::cooldown,
            ValueTypes.NON_NEGATIVE_INT.streamCodec(),
            AttackEffect::itemDamage,
            AttackEffect::new
    );

    public static void onLivingHurt(LivingEntity target, DamageSource damageSource) {
        LivingEntity attacker = DamageSourceHelper.getAttacker(damageSource);
        if (attacker != null && DamageSourceHelper.isMeleeAttack(damageSource) && !attacker.level().isClientSide()) {
            ModDataComponents.ATTACK_EFFECTS.on(attacker).iterate((effect, slot) -> {
                if (effect.chance().get() > attacker.getRandom().nextDouble()) {
                    target.addEffect(effect.provider().createEffect(), attacker);
                    slot.addCooldown(effect.cooldown.get() * 20);
                    slot.hurtAndBreak(effect.itemDamage.get());
                }
            });
        }
    }

    @Override
    public boolean isNonCosmetic() {
        return provider().isNonCosmetic() && chance().get() > 0;
    }

    @Override
    public void addToTooltip(TooltipWriter writer) {
        for (Holder<MobEffect> mobEffect : CUSTOM_TOOLTIP_MOB_EFFECTS) {
            if (mobEffect.isBound() && mobEffect.value() == provider.mobEffect().value() && isNonCosmetic()) {
                String name = Objects.requireNonNull(BuiltInRegistries.MOB_EFFECT.getKey(mobEffect.value())).getPath();
                if (Mth.equal(chance().get(), 1)) {
                    writer.add(name + ".constant");
                } else {
                    writer.add(name + ".chance");
                }
                return;
            }
        }
    }
}
