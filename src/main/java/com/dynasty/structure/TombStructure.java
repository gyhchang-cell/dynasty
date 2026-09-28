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
        int surface=ctx.chunkGenerator().getFirstFreeHeight(x+19,z+3,net.minecraft.world.level.levelgen.Heightmap.Types.WORLD_SURFACE_WG,ctx.heightAccessor(),ctx.randomState());
        return Optional.of(new GenerationStub(new BlockPos(x+19,surface,z+3), builder -> {
                builder.addPiece(new TombPiece(DynastyStructures.TOMB_PIECE.get(), 0, origin));
                builder.addPiece(new TombAccessPiece(origin.offset(17,1,1),Math.max(y+17,surface)));
        }));
    }

    @Override
    public StructureType<?> type() {
        return DynastyStructures.IMPERIAL_TOMB.get();
    }
}
