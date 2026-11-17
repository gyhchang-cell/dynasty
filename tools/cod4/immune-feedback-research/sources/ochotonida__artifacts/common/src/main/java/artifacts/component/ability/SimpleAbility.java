package artifacts.component.ability;

import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.StreamCodec;

public record SimpleAbility(Value<Boolean> enabled) implements EquipmentAbility {

    public static final Codec<SimpleAbility> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            ValueTypes.enabledField().forGetter(SimpleAbility::enabled)
    ).apply(instance, SimpleAbility::new));

    public static final StreamCodec<ByteBuf, SimpleAbility> STREAM_CODEC = ValueTypes.BOOLEAN.streamCodec()
            .map(SimpleAbility::new, SimpleAbility::enabled);

    @Override
    public boolean isNonCosmetic() {
        return enabled.get();
    }
}
