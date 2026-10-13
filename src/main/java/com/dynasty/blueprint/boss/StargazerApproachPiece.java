package com.dynasty.blueprint.boss;

import com.dynasty.structure.DynastyStructurePiece;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.*;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;

/** An outside-edge hanging hoist gives survival players a first ascent before the central reward rope. */
public final class StargazerApproachPiece extends DynastyStructurePiece {
    public StargazerApproachPiece(BlockPos ground) {
        super(WoodKiteContent.APPROACH_PIECE.get(), 0, new BoundingBox(ground.getX(), ground.getY(), ground.getZ(), ground.getX(), 201, ground.getZ()));
        setOrientation(Direction.SOUTH);
    }
    public StargazerApproachPiece(StructurePieceSerializationContext context, CompoundTag tag) { super(WoodKiteContent.APPROACH_PIECE.get(), tag); }
    @Override public void postProcess(WorldGenLevel world, StructureManager structures, ChunkGenerator generator, RandomSource random, BoundingBox clip, ChunkPos chunk, BlockPos pivot) {
        for (int y=0; y<=201-getBoundingBox().minY(); y++) {
            var at=getWorldPos(0,y,0);
            if (clip.isInside(at) && world.getBlockState(at).isAir() && world.getFluidState(at).isEmpty() && world.getBlockEntity(at)==null)
                set(world, clip, 0,y,0, WoodKiteContent.ROPE.get().defaultBlockState());
        }
    }
}
