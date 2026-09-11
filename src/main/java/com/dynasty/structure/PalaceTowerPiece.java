package com.dynasty.structure;

import com.dynasty.DynastyBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;

/**
 * 角楼：城墙四角的楼阁（重檐攒尖顶 + 飞檐 + 宫灯）。
 * Corner tower: pavilion at each palace corner with a tiered pyramidal roof.
 */
public class PalaceTowerPiece extends DynastyStructurePiece {

    public static final int SIZE = 12;
    public static final int HEIGHT = 26;

    public PalaceTowerPiece(StructurePieceType type, int genDepth, BlockPos pos) {
        super(type, genDepth,
                makeBoundingBox(pos.getX(), pos.getY(), pos.getZ(), Direction.NORTH, SIZE, HEIGHT, SIZE));
        this.setOrientation(Direction.NORTH);
    }

    public PalaceTowerPiece(StructurePieceType type, CompoundTag tag) {
        super(type, tag);
    }

    @Override
    public void postProcess(WorldGenLevel level, StructureManager manager, ChunkGenerator generator,
                            RandomSource random, BoundingBox box, ChunkPos chunkPos, BlockPos pos) {
        BlockState brick = DynastyBlocks.PALACE_BRICKS.get().defaultBlockState();
        BlockState marble = DynastyBlocks.MARBLE_BLOCK.get().defaultBlockState();
        BlockState jade = DynastyBlocks.JADE_BLOCK.get().defaultBlockState();
        BlockState pillar = DynastyBlocks.CRIMSON_PILLAR.get().defaultBlockState();
        BlockState lantern = DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState();
        BlockState air = Blocks.AIR.defaultBlockState();

        // 基座 / base
        fill(level, box, 0, 0, 0, 11, 1, 11, marble);
        fill(level, box, 1, 2, 1, 10, 2, 10, brick);

        // 楼身（中空）/ hollow tower body
        walls(level, box, 1, 3, 1, 10, 16, 10, brick);
        fill(level, box, 2, 3, 2, 9, 16, 9, air);
        fill(level, box, 2, 3, 2, 9, 3, 9, marble);

        // 角柱 / corner columns
        for (int y = 2; y <= 16; y++) {
            set(level, box, 1, y, 1, pillar);
            set(level, box, 1, y, 10, pillar);
            set(level, box, 10, y, 1, pillar);
            set(level, box, 10, y, 10, pillar);
        }

        // 窗洞 / window slits
        for (int y = 6; y <= 11; y += 5) {
            set(level, box, 5, y, 1, air);
            set(level, box, 6, y, 1, air);
            set(level, box, 5, y, 10, air);
            set(level, box, 6, y, 10, air);
            set(level, box, 1, y, 5, air);
            set(level, box, 1, y, 6, air);
            set(level, box, 10, y, 5, air);
            set(level, box, 10, y, 6, air);
        }

        // 楼内宫灯 / lanterns inside
        set(level, box, 3, 14, 3, lantern);
        set(level, box, 8, 14, 8, lantern);

        // 重檐攒尖顶 / tiered pyramidal roof
        for (int layer = 0; layer < 5; layer++) {
            int a = layer;
            int b = 11 - layer;
            walls(level, box, a, 17 + layer, a, b, 17 + layer, b, layer % 2 == 0 ? brick : jade);
            fill(level, box, a + 1, 17 + layer, a + 1, b - 1, 17 + layer, b - 1, air);
        }
        set(level, box, 5, 22, 5, jade);
        set(level, box, 6, 22, 6, jade);
        set(level, box, 5, 23, 5, DynastyBlocks.DRAGON_THRONE.get().defaultBlockState());

        // 飞檐角饰 / upturned eave tips
        for (int[] c : new int[][]{{1, 1}, {1, 10}, {10, 1}, {10, 10}}) {
            set(level, box, c[0], 17, c[1], marble);
            set(level, box, c[0], 18, c[1], jade);
        }
    }
}
