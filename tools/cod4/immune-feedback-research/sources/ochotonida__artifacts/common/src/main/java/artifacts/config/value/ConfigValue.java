package artifacts.config.value;

import artifacts.config.ConfigEntryKey;
import artifacts.config.value.type.ValueType;
import net.minecraft.util.StringRepresentable;

public final class ConfigValue<T> implements Value<T>, StringRepresentable {

    private final ValueType<T, ?> type;
    private final ConfigEntryKey key;
    private final T defaultValue;
    private final boolean requiresRestart;
    private final boolean shouldSyncToClients;

    private T value;

    public ConfigValue(ValueType<T, ?> type, ConfigEntryKey key, T defaultValue, boolean requiresRestart, boolean shouldSyncToClient) {
        this.type = type;
        this.key = key;
        this.defaultValue = defaultValue;
        this.requiresRestart = requiresRestart;
        this.shouldSyncToClients = shouldSyncToClient;
        this.value = this.defaultValue;
    }

    public ConfigEntryKey getKey() {
        return key;
    }

    public String getSerializedName() {
        return key.toString();
    }

    public T get() {
        return value;
    }

    public void set(T value) {
        this.value = value;
    }

    public T getDefaultValue() {
        return defaultValue;
    }

    public ValueType<T, ?> type() {
        return type;
    }

    public boolean requiresRestart() {
        return requiresRestart;
    }

    public boolean shouldSyncToClients() {
        return shouldSyncToClients;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (!(obj instanceof ConfigValue<?> that)) return false;
        return key.equals(that.key);
    }

    @Override
    public int hashCode() {
        return key.hashCode();
    }
}
