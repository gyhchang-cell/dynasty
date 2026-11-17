package com.dynasty.cod3;

import net.minecraft.core.*;
import net.minecraft.world.level.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import javax.annotation.Nullable;

/** The full procession route must be loaded, flat and dry: no AI, terrain writes or floating feet. */
public final class ScenicGhostArmySite {
    public static final int SOLDIERS=24;
    public static double visibility(Level level){return level.dimension().equals(Level.OVERWORLD)?level.getRainLevel(1):0;}
    @Nullable public static Vec3 find(Level level,Vec3 near){
        if(visibility(level)<=0||level instanceof ServerLevel server&&!ScenicGreatWallSite.battlefieldNear(server,near))return null;
        for(int radius:new int[]{0,16,32})for(int side=0;side<(radius==0?1:4);side++){
            int x=(int)Math.floor(near.x)+(side<2?(side==0?radius:-radius):0),z=(int)Math.floor(near.z)+(side>=2?(side==2?radius:-radius):0);
            if(!level.hasChunkAt(new BlockPos(x,0,z)))continue;
            var origin=new Vec3(x,level.getHeight(Heightmap.Types.MOTION_BLOCKING,x,z),z);
            if(valid(level,origin)&&(!(level instanceof ServerLevel server)||ScenicGreatWallSite.battlefieldNear(server,origin)))return origin;
        }
        return null;
    }
    public static boolean valid(Level level,Vec3 origin){
        if(!Double.isFinite(origin.lengthSqr())||!level.dimension().equals(Level.OVERWORLD)||origin.x!=Math.floor(origin.x)||origin.y!=Math.floor(origin.y)||origin.z!=Math.floor(origin.z))return false;
        var center=BlockPos.containing(origin);
        for(int x=-9;x<=9;x++)for(int z=-14;z<=14;z++){
            var at=center.offset(x,0,z);if(!level.hasChunkAt(at))return false;
            if(level.getHeight(Heightmap.Types.MOTION_BLOCKING,at.getX(),at.getZ())!=center.getY())return false;
            var floor=at.below();if(!level.getFluidState(floor).isEmpty()||!level.getBlockState(floor).isFaceSturdy(level,floor,Direction.UP))return false;
        }
        return true;
    }
    /** Fixed world +Z route, 0.8m per 4s gait cycle; all instance clocks are absolute packet age. */
    public static Vec3 position(Vec3 origin,int soldier,double age){
        if(soldier<0||soldier>=SOLDIERS)throw new IllegalArgumentException("soldier");
        return origin.add((soldier%6-2.5)*2.8,0,(soldier/6-1.5)*3.4+(age*.01-6));
    }
    public static double alpha(double age,int duration,double distance,double visibility){return .48*visibility*ScenicAurora.envelope(age,duration,distance)*Math.max(0,Math.min(1,(distance-16)/8))*Math.max(0,Math.min(1,(224-distance)/48));}
    public static double farBlend(double distance,boolean minimal){return minimal?1:Math.max(0,Math.min(1,(distance-80)/24));}
    private ScenicGhostArmySite(){}
}
