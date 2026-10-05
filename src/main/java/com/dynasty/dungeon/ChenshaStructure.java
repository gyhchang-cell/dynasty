package com.dynasty.dungeon;

import com.mojang.serialization.Codec;
import com.dynasty.structure.megabuild.NaturalSculptures;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;
import java.nio.charset.StandardCharsets;
import java.util.Optional;
import java.util.UUID;

/** A deterministic three-storey tomb, scheduled as 24 independently clipped column pieces. */
public final class ChenshaStructure extends Structure {
    public static final Codec<ChenshaStructure> CODEC=simpleCodec(ChenshaStructure::new);
    public ChenshaStructure(StructureSettings settings){super(settings);}
    @Override public StructureType<?> type(){return DungeonContent.CHENSHA.get();}
    public static UUID instanceId(long seed,BlockPos origin){
        return UUID.nameUUIDFromBytes(("dynasty:chensha:"+seed+":"+origin.asLong()).getBytes(StandardCharsets.UTF_8));
    }
    public static boolean farFromSpawn(BlockPos corner,BlockPos spawn){
        // Nearest footprint point, rather than its centre, must clear the spawn exclusion circle.
        int x=Math.max(corner.getX(),Math.min(corner.getX()+63,spawn.getX()));
        int z=Math.max(corner.getZ(),Math.min(corner.getZ()+95,spawn.getZ()));
        return (long)(x-spawn.getX())*(x-spawn.getX())+(long)(z-spawn.getZ())*(z-spawn.getZ())>=2500L*2500;
    }
    @Override protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx){
        if(!(ctx.heightAccessor() instanceof ServerLevelAccessor accessor)||accessor.getLevel().dimension()!=Level.OVERWORLD)return Optional.empty();
        int x=ctx.chunkPos().getMinBlockX(),z=ctx.chunkPos().getMinBlockZ();
        var corner=new BlockPos(x,0,z);
        if(!farFromSpawn(corner,accessor.getLevel().getSharedSpawnPos()))return Optional.empty();
        // Nine bounded noise-column samples. No neighbouring chunk queries or tickets.
        int low=Integer.MAX_VALUE,high=Integer.MIN_VALUE;
        for(int dx:new int[]{8,32,56})for(int dz:new int[]{8,48,88}){
            int y=ctx.chunkGenerator().getFirstFreeHeight(x+dx,z+dz,Heightmap.Types.OCEAN_FLOOR_WG,ctx.heightAccessor(),ctx.randomState());
            low=Math.min(low,y);high=Math.max(high,y);
        }
        boolean flat=ctx.chunkGenerator() instanceof net.minecraft.world.level.levelgen.FlatLevelSource;
        if(high-low>20||!flat&&low<ctx.chunkGenerator().getSeaLevel()||high+8>=ctx.heightAccessor().getMaxBuildHeight()
                ||high-72<ctx.heightAccessor().getMinBuildHeight()+4)return Optional.empty();
        if(!clearOfReservedSites(ctx,x,z))return Optional.empty();
        BlockPos origin=new BlockPos(x,high-72,z);UUID instance=instanceId(ctx.seed(),origin);
        return Optional.of(new GenerationStub(origin.offset(32,72,4),builder->{
            for(int cx=0;cx<4;cx++)for(int cz=0;cz<6;cz++)builder.addPiece(new ChenshaPiece(origin,cx,cz,instance));
        }));
    }
    private static boolean clearOfReservedSites(GenerationContext ctx,int x,int z){
        // The existing huge-dragon/manor footprints can straddle their 625-chunk site cell.
        for(int dx:new int[]{-600,0,600})for(int dz:new int[]{-600,0,600}){
            var site=NaturalSculptures.site(ctx.seed(),(x+dx)>>4,(z+dz)>>4);
            if(site.x()+400>=x-96&&site.x()-400<=x+159&&site.z()+400>=z-96&&site.z()-400<=z+191)return false;
        }
        for(var set:ctx.registryAccess().registryOrThrow(Registries.STRUCTURE_SET)){
            if(!(set.placement() instanceof RandomSpreadStructurePlacement spread)||spread instanceof NaturalSculptures.Placement
                    ||set.structures().stream().anyMatch(e->e.structure().value() instanceof ChenshaStructure))continue;
            int minX=(x-128)>>4,maxX=(x+191)>>4,minZ=(z-128)>>4,maxZ=(z+223)>>4;
            for(int rx=Math.floorDiv(minX,spread.spacing());rx<=Math.floorDiv(maxX,spread.spacing());rx++)
                for(int rz=Math.floorDiv(minZ,spread.spacing());rz<=Math.floorDiv(maxZ,spread.spacing());rz++){
                    var candidate=spread.getPotentialStructureChunk(ctx.seed(),rx*spread.spacing(),rz*spread.spacing());
                    if(candidate.x>=minX&&candidate.x<=maxX&&candidate.z>=minZ&&candidate.z<=maxZ)return false;
                }
        }
        return true;
    }
}
