package artifacts.component.ability.retaliation;

import artifacts.component.ability.EquipmentAbility;
import artifacts.equipment.EquipmentSlotAccess;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;

import java.util.Optional;

public record RetaliationEffects(Optional<ThornsEffect> thorns, Optional<FireEffect> fire, Optional<LightningEffect> lightning) implements EquipmentAbility {

    public static final Codec<RetaliationEffects> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            ThornsEffect.CODEC.optionalFieldOf("thorns").forGetter(RetaliationEffects::thorns),
            FireEffect.CODEC.optionalFieldOf("fire").forGetter(RetaliationEffects::fire),
            LightningEffect.CODEC.optionalFieldOf("lightning").forGetter(RetaliationEffects::lightning)
    ).apply(instance, RetaliationEffects::new));

    public static final StreamCodec<ByteBuf, RetaliationEffects> STREAM_CODEC = StreamCodec.composite(
            ByteBufCodecs.optional(ThornsEffect.STREAM_CODEC),
            RetaliationEffects::thorns,
            ByteBufCodecs.optional(FireEffect.STREAM_CODEC),
            RetaliationEffects::fire,
            ByteBufCodecs.optional(LightningEffect.STREAM_CODEC),
            RetaliationEffects::lightning,
            RetaliationEffects::new
    );

    public void onLivingHurt(LivingEntity entity, EquipmentSlotAccess slotAccess, DamageSource damageSource) {
        thorns.ifPresent(effect -> effect.onLivingHurt(entity, slotAccess, damageSource));
        fire.ifPresent(effect -> effect.onLivingHurt(entity, slotAccess, damageSource));
        lightning.ifPresent(effect -> effect.onLivingHurt(entity, slotAccess, damageSource));
    }

    @Override
    public boolean isNonCosmetic() {
        return thorns.isPresent() && thorns.get().isNonCosmetic()
                || fire.isPresent() && fire.get().isNonCosmetic()
                || lightning.isPresent() && lightning.get().isNonCosmetic();
    }

    @Override
    public void addToTooltip(TooltipWriter writer) {
        addToTooltip(writer, thorns);
        addToTooltip(writer, fire);
        addToTooltip(writer, lightning);
    }

    private void addToTooltip(TooltipWriter writer, Optional<? extends RetaliationEffect> effect) {
        if (effect.isPresent() && effect.get().isNonCosmetic()) {
            effect.get().addToTooltip(writer);
        }
    }
}
