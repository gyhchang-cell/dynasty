package artifacts.component.ability.retaliation;

import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;

public class FireEffect extends RetaliationEffect {

    public static final Codec<FireEffect> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            ActivationParams.CODEC.forGetter(FireEffect::activationParams),
            ValueTypes.DURATION.codec().fieldOf("duration").forGetter(FireEffect::fireDuration),
            ValueTypes.BOOLEAN.codec().optionalFieldOf("grant_fire_resistance", Value.of(true)).forGetter(FireEffect::grantsFireResistance)
    ).apply(instance, FireEffect::new));

    public static final StreamCodec<ByteBuf, FireEffect> STREAM_CODEC = StreamCodec.composite(
            ActivationParams.STREAM_CODEC,
            FireEffect::activationParams,
            ValueTypes.DURATION.streamCodec(),
            FireEffect::fireDuration,
            ValueTypes.BOOLEAN.streamCodec(),
            FireEffect::grantsFireResistance,
            FireEffect::new
    );

    private final Value<Integer> fireDuration;
    private final Value<Boolean> grantsFireResistance;

    public FireEffect(ActivationParams activationParams, Value<Integer> fireDuration, Value<Boolean> grantsFireResistance) {
        super("fire", activationParams);
        this.fireDuration = fireDuration;
        this.grantsFireResistance = grantsFireResistance;
    }

    public Value<Integer> fireDuration() {
        return fireDuration;
    }

    public Value<Boolean> grantsFireResistance() {
        return grantsFireResistance;
    }

    @Override
    public boolean isNonCosmetic() {
        return super.isNonCosmetic() && fireDuration().get() > 0;
    }

    @Override
    protected boolean applyEffect(LivingEntity target, LivingEntity attacker) {
        if (!attacker.fireImmune() && attacker.attackable() && fireDuration().get() > 0) {
            if (grantsFireResistance().get()) {
                target.addEffect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, fireDuration().get() * 20, 0, false, false, true));
            }
            attacker.igniteForSeconds(fireDuration().get());
            return true;
        }
        return false;
    }

    @Override
    public void addToTooltip(TooltipWriter writer) {
        super.addToTooltip(writer);
        if (grantsFireResistance().get()) {
            writer.add("fire.fire_resistance");
        }
    }

    @Override
    public final boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof FireEffect that)) return false;
        if (!super.equals(o)) return false;

        return fireDuration.equals(that.fireDuration) && grantsFireResistance.equals(that.grantsFireResistance);
    }

    @Override
    public int hashCode() {
        int result = super.hashCode();
        result = 31 * result + fireDuration.hashCode();
        result = 31 * result + grantsFireResistance.hashCode();
        return result;
    }
}
