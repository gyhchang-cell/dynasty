package com.dynasty.blueprint.boss;
import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.*;
import java.util.Optional;

public final class StargazerPlatformStructure extends Structure {
    public static final Codec<StargazerPlatformStructure> CODEC=simpleCodec(StargazerPlatformStructure::new);
    public StargazerPlatformStructure(StructureSettings s){super(s);}
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext c){int x=c.chunkPos().getMiddleBlockX(),z=c.chunkPos().getMiddleBlockZ();if(c.heightAccessor().getMaxBuildHeight()<=268||c.heightAccessor().getMinBuildHeight()>=196)return Optional.empty();for(int dx:new int[]{-17,0,17})for(int dz:new int[]{-17,0,17}){int height=c.chunkGenerator().getFirstFreeHeight(x+dx,z+dz,Heightmap.Types.WORLD_SURFACE_WG,c.heightAccessor(),c.randomState());if(height<50||height>160)return Optional.empty();}var at=new BlockPos(x-17,199,z-17);int ground=c.chunkGenerator().getFirstFreeHeight(x,z-18,Heightmap.Types.WORLD_SURFACE_WG,c.heightAccessor(),c.randomState());if(ground<50||ground>160)return Optional.empty();return Optional.of(new GenerationStub(at,b->{b.addPiece(new StargazerPlatformPiece(at));b.addPiece(new StargazerApproachPiece(new BlockPos(x,ground,z-18)));}));}
    @Override public StructureType<?> type(){return WoodKiteContent.PLATFORM_TYPE.get();}
}
