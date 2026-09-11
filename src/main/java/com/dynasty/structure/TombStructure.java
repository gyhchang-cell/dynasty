package com.dynasty.structure;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;

import java.util.Optional;

/**
 * 帝陵地宫结构：地下深处生成墓道 + 耳室 + 主墓室。
 * Imperial Mausoleum structure: underground corridors, side chambers and a burial chamber.
 */
public class TombStructure extends Structure {

    public static final Codec<TombStructure> CODEC = simpleCodec(TombStructure::new);

    public TombStructure(StructureSettings settings) {
        super(settings);
    }

    @Override
    protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx) {
        ChunkPos chunkPos = ctx.chunkPos();
        int x = chunkPos.getMiddleBlockX() - 16;
        int z = chunkPos.getMiddleBlockZ() - 16;
        int minY = ctx.heightAccessor().getMinBuildHeight();
        int y = Math.max(minY + 18, -20);
        BlockPos origin = new BlockPos(x, y, z);
        return Optional.of(new GenerationStub(origin, builder ->
                builder.addPiece(new TombPiece(DynastyStructures.TOMB_PIECE.get(), 0, origin))));
    }

    @Override
    public StructureType<?> type() {
        return DynastyStructures.IMPERIAL_TOMB.get();
    }
}
