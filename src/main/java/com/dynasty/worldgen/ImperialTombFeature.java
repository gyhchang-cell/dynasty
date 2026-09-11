package com.dynasty.worldgen;

import com.dynasty.Dynasty;
import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/**
 * 皇陵地宫：大理石墓室 + 宫砖地 + 宫灯 + 宝箱 + 兵马俑。
 * Underground imperial tomb with treasure and terracotta guardians.
 */
@SuppressWarnings({"null", "removal"})
public class ImperialTombFeature extends Feature<NoneFeatureConfiguration> {

    public ImperialTombFeature(Codec<NoneFeatureConfiguration> codec) {
        super(codec);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
        WorldGenLevel level = ctx.level();
        RandomSource rand = ctx.random();
        BlockPos origin = ctx.origin();
        int r = 6;
        int h = 5;

        for (int dx = -r; dx <= r; dx++) {
            for (int dz = -r; dz <= r; dz++) {
                for (int dy = -1; dy <= h; dy++) {
                    BlockPos p = origin.offset(dx, dy, dz);
                    boolean shell = Math.abs(dx) == r || Math.abs(dz) == r || dy == -1 || dy == h;
                    if (shell) {
                        level.setBlock(p, (dy == -1) ? DynastyFeatures.bricks() : DynastyFeatures.marble(), 2);
                    } else {
                        level.setBlock(p, Blocks.CAVE_AIR.defaultBlockState(), 2);
                    }
                }
            }
        }
        level.setBlock(origin.below(), DynastyFeatures.jade(), 2);
        level.setBlock(origin, Blocks.CHEST.defaultBlockState(), 2);
        if (level.getBlockEntity(origin) instanceof ChestBlockEntity chest) {
            chest.setLootTable(new ResourceLocation(Dynasty.MODID, "chests/imperial_tomb"), rand.nextLong());
        }
        for (int dx : new int[]{-r + 1, r - 1}) {
            for (int dz : new int[]{-r + 1, r - 1}) {
                level.setBlock(origin.offset(dx, 2, dz), DynastyFeatures.lantern(), 2);
            }
        }
        // 守卫：兵马俑 / guardians
        for (int i = 0; i < 3; i++) {
            var warrior = com.dynasty.entity.DynastyEntities.TERRACOTTA_WARRIOR.get().create(level.getLevel());
            if (warrior != null) {
                double dx = (rand.nextDouble() - 0.5D) * 6.0D;
                double dz = (rand.nextDouble() - 0.5D) * 6.0D;
                warrior.moveTo(origin.getX() + dx + 0.5D, origin.getY(), origin.getZ() + dz + 0.5D, 0.0F, 0.0F);
                level.addFreshEntity(warrior);
            }
        }
        return true;
    }
}
