package com.dynasty.expansion;

import com.google.gson.GsonBuilder;
import com.dynasty.blueprint.LoadedStructureRegions;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
import java.nio.file.*;

/** Read-only observations of a real normal-generator dedicated Overworld. No piece placement or biome editing. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class NaturalEcologyAcceptance {
    private static final Map<String,Object> OUT=new LinkedHashMap<>();
    private static final List<Map<String,Object>> ROWS=new ArrayList<>();
    private static Map<String,Object> row(Object... values){var m=new LinkedHashMap<String,Object>();for(int i=0;i<values.length;i+=2)m.put(values[i].toString(),values[i+1]);return m;}
    private static void save() {try{OUT.put("observations",ROWS);Files.writeString(Path.of(System.getProperty("ecology.evidence")),new GsonBuilder().setPrettyPrinting().create().toJson(OUT));}catch(Exception ex){throw new RuntimeException(ex);}}
    @SubscribeEvent public static void started(ServerStartedEvent event){
        if(System.getProperty("ecology.evidence")==null||Boolean.getBoolean("ecology.live"))return;
        var server=event.getServer();var l=server.overworld();
        OUT.put("seed",l.getSeed());OUT.put("generator",l.getChunkSource().getGenerator().getClass().getName());OUT.put("flat_generator",l.getChunkSource().getGenerator() instanceof net.minecraft.world.level.levelgen.FlatLevelSource);
        OUT.put("artificial_piece_placement",false);OUT.put("biome_mutation",false);OUT.put("artificial_mob_spawn",false);OUT.put("time_or_weather_mutation",false);OUT.put("human_multiplayer",false);
        try {
            if(Boolean.TRUE.equals(OUT.get("flat_generator")))throw new IllegalStateException("Normal Overworld required");
            var br=l.registryAccess().registryOrThrow(Registries.BIOME);var sr=l.registryAccess().registryOrThrow(Registries.STRUCTURE);
            // Live datapack-resolved biomes, actual biome-modified spawn lists and native placement callback.
            for(var spec:SecondaryMobs.SPECS){
                var type=SecondaryMobs.TYPES.get(spec.id()).get();var tag=TagKey.create(Registries.BIOME,new ResourceLocation("dynasty","secondary/"+spec.id()));var biomes=new ArrayList<Object>();
                for(var holder:br.holders().toList())if(holder.is(tag)){
                    var entries=holder.value().getMobSettings().getMobs(type.getCategory()).unwrap().stream().filter(e->e.type==type).map(e->row("weight",e.getWeight().asInt(),"min",e.minCount,"max",e.maxCount)).toList();
                    biomes.add(row("biome",br.getKey(holder.value()).toString(),"native_spawn_entries",entries));
                }
                ROWS.add(row("kind","registered_species","id",spec.id(),"category",type.getCategory().getName(),"biomes",biomes));
            }
            for(var name:List.of("ecology/ruined_villages","blueprint/ghost_sites","ecology/tombs","secondary/ruins","ecology/roads","blueprint/clockwork_dog_sites","blueprint/mining_spider_sites")){
                var tag=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty",name));ROWS.add(row("kind","resolved_structure_tag","tag",name,"members",sr.getTag(tag).map(v->v.stream().map(h->sr.getKey(h.value()).toString()).toList()).orElse(List.of())));
            }
            OUT.put("species_denominator",SecondaryMobs.SPECS.size());OUT.put("spawn_position",l.getSharedSpawnPos().toShortString());save();
            // Explicitly bounded native locate: radius=4 placement-region rings, not a claim of world coverage.
            for(var name:List.of("ecology/tombs","blueprint/ghost_sites","ecology/roads","blueprint/clockwork_dog_sites")){
                var tag=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty",name));long begin=System.nanoTime();
                var found=l.findNearestMapStructure(tag,l.getSharedSpawnPos(),4,false);
                ROWS.add(row("kind","native_locate","tag",name,"origin",l.getSharedSpawnPos().toShortString(),"radius_placement_regions",4,"found",found==null?null:found.toShortString(),"elapsed_ms",(System.nanoTime()-begin)/1000000));save();
                if(found!=null)observeArea(l,found,name);
            }
            // Fixed small normal-world sample, including terrain and underwater levels; no setBlock/setBiome.
            for(var p:List.of(l.getSharedSpawnPos(),new BlockPos(512,64,512),new BlockPos(-512,64,512),new BlockPos(512,64,-512)))observeArea(l,p,"fixed_sample");
            OUT.put("status","NATIVE_BOUNDED_CHECK_COMPLETED");OUT.put("natural_mob_deaths_observed",0);OUT.put("natural_drop_verification","PENDING: no naturally spawned mob killed in this no-player bounded scan");
        }catch(Throwable t){OUT.put("status","FAILED");OUT.put("error",t.toString());t.printStackTrace();}
        finally{save();System.out.println("ECOLOGY_NATIVE_FINISHED "+OUT.get("status"));server.halt(false);}
    }
    private static final Set<Long> FULL=new HashSet<>();
    private static final Set<String> STARTS=new HashSet<>();
    private static void observeArea(ServerLevel l,BlockPos center,String purpose){
        int cx=center.getX()>>4,cz=center.getZ()>>4;
        for(int x=cx-1;x<=cx+1;x++)for(int z=cz-1;z<=cz+1;z++){
            var c=l.getChunk(x,z);FULL.add(ChunkPos.asLong(x,z));
            for(var e:c.getAllStarts().entrySet()){
                var st=e.getValue();if(!st.isValid())continue;var id=l.registryAccess().registryOrThrow(Registries.STRUCTURE).getKey(e.getKey());String key=id+"@"+st.getChunkPos();
                if(STARTS.add(key))ROWS.add(row("kind","naturally_generated_start","structure",id.toString(),"start_chunk",st.getChunkPos().toString(),"bbox",st.getBoundingBox().toString(),"pieces",st.getPieces().size(),"observed_full_chunk",c.getPos().toString(),"purpose",purpose));
            }
        }
        for(int dx:new int[]{-4,0,4})for(int dz:new int[]{-4,0,4}){
            int x=center.getX()+dx,z=center.getZ()+dz;int surface=l.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,x,z);
            for(int y:new int[]{surface,surface-2,32,0,-32}){
                var p=new BlockPos(x,y,z);var b=l.getBiome(p);var br=l.registryAccess().registryOrThrow(Registries.BIOME);var eligible=new ArrayList<String>();var tags=new ArrayList<String>();
                for(var spec:SecondaryMobs.SPECS){if(b.is(TagKey.create(Registries.BIOME,new ResourceLocation("dynasty","secondary/"+spec.id()))))tags.add(spec.id());if(SpawnPlacements.checkSpawnRules(SecondaryMobs.TYPES.get(spec.id()).get(),l,MobSpawnType.NATURAL,p,l.random))eligible.add(spec.id());}
                var habitats=new ArrayList<String>();for(var name:List.of("ecology/tombs","blueprint/ghost_sites","secondary/ruins","ecology/roads","blueprint/clockwork_dog_sites"))if(LoadedStructureRegions.contains(l,p,new ResourceLocation("dynasty",name),0))habitats.add(name);
                ROWS.add(row("kind","normal_world_position","purpose",purpose,"pos",p.toShortString(),"biome",br.getKey(b.value()).toString(),"surface_y",surface,"day_time",l.getDayTime(),"night",l.isNight(),"raw_brightness",l.getMaxLocalRawBrightness(p),"sky_visible",l.canSeeSky(p),"fluid",l.getFluidState(p).getType().toString(),"biome_tag_members",tags,"native_placement_callback_pass",eligible,"loaded_structure_tags_radius0",habitats));
            }
        }
        OUT.put("distinct_full_chunks_requested",FULL.size());OUT.put("distinct_valid_structure_starts",STARTS.size());save();
    }
}
