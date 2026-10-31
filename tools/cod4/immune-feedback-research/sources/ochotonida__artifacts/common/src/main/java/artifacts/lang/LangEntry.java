package artifacts.lang;

import net.minecraft.network.chat.Component;

import java.util.Optional;

public record LangEntry(String key, Optional<String> english, Object... args) {

    public LangEntry(String key, String english, Object... args) {
        this(key, Optional.of(english), args);
    }

    public LangEntry(String key) {
        this(key, Optional.empty());
    }

    public LangEntry withArgs(Object args) {
        return new LangEntry(key, english, args);
    }

    public LangEntry withPrefix(String prefix) {
        return new LangEntry(prefix + '.' + key, english);
    }

    public LangEntry withSuffix(String suffix) {
        return new LangEntry(key + '.' + suffix, english);
    }

    public LangEntry dropSuffix(String suffix) {
        if (key.endsWith(suffix)) {
            return new LangEntry(key.substring(0, key.lastIndexOf(suffix)), english);
        }
        return this;
    }

    public Component asComponent() {
        return Component.translatable(key, args);
    }
}
