package com.dynasty.blueprint.artifact;

import com.dynasty.structure.DynastyStructurePiece;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;

/** Original open court, three supported glazed-roof shrines, actual meditation/path/ring floor markers. */
public final class TaiqingTemplePiece extends DynastyStructurePiece {
    public TaiqingTemplePiece(BlockPos p){super(TaiqingContent.TEMPLE_PIECE.get(),0,new BoundingBox(p.getX(),p.getY(),p.getZ(),p.getX()+20,p.getY()+15,p.getZ()+20));setOrientation(Direction.SOUTH);}
    public TaiqingTemplePiece(StructurePieceSerializationContext c,CompoundTag n){super(TaiqingContent.TEMPLE_PIECE.get(),n);}
    public BlockPos swordCase(){return getWorldPos(10,7,10).immutable();}
    @Override public void postProcess(WorldGenLevel w,StructureManager structures,ChunkGenerator generator,RandomSource random,BoundingBox clip,ChunkPos chunk,BlockPos pivot){
        fill(w,clip,0,0,0,20,5,20,Blocks.STONE_BRICKS.defaultBlockState());fill(w,clip,0,6,0,20,6,20,Blocks.POLISHED_ANDESITE.defaultBlockState());
        fill(w,clip,1,7,1,19,11,19,Blocks.AIR.defaultBlockState());walls(w,clip,0,7,0,20,8,20,Blocks.STONE_BRICKS.defaultBlockState());
        fill(w,clip,9,7,0,11,9,0,Blocks.AIR.defaultBlockState());fill(w,clip,9,6,0,11,6,10,Blocks.CALCITE.defaultBlockState());
        for(int[] centre:new int[][]{{4,4},{16,4},{4,16}}){int x=centre[0],z=centre[1];
            for(int dx:new int[]{-2,2})for(int dz:new int[]{-2,2})fill(w,clip,x+dx,7,z+dz,x+dx,11,z+dz,Blocks.STRIPPED_SPRUCE_LOG.defaultBlockState());
            fill(w,clip,x-2,11,z-2,x+2,11,z+2,Blocks.SPRUCE_PLANKS.defaultBlockState());glazedRoof(w,clip,x-3,z-3,x+3,z+3,12,3);
            set(w,clip,x,10,z,Blocks.SEA_LANTERN.defaultBlockState());
        }
        set(w,clip,4,6,4,Blocks.LIME_TERRACOTTA.defaultBlockState());
        for(int[] at:TaiqingTrials.PATH){int x=10+at[0],z=10+at[1];set(w,clip,x,6,z,Blocks.CALCITE.defaultBlockState());}
        for(int[] pair:new int[][]{{16,4,16,7},{16,7,13,7},{13,7,13,10},{13,10,13,13}})fill(w,clip,Math.min(pair[0],pair[2]),6,Math.min(pair[1],pair[3]),Math.max(pair[0],pair[2]),6,Math.max(pair[1],pair[3]),Blocks.CALCITE.defaultBlockState());
        for(int dx=-3;dx<=3;dx++)for(int dz=-3;dz<=3;dz++)if(dx*dx+dz*dz<=9)set(w,clip,4+dx,6,16+dz,Blocks.CYAN_TERRACOTTA.defaultBlockState());
        set(w,clip,10,7,10,TaiqingContent.SWORD_CASE.get().defaultBlockState());
    }
}
