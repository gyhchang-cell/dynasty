package com.dynasty.worldgen;

import com.dynasty.DynastyBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;

/**
 * 中式建筑构件工具箱：把「火柴盒」换成有台基、立柱、门窗、翘檐、屋脊、院落、栏杆的房子。
 *
 * 之前每个建筑都是「一圈墙 + 平屋顶」，一眼就是火柴盒。这里把中式建筑拆成可复用构件，
 * 新建筑只要「台基 + 殿身 + 屋顶 + 装饰」四步就能拼出来，而且风格统一。
 *
 * A reusable Chinese-architecture kit: podium, column rows, hall body, hip/gable roofs
 * with upturned eaves, stairs, railings, courtyards and lanterns.
 */
@SuppressWarnings({"null", "removal"})
public final class DynastyBuildKit {

    private DynastyBuildKit() {
    }

    // ---------------------------------------------------------------- 常用方块
    public static BlockState marble() {
        return DynastyBlocks.MARBLE_BLOCK.get().defaultBlockState();
    }

    public static BlockState bricks() {
        return DynastyBlocks.PALACE_BRICKS.get().defaultBlockState();
    }

    public static BlockState pillar() {
        return DynastyBlocks.CRIMSON_PILLAR.get().defaultBlockState();
    }

    public static BlockState lantern() {
        return DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState();
    }

    public static BlockState jade() {
        return DynastyBlocks.JADE_BLOCK.get().defaultBlockState();
    }

    public static BlockState bronze() {
        return DynastyBlocks.BRONZE_BLOCK.get().defaultBlockState();
    }

    public static BlockState plaque() {
        return DynastyBlocks.PLAQUE.get().defaultBlockState();
    }

    public static BlockState air() {
        return Blocks.AIR.defaultBlockState();
    }

    public static BlockState quartzStair() {
        return Blocks.QUARTZ_STAIRS.defaultBlockState();
    }

    public static BlockState blackstoneStair() {
        return Blocks.POLISHED_BLACKSTONE_STAIRS.defaultBlockState();
    }

    public static BlockState prismarineStair() {
        return Blocks.PRISMARINE_STAIRS.defaultBlockState();
    }

    public static BlockState darkOakStair() {
        return Blocks.DARK_OAK_STAIRS.defaultBlockState();
    }

    public static BlockState darkPrismarine() {
        return Blocks.DARK_PRISMARINE.defaultBlockState();
    }

    public static BlockState prismarine() {
        return Blocks.PRISMARINE.defaultBlockState();
    }

    public static BlockState soulSoil() {
        return Blocks.SOUL_SOIL.defaultBlockState();
    }

    public static BlockState blackstone() {
        return Blocks.POLISHED_BLACKSTONE.defaultBlockState();
    }

    public static BlockState bone() {
        return Blocks.BONE_BLOCK.defaultBlockState();
    }

    public static BlockState seaLantern() {
        return Blocks.SEA_LANTERN.defaultBlockState();
    }

    // ---------------------------------------------------------------- 基础
    public static void plane(WorldGenLevel level, int x0, int z0, int x1, int z1, int y, BlockState state) {
        for (int x = x0; x <= x1; x++) {
            for (int z = z0; z <= z1; z++) {
                level.setBlock(new BlockPos(x, y, z), state, 2);
            }
        }
    }

    public static void clearBox(WorldGenLevel level, int x0, int y0, int z0, int x1, int y1, int z1) {
        for (int x = x0; x <= x1; x++) {
            for (int y = y0; y <= y1; y++) {
                for (int z = z0; z <= z1; z++) {
                    level.setBlock(new BlockPos(x, y, z), air(), 2);
                }
            }
        }
    }

    /** 空心墙（只有四面）/ hollow box walls */
    public static void walls(WorldGenLevel level, int x0, int y0, int z0, int x1, int y1, int z1,
                             BlockState state) {
        for (int y = y0; y <= y1; y++) {
            for (int x = x0; x <= x1; x++) {
                level.setBlock(new BlockPos(x, y, z0), state, 2);
                level.setBlock(new BlockPos(x, y, z1), state, 2);
            }
            for (int z = z0; z <= z1; z++) {
                level.setBlock(new BlockPos(x0, y, z), state, 2);
                level.setBlock(new BlockPos(x1, y, z), state, 2);
            }
        }
    }

    public static void column(WorldGenLevel level, int x, int y0, int y1, int z, BlockState state) {
        for (int y = y0; y <= y1; y++) {
            level.setBlock(new BlockPos(x, y, z), state, 2);
        }
    }

    /** 沿四边立柱（每 step 一根）/ column rows along the edges */
    public static void columnRing(WorldGenLevel level, int x0, int z0, int x1, int z1,
                                  int y0, int y1, int step, BlockState state) {
        int gap = Math.max(2, step);
        for (int x = x0; x <= x1; x += gap) {
            column(level, x, y0, y1, z0, state);
            column(level, x, y0, y1, z1, state);
        }
        for (int z = z0; z <= z1; z += gap) {
            column(level, x0, y0, y1, z, state);
            column(level, x1, y0, y1, z, state);
        }
        column(level, x1, y0, y1, z1, state);
    }

    // ---------------------------------------------------------------- 中式构件
    /** 台基：两层收分 + 四面踏步 / two-tier podium with steps on four sides */
    public static void podium(WorldGenLevel level, int cx, int y, int cz, int hx, int hz,
                              BlockState edge, BlockState top, BlockState stair) {
        plane(level, cx - hx - 1, cz - hz - 1, cx + hx + 1, cz + hz + 1, y - 1, edge);
        plane(level, cx - hx, cz - hz, cx + hx, cz + hz, y, top);
        clearBox(level, cx - hx, y + 1, cz - hz, cx + hx, y + 1, cz + hz);
        stairsUp(level, cx, y, cz - hz - 1, 3, 2, false, false, stair);
        stairsUp(level, cx, y, cz + hz + 1, 3, 2, false, true, stair);
        stairsUp(level, cx - hx - 1, y, cz, 3, 2, true, false, stair);
        stairsUp(level, cx + hx + 1, y, cz, 3, 2, true, true, stair);
    }

    /** 踏步：从 (x,y,z) 往指定方向逐级上升 / a run of steps */
    public static void stairsUp(WorldGenLevel level, int x, int y, int z, int width, int height,
                                boolean alongX, boolean toward, BlockState state) {
        for (int step = 0; step < height; step++) {
            int offset = step + 1;
            for (int w = -width / 2; w <= width / 2; w++) {
                int px = alongX ? x + (toward ? offset : -offset) : x + w;
                int pz = alongX ? z + w : z + (toward ? offset : -offset);
                level.setBlock(new BlockPos(px, y + step, pz), state, 2);
            }
        }
    }

    /**
     * 庑殿顶 / 攒尖顶：逐层收分的瓦顶 + 屋脊 + 四角翘檐 + 檐下宫灯。
     *
     * @param stair 四角翘檐用的楼梯块
     */
    public static void roof(WorldGenLevel level, int cx, int y, int cz, int hx, int hz,
                            BlockState tile, BlockState ridge, BlockState stair) {
        int layer = 0;
        while (layer < 12) {
            int x0 = cx - hx + layer;
            int x1 = cx + hx - layer;
            int z0 = cz - hz + layer;
            int z1 = cz + hz - layer;
            if (x0 > x1 || z0 > z1) {
                break;
            }
            int yy = y + layer;
            if (x0 >= x1 || z0 >= z1) {                        // 屋脊 / ridge
                for (int x = x0; x <= x1; x++) {
                    for (int z = z0; z <= z1; z++) {
                        level.setBlock(new BlockPos(x, yy, z), ridge, 2);
                    }
                }
                level.setBlock(new BlockPos(x0, yy + 1, z0), ridge, 2);
                break;
            }
            for (int x = x0; x <= x1; x++) {
                for (int z = z0; z <= z1; z++) {
                    if (x == x0 || x == x1 || z == z0 || z == z1) {
                        level.setBlock(new BlockPos(x, yy, z), tile, 2);
                    }
                }
            }
            for (int[] corner : new int[][]{{x0, z0}, {x0, z1}, {x1, z0}, {x1, z1}}) {
                level.setBlock(new BlockPos(corner[0], yy, corner[1]), stair, 2);
                level.setBlock(new BlockPos(corner[0], yy - 1, corner[1]), lantern(), 2);
            }
            if (layer == 0) {
                for (int x = x0 + 2; x <= x1 - 2; x += 3) {
                    level.setBlock(new BlockPos(x, yy - 1, z0 + 1), lantern(), 2);
                    level.setBlock(new BlockPos(x, yy - 1, z1 - 1), lantern(), 2);
                }
                for (int z = z0 + 2; z <= z1 - 2; z += 3) {
                    level.setBlock(new BlockPos(x0 + 1, yy - 1, z), lantern(), 2);
                    level.setBlock(new BlockPos(x1 - 1, yy - 1, z), lantern(), 2);
                }
            }
            layer++;
        }
    }

    /** 硬山顶：两坡瓦顶 + 屋脊 / gable roof */
    public static void gableRoof(WorldGenLevel level, int x0, int y0, int z0, int x1, int z1,
                                 BlockState tile, BlockState ridge, BlockState stair) {
        int half = Math.max(1, (z1 - z0) / 2);
        for (int layer = 0; layer <= half; layer++) {
            int yy = y0 + layer;
            int za = z0 + layer;
            int zb = z1 - layer;
            for (int x = x0 - 1; x <= x1 + 1; x++) {
                level.setBlock(new BlockPos(x, yy, za), layer == 0 ? stair : tile, 2);
                if (zb != za) {
                    level.setBlock(new BlockPos(x, yy, zb), layer == 0 ? stair : tile, 2);
                }
            }
            if (za >= zb - 1) {
                for (int x = x0 - 1; x <= x1 + 1; x++) {
                    level.setBlock(new BlockPos(x, yy + 1, (z0 + z1) / 2), ridge, 2);
                }
                break;
            }
        }
    }

    /** 殿身：墙 + 柱列 + 门窗洞 + 匾额 / hall body with walls, columns, door and windows */
    public static void hallBody(WorldGenLevel level, int x0, int y0, int z0, int x1, int z1, int height,
                                BlockState wall, BlockState col) {
        walls(level, x0, y0, z0, x1, y0 + height - 1, z1, wall);
        columnRing(level, x0, z0, x1, z1, y0, y0 + height - 1, 3, col);
        clearBox(level, x0 + 1, y0, z0 + 1, x1 - 1, y0 + height - 1, z1 - 1);
        int mx = x0 + (x1 - x0) / 2;
        level.setBlock(new BlockPos(mx, y0, z0), air(), 2);
        level.setBlock(new BlockPos(mx, y0 + 1, z0), air(), 2);
        level.setBlock(new BlockPos(mx + 1, y0, z0), air(), 2);
        level.setBlock(new BlockPos(mx + 1, y0 + 1, z0), air(), 2);
        level.setBlock(new BlockPos(mx, y0 + height, z0), plaque(), 2);
        for (int x = x0 + 2; x <= x1 - 2; x += 3) {
            level.setBlock(new BlockPos(x, y0 + 1, z1), air(), 2);
        }
        for (int z = z0 + 2; z <= z1 - 2; z += 3) {
            level.setBlock(new BlockPos(x0, y0 + 1, z), air(), 2);
            level.setBlock(new BlockPos(x1, y0 + 1, z), air(), 2);
        }
    }

    /** 栏杆 / railing around a platform */
    public static void railing(WorldGenLevel level, int x0, int z0, int x1, int z1, int y,
                               BlockState post) {
        for (int x = x0; x <= x1; x++) {
            level.setBlock(new BlockPos(x, y, z0), post, 2);
            level.setBlock(new BlockPos(x, y, z1), post, 2);
        }
        for (int z = z0; z <= z1; z++) {
            level.setBlock(new BlockPos(x0, y, z), post, 2);
            level.setBlock(new BlockPos(x1, y, z), post, 2);
        }
    }

    /** 院墙 + 大门（3 宽门洞 + 门柱挂灯 + 台阶）/ courtyard wall with a gate */
    public static void courtyard(WorldGenLevel level, int cx, int y, int cz, int halfX, int halfZ,
                                 BlockState wall, BlockState top, BlockState post, BlockState stair) {
        int x0 = cx - halfX;
        int x1 = cx + halfX;
        int z0 = cz - halfZ;
        int z1 = cz + halfZ;
        for (int h = 0; h < 3; h++) {
            for (int x = x0; x <= x1; x++) {
                boolean door = h < 2 && Math.abs(x - cx) <= 1;
                level.setBlock(new BlockPos(x, y + h, z0), door ? air() : (h == 2 ? top : wall), 2);
                level.setBlock(new BlockPos(x, y + h, z1), h == 2 ? top : wall, 2);
            }
            for (int z = z0; z <= z1; z++) {
                level.setBlock(new BlockPos(x0, y + h, z), h == 2 ? top : wall, 2);
                level.setBlock(new BlockPos(x1, y + h, z), h == 2 ? top : wall, 2);
            }
        }
        for (int side : new int[]{-2, 2}) {
            column(level, cx + side, y, y + 2, z0, post);
            level.setBlock(new BlockPos(cx + side, y + 3, z0), lantern(), 2);
        }
        stairsUp(level, cx, y - 1, z0 - 1, 3, 2, false, false, stair);
    }

    public static void floor(WorldGenLevel level, int x0, int y, int z0, int x1, int z1, BlockState state) {
        plane(level, x0, z0, x1, z1, y, state);
    }

    public static void chest(WorldGenLevel level, RandomSource rand, int x, int y, int z, String loot) {
        BlockPos pos = new BlockPos(x, y, z);
        level.setBlock(pos, Blocks.CHEST.defaultBlockState(), 2);
        if (level.getBlockEntity(pos) instanceof ChestBlockEntity be) {
            be.setLootTable(new ResourceLocation("dynasty", "chests/" + loot), rand.nextLong());
        }
    }

    public static int ground(WorldGenLevel level, int x, int z) {
        return level.getHeight(Heightmap.Types.WORLD_SURFACE_WG, x, z);
    }

    /** 在建筑里放几个守卫（建筑不能是空壳）/ spawn guards inside a building */
    public static void guard(WorldGenLevel level, RandomSource rand, int x, int y, int z,
                             net.minecraft.world.entity.EntityType<? extends net.minecraft.world.entity.Mob> type,
                             int count) {
        for (int index = 0; index < count; index++) {
            net.minecraft.world.entity.Mob mob = type.create(level.getLevel());
            if (mob == null) {
                continue;
            }
            mob.moveTo(x + rand.nextInt(7) - 3, y, z + rand.nextInt(7) - 3,
                    rand.nextFloat() * 360.0F, 0.0F);
            mob.setPersistenceRequired();
            level.addFreshEntity(mob);
        }
    }

    /** 一堆材料：让建筑里有东西可拿 / a small pile of materials */
    public static void materials(WorldGenLevel level, RandomSource rand, int x, int y, int z,
                                 BlockState state, int size) {
        for (int index = 0; index < size; index++) {
            int dx = rand.nextInt(3) - 1;
            int dz = rand.nextInt(3) - 1;
            level.setBlock(new BlockPos(x + dx, y + rand.nextInt(2), z + dz), state, 2);
        }
    }
}
