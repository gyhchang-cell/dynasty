package com.dynasty.structure;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;

/**
 * 王朝结构部件基类：提供局部坐标放置/填充工具。
 * Base class for dynasty structure pieces: local-coordinate placement helpers.
 */
public abstract class DynastyStructurePiece extends StructurePiece {

    protected DynastyStructurePiece(StructurePieceType type, int genDepth, BoundingBox box) {
        super(type, genDepth, box);
    }

    protected DynastyStructurePiece(StructurePieceType type, CompoundTag tag) {
        super(type, tag);
    }

    @Override
    protected void addAdditionalSaveData(net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext ctx,
                                         CompoundTag tag) {
        // 确定性生成，无需保存额外数据 / deterministic generation, nothing to store
    }

    protected void set(WorldGenLevel level, BoundingBox box, int dx, int dy, int dz, BlockState state) {
        // 注意：placeBlock 内部会自行把局部坐标转换为世界坐标
        // NOTE: placeBlock converts local coordinates to world coordinates itself.
        placeBlock(level, state, dx, dy, dz, box);
    }

    protected void fill(WorldGenLevel level, BoundingBox box, int x1, int y1, int z1,
                        int x2, int y2, int z2, BlockState state) {
        for (int y = y1; y <= y2; y++) {
            for (int x = x1; x <= x2; x++) {
                for (int z = z1; z <= z2; z++) {
                    set(level, box, x, y, z, state);
                }
            }
        }
    }

    /** 只砌四壁 / perimeter walls only */
    protected void walls(WorldGenLevel level, BoundingBox box, int x1, int y1, int z1,
                         int x2, int y2, int z2, BlockState state) {
        for (int y = y1; y <= y2; y++) {
            for (int x = x1; x <= x2; x++) {
                set(level, box, x, y, z1, state);
                set(level, box, x, y, z2, state);
            }
            for (int z = z1; z <= z2; z++) {
                set(level, box, x1, y, z, state);
                set(level, box, x2, y, z, state);
            }
        }
    }

    protected BlockPos world(int dx, int dy, int dz) {
        return new BlockPos(getWorldX(dx, dz), getWorldY(dy), getWorldZ(dx, dz));
    }
}
