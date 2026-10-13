package com.dynasty.blueprint.artifact;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.*;
import java.util.Optional;

public final class TaiqingTempleStructure extends Structure {
    public static final Codec<TaiqingTempleStructure> CODEC=simpleCodec(TaiqingTempleStructure::new);
    public TaiqingTempleStructure(StructureSettings settings){super(settings);}
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext c){
        int x=c.chunkPos().getMiddleBlockX(),z=c.chunkPos().getMiddleBlockZ(),lo=Integer.MAX_VALUE,hi=Integer.MIN_VALUE;
        for(int dx:new int[]{-10,0,10})for(int dz:new int[]{-10,0,10}){
            int h=c.chunkGenerator().getFirstFreeHeight(x+dx,z+dz,Heightmap.Types.WORLD_SURFACE_WG,c.heightAccessor(),c.randomState());lo=Math.min(lo,h);hi=Math.max(hi,h);
        }
        if(lo<60||hi>160||hi-lo>5||lo<c.heightAccessor().getMinBuildHeight()+8||hi+10>=c.heightAccessor().getMaxBuildHeight())return Optional.empty();
        var origin=new BlockPos(x-10,hi-6,z-10);return Optional.of(new GenerationStub(origin,b->b.addPiece(new TaiqingTemplePiece(origin))));
    }
    @Override public StructureType<?> type(){return TaiqingContent.TEMPLE.get();}
}
