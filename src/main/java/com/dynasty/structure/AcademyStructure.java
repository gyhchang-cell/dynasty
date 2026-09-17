package com.dynasty.structure;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;

import java.util.Optional;

/**
 * 国子监：陆地表层的书院院落（与科举联动的地方）。
 * Imperial Academy: the walled academy that the Keju examination points at.
 */
public class AcademyStructure extends Structure {

    public static final Codec<AcademyStructure> CODEC = simpleCodec(AcademyStructure::new);

    public AcademyStructure(StructureSettings settings) {
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
            return Optional.empty();                                   // 虚空里不生成 / never in the void
        }
        BlockPos origin = new BlockPos(x - AcademyPiece.SIZE / 2, y, z - AcademyPiece.SIZE / 2);
        return Optional.of(new GenerationStub(origin, builder ->
                builder.addPiece(new AcademyPiece(DynastyStructures.ACADEMY_PIECE.get(), 0, origin))));
    }

    @Override
    public StructureType<?> type() {
        return DynastyStructures.ACADEMY.get();
    }
}
