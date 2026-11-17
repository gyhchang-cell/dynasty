package artifacts.world.placement;

import artifacts.Artifacts;
import artifacts.registry.ModPlacementModifierTypes;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.levelgen.placement.PlacementContext;
import net.minecraft.world.level.levelgen.placement.PlacementModifier;
import net.minecraft.world.level.levelgen.placement.PlacementModifierType;

import java.util.stream.Stream;

public class CampsiteHeightRangePlacement extends PlacementModifier {

    private static final CampsiteHeightRangePlacement INSTANCE = new CampsiteHeightRangePlacement();
    public static final MapCodec<CampsiteHeightRangePlacement> CODEC = MapCodec.unit(() -> INSTANCE);

    private CampsiteHeightRangePlacement() {

    }

    public static CampsiteHeightRangePlacement campsiteHeightRange() {
        return INSTANCE;
    }

    @Override
    public Stream<BlockPos> getPositions(PlacementContext context, RandomSource randomSource, BlockPos pos) {
        int minY = Artifacts.CONFIG.general.campsite.minY.get();
        int maxY = Artifacts.CONFIG.general.campsite.maxY.get();
        if (minY > maxY) {
            return Stream.of();
        }
        return Stream.of(pos.atY(Mth.randomBetweenInclusive(randomSource, minY, maxY)));
    }

    @Override
    public PlacementModifierType<?> type() {
        return ModPlacementModifierTypes.CAMPSITE_HEIGHT_RANGE.value();
    }
}
