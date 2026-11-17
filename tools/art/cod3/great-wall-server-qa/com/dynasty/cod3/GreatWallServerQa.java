package com.dynasty.cod3;
import com.google.gson.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.*;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;
import java.io.*;
import java.util.*;
@GameTestHolder("dynasty_scenic_qa")
@PrefixGameTestTemplate(false)
public final class GreatWallServerQa {
 @GameTest(template="bow_ritual_test") public static void actualNbtAndClientMeshHaveExactlyTheSameExposedBlocks(GameTestHelper h)throws Exception{
  CompoundTag nbt;try(var in=GreatWallServerQa.class.getResourceAsStream("/data/dynasty/structures/scenic_great_wall_echo.nbt")){nbt=NbtIo.readCompressed(in);}
  JsonObject json;try(var reader=new InputStreamReader(GreatWallServerQa.class.getResourceAsStream("/assets/dynasty/scenic/great_wall_echo.json"))){json=JsonParser.parseReader(reader).getAsJsonObject();}
  var blocks=nbt.getList("blocks",10);var all=new HashMap<String,Integer>();var mesh=new HashMap<String,Integer>();
  for(var item:blocks){var b=(CompoundTag)item;var p=b.getList("pos",3);all.put(p.getInt(0)+","+p.getInt(1)+","+p.getInt(2),b.getInt("state"));h.assertTrue(!b.contains("nbt"),"Block entity payload");}
  for(var item:json.getAsJsonArray("blocks")){var a=item.getAsJsonArray();mesh.put(a.get(0)+","+a.get(1)+","+a.get(2),a.get(3).getAsInt());}
  h.assertTrue(all.equals(mesh)&&all.size()==6086,"NBT and client mesh diverged");h.assertTrue(nbt.getList("entities",10).isEmpty(),"Physical mirage entity");
  int count=0;var actual=new HashSet<String>();
  for(var item:json.getAsJsonArray("exposedFaces")){var a=item.getAsJsonArray();var d=Direction.byName(a.get(4).getAsString());h.assertTrue(d!=null,"Invalid face");int x=a.get(0).getAsInt(),y=a.get(1).getAsInt(),z=a.get(2).getAsInt();String key=x+","+y+","+z;h.assertTrue(all.get(key)==a.get(3).getAsInt(),"Wrong face material");h.assertTrue(!all.containsKey((x+d.getStepX())+","+(y+d.getStepY())+","+(z+d.getStepZ())),"Hidden face exported");h.assertTrue(actual.add(key+","+d),"Duplicate face");count++;}
  h.assertTrue(count==5320,"Wrong exposed-face budget");
  for(var key:all.keySet()){var p=key.split(",");int x=Integer.parseInt(p[0]),y=Integer.parseInt(p[1]),z=Integer.parseInt(p[2]);for(var d:Direction.values())if(!all.containsKey((x+d.getStepX())+","+(y+d.getStepY())+","+(z+d.getStepZ())))h.assertTrue(actual.contains(key+","+d),"Missing real exposed face");}
  var palette=nbt.getList("palette",10);h.assertTrue(palette.size()==json.getAsJsonArray("palette").size(),"Palette mismatch");for(int i=0;i<palette.size();i++)h.assertTrue(palette.getCompound(i).getString("Name").equals(json.getAsJsonArray("palette").get(i).getAsJsonObject().get("Name").getAsString()),"Different block");h.succeed();
 }
 @GameTest(template="bow_ritual_test",timeoutTicks=120) public static void loadedBattlefieldGroundRainDawnClockAndFarFlags(GameTestHelper h)throws Exception{
  var l=h.getLevel();var center=h.absolutePos(new BlockPos(1400,190,1400));
  for(int x=(center.getX()-48)>>4;x<=(center.getX()+48)>>4;x++)for(int z=(center.getZ()-112)>>4;z<=(center.getZ()+48)>>4;z++)l.getChunk(x,z);
  for(int x=-36;x<=35;x++)for(int z=-20;z<=15;z++)for(int y=-1;y<=25;y++)l.setBlock(center.offset(x,y,z),y<0?Blocks.STONE.defaultBlockState():Blocks.AIR.defaultBlockState(),2);
  l.setDayTime(900);l.setWeatherParameters(6000,6000,true,false);l.setRainLevel(1);var anchor=Vec3.atLowerCornerOf(center);
  h.assertTrue(ScenicGreatWallSite.valid(l,anchor),"Broad dry flat ground rejected");h.assertTrue(!new ScenicEvents().start(l,18,anchor),"Height alone invents battlefield");
  var structure=l.registryAccess().registryOrThrow(Registries.STRUCTURE).get(new net.minecraft.resources.ResourceLocation("dynasty","ruined_battlefield"));
  var piece=new com.dynasty.structure.BattlefieldPiece(center.offset(-16,-1,-96));var cp=new net.minecraft.world.level.ChunkPos(center.offset(-16,-1,-96));
  var start=new net.minecraft.world.level.levelgen.structure.StructureStart(structure,cp,0,new net.minecraft.world.level.levelgen.structure.pieces.PiecesContainer(List.of(piece)));l.getChunk(cp.x,cp.z).setStartForStructure(structure,start);
  h.assertTrue(ScenicGreatWallSite.battlefieldNear(l,anchor),"Actual loaded registered start missed");
  var events=new ScenicEvents();h.assertTrue(events.start(l,18,anchor),"Production wall start rejected");var p=events.packets(l,anchor).get(0);
  h.assertTrue(p.duration()==1200&&p.scale()==1&&p.entityId()==-1,"Wrong nonphysical sixty-second wall");h.assertTrue(ScenicEvents.load(events.save(new CompoundTag())).packets(l,anchor).equals(List.of(p)),"Saved anchor/clock changed");
  var odd=center.offset(-29,-1,9);l.setBlock(odd,Blocks.AIR.defaultBlockState(),2);h.assertTrue(!ScenicGreatWallSite.valid(l,anchor),"Odd-cell foundation floats");l.setBlock(odd,Blocks.STONE.defaultBlockState(),2);
  l.setBlock(center.offset(7,4,9),Blocks.STONE.defaultBlockState(),2);h.assertTrue(!ScenicGreatWallSite.valid(l,anchor),"Obstructed silhouette accepted");l.setBlock(center.offset(7,4,9),Blocks.AIR.defaultBlockState(),2);
  l.setRainLevel(0);h.assertTrue(events.packets(l,anchor).isEmpty(),"Dry fog leaks");l.setRainLevel(1);l.setDayTime(6000);h.assertTrue(events.packets(l,anchor).isEmpty(),"Noon fog leaks");l.setDayTime(900);
  for(int t=0;t<=1200;t+=17){double a=ScenicGreatWallSite.alpha(t,1200,64,1),v=ScenicGreatWallSite.soundVolume(t,1200,0,1);h.assertTrue(a>=0&&a<=.52&&v>=0&&v<=.035,"Ghost/horn exceeds cap");}
  h.assertTrue(ScenicGreatWallSite.alpha(600,1200,12,1)==0&&ScenicGreatWallSite.alpha(600,1200,225,1)==0&&ScenicGreatWallSite.soundVolume(600,1200,129,1)==0,"Inside/far/global leak");
  h.assertTrue(ScenicGreatWallSite.farBlend(88,false)==0&&ScenicGreatWallSite.farBlend(100,false)==.5&&ScenicGreatWallSite.farBlend(112,false)==1&&ScenicGreatWallSite.farBlend(64,true)==1,"LOD crossfade discontinuity");
  JsonObject full,flags;try(var r=new InputStreamReader(GreatWallServerQa.class.getResourceAsStream("/assets/dynasty/scenic/great_wall_echo.json"))){full=JsonParser.parseReader(r).getAsJsonObject();}try(var r=new InputStreamReader(GreatWallServerQa.class.getResourceAsStream("/assets/dynasty/scenic/great_wall_echo_flags.json"))){flags=JsonParser.parseReader(r).getAsJsonObject();}
  var all=new HashSet<String>();for(var e:full.getAsJsonArray("blocks"))all.add(e.toString());var subset=new HashMap<String,Integer>();for(var e:flags.getAsJsonArray("blocks")){h.assertTrue(all.contains(e.toString()),"Far flag changed original anchor/material");var a=e.getAsJsonArray();subset.put(a.get(0)+","+a.get(1)+","+a.get(2),a.get(3).getAsInt());}
  var expected=new HashSet<String>();for(var key:subset.keySet()){var a=key.split(",");int x=Integer.parseInt(a[0]),y=Integer.parseInt(a[1]),z=Integer.parseInt(a[2]);for(var d:Direction.values())if(!subset.containsKey((x+d.getStepX())+","+(y+d.getStepY())+","+(z+d.getStepZ())))expected.add(key+","+d.getName());}
  var actual=new HashSet<String>();for(var e:flags.getAsJsonArray("exposedFaces")){var a=e.getAsJsonArray();var key=a.get(0)+","+a.get(1)+","+a.get(2);h.assertTrue(subset.get(key)==a.get(3).getAsInt(),"Wrong flag face palette");h.assertTrue(actual.add(key+","+a.get(4).getAsString()),"Duplicate flag face");}h.assertTrue(actual.equals(expected)&&actual.size()<500&&subset.size()>90,"Far subset lacks recomputed base faces or exceeds budget");h.succeed();
 }
}
