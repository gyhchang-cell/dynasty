package artifacts.config.value.type;

import artifacts.Artifacts;
import artifacts.config.screen.ConfigEntries;
import artifacts.config.value.ConfigValue;
import artifacts.config.value.Value;
import artifacts.util.ModCodecs;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.StringRepresentable;
import net.minecraft.util.Util;

import java.util.Arrays;
import java.util.function.Supplier;

public abstract class ValueType<T, C> {

    public abstract String getAllowedValuesComment();

    public abstract T read(C c);

    @SuppressWarnings("unchecked")
    public T cast(Object value) {
        return (T) value;
    }

    public abstract C write(T value);

    public final Codec<Value<T>> codec() {
        return ModCodecs.xorAlternative(
                configCodec().flatXmap(
                        DataResult::success,
                        value -> {
                            if (value instanceof ConfigValue<T> configValue
                                    && Artifacts.CONFIG.items.getValues(this).containsKey(configValue.getKey())
                            ) {
                                return DataResult.success(configValue);
                            }
                            return DataResult.error(() -> "Not a valid config value: %s".formatted(value));
                        }
                ),
                constantCodec()
        );
    }

    protected abstract Codec<T> valueCodec();

    public final Codec<Value<T>> constantCodec() {
        return valueCodec().xmap(Value.Constant::new, Supplier::get);
    }

    public final Codec<ConfigValue<T>> configCodec() {
        return StringRepresentable.fromValues(this::getConfigValues);
    }

    public final StreamCodec<ByteBuf, Value<T>> streamCodec() {
        return ByteBufCodecs.BOOL.dispatch(
                value -> value instanceof ConfigValue<?>,
                b -> b ? configReferenceStreamCodec() : valueStreamCodec().map(Value.Constant::new, Supplier::get)
        );
    }

    public abstract StreamCodec<ByteBuf, T> valueStreamCodec();

    public final StreamCodec<ByteBuf, ConfigValue<T>> configReferenceStreamCodec() {
        ConfigValue<T>[] values = getConfigValues();
        return ByteBufCodecs.idMapper(i -> values[i], Util.createIndexLookup(Arrays.asList(values)));
    }

    @SuppressWarnings("unchecked")
    private ConfigValue<T>[] getConfigValues() {
        return Artifacts.CONFIG.items.getValues(this).values().toArray(ConfigValue[]::new);
    }

    public abstract ConfigEntries.ConfigEntryFactory<T> getConfigEntryFactory();
}
