package artifacts.component.ability;

import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.StreamCodec;

public record EnderPearlHungerCost(
        Value<Boolean> enabled,
        Value<Integer> foodCost,
        Value<Integer> itemDamage,
        Value<Integer> cooldown
) implements EquipmentAbility {

    public static final Codec<EnderPearlHungerCost> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            ValueTypes.enabledField().forGetter(EnderPearlHungerCost::enabled),
            ValueTypes.NON_NEGATIVE_INT.codec().fieldOf("cost").forGetter(EnderPearlHungerCost::foodCost),
            ValueTypes.itemDamageField().forGetter(EnderPearlHungerCost::itemDamage),
            ValueTypes.cooldownField().forGetter(EnderPearlHungerCost::cooldown)
    ).apply(instance, EnderPearlHungerCost::new));

    public static final StreamCodec<ByteBuf, EnderPearlHungerCost> STREAM_CODEC = StreamCodec.composite(
            ValueTypes.BOOLEAN.streamCodec(),
            EnderPearlHungerCost::enabled,
            ValueTypes.NON_NEGATIVE_INT.streamCodec(),
            EnderPearlHungerCost::foodCost,
            ValueTypes.NON_NEGATIVE_INT.streamCodec(),
            EnderPearlHungerCost::itemDamage,
            ValueTypes.DURATION.streamCodec(),
            EnderPearlHungerCost::cooldown,
            EnderPearlHungerCost::new
    );

    @Override
    public boolean isNonCosmetic() {
        return enabled.get();
    }

    @Override
    public void addToTooltip(TooltipWriter writer) {
        if (foodCost.get() == 0) {
            writer.add("free");
        } else {
            writer.add("cost");
        }
    }
}
