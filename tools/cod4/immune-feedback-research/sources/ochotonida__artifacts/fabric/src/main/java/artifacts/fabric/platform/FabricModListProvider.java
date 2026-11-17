package artifacts.fabric.platform;

import artifacts.platform.ModListProvider;
import net.fabricmc.loader.api.FabricLoader;

public class FabricModListProvider implements ModListProvider {

    @Override
    public boolean isModLoaded(String modId) {
        return FabricLoader.getInstance().isModLoaded(modId);
    }
}
