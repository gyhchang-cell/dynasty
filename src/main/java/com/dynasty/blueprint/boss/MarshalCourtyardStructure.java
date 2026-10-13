package com.dynasty.blueprint.boss;
import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.*;
import java.util.Optional;

public final class MarshalCourtyardStructure extends Structure {
    public static final Codec<MarshalCourtyardStructure> CODEC=simpleCodec(MarshalCourtyardStructure::new);
    public MarshalCourtyardStructure(StructureSettings s){super(s);}
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext c){int x=c.chunkPos().getMiddleBlockX(),z=c.chunkPos().getMiddleBlockZ(),y=height(c,x,z);if(y<c.heightAccessor().getMinBuildHeight()+4||y+17>=c.heightAccessor().getMaxBuildHeight())return Optional.empty();for(int dx:new int[]{-16,0,16})for(int dz:new int[]{-16,0,16}){int h=height(c,x+dx,z+dz);if(Math.abs(h-y)>3||!c.chunkGenerator().getBaseColumn(x+dx,z+dz,c.heightAccessor(),c.randomState()).getBlock(h-1).getFluidState().isEmpty())return Optional.empty();}var origin=new BlockPos(x-16,y-1,z-16);return Optional.of(new GenerationStub(origin,b->b.addPiece(new MarshalCourtyardPiece(origin))));}
    private static int height(GenerationContext c,int x,int z){return c.chunkGenerator().getFirstFreeHeight(x,z,Heightmap.Types.WORLD_SURFACE_WG,c.heightAccessor(),c.randomState());}
    @Override public StructureType<?> type(){return BlindMarshalContent.YARD_TYPE.get();}
}
