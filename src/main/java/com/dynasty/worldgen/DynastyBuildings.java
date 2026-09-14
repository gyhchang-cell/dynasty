package com.dynasty.worldgen;

import com.dynasty.DynastyBlocks;
import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/**
 * 王朝新建筑（世界生成）：长城、宝塔、天坛、驿站、牌坊。
 *
 * 全部使用本模组方块（白玉 / 宫砖 / 朱红柱 / 宫灯 / 玉石），
 * 通过 Forge biome modifier 加进「天朝」与「地府」的群系。
 *
 * New Dynasty buildings: Great Wall, pagoda, altar of heaven, post station, memorial arch.
 */
@SuppressWarnings({"null", "removal"})
public final class DynastyBuildings {

    private DynastyBuildings() {
    }

    // ---------------------------------------------------------------- 方块
    static BlockState marble() {
        return DynastyBlocks.MARBLE_BLOCK.get().defaultBlockState();
    }

    static BlockState bricks() {
        return DynastyBlocks.PALACE_BRICKS.get().defaultBlockState();
    }

    static BlockState pillar() {
        return DynastyBlocks.CRIMSON_PILLAR.get().defaultBlockState();
    }

    static BlockState lantern() {
        return DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState();
    }

    static BlockState jade() {
        return DynastyBlocks.JADE_BLOCK.get().defaultBlockState();
    }

    static BlockState bronze() {
        return DynastyBlocks.BRONZE_BLOCK.get().defaultBlockState();
    }

    static BlockState air() {
        return Blocks.AIR.defaultBlockState();
    }

    // ---------------------------------------------------------------- 工具
    static void plane(WorldGenLevel level, int x0, int z0, int x1, int z1, int y, BlockState state) {
        for (int x = x0; x <= x1; x++) {
            for (int z = z0; z <= z1; z++) {
                level.setBlock(new BlockPos(x, y, z), state, 2);
            }
        }
    }

    static void clear(WorldGenLevel level, int x0, int y0, int z0, int x1, int y1, int z1) {
        for (int x = x0; x <= x1; x++) {
            for (int y = y0; y <= y1; y++) {
                for (int z = z0; z <= z1; z++) {
                    level.setBlock(new BlockPos(x, y, z), air(), 2);
                }
            }
        }
    }

    static void walls(WorldGenLevel level, int x0, int y0, int z0, int x1, int y1, int z1, BlockState state) {
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

    static void chest(WorldGenLevel level, RandomSource rand, int x, int y, int z, ResourceLocation loot) {
        BlockPos pos = new BlockPos(x, y, z);
        level.setBlock(pos, Blocks.CHEST.defaultBlockState(), 2);
        if (level.getBlockEntity(pos) instanceof ChestBlockEntity be) {
            be.setLootTable(loot, rand.nextLong());
        }
    }

    static ResourceLocation loot(String name) {
        return new ResourceLocation("dynasty", "chests/" + name);
    }

    static int ground(WorldGenLevel level, int x, int z) {
        return level.getHeight(Heightmap.Types.WORLD_SURFACE_WG, x, z);
    }

    /** 长城 / Great Wall：带垛口与城楼的长墙 */
    public static class GreatWallFeature extends Feature<NoneFeatureConfiguration> {
        public GreatWallFeature(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource rand = ctx.random();
            BlockPos origin = ctx.origin();
            boolean alongX = rand.nextBoolean();
            if (ground(level, origin.getX(), origin.getZ()) <= level.getSeaLevel() + 1) {
                return false;
            }
            int length = 40 + rand.nextInt(24);
            for (int i = 0; i < length; i++) {
                int bx = alongX ? origin.getX() + i : origin.getX();
                int bz = alongX ? origin.getZ() : origin.getZ() + i;
                int y = ground(level, bx, bz);
                for (int wy = 0; wy < 6; wy++) {
                    for (int w = -1; w <= 1; w++) {
                        int px = alongX ? bx : bx + w;
                        int pz = alongX ? bz + w : bz;
                        level.setBlock(new BlockPos(px, y + wy, pz), wy == 5 ? bricks() : marble(), 2);
                    }
                }
                level.setBlock(new BlockPos(bx, y + 6, bz), bricks(), 2);
                if (i % 6 == 0) {
                    level.setBlock(new BlockPos(alongX ? bx : bx + 1, y + 7, alongX ? bz + 1 : bz),
                            lantern(), 2);
                }
                if (i == length / 2) {
                    for (int wy = 6; wy < 12; wy++) {
                        for (int dx = -2; dx <= 2; dx++) {
                            for (int dz = -2; dz <= 2; dz++) {
                                if (Math.abs(dx) == 2 || Math.abs(dz) == 2) {
                                    level.setBlock(new BlockPos(bx + dx, y + wy, bz + dz),
                                            wy >= 9 ? bricks() : pillar(), 2);
                                }
                            }
                        }
                    }
                    plane(level, bx - 2, bz - 2, bx + 2, bz + 2, y + 12, bricks());
                    level.setBlock(new BlockPos(bx, y + 13, bz), lantern(), 2);
                    chest(level, rand, bx + 1, y + 7, bz + 1, loot("palace_ruin"));
                }
            }
            return true;
        }
    }

    /** 宝塔 / Pagoda：七层收分塔 */
    public static class PagodaFeature extends Feature<NoneFeatureConfiguration> {
        public PagodaFeature(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource rand = ctx.random();
            BlockPos origin = ctx.origin();
            int y0 = ground(level, origin.getX(), origin.getZ());
            if (y0 <= level.getSeaLevel() + 1) {
                return false;
            }
            // 台基 / platform
            plane(level, origin.getX() - 7, origin.getZ() - 7, origin.getX() + 7, origin.getZ() + 7,
                    y0 - 1, marble());
            plane(level, origin.getX() - 7, origin.getZ() - 7, origin.getX() + 7, origin.getZ() + 7,
                    y0, bricks());

            int radius = 5;
            for (int tier = 0; tier < 7; tier++) {
                int base = y0 + 1 + tier * 4;
                // 塔身 / body
                walls(level, origin.getX() - radius, base, origin.getZ() - radius,
                        origin.getX() + radius, base + 2, origin.getZ() + radius, bricks());
                clear(level, origin.getX() - radius + 1, base, origin.getZ() - radius + 1,
                        origin.getX() + radius - 1, base + 2, origin.getZ() + radius - 1);
                // 檐 / eaves
                plane(level, origin.getX() - radius - 1, origin.getZ() - radius - 1,
                        origin.getX() + radius + 1, origin.getZ() + radius + 1, base + 3, marble());
                for (int dx = -radius - 1; dx <= radius + 1; dx += 2 * (radius + 1)) {
                    for (int dz = -radius - 1; dz <= radius + 1; dz += 2 * (radius + 1)) {
                        level.setBlock(new BlockPos(origin.getX() + dx, base + 4, origin.getZ() + dz),
                                lantern(), 2);
                    }
                }
                // 塔心柱 / central pillar
                for (int h = 0; h <= 3; h++) {
                    level.setBlock(new BlockPos(origin.getX(), base + h, origin.getZ()), pillar(), 2);
                }
                if (tier % 2 == 0) {
                    chest(level, rand, origin.getX() + 1, base + 1, origin.getZ() + 1, loot("palace_ruin"));
                }
                radius = Math.max(2, radius - 1);
            }
            // 塔刹 / finial
            int top = y0 + 1 + 7 * 4;
            level.setBlock(new BlockPos(origin.getX(), top, origin.getZ()), jade(), 2);
            level.setBlock(new BlockPos(origin.getX(), top + 1, origin.getZ()), bronze(), 2);
            level.setBlock(new BlockPos(origin.getX(), top + 2, origin.getZ()), lantern(), 2);
            return true;
        }
    }

    /** 天坛 / Altar of Heaven：三层圆坛 + 四柱 + 祭台 */
    public static class AltarFeature extends Feature<NoneFeatureConfiguration> {
        public AltarFeature(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        private void disc(WorldGenLevel level, int cx, int cz, int y, int r, BlockState state) {
            for (int x = -r; x <= r; x++) {
                for (int z = -r; z <= r; z++) {
                    if (x * x + z * z <= r * r) {
                        level.setBlock(new BlockPos(cx + x, y, cz + z), state, 2);
                    }
                }
            }
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource rand = ctx.random();
            BlockPos origin = ctx.origin();
            int y0 = ground(level, origin.getX(), origin.getZ());
            if (y0 <= level.getSeaLevel() + 1) {
                return false;
            }
            disc(level, origin.getX(), origin.getZ(), y0 - 1, 11, marble());
            disc(level, origin.getX(), origin.getZ(), y0, 9, bricks());
            disc(level, origin.getX(), origin.getZ(), y0 + 1, 7, marble());
            disc(level, origin.getX(), origin.getZ(), y0 + 2, 5, bricks());
            for (int[] c : new int[][]{{-4, -4}, {-4, 4}, {4, -4}, {4, 4}}) {
                for (int h = 0; h < 5; h++) {
                    level.setBlock(new BlockPos(origin.getX() + c[0], y0 + 3 + h, origin.getZ() + c[1]),
                            pillar(), 2);
                }
                level.setBlock(new BlockPos(origin.getX() + c[0], y0 + 8, origin.getZ() + c[1]),
                        lantern(), 2);
            }
            level.setBlock(new BlockPos(origin.getX(), y0 + 3, origin.getZ()),
                    DynastyBlocks.ALTAR.get().defaultBlockState(), 2);
            level.setBlock(new BlockPos(origin.getX(), y0 + 3, origin.getZ() + 1), jade(), 2);
            chest(level, rand, origin.getX() + 1, y0 + 3, origin.getZ() - 1, loot("palace_ruin"));
            return true;
        }
    }

    /** 驿站 / Post station：三间小屋 + 围墙 + 水井 + 宝箱 */
    public static class PostStationFeature extends Feature<NoneFeatureConfiguration> {
        public PostStationFeature(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        private void house(WorldGenLevel level, int x, int z, int y, int w, int d) {
            walls(level, x, y, z, x + w, y + 3, z + d, bricks());
            clear(level, x + 1, y, z + 1, x + w - 1, y + 3, z + d - 1);
            plane(level, x - 1, z - 1, x + w + 1, z + d + 1, y + 4, marble());
            for (int dx = -1; dx <= w + 1; dx += w + 2) {
                for (int dz = -1; dz <= d + 1; dz += d + 2) {
                    level.setBlock(new BlockPos(x + dx, y + 5, z + dz), lantern(), 2);
                }
            }
            level.setBlock(new BlockPos(x + w / 2, y + 1, z + d / 2), pillar(), 2);
            level.setBlock(new BlockPos(x + w / 2, y + 2, z + d / 2), lantern(), 2);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource rand = ctx.random();
            BlockPos origin = ctx.origin();
            int y = ground(level, origin.getX(), origin.getZ());
            if (y <= level.getSeaLevel() + 1) {
                return false;
            }
            for (int x = -9; x <= 9; x++) {
                for (int z = -9; z <= 9; z++) {
                    boolean edge = Math.abs(x) == 9 || Math.abs(z) == 9;
                    level.setBlock(new BlockPos(origin.getX() + x, y - 1, origin.getZ() + z),
                            edge ? bricks() : marble(), 2);
                }
            }
            house(level, origin.getX() - 7, origin.getZ() - 7, y, 5, 5);
            house(level, origin.getX() + 2, origin.getZ() - 7, y, 5, 4);
            house(level, origin.getX() - 7, origin.getZ() + 2, y, 4, 5);
            level.setBlock(new BlockPos(origin.getX() + 3, y, origin.getZ() + 3),
                    Blocks.WATER.defaultBlockState(), 2);
            for (int[] c : new int[][]{{2, 2}, {2, 4}, {4, 2}, {4, 4}}) {
                level.setBlock(new BlockPos(origin.getX() + c[0], y + 1, origin.getZ() + c[1]),
                        bronze(), 2);
                level.setBlock(new BlockPos(origin.getX() + c[0], y + 2, origin.getZ() + c[1]),
                        bricks(), 2);
            }
            chest(level, rand, origin.getX() + 3, y + 1, origin.getZ() + 2, loot("palace_ruin"));
            return true;
        }
    }

    /** 牌坊 / Memorial arch（小型建筑，出现频率高） */
    public static class PaifangFeature extends Feature<NoneFeatureConfiguration> {
        public PaifangFeature(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            BlockPos origin = ctx.origin();
            int y = ground(level, origin.getX(), origin.getZ());
            if (y <= level.getSeaLevel() + 1) {
                return false;
            }
            for (int side : new int[]{-3, 3}) {
                for (int h = 0; h < 6; h++) {
                    level.setBlock(new BlockPos(origin.getX() + side, y + h, origin.getZ()), pillar(), 2);
                }
            }
            plane(level, origin.getX() - 4, origin.getZ(), origin.getX() + 4, origin.getZ(), y + 6, bricks());
            plane(level, origin.getX() - 5, origin.getZ(), origin.getX() + 5, origin.getZ(), y + 7, marble());
            for (int dx = -5; dx <= 5; dx += 10) {
                level.setBlock(new BlockPos(origin.getX() + dx, y + 8, origin.getZ()), lantern(), 2);
            }
            level.setBlock(new BlockPos(origin.getX(), y + 5, origin.getZ()),
                    DynastyBlocks.PLAQUE.get().defaultBlockState(), 2);
            level.setBlock(new BlockPos(origin.getX() - 1, y + 5, origin.getZ()), jade(), 2);
            level.setBlock(new BlockPos(origin.getX() + 1, y + 5, origin.getZ()), jade(), 2);
            return true;
        }
    }
}
