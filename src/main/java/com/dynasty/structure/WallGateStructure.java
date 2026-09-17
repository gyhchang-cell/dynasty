package com.dynasty.structure;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;

import java.util.Optional;

/**
 * 长城关隘：一段带城楼与角楼的城墙横在地表。
 * Great Wall Gate: a wall segment with a gate tower and two flanking turrets.
 */
public class WallGateStructure extends Structure {

    public static final Codec<WallGateStructure> CODEC = simpleCodec(WallGateStructure::new);

    public WallGateStructure(StructureSettings settings) {
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
        BlockPos origin = new BlockPos(x - WallGatePiece.SIZE / 2, y, z - WallGatePiece.LENGTH / 2);
        return Optional.of(new GenerationStub(origin, builder ->
                builder.addPiece(new WallGatePiece(DynastyStructures.WALL_GATE_PIECE.get(), 0, origin))));
    }

    @Override
    public StructureType<?> type() {
        return DynastyStructures.GREAT_WALL_GATE.get();
    }
}
