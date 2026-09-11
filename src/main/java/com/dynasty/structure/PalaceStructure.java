package com.dynasty.structure;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;

import java.util.Optional;

/**
 * 皇家宫殿结构：在陆地表层生成完整的宫殿建筑群（台基 + 城墙 + 角楼 + 太和殿 + 御花园）。
 * Imperial Palace structure: a full palace complex (terrace, walls, corner towers, main hall, garden).
 */
public class PalaceStructure extends Structure {

    public static final Codec<PalaceStructure> CODEC = simpleCodec(PalaceStructure::new);

    public PalaceStructure(StructureSettings settings) {
        super(settings);
    }

    @Override
    protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx) {
        ChunkPos chunkPos = ctx.chunkPos();
        int x = chunkPos.getMiddleBlockX();
        int z = chunkPos.getMiddleBlockZ();
        int y = ctx.chunkGenerator().getFirstFreeHeight(x, z, Heightmap.Types.WORLD_SURFACE_WG,
                ctx.heightAccessor(), ctx.randomState());
        // 不在水面/海底生成 / never spawn under water
        if (y <= ctx.chunkGenerator().getSeaLevel() + 1) {
            return Optional.empty();
        }
        BlockPos origin = new BlockPos(x - 24, y - 2, z - 24);
        return Optional.of(new GenerationStub(origin, builder -> {
            PalacePiece piece = new PalacePiece(DynastyStructures.PALACE_PIECE.get(), 0, origin);
            builder.addPiece(piece);
            piece.addChildren(piece, builder, ctx.random());
        }));
    }

    @Override
    public StructureType<?> type() {
        return DynastyStructures.PALACE.get();
    }
}
