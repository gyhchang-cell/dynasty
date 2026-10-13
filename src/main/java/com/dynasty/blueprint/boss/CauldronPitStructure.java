package com.dynasty.blueprint.boss;
import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.*;
import java.util.Optional;

/** Authored forty-metre sunken battle pit, limited to dry, nearly flat overworld terrain. */
public final class CauldronPitStructure extends Structure {
    public static final Codec<CauldronPitStructure> CODEC=simpleCodec(CauldronPitStructure::new);
    public CauldronPitStructure(StructureSettings settings){super(settings);}
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx){int x=ctx.chunkPos().getMiddleBlockX(),z=ctx.chunkPos().getMiddleBlockZ();int y=height(ctx,x,z);if(y<ctx.heightAccessor().getMinBuildHeight()+16||y+10>=ctx.heightAccessor().getMaxBuildHeight())return Optional.empty();for(int dx:new int[]{-20,0,20})for(int dz:new int[]{-20,0,20}){int sample=height(ctx,x+dx,z+dz);if(Math.abs(sample-y)>3||!ctx.chunkGenerator().getBaseColumn(x+dx,z+dz,ctx.heightAccessor(),ctx.randomState()).getBlock(sample-1).getFluidState().isEmpty())return Optional.empty();}var origin=new BlockPos(x-21,y-8,z-21);return Optional.of(new GenerationStub(origin,b->b.addPiece(new CauldronPitPiece(origin))));}
    private static int height(GenerationContext ctx,int x,int z){return ctx.chunkGenerator().getFirstFreeHeight(x,z,Heightmap.Types.WORLD_SURFACE_WG,ctx.heightAccessor(),ctx.randomState());}
    @Override public StructureType<?> type(){return CauldronPitContent.PIT_TYPE.get();}
}
