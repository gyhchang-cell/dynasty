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
                    level.setBlock(p, (Math.abs(dx) == half || Math.abs(dz) == half) ? bricks() : marble(), 2);
                    level.setBlock(p.above(), Blocks.AIR.defaultBlockState(), 2);
                }
            }
            for (int dx : new int[]{-half + 1, half - 1}) {
                for (int dz : new int[]{-half + 1, half - 1}) {
                    for (int h = 0; h < 4; h++) {
                        level.setBlock(new BlockPos(origin.getX() + dx, y + h, origin.getZ() + dz), pillar(), 2);
                    }
                    level.setBlock(new BlockPos(origin.getX() + dx, y + 4, origin.getZ() + dz), lantern(), 2);
                }
            }
            level.setBlock(new BlockPos(origin.getX(), y, origin.getZ()), jade(), 2);
            BlockPos chestPos = new BlockPos(origin.getX(), y + 1, origin.getZ());
            level.setBlock(chestPos, Blocks.CHEST.defaultBlockState(), 2);
            if (level.getBlockEntity(chestPos) instanceof ChestBlockEntity chest) {
                chest.setLootTable(new ResourceLocation(Dynasty.MODID, "chests/palace_ruin"), rand.nextLong());
            }
            return true;
        }
    }
}
