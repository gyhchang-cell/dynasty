package com.dynasty.cod3;

import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import javax.annotation.Nullable;

/** Loaded terrain only. The long hull must have an actual continuous liquid course. */
public final class ScenicGhostShipRoute {
    public record Route(Vec3 origin,Vec3 direction){}
    public static boolean dimension(String id){return id.equals("minecraft:overworld")||id.equals("dynasty:underworld");}
    public static double visibility(Level level){
        long t=Math.floorMod(level.getDayTime(),24000);if(t<13000||t>=23000)return 0;
        String id=level.dimension().location().toString();if(!dimension(id))return 0;
        // Soul River already has the End dimension's permanent fog and no rain system.
        if(id.equals("minecraft:overworld")&&level.getRainLevel(1)<.5f)return 0;
        return Math.min(1,Math.min((t-13000)/60.,(23000-t)/60.));
    }
    private static boolean liquid(Level level,BlockPos p){
        var fluid=level.getFluidState(p);
        if(!fluid.isSource())return false;
        if(fluid.is(FluidTags.WATER))return true;
        // Existing Soul River uses lava as its default fluid. Do not replace its terrain.
        return level.dimension().location().toString().equals("dynasty:underworld")
            &&level.getBiome(p).is(new net.minecraft.resources.ResourceLocation("dynasty","soul_river"))&&fluid.is(FluidTags.LAVA);
    }
    @Nullable public static Route find(Level level,Vec3 near){
        if(visibility(level)<=0)return null;
        for(int radius:new int[]{0,16,32})for(int side=0;side<(radius==0?1:4);side++){
            int dx=side<2?(side==0?radius:-radius):0,dz=side>=2?(side==2?radius:-radius):0;
            var column=BlockPos.containing(near.add(dx,0,dz));if(!level.hasChunkAt(column))continue;
            int y=level.getHeight(Heightmap.Types.MOTION_BLOCKING,column.getX(),column.getZ());
            var top=new BlockPos(column.getX(),y-1,column.getZ());if(!liquid(level,top))continue;
            double height=top.getY()+level.getFluidState(top).getHeight(level,top);
            Vec3 origin=new Vec3(column.getX()+.5,height,column.getZ()+.5);
            for(var direction:new Vec3[]{new Vec3(0,0,1),new Vec3(1,0,0)}){
                var route=new Route(origin,direction);if(valid(level,route))return route;
            }
        }
        return null;
    }
    @Nullable public static Route nearObserver(Level level,Vec3 position,Vec3 look){
        var forward=look.multiply(1,0,1).normalize();
        var route=find(level,position.add(forward.scale(48)));
        return route!=null?route:find(level,position);
    }
    public static boolean valid(Level level,Route route){
        var o=route.origin();var f=route.direction();
        if(!Double.isFinite(o.lengthSqr())||!(f.equals(new Vec3(0,0,1))||f.equals(new Vec3(1,0,0))))return false;
        var right=new Vec3(f.z,0,-f.x);int topY=BlockPos.containing(o).getY();
        // 32m drift + 24m hull, with 12m beam/rig clearance. No chunk loads or tickets.
        for(int z=-28;z<=28;z++)for(int x=-6;x<=6;x++){
            var at=BlockPos.containing(o.add(f.scale(z)).add(right.scale(x)));
            if(!level.hasChunkAt(at)||!liquid(level,at)||!liquid(level,at.below()))return false;
            double surface=topY+level.getFluidState(at).getHeight(level,at);
            if(Math.abs(surface-o.y)>.02)return false;
            // A source-liquid heightmap top also excludes single-block obstacles and overhangs.
            if(level.getHeight(Heightmap.Types.MOTION_BLOCKING,at.getX(),at.getZ())!=topY+1)return false;
        }
        return true;
    }
    public static Vec3 position(Cod3VisualPacket p,double age){return p.origin().add(p.direction().scale((age/p.duration()-.5)*32));}
    public static double alpha(Cod3VisualPacket p,double age,double distance,double visibility){
        return .86*visibility*ScenicAurora.envelope(age,p.duration(),distance)*Math.max(0,Math.min(1,(distance-6)/4));
    }
    public static double soundVolume(Cod3VisualPacket p,double age,double distance,double visibility){return .06*visibility*ScenicAurora.envelope(age,p.duration(),distance)*Math.max(0,Math.min(1,(40-distance)/20));}
    private ScenicGhostShipRoute(){}
}
