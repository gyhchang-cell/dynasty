package com.dynasty.dungeon;

import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;
import java.nio.charset.StandardCharsets;
import java.util.Optional;
import java.util.UUID;

/** The existing underworld's enclosed ghost city, generated in 48 clipped columns. */
public final class WangsiStructure extends Structure {
    public static final Codec<WangsiStructure> CODEC=simpleCodec(WangsiStructure::new);
    public WangsiStructure(StructureSettings settings){super(settings);}
    @Override public StructureType<?> type(){return DungeonContent.WANGSI.get();}
    public static UUID instanceId(long seed,BlockPos origin){
        return UUID.nameUUIDFromBytes(("dynasty:wangsi:"+seed+":"+origin.asLong()).getBytes(StandardCharsets.UTF_8));
    }
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx){
        var level=ChenshaStructure.generationLevel(ctx);
        if(level==null||!level.dimension().location().toString().equals("dynasty:underworld"))return Optional.empty();
        int x=ctx.chunkPos().getMinBlockX(),z=ctx.chunkPos().getMinBlockZ();
        var spawn=level.getSharedSpawnPos();
        long sx=Math.max(x,Math.min(x+95,spawn.getX()))-(long)spawn.getX();
        long sz=Math.max(z,Math.min(z+127,spawn.getZ()))-(long)spawn.getZ();
        if(sx*sx+sz*sz<2500L*2500)return Optional.empty();
        int low=Integer.MAX_VALUE,high=Integer.MIN_VALUE;
        for(int dx:new int[]{8,48,88})for(int dz:new int[]{8,64,120}){
            int y=ctx.chunkGenerator().getFirstFreeHeight(x+dx,z+dz,Heightmap.Types.OCEAN_FLOOR_WG,ctx.heightAccessor(),ctx.randomState());
            low=Math.min(low,y);high=Math.max(high,y);
        }
        if(high-low>24||low<ctx.chunkGenerator().getSeaLevel()+2||high-40<ctx.heightAccessor().getMinBuildHeight()+4
                ||high+8>=ctx.heightAccessor().getMaxBuildHeight())return Optional.empty();
        // Reserve existing Dynasty structure slots without loading their chunks.
        // This dimension has no sculpture tile placement; it keeps all its older landmarks.
        var placements=level.getChunkSource().getGeneratorState();
        for(var holder:placements.possibleStructureSets()){
            if(holder.unwrapKey().map(k->!k.location().getNamespace().equals("dynasty")).orElse(true))continue;
            var set=holder.value();
            if(!(set.placement() instanceof RandomSpreadStructurePlacement spread)
                    ||set.structures().stream().anyMatch(e->e.structure().value() instanceof WangsiStructure))continue;
            int minX=(x-48)>>4,maxX=(x+143)>>4,minZ=(z-48)>>4,maxZ=(z+175)>>4;
            for(int rx=Math.floorDiv(minX,spread.spacing());rx<=Math.floorDiv(maxX,spread.spacing());rx++)
                for(int rz=Math.floorDiv(minZ,spread.spacing());rz<=Math.floorDiv(maxZ,spread.spacing());rz++){
                    var p=spread.getPotentialStructureChunk(ctx.seed(),rx*spread.spacing(),rz*spread.spacing());
                    if(p.x>=minX&&p.x<=maxX&&p.z>=minZ&&p.z<=maxZ&&spread.isStructureChunk(placements,p.x,p.z))return Optional.empty();
                }
        }
        BlockPos origin=new BlockPos(x,high-40,z);UUID instance=instanceId(ctx.seed(),origin);
        return Optional.of(new GenerationStub(origin.offset(48,41,3),builder->{
            for(int cx=0;cx<6;cx++)for(int cz=0;cz<8;cz++)builder.addPiece(new WangsiPiece(origin,cx,cz,instance));
        }));
    }
}
