package com.dynasty.ritual;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;

/** Reserved, sealed 96 × 96 × 40 arena cells; no overworld terrain and no global gamerule changes. */
public final class ZhenyuanArena {
    public static final ResourceKey<Level> DIMENSION = ResourceKey.create(Registries.DIMENSION,
            new ResourceLocation("dynasty", "zhenyuan_arena"));
    public static final int FLOOR_Y = 64;
    private ZhenyuanArena() {}

    public static BlockPos center(int index) {
        if (index < 0 || index >= 1024 * 1024) throw new IllegalArgumentException("Arena allocation out of bounds");
        return new BlockPos((index % 1024) * 512, FLOOR_Y + 1, (index / 1024) * 512);
    }
    public static BlockPos arrival(int index) { return center(index).offset(0, 0, 28); }
    public static AABB interior(int index) {
        BlockPos c = center(index);
        return new AABB(c.getX() - 47, FLOOR_Y + 1, c.getZ() - 47, c.getX() + 49, FLOOR_Y + 41, c.getZ() + 49);
    }
    public static void forceChunks(ServerLevel level, int index, boolean forced) {
        BlockPos c = center(index);
        for (int x = (c.getX() - 50) >> 4; x <= (c.getX() + 51) >> 4; x++)
            for (int z = (c.getZ() - 50) >> 4; z <= (c.getZ() + 51) >> 4; z++) level.setChunkForced(x, z, forced);
    }
    public static void build(ServerLevel level, int index) {
        if (!level.dimension().equals(DIMENSION)) throw new IllegalArgumentException("Refusing arena writes outside reserved dimension");
        BlockPos c = center(index);
        forceChunks(level, index, true);
        // Only new, monotonically allocated cells may be built. Never use this as a repair/clear command.
        for (int x = -49; x <= 50; x++) for (int z = -49; z <= 50; z++) {
            set(level, c, x, -2, z, Blocks.BEDROCK.defaultBlockState());
            double r = Math.hypot(x, z);
            BlockState paving = (Math.abs(r - 31) < .8 || Math.abs(r - 17) < .8)
                    ? Blocks.CHISELED_POLISHED_BLACKSTONE.defaultBlockState()
                    : Math.abs(x) <= 1 || Math.abs(z) <= 1 ? Blocks.DEEPSLATE_TILES.defaultBlockState()
                    : Blocks.POLISHED_DEEPSLATE.defaultBlockState();
            if ((x % 12 == 0 && z % 12 == 0) || r < 3) paving = Blocks.SEA_LANTERN.defaultBlockState();
            set(level, c, x, -1, z, paving);
            set(level, c, x, 40, z, Blocks.DEEPSLATE_TILES.defaultBlockState());
            set(level, c, x, 41, z, Blocks.BEDROCK.defaultBlockState());
        }
        for (int y = 0; y < 40; y++) for (int n = -49; n <= 50; n++) {
            set(level, c, -49, y, n, Blocks.BEDROCK.defaultBlockState());
            set(level, c, 50, y, n, Blocks.BEDROCK.defaultBlockState());
            set(level, c, n, y, -49, Blocks.BEDROCK.defaultBlockState());
            set(level, c, n, y, 50, Blocks.BEDROCK.defaultBlockState());
            BlockState lining = (y % 10 == 0 || n % 12 == 0) ? Blocks.CHISELED_DEEPSLATE.defaultBlockState()
                    : Blocks.DEEPSLATE_BRICKS.defaultBlockState();
            if (y == 7 && n % 12 == 0) lining = Blocks.SEA_LANTERN.defaultBlockState();
            set(level, c, -48, y, n, lining); set(level, c, 49, y, n, lining);
            set(level, c, n, y, -48, lining); set(level, c, n, y, 49, lining);
        }
        // Twelve tall buttresses make the chamber read as a monumental buried sanctum.
        for (int[] p : new int[][]{{-38,-38},{0,-41},{38,-38},{41,-18},{41,18},{38,38},
                {0,41},{-38,38},{-41,18},{-41,-18},{-18,-41},{18,-41}}) {
            for (int y = 0; y < 31; y++) for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++) {
                BlockState s = y % 9 == 0 ? Blocks.WAXED_WEATHERED_CUT_COPPER.defaultBlockState()
                        : Blocks.POLISHED_BLACKSTONE_BRICKS.defaultBlockState();
                if (dx == 0 && dz == 0 && y == 30) s = Blocks.SEA_LANTERN.defaultBlockState();
                set(level, c, p[0]+dx, y, p[1]+dz, s);
            }
        }
        // Midpoints between the existing lantern grid; no material replacements or combat changes.
        for(int x=-36;x<=36;x+=12)for(int z=-36;z<=36;z+=12) {
            BlockPos light=c.offset(x+6,3,z+6);
            if(level.isEmptyBlock(light))level.setBlock(light,Blocks.LIGHT.defaultBlockState()
                    .setValue(net.minecraft.world.level.block.LightBlock.LEVEL,9),2);
        }
    }
    private static void set(ServerLevel level, BlockPos c, int x, int y, int z, BlockState state) {
        level.setBlock(c.offset(x, y, z), state, 2);
    }
}
