package artifacts.component.ability.mobeffect;

import artifacts.component.ability.EntityCondition;
import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.LivingEntity;

public record MobEffectProvider(Holder<MobEffect> mobEffect, Value<Integer> level, Value<Integer> duration, Value<Boolean> spawnParticles, Value<Boolean> showIcon, EntityCondition condition) {

    public static Codec<MobEffectProvider> codec(boolean showParticlesByDefault) {
        return RecordCodecBuilder.create(instance -> instance.group(
                BuiltInRegistries.MOB_EFFECT.holderByNameCodec().fieldOf("id").forGetter(MobEffectProvider::mobEffect),
                ValueTypes.MOB_EFFECT_LEVEL.codec().optionalFieldOf("level", Value.of(1)).forGetter(MobEffectProvider::level),
                ValueTypes.DURATION.codec().optionalFieldOf("duration", Value.of(10)).forGetter(MobEffectProvider::duration),
                ValueTypes.BOOLEAN.codec().optionalFieldOf("spawn_particles", Value.of(showParticlesByDefault)).forGetter(MobEffectProvider::spawnParticles),
                ValueTypes.BOOLEAN.codec().optionalFieldOf("show_icon", Value.of(false)).forGetter(MobEffectProvider::showIcon),
                EntityCondition.CODEC.optionalFieldOf("condition", EntityCondition.ALWAYS).forGetter(MobEffectProvider::condition)
        ).apply(instance, MobEffectProvider::new));
    }

    public static final StreamCodec<RegistryFriendlyByteBuf, MobEffectProvider> STREAM_CODEC = StreamCodec.composite(
            ByteBufCodecs.holderRegistry(Registries.MOB_EFFECT),
            MobEffectProvider::mobEffect,
            ValueTypes.MOB_EFFECT_LEVEL.streamCodec(),
            MobEffectProvider::level,
            ValueTypes.DURATION.streamCodec(),
            MobEffectProvider::duration,
            ValueTypes.BOOLEAN.streamCodec(),
            MobEffectProvider::spawnParticles,
            ValueTypes.BOOLEAN.streamCodec(),
            MobEffectProvider::showIcon,
            EntityCondition.STREAM_CODEC,
            MobEffectProvider::condition,
            MobEffectProvider::new
    );

    public int getDuration(int multiplier) {
        return duration().get() * 20 * multiplier + 19;
    }

    public int getAmplifier() {
        return level().get() - 1;
    }

    public boolean isNonCosmetic() {
        return level().get() > 0 && duration().get() > 0 && condition() != EntityCondition.NEVER;
    }

    public boolean canApply(LivingEntity entity) {
        return isNonCosmetic() && condition.test(entity);
    }

    public MobEffectInstance createEffect() {
        return createEffect(1);
    }

    public MobEffectInstance createEffect(int multiplier) {
        return new MobEffectInstance(mobEffect(), getDuration(multiplier), getAmplifier(), false, spawnParticles().get(), showIcon().get());
    }
}
