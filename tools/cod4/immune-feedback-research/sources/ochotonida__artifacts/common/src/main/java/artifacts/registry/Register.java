package artifacts.registry;

import artifacts.Artifacts;
import artifacts.platform.PlatformServices;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import org.jetbrains.annotations.NotNull;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.function.Supplier;

public abstract class Register<R> implements Iterable<R> {

    private final ResourceKey<Registry<R>> registry;
    private final List<RegistryHolder<R, ?>> entries = new ArrayList<>();

    public Register(ResourceKey<Registry<R>> registry) {
        this.registry = registry;
    }

    public static <R> Register<R> create(ResourceKey<Registry<R>> registry) {
        return PlatformServices.getPlatformHelper().createRegister(registry);
    }

    public ResourceKey<Registry<R>> getRegistry() {
        return registry;
    }

    public Collection<RegistryHolder<R, ?>> getEntries() {
        return entries;
    }

    public <T extends R> RegistryHolder<R, T> register(String name, Supplier<T> supplier) {
        RegistryHolder<R, T> holder = new RegistryHolder<>(Artifacts.key(registry, name), supplier);
        entries.add(holder);
        if (getRegistry().equals(Registries.ATTRIBUTE)
                || getRegistry().equals(Registries.MOB_EFFECT)
                || getRegistry().equals(Registries.DATA_COMPONENT_TYPE)
        ) {
            bind(holder);
        }
        return holder;
    }

    @NotNull
    @Override
    public Iterator<R> iterator() {
        return entries.stream().map(RegistryHolder::value).iterator();
    }

    public void register() {
        if (!getRegistry().equals(Registries.ATTRIBUTE)
                && !getRegistry().equals(Registries.MOB_EFFECT)
                && !getRegistry().equals(Registries.DATA_COMPONENT_TYPE)
        ) {
            for (RegistryHolder<R, ?> holder : getEntries()) {
                bind(holder);
            }
        }
    }

    protected abstract <T extends R> void bind(RegistryHolder<R, T> holder);
}
