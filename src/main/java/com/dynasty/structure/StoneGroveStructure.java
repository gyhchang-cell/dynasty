package com.dynasty.structure;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;

import java.util.Optional;

/**
 * 皇陵石刻：享殿 + 石像生 + 石碑林（地府）。
 * Imperial Stone Grove: offering hall, spirit-path statues and stelae rows (underworld).
 */
public class StoneGroveStructure extends Structure {

    public static final Codec<StoneGroveStructure> CODEC = simpleCodec(StoneGroveStructure::new);

    public StoneGroveStructure(StructureSettings settings) {
        super(settings);
    }

    @Override
    protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx) {
        ChunkPos chunkPos = ctx.chunkPos();
        int x = chunkPos.getMiddleBlockX();
        int z = chunkPos.getMiddleBlockZ();
        int y = ctx.chunkGenerator().getFirstFreeHeight(x, z, Heightmap.Types.WORLD_SURFACE_WG,
                ctx.heightAccessor(), ctx.randomState());
        if (y <= ctx.heightAccessor().getMinBuildHeight() + 5) {
            return Optional.empty();
        }
        BlockPos origin = new BlockPos(x - StoneGrovePiece.SIZE / 2, y, z - StoneGrovePiece.SIZE / 2);
        return Optional.of(new GenerationStub(origin, builder ->
                builder.addPiece(new StoneGrovePiece(DynastyStructures.STONE_GROVE_PIECE.get(), 0, origin))));
    }

    @Override
    public StructureType<?> type() {
        return DynastyStructures.STONE_GROVE.get();
    }
}
