package artifacts.platform;

import artifacts.Artifacts;
import com.google.common.base.Suppliers;

import java.util.ServiceLoader;
import java.util.function.Supplier;

public class PlatformServices {

    // safe to call from mixin plugin
    private static final Supplier<ModListProvider> MOD_LIST = lazyLoad(ModListProvider.class);

    private static final Supplier<PlatformHelper> PLATFORM_HELPER = lazyLoad(PlatformHelper.class);

    public static ModListProvider getModList() {
        return MOD_LIST.get();
    }

    public static PlatformHelper getPlatformHelper() {
        return PLATFORM_HELPER.get();
    }

    private static <T> Supplier<T> lazyLoad(Class<T> c) {
        return Suppliers.memoize(() -> load(c));
    }

    private static <T> T load(Class<T> c) {
        final T loadedService = ServiceLoader.load(c)
                .findFirst()
                .orElseThrow(() -> new NullPointerException("Failed to load service for " + c.getName()));
        Artifacts.LOGGER.debug("Loaded {} for service {}", loadedService, c);
        return loadedService;
    }
}