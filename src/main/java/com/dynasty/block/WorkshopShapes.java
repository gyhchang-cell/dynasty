package com.dynasty.block;

import java.util.EnumMap;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Generated with the JSON models by tools/art/workshop_assets_v9.py. */
final class WorkshopShapes {
    private static final EnumMap<LivingWorkshopBlock.Kind,VoxelShape[]> SHAPES = new EnumMap<>(LivingWorkshopBlock.Kind.class);
    static {
        SHAPES.put(LivingWorkshopBlock.Kind.MARROW, rotations(Shapes.or(Block.box(1,1,1,15,3,15), Block.box(1,3,1,3,14,15), Block.box(13,3,1,15,14,15), Block.box(3,3,1,13,14,3), Block.box(3,3,13,13,14,15))));
        SHAPES.put(LivingWorkshopBlock.Kind.ESSENCE, rotations(Shapes.or(Block.box(1,0,1,15,3,15), Block.box(5,3,5,11,5,11), Block.box(6,5,6,10,13,10), Block.box(4,13,4,12,15,12))));
        SHAPES.put(LivingWorkshopBlock.Kind.REPAIR, rotations(Shapes.or(Block.box(1,0,2,15,3,14), Block.box(5,3,5,11,10,11), Block.box(0,10,2,16,14,14))));
        SHAPES.put(LivingWorkshopBlock.Kind.VITALITY, rotations(Shapes.or(Block.box(1,0,2,15,3,15), Block.box(1,3,12,15,14,15), Block.box(1,3,2,4,12,12), Block.box(12,3,2,15,12,12), Block.box(0,12,1,16,15,16), Block.box(6,3,7,10,8,11))));
        SHAPES.put(LivingWorkshopBlock.Kind.HIDE, rotations(Shapes.or(Block.box(1,0,2,4,2,14), Block.box(12,0,2,15,2,14), Block.box(1,2,6,3,16,9), Block.box(13,2,6,15,16,9), Block.box(3,13,6,13,16,9), Block.box(3,3,6,13,5,9), Block.box(4,5,7,12,13,8))));
        SHAPES.put(LivingWorkshopBlock.Kind.HERBAL, rotations(Shapes.or(Block.box(1,1,1,15,3,15), Block.box(1,3,1,3,9,15), Block.box(13,3,1,15,9,15), Block.box(3,3,1,13,9,3), Block.box(3,3,13,13,9,15), Block.box(0,7,0,16,10,3), Block.box(0,7,13,16,10,16), Block.box(0,7,3,3,10,13), Block.box(13,7,3,16,10,13))));
        SHAPES.put(LivingWorkshopBlock.Kind.LAPIDARY, rotations(Shapes.or(Block.box(1,0,1,4,9,4), Block.box(1,0,12,4,9,15), Block.box(12,0,1,15,9,4), Block.box(12,0,12,15,9,15), Block.box(0,9,0,16,12,16), Block.box(6,12,6,10,15,10), Block.box(1,5,7,15,7,9))));
        SHAPES.put(LivingWorkshopBlock.Kind.EMBER, rotations(Shapes.or(Block.box(1,0,1,4,4,4), Block.box(1,0,12,4,4,15), Block.box(12,0,1,15,4,4), Block.box(12,0,12,15,4,15), Block.box(2,4,2,14,6,14), Block.box(1,4,1,3,11,15), Block.box(13,4,1,15,11,15), Block.box(3,4,1,13,11,3), Block.box(3,4,13,13,11,15))));
    }
    private static VoxelShape[] rotations(VoxelShape north) {
        VoxelShape[] shapes=new VoxelShape[4]; shapes[0]=north.optimize();
        for(int i=1;i<4;i++) {
            final VoxelShape[] next={Shapes.empty()};
            shapes[i-1].forAllBoxes((x1,y1,z1,x2,y2,z2) ->
                next[0]=Shapes.or(next[0],Shapes.box(1-z2,y1,x1,1-z1,y2,x2)));
            shapes[i]=next[0].optimize();
        }
        return shapes;
    }
    static VoxelShape get(LivingWorkshopBlock.Kind kind,Direction facing) {
        int index=switch(facing) {case EAST -> 1; case SOUTH -> 2; case WEST -> 3; default -> 0;};
        return SHAPES.get(kind)[index];
    }
}
