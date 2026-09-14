package com.dynasty.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
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
import net.minecraft.world.level.block.Blocks;
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
    /** 九霄天界 / the nine-heaven realm */
    public static final ResourceKey<Level> JIUXIAO = ResourceKey.create(
            Registries.DIMENSION, new ResourceLocation(Dynasty.MODID, "jiuxiao"));
    /** 东海龙宫 / the Dragon Palace of the East Sea */
    public static final ResourceKey<Level> DRAGON_PALACE = ResourceKey.create(
            Registries.DIMENSION, new ResourceLocation(Dynasty.MODID, "dragon_palace"));

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
        BlockPos spot = findArrival(destination, (int) Math.floor(x), (int) Math.floor(z));
        serverPlayer.teleportTo(destination, spot.getX() + 0.5D, spot.getY(), spot.getZ() + 0.5D,
                serverPlayer.getYRot(), serverPlayer.getXRot());
        return InteractionResult.SUCCESS;
    }

    /**
     * 找一个「能站人」的落点：脚下实心、身体两格是空的、不泡在液体里。
     *
     * 以前直接用 {@code getHeight(MOTION_BLOCKING_NO_LEAVES)}：在有基岩顶棚的维度里会把人放到顶棚上，
     * 在岩浆海上方会把人丢进岩浆 —— 玩家反馈「出生点在底部基岩层」就是这个原因。
     * 现在从高处往下扫，找不到就搭一个 3×3 的小平台，保证一定落在陆地上。
     *
     * Finds a safe standing spot (solid floor, two air blocks, no fluid). Falls back to
     * building a small platform if the destination has nowhere to stand.
     */
    public static BlockPos findArrival(ServerLevel level, int x, int z) {
        int top = level.getMaxBuildHeight() - 3;
        for (int y = top; y > level.getMinBuildHeight() + 1; y--) {
            BlockPos candidate = new BlockPos(x, y, z);
            if (isStandable(level, candidate)) {
                return candidate;
            }
        }
        return buildLanding(level, x, z, top);
    }

    /** 判断能否站在这里 / whether a player can stand at this position */
    private static boolean isStandable(ServerLevel level, BlockPos pos) {
        if (!level.isLoaded(pos)) {
            level.getChunkAt(pos);                       // 先加载区块，否则读到的都是空
        }
        return isStandable(level, pos, level.getBlockState(pos));
    }

    private static boolean isStandable(ServerLevel level, BlockPos pos, BlockState at) {
        BlockPos below = pos.below();
        BlockState floor = level.getBlockState(below);
        if (floor.getFluidState().isEmpty()
                && !floor.isFaceSturdy(level, below, Direction.UP)) {
            return false;                                // 脚下不是实心地面
        }
        if (!floor.getFluidState().isEmpty()) {
            return false;                                // 站在液体（岩浆）上不算
        }
        if (!at.getFluidState().isEmpty() || !at.getCollisionShape(level, pos).isEmpty()) {
            return false;                                // 身体位置被占/有液体
        }
        BlockState above = level.getBlockState(pos.above());
        if (!above.getFluidState().isEmpty()
                || !above.getCollisionShape(level, pos.above()).isEmpty()) {
            return false;                                // 头顶两格要空
        }
        return !level.getBlockState(pos.above(2)).getFluidState().toString().contains("lava");
    }

    /** 实在没地方站：在最高处铺 3×3 石台，保证不会掉进岩浆 / emergency platform */
    private static BlockPos buildLanding(ServerLevel level, int x, int z, int top) {
        int y = Math.min(top, level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z) + 2);
        for (int dx = -1; dx <= 1; dx++) {
            for (int dz = -1; dz <= 1; dz++) {
                BlockPos floor = new BlockPos(x + dx, y - 1, z + dz);
                level.setBlockAndUpdate(floor, Blocks.COBBLESTONE.defaultBlockState());
                level.setBlockAndUpdate(new BlockPos(x + dx, y, z + dz), Blocks.AIR.defaultBlockState());
                level.setBlockAndUpdate(new BlockPos(x + dx, y + 1, z + dz), Blocks.AIR.defaultBlockState());
            }
        }
        return new BlockPos(x, y, z);
    }
}
