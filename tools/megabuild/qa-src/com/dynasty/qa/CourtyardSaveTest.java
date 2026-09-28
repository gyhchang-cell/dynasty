package com.dynasty.qa;
import java.nio.file.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.*;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.storage.RegionFile;
import net.minecraft.world.level.chunk.storage.ChunkSerializer;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty") @PrefixGameTestTemplate(false)
public final class CourtyardSaveTest {
    @GameTest(templateNamespace="dynasty",template="bow_ritual_test",timeoutTicks=600)
    public static void independentWorldLoads(GameTestHelper h) throws Exception {
        var folder=Path.of(System.getProperty("dynasty.courtyard.world"));
        var level=NbtIo.readCompressed(folder.resolve("level.dat").toFile()).getCompound("Data");
        h.assertTrue(level.getString("LevelName").startsWith("徽院"),"Independent save name");
        h.assertTrue(!level.contains("Player"),"Must not clone player inventory");
        int loaded=0,states=0;
        try(var region=new RegionFile(folder.resolve("region/r.0.-1.mca"),folder.resolve("region"),true)){
            boolean full=Boolean.getBoolean("dynasty.courtyard.full");
            for(int x=full?15:19;x<(full?27:28);x++)for(int z=-13;z<(full?-4:-3);z++){
                var pos=new ChunkPos(x,z);
                try(var in=region.getChunkDataInputStream(pos)){
                    h.assertTrue(in!=null,"Missing chunk "+pos);
                    var tag=NbtIo.read(in);
                    for(var entry:tag.getList("sections",10)){
                        var section=(CompoundTag)entry;
                        for(var p:section.getCompound("block_states").getList("palette",10)){
                            var palette=(CompoundTag)p;var id=new ResourceLocation(palette.getString("Name"));
                            h.assertTrue(BuiltInRegistries.BLOCK.containsKey(id),"Unknown block "+id);
                            var block=BuiltInRegistries.BLOCK.get(id);var props=palette.getCompound("Properties");
                            for(var key:props.getAllKeys()){
                                var property=block.getStateDefinition().getProperty(key);
                                h.assertTrue(property!=null&&property.getValue(props.getString(key)).isPresent(),"Invalid property "+id+" "+key);
                            }states++;
                        }
                    }
                    var chunk=ChunkSerializer.read(h.getLevel(),h.getLevel().getPoiManager(),pos,tag);
                    h.assertTrue(chunk!=null,"Chunk decoding failed");loaded++;
                }
            }
        }
        System.out.println("COURTYARD QA: "+loaded+" chunks decoded; "+states+" palette states validated");
        h.succeed();
    }
}
