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

    /** Layered glazed roof; all writes retain StructurePiece's chunk clipping and rotation. */
    protected void glazedRoof(WorldGenLevel level, BoundingBox box,int x0,int z0,int x1,int z1,int y,int layers) {
        var tile=net.minecraft.world.level.block.Blocks.DARK_PRISMARINE.defaultBlockState();
        var stair=net.minecraft.world.level.block.Blocks.DARK_PRISMARINE_STAIRS.defaultBlockState();
        var ridge=com.dynasty.DynastyBlocks.JADE_BLOCK.get().defaultBlockState();
        for(int k=0;k<layers;k++) {
            int a=x0+k,b=x1-k,c=z0+k,d=z1-k;
            if(a>b||c>d)break;
            fill(level,box,a,y+k,c,b,y+k,d,tile);
            for(int x=a;x<=b;x++) {
                set(level,box,x,y+k,c,com.dynasty.worldgen.DynastyBuildKit.facing(stair,net.minecraft.core.Direction.SOUTH));
                set(level,box,x,y+k,d,com.dynasty.worldgen.DynastyBuildKit.facing(stair,net.minecraft.core.Direction.NORTH));
            }
            for(int z=c+1;z<d;z++) {
                set(level,box,a,y+k,z,com.dynasty.worldgen.DynastyBuildKit.facing(stair,net.minecraft.core.Direction.EAST));
                set(level,box,b,y+k,z,com.dynasty.worldgen.DynastyBuildKit.facing(stair,net.minecraft.core.Direction.WEST));
            }
            if(k==0)for(int[] p:new int[][]{{a,c},{a,d},{b,c},{b,d}})set(level,box,p[0],y+k,p[1],ridge);
        }
    }
}
