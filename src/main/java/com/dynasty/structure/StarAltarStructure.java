package com.dynasty.structure;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;

import java.util.Optional;

/**
 * 观星台：九霄天界的五层祭台（八卦立柱 + 星图）。
 * Star Altar: the five-tiered observatory platform of the nine heavens.
 */
public class StarAltarStructure extends Structure {

    public static final Codec<StarAltarStructure> CODEC = simpleCodec(StarAltarStructure::new);

    public StarAltarStructure(StructureSettings settings) {
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
        BlockPos origin = new BlockPos(x - StarAltarPiece.SIZE / 2, y, z - StarAltarPiece.SIZE / 2);
        return Optional.of(new GenerationStub(origin, builder ->
                builder.addPiece(new StarAltarPiece(DynastyStructures.STAR_ALTAR_PIECE.get(), 0, origin))));
    }

    @Override
    public StructureType<?> type() {
        return DynastyStructures.STAR_ALTAR.get();
    }
}
