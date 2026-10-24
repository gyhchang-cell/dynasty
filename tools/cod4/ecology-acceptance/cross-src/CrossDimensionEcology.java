package com.dynasty.expansion;

import com.google.gson.GsonBuilder;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;
import java.util.*;

/** Independent normal generator only. No artificial pieces, blocks, biomes, actors or clock changes. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class CrossDimensionEcology {
    static final Map<String,Object> OUT=new LinkedHashMap<>();
    static final List<Object> ROWS=new ArrayList<>();
    static Map<String,Object> row(Object...v){var m=new LinkedHashMap<String,Object>();for(int i=0;i<v.length;i+=2)m.put(v[i].toString(),v[i+1]);return m;}
    static void save(){try{OUT.put("observations",ROWS);Files.writeString(Path.of(System.getProperty("ecology.crossOutput")),new GsonBuilder().serializeNulls().setPrettyPrinting().create().toJson(OUT));}catch(Exception e){throw new RuntimeException(e);}}
    @SubscribeEvent public static void started(ServerStartedEvent event){
        if(System.getProperty("ecology.crossOutput")==null)return;
        var server=event.getServer();
        OUT.put("seed",server.overworld().getSeed());OUT.put("artificial_placement_or_spawn",false);OUT.put("time_weather_or_biome_mutation",false);OUT.put("player_journey_tested",false);
        try{
            var key=ResourceKey.create(Registries.DIMENSION,new ResourceLocation("dynasty:underworld"));var l=server.getLevel(key);
            if(l==null)throw new IllegalStateException("Registered underworld level missing");
            OUT.put("dimension",l.dimension().location().toString());OUT.put("generator",l.getChunkSource().getGenerator().getClass().getName());
            var br=l.registryAccess().registryOrThrow(Registries.BIOME);var sr=l.registryAccess().registryOrThrow(Registries.STRUCTURE);
            for(var b:l.getChunkSource().getGenerator().getBiomeSource().possibleBiomes()){
                var entries=new ArrayList<Object>();
                for(var spec:SecondaryMobs.SPECS){var type=SecondaryMobs.TYPES.get(spec.id()).get();
                    var spawn=b.value().getMobSettings().getMobs(type.getCategory()).unwrap().stream().filter(e->e.type==type).map(e->row("weight",e.getWeight().asInt(),"min",e.minCount,"max",e.maxCount)).toList();
                    entries.add(row("species",spec.id(),"biome_tag",b.is(TagKey.create(Registries.BIOME,new ResourceLocation("dynasty","secondary/"+spec.id()))),"spawn_entries",spawn));
                }
                ROWS.add(row("kind","underworld_biome","biome",br.getKey(b.value()).toString(),"species",entries));
            }
            for(var tag:List.of("blueprint/ghost_sites","secondary/ruins","ecology/ruined_villages","ecology/tombs"))ROWS.add(row("kind","resolved_structure_tag","tag",tag,"members",sr.getTag(TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty",tag))).map(s->s.stream().map(h->sr.getKey(h.value()).toString()).toList()).orElse(List.of())));
            sample(l,new BlockPos(0,80,0),"underworld_origin");save();
            // Existing legacy gate is only a positive control for natural underworld generation, never a whole ghost market.
            var gate=sr.getHolderOrThrow(ResourceKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty:legacy_ghost_gate")));
            long gateBegin=System.nanoTime();var gateFound=l.getChunkSource().getGenerator().findNearestMapStructure(l,HolderSet.direct(gate),BlockPos.ZERO,4,false);
            ROWS.add(row("kind","native_control_locate","structure","dynasty:legacy_ghost_gate","radius_placement_regions",4,"found",gateFound==null?null:gateFound.getFirst().toShortString(),"elapsed_ms",(System.nanoTime()-gateBegin)/1000000));save();
            if(gateFound!=null){var gp=gateFound.getFirst();var gc=l.getChunk(gp.getX()>>4,gp.getZ()>>4);var gs=gc.getStartForStructure(gate.value());ROWS.add(row("kind","natural_control_start","structure","dynasty:legacy_ghost_gate","valid",gs!=null&&gs.isValid(),"bbox",gs==null?null:gs.getBoundingBox().toString(),"pieces",gs==null?0:gs.getPieces().size(),"not_a_whole_market",true));save();}
            var holder=sr.getHolderOrThrow(ResourceKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty:yinsi_wangsi_cheng")));
            var placements=l.getChunkSource().getGeneratorState().getPlacementsForStructure(holder);
            ROWS.add(row("kind","resolved_wangsi_placements","count",placements.size(),"placements",placements.stream().map(x->x.getClass().getName()).toList(),"possible_sets",l.getChunkSource().getGeneratorState().possibleStructureSets().size()));save();
            for(int radius:new int[]{16}){
                long start=System.nanoTime();var found=l.getChunkSource().getGenerator().findNearestMapStructure(l,HolderSet.direct(holder),BlockPos.ZERO,radius,false);
                ROWS.add(row("kind","native_locate","structure","dynasty:yinsi_wangsi_cheng","origin","0, 0, 0","radius_placement_regions",radius,"found",found==null?null:found.getFirst().toShortString(),"elapsed_ms",(System.nanoTime()-start)/1000000));save();
                if(found==null)continue;
                var p=found.getFirst();var chunk=l.getChunk(p.getX()>>4,p.getZ()>>4);var st=chunk.getStartForStructure(holder.value());
                if(st==null||!st.isValid())throw new IllegalStateException("Locate hit has no valid natural StructureStart");
                var box=st.getBoundingBox();ROWS.add(row("kind","natural_wangsi_start","start_chunk",st.getChunkPos().toString(),"bbox",box.toString(),"pieces",st.getPieces().size(),"piece_classes",st.getPieces().stream().map(x->x.getClass().getName()).distinct().toList()));save();
                // SOUTH-oriented clipped columns share origin = overall bbox minimum. Actual native FULL chunks generate signs.
                for(var off:List.of(new BlockPos(28,15,27),new BlockPos(59,15,27),new BlockPos(48,44,0))){
                    var q=new BlockPos(box.minX()+off.getX(),box.minY()+off.getY(),box.minZ()+off.getZ());l.getChunk(q.getX()>>4,q.getZ()>>4);
                    var be=l.getBlockEntity(q);ROWS.add(row("kind","natural_market_anchor","local_offset",off.toShortString(),"pos",q.toShortString(),"state",l.getBlockState(q).toString(),"block_entity",be==null?null:be.saveWithFullMetadata().toString()));sample(l,q.above(),"natural_wangsi_market");save();
                }
                OUT.put("natural_wangsi_observed",true);break;
            }
            if(!OUT.containsKey("natural_wangsi_observed")){
                var generator=l.getChunkSource().getGenerator();int candidates=0,accepted=0;
                for(var placement:placements)if(placement instanceof net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement spread){
                    for(int rx=-17;rx<=-17;rx++)for(int rz=-7;rz<=-7;rz++){
                        var cp=spread.getPotentialStructureChunk(l.getSeed(),rx*spread.spacing(),rz*spread.spacing());var heights=new ArrayList<Integer>();
                        for(int dx:new int[]{8,48,88})for(int dz:new int[]{8,64,120})heights.add(generator.getFirstFreeHeight(cp.getMinBlockX()+dx,cp.getMinBlockZ()+dz,Heightmap.Types.OCEAN_FLOOR_WG,l,l.getChunkSource().randomState()));
                        var ctx=new net.minecraft.world.level.levelgen.structure.Structure.GenerationContext(l.registryAccess(),generator,generator.getBiomeSource(),l.getChunkSource().randomState(),server.getStructureManager(),l.getSeed(),cp,l,holder.value().biomes()::contains);
                        boolean valid=holder.value().findValidGenerationPoint(ctx).isPresent();candidates++;if(valid){accepted++;
                            ROWS.add(row("kind","accepted_native_candidate_before_FULL","region",rx+", "+rz,"candidate_chunk",cp.toString(),"origin_x",cp.getMinBlockX(),"origin_z",cp.getMinBlockZ(),"ocean_floor_WG_3x3",heights,"placement_is_structure_chunk",spread.isStructureChunk(l.getChunkSource().getGeneratorState(),cp.x,cp.z)));
                            OUT.put("candidate_region_denominator",candidates);OUT.put("production_generation_points_accepted",accepted);save();
                            if(spread.isStructureChunk(l.getChunkSource().getGeneratorState(),cp.x,cp.z)){
                                OUT.put("native_FULL_request_chunk",cp.toString());save();
                                var actual=l.getChunk(cp.x,cp.z).getStartForStructure(holder.value());
                                ROWS.add(row("kind","candidate_natural_wangsi_start","candidate_chunk",cp.toString(),"valid",actual!=null&&actual.isValid(),"pieces",actual==null?0:actual.getPieces().size(),"bbox",actual==null?null:actual.getBoundingBox().toString()));
                                if(actual!=null&&actual.isValid()){OUT.put("natural_wangsi_observed",true);var box=actual.getBoundingBox();
                                    for(var off:List.of(new BlockPos(28,15,27),new BlockPos(59,15,27))){var q=new BlockPos(box.minX()+off.getX(),box.minY()+off.getY(),box.minZ()+off.getZ());l.getChunk(q.getX()>>4,q.getZ()>>4);var be=l.getBlockEntity(q);ROWS.add(row("kind","natural_market_anchor","local_offset",off.toShortString(),"pos",q.toShortString(),"state",l.getBlockState(q).toString(),"block_entity",be==null?null:be.saveWithFullMetadata().toString()));sample(l,q.above(),"natural_wangsi_market");}
                                }
                            }
                        }
                        int x=cp.getMinBlockX(),z=cp.getMinBlockZ();var collisions=new ArrayList<String>();var state=l.getChunkSource().getGeneratorState();
                        // Read-only attribution of the exact existing reserved-slot branch. These are theoretical slots, not extra natural buildings.
                        for(var setHolder:state.possibleStructureSets()){
                            if(setHolder.unwrapKey().map(k->!k.location().getNamespace().equals("dynasty")).orElse(true))continue;
                            var set=setHolder.value();if(!(set.placement() instanceof net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement other)||set.structures().stream().anyMatch(e->e.structure().value()==holder.value()))continue;
                            int minX=(x-48)>>4,maxX=(x+143)>>4,minZ=(z-48)>>4,maxZ=(z+175)>>4;
                            for(int arx=Math.floorDiv(minX,other.spacing());arx<=Math.floorDiv(maxX,other.spacing());arx++)for(int arz=Math.floorDiv(minZ,other.spacing());arz<=Math.floorDiv(maxZ,other.spacing());arz++){
                                var pos=other.getPotentialStructureChunk(l.getSeed(),arx*other.spacing(),arz*other.spacing());if(pos.x>=minX&&pos.x<=maxX&&pos.z>=minZ&&pos.z<=maxZ&&other.isStructureChunk(state,pos.x,pos.z))collisions.add(setHolder.unwrapKey().map(k->k.location().toString()).orElse("unkeyed")+"@"+pos);
                            }
                        }
                        ROWS.add(row("kind","native_candidate_generation_point","region",rx+", "+rz,"candidate_chunk",cp.toString(),"placement_is_structure_chunk",spread.isStructureChunk(state,cp.x,cp.z),"ocean_floor_WG_3x3",heights,"production_findValidGenerationPoint_present",valid,"read_only_reserved_slot_conflicts",collisions));
                    }
                }
                OUT.put("candidate_region_denominator",candidates);OUT.put("production_generation_points_accepted",accepted);save();
            }
            OUT.put("status","NATIVE_BOUNDED_CROSS_DIMENSION_CHECK_COMPLETED");
        }catch(Throwable t){OUT.put("status","FAILED");OUT.put("error",t.toString());t.printStackTrace();}
        finally{save();System.out.println("ECOLOGY_CROSS_FINISHED "+OUT.get("status"));server.halt(false);}
    }
    static void sample(ServerLevel l,BlockPos p,String purpose){
        l.getChunk(p.getX()>>4,p.getZ()>>4);var b=l.getBiome(p);var results=new ArrayList<Object>();
        for(var s:SecondaryMobs.SPECS)results.add(row("species",s.id(),"production_eligible",SecondarySpawnHooks.eligible(l,p,s.id()),"native_NATURAL_callback",SpawnPlacements.checkSpawnRules(SecondaryMobs.TYPES.get(s.id()).get(),l,MobSpawnType.NATURAL,p,l.random)));
        ROWS.add(row("kind","native_position","purpose",purpose,"pos",p.toShortString(),"biome",l.registryAccess().registryOrThrow(Registries.BIOME).getKey(b.value()).toString(),"day_time",l.getDayTime(),"ground",l.getBlockState(p.below()).toString(),"results",results));
    }
}
