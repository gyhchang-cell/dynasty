package artifacts.fabric.registry;

import artifacts.registry.ModFeatures;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.minecraft.world.level.levelgen.GenerationStep;

public class ModFeaturesFabric {

    public static void register() {
        BiomeModifications.addFeature(
                BiomeSelectors.foundInOverworld(),
                GenerationStep.Decoration.UNDERGROUND_STRUCTURES,
                ModFeatures.UNDERGROUND_CAMPSITE
        );
        BiomeModifications.addFeature(
                BiomeSelectors.foundInOverworld(),
                GenerationStep.Decoration.UNDERGROUND_STRUCTURES,
                ModFeatures.UNDERGROUND_MINIMALIST_CAMPSITE
        );
    }
}
