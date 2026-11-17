package com.dynasty.wangsiqa;

import com.dynasty.expansion.SmallInteractions;
import com.google.gson.GsonBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderSet;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;
import java.util.*;

/** Read-only native natural placement, separate from timed or network acceptance. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class NaturalInteractionPlacementAcceptance {
    private static final Map<String,Object> OUT=new LinkedHashMap<>();
    private static final List<Object> ROWS=new ArrayList<>();
    private static Path target;
    private static Map<String,Object> row(Object...v){var m=new LinkedHashMap<String,Object>();for(int i=0;i<v.length;i+=2)m.put(v[i].toString(),v[i+1]);return m;}
    private static void save() throws Exception {OUT.put("observations",ROWS);Files.writeString(target,new GsonBuilder().setPrettyPrinting().serializeNulls().create().toJson(OUT));}
    private static void require(boolean b,String why){if(!b)throw new IllegalStateException(why);}
    @SubscribeEvent public static void started(ServerStartedEvent event){
        String requested=System.getProperty("interactions.qa.output");if(requested==null)return;
        var server=event.getServer();
        try{
            target=Path.of(requested).resolve("natural_interactions.json");Files.createDirectories(target.getParent());require(!Files.exists(target),"Do not overwrite evidence");
            var level=server.overworld();OUT.put("seed",level.getSeed());OUT.put("manual_placement",false);OUT.put("time_weather_biome_mutation",false);OUT.put("players",server.getPlayerCount());OUT.put("actual_client_interaction_or_timing_test",false);
            require(level.getSeed()==20261023L&&server.getPlayerCount()==0,"Unexpected private world");
            OUT.put("generator",level.getChunkSource().getGenerator().getClass().getName());
            var registry=level.registryAccess().registryOrThrow(Registries.STRUCTURE);
            String[] structures={"post_house","herbal_retreat","desert_caravan"};
            String[][] sites={{"wayside_shrine","old_weapon_rack","puzzle_box","wayside_tea_stall","broken_stele"},{"herb_spot","nameless_tomb","sword_scar_wall","mortuary_room","broken_waterwheel"},{"abandoned_armory","battlefield_remnant","ghost_market_boat","old_bellows","ancient_well"}};
            BlockPos[] origins={new BlockPos(752,80,-640),new BlockPos(-64,80,-80),new BlockPos(2112,80,-720)};
            var transform=StructurePiece.class.getDeclaredMethod("getWorldPos",int.class,int.class,int.class);transform.setAccessible(true);
            int accepted=0;
            for(int style=0;style<structures.length;style++){
                var id=new ResourceLocation("dynasty",structures[style]);var holder=registry.getHolderOrThrow(ResourceKey.create(Registries.STRUCTURE,id));
                long begin=System.nanoTime();var found=level.getChunkSource().getGenerator().findNearestMapStructure(level,HolderSet.direct(holder),origins[style],4,false);
                ROWS.add(row("kind","native_locate","structure",id.toString(),"origin",origins[style].toShortString(),"radius_regions",4,"found",found==null?null:found.getFirst().toShortString(),"elapsed_ms",(System.nanoTime()-begin)/1000000));save();
                if(found==null)continue;
                var p=found.getFirst();net.minecraft.world.level.levelgen.structure.StructureStart start=null;
                for(int dx=-1;dx<=1&&start==null;dx++)for(int dz=-1;dz<=1&&start==null;dz++){
                    var candidate=level.getChunk((p.getX()>>4)+dx,(p.getZ()>>4)+dz).getStartForStructure(holder.value());
                    if(candidate!=null&&candidate.isValid())start=candidate;
                }
                require(start!=null,"Locate result without native start");require(start.getPieces().size()==1,"Unexpected travel site pieces");
                var piece=start.getPieces().get(0);var box=piece.getBoundingBox();
                for(int x=box.minX()>>4;x<=box.maxX()>>4;x++)for(int z=box.minZ()>>4;z<=box.maxZ()>>4;z++)level.getChunk(x,z);
                ROWS.add(row("kind","natural_structure","structure",id.toString(),"start_chunk",start.getChunkPos().toString(),"bbox",box.toString(),"orientation",piece.getOrientation().getName()));save();
                for(int i=0;i<5;i++){
                    var pos=((BlockPos)transform.invoke(piece,5+i*4,1,28)).immutable();
                    var approach=((BlockPos)transform.invoke(piece,5+i*4,1,27)).immutable();var state=level.getBlockState(pos);
                    boolean expected=state.is(SmallInteractions.ENTRIES.get(sites[style][i]).get());
                    var footprint=new AABB(approach.getX()+.2,approach.getY(),approach.getZ()+.2,approach.getX()+.8,approach.getY()+1.8,approach.getZ()+.8);
                    boolean standing=level.getBlockState(approach.below()).isFaceSturdy(level,approach.below(),Direction.UP);
                    boolean clear=level.noCollision(footprint);boolean solid=!state.getCollisionShape(level,pos).isEmpty();
                    ROWS.add(row("kind","natural_interaction","id",sites[style][i],"structure",id.toString(),"pos",pos.toShortString(),"state",state.toString(),"expected_registered_block",expected,"collision_nonempty",solid,"outline_nonempty",!state.getShape(level,pos).isEmpty(),"approach",approach.toShortString(),"approach_ground_support",standing,"approach_body_clear",clear));save();
                    require(expected&&solid&&standing&&clear,"Natural placement/approach failed for "+sites[style][i]);accepted++;
                }
            }
            OUT.put("natural_interactions_verified",accepted);OUT.put("status",accepted==15?"PASS":"BOUNDED_SEARCH_INCOMPLETE");server.saveEverything(false,true,true);save();
        }catch(Throwable t){OUT.put("status","FAILED");OUT.put("error",t.toString());t.printStackTrace();try{save();}catch(Exception ignored){}}
        finally{System.out.println("NATURAL_INTERACTIONS_QA_FINISHED "+OUT.get("status"));server.halt(false);}
    }
}
