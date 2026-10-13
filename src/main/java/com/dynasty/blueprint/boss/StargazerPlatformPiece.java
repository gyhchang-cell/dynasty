package com.dynasty.blueprint.boss;
import com.dynasty.structure.DynastyStructurePiece;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;

/** Original35-block octagonal wood platform at floor200. No edge rail or invisible wall. */
public final class StargazerPlatformPiece extends DynastyStructurePiece {
    public StargazerPlatformPiece(BlockPos p){super(WoodKiteContent.PLATFORM_PIECE.get(),0,new BoundingBox(p.getX(),p.getY(),p.getZ(),p.getX()+34,p.getY()+7,p.getZ()+34));setOrientation(Direction.SOUTH);}
    public StargazerPlatformPiece(StructurePieceSerializationContext c,CompoundTag t){super(WoodKiteContent.PLATFORM_PIECE.get(),t);}
    public BlockPos centre(){return getWorldPos(17,2,17).immutable();}
    public static boolean inside(int x,int z){return Math.abs(x)<=17&&Math.abs(z)<=17&&Math.abs(x)+Math.abs(z)<=24;}
    @Override public void postProcess(WorldGenLevel w,StructureManager sm,ChunkGenerator gen,RandomSource random,BoundingBox clip,ChunkPos chunk,BlockPos pivot){for(int x=-17;x<=17;x++)for(int z=-17;z<=17;z++)if(inside(x,z)){set(w,clip,x+17,1,z+17,WoodKiteContent.PLANK.get().defaultBlockState());if(Math.abs(x)<=1||Math.abs(z)<=1||Math.abs(Math.abs(x)-Math.abs(z))<=1)set(w,clip,x+17,0,z+17,Blocks.STRIPPED_DARK_OAK_LOG.defaultBlockState());}for(int x:new int[]{-10,10})for(int z:new int[]{-10,10}){fill(w,clip,x+17,2,z+17,x+17,6,z+17,Blocks.STRIPPED_DARK_OAK_LOG.defaultBlockState());set(w,clip,x+17,7,z+17,Blocks.OAK_SLAB.defaultBlockState());}set(w,clip,17,1,17,WoodKiteContent.SOCKET.get().defaultBlockState());}
}
