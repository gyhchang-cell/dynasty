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
public final class DragonPalaceServerQa {
 @GameTest(template="bow_ritual_test") public static void actualNbtAndClientMeshHaveExactlyTheSameExposedBlocks(GameTestHelper h)throws Exception{
  CompoundTag nbt;try(var in=DragonPalaceServerQa.class.getResourceAsStream("/data/dynasty/structures/scenic_dragon_palace_mirage.nbt")){nbt=NbtIo.readCompressed(in);}
  JsonObject json;try(var reader=new InputStreamReader(DragonPalaceServerQa.class.getResourceAsStream("/assets/dynasty/scenic/dragon_palace_mirage.json"))){json=JsonParser.parseReader(reader).getAsJsonObject();}
  var blocks=nbt.getList("blocks",10);var all=new HashMap<String,Integer>();var mesh=new HashMap<String,Integer>();
  for(var item:blocks){var b=(CompoundTag)item;var p=b.getList("pos",3);all.put(p.getInt(0)+","+p.getInt(1)+","+p.getInt(2),b.getInt("state"));h.assertTrue(!b.contains("nbt"),"Block entity payload");}
  for(var item:json.getAsJsonArray("blocks")){var a=item.getAsJsonArray();mesh.put(a.get(0)+","+a.get(1)+","+a.get(2),a.get(3).getAsInt());}
  h.assertTrue(all.equals(mesh)&&all.size()==4976,"NBT and client mesh diverged");h.assertTrue(nbt.getList("entities",10).isEmpty(),"Physical mirage entity");
  int count=0;var actual=new HashSet<String>();
  for(var item:json.getAsJsonArray("exposedFaces")){var a=item.getAsJsonArray();var d=Direction.byName(a.get(4).getAsString());h.assertTrue(d!=null,"Invalid face");int x=a.get(0).getAsInt(),y=a.get(1).getAsInt(),z=a.get(2).getAsInt();String key=x+","+y+","+z;h.assertTrue(all.get(key)==a.get(3).getAsInt(),"Wrong face material");h.assertTrue(!all.containsKey((x+d.getStepX())+","+(y+d.getStepY())+","+(z+d.getStepZ())),"Hidden face exported");h.assertTrue(actual.add(key+","+d),"Duplicate face");count++;}
  h.assertTrue(count==7726,"Wrong exposed-face budget");
  for(var key:all.keySet()){var p=key.split(",");int x=Integer.parseInt(p[0]),y=Integer.parseInt(p[1]),z=Integer.parseInt(p[2]);for(var d:Direction.values())if(!all.containsKey((x+d.getStepX())+","+(y+d.getStepY())+","+(z+d.getStepZ())))h.assertTrue(actual.contains(key+","+d),"Missing real exposed face");}
  var palette=nbt.getList("palette",10);h.assertTrue(palette.size()==json.getAsJsonArray("palette").size(),"Palette mismatch");for(int i=0;i<palette.size();i++)h.assertTrue(palette.getCompound(i).getString("Name").equals(json.getAsJsonArray("palette").get(i).getAsJsonObject().get("Name").getAsString()),"Different block");h.succeed();
 }
 @GameTest(template="bow_ritual_test",timeoutTicks=120) public static void actualSourceWaterMirroringAndSavedClock(GameTestHelper h){
  var l=h.getLevel().getServer().getLevel(net.minecraft.resources.ResourceKey.create(Registries.DIMENSION,new net.minecraft.resources.ResourceLocation("dynasty","dragon_palace")));h.assertTrue(l!=null,"Actual dragon palace dimension missing");
  var center=new BlockPos(600,190,600);
  for(int x=(center.getX()-32)>>4;x<=(center.getX()+32)>>4;x++)for(int z=(center.getZ()-32)>>4;z<=(center.getZ()+32)>>4;z++)l.getChunk(x,z);
  for(int x=-26;x<=25;x++)for(int z=-22;z<=21;z++)for(int y=-24;y<=1;y++)l.setBlock(center.offset(x,y,z),y==-24||x==-26||x==25||z==-22||z==21?Blocks.STONE.defaultBlockState():y<=0?Blocks.WATER.defaultBlockState():Blocks.AIR.defaultBlockState(),2);
  var origin=new Vec3(center.getX(),center.getY()+l.getFluidState(center).getHeight(l,center),center.getZ());
  h.assertTrue(ScenicDragonPalaceSite.valid(l,origin),"Actual open deep water rejected");
  h.assertTrue(!ScenicDragonPalaceSite.valid(h.getLevel(),origin),"Overworld reflection leaked");
  h.assertTrue(!ScenicDragonPalaceSite.valid(l,origin.add(0,.1,0)),"Invented water height accepted");
  var surface=center.offset(13,0,-7);l.setBlock(surface,Blocks.ICE.defaultBlockState(),2);h.assertTrue(!ScenicDragonPalaceSite.valid(l,origin),"Odd footprint surface ice missed");l.setBlock(surface,Blocks.WATER.defaultBlockState(),2);
  var mesh=JsonParser.parseReader(new InputStreamReader(DragonPalaceServerQa.class.getResourceAsStream("/assets/dynasty/scenic/dragon_palace_mirage.json"))).getAsJsonObject();
  JsonArray roof=null;for(var e:mesh.getAsJsonArray("blocks")){var b=e.getAsJsonArray();if(b.get(1).getAsInt()==22){roof=b;break;}}h.assertTrue(roof!=null,"No real palace roof");
  var obstruction=new BlockPos(center.getX()+roof.get(0).getAsInt()-24,(int)Math.floor(origin.y-23),center.getZ()+roof.get(2).getAsInt()-20);l.setBlock(obstruction,Blocks.STONE.defaultBlockState(),2);h.assertTrue(!ScenicDragonPalaceSite.valid(l,origin),"Actual inverted roof intersects seabed");l.setBlock(obstruction,Blocks.WATER.defaultBlockState(),2);
  h.assertTrue(ScenicDragonPalaceSite.valid(l,origin),"Restored water rejected");
  l.setDayTime(0);l.setRainLevel(1);var events=new ScenicEvents();h.assertTrue(events.start(l,17,origin),"Production start requires unrelated weather/time");var p=events.packets(l,origin).get(0);h.assertTrue(p.duration()==1200&&p.scale()==1&&p.entityId()==-1&&p.sequence().equals("scenic_17"),"Wrong actual city packet");
  h.assertTrue(ScenicEvents.load(events.save(new CompoundTag())).packets(l,origin).equals(List.of(p)),"Saved city clock/anchor changed");l.setDayTime(18000);l.setRainLevel(0);h.assertTrue(events.packets(l,origin).equals(List.of(p)),"Night/clear suppressed unconstrained row");h.assertTrue(!events.start(l,17,origin),"Duplicate city accepted");
  l.setBlock(surface,Blocks.STONE.defaultBlockState(),2);h.assertTrue(events.packets(l,origin).isEmpty(),"Invalid actual water remains visible");l.setBlock(surface,Blocks.WATER.defaultBlockState(),2);
  for(int t=0;t<=1200;t+=11){var a=ScenicDragonPalaceSite.alpha(t,1200,64);var v=ScenicDragonPalaceSite.soundVolume(t,1200,0);h.assertTrue(a>=0&&a<=.58&&v>=0&&v<=.05,"Opacity/local cue cap");}
  h.assertTrue(ScenicDragonPalaceSite.alpha(600,1200,12)==0&&ScenicDragonPalaceSite.alpha(600,1200,177)==0&&ScenicDragonPalaceSite.soundVolume(600,1200,97)==0,"Inside/far/global ghost");h.succeed();
 }
}
