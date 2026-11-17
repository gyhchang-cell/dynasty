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
public final class MirageStreetServerQa {
 @GameTest(template="bow_ritual_test") public static void actualNbtAndClientMeshHaveExactlyTheSameExposedBlocks(GameTestHelper h)throws Exception{
  CompoundTag nbt;try(var in=MirageStreetServerQa.class.getResourceAsStream("/data/dynasty/structures/scenic_mirage_street.nbt")){nbt=NbtIo.readCompressed(in);}
  JsonObject json;try(var reader=new InputStreamReader(MirageStreetServerQa.class.getResourceAsStream("/assets/dynasty/scenic/mirage_street.json"))){json=JsonParser.parseReader(reader).getAsJsonObject();}
  var blocks=nbt.getList("blocks",10);var all=new HashMap<String,Integer>();var mesh=new HashMap<String,Integer>();
  for(var item:blocks){var b=(CompoundTag)item;var p=b.getList("pos",3);all.put(p.getInt(0)+","+p.getInt(1)+","+p.getInt(2),b.getInt("state"));h.assertTrue(!b.contains("nbt"),"Block entity payload");}
  for(var item:json.getAsJsonArray("blocks")){var a=item.getAsJsonArray();mesh.put(a.get(0)+","+a.get(1)+","+a.get(2),a.get(3).getAsInt());}
  h.assertTrue(all.equals(mesh)&&all.size()==3648,"NBT and client mesh diverged");h.assertTrue(nbt.getList("entities",10).isEmpty(),"Physical mirage entity");
  int count=0;var actual=new HashSet<String>();
  for(var item:json.getAsJsonArray("exposedFaces")){var a=item.getAsJsonArray();var d=Direction.byName(a.get(4).getAsString());h.assertTrue(d!=null,"Invalid face");int x=a.get(0).getAsInt(),y=a.get(1).getAsInt(),z=a.get(2).getAsInt();String key=x+","+y+","+z;h.assertTrue(all.get(key)==a.get(3).getAsInt(),"Wrong face material");h.assertTrue(!all.containsKey((x+d.getStepX())+","+(y+d.getStepY())+","+(z+d.getStepZ())),"Hidden face exported");h.assertTrue(actual.add(key+","+d),"Duplicate face");count++;}
  h.assertTrue(count==7370,"Wrong exposed-face budget");
  for(var key:all.keySet()){var p=key.split(",");int x=Integer.parseInt(p[0]),y=Integer.parseInt(p[1]),z=Integer.parseInt(p[2]);for(var d:Direction.values())if(!all.containsKey((x+d.getStepX())+","+(y+d.getStepY())+","+(z+d.getStepZ())))h.assertTrue(actual.contains(key+","+d),"Missing real exposed face");}
  var palette=nbt.getList("palette",10);h.assertTrue(palette.size()==json.getAsJsonArray("palette").size(),"Palette mismatch");for(int i=0;i<palette.size();i++)h.assertTrue(palette.getCompound(i).getString("Name").equals(json.getAsJsonArray("palette").get(i).getAsJsonObject().get("Name").getAsString()),"Different block");h.succeed();
 }
 @GameTest(template="bow_ritual_test",timeoutTicks=120) public static void loadedDesertFootprintWeatherAndSavedClockAreReal(GameTestHelper h){
  var level=h.getLevel();var center=h.absolutePos(new BlockPos(740,190,740));var biome=level.registryAccess().registryOrThrow(Registries.BIOME).getHolderOrThrow(Biomes.DESERT);
  for(int x=(center.getX()-48)>>4;x<=(center.getX()+48)>>4;x++)for(int z=(center.getZ()-40)>>4;z<=(center.getZ()+40)>>4;z++)level.getChunk(x,z).fillBiomesFromNoise((a,b,c,s)->biome,level.getChunkSource().randomState().sampler());
  for(int x=-46;x<=46;x++)for(int z=-34;z<=34;z++)for(int y=-1;y<=26;y++)level.setBlock(center.offset(x,y,z),y<0?Blocks.SANDSTONE.defaultBlockState():Blocks.AIR.defaultBlockState(),2);
  level.setDayTime(18000);level.setWeatherParameters(6000,6000,false,false);level.setRainLevel(0);var anchor=Vec3.atLowerCornerOf(center);
  h.assertTrue(ScenicMirageSite.valid(level,anchor),"Actual broad dry desert rejected");var odd=center.offset(3,-1,5);level.setBlock(odd,Blocks.AIR.defaultBlockState(),2);h.assertTrue(!ScenicMirageSite.valid(level,anchor),"Odd-cell hole below shop missed");level.setBlock(odd,Blocks.SANDSTONE.defaultBlockState(),2);
  level.setBlock(center.offset(7,4,9),Blocks.STONE.defaultBlockState(),2);h.assertTrue(!ScenicMirageSite.valid(level,anchor),"Obstructed skyline accepted");level.setBlock(center.offset(7,4,9),Blocks.AIR.defaultBlockState(),2);
  var events=new ScenicEvents();h.assertTrue(events.start(level,14,anchor),"Production start rejects valid site");var p=events.packets(level,anchor).get(0);h.assertTrue(p.duration()==1800&&p.scale()==1&&p.entityId()==-1,"Mirage becomes physical/scaled or wrong duration");h.assertTrue(ScenicEvents.load(events.save(new CompoundTag())).packets(level,anchor).equals(List.of(p)),"Clock/anchor not persistent");
  level.setDayTime(6000);h.assertTrue(events.packets(level,anchor).isEmpty()&&!new ScenicEvents().start(level,14,anchor),"Daytime mirage leaks");level.setDayTime(18000);level.setRainLevel(1);h.assertTrue(events.packets(level,anchor).isEmpty(),"Rain mirage leaks");level.setRainLevel(0);
  h.assertTrue(ScenicMirageSite.alpha(900,1800,12,1)==0&&ScenicMirageSite.alpha(900,1800,170,1)==0,"Fullscreen/far ghost");for(int t=0;t<=1800;t+=13){double a=ScenicMirageSite.alpha(t,1800,64,1),v=ScenicMirageSite.soundVolume(t,1800,0,1);h.assertTrue(a>=0&&a<=.60&&v>=0&&v<=.04,"Opacity/quiet cue cap");}h.assertTrue(ScenicMirageSite.soundVolume(900,1800,65,1)==0,"Global market cue");h.succeed();
 }
}
