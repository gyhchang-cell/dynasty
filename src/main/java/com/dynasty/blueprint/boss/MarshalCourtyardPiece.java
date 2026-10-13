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

/** Thirty-two-metre centre span, fifteen-metre broken walls and a genuinely open entry gate. */
public final class MarshalCourtyardPiece extends DynastyStructurePiece {
    public MarshalCourtyardPiece(BlockPos origin){super(BlindMarshalContent.YARD_PIECE.get(),0,new BoundingBox(origin.getX(),origin.getY(),origin.getZ(),origin.getX()+32,origin.getY()+16,origin.getZ()+32));setOrientation(Direction.SOUTH);}
    public MarshalCourtyardPiece(StructurePieceSerializationContext c,CompoundTag t){super(BlindMarshalContent.YARD_PIECE.get(),t);}
    public BlockPos centre(){return getWorldPos(16,1,16).immutable();}
    @Override public void postProcess(WorldGenLevel w,StructureManager sm,ChunkGenerator gen,RandomSource random,BoundingBox clip,ChunkPos chunk,BlockPos pivot){
        fill(w,clip,0,0,0,32,0,32,Blocks.SANDSTONE.defaultBlockState());fill(w,clip,3,1,3,29,16,29,Blocks.AIR.defaultBlockState());
        for(int x=0;x<=32;x++)for(int z=0;z<=32;z++){
            if(x<=2||x>=30||z<=2||z>=30){int height=15-((x*7+z*11)%7==0?2:0);fill(w,clip,x,1,z,x,height,z,(x+z)%5==0?Blocks.CUT_SANDSTONE.defaultBlockState():Blocks.SANDSTONE.defaultBlockState());}
            else if((x*13+z*3)%31==0)set(w,clip,x,0,z,Blocks.BONE_BLOCK.defaultBlockState());
        }
        // No narrow doorway forces the5.2m actor or players to phase through terrain.
        fill(w,clip,13,1,0,19,7,2,Blocks.AIR.defaultBlockState());
        for(int i=0;i<8;i++){double a=i*Math.PI/4;int x=16+(int)Math.round(Math.cos(a)*12),z=16+(int)Math.round(Math.sin(a)*12);set(w,clip,x,0,z,Blocks.CRACKED_STONE_BRICKS.defaultBlockState());}
        set(w,clip,16,0,16,BlindMarshalContent.SOCKET.get().defaultBlockState());
    }
}
