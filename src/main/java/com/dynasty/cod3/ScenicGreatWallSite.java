package com.dynasty.cod3;

import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.phys.Vec3;
import javax.annotation.Nullable;
import java.util.*;

/** Loaded battlefield neighbourhood and dry ground only; never places a phantom block. */
public final class ScenicGreatWallSite {
    public static double visibility(Level level){
        if(!level.dimension().equals(Level.OVERWORLD))return 0;
        long t=Math.floorMod(level.getDayTime(),24000);
        return t>=2500?0:level.getRainLevel(1)*Math.min(1,(2500-t)/60.);
    }
    public static boolean battlefieldNear(ServerLevel level,Vec3 near){
        if(!level.dimension().equals(Level.OVERWORLD))return false;
        var structure=level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(ResourceLocation.fromNamespaceAndPath("dynasty","ruined_battlefield"));
        if(structure==null)return false;
        int cx=((int)Math.floor(near.x))>>4,cz=((int)Math.floor(near.z))>>4;
        var visited=new HashSet<Long>();
        for(int dx=-8;dx<=8;dx++)for(int dz=-8;dz<=8;dz++){
            var chunk=level.getChunkSource().getChunkNow(cx+dx,cz+dz);if(chunk==null)continue;
            var starts=new ArrayList<StructureStart>();var own=chunk.getStartForStructure(structure);if(own!=null)starts.add(own);
            for(long ref:chunk.getReferencesForStructure(structure))if(visited.add(ref)){
                var source=level.getChunkSource().getChunkNow(ChunkPos.getX(ref),ChunkPos.getZ(ref));
                if(source!=null){var start=source.getStartForStructure(structure);if(start!=null)starts.add(start);}
            }
            for(var start:starts)if(start.isValid()){
                var b=start.getBoundingBox();double x=Math.max(b.minX()-near.x,Math.max(0,near.x-b.maxX())),z=Math.max(b.minZ()-near.z,Math.max(0,near.z-b.maxZ()));
                if(x*x+z*z<=128*128)return true;
            }
        }
        return false;
    }
    @Nullable public static Vec3 find(Level level,Vec3 near){
        if(visibility(level)<=0)return null;
        if(level instanceof ServerLevel server&&!battlefieldNear(server,near))return null;
        for(int radius:new int[]{0,16,32,48})for(int side=0;side<(radius==0?1:4);side++){
            int x=(int)Math.floor(near.x)+(side<2?(side==0?radius:-radius):0);
            int z=(int)Math.floor(near.z)+(side>=2?(side==2?radius:-radius):0);
            int min=Integer.MAX_VALUE;boolean loaded=true;
            for(int dx=-32;dx<32&&loaded;dx++)for(int dz=-16;dz<12;dz++){
                var at=new BlockPos(x+dx,0,z+dz);if(!level.hasChunkAt(at)){loaded=false;break;}
                min=Math.min(min,level.getHeight(Heightmap.Types.MOTION_BLOCKING,at.getX(),at.getZ()));
            }
            if(loaded){var o=new Vec3(x,min,z);if(valid(level,o)&&(!(level instanceof ServerLevel server)||battlefieldNear(server,o)))return o;}
        }
        return null;
    }
    public static boolean valid(Level level,Vec3 origin){
        if(!Double.isFinite(origin.lengthSqr())||!level.dimension().equals(Level.OVERWORLD)||origin.x!=Math.floor(origin.x)||origin.y!=Math.floor(origin.y)||origin.z!=Math.floor(origin.z))return false;
        var center=BlockPos.containing(origin);
        for(int dx=-32;dx<32;dx++)for(int dz=-16;dz<12;dz++){
            var at=center.offset(dx,0,dz);if(!level.hasChunkAt(at))return false;
            int h=level.getHeight(Heightmap.Types.MOTION_BLOCKING,at.getX(),at.getZ());if(h<origin.y||h>origin.y+2)return false;
            var floor=new BlockPos(at.getX(),h-1,at.getZ());
            if(!level.getFluidState(floor).isEmpty()||!level.getBlockState(floor).isFaceSturdy(level,floor,Direction.UP))return false;
        }
        return true;
    }
    public static double alpha(double age,int duration,double distance,double visibility){return .52*visibility*ScenicAurora.envelope(age,duration,distance)*Math.max(0,Math.min(1,(distance-24)/16))*Math.max(0,Math.min(1,(224-distance)/48));}
    public static double soundVolume(double age,int duration,double distance,double visibility){return .035*visibility*ScenicAurora.envelope(age,duration,distance)*Math.max(0,1-distance/128);}
    public static double farBlend(double distance,boolean minimal){return minimal?1:Math.max(0,Math.min(1,(distance-88)/24));}
    private ScenicGreatWallSite(){}
}
