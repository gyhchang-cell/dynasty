package com.dynasty.worldgen;

import com.dynasty.DynastyBlocks;
import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/**
 * 王朝第二批建筑：法阵、神庙、兵营、烽火台。
 *
 * 其中「法阵」与「神庙」里会生成 §6法阵·祭坛（ritual_altar）§r：
 * 四周再补上 4 块玉石块，就能用 Boss 信物在这里反复召唤 Boss。
 *
 * Second batch of Dynasty buildings: ritual circle, temple, barracks and watchtower.
 */
@SuppressWarnings({"null", "removal"})
public final class DynastyBuildings2 {

    private DynastyBuildings2() {
    }

    private static BlockState altar() {
        return DynastyBlocks.RITUAL_ALTAR.get().defaultBlockState();
    }

    private static BlockState jade() {
        return DynastyBlocks.JADE_BLOCK.get().defaultBlockState();
    }

    private static BlockState marble() {
        return DynastyBlocks.MARBLE_BLOCK.get().defaultBlockState();
    }

    private static BlockState bricks() {
        return DynastyBlocks.PALACE_BRICKS.get().defaultBlockState();
    }

    private static BlockState pillar() {
        return DynastyBlocks.CRIMSON_PILLAR.get().defaultBlockState();
    }

    private static BlockState lantern() {
        return DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState();
    }

    private static BlockState bronze() {
        return DynastyBlocks.BRONZE_BLOCK.get().defaultBlockState();
    }

    /** 天罡法阵 / ritual circle：石阵 + 中央法阵祭坛 + 四块玉石（可直接召唤 Boss） */
    public static class RitualCircleFeature extends Feature<NoneFeatureConfiguration> {
        public RitualCircleFeature(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource rand = ctx.random();
            BlockPos origin = ctx.origin();
            int y = DynastyBuildings.ground(level, origin.getX(), origin.getZ());
            if (y <= level.getSeaLevel() + 1) {
                return false;
            }
            // 圆形石阵 / circular platform
            for (int x = -8; x <= 8; x++) {
                for (int z = -8; z <= 8; z++) {
                    int d = x * x + z * z;
                    if (d > 64) {
                        continue;
                    }
                    level.setBlock(new BlockPos(origin.getX() + x, y - 1, origin.getZ() + z), marble(), 2);
                    if (d <= 25 && d >= 16) {
                        level.setBlock(new BlockPos(origin.getX() + x, y, origin.getZ() + z), jade(), 2);
                    } else if (d <= 9) {
                        level.setBlock(new BlockPos(origin.getX() + x, y, origin.getZ() + z), bricks(), 2);
                    }
                }
            }
            // 中央法阵祭坛 + 四块玉石 / central altar with jade ring
            level.setBlock(new BlockPos(origin.getX(), y + 1, origin.getZ()), altar(), 2);
            for (int[] c : new int[][]{{-1, 0}, {1, 0}, {0, -1}, {0, 1}}) {
                level.setBlock(new BlockPos(origin.getX() + c[0], y + 1, origin.getZ() + c[1]), jade(), 2);
            }
            // 四根立柱 / four pillars
            for (int[] c : new int[][]{{-6, -6}, {-6, 6}, {6, -6}, {6, 6}}) {
                for (int h = 0; h < 4; h++) {
                    level.setBlock(new BlockPos(origin.getX() + c[0], y + h, origin.getZ() + c[1]), pillar(), 2);
                }
                level.setBlock(new BlockPos(origin.getX() + c[0], y + 4, origin.getZ() + c[1]), lantern(), 2);
            }
            DynastyBuildings.chest(level, rand, origin.getX() + 2, y + 1, origin.getZ() + 2, DynastyBuildings.loot("ritual_circle"));
            return true;
        }
    }

    /** 山门神庙 / temple：围墙 + 神像台 + 法阵祭坛 + 宝箱，是召唤 Boss 的主场 */
    public static class TempleFeature extends Feature<NoneFeatureConfiguration> {
        public TempleFeature(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource rand = ctx.random();
            BlockPos origin = ctx.origin();
            int y = DynastyBuildings.ground(level, origin.getX(), origin.getZ());
            if (y <= level.getSeaLevel() + 1) {
                return false;
            }
            // 台基 / platform
            DynastyBuildings.plane(level, origin.getX() - 14, origin.getZ() - 14,
                    origin.getX() + 14, origin.getZ() + 14, y - 1, marble());
            // 围墙 / walls
            DynastyBuildings.walls(level, origin.getX() - 14, y, origin.getZ() - 14,
                    origin.getX() + 14, y + 5, origin.getZ() + 14, bricks());
            DynastyBuildings.clear(level, origin.getX() - 13, y, origin.getZ() - 13,
                    origin.getX() + 13, y + 5, origin.getZ() + 13);
            // 屋脊 / roof
            DynastyBuildings.plane(level, origin.getX() - 15, origin.getZ() - 15,
                    origin.getX() + 15, origin.getZ() + 15, y + 6, marble());
            for (int[] c : new int[][]{{-14, -14}, {-14, 14}, {14, -14}, {14, 14}}) {
                level.setBlock(new BlockPos(origin.getX() + c[0], y + 7, origin.getZ() + c[1]), lantern(), 2);
            }
            // 大门 / gateway on the south wall
            DynastyBuildings.clear(level, origin.getX() - 2, y, origin.getZ() + 14,
                    origin.getX() + 2, y + 3, origin.getZ() + 14);

            // 神像台 + 法阵祭坛 / idol platform and ritual altar
            DynastyBuildings.plane(level, origin.getX() - 4, origin.getZ() - 4,
                    origin.getX() + 4, origin.getZ() + 4, y, bricks());
            level.setBlock(new BlockPos(origin.getX(), y + 1, origin.getZ()), altar(), 2);
            for (int[] c : new int[][]{{-1, 0}, {1, 0}, {0, -1}, {0, 1}}) {
                level.setBlock(new BlockPos(origin.getX() + c[0], y + 1, origin.getZ() + c[1]), jade(), 2);
            }
            for (int[] c : new int[][]{{-3, -3}, {-3, 3}, {3, -3}, {3, 3}}) {
                for (int h = 1; h <= 6; h++) {
                    level.setBlock(new BlockPos(origin.getX() + c[0], y + h, origin.getZ() + c[1]), pillar(), 2);
                }
                level.setBlock(new BlockPos(origin.getX() + c[0], y + 7, origin.getZ() + c[1]), lantern(), 2);
            }
            // 两侧神台与宝箱 / side shrines
            for (int side : new int[]{-9, 9}) {
                DynastyBuildings.plane(level, origin.getX() + side - 2, origin.getZ() - 2,
                        origin.getX() + side + 2, origin.getZ() + 2, y, bricks());
                level.setBlock(new BlockPos(origin.getX() + side, y + 1, origin.getZ()), bronze(), 2);
                level.setBlock(new BlockPos(origin.getX() + side, y + 2, origin.getZ()), jade(), 2);
                DynastyBuildings.chest(level, rand, origin.getX() + side, y + 1, origin.getZ() + 2,
                        DynastyBuildings.loot("temple"));
            }
            DynastyBuildings.chest(level, rand, origin.getX(), y + 1, origin.getZ() - 3,
                    DynastyBuildings.loot("imperial_mausoleum"));
            return true;
        }
    }

    /** 兵营 / barracks：木栅营地 + 三座营帐 + 兵器架 + 宝箱 */
    public static class BarracksFeature extends Feature<NoneFeatureConfiguration> {
        public BarracksFeature(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        private void tent(WorldGenLevel level, int x, int z, int y, int w, int d) {
            DynastyBuildings.walls(level, x, y, z, x + w, y + 3, z + d, bricks());
            DynastyBuildings.clear(level, x + 1, y, z + 1, x + w - 1, y + 3, z + d - 1);
            DynastyBuildings.plane(level, x - 1, z - 1, x + w + 1, z + d + 1, y + 4, marble());
            level.setBlock(new BlockPos(x + w / 2, y + 2, z + d / 2), lantern(), 2);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource rand = ctx.random();
            BlockPos origin = ctx.origin();
            int y = DynastyBuildings.ground(level, origin.getX(), origin.getZ());
            if (y <= level.getSeaLevel() + 1) {
                return false;
            }
            for (int x = -11; x <= 11; x++) {
                for (int z = -11; z <= 11; z++) {
                    level.setBlock(new BlockPos(origin.getX() + x, y - 1, origin.getZ() + z),
                            (Math.abs(x) == 11 || Math.abs(z) == 11) ? bricks() : marble(), 2);
                }
            }
            tent(level, origin.getX() - 9, origin.getZ() - 9, y, 5, 5);
            tent(level, origin.getX() + 4, origin.getZ() - 9, y, 5, 5);
            tent(level, origin.getX() - 3, origin.getZ() + 5, y, 6, 5);
            // 兵器架 / weapon racks
            for (int[] c : new int[][]{{-6, 2}, {6, 2}, {0, 0}}) {
                for (int h = 0; h < 3; h++) {
                    level.setBlock(new BlockPos(origin.getX() + c[0], y + h, origin.getZ() + c[1]), pillar(), 2);
                }
                level.setBlock(new BlockPos(origin.getX() + c[0], y + 3, origin.getZ() + c[1]), bronze(), 2);
            }
            DynastyBuildings.chest(level, rand, origin.getX(), y, origin.getZ() - 2,
                    DynastyBuildings.loot("barracks"));
            DynastyBuildings.chest(level, rand, origin.getX() - 6, y, origin.getZ() + 2,
                    DynastyBuildings.loot("barracks"));
            return true;
        }
    }

    /** 烽火台 / watchtower：高台望楼 + 火盆 + 宝箱 */
    public static class WatchtowerFeature extends Feature<NoneFeatureConfiguration> {
        public WatchtowerFeature(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource rand = ctx.random();
            BlockPos origin = ctx.origin();
            int y = DynastyBuildings.ground(level, origin.getX(), origin.getZ());
            if (y <= level.getSeaLevel() + 1) {
                return false;
            }
            for (int x = -4; x <= 4; x++) {
                for (int z = -4; z <= 4; z++) {
                    level.setBlock(new BlockPos(origin.getX() + x, y - 1, origin.getZ() + z), marble(), 2);
                }
            }
            // 塔身 / tower body
            DynastyBuildings.walls(level, origin.getX() - 3, y, origin.getZ() - 3,
                    origin.getX() + 3, y + 14, origin.getZ() + 3, bricks());
            DynastyBuildings.clear(level, origin.getX() - 2, y, origin.getZ() - 2,
                    origin.getX() + 2, y + 14, origin.getZ() + 2);
            // 观景台 / balcony
            DynastyBuildings.plane(level, origin.getX() - 5, origin.getZ() - 5,
                    origin.getX() + 5, origin.getZ() + 5, y + 15, marble());
            for (int[] c : new int[][]{{-5, -5}, {-5, 5}, {5, -5}, {5, 5}}) {
                level.setBlock(new BlockPos(origin.getX() + c[0], y + 16, origin.getZ() + c[1]), lantern(), 2);
            }
            level.setBlock(new BlockPos(origin.getX(), y + 16, origin.getZ()), bronze(), 2);
            level.setBlock(new BlockPos(origin.getX(), y + 17, origin.getZ()), lantern(), 2);
            // 层间地板与箱 / floors and chests
            for (int floorY : new int[]{y + 5, y + 10}) {
                DynastyBuildings.plane(level, origin.getX() - 2, origin.getZ() - 2,
                        origin.getX() + 2, origin.getZ() + 2, floorY, bricks());
                level.setBlock(new BlockPos(origin.getX() + 1, floorY + 1, origin.getZ() + 1), jade(), 2);
                DynastyBuildings.chest(level, rand, origin.getX() - 1, floorY + 1, origin.getZ() - 1,
                        DynastyBuildings.loot("watchtower"));
            }
            return true;
        }
    }

    /** 九霄天界建筑：宝塔 / 云台 / 演武场 / sky buildings of the nine-heaven realm */
    public static class SkyBuilding extends Feature<NoneFeatureConfiguration> {

        /** 三种建筑 / the three kinds */
        public enum Kind { PAGODA, PLATFORM, DOJO }

        private static BlockState roof() {
            return Blocks.DEEPSLATE_TILES.defaultBlockState();
        }

        private final Kind kind;

        public SkyBuilding(Codec<NoneFeatureConfiguration> codec, Kind kind) {
            super(codec);
            this.kind = kind;
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            BlockPos origin = ctx.origin();
            return switch (this.kind) {
                case PAGODA -> pagoda(level, origin);
                case PLATFORM -> platform(level, origin);
                case DOJO -> dojo(level, origin);
            };
        }

        /** 九霄宝塔：五层塔身，层层有屋檐与朱柱 / five-tier pagoda */
        private boolean pagoda(WorldGenLevel level, BlockPos origin) {
            int y = origin.getY();
            for (int x = -4; x <= 4; x++) {
                for (int z = -4; z <= 4; z++) {
                    level.setBlock(origin.offset(x, y - 1, z), marble(), 2);
                    if (Math.abs(x) == 4 || Math.abs(z) == 4) {
                        level.setBlock(origin.offset(x, y, z), bricks(), 2);
                    }
                }
            }
            for (int tier = 0; tier < 5; tier++) {
                int ty = y + 1 + tier * 4;
                int r = Math.max(1, 3 - tier / 2);
                for (int x = -r; x <= r; x++) {
                    for (int z = -r; z <= r; z++) {
                        boolean edge = Math.abs(x) == r || Math.abs(z) == r;
                        if (!edge) {
                            continue;
                        }
                        boolean door = z == r && Math.abs(x) <= 1 && tier % 2 == 0;
                        if (!door) {
                            level.setBlock(origin.offset(x, ty, z), bricks(), 2);
                        }
                        level.setBlock(origin.offset(x, ty + 3, z), roof(), 2);
                    }
                }
                for (int cx : new int[]{-r, r}) {
                    for (int cz : new int[]{-r, r}) {
                        level.setBlock(origin.offset(cx, ty, cz), pillar(), 2);
                        level.setBlock(origin.offset(cx, ty + 2, cz), lantern(), 2);
                    }
                }
            }
            level.setBlock(origin.offset(0, y + 21, 0), jade(), 2);
            level.setBlock(origin.offset(0, y + 22, 0), bronze(), 2);
            return true;
        }

        /** 云台：悬浮石台 + 中央法阵祭坛（可直接召唤 Boss）/ platform with an altar */
        private boolean platform(WorldGenLevel level, BlockPos origin) {
            int y = origin.getY();
            for (int x = -4; x <= 4; x++) {
                for (int z = -4; z <= 4; z++) {
                    level.setBlock(origin.offset(x, y - 1, z), marble(), 2);
                }
            }
            for (int[] corner : new int[][]{{-4, -4}, {-4, 4}, {4, -4}, {4, 4}}) {
                level.setBlock(origin.offset(corner[0], y, corner[1]), pillar(), 2);
                level.setBlock(origin.offset(corner[0], y + 1, corner[1]), pillar(), 2);
                level.setBlock(origin.offset(corner[0], y + 2, corner[1]), lantern(), 2);
            }
            level.setBlock(origin.offset(0, y, 0), altar(), 2);
            for (int[] d : new int[][]{{2, 0}, {-2, 0}, {0, 2}, {0, -2}}) {
                level.setBlock(origin.offset(d[0], y, d[1]), jade(), 2);
            }
            return true;
        }

        /** 演武场：砖石校场 + 靶子与兵器架 / training ground */
        private boolean dojo(WorldGenLevel level, BlockPos origin) {
            int y = origin.getY();
            for (int x = -6; x <= 6; x++) {
                for (int z = -6; z <= 6; z++) {
                    boolean border = Math.abs(x) == 6 || Math.abs(z) == 6;
                    level.setBlock(origin.offset(x, y - 1, z), border ? marble() : bricks(), 2);
                }
            }
            for (int[] corner : new int[][]{{-6, -6}, {-6, 6}, {6, -6}, {6, 6}}) {
                level.setBlock(origin.offset(corner[0], y, corner[1]), pillar(), 2);
                level.setBlock(origin.offset(corner[0], y + 1, corner[1]), pillar(), 2);
                level.setBlock(origin.offset(corner[0], y + 2, corner[1]), lantern(), 2);
            }
            // 靶子与兵器架 / targets and weapon racks
            for (int[] t : new int[][]{{-3, -3}, {3, -3}, {-3, 3}, {3, 3}}) {
                level.setBlock(origin.offset(t[0], y, t[1]), Blocks.TARGET.defaultBlockState(), 2);
            }
            for (int i = -2; i <= 2; i++) {
                level.setBlock(origin.offset(i, y, 6), bronze(), 2);
            }
            level.setBlock(origin.offset(0, y, 0), altar(), 2);
            return true;
        }
    }

}
