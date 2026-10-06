package com.dynasty.structure;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import java.util.Optional;

/** Overworld ruined camp. Its structure start owns the existing blueprint encounter marker. */
public final class BattlefieldStructure extends Structure {
    public static final Codec<BattlefieldStructure> CODEC=simpleCodec(BattlefieldStructure::new);
    public BattlefieldStructure(StructureSettings settings){super(settings);}
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx){
        int x=ctx.chunkPos().getMiddleBlockX(),z=ctx.chunkPos().getMiddleBlockZ();
        int y=height(ctx,x,z);
        for(int dx:new int[]{-16,0,16})for(int dz:new int[]{-16,0,16}){
            int sample=height(ctx,x+dx,z+dz);
            if(Math.abs(sample-y)>3||!ctx.chunkGenerator().getBaseColumn(x+dx,z+dz,ctx.heightAccessor(),ctx.randomState())
                    .getBlock(sample-1).getFluidState().isEmpty())return Optional.empty();
        }
        var origin=new BlockPos(x-16,y-1,z-16);
        return Optional.of(new GenerationStub(origin,b->b.addPiece(new BattlefieldPiece(origin))));
    }
    private static int height(GenerationContext ctx,int x,int z){
        return ctx.chunkGenerator().getFirstFreeHeight(x,z,Heightmap.Types.WORLD_SURFACE_WG,ctx.heightAccessor(),ctx.randomState());
    }
    @Override public StructureType<?> type(){return DynastyStructures.BATTLEFIELD.get();}
}
