package artifacts.config;

import java.util.Map;

public class ModConfig {

    public final ClientConfig client = new ClientConfig();
    public final GeneralConfig general = new GeneralConfig();
    public final ItemConfigs items = new ItemConfigs();

    public final Map<String, ConfigManager> configs = Map.of(
            "general", general,
            "client", client,
            "items", items
    );

    public void setup() {
        configs.values().forEach(ConfigManager::setup);
    }
}
