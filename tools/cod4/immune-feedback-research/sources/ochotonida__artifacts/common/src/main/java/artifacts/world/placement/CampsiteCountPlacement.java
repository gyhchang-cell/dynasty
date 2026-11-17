package artifacts.world.placement;

import artifacts.Artifacts;
import artifacts.registry.ModPlacementModifierTypes;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.levelgen.placement.PlacementModifierType;
import net.minecraft.world.level.levelgen.placement.RepeatingPlacement;

public class CampsiteCountPlacement extends RepeatingPlacement {

    private static final CampsiteCountPlacement INSTANCE = new CampsiteCountPlacement();
    public static final MapCodec<CampsiteCountPlacement> CODEC = MapCodec.unit(() -> INSTANCE);

    private CampsiteCountPlacement() {

    }

    public static CampsiteCountPlacement campsiteCount() {
        return INSTANCE;
    }

    @Override
    protected int count(RandomSource p_226333_, BlockPos p_226334_) {
        return Artifacts.CONFIG.general.campsite.count.get();
    }

    @Override
    public PlacementModifierType<?> type() {
        return ModPlacementModifierTypes.CAMPSITE_COUNT.value();
    }
}
