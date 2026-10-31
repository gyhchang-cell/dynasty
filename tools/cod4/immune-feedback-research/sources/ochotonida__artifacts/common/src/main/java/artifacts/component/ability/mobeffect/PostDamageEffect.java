package artifacts.component.ability.mobeffect;

import artifacts.component.ability.EquipmentAbility;
import artifacts.registry.ModDataComponents;
import artifacts.util.ModCodecs;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;

import java.util.Optional;

public record PostDamageEffect(
        MobEffectProvider provider,
        Optional<TagKey<DamageType>> tag
) implements EquipmentAbility {

    public static final Codec<PostDamageEffect> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            MobEffectProvider.codec(true).fieldOf("effect").forGetter(PostDamageEffect::provider),
            TagKey.codec(Registries.DAMAGE_TYPE).optionalFieldOf("tag").forGetter(PostDamageEffect::tag)
    ).apply(instance, PostDamageEffect::new));

    public static final StreamCodec<RegistryFriendlyByteBuf, PostDamageEffect> STREAM_CODEC = StreamCodec.composite(
            MobEffectProvider.STREAM_CODEC,
            PostDamageEffect::provider,
            ByteBufCodecs.optional(ModCodecs.tagKeyStreamCodec(Registries.DAMAGE_TYPE)),
            PostDamageEffect::tag,
            PostDamageEffect::new
    );

    public static void onLivingDamaged(LivingEntity entity, DamageSource damageSource) {
        if (!entity.level().isClientSide()) {
            ModDataComponents.POST_DAMAGE_EFFECTS.on(entity).iterate((entry, _) -> {
                if (entry.shouldApply(damageSource, entity)) {
                    entity.addEffect(entry.provider.createEffect());
                }
            });
        }
    }

    public boolean shouldApply(DamageSource damageSource, LivingEntity entity) {
        return provider.canApply(entity) && (tag.isEmpty() || damageSource.is(tag.get()));
    }

    @Override
    public boolean isNonCosmetic() {
        return provider.isNonCosmetic();
    }

    @Override
    public void addToTooltip(TooltipWriter writer) {
        if (provider.mobEffect().equals(MobEffects.FIRE_RESISTANCE) && tag.isPresent() && tag.get().equals(DamageTypeTags.IS_FIRE)) {
            writer.add("fire_resistance");
        } else if (provider.mobEffect().equals(MobEffects.SPEED) && tag.isEmpty()) {
            writer.add("speed");
        }
    }
}
