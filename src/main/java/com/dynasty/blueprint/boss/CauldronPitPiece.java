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

public final class CauldronPitPiece extends DynastyStructurePiece {
    public CauldronPitPiece(BlockPos origin){super(CauldronPitContent.PIT_PIECE.get(),0,new BoundingBox(origin.getX(),origin.getY(),origin.getZ(),origin.getX()+42,origin.getY()+18,origin.getZ()+42));setOrientation(Direction.SOUTH);}
    public CauldronPitPiece(StructurePieceSerializationContext context,CompoundTag tag){super(CauldronPitContent.PIT_PIECE.get(),tag);}
    public BlockPos centre(){return getWorldPos(21,6,21).immutable();}
    public static BlockPos pillar(BlockPos centre,int i){double a=i*Math.PI/6;return centre.offset((int)Math.round(Math.cos(a)*18),0,(int)Math.round(Math.sin(a)*18));}
    public static BlockPos altar(BlockPos centre,int i){double a=Math.PI/2+i*2*Math.PI/3;return centre.offset((int)Math.round(Math.cos(a)*15),0,(int)Math.round(Math.sin(a)*15));}
    @Override public void postProcess(WorldGenLevel level,StructureManager manager,ChunkGenerator generator,RandomSource random,BoundingBox clip,ChunkPos chunk,BlockPos pivot){
        for(int x=0;x<=42;x++)for(int z=0;z<=42;z++){
            int dx=x-21,dz=z-21,rr=dx*dx+dz*dz;if(rr>400)continue;
            for(int y=0;y<=15;y++)set(level,clip,x,y,z,(y==0?Blocks.DEEPSLATE:Blocks.AIR).defaultBlockState());
            if(rr<=17*17){for(int y=1;y<=5;y++)set(level,clip,x,y,z,(y==5&&((x*13+z*7)%17==0)?Blocks.BONE_BLOCK:Blocks.CRACKED_STONE_BRICKS).defaultBlockState());}
            else {for(int y=1;y<=4;y++)set(level,clip,x,y,z,CauldronPitContent.SOUL_OIL.get().defaultBlockState());}
        }
        // Broad stairs connect the surface approach; combat edge itself has no rail.
        for(int z=1;z<=8;z++)for(int x=19;x<=23;x++){int y=13-z;fill(level,clip,x,1,z,x,y,z,Blocks.STONE_BRICKS.defaultBlockState());}
        for(int i=0;i<12;i++){double a=i*Math.PI/6;int x=21+(int)Math.round(Math.cos(a)*18),z=21+(int)Math.round(Math.sin(a)*18);fill(level,clip,x-1,1,z-1,x+1,5,z+1,Blocks.BONE_BLOCK.defaultBlockState());fill(level,clip,x,6,z,x,10,z,Blocks.BONE_BLOCK.defaultBlockState());set(level,clip,x,11,z,Blocks.SOUL_CAMPFIRE.defaultBlockState());}
        for(int i=0;i<3;i++){double a=Math.PI/2+i*2*Math.PI/3;set(level,clip,21+(int)Math.round(Math.cos(a)*15),6,21+(int)Math.round(Math.sin(a)*15),CauldronPitContent.RITUAL.get().defaultBlockState());}
        set(level,clip,21,5,21,CauldronPitContent.RITUAL.get().defaultBlockState());
        // An actual old walkway and closed door are buried below the south oil moat.
        fill(level,clip,19,0,34,23,0,40,Blocks.DARK_OAK_PLANKS.defaultBlockState());fill(level,clip,19,1,34,23,3,40,Blocks.AIR.defaultBlockState());set(level,clip,21,1,40,Blocks.IRON_DOOR.defaultBlockState());set(level,clip,21,2,40,Blocks.IRON_DOOR.defaultBlockState().setValue(net.minecraft.world.level.block.DoorBlock.HALF,net.minecraft.world.level.block.state.properties.DoubleBlockHalf.UPPER));
    }
}
