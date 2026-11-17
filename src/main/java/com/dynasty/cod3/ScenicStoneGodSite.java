package com.dynasty.cod3;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import javax.annotation.Nullable;
/** A supported broad valley floor with higher sides and open space for the exported axe sweep. */
public final class ScenicStoneGodSite {
 public record Site(Vec3 origin,Vec3 direction){}
 public static double visibility(Level level){
  if(!level.dimension().equals(Level.OVERWORLD)||level.getRainLevel(1)>.01f)return 0;long t=Math.floorMod(level.getDayTime(),24000);
  return t>=1800?0:Math.min(1,Math.min(t/60.,(1800-t)/60.));
 }
 private static BlockPos at(Site site,int x,int z){var f=site.direction();return BlockPos.containing(site.origin().add(f.z*x+f.x*z,0,-f.x*x+f.z*z));}
 private static int height(Level level,BlockPos p){return level.getHeight(Heightmap.Types.MOTION_BLOCKING,p.getX(),p.getZ());}
 @Nullable public static Site find(Level level,Vec3 near){
  if(visibility(level)<=0)return null;
  for(int radius:new int[]{0,16,32})for(int side=0;side<(radius==0?1:4);side++){
   var col=BlockPos.containing(near.add(side<2?(side==0?radius:-radius):0,0,side>=2?(side==2?radius:-radius):0));if(!level.hasChunkAt(col))continue;
   var origin=new Vec3(col.getX()+.5,height(level,col),col.getZ()+.5);
   for(var f:new Vec3[]{new Vec3(0,0,1),new Vec3(1,0,0),new Vec3(0,0,-1),new Vec3(-1,0,0)}){var site=new Site(origin,f);if(valid(level,site))return site;}
  }
  return null;
 }
 @Nullable public static Site nearObserver(Level level,Vec3 pos,Vec3 look){var site=find(level,pos.add(look.multiply(1,0,1).normalize().scale(80)));return site!=null?site:find(level,pos);}
 public static boolean valid(Level level,Site site){
  var o=site.origin();var f=site.direction();if(!Double.isFinite(o.lengthSqr())||!level.dimension().equals(Level.OVERWORLD)||f.y!=0||Math.abs(f.x)+Math.abs(f.z)!=1||f.x!=Math.rint(f.x)||f.z!=Math.rint(f.z))return false;
  // Both actual foot beds are stationary throughout all three exported animation LODs.
  for(int side:new int[]{-1,1})for(int x=3;x<=8;x++)for(int z=-3;z<=5;z++){
   var p=at(site,x*side,z);if(!level.hasChunkAt(p)||height(level,p)!=o.y)return false;var floor=p.below();
   if(!level.getFluidState(floor).isEmpty()||!level.getBlockState(floor).isFaceSturdy(level,floor,Direction.UP))return false;
  }
  // Symmetric clearance conservatively covers GeckoLib's X convention and all axe poses.
  for(int x=-20;x<=20;x++)for(int z=-6;z<=12;z++){var p=at(site,x,z);if(!level.hasChunkAt(p)||height(level,p)>o.y+1)return false;}
  // Two higher sides define a real valley; a flat plain or isolated pedestal is insufficient.
  for(int side:new int[]{-1,1})for(int z:new int[]{-8,8}){var p=at(site,36*side,z);if(!level.hasChunkAt(p)||height(level,p)<o.y+8)return false;}
  for(int z=16;z<=40;z+=8){var p=at(site,0,z);if(!level.hasChunkAt(p)||height(level,p)>o.y+3)return false;}
  return true;
 }
 public static double alpha(double age,int duration,double distance,double visibility){return .78*visibility*ScenicAurora.envelope(age,duration,distance)*Math.max(0,Math.min(1,(distance-24)/16));}
 public static double soundVolume(double age,int duration,double distance,double visibility){return .08*visibility*ScenicAurora.envelope(age,duration,distance)*Math.max(0,Math.min(1,(96-distance)/40));}
 private ScenicStoneGodSite(){}
}
