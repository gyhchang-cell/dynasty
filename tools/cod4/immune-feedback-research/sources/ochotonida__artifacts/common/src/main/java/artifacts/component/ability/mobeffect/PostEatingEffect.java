package artifacts.component.ability.mobeffect;

import artifacts.component.ability.EntityCondition;
import artifacts.component.ability.EquipmentAbility;
import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import artifacts.registry.ModDataComponents;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.food.FoodProperties;

public record PostEatingEffect(MobEffectProvider provider, Value<Integer> itemDamage) implements EquipmentAbility {

    public static final Codec<PostEatingEffect> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            MobEffectProvider.codec(false).fieldOf("effect").forGetter(PostEatingEffect::provider),
            ValueTypes.itemDamageField().forGetter(PostEatingEffect::itemDamage)
    ).apply(instance, PostEatingEffect::new));

    public static final StreamCodec<RegistryFriendlyByteBuf, PostEatingEffect> STREAM_CODEC = StreamCodec.composite(
            MobEffectProvider.STREAM_CODEC,
            PostEatingEffect::provider,
            ValueTypes.NON_NEGATIVE_INT.streamCodec(),
            PostEatingEffect::itemDamage,
            PostEatingEffect::new
    );

    public static void applyEffects(LivingEntity entity, FoodProperties properties) {
        int foodPointsMissing = entity instanceof Player player ? 20 - player.getFoodData().getFoodLevel() : 20;
        int foodPointsRestored = Math.min(properties.nutrition(), foodPointsMissing);
        applyEffects(entity, foodPointsRestored);
    }

    public static void applyEffects(LivingEntity entity, int foodPointsRestored) {
        if (foodPointsRestored > 0) {
            ModDataComponents.POST_EATING_EFFECTS.on(entity).iterate((entry, slot) -> {
                if (entry.provider().canApply(entity)) {
                    entity.addEffect(entry.provider().createEffect(foodPointsRestored));
                    slot.hurtAndBreak(entry.itemDamage.get());
                }
            });
        }
    }

    @Override
    public boolean isNonCosmetic() {
        return provider().isNonCosmetic();
    }

    @Override
    public void addToTooltip(TooltipWriter writer) {
        if (provider.mobEffect().equals(MobEffects.HASTE) && provider.condition() == EntityCondition.ALWAYS) {
            writer.add("haste");
        }
    }
}
