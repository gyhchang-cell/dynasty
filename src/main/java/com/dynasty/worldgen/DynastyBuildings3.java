package com.dynasty.worldgen;

import com.dynasty.DynastyBlocks;
import com.dynasty.entity.DynastyEntities;
import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

import static com.dynasty.worldgen.DynastyBuildKit.*;

/**
 * 各维度新增建筑（第二十五轮）：用构件工具箱拼出中式建筑，不再是一个个「火柴盒」。
 *
 * 天朝·龙庭：玉阶大殿 HALL / 观星台 OBSERVATORY / 市集街 MARKET
 * 地府：鬼门关 GHOST_GATE / 判官府 JUDGE_HALL / 奈何桥 BRIDGE
 * 九霄天界：天梯 SKY_STAIR / 雷池 THUNDER_POOL
 * 东海龙宫：龙王殿 DRAGON_HALL / 珍珠塔 PEARL_TOWER
 *
 * One generic feature class with a {@link Kind} switch (same idea as SkyBuilding).
 */
@SuppressWarnings({"null", "removal"})
public class DynastyBuildings3 {

    private DynastyBuildings3() {
    }

    public enum Kind {
        HALL, OBSERVATORY, MARKET, GHOST_GATE, JUDGE_HALL, BRIDGE, SKY_STAIR, THUNDER_POOL,
        DRAGON_HALL, PEARL_TOWER
    }

    public static class CityBuilding extends Feature<NoneFeatureConfiguration> {

        private final Kind kind;

        public CityBuilding(Codec<NoneFeatureConfiguration> codec, Kind kind) {
            super(codec);
            this.kind = kind;
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource rand = ctx.random();
            BlockPos o = ctx.origin();
            int x = o.getX();
            int z = o.getZ();
            int y = ground(level, x, z) + 1;
            if (y <= level.getSeaLevel() + 1) {
                return false;
            }
            switch (kind) {
                case HALL -> hall(level, rand, x, y, z);
                case OBSERVATORY -> observatory(level, rand, x, y, z);
                case MARKET -> market(level, rand, x, y, z);
                case GHOST_GATE -> ghostGate(level, rand, x, y, z);
                case JUDGE_HALL -> judgeHall(level, rand, x, y, z);
                case BRIDGE -> bridge(level, rand, x, y, z);
                case SKY_STAIR -> skyStair(level, rand, x, y, z);
                case THUNDER_POOL -> thunderPool(level, rand, x, y, z);
                case DRAGON_HALL -> dragonHall(level, rand, x, y, z);
                case PEARL_TOWER -> pearlTower(level, rand, x, y, z);
            }
            return true;
        }
        /** 玉阶大殿：重檐 + 二层 + 内部宝座 / grand hall with twin eaves */
        private void hall(WorldGenLevel level, RandomSource rand, int x, int y, int z) {
            podium(level, x, y, z, 9, 6, bricks(), marble(), quartzStair());
            int base = y + 1;
            hallBody(level, x - 8, base, z - 5, x + 8, base + 4, z + 5, marble(), pillar());
            roof(level, x, base + 6, z, 10, 7, bricks(), jade(), quartzStair());
            hallBody(level, x - 5, base + 5, z - 3, x + 5, base + 8, z + 3, marble(), pillar());
            roof(level, x, base + 10, z, 6, 4, bricks(), jade(), quartzStair());
            floor(level, x - 7, base, z - 4, x + 7, z + 4, bricks());
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, base + 1, z + 3),
                    DynastyBlocks.DRAGON_THRONE.get().defaultBlockState(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, base + 2, z + 3), lantern(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x - 6, base + 1, z - 4),
                    DynastyBlocks.INCENSE_BURNER.get().defaultBlockState(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x + 6, base + 1, z - 4),
                    DynastyBlocks.INCENSE_BURNER.get().defaultBlockState(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x - 3, base + 1, z - 3),
                    DynastyBlocks.CHIME_BELL.get().defaultBlockState(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x + 3, base + 1, z - 3),
                    DynastyBlocks.TAIKO_DRUM.get().defaultBlockState(), 2);
            chest(level, rand, x - 6, base + 1, z + 3, "palace_ruin");
            chest(level, rand, x + 6, base + 1, z + 3, "palace_ruin");
            guard(level, rand, x, base + 1, z, DynastyEntities.JADE_GUARD.get(), 3);
            materials(level, rand, x - 4, base + 1, z - 2, jade(), 6);
        }

        /** 观星台：三层收分高台 + 四角灯柱 + 浑天仪 / observatory tower */
        private void observatory(WorldGenLevel level, RandomSource rand, int x, int y, int z) {
            podium(level, x, y, z, 10, 10, bricks(), marble(), quartzStair());
            int base = y + 1;
            floor(level, x - 9, base, z - 9, x + 9, z + 9, marble());
            railing(level, x - 9, z - 9, x + 9, z + 9, base + 1, pillar());
            for (int tier = 0; tier < 3; tier++) {
                int half = 7 - tier * 2;
                int ty = base + 1 + tier * 3;
                walls(level, x - half, ty, z - half, x + half, ty + 2, z + half, bricks());
                clearBox(level, x - half + 1, ty, z - half + 1, x + half - 1, ty + 2, z + half - 1);
                stairsUp(level, x, ty, z - half - 1, 3, 2, false, false, quartzStair());
            }
            int top = base + 10;
            floor(level, x - 3, top, z - 3, x + 3, z + 3, marble());
            railing(level, x - 3, z - 3, x + 3, z + 3, top + 1, pillar());
            for (int[] c : new int[][]{{-3, -3}, {-3, 3}, {3, -3}, {3, 3}}) {
                column(level, x + c[0], top, top + 2, z + c[1], pillar());
                DynastyFeaturePlacement.setBlock(level, new BlockPos(x + c[0], top + 3, z + c[1]), lantern(), 2);
            }
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, top + 1, z), bronze(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, top + 2, z), jade(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, top + 3, z), jade(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, top + 4, z), jade(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, top + 5, z), lantern(), 2);
            chest(level, rand, x, top + 1, z + 2, "palace_ruin");
            chest(level, rand, x - 2, top + 1, z - 2, "palace_ruin");
            guard(level, rand, x, top + 1, z, DynastyEntities.ARCHER.get(), 2);
            materials(level, rand, x + 2, top + 1, z + 2, DynastyBlocks.JADE_ORE.get().defaultBlockState(), 4);
        }

        /** 市集街：石板路 + 两侧带檐店铺 + 灯杆 + 货箱 / market street */
        private void market(WorldGenLevel level, RandomSource rand, int x, int y, int z) {
            int length = 16;
            floor(level, x - 1, y, z - 3, x + length + 1, z + 3, bricks());
            for (int i = 0; i <= length; i += 4) {
                plane(level, x + i, z - 4, x + i + 1, z + 4, y, marble());
            }
            for (int side : new int[]{-1, 1}) {
                for (int i = 0; i < length; i += 7) {
                    shop(level, rand, x + i, y + 1, z + side * 6, side);
                }
            }
            for (int i = 3; i < length; i += 6) {
                column(level, x + i, y + 1, y + 3, z - 1, pillar());
                DynastyFeaturePlacement.setBlock(level, new BlockPos(x + i, y + 4, z - 1), lantern(), 2);
                column(level, x + i, y + 1, y + 3, z + 1, pillar());
                DynastyFeaturePlacement.setBlock(level, new BlockPos(x + i, y + 4, z + 1), lantern(), 2);
            }
            chest(level, rand, x + 4, y + 1, z + 5, "palace_ruin");
            chest(level, rand, x + 11, y + 1, z - 5, "palace_ruin");
            guard(level, rand, x + 6, y + 1, z, DynastyEntities.ROYAL_GUARD.get(), 2);
            materials(level, rand, x + 9, y + 1, z, bronze(), 6);
        }

        /** 小店铺：木构 + 硬山顶 + 招牌 + 柜台 / a small roofed shop */
        private void shop(WorldGenLevel level, RandomSource rand, int x, int y, int z, int side) {
            int hx = 2;
            floor(level, x - hx, y, z - hx, x + hx, z + hx, marble());
            hallBody(level, x - hx, y + 1, z - hx, x + hx, y + 3, z + hx, bricks(), pillar());
            gableRoof(level, x - hx, y + 5, z - hx, x + hx, z + hx, darkOakStair(), jade(), darkOakStair());
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, y + 6, z - hx), plaque(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x + side, y + 1, z + side * hx), bronze(), 2);
            if (rand.nextBoolean()) {
                chest(level, rand, x - 1, y + 1, z + 1, "palace_ruin");
            }
        }

        /** 鬼门关：黑石关隘 + 骷髅柱 + 冥灯 / the ghost gate of the underworld */
        private void ghostGate(WorldGenLevel level, RandomSource rand, int x, int y, int z) {
            floor(level, x - 6, y, z - 2, x + 6, z + 2, blackstone());
            for (int side : new int[]{-5, 5}) {
                column(level, x + side, y + 1, y + 7, z - 2, blackstone());
                column(level, x + side, y + 1, y + 7, z + 2, blackstone());
                column(level, x + side, y + 1, y + 7, z, bone());
                DynastyFeaturePlacement.setBlock(level, new BlockPos(x + side, y + 8, z - 2), lantern(), 2);
                DynastyFeaturePlacement.setBlock(level, new BlockPos(x + side, y + 8, z + 2), lantern(), 2);
                DynastyFeaturePlacement.setBlock(level, new BlockPos(x + side, y + 8, z), soulSoil(), 2);
            }
            plane(level, x - 6, z - 2, x + 6, z + 2, y + 8, blackstone());
            plane(level, x - 5, z - 1, x + 5, z + 1, y + 9, soulSoil());
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, y + 8, z - 2), lantern(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, y + 8, z + 2), lantern(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, y + 6, z - 3), plaque(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, y + 6, z + 3), plaque(), 2);
            chest(level, rand, x + 3, y + 1, z - 1, "palace_ruin");
            guard(level, rand, x, y + 1, z, DynastyEntities.SOUL_SOLDIER.get(), 3);
            materials(level, rand, x - 3, y + 1, z + 1, bone(), 6);
        }

        /** 判官府：青灰殿宇 + 案台 + 书卷 + 灯 / judge's hall */
        private void judgeHall(WorldGenLevel level, RandomSource rand, int x, int y, int z) {
            podium(level, x, y, z, 8, 5, blackstone(), soulSoil(), blackstoneStair());
            int base = y + 1;
            hallBody(level, x - 7, base, z - 4, x + 7, base + 4, z + 4, blackstone(), bone());
            roof(level, x, base + 5, z, 9, 6, soulSoil(), blackstone(), blackstoneStair());
            floor(level, x - 6, base, z - 3, x + 6, z + 3, blackstone());
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, base + 1, z + 2),
                    DynastyBlocks.ALTAR.get().defaultBlockState(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, base + 2, z + 2), lantern(), 2);
            for (int i = -2; i <= 2; i += 2) {
                column(level, x + i, base + 1, base + 3, z - 3, bone());
                DynastyFeaturePlacement.setBlock(level, new BlockPos(x + i, base + 4, z - 3), lantern(), 2);
            }
            chest(level, rand, x - 5, base + 1, z + 2, "palace_ruin");
            chest(level, rand, x + 5, base + 1, z + 2, "palace_ruin");
            guard(level, rand, x, base + 1, z, DynastyEntities.SOUL_SOLDIER.get(), 2);
            materials(level, rand, x + 4, base + 1, z - 2, DynastyBlocks.DRAGON_CRYSTAL_ORE.get().defaultBlockState(), 3);
        }

        /** 奈何桥：拱桥 + 栏杆 + 桥头灯 / the bridge over the river of souls */
        private void bridge(WorldGenLevel level, RandomSource rand, int x, int y, int z) {
            int span = 14;
            for (int i = 0; i <= span; i++) {
                int arch = (int) Math.round(4.0D * Math.sin(Math.PI * i / span));
                int yy = y + arch;
                for (int w = -2; w <= 2; w++) {
                    DynastyFeaturePlacement.setBlock(level, new BlockPos(x + i, yy, z + w), blackstone(), 2);
                    if (Math.abs(w) == 2) {
                        DynastyFeaturePlacement.setBlock(level, new BlockPos(x + i, yy + 1, z + w), bone(), 2);
                    }
                    DynastyFeaturePlacement.setBlock(level, new BlockPos(x + i, yy - 1, z + w), air(), 2);
                }
            }
            for (int i = 0; i <= span; i += span) {
                column(level, x + i, y, y + 5, z - 3, bone());
                column(level, x + i, y, y + 5, z + 3, bone());
                DynastyFeaturePlacement.setBlock(level, new BlockPos(x + i, y + 6, z - 3), lantern(), 2);
                DynastyFeaturePlacement.setBlock(level, new BlockPos(x + i, y + 6, z + 3), lantern(), 2);
            }
            chest(level, rand, x + span / 2, y + 4, z, "palace_ruin");
            guard(level, rand, x + span / 2, y + 4, z, DynastyEntities.SOUL_SOLDIER.get(), 2);
            materials(level, rand, x + span / 4, y + 3, z, soulSoil(), 4);
        }

        /** 天梯：长阶 + 云台 + 顶端牌坊 / the heavenly stairway */
        private void skyStair(WorldGenLevel level, RandomSource rand, int x, int y, int z) {
            int steps = 18;
            for (int i = 0; i < steps; i++) {
                int yy = y + i;
                for (int w = -2; w <= 2; w++) {
                    DynastyFeaturePlacement.setBlock(level, new BlockPos(x, yy, z + i * 1).offset(0, 0, 0), marble(), 2);
                    DynastyFeaturePlacement.setBlock(level, new BlockPos(x + w, yy, z + i), marble(), 2);
                    if (Math.abs(w) == 2) {
                        DynastyFeaturePlacement.setBlock(level, new BlockPos(x + w, yy + 1, z + i), pillar(), 2);
                    }
                }
                if (i % 6 == 0) {
                    DynastyFeaturePlacement.setBlock(level, new BlockPos(x - 3, yy + 1, z + i), lantern(), 2);
                    DynastyFeaturePlacement.setBlock(level, new BlockPos(x + 3, yy + 1, z + i), lantern(), 2);
                }
            }
            int top = y + steps;
            floor(level, x - 6, top, z + steps - 6, x + 6, z + steps + 6, marble());
            railing(level, x - 6, z + steps - 6, x + 6, z + steps + 6, top + 1, pillar());
            for (int[] c : new int[][]{{-6, -6}, {-6, 6}, {6, -6}, {6, 6}}) {
                column(level, x + c[0], top + 1, top + 4, z + steps + c[1], pillar());
                DynastyFeaturePlacement.setBlock(level, new BlockPos(x + c[0], top + 5, z + steps + c[1]), lantern(), 2);
            }
            chest(level, rand, x, top + 1, z + steps, "palace_ruin");
            guard(level, rand, x, top + 1, z + steps, DynastyEntities.THUNDER_ENVOY.get(), 2);
            materials(level, rand, x + 3, top + 1, z + steps - 3, jade(), 5);
        }

        /** 雷池：水台 + 柱阵 + 避雷针 / the thunder pool */
        private void thunderPool(WorldGenLevel level, RandomSource rand, int x, int y, int z) {
            podium(level, x, y, z, 8, 8, marble(), marble(), quartzStair());
            int base = y + 1;
            floor(level, x - 7, base, z - 7, x + 7, z + 7, marble());
            plane(level, x - 4, z - 4, x + 4, z + 4, base,
                    net.minecraft.world.level.block.Blocks.WATER.defaultBlockState());
            railing(level, x - 7, z - 7, x + 7, z + 7, base + 1, pillar());
            for (int[] c : new int[][]{{-5, -5}, {-5, 0}, {-5, 5}, {0, -5}, {0, 5}, {5, -5}, {5, 0}, {5, 5}}) {
                column(level, x + c[0], base + 1, base + 4, z + c[1], marble());
                DynastyFeaturePlacement.setBlock(level, new BlockPos(x + c[0], base + 5, z + c[1]),
                        net.minecraft.world.level.block.Blocks.LIGHTNING_ROD.defaultBlockState(), 2);
            }
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, base + 1, z), jade(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, base + 2, z), bronze(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, base + 3, z), jade(), 2);
            chest(level, rand, x + 6, base + 1, z + 6, "palace_ruin");
            chest(level, rand, x - 6, base + 1, z - 6, "palace_ruin");
            guard(level, rand, x, base + 1, z, DynastyEntities.THUNDER_ENVOY.get(), 3);
            materials(level, rand, x, base + 1, z + 5, bronze(), 5);
        }

        /** 龙王殿：海晶殿宇 + 珊瑚 + 宝座 / the Dragon King's hall */
        private void dragonHall(WorldGenLevel level, RandomSource rand, int x, int y, int z) {
            podium(level, x, y, z, 9, 6, darkPrismarine(), prismarine(), prismarineStair());
            int base = y + 1;
            hallBody(level, x - 8, base, z - 5, x + 8, base + 4, z + 5, prismarine(), darkPrismarine());
            roof(level, x, base + 5, z, 10, 7, darkPrismarine(), prismarine(), prismarineStair());
            floor(level, x - 7, base, z - 4, x + 7, z + 4, darkPrismarine());
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, base + 1, z + 3),
                    DynastyBlocks.DRAGON_THRONE.get().defaultBlockState(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, base + 2, z + 3), seaLantern(), 2);
            for (int[] c : new int[][]{{-5, -4}, {5, -4}, {-5, 4}, {5, 4}}) {
                DynastyFeaturePlacement.setBlock(level, new BlockPos(x + c[0], base + 1, z + c[1]), seaLantern(), 2);
            }
            chest(level, rand, x - 6, base + 1, z + 3, "dragon_palace");
            chest(level, rand, x + 6, base + 1, z + 3, "dragon_palace");
            guard(level, rand, x, base + 1, z, DynastyEntities.MERFOLK.get(), 4);
            materials(level, rand, x - 4, base + 1, z - 3, prismarine(), 8);
        }

        /** 珍珠塔：海晶塔 + 顶珠 / the pearl tower */
        private void pearlTower(WorldGenLevel level, RandomSource rand, int x, int y, int z) {
            podium(level, x, y, z, 6, 6, darkPrismarine(), prismarine(), prismarineStair());
            int base = y + 1;
            int radius = 4;
            for (int tier = 0; tier < 5; tier++) {
                int ty = base + tier * 4;
                walls(level, x - radius, ty, z - radius, x + radius, ty + 2, z + radius, prismarine());
                clearBox(level, x - radius + 1, ty, z - radius + 1, x + radius - 1, ty + 2, z + radius - 1);
                plane(level, x - radius - 1, z - radius - 1, x + radius + 1, z + radius + 1, ty + 3,
                        darkPrismarine());
                for (int[] c : new int[][]{{-radius - 1, -radius - 1}, {-radius - 1, radius + 1},
                                           {radius + 1, -radius - 1}, {radius + 1, radius + 1}}) {
                    DynastyFeaturePlacement.setBlock(level, new BlockPos(x + c[0], ty + 3, z + c[1]), prismarineStair(), 2);
                    DynastyFeaturePlacement.setBlock(level, new BlockPos(x + c[0], ty + 2, z + c[1]), seaLantern(), 2);
                }
                if (tier % 2 == 0) {
                    chest(level, rand, x + 1, ty + 1, z + 1, "dragon_palace");
                }
                radius = Math.max(2, radius - 1);
            }
            int top = base + 5 * 4;
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, top, z), seaLantern(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, top + 1, z), prismarine(), 2);
            DynastyFeaturePlacement.setBlock(level, new BlockPos(x, top + 2, z), seaLantern(), 2);
            chest(level, rand, x, top + 1, z + 1, "dragon_palace");
            guard(level, rand, x, top + 1, z, DynastyEntities.MERFOLK.get(), 2);
            materials(level, rand, x + 1, top + 1, z - 1, seaLantern(), 4);
        }
    }
}
