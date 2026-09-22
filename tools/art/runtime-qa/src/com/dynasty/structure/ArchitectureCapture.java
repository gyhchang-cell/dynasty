package com.dynasty.structure;

import java.util.HashMap;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;

/** Test source only. Captures production block placement, never enters or changes a world. */
public final class ArchitectureCapture {
    public static Map<BlockPos,BlockState> blocks(String name) {
        Map<BlockPos,BlockState> out=new HashMap<>();
        DynastyStructurePiece piece=switch(name) {
            case "palace" -> new PalacePiece(DynastyStructures.PALACE_PIECE.get(),0,BlockPos.ZERO) {
                @Override protected void set(WorldGenLevel w,BoundingBox b,int x,int y,int z,BlockState s){out.put(new BlockPos(x,y,z),s);}
                @Override protected boolean createChest(WorldGenLevel w,BoundingBox b,RandomSource r,int x,int y,int z,ResourceLocation loot){set(w,b,x,y,z,Blocks.CHEST.defaultBlockState());return true;}
            };
            case "tomb" -> new TombPiece(DynastyStructures.TOMB_PIECE.get(),0,BlockPos.ZERO) {
                @Override protected void set(WorldGenLevel w,BoundingBox b,int x,int y,int z,BlockState s){out.put(new BlockPos(x,y,z),s);}
                @Override protected boolean createChest(WorldGenLevel w,BoundingBox b,RandomSource r,int x,int y,int z,ResourceLocation loot){set(w,b,x,y,z,Blocks.CHEST.defaultBlockState());return true;}
            };
            case "observatory" -> new StarAltarPiece(DynastyStructures.STAR_ALTAR_PIECE.get(),0,BlockPos.ZERO) {
                @Override protected void set(WorldGenLevel w,BoundingBox b,int x,int y,int z,BlockState s){out.put(new BlockPos(x,y,z),s);}
                @Override protected boolean createChest(WorldGenLevel w,BoundingBox b,RandomSource r,int x,int y,int z,ResourceLocation loot){set(w,b,x,y,z,Blocks.CHEST.defaultBlockState());return true;}
            };
            default -> throw new IllegalArgumentException(name);
        };
        piece.postProcess(null,null,null,RandomSource.create(1),piece.getBoundingBox(),null,BlockPos.ZERO);
        if(name.equals("palace")) {
            // Same local offset as PalacePiece.addChildren; include the actual MainHall production code.
            var hall=new MainHallPiece(DynastyStructures.MAIN_HALL_PIECE.get(),1,BlockPos.ZERO) {
                @Override protected void set(WorldGenLevel w,BoundingBox b,int x,int y,int z,BlockState s){out.put(new BlockPos(x+21,y+3,z+14),s);}
                @Override protected boolean createChest(WorldGenLevel w,BoundingBox b,RandomSource r,int x,int y,int z,ResourceLocation loot){set(w,b,x,y,z,Blocks.CHEST.defaultBlockState());return true;}
            };
            hall.postProcess(null,null,null,RandomSource.create(1),hall.getBoundingBox(),null,BlockPos.ZERO);
        }
        return out;
    }
}
