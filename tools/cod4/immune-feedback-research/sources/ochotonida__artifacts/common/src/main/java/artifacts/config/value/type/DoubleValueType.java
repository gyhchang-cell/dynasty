package artifacts.config.value.type;

import artifacts.config.screen.ConfigEntries;
import com.mojang.serialization.Codec;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.StreamCodec;

public class DoubleValueType extends NumberValueType<Double> {

    public DoubleValueType(Double min, Double max, Codec<Double> valueCodec, StreamCodec<ByteBuf, Double> valueStreamCodec) {
        super(min, max, valueCodec, valueStreamCodec);
    }

    @Override
    public Double read(Number value) {
        return value.doubleValue();
    }

    @Override
    public ConfigEntries.ConfigEntryFactory<Double> getConfigEntryFactory() {
        return ConfigEntries.doubleConfigEntryFactory(this);
    }
}
