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
public final class GhostMarketServerQa {
 @GameTest(template="bow_ritual_test") public static void actualNbtAndClientMeshHaveExactlyTheSameExposedBlocks(GameTestHelper h)throws Exception{
  CompoundTag nbt;try(var in=GhostMarketServerQa.class.getResourceAsStream("/data/dynasty/structures/scenic_ghost_market.nbt")){nbt=NbtIo.readCompressed(in);}
  JsonObject json;try(var reader=new InputStreamReader(GhostMarketServerQa.class.getResourceAsStream("/assets/dynasty/scenic/ghost_market.json"))){json=JsonParser.parseReader(reader).getAsJsonObject();}
  var blocks=nbt.getList("blocks",10);var all=new HashMap<String,Integer>();var mesh=new HashMap<String,Integer>();
  for(var item:blocks){var b=(CompoundTag)item;var p=b.getList("pos",3);all.put(p.getInt(0)+","+p.getInt(1)+","+p.getInt(2),b.getInt("state"));h.assertTrue(!b.contains("nbt"),"Block entity payload");}
  for(var item:json.getAsJsonArray("blocks")){var a=item.getAsJsonArray();mesh.put(a.get(0)+","+a.get(1)+","+a.get(2),a.get(3).getAsInt());}
  h.assertTrue(all.equals(mesh)&&all.size()==2981,"NBT and client mesh diverged");h.assertTrue(nbt.getList("entities",10).isEmpty(),"Physical mirage entity");
  int count=0;var actual=new HashSet<String>();
  for(var item:json.getAsJsonArray("exposedFaces")){var a=item.getAsJsonArray();var d=Direction.byName(a.get(4).getAsString());h.assertTrue(d!=null,"Invalid face");int x=a.get(0).getAsInt(),y=a.get(1).getAsInt(),z=a.get(2).getAsInt();String key=x+","+y+","+z;h.assertTrue(all.get(key)==a.get(3).getAsInt(),"Wrong face material");h.assertTrue(!all.containsKey((x+d.getStepX())+","+(y+d.getStepY())+","+(z+d.getStepZ())),"Hidden face exported");h.assertTrue(actual.add(key+","+d),"Duplicate face");count++;}
  h.assertTrue(count==5564,"Wrong exposed-face budget");
  for(var key:all.keySet()){var p=key.split(",");int x=Integer.parseInt(p[0]),y=Integer.parseInt(p[1]),z=Integer.parseInt(p[2]);for(var d:Direction.values())if(!all.containsKey((x+d.getStepX())+","+(y+d.getStepY())+","+(z+d.getStepZ())))h.assertTrue(actual.contains(key+","+d),"Missing real exposed face");}
  var palette=nbt.getList("palette",10);h.assertTrue(palette.size()==json.getAsJsonArray("palette").size(),"Palette mismatch");for(int i=0;i<palette.size();i++)h.assertTrue(palette.getCompound(i).getString("Name").equals(json.getAsJsonArray("palette").get(i).getAsJsonObject().get("Name").getAsString()),"Different block");h.succeed();
 }
 @GameTest(template="bow_ritual_test",timeoutTicks=120) public static void actualUnderworldDryGroundClockAndRealLampAnchors(GameTestHelper h)throws Exception{
  var l=h.getLevel().getServer().getLevel(net.minecraft.resources.ResourceKey.create(Registries.DIMENSION,new net.minecraft.resources.ResourceLocation("dynasty","underworld")));h.assertTrue(l!=null,"Actual underworld missing");var center=new BlockPos(-600,190,-600);
  for(int x=(center.getX()-32)>>4;x<=(center.getX()+32)>>4;x++)for(int z=(center.getZ()-40)>>4;z<=(center.getZ()+40)>>4;z++)l.getChunk(x,z);
  for(int x=-18;x<=17;x++)for(int z=-26;z<=25;z++)for(int y=-1;y<l.getMaxBuildHeight()-190;y++)l.setBlock(center.offset(x,y,z),y<0?Blocks.STONE.defaultBlockState():Blocks.AIR.defaultBlockState(),2);
  l.getServer().overworld().setDayTime(18000);l.setRainLevel(0);var origin=Vec3.atLowerCornerOf(center);h.assertTrue(ScenicGhostMarketSite.valid(l,origin),"Actual dry underworld floor rejected");h.assertTrue(!ScenicGhostMarketSite.valid(h.getLevel(),origin),"Overworld ghost market leak");
  var events=new ScenicEvents();h.assertTrue(events.start(l,22,origin),"Production ghost market start failed");var p=events.packets(l,origin).get(0);h.assertTrue(p.scale()==1&&p.duration()==1800&&p.entityId()==-1,"Wrong ninety-second nonphysical market");h.assertTrue(ScenicEvents.load(events.save(new CompoundTag())).packets(l,origin).equals(List.of(p)),"Saved ghost market clock lost");
  var odd=center.offset(-13,-1,19);l.setBlock(odd,Blocks.AIR.defaultBlockState(),2);h.assertTrue(!ScenicGhostMarketSite.valid(l,origin),"Far foundation floats");l.setBlock(odd,Blocks.STONE.defaultBlockState(),2);l.setBlock(center.offset(3,4,9),Blocks.STONE.defaultBlockState(),2);h.assertTrue(!ScenicGhostMarketSite.valid(l,origin),"Blocked shop envelope");l.setBlock(center.offset(3,4,9),Blocks.AIR.defaultBlockState(),2);
  l.getServer().overworld().setDayTime(6000);h.assertTrue(events.packets(l,origin).isEmpty(),"Daytime ghost market leaks");l.getServer().overworld().setDayTime(18000);l.setRainLevel(1);h.assertTrue(events.packets(l,origin).size()==1,"Skyless dimension incorrectly requires precipitation for native regional fog");l.setRainLevel(0);
  var json=JsonParser.parseReader(new InputStreamReader(GhostMarketServerQa.class.getResourceAsStream("/assets/dynasty/scenic/ghost_market.json"))).getAsJsonObject();int lamps=0;for(var e:json.getAsJsonArray("blocks")){var a=e.getAsJsonArray();var palette=json.getAsJsonArray("palette").get(a.get(3).getAsInt()).getAsJsonObject();if(palette.get("Name").getAsString().equals("minecraft:verdant_froglight")){lamps++;h.assertTrue(palette.getAsJsonObject("Properties").get("axis").getAsString().equals("y"),"Wrong actual supported lamp axis");}}
  h.assertTrue(lamps==12,"Actual flame anchor count changed");for(int t=0;t<=1800;t+=17){double a=ScenicGhostMarketSite.alpha(t,1800,64,1),v=ScenicGhostMarketSite.soundVolume(t,1800,0,1);h.assertTrue(a>=0&&a<=.54&&v>=0&&v<=.025,"Opacity/quiet market call exceeds cap");}
  h.assertTrue(ScenicGhostMarketSite.alpha(900,1800,8,1)==0&&ScenicGhostMarketSite.alpha(900,1800,193,1)==0&&ScenicGhostMarketSite.soundVolume(900,1800,65,1)==0,"Fullscreen/far/global market leak");h.succeed();
 }
}
