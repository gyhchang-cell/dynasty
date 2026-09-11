package com.dynasty.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.BlockHitResult;

import com.dynasty.Dynasty;

/**
 * 王朝传送门：右键传送到对应维度，再右键同一方块返回主世界。
 * Dynasty portal: right-click to travel to the target dimension, right-click again to return home.
 */
@SuppressWarnings({"null", "removal"})
public class DynastyPortalBlock extends Block {

    public static final ResourceKey<Level> CELESTIAL_DYNASTY = ResourceKey.create(
            Registries.DIMENSION, new ResourceLocation(Dynasty.MODID, "celestial_dynasty"));
    public static final ResourceKey<Level> UNDERWORLD = ResourceKey.create(
            Registries.DIMENSION, new ResourceLocation(Dynasty.MODID, "underworld"));

    private final ResourceKey<Level> target;
    private final ResourceKey<Level> home = Level.OVERWORLD;

    public DynastyPortalBlock(Properties props, ResourceKey<Level> target) {
        super(props);
        this.target = target;
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player,
                                 InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide || !(player instanceof ServerPlayer serverPlayer)) {
            return InteractionResult.sidedSuccess(level.isClientSide);
        }
        ServerLevel destination = serverPlayer.server.getLevel(level.dimension().equals(this.target) ? this.home : this.target);
        if (destination == null) {
            return InteractionResult.PASS;
        }
        double x = serverPlayer.getX();
        double z = serverPlayer.getZ();
        int y = destination.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, (int) x, (int) z) + 1;
        serverPlayer.teleportTo(destination, x, y, z, serverPlayer.getYRot(), serverPlayer.getXRot());
        return InteractionResult.SUCCESS;
    }
}
