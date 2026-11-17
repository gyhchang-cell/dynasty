package artifacts.config;

import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

public record ConfigEntryKey(String configManager, List<String> path) implements Comparable<ConfigEntryKey> {

    public static final StreamCodec<ByteBuf, ConfigEntryKey> STREAM_CODEC = StreamCodec.composite(
            ByteBufCodecs.STRING_UTF8, ConfigEntryKey::configManager,
            ByteBufCodecs.collection(ArrayList::new, ByteBufCodecs.STRING_UTF8), ConfigEntryKey::path,
            ConfigEntryKey::new
    );

    public ConfigEntryKey {
        path = List.copyOf(path);
    }

    public ConfigEntryKey(String configManager, String path) {
        this(configManager, splitPath(path));
    }

    public String joinedPath() {
        return String.join(".", path);
    }

    public Optional<ConfigEntryKey> parent() {
        if (path.size() <= 1) {
            return Optional.empty();
        }
        return Optional.of(new ConfigEntryKey(configManager, path.subList(0, path.size() - 1)));
    }

    @Override
    public String toString() {
        return configManager + '.' + joinedPath();
    }

    @Override
    public int compareTo(ConfigEntryKey other) {
        return toString().compareTo(other.toString());
    }

    private static List<String> splitPath(String path) {
        return Arrays.asList(path.split("\\."));
    }
}
