package artifacts.world;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;

public class SuspiciousChestFeature extends AbstractCampsiteFeature<SuspiciousChestFeatureConfiguration> {

    public SuspiciousChestFeature() {
        super(SuspiciousChestFeatureConfiguration.CODEC);
    }

    @Override
    public boolean place(FeaturePlaceContext<SuspiciousChestFeatureConfiguration> context) {
        WorldGenLevel level = context.level();
        BlockPos origin = context.origin();
        RandomSource random = context.random();
        SuspiciousChestFeatureConfiguration config = context.config();

        Direction direction = Direction.Plane.HORIZONTAL.getRandomDirection(random);
        placeChest(level, origin, random, direction.getOpposite(), config.chestConfig());

        return true;
    }
}
