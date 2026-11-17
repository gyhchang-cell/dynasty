package artifacts.fabric.registry;

import artifacts.Artifacts;
import artifacts.fabric.component.SwimDataComponent;
import org.ladysnake.cca.api.v3.component.ComponentKey;
import org.ladysnake.cca.api.v3.component.ComponentRegistryV3;
import org.ladysnake.cca.api.v3.entity.EntityComponentFactoryRegistry;
import org.ladysnake.cca.api.v3.entity.EntityComponentInitializer;
import org.ladysnake.cca.api.v3.entity.RespawnCopyStrategy;

public class ModComponents implements EntityComponentInitializer {

    public static final ComponentKey<SwimDataComponent> SWIM_DATA = ComponentRegistryV3.INSTANCE.getOrCreate(Artifacts.id("swim_data"), SwimDataComponent.class);

    @Override
    public void registerEntityComponentFactories(EntityComponentFactoryRegistry registry) {
        registry.registerForPlayers(SWIM_DATA, _ -> new SwimDataComponent(), RespawnCopyStrategy.LOSSLESS_ONLY);
    }
}
