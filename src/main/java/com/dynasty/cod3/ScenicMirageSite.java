package com.dynasty.cod3;

import net.minecraft.core.BlockPos;
import net.minecraft.tags.BiomeTags;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import javax.annotation.Nullable;

/** Read-only loaded desert ground for the 44x32m phantom street. Never places its NBT. */
public final class ScenicMirageSite {
    public static double visibility(Level level){
        if(!level.dimension().equals(Level.OVERWORLD)||level.getRainLevel(1)>.01f)return 0;
        long t=Math.floorMod(level.getDayTime(),24000);
        return t<16000||t>=22000?0:Math.min(1,Math.min((t-16000)/60.,(22000-t)/60.));
    }
    public static boolean desert(Level level,BlockPos at){var b=level.getBiome(at);return b.is(Biomes.DESERT)||b.is(BiomeTags.IS_BADLANDS);}
    @Nullable public static Vec3 find(Level level,Vec3 near){
        if(visibility(level)<=0)return null;
        for(int radius:new int[]{0,16,32})for(int side=0;side<(radius==0?1:4);side++){
            int x=(int)Math.floor(near.x)+(side<2?(side==0?radius:-radius):0);
            int z=(int)Math.floor(near.z)+(side>=2?(side==2?radius:-radius):0);
            if(!level.hasChunkAt(new BlockPos(x,0,z)))continue;
            int y=level.getHeight(Heightmap.Types.MOTION_BLOCKING,x,z);
            var o=new Vec3(x,y,z);if(!desert(level,BlockPos.containing(o)))continue;
            int min=y;boolean loaded=true;
            for(int dx=-22;dx<=21&&loaded;dx++)for(int dz=-16;dz<=15;dz++){
                var at=new BlockPos(x+dx,y,z+dz);if(!level.hasChunkAt(at)){loaded=false;break;}
                min=Math.min(min,level.getHeight(Heightmap.Types.MOTION_BLOCKING,at.getX(),at.getZ()));
            }
            if(loaded){o=new Vec3(x,min,z);if(valid(level,o))return o;}
        }
        return null;
    }
    public static boolean valid(Level level,Vec3 o){
        if(!Double.isFinite(o.lengthSqr())||!level.dimension().equals(Level.OVERWORLD))return false;
        var center=BlockPos.containing(o);if(!level.hasChunkAt(center)||!desert(level,center))return false;
        // Exact full footprint: small height variation can bury the base, never float a shop.
        for(int dx=-22;dx<=21;dx++)for(int dz=-16;dz<=15;dz++){
            var at=center.offset(dx,0,dz);if(!level.hasChunkAt(at))return false;
            int h=level.getHeight(Heightmap.Types.MOTION_BLOCKING,at.getX(),at.getZ());
            if(h<o.y||h>o.y+2)return false;
            var floor=new BlockPos(at.getX(),h-1,at.getZ());
            if(!level.getFluidState(floor).isEmpty()||!level.getBlockState(floor).isFaceSturdy(level,floor,net.minecraft.core.Direction.UP))return false;
        }
        return true;
    }
    public static double alpha(double age,int duration,double distance,double visibility){
        return .60*visibility*ScenicAurora.envelope(age,duration,distance)*Math.max(0,Math.min(1,(distance-24)/16))*Math.max(0,Math.min(1,(160-distance)/32));
    }
    public static double soundVolume(double age,int duration,double distance,double visibility){return .04*visibility*ScenicAurora.envelope(age,duration,distance)*Math.max(0,Math.min(1,(64-distance)/24));}
    private ScenicMirageSite(){}
}
