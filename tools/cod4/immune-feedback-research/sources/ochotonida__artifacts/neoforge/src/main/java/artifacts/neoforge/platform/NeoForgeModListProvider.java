package artifacts.neoforge.platform;

import artifacts.platform.ModListProvider;
import net.neoforged.fml.ModList;
import net.neoforged.fml.loading.FMLLoader;

public class NeoForgeModListProvider implements ModListProvider {

    @Override
    public boolean isModLoaded(String modId) {
        var modlist = ModList.get();
        if (modlist == null) {
            return FMLLoader.getCurrent().getLoadingModList().getModFileById(modId) != null;
        }

        return ModList.get().isLoaded(modId);
    }
}
