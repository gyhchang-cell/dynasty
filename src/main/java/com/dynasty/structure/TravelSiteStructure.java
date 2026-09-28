package com.dynasty.structure;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import java.util.Optional;

/** Small inhabited-looking stops, with no spawned patrols or ticking machines. */
public final class TravelSiteStructure extends Structure {
    public static final Codec<TravelSiteStructure> CODEC=RecordCodecBuilder.create(i -> i.group(
            settingsCodec(i),Codec.intRange(0,2).fieldOf("style").forGetter(s -> s.style)
    ).apply(i,TravelSiteStructure::new));
    private final int style;
    public TravelSiteStructure(StructureSettings settings,int style){super(settings);this.style=style;}
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx){
        int x=ctx.chunkPos().getMiddleBlockX(),z=ctx.chunkPos().getMiddleBlockZ();
        int y=ctx.chunkGenerator().getFirstFreeHeight(x,z,Heightmap.Types.WORLD_SURFACE_WG,ctx.heightAccessor(),ctx.randomState());
        if(!ctx.chunkGenerator().getBaseColumn(x,z,ctx.heightAccessor(),ctx.randomState()).getBlock(y-1).getFluidState().isEmpty())return Optional.empty();
        var origin=new BlockPos(x-15,y-1,z-15);
        return Optional.of(new GenerationStub(origin,b -> b.addPiece(new TravelSitePiece(origin,style))));
    }
    @Override public StructureType<?> type(){return DynastyStructures.TRAVEL_SITE.get();}
}
