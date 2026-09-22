package com.dynasty.worldgen;

import com.dynasty.Dynasty;
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
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * Dynasty 世界生成注册 / Dynasty worldgen features registry.
 */
@SuppressWarnings({"null", "removal"})
public class DynastyFeatures {

    public static final DeferredRegister<Feature<?>> FEATURES =
            DeferredRegister.create(ForgeRegistries.FEATURES, Dynasty.MODID);

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> PALACE_RUIN =
            FEATURES.register("palace_ruin", () -> new PalaceRuinFeature(NoneFeatureConfiguration.CODEC));

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> IMPERIAL_TOMB =
            FEATURES.register("imperial_tomb", () -> new ImperialTombFeature(NoneFeatureConfiguration.CODEC));

    // ---- 2024 新增建筑 / new buildings ----
    public static final RegistryObject<Feature<NoneFeatureConfiguration>> GREAT_WALL =
            FEATURES.register("great_wall", () -> new DynastyBuildings.GreatWallFeature(NoneFeatureConfiguration.CODEC));

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> PAGODA =
            FEATURES.register("pagoda", () -> new DynastyBuildings.PagodaFeature(NoneFeatureConfiguration.CODEC));

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> HEAVEN_ALTAR =
            FEATURES.register("heaven_altar", () -> new DynastyBuildings.AltarFeature(NoneFeatureConfiguration.CODEC));

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> POST_STATION =
            FEATURES.register("post_station", () -> new DynastyBuildings.PostStationFeature(NoneFeatureConfiguration.CODEC));

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> PAIFANG =
            FEATURES.register("paifang", () -> new DynastyBuildings.PaifangFeature(NoneFeatureConfiguration.CODEC));

    // ---- 第二批建筑（含法阵召唤场）/ second batch ----
    public static final RegistryObject<Feature<NoneFeatureConfiguration>> RITUAL_CIRCLE =
            FEATURES.register("ritual_circle", () -> new DynastyBuildings2.RitualCircleFeature(NoneFeatureConfiguration.CODEC));

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> TEMPLE =
            FEATURES.register("temple", () -> new DynastyBuildings2.TempleFeature(NoneFeatureConfiguration.CODEC));

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> BARRACKS =
            FEATURES.register("barracks", () -> new DynastyBuildings2.BarracksFeature(NoneFeatureConfiguration.CODEC));

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> WATCHTOWER =
            FEATURES.register("watchtower", () -> new DynastyBuildings2.WatchtowerFeature(NoneFeatureConfiguration.CODEC));
    // ---- 九霄天界建筑 / nine-heaven buildings ----
    public static final RegistryObject<Feature<NoneFeatureConfiguration>> SKY_PAGODA =
            FEATURES.register("sky_pagoda", () -> new DynastyBuildings2.SkyBuilding(
                    NoneFeatureConfiguration.CODEC, DynastyBuildings2.SkyBuilding.Kind.PAGODA));

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> CLOUD_PLATFORM =
            FEATURES.register("cloud_platform", () -> new DynastyBuildings2.SkyBuilding(
                    NoneFeatureConfiguration.CODEC, DynastyBuildings2.SkyBuilding.Kind.PLATFORM));

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> SKY_DOJO =
            FEATURES.register("sky_dojo", () -> new DynastyBuildings2.SkyBuilding(
                    NoneFeatureConfiguration.CODEC, DynastyBuildings2.SkyBuilding.Kind.DOJO));

    // ---- 第三批：各维度新建筑（中式构件拼出来的，不再是火柴盒）----
    private static RegistryObject<Feature<NoneFeatureConfiguration>> city(String id,
                                                                          DynastyBuildings3.Kind kind) {
        return FEATURES.register(id, () -> new DynastyBuildings3.CityBuilding(
                NoneFeatureConfiguration.CODEC, kind));
    }

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> HALL =
            city("hall", DynastyBuildings3.Kind.HALL);

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> OBSERVATORY =
            city("observatory", DynastyBuildings3.Kind.OBSERVATORY);

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> MARKET =
            city("market", DynastyBuildings3.Kind.MARKET);

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> GHOST_GATE =
            city("ghost_gate", DynastyBuildings3.Kind.GHOST_GATE);

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> JUDGE_HALL =
            city("judge_hall", DynastyBuildings3.Kind.JUDGE_HALL);

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> BRIDGE =
            city("bridge", DynastyBuildings3.Kind.BRIDGE);

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> SKY_STAIR =
            city("sky_stair", DynastyBuildings3.Kind.SKY_STAIR);

    /** 雷池 / the thunder pool */
    public static final RegistryObject<Feature<NoneFeatureConfiguration>> THUNDER_POOL =
            city("thunder_pool", DynastyBuildings3.Kind.THUNDER_POOL);

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> DRAGON_HALL =
            city("dragon_hall", DynastyBuildings3.Kind.DRAGON_HALL);

    public static final RegistryObject<Feature<NoneFeatureConfiguration>> PEARL_TOWER =
            city("pearl_tower", DynastyBuildings3.Kind.PEARL_TOWER);

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

    /** 皇宫遗迹：白玉台基 + 宫砖 + 朱红柱 + 宫灯 / surface palace ruin */
    public static class PalaceRuinFeature extends Feature<NoneFeatureConfiguration> {

        public PalaceRuinFeature(Codec<NoneFeatureConfiguration> codec) {
            super(codec);
        }

        @Override
        public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
            WorldGenLevel level = ctx.level();
            RandomSource rand = ctx.random();
            BlockPos origin = ctx.origin();
            int y = level.getHeight(Heightmap.Types.WORLD_SURFACE_WG, origin.getX(), origin.getZ());
            int half = 5;

            for (int dx = -half; dx <= half; dx++) {
                for (int dz = -half; dz <= half; dz++) {
                    BlockPos p = new BlockPos(origin.getX() + dx, y - 1, origin.getZ() + dz);
                    DynastyFeaturePlacement.setBlock(level, p, (Math.abs(dx) == half || Math.abs(dz) == half) ? bricks() : marble(), 2);
                    DynastyFeaturePlacement.setBlock(level, p.above(), Blocks.AIR.defaultBlockState(), 2);
                }
            }
            for (int dx : new int[]{-half + 1, half - 1}) {
                for (int dz : new int[]{-half + 1, half - 1}) {
                    for (int h = 0; h < 4; h++) {
                        DynastyFeaturePlacement.setBlock(level, new BlockPos(origin.getX() + dx, y + h, origin.getZ() + dz), pillar(), 2);
                    }
                    DynastyFeaturePlacement.setBlock(level, new BlockPos(origin.getX() + dx, y + 4, origin.getZ() + dz), lantern(), 2);
                }
            }
            DynastyFeaturePlacement.setBlock(level, new BlockPos(origin.getX(), y, origin.getZ()), jade(), 2);
            BlockPos chestPos = new BlockPos(origin.getX(), y + 1, origin.getZ());
            if (DynastyFeaturePlacement.setBlock(level, chestPos, Blocks.CHEST.defaultBlockState(), 2)
                    && level.getBlockEntity(chestPos) instanceof ChestBlockEntity chest) {
                chest.setLootTable(new ResourceLocation(Dynasty.MODID, "chests/palace_ruin"), rand.nextLong());
            }
            return true;
        }
    }
}
