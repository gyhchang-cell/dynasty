package artifacts.config;

import artifacts.Artifacts;
import artifacts.ArtifactsClient;
import artifacts.config.display.ConfigEntryDisplay;
import artifacts.config.display.SharedConfigLang;
import artifacts.config.value.ConfigValue;
import artifacts.config.value.ValueTypes;
import artifacts.config.value.type.EnumValueType;
import artifacts.config.value.type.NumberValueType;
import artifacts.config.value.type.ValueType;
import artifacts.lang.LangEntry;
import artifacts.lang.LangUtil;
import artifacts.network.NetworkHandler;
import artifacts.network.payload.UpdateConfigValuePacket;
import artifacts.platform.PlatformServices;
import com.electronwill.nightconfig.core.ConfigFormat;
import com.electronwill.nightconfig.core.ConfigSpec;
import com.electronwill.nightconfig.core.file.CommentedFileConfig;
import com.electronwill.nightconfig.core.file.FileWatcher;
import com.electronwill.nightconfig.core.io.ParsingException;
import com.electronwill.nightconfig.core.io.WritingMode;
import net.minecraft.network.protocol.Packet;
import net.minecraft.server.MinecraftServer;
import net.minecraft.util.StringRepresentable;
import org.apache.commons.io.FilenameUtils;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;
import java.util.function.Consumer;

// see Neoforge ConfigFileTypeHandler
public abstract class ConfigManager {

    protected CommentedFileConfig config;
    protected final ConfigSpec spec = new ConfigSpec();
    private final Path configPath;
    private final String name;

    private final Map<ConfigEntryKey, ConfigValue<?>> values = new HashMap<>();
    private final Map<ConfigEntryKey, ConfigEntryDisplay> displays = new HashMap<>();

    private final Map<ValueType<?, ?>, Map<ConfigEntryKey, ConfigValue<?>>> typeToValues = new HashMap<>();

    protected ConfigManager(String fileName) {
        this.name = fileName;
        this.configPath = Path.of(Artifacts.MOD_ID, "%s.toml".formatted(fileName));
    }

    protected ConfigEntryKey key(String path) {
        return new ConfigEntryKey(getName(), path);
    }

    protected void checkKey(ConfigEntryKey key) {
        if (!key.configManager().equals(getName())) {
            throw new IllegalArgumentException();
        }
    }

    protected void setup() {
        config = CommentedFileConfig.builder(PlatformServices.getPlatformHelper().getConfigDir().resolve(configPath))
                .sync()
                .preserveInsertionOrder()
                .autosave()
                .onFileNotFound(this::createNewConfigFile)
                .writingMode(WritingMode.REPLACE)
                .build();

        Path path = PlatformServices.getPlatformHelper().getConfigDir().resolve(configPath);

        try {
            config.load();
        } catch (ParsingException exception) {
            Artifacts.LOGGER.warn("Failed to load config file {}, attempting to recreate", configPath);
            try {
                createBackup(config.getNioPath(), 5);
                Files.delete(config.getNioPath());
                config.load();
            } catch (Throwable t) {
                exception.addSuppressed(t);
                throw new RuntimeException("Failed to load config file " + configPath, exception);
            }
        }

        if (!spec.isCorrect(config)) {
            correctConfigAndSave();
        }

        Artifacts.LOGGER.debug("Loaded config file {}", configPath);
        FileWatcher.defaultInstance().addWatch(path, new ConfigWatcher());
        Artifacts.LOGGER.debug("Watching config file {} for changes", configPath);
    }

    private boolean createNewConfigFile(Path file, ConfigFormat<?> conf) throws IOException {
        Files.createDirectories(file.getParent());
        Files.createFile(file);
        conf.initEmptyFile(file);
        return true;
    }

    private void correctConfigAndSave() {
        addMissingKeys();
        spec.correct(config);
        config.save();
    }

    public String getName() {
        return name;
    }

    public Map<ConfigEntryKey, ConfigValue<?>> getValues() {
        return values;
    }

    public Map<ConfigEntryKey, ConfigEntryDisplay> getDisplays() {
        return displays;
    }

    @SuppressWarnings("unchecked")
    public <T> Map<ConfigEntryKey, ConfigValue<T>> getValues(ValueType<T, ?> type) {
        return (Map<ConfigEntryKey, ConfigValue<T>>) (Object) typeToValues.get(type);
    }

    public ConfigEntryDisplay getDisplay(ConfigEntryKey key) {
        return displays.get(key);
    }

    public List<LangEntry> getDescription(ConfigEntryKey key) {
        return displays.get(key).description();
    }

    public <T, C> T read(ValueType<T, C> type, ConfigEntryKey key) {
        checkKey(key);
        return type.read(config.get(key.joinedPath()));
    }

    public <T, C> void write(ValueType<T, C> type, ConfigEntryKey key, T value) {
        checkKey(key);
        config.set(key.joinedPath(), type.write(value));
    }

    private <T> void reset(ConfigEntryKey key, ConfigValue<T> value) {
        checkKey(key);
        config.add(key.joinedPath(), value.type().write(value.getDefaultValue()));
    }

    protected <T> void readValueFromConfig(ConfigEntryKey key, ConfigValue<T> value) {
        value.set(read(value.type(), key));
    }

    public void readValuesFromConfig(boolean readSyncedValues) {
        getValues().forEach((key, value) -> {
            // Clients should always receive synced configs from the server, only servers should read these from file
            if (!value.shouldSyncToClients() || readSyncedValues) {
                readValueFromConfig(key, value);
            }
        });
    }

    protected void addMissingKeys() {
        Map<ConfigEntryKey, ConfigValue<?>> values = getValues();

        List<ConfigEntryKey> keys = new ArrayList<>(values.keySet());
        Collections.sort(keys);
        for (ConfigEntryKey key : keys) {
            if (!config.contains(key.joinedPath())) {
                ConfigValue<?> value = values.get(key);
                reset(key, value);
                StringBuilder builder = new StringBuilder();
                for (LangEntry entry : getDescription(key)) {
                    entry.english().ifPresent(line -> builder.append(line.formatted(entry.args())).append('\n'));
                }
                builder.append(value.type().getAllowedValuesComment());
                config.setComment(key.joinedPath(), builder.toString());
            }
        }
    }

    public void onConfigChanged() {
        // Don't read synced config values when this would override those received from the server
        boolean readSyncedValues = PlatformServices.getPlatformHelper().isDedicatedServer()
                || !ArtifactsClient.isConnectedToRemoteServer();
        readValuesFromConfig(readSyncedValues);
        if (Artifacts.getCurrentServer() != null) {
            Artifacts.LOGGER.info("Sending updated {} config values to connected clients", getName());
            sendToClients(Artifacts.getCurrentServer());
        }
    }

    private void sendToClients(MinecraftServer server) {
        getValues().forEach((_, value) -> {
            if (value.shouldSyncToClients()) {
                NetworkHandler.sendToPlayers(server.getPlayerList().getPlayers(), UpdateConfigValuePacket.of(value));
            }
        });
    }

    public void sendToClient(Consumer<Packet<?>> connection) {
        Artifacts.LOGGER.info("Sending {} config values to client", getName());
        getValues().forEach((_, value) -> {
            if (value.shouldSyncToClients()) {
                NetworkHandler.sendToClient(connection, UpdateConfigValuePacket.of(value));
            }
        });
    }

    public static void createBackup(final Path commentedFileConfig, final int maxBackups) {
        Path bakFileLocation = commentedFileConfig.getParent();
        String bakFileName = FilenameUtils.removeExtension(commentedFileConfig.getFileName().toString());
        String bakFileExtension = FilenameUtils.getExtension(commentedFileConfig.getFileName().toString()) + ".bak";
        Path bakFile = bakFileLocation.resolve(bakFileName + "-1" + "." + bakFileExtension);
        try {
            for (int i = maxBackups; i > 0; i--) {
                Path oldBak = bakFileLocation.resolve(bakFileName + "-" + i + "." + bakFileExtension);
                if (Files.exists(oldBak)) {
                    if (i >= maxBackups)
                        Files.delete(oldBak);
                    else
                        Files.move(oldBak, bakFileLocation.resolve(bakFileName + "-" + (i + 1) + "." + bakFileExtension));
                }
            }
            Files.copy(commentedFileConfig, bakFile);
        } catch (IOException exception) {
            Artifacts.LOGGER.warn("Failed to back up config file {}", commentedFileConfig, exception);
        }
    }

    protected ConfigValueBuilder<Boolean> define(String path, boolean defaultValue) {
        return new ConfigValueBuilder<>(path, ValueTypes.BOOLEAN, defaultValue) {
            @Override
            protected void defineInSpec() {
                spec.define(path, defaultValue);
            }
        };
    }

    protected <T extends Number & Comparable<T>> ConfigValueBuilder<T> define(String key, NumberValueType<T> type, T defaultValue) {
        return new ConfigValueBuilder<>(key, type, defaultValue) {
            @Override
            protected void defineInSpec() {
                spec.defineInRange(key, defaultValue, type.getMin(), type.getMax());
            }
        };
    }

    protected <T extends Enum<T> & StringRepresentable> ConfigValueBuilder<T> define(String key, EnumValueType<T> type, T defaultValue) {
        return new ConfigValueBuilder<>(key, type, defaultValue) {
            @Override
            protected void defineInSpec() {
                List<String> allowedValues = new ArrayList<>();
                allowedValues.addAll(type.getValues().stream().map(StringRepresentable::getSerializedName).toList());
                allowedValues.addAll(type.getValues().stream().map(StringRepresentable::getSerializedName).map(String::toUpperCase).toList());
                spec.defineInList(key, defaultValue.getSerializedName(), allowedValues);
            }
        };
    }

    public abstract class SubCategory {

        private final ConfigEntryKey key;

        protected SubCategory(SubCategory parent, String name) {
            this(parent.addPrefix(name));
        }

        protected SubCategory(String name) {
            this.key = new ConfigEntryKey(ConfigManager.this.getName(), name);
        }

        public ConfigEntryKey getKey() {
            return key;
        }

        protected void setTitle(String english) {
            setTitle(new LangEntry(key.toString(), english)
                    .withPrefix("artifacts.config")
                    .withSuffix("title")
            );
        }

        // TODO: Title should be a constructor argument
        // TODO: Subcategories do not respect display priority
        protected void setTitle(LangEntry title) {
            ConfigManager.this.displays.put(key, new ConfigEntryDisplay(title, List.of(), 1));
        }

        protected ConfigValueBuilder<Boolean> define(String key, boolean defaultValue) {
            return ConfigManager.this.define(addPrefix(key), defaultValue);
        }

        protected <T extends Number & Comparable<T>> ConfigValueBuilder<T> define(String key, NumberValueType<T> type, T defaultValue) {
            return ConfigManager.this.define(addPrefix(key), type, defaultValue);
        }

        protected <T extends Enum<T> & StringRepresentable> ConfigValueBuilder<T> define(String key, EnumValueType<T> type, T defaultValue) {
            return ConfigManager.this.define(addPrefix(key), type, defaultValue);
        }

        protected String addPrefix(String key) {
            return this.key.joinedPath() + '.' + key;
        }
    }

    public abstract class ConfigValueBuilder<T> {

        private final ConfigEntryKey key;
        private final ValueType<T, ?> type;
        private final T defaultValue;

        private int displayPriority = 0;
        private int customTooltipCount = 0;
        private final List<LangEntry> tooltip = new ArrayList<>();
        private LangEntry title;
        private boolean requiresRestart = false;
        private boolean shouldSyncToClients = false;

        public ConfigValueBuilder(String path, ValueType<T, ?> type, T defaultValue) {
            this.key = key(path);
            this.defaultValue = defaultValue;
            this.type = type;
            setDefaultTitle(key);
        }

        protected abstract void defineInSpec();

        public ConfigValue<T> build() {
            defineInSpec();

            if (customTooltipCount == 1) {
                tooltip.replaceAll(entry -> entry.dropSuffix(".0"));
            }

            ConfigValue<T> value = new ConfigValue<>(type, key, defaultValue, requiresRestart, shouldSyncToClients);
            values.put(key, value);

            ConfigEntryDisplay display = new ConfigEntryDisplay(title, List.copyOf(this.tooltip), displayPriority);
            ConfigManager.this.displays.put(key, display);

            if (!ConfigManager.this.typeToValues.containsKey(type)) {
                typeToValues.put(type, new HashMap<>());
            }
            getValues(type).put(key, value);
            return value;
        }

        public ConfigValueBuilder<T> displayPriority(int priority) {
            this.displayPriority = priority;
            return this;
        }

        public ConfigValueBuilder<T> requiresRestart() {
            requiresRestart = true;
            return this;
        }

        /**
         * Sync this config option from the server to connected clients.
         * Required when clientside logic is performed on the client using this config option,
         * or the value itself is displayed on the client somewhere, such as in a tooltip.
         */
        public ConfigValueBuilder<T> syncToClients() {
            shouldSyncToClients = true;
            return this;
        }

        public ConfigValueBuilder<T> titleAndDescription(SharedConfigLang.ConfigEntry entry) {
            return title(entry.title()).descriptionLine(entry.description());
        }

        public ConfigValueBuilder<T> descriptionLine(String line) {
            return descriptionLine(new LangEntry(key.toString(), line)
                    .withPrefix("artifacts.config")
                    .withSuffix("description")
                    .withSuffix(Integer.toString(customTooltipCount++))
            );
        }

        public ConfigValueBuilder<T> descriptionLine(LangEntry line) {
            tooltip.add(line);
            return this;
        }

        public ConfigValueBuilder<T> title(String title) {
            return title(new LangEntry(key.toString(), title)
                    .withPrefix("artifacts.config")
                    .withSuffix("title")
            );
        }

        public ConfigValueBuilder<T> title(LangEntry title) {
            this.title = title;
            return this;
        }

        private void setDefaultTitle(ConfigEntryKey key) {
            title(LangUtil.fromCamelCasedString(key.path().getLast()));
        }
    }

    private class ConfigWatcher implements Runnable {

        @Override
        public void run() {
            try {
                config.load();
                if (!spec.isCorrect(config)) {
                    Artifacts.LOGGER.warn("Configuration file {} is not correct. Correcting", configPath);
                    correctConfigAndSave();
                }
            } catch (ParsingException exception) {
                throw new RuntimeException("Failed to load config file " + configPath, exception);
            }
            Artifacts.LOGGER.info("Config file {} changed", configPath);
            onConfigChanged();
        }
    }
}
