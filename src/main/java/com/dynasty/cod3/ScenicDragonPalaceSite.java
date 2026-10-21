package com.dynasty.cod3;

import com.google.gson.*;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import javax.annotation.Nullable;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Read-only water support for the inverted palace. Never places its structure or loads chunks. */
public final class ScenicDragonPalaceSite {
    private static final List<BlockPos> OCCUPIED=occupied();
    private static List<BlockPos> occupied(){
        try(var in=ScenicDragonPalaceSite.class.getResourceAsStream("/assets/dynasty/scenic/dragon_palace_mirage.json")){
            if(in==null)throw new IllegalStateException("Missing palace mesh");
            var json=JsonParser.parseReader(new InputStreamReader(in,StandardCharsets.UTF_8)).getAsJsonObject();
            var pivot=json.getAsJsonArray("centerPivot");
            if(json.get("version").getAsInt()!=1||pivot.get(0).getAsInt()!=24||pivot.get(1).getAsInt()!=0||pivot.get(2).getAsInt()!=20)throw new IllegalStateException("Palace water pivot changed");
            var out=new ArrayList<BlockPos>();for(var e:json.getAsJsonArray("blocks")){var a=e.getAsJsonArray();out.add(new BlockPos(a.get(0).getAsInt()-24,a.get(1).getAsInt(),a.get(2).getAsInt()-20));}
            if(out.size()!=4976)throw new IllegalStateException("Palace support contract changed");return List.copyOf(out);
        }catch(Exception e){throw new IllegalStateException("Cannot read palace water footprint",e);}
    }
    public static boolean dimension(Level l){return l.dimension().location().toString().equals("dynasty:dragon_palace");}
    private static boolean water(Level l,BlockPos at){var f=l.getFluidState(at);return f.is(FluidTags.WATER)&&f.isSource()&&l.getBlockState(at).getCollisionShape(l,at).isEmpty();}
    @Nullable public static Vec3 find(Level l,Vec3 near){
        if(!dimension(l)||near==null||!Double.isFinite(near.lengthSqr()))return null;
        for(int radius:new int[]{0,16,32})for(int side=0;side<(radius==0?1:4);side++){
            int x=(int)Math.floor(near.x)+(side<2?(side==0?radius:-radius):0),z=(int)Math.floor(near.z)+(side>=2?(side==2?radius:-radius):0);
            var sample=new BlockPos(x,0,z);if(!l.hasChunkAt(sample))continue;
            int y=l.getHeight(Heightmap.Types.MOTION_BLOCKING,x,z)-1;var at=new BlockPos(x,y,z);if(!water(l,at))continue;
            var o=new Vec3(x,y+l.getFluidState(at).getHeight(l,at),z);if(valid(l,o))return o;
        }
        return null;
    }
    public static boolean valid(Level l,Vec3 o){
        if(o==null||!Double.isFinite(o.lengthSqr())||!dimension(l)||o.x!=Math.floor(o.x)||o.z!=Math.floor(o.z))return false;
        int top=(int)Math.floor(o.y),x=(int)o.x,z=(int)o.z;
        // Every column of the declared city footprint must share the actual open source-water plane.
        // Check loaded status first; fluid height may consult a neighbouring cell.
        for(int dx=-25;dx<=24;dx++)for(int dz=-21;dz<=20;dz++)if(!l.hasChunkAt(new BlockPos(x+dx,top,z+dz)))return false;
        for(int dx=-24;dx<=23;dx++)for(int dz=-20;dz<=19;dz++){
            var p=new BlockPos(x+dx,top,z+dz);
            if(!water(l,p)||!l.getFluidState(p.above()).isEmpty()||!l.getBlockState(p.above()).getCollisionShape(l,p.above()).isEmpty())return false;
            if(Math.abs(top+l.getFluidState(p).getHeight(l,p)-o.y)>.001)return false;
        }
        // A reflected unit cube at a fractional waterline overlaps two world cells vertically.
        // Validate the actual occupied mesh, including low roofs, without a 48*40*24 full-volume scan.
        for(var v:OCCUPIED){int low=(int)Math.floor(o.y-v.getY()-1);var p=new BlockPos(x+v.getX(),low,z+v.getZ());if(!water(l,p)||!water(l,p.above()))return false;}
        return true;
    }
    @Nullable public static Vec3 nearObserver(Level l,Vec3 viewer,Vec3 look){var f=look.multiply(1,0,1).normalize();var found=find(l,viewer.add(f.scale(72)));return found!=null?found:find(l,viewer);}
    public static double alpha(double age,int duration,double distance){return .58*ScenicAurora.envelope(age,duration,distance)*Math.max(0,Math.min(1,(distance-24)/16))*Math.max(0,Math.min(1,(176-distance)/32));}
    public static double soundVolume(double age,int duration,double distance){return .05*ScenicAurora.envelope(age,duration,distance)*Math.max(0,Math.min(1,(96-distance)/32));}
    private ScenicDragonPalaceSite(){}
}
