package com.dynasty.cod3;
import com.google.gson.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;
import java.io.*;
import java.util.*;
@GameTestHolder("dynasty_scenic_qa")
@PrefixGameTestTemplate(false)
public final class GhostArmyServerQa {
 private static JsonObject read(String path)throws Exception{try(var r=new InputStreamReader(GhostArmyServerQa.class.getResourceAsStream(path))){return JsonParser.parseReader(r).getAsJsonObject();}}
 @GameTest(template="bow_ritual_test") public static void actualThreeLodRigsAnimationAndFinalPixelAtlasLoad(GameTestHelper h)throws Exception{
  Set<String> full=null;int index=0;for(var lod:List.of("","_medium","_far")){
   var geo=read("/assets/dynasty/geo/scenic/ghost_army_soldier"+lod+".geo.json").getAsJsonArray("minecraft:geometry").get(0).getAsJsonObject();var desc=geo.getAsJsonObject("description");h.assertTrue(desc.get("texture_width").getAsInt()==256&&desc.get("texture_height").getAsInt()==256,"Wrong native atlas size");
   var names=new HashSet<String>();int cubes=0;for(var e:geo.getAsJsonArray("bones")){var b=e.getAsJsonObject();h.assertTrue(names.add(b.get("name").getAsString()),"Duplicate bone");if(b.has("cubes"))cubes+=b.getAsJsonArray("cubes").size();}
   if(full==null)full=names;h.assertTrue(names.equals(full)&&names.size()==19&&cubes==new int[]{56,45,24}[index++],"LOD skeleton/cube contract diverged");
  }
  var animation=read("/assets/dynasty/animations/scenic/ghost_army_soldier.animation.json").getAsJsonObject("animations").getAsJsonObject("animation.scenic.idle");h.assertTrue(animation.get("animation_length").getAsDouble()==4&&animation.get("loop").getAsBoolean(),"Wrong absolute gait cycle");for(var name:animation.getAsJsonObject("bones").keySet())h.assertTrue(full.contains(name),"Animation targets absent bone");
  try(var in=GhostArmyServerQa.class.getResourceAsStream("/assets/dynasty/textures/entity/scenic/ghost_army_soldier.png")){var image=javax.imageio.ImageIO.read(in);h.assertTrue(image!=null&&image.getWidth()==256&&image.getHeight()==256,"Final production PNG absent");}h.succeed();
 }
 @GameTest(template="bow_ritual_test",timeoutTicks=120) public static void loadedBattlefieldRouteSavedClockAndNonphysicalArmy(GameTestHelper h){
  var l=h.getLevel();var center=h.absolutePos(new BlockPos(2600,190,-2600));
  for(int x=(center.getX()-32)>>4;x<=(center.getX()+32)>>4;x++)for(int z=(center.getZ()-112)>>4;z<=(center.getZ()+32)>>4;z++)l.getChunk(x,z);
  for(int x=-18;x<=17;x++)for(int z=-24;z<=23;z++)for(int y=-1;y<=10;y++)l.setBlock(center.offset(x,y,z),y<0?Blocks.STONE.defaultBlockState():Blocks.AIR.defaultBlockState(),2);
  l.setDayTime(900);l.setWeatherParameters(6000,6000,true,false);l.setRainLevel(1);var anchor=Vec3.atLowerCornerOf(center);
  h.assertTrue(ScenicGhostArmySite.valid(l,anchor),"Actual flat route rejected");h.assertTrue(!new ScenicEvents().start(l,4,anchor),"Height alone invents battlefield army");
  var structure=l.registryAccess().registryOrThrow(Registries.STRUCTURE).get(new net.minecraft.resources.ResourceLocation("dynasty","ruined_battlefield"));var piece=new com.dynasty.structure.BattlefieldPiece(center.offset(-16,-1,-96));var cp=new net.minecraft.world.level.ChunkPos(center.offset(-16,-1,-96));l.getChunk(cp.x,cp.z).setStartForStructure(structure,new net.minecraft.world.level.levelgen.structure.StructureStart(structure,cp,0,new net.minecraft.world.level.levelgen.structure.pieces.PiecesContainer(List.of(piece))));
  var events=new ScenicEvents();h.assertTrue(events.start(l,4,anchor),"Actual battlefield army start rejected");var p=events.packets(l,anchor).get(0);h.assertTrue(p.duration()==1200&&p.scale()==1&&p.entityId()==-1,"Wrong nonphysical sixty-second army");h.assertTrue(ScenicEvents.load(events.save(new CompoundTag())).packets(l,anchor).equals(List.of(p)),"Saved clock or formation anchor lost");
  var odd=center.offset(7,-1,13);l.setBlock(odd,Blocks.AIR.defaultBlockState(),2);h.assertTrue(!ScenicGhostArmySite.valid(l,anchor),"Far route hole floats feet");l.setBlock(odd,Blocks.STONE.defaultBlockState(),2);l.setBlock(center.offset(3,2,7),Blocks.STONE.defaultBlockState(),2);h.assertTrue(!ScenicGhostArmySite.valid(l,anchor),"Procession walks through obstacle");l.setBlock(center.offset(3,2,7),Blocks.AIR.defaultBlockState(),2);
  l.setRainLevel(0);h.assertTrue(events.packets(l,anchor).isEmpty(),"Dry army leaks");l.setRainLevel(1);l.setDayTime(18000);h.assertTrue(events.packets(l,anchor).size()==1,"Rainy night incorrectly suppresses untimed army");
  for(int soldier=0;soldier<ScenicGhostArmySite.SOLDIERS;soldier++)for(int t=0;t<=1200;t+=11){var at=ScenicGhostArmySite.position(anchor,soldier,t);h.assertTrue(Math.abs(at.x-anchor.x)<8&&Math.abs(at.z-anchor.z)<12&&at.y==anchor.y,"Soldier leaves validated route");h.assertTrue(Math.abs(ScenicGhostArmySite.position(anchor,soldier,t+80).z-at.z-.8)<1e-8,"World speed disagrees with gait displacement");}
  h.assertTrue(ScenicGhostArmySite.alpha(600,1200,8,1)==0&&ScenicGhostArmySite.alpha(600,1200,225,1)==0&&ScenicGhostArmySite.farBlend(80,false)==0&&ScenicGhostArmySite.farBlend(104,false)==1&&ScenicGhostArmySite.farBlend(32,true)==1,"Near/far/white-array safety failed");h.succeed();
 }
}
