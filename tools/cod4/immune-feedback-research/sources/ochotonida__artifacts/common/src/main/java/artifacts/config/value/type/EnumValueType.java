package artifacts.config.value.type;

import artifacts.config.screen.ConfigEntries;
import com.mojang.serialization.Codec;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.StringRepresentable;
import net.minecraft.util.Util;

import java.util.Arrays;
import java.util.List;
import java.util.function.Function;

public class EnumValueType<T extends Enum<T> & StringRepresentable> extends ValueType<T, String> {

    private final Function<T, Component> toText;
    private final Class<T> enumClass;

    public EnumValueType(Class<T> enumClass, Function<T, Component> toText) {
        this.enumClass = enumClass;
        this.toText = toText;
    }

    public List<T> getValues() {
        return Arrays.asList(enumClass.getEnumConstants());
    }

    @Override
    public String getAllowedValuesComment() {
        StringBuilder builder = new StringBuilder("Allowed Values: ");
        builder.append(enumClass.getEnumConstants()[0].getSerializedName());
        for (int i = 1; i < enumClass.getEnumConstants().length; i++) {
            builder.append(", ").append(enumClass.getEnumConstants()[i].getSerializedName());
        }
        return builder.toString();
    }

    @Override
    public T read(String configValue) {
        for (T value : enumClass.getEnumConstants()) {
            if (value.getSerializedName().equalsIgnoreCase(configValue)) {
                return value;
            }
        }
        throw new IllegalArgumentException("Unknown value '%s'".formatted(configValue));
    }

    @Override
    public String write(T value) {
        return value.getSerializedName();
    }

    @Override
    protected Codec<T> valueCodec() {
        return StringRepresentable.fromValues(enumClass::getEnumConstants);
    }

    @Override
    public StreamCodec<ByteBuf, T> valueStreamCodec() {
        return ByteBufCodecs.idMapper(i -> enumClass.getEnumConstants()[i], Util.createIndexLookup(Arrays.asList(enumClass.getEnumConstants())));
    }

    public Component getAsComponent(T value) {
        return toText.apply(value);
    }

    @Override
    public ConfigEntries.ConfigEntryFactory<T> getConfigEntryFactory() {
        return ConfigEntries.enumConfigEntryFactory(this);
    }
}
