package com.dynasty.dungeon;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import java.nio.charset.StandardCharsets;
import java.util.Optional;
import java.util.UUID;

/** First-stage three-piece connectivity probe; deliberately absent from natural placement. */
public final class DungeonProbeStructure extends Structure {
    public static final Codec<DungeonProbeStructure> CODEC=simpleCodec(DungeonProbeStructure::new);
    public DungeonProbeStructure(StructureSettings settings){super(settings);}
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx){
        int x=ctx.chunkPos().getMinBlockX(),z=ctx.chunkPos().getMinBlockZ();
        int y=ctx.chunkGenerator().getFirstFreeHeight(x+6,z+8,Heightmap.Types.WORLD_SURFACE_WG,ctx.heightAccessor(),ctx.randomState());
        if(y<ctx.heightAccessor().getMinBuildHeight()+2||y+7>=ctx.heightAccessor().getMaxBuildHeight())return Optional.empty();
        BlockPos origin=new BlockPos(x,y,z);
        UUID instance=instanceId(ctx.seed(),origin);
        return Optional.of(new GenerationStub(origin,builder->{for(int part=0;part<3;part++)builder.addPiece(new DungeonProbePiece(origin,part,instance));}));
    }
    static UUID instanceId(long seed,BlockPos origin){return UUID.nameUUIDFromBytes(("dynasty:probe:"+seed+":"+origin.asLong()).getBytes(StandardCharsets.UTF_8));}
    @Override public StructureType<?> type(){return DungeonContent.PROBE.get();}
}
