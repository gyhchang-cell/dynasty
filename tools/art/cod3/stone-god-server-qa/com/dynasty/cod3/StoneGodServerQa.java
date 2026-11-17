package com.dynasty.cod3;
import com.google.gson.*;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;
import software.bernie.geckolib.loading.json.raw.Model;
import software.bernie.geckolib.loading.object.*;
import software.bernie.geckolib.util.JsonUtil;
import java.io.*;import java.util.*;
@GameTestHolder("dynasty_scenic_qa") @PrefixGameTestTemplate(false)
public final class StoneGodServerQa {
 private static JsonObject asset(String n)throws Exception{try(var reader=new InputStreamReader(StoneGodServerQa.class.getResourceAsStream("/assets/dynasty/"+n))){return JsonParser.parseReader(reader).getAsJsonObject();}}
 @GameTest(template="bow_ritual_test") public static void realStoneRigAndAtlasBakeWithoutClientClasses(GameTestHelper h)throws Exception{
  int[] counts={70,59,31};int i=0;for(String lod:List.of("","_medium","_far")){var j=asset("geo/scenic/stone_god"+lod+".geo.json");var tree=GeometryTree.fromModel(JsonUtil.GEO_GSON.fromJson(j,Model.class));h.assertTrue(!BakedModelFactory.getForNamespace("dynasty").constructGeoModel(tree).topLevelBones().isEmpty(),"Actual Gecko bake failed");var bones=j.getAsJsonArray("minecraft:geometry").get(0).getAsJsonObject().getAsJsonArray("bones");int cubes=0;boolean grip=false;for(var b:bones){var o=b.getAsJsonObject();cubes+=o.getAsJsonArray("cubes").size();if(o.get("name").getAsString().equals("axe"))grip=o.get("parent").getAsString().equals("right_hand");}h.assertTrue(bones.size()==19&&cubes==counts[i++]&&grip,"LOD/weapon parent changed");}
  var animation=JsonUtil.GEO_GSON.fromJson(asset("animations/scenic/stone_god.animation.json").getAsJsonObject("animations"),BakedAnimations.class).getAnimation("animation.scenic.idle");h.assertTrue(animation!=null&&animation.length()==160,"Eight-second real animation missing");try(var in=StoneGodServerQa.class.getResourceAsStream("/assets/dynasty/textures/entity/scenic/stone_god.png")){var image=javax.imageio.ImageIO.read(in);h.assertTrue(image.getWidth()==1024&&image.getHeight()==1024,"Final original atlas not loaded");}h.succeed();
 }
 @GameTest(template="bow_ritual_test",timeoutTicks=120) public static void actualValleyFootBedsAndClearancePersistWithOriginalClock(GameTestHelper h){
  var l=h.getLevel();var c=h.absolutePos(new BlockPos(1800,190,1800));
  for(int x=-44;x<=44;x++)for(int z=-12;z<=44;z++)for(int y=-1;y<=14;y++)l.setBlock(c.offset(x,y,z),y<0||Math.abs(x)>=34&&Math.abs(x)<=38&&y<12?Blocks.STONE.defaultBlockState():Blocks.AIR.defaultBlockState(),2);
  l.setDayTime(900);l.setWeatherParameters(6000,6000,false,false);l.setRainLevel(0);var anchor=new Vec3(c.getX()+.5,c.getY(),c.getZ()+.5);var site=new ScenicStoneGodSite.Site(anchor,new Vec3(0,0,1));h.assertTrue(ScenicStoneGodSite.valid(l,site),"Supported real canyon rejected");
  var foot=c.offset(5,-1,1);l.setBlock(foot,Blocks.AIR.defaultBlockState(),2);h.assertTrue(!ScenicStoneGodSite.valid(l,site),"Foot floats over odd-cell hole");l.setBlock(foot,Blocks.STONE.defaultBlockState(),2);
  var axe=c.offset(17,20,5);l.setBlock(axe,Blocks.STONE.defaultBlockState(),2);h.assertTrue(!ScenicStoneGodSite.valid(l,site),"Exported axe sweep intersects obstacle");l.setBlock(axe,Blocks.AIR.defaultBlockState(),2);
  h.assertTrue(!ScenicStoneGodSite.valid(l,new ScenicStoneGodSite.Site(anchor,new Vec3(1,0,1))),"Diagonal site accepted");
  var scenes=new ScenicEvents();h.assertTrue(scenes.start(l,6,anchor),"Cannot start actual supported statue");var packet=scenes.packets(l,anchor).get(0);h.assertTrue(packet.scale()==1&&packet.duration()==1200&&packet.entityId()==-1&&packet.direction().equals(site.direction()),"Wrong packet origin/scale/direction/lifetime");h.assertTrue(ScenicEvents.load(scenes.save(new CompoundTag())).packets(l,anchor).equals(List.of(packet)),"Saved statue restarts/loses ground");
  l.setDayTime(6000);h.assertTrue(scenes.packets(l,anchor).isEmpty(),"Statue remains after dawn");l.setDayTime(900);l.setRainLevel(1);h.assertTrue(scenes.packets(l,anchor).isEmpty(),"Rain statue leaks");l.setRainLevel(0);
  for(int t=0;t<=1200;t+=13){double a=ScenicStoneGodSite.alpha(t,1200,70,1),v=ScenicStoneGodSite.soundVolume(t,1200,0,1);h.assertTrue(a>=0&&a<=.78&&v>=0&&v<=.08,"Opacity or quiet cue exceeds cap");}h.assertTrue(ScenicStoneGodSite.alpha(600,1200,12,1)==0&&ScenicStoneGodSite.soundVolume(600,1200,97,1)==0,"Near screen/global clang");h.succeed();
 }
}
