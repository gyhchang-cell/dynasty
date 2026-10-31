package artifacts.component.ability.mobeffect;

import artifacts.component.ability.AbilityTicker;
import artifacts.component.ability.EntityCondition;
import artifacts.component.ability.EquipmentAbility;
import artifacts.config.value.Value;
import artifacts.equipment.EquipmentSlotAccess;
import artifacts.registry.ModDataComponents;
import artifacts.registry.ModMobEffects;
import com.mojang.serialization.Codec;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.Identifier;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;

import java.util.Objects;
import java.util.Set;

public record EquipmentMobEffect(MobEffectProvider provider) implements EquipmentAbility {

    private static final Set<Holder<MobEffect>> CUSTOM_TOOLTIP_MOB_EFFECTS = Set.of(
            MobEffects.INVISIBILITY,
            ModMobEffects.MAGNETISM
    );

    public static final Codec<EquipmentMobEffect> CODEC =
            MobEffectProvider.codec(false).xmap(EquipmentMobEffect::new, EquipmentMobEffect::provider);
    public static final StreamCodec<RegistryFriendlyByteBuf, EquipmentMobEffect> STREAM_CODEC =
            MobEffectProvider.STREAM_CODEC.map(EquipmentMobEffect::new, EquipmentMobEffect::provider);

    @Override
    public boolean isNonCosmetic() {
        return provider().isNonCosmetic();
    }

    @Override
    public void addToTooltip(TooltipWriter writer) {
        if (CUSTOM_TOOLTIP_MOB_EFFECTS.contains(provider.mobEffect())) {
            Identifier id = BuiltInRegistries.MOB_EFFECT.getKey(provider.mobEffect().value());
            writer.add(Objects.requireNonNull(id).getPath());
        }
        if (provider.mobEffect().value() == net.minecraft.world.effect.MobEffects.NIGHT_VISION.value()) {
            Value<Double> nightVisionStrength = writer.components().get(ModDataComponents.REDUCED_NIGHT_VISION.get());
            if (nightVisionStrength != null && nightVisionStrength.get() < 0.5) {
                writer.add("night_vision.partial");
            } else {
                writer.add("night_vision.full");
            }
        }
        if (provider.mobEffect().value() == net.minecraft.world.effect.MobEffects.WATER_BREATHING.value()) {
            if (provider.condition() == EntityCondition.ALWAYS) {
                writer.add("water_breathing.infinite");
            } else {
                writer.add("water_breathing.limited");
            }
        }
    }

    public record Ticker() implements AbilityTicker<EquipmentMobEffect> {

        @Override
        public void onUnequip(EquipmentMobEffect ability, LivingEntity entity) {
            MobEffectProvider provider = ability.provider;
            MobEffectInstance instance = entity.getEffect(provider.mobEffect());
            if (instance != null
                    && instance.getAmplifier() == provider.getAmplifier()
                    && instance.isVisible() == provider.spawnParticles().get()
                    && instance.showIcon() == provider.showIcon().get()
                    && instance.endsWithin(provider.getDuration(1) * 20 + 19)
            ) {
                entity.removeEffect(provider.mobEffect());
            }
        }

        @Override
        public void wornTick(EquipmentMobEffect ability, EquipmentSlotAccess slotAccess, LivingEntity entity, boolean isOnCooldown, boolean isDisabled) {
            MobEffectProvider provider = ability.provider;
            if (!isDisabled && !isOnCooldown) {
                if (provider.canApply(entity)) {
                    entity.addEffect(provider.createEffect());
                }
            }
        }

    }
}
