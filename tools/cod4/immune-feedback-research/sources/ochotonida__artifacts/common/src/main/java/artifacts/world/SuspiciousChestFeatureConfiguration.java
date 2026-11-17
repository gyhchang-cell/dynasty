package artifacts.world;

import com.mojang.serialization.Codec;
import net.minecraft.world.level.levelgen.feature.configurations.FeatureConfiguration;

public record SuspiciousChestFeatureConfiguration(
    CampsiteChestConfiguration chestConfig
) implements FeatureConfiguration {

    public static final Codec<SuspiciousChestFeatureConfiguration> CODEC = CampsiteChestConfiguration.CODEC.fieldOf("chest").codec()
            .xmap(SuspiciousChestFeatureConfiguration::new, SuspiciousChestFeatureConfiguration::chestConfig);
}
