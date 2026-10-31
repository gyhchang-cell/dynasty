package com.dynasty.wangsiqa;

import com.google.gson.GsonBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.block.entity.SignBlockEntity;
import net.minecraft.world.level.block.WallSignBlock;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;
import java.util.*;

/** Actual natural FULL generation; no manual piece/block/entity/clock placement. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class WangsiSignAcceptance {
    private static final Map<String,Object> OUT=new LinkedHashMap<>();
    private static final List<Object> ROWS=new ArrayList<>();
    private static Path output;
    private static String phase;
    private static final int[][] OFFSETS={{48,44,0},{28,15,27},{59,15,27},{48,21,89}};
    private static final String[][] TEXT={{"阴阳界","生魂止步","酆都外郭","枉死城"},{"生魂当铺","旧契未赎","柜中无主","请留归路"},{"买命香火","烛灭客散","勿食供品","勿应招魂"},{"阎罗内衙","火线亮起先退","等铡刀抬起","穿过后再前行"}};
    private static Map<String,Object> row(Object... v){var m=new LinkedHashMap<String,Object>();for(int i=0;i<v.length;i+=2)m.put(v[i].toString(),v[i+1]);return m;}
    private static void save() throws Exception {OUT.put("observations",ROWS);Files.writeString(output.resolve(phase+".json"),new GsonBuilder().serializeNulls().setPrettyPrinting().create().toJson(OUT));}
    private static void require(boolean value,String why){if(!value)throw new IllegalStateException(why);}
    @SubscribeEvent public static void started(ServerStartedEvent event) {
        String requested=System.getProperty("wangsi.qa.output");if(requested==null)return;
        var server=event.getServer();phase=System.getProperty("wangsi.qa.phase","generate");output=Path.of(requested);
        try {
            require(phase.equals("generate")||phase.equals("reopen"),"Unknown phase");
            Files.createDirectories(output);require(!Files.exists(output.resolve(phase+".json")),"Refusing to overwrite evidence");
            OUT.put("phase",phase);OUT.put("seed",server.overworld().getSeed());OUT.put("connected_players",server.getPlayerCount());
            OUT.put("manual_piece_block_or_actor_placement",false);OUT.put("time_weather_or_biome_mutation",false);OUT.put("player_journey_or_visual_acceptance",false);
            require(server.overworld().getSeed()==20261023L,"Wrong seed");require(server.getPlayerCount()==0,"Private server must have no players");
            ServerLevel level=server.getLevel(ResourceKey.create(Registries.DIMENSION,new ResourceLocation("dynasty:underworld")));
            require(level!=null,"Missing native underworld");OUT.put("generator",level.getChunkSource().getGenerator().getClass().getName());
            require(!(level.getChunkSource().getGenerator() instanceof net.minecraft.world.level.levelgen.FlatLevelSource),"Flat fixture is invalid");
            var structure=level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(new ResourceLocation("dynasty:yinsi_wangsi_cheng"));
            require(structure!=null,"Missing registered structure");
            OUT.put("native_FULL_request_chunk",List.of(-6520,-2626));save();
            var start=level.getChunk(-6520,-2626).getStartForStructure(structure);
            require(start!=null&&start.isValid(),"No natural valid Wangsi start");require(start.getPieces().size()==48,"Natural city must preserve all48pieces");
            var box=start.getBoundingBox();OUT.put("bbox",box.toString());OUT.put("pieces",start.getPieces().size());save();
            int chunks=0;
            for(int x=box.minX()>>4;x<=box.maxX()>>4;x++)for(int z=box.minZ()>>4;z<=box.maxZ()>>4;z++){
                var chunk=level.getChunk(x,z);require(chunk.getStatus()==net.minecraft.world.level.chunk.ChunkStatus.FULL,"Chunk not FULL");chunks++;OUT.put("full_chunks",chunks);save();
            }
            require(chunks==48,"Unexpected natural city chunk footprint");
            for(int i=0;i<OFFSETS.length;i++){
                int[] off=OFFSETS[i];var pos=new BlockPos(box.minX()+off[0],box.minY()+off[1],box.minZ()+off[2]);
                var state=level.getBlockState(pos);var entity=level.getBlockEntity(pos);
                require(entity instanceof SignBlockEntity,"Sign absent at "+pos);var sign=(SignBlockEntity)entity;
                var messages=new ArrayList<String>();for(var message:sign.getFrontText().getMessages(false))messages.add(message.getString());
                var facing=state.getValue(WallSignBlock.FACING);var support=pos.relative(facing.getOpposite());
                ROWS.add(row("kind","natural_sign","pos",pos.toShortString(),"messages",messages,"waxed",sign.isWaxed(),"color",sign.getFrontText().getColor().getName(),"facing",facing.getName(),"support_pos",support.toShortString(),"support_state",level.getBlockState(support).toString(),"can_survive",state.canSurvive(level,pos),"has_level",sign.hasLevel(),"nbt",sign.saveWithFullMetadata().toString()));save();
                require(messages.equals(Arrays.asList(TEXT[i])),"Chinese text changed");require(sign.isWaxed(),"Sign not waxed");require(facing==Direction.NORTH,"Sign faces unsupported side");require(state.canSurvive(level,pos),"Unsupported sign");require(sign.hasLevel(),"FULL sign has no Level");
                require(sign.getFrontText().getColor()==(i==0?DyeColor.RED:DyeColor.BLACK),"Unexpected text color");
                // Native detached NBT round-trip, then normal attached-world neighbor notification.
                var detached=new SignBlockEntity(pos,state);detached.load(sign.saveWithoutMetadata());
                require(!detached.hasLevel()&&detached.isWaxed(),"Detached load/wax failed");
                require(Arrays.stream(detached.getFrontText().getMessages(false)).map(c->c.getString()).toList().equals(messages),"Detached text roundtrip failed");
                state.neighborChanged(level,pos,level.getBlockState(support).getBlock(),support,false);
                require(level.getBlockEntity(pos)==sign,"Native neighbor notification removed sign");
            }
            server.saveEverything(false,true,true);OUT.put("status","PASS");OUT.put("save_completed",true);save();
        } catch(Throwable t){OUT.put("status","FAILED");OUT.put("error",t.toString());t.printStackTrace();try{save();}catch(Exception ignored){}}
        finally {System.out.println("WANGSI_SIGN_QA_FINISHED "+OUT.get("status"));server.halt(false);}
    }
}
