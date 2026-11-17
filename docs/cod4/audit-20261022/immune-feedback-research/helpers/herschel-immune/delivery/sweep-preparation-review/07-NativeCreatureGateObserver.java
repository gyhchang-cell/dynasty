package com.dynasty.ecologyqa;

import com.google.gson.Gson;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.LocalMobCapCalculator;
import net.minecraft.world.level.NaturalSpawner;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import java.nio.file.*;
import java.util.*;

/** Private diagnostics. Future isolated bootstrap must explicitly register this class once on Forge EVENT_BUS. */
public final class NativeCreatureGateObserver {
    private static final boolean ENABLED=Boolean.getBoolean("ecology.nativegate.observe");
    private static final Gson JSON=new Gson();
    private static final ThreadLocal<Deque<Scope>> CONTEXT=ThreadLocal.withInitial(ArrayDeque::new);
    private static MinecraftServer server;
    private static Path output;
    private static long startedNanos,ticks,rows,nextScopeId;
    private static boolean stopped;
    private static final class Scope {
        final ServerLevel level;final ChunkPos chunk;final NaturalSpawner.SpawnState state;
        final boolean eligible;final long id,parentId;
        final List<Boolean> localReturns=new ArrayList<>();
        Object calculator;String calculatorIdentityFailure="";
        int foreignLocalReturns,combinedReturns;
        Scope(ServerLevel l,ChunkPos p,NaturalSpawner.SpawnState s,boolean eligible,long id,long parentId){
            level=l;chunk=p;state=s;this.eligible=eligible;this.id=id;this.parentId=parentId;
            if(!eligible)return;
            try {
                var fields=Arrays.stream(s.getClass().getDeclaredFields()).filter(f->f.getType()==LocalMobCapCalculator.class).toList();
                if(fields.size()!=1)throw new IllegalStateException("Expected exactly one native calculator field, found"+fields.size());
                var field=fields.get(0);field.setAccessible(true);calculator=field.get(s);
                if(calculator==null)throw new IllegalStateException("No native calculator identity");
            }catch(ReflectiveOperationException|RuntimeException e){calculator=null;calculatorIdentityFailure=e.toString();}
        }
    }
    private static Scope current(){return CONTEXT.get().peek();}
    private static Map<String,Object> row(Object... values){var out=new LinkedHashMap<String,Object>();for(int i=0;i<values.length;i+=2)out.put(values[i].toString(),values[i+1]);return out;}
    private static boolean active(){return ENABLED&&output!=null&&!stopped;}
    private static void record(String kind,Object... values){
        if(!active())return;
        // Admission limits further rows; a blocked I/O operation still needs the external watchdog.
        if(rows>=32000||System.nanoTime()-startedNanos>=300_000_000_000L){stopBudget("row_or_wall_admission");return;}
        var event=row(values);event.put("kind",kind);event.put("observer_ticks",ticks);event.put("overworld_game_time",server.overworld().getGameTime());
        try{Files.writeString(output.resolve("native-gates.jsonl"),JSON.toJson(event)+"\n",StandardOpenOption.CREATE,StandardOpenOption.APPEND);rows++;}
        catch(Exception ex){throw new IllegalStateException("Cannot preserve native gate evidence",ex);}
    }
    @SubscribeEvent public static void started(ServerStartedEvent event)throws Exception {
        if(!ENABLED)return;
        String target=System.getProperty("ecology.nativegate.output");if(target==null||target.isBlank())throw new IllegalArgumentException("Fresh private nativegate output required");
        if(server!=null)throw new IllegalStateException("One private observer session per JVM required");
        output=Path.of(target);Files.createDirectory(output);server=event.getServer();startedNanos=System.nanoTime();
        record("observer_started","world_mutations",false,"calls_spawn_or_cap_predicates",false,"runtime_version_bound","Minecraft1.20.1 Forge SRG methods pinned by independent bytecode receipt","external_controller_required",true);
    }
    private static void stopBudget(String reason){
        if(!active())return;stopped=true;CONTEXT.remove();
        try{Files.writeString(output.resolve("bounded-stop-request.txt"),"Observer budget "+reason+" exhausted. External controller must save/stop only this private QA. Rows="+rows+"\n",StandardOpenOption.CREATE_NEW);}
        catch(Exception e){throw new IllegalStateException("Cannot preserve budget stop request",e);}
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event)throws Exception {
        if(!active()||event.phase!=TickEvent.Phase.END)return;
        ticks++;
        if(!CONTEXT.get().isEmpty()){
            record("unclosed_native_scopes_at_tick_end","scope_ids",CONTEXT.get().stream().map(v->v.id).toList(),"reject_unpaired_scopes_as_complete_opportunities",true);
            CONTEXT.remove();
        }
        if(ticks>=4600||System.nanoTime()-startedNanos>=300_000_000_000L||rows>=32000)stopBudget("end_tick");
    }
    public static void begin(ServerLevel level,LevelChunk chunk,NaturalSpawner.SpawnState state,boolean friendlies,boolean enemies,boolean persistentPhase){
        if(!active())return;
        boolean eligible=level==server.overworld()&&friendlies&&persistentPhase;
        var stack=CONTEXT.get();if(!eligible&&stack.isEmpty())return;
        var scope=new Scope(level,chunk.getPos(),state,eligible,++nextScopeId,stack.isEmpty()?0:stack.peek().id);stack.push(scope);
        if(eligible)record("native_persistent_chunk_opportunity","scope_id",scope.id,"parent_scope_id",scope.parentId,"chunk",List.of(scope.chunk.x,scope.chunk.z),"dimension",level.dimension().location().toString(),"native_spawn_friendlies",friendlies,"native_spawn_enemies",enemies,"native_persistent_phase",persistentPhase,"native_calculator_identity_observed",scope.calculator!=null,"identity_read_failure",scope.calculatorIdentityFailure,"player_UUIDs",level.players().stream().map(p->p.getUUID().toString()).toList(),"does_not_prove_species_selected",true);
    }
    public static void local(Object self,MobCategory category,ChunkPos chunk,boolean actualReturn){
        var scope=current();if(!active()||scope==null||!scope.eligible||category!=MobCategory.CREATURE||!scope.chunk.equals(chunk))return;
        if(scope.calculator!=null&&scope.calculator==self)scope.localReturns.add(actualReturn);else scope.foreignLocalReturns++;
    }
    public static void combined(Object self,MobCategory category,ChunkPos chunk,boolean actualReturn){
        var scope=current();if(!active()||scope==null||!scope.eligible||self!=scope.state||category!=MobCategory.CREATURE||!scope.chunk.equals(chunk))return;
        scope.combinedReturns++;int chunks=scope.state.getSpawnableChunkCount();int count=scope.state.getMobCategoryCounts().getInt(category);int cap=category.getMaxInstancesPerChunk()*chunks/289;
        String pairing=scope.calculator==null?"UNKNOWN_CALCULATOR_IDENTITY":scope.foreignLocalReturns>0||scope.localReturns.size()>1?"ANOMALY_FOREIGN_OR_MULTIPLE_LOCAL_RETURNS":scope.localReturns.size()==1?"ONE_IDENTITY_MATCHED_LOCAL_RETURN":"LOCAL_RETURN_NOT_OBSERVED";
        record("actual_native_creature_category_return","scope_id",scope.id,"chunk",List.of(chunk.x,chunk.z),"spawnable_chunks",chunks,"native_count_read",count,"computed_vanilla_cap",cap,"read_count_below_vanilla_cap",count<cap,"actual_category_return",actualReturn,"actual_identity_matched_local_returns",List.copyOf(scope.localReturns),"foreign_local_return_count",scope.foreignLocalReturns,"pairing_status",pairing,"local_evaluation_observed",!scope.localReturns.isEmpty(),"not_local_gate_open_when_unobserved",true,"does_not_prove_weighted_selection_or_birth",true);
    }
    public static void end(){
        var stack=CONTEXT.get();if(stack.isEmpty())return;var scope=stack.pop();
        if(scope.eligible&&active())record("native_chunk_loop_return","scope_id",scope.id,"parent_scope_id",scope.parentId,"chunk",List.of(scope.chunk.x,scope.chunk.z),"creature_category_return_count",scope.combinedReturns,"foreign_local_return_count",scope.foreignLocalReturns,"identity_matched_local_return_count",scope.localReturns.size(),"paired_return",true);
        if(stack.isEmpty())CONTEXT.remove();
    }
}
