package artifacts.world.placement;

import artifacts.registry.ModPlacementModifierTypes;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.levelgen.placement.PlacementContext;
import net.minecraft.world.level.levelgen.placement.PlacementFilter;
import net.minecraft.world.level.levelgen.placement.PlacementModifierType;

public class SurfaceFlatnessFilter extends PlacementFilter {

    public static final MapCodec<SurfaceFlatnessFilter> CODEC = MapCodec.unit(new SurfaceFlatnessFilter());

    public static SurfaceFlatnessFilter checkSurfaceFlatness() {
        return new SurfaceFlatnessFilter();
    }

    @Override
    protected boolean shouldPlace(PlacementContext context, RandomSource randomSource, BlockPos origin) {
        BlockGetter level = context.getLevel();
        return BlockPos.betweenClosedStream(origin.offset(-2, 0, -2), origin.offset(2, 0, 2))
                .filter(pos -> level.getBlockState(pos.below()).isFaceSturdy(level, pos.below(), Direction.UP))
                .filter(pos -> level.getBlockState(pos).isAir())
                .count() >= 6;
    }

    @Override
    public PlacementModifierType<?> type() {
        return ModPlacementModifierTypes.SURFACE_FLATNESS_FILTER.value();
    }
}
