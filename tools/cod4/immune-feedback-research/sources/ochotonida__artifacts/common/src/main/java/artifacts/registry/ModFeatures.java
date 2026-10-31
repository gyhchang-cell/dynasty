package artifacts.registry;

import artifacts.Artifacts;
import artifacts.world.CampsiteFeature;
import artifacts.world.CampsiteFeatureConfiguration;
import artifacts.world.SuspiciousChestFeature;
import artifacts.world.SuspiciousChestFeatureConfiguration;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.placement.PlacedFeature;

public class ModFeatures {

    public static final Register<Feature<?>> FEATURES = Register.create(Registries.FEATURE);

    public static final RegistryHolder<Feature<?>, Feature<CampsiteFeatureConfiguration>> CAMPSITE = FEATURES.register("campsite", CampsiteFeature::new);
    public static final RegistryHolder<Feature<?>, Feature<SuspiciousChestFeatureConfiguration>> SUSPICIOUS_CHEST = FEATURES.register("suspicious_chest", SuspiciousChestFeature::new);

    public static final ResourceKey<PlacedFeature> UNDERGROUND_CAMPSITE = Artifacts.key(Registries.PLACED_FEATURE, "underground_campsite");
    public static final ResourceKey<PlacedFeature> UNDERGROUND_MINIMALIST_CAMPSITE = Artifacts.key(Registries.PLACED_FEATURE, "underground_minimalist_campsite");
}
