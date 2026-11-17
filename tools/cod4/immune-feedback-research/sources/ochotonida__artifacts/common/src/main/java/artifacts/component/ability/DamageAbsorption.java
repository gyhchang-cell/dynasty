package artifacts.component.ability;

import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.Mth;

public record DamageAbsorption(
        Value<Double> absorptionRatio,
        Value<Double> absorptionChance,
        Value<Integer> maxDamageAbsorbed,
        Value<Integer> itemDamage
) implements EquipmentAbility {

    public static final Codec<DamageAbsorption> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            ValueTypes.NON_NEGATIVE_DOUBLE.codec().fieldOf("absorption_ratio").forGetter(DamageAbsorption::absorptionRatio),
            ValueTypes.FRACTION.codec().fieldOf("absorption_chance").forGetter(DamageAbsorption::absorptionChance),
            ValueTypes.NON_NEGATIVE_INT.codec().fieldOf("max_damage_absorbed").forGetter(DamageAbsorption::maxDamageAbsorbed),
            ValueTypes.itemDamageField().forGetter(DamageAbsorption::itemDamage)
    ).apply(instance, DamageAbsorption::new));

    public static final StreamCodec<ByteBuf, DamageAbsorption> STREAM_CODEC = StreamCodec.composite(
            ValueTypes.NON_NEGATIVE_DOUBLE.streamCodec(),
            DamageAbsorption::absorptionRatio,
            ValueTypes.FRACTION.streamCodec(),
            DamageAbsorption::absorptionChance,
            ValueTypes.NON_NEGATIVE_INT.streamCodec(),
            DamageAbsorption::maxDamageAbsorbed,
            ValueTypes.NON_NEGATIVE_INT.streamCodec(),
            DamageAbsorption::itemDamage,
            DamageAbsorption::new
    );

    @Override
    public boolean isNonCosmetic() {
        return absorptionRatio.get() > 0 && absorptionChance.get() > 0 && maxDamageAbsorbed.get() > 0;
    }

    @Override
    public void addToTooltip(TooltipWriter writer) {
        if (Mth.equal(absorptionChance.get(), 1)) {
            writer.add("constant");
        } else {
            writer.add("chance", Math.round(absorptionChance.get() * 100));
        }
    }
}
