package com.dynasty.structure;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;

/** Scorched muster ground, broken palisades, burial rows and a collapsed command tent. */
public final class BattlefieldPiece extends DynastyStructurePiece {
    public BattlefieldPiece(BlockPos origin){
        super(DynastyStructures.BATTLEFIELD_PIECE.get(),0,new BoundingBox(origin.getX(),origin.getY()-3,origin.getZ(),
            origin.getX()+32,origin.getY()+8,origin.getZ()+32));setOrientation(Direction.SOUTH);
    }
    public BattlefieldPiece(StructurePieceSerializationContext context,CompoundTag tag){super(DynastyStructures.BATTLEFIELD_PIECE.get(),tag);}
    @Override public void postProcess(WorldGenLevel level,StructureManager manager,ChunkGenerator generator,RandomSource random,
            BoundingBox clip,ChunkPos chunk,BlockPos pivot){
        // Three layers bridge only the small slopes accepted by findGenerationPoint.
        fill(level,clip,0,0,0,32,2,32,Blocks.DIRT.defaultBlockState());
        for(int x=0;x<33;x++)for(int z=0;z<33;z++){
            int noise=(x*73428767^z*912931)>>>1;
            boolean scorch=(x-9)*(x-9)+(z-10)*(z-10)<30+noise%13
                ||(x-22)*(x-22)+(z-18)*(z-18)<40+noise%17
                ||(x-15)*(x-15)+(z-26)*(z-26)<17+noise%11;
            set(level,clip,x,3,z,(scorch&&noise%4!=0?Blocks.BLACKSTONE:noise%7<2?Blocks.GRAVEL:Blocks.COARSE_DIRT).defaultBlockState());
        }
        fill(level,clip,0,4,0,32,11,32,Blocks.AIR.defaultBlockState());
        // Leave wide gaps on all four sides; neither players nor pathfinding need to jump a wall.
        for(int i=3;i<30;i+=3)if(i<12||i>20){
            fill(level,clip,i,4,2,i,4+i%3,2,Blocks.STRIPPED_DARK_OAK_LOG.defaultBlockState());
            fill(level,clip,2,4,i,2,5+i%2,i,Blocks.DARK_OAK_LOG.defaultBlockState());
            set(level,clip,i,4,30,Blocks.DARK_OAK_FENCE.defaultBlockState());
        }
        // Central flag socket and a toppled beam make the encounter readable from the approach.
        fill(level,clip,14,3,14,18,3,18,Blocks.CRACKED_STONE_BRICKS.defaultBlockState());
        fill(level,clip,16,4,16,16,8,16,Blocks.DARK_OAK_FENCE.defaultBlockState());
        set(level,clip,16,9,16,Blocks.BLACK_BANNER.defaultBlockState());
        fill(level,clip,19,4,18,23,4,18,Blocks.DARK_OAK_LOG.defaultBlockState()
            .setValue(net.minecraft.world.level.block.RotatedPillarBlock.AXIS,Direction.Axis.X));
        // Raised rear platform and torn roof give the priest actual cover and a flank route.
        fill(level,clip,10,4,24,22,4,29,Blocks.DARK_OAK_PLANKS.defaultBlockState());
        for(int x:new int[]{10,22})fill(level,clip,x,5,26,x,8,26,Blocks.DARK_OAK_FENCE.defaultBlockState());
        fill(level,clip,10,8,25,15,8,29,Blocks.BROWN_WOOL.defaultBlockState());
        fill(level,clip,17,7,27,22,7,29,Blocks.BLACK_WOOL.defaultBlockState());
        for(int x=14;x<=18;x++)set(level,clip,x,4,23,Blocks.DARK_OAK_STAIRS.defaultBlockState()
            .setValue(net.minecraft.world.level.block.StairBlock.FACING,Direction.SOUTH));
        for(int z:new int[]{7,11,15,19}){
            fill(level,clip,25,3,z,28,3,z+1,Blocks.PODZOL.defaultBlockState());
            set(level,clip,29,4,z,Blocks.COBBLESTONE_WALL.defaultBlockState());
        }
        for(int[] p:new int[][]{{6,7},{7,22},{25,24}}){
            fill(level,clip,p[0],4,p[1],p[0],6,p[1],Blocks.COAL_BLOCK.defaultBlockState());
            set(level,clip,p[0]+1,5,p[1],Blocks.DARK_OAK_FENCE.defaultBlockState());
        }
    }
}
