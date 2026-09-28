package com.dynasty.structure;

import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;

/** Visible surface pavilion plus a protected ladder shaft into the burial passage. */
public class TombAccessPiece extends DynastyStructurePiece {
    public TombAccessPiece(BlockPos origin,int top) {
        super(DynastyStructures.TOMB_ACCESS_PIECE.get(),0,makeBoundingBox(origin.getX(),origin.getY(),origin.getZ(),Direction.NORTH,6,top-origin.getY()+6,6));
        setOrientation(Direction.NORTH);
    }
    public TombAccessPiece(net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext c,CompoundTag tag){super(DynastyStructures.TOMB_ACCESS_PIECE.get(),tag);}
    @Override public void postProcess(WorldGenLevel level,StructureManager manager,net.minecraft.world.level.chunk.ChunkGenerator generator,net.minecraft.util.RandomSource random,BoundingBox box,ChunkPos chunk,BlockPos pos) {
        int surface=getBoundingBox().getYSpan()-6;
        var wall=Blocks.DEEPSLATE_BRICKS.defaultBlockState();var air=Blocks.AIR.defaultBlockState();
        walls(level,box,0,0,0,5,surface+3,5,wall);
        fill(level,box,1,0,1,4,surface+3,4,air);
        fill(level,box,1,0,1,4,0,4,wall);
        fill(level,box,1,1,0,4,3,0,air);fill(level,box,1,1,5,4,3,5,air);
        fill(level,box,2,surface,0,3,surface+2,0,air);
        fill(level,box,2,1,1,2,surface+1,1,Blocks.LADDER.defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING,Direction.SOUTH));
        for(int y=4;y<surface;y+=8)set(level,box,4,y,4,Blocks.SEA_LANTERN.defaultBlockState());
        fill(level,box,0,surface+4,0,5,surface+4,5,com.dynasty.DynastyBlocks.JADE_BLOCK.get().defaultBlockState());
        set(level,box,1,surface+3,0,com.dynasty.DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState());
        set(level,box,4,surface+3,0,com.dynasty.DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState());
    }
}
