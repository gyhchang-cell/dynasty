package com.dynasty.structure;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.*;
import java.util.Optional;

/** Gives existing building generators real structure starts, making them locatable. */
public final class LegacyBuildingStructure extends Structure {
    public static final Codec<LegacyBuildingStructure> CODEC=RecordCodecBuilder.create(i->i.group(settingsCodec(i),ResourceLocation.CODEC.fieldOf("feature").forGetter(s->s.feature)).apply(i,LegacyBuildingStructure::new));
    final ResourceLocation feature;
    public LegacyBuildingStructure(StructureSettings s,ResourceLocation f){super(s);feature=f;}
    protected Optional<GenerationStub> findGenerationPoint(GenerationContext c){
        int x=c.chunkPos().getMiddleBlockX(),z=c.chunkPos().getMiddleBlockZ();
        int y=c.chunkGenerator().getFirstFreeHeight(x,z,Heightmap.Types.WORLD_SURFACE_WG,c.heightAccessor(),c.randomState());
        if(y<=c.chunkGenerator().getSeaLevel()+2 || y+70>=c.heightAccessor().getMaxBuildHeight())return Optional.empty();
        if(!c.chunkGenerator().getBaseColumn(x,z,c.heightAccessor(),c.randomState()).getBlock(y-1).getFluidState().isEmpty())return Optional.empty();
        var p=new BlockPos(x,y,z);long seed=c.random().nextLong();
        return Optional.of(new GenerationStub(p,b->b.addPiece(new LegacyBuildingPiece(p,feature,seed))));
    }
    public StructureType<?> type(){return DynastyStructures.LEGACY_BUILDING.get();}
}
