package artifacts.world.placement;

import artifacts.registry.ModPlacementModifierTypes;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.util.ExtraCodecs;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.levelgen.placement.PlacementContext;
import net.minecraft.world.level.levelgen.placement.PlacementFilter;
import net.minecraft.world.level.levelgen.placement.PlacementModifierType;

public class CeilingHeightFilter extends PlacementFilter {

    public static final MapCodec<CeilingHeightFilter> CODEC = ExtraCodecs.NON_NEGATIVE_INT
            .fieldOf("max_height")
            .xmap(CeilingHeightFilter::new, f -> f.maxHeight);

    private final int maxHeight;

    private CeilingHeightFilter(int maxHeight) {
        this.maxHeight = maxHeight;
    }

    public static CeilingHeightFilter maxCeilingHeight(int maxHeight) {
        return new CeilingHeightFilter(maxHeight);
    }

    @Override
    protected boolean shouldPlace(PlacementContext context, RandomSource random, BlockPos pos) {
        if (maxHeight == 0) {
            return true;
        }
        for (int i = 1; i <= maxHeight; i ++) {
            if (!context.getBlockState(pos.above(i)).isAir()) {
                return true;
            }
        }

        return false;
    }

    @Override
    public PlacementModifierType<?> type() {
        return ModPlacementModifierTypes.CEILING_HEIGHT_FILTER.value();
    }
}
