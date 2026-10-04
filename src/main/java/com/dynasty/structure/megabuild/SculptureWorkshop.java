package com.dynasty.structure.megabuild;

import com.dynasty.ritual.ZhenyuanRitualService;
import com.mojang.logging.LogUtils;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.server.ServerLifecycleHooks;
import org.slf4j.Logger;

import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/** Explicit original-art placement: asynchronous resource decode, bounded preflight and safe writes. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class SculptureWorkshop {
    private static final Logger LOG=LogUtils.getLogger();
    private static final int MAX_SCAN=8192,MAX_WRITES=256;
    private static final long TIME_BUDGET_NS=4_000_000;
    private static Job active;
    private static CompletableFuture<SculptureBlueprint> loading;
    private static MinecraftServer loadingServer;
    private SculptureWorkshop(){}

    @SubscribeEvent public static void commands(RegisterCommandsEvent event){
        var place=Commands.literal("place");
        for(String id:new String[]{"longque_sanctuary","yunqi_manor"})
            place.then(Commands.literal(id).executes(c->start(c.getSource(),id)));
        event.getDispatcher().register(Commands.literal("dynasty_build").requires(s->s.hasPermission(2)).then(place));
    }
    private static int start(CommandSourceStack s,String id){
        if(active!=null||loading!=null){s.sendFailure(Component.literal("建筑正在直接生成，请等待完成，勿强退。"));return 0;}
        var d=SculptureSavedData.get(s.getServer());
        // Preserve old receipts. Repeating the same place command safely completes an interrupted paste.
        if(d.present()){
            if(!d.id.equals(id)){s.sendFailure(Component.literal("有未完成的 "+d.id+"；先执行 /dynasty_build place "+d.id+" 完成原位置建筑。"));return 0;}
            if(!d.hash.isEmpty()&&!d.phase.equals("binding")){
                d.phase=d.placedVoxels.isEmpty()?"checking":"recovering";d.chunk=d.cell=0;d.checked=0;
            }
        }else{
            d.clear();d.id=id;d.dimension=s.getLevel().dimension().location().toString();
            d.owner=s.getEntity() instanceof ServerPlayer p?p.getUUID():null;
            d.origin=BlockPos.containing(s.getPosition());
        }
        d.paused=false;d.direct=true;d.setDirty();
        s.getServer().overworld().getDataStorage().save();beginLoad(s.getServer(),d);
        s.sendSuccess(()->Component.literal("正在直接生成建筑（从脚下向北、左右居中）。可能短暂卡顿，请勿强退；不会覆盖已有建筑。"),false);return 1;
    }
    private static void beginLoad(MinecraftServer server,SculptureSavedData data){
        loadingServer=server;String id=data.id;var manager=server.getResourceManager();
        loading=CompletableFuture.supplyAsync(()->{try{return SculptureBlueprint.load(manager,id);}catch(Exception e){throw new java.util.concurrent.CompletionException(e);}});
    }
    private static void cancelLoading(){if(loading!=null)loading.cancel(false);loading=null;loadingServer=null;}
    private static void tell(MinecraftServer server,SculptureSavedData d,String message){
        d.message=message;d.setDirty();LOG.info("Sculpture {}: {}",d.id,message);
        if(d.owner!=null){var p=server.getPlayerList().getPlayer(d.owner);if(p!=null)p.sendSystemMessage(Component.literal(message));}
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event){
        if(event.phase!=TickEvent.Phase.END)return;
        MinecraftServer server=ServerLifecycleHooks.getCurrentServer();if(server==null)return;
        if(loading!=null&&loading.isDone()){
            var d=SculptureSavedData.get(server);
            try{
                if(server!=loadingServer)throw new IllegalStateException("Server changed during resource load");
                var blueprint=loading.join();loading=null;loadingServer=null;
                if(d.hash.isEmpty()){d.origin=d.origin.offset(-blueprint.width/2,0,-blueprint.length);d.hash=blueprint.manifestSha256;d.setDirty();server.overworld().getDataStorage().save();}
                active=new Job(server,d,blueprint);
            }catch(Exception e){cancelLoading();active=null;d.paused=true;tell(server,d,"资源/边界检查失败，未覆盖原建筑："+rootMessage(e));}
        }
        if(active!=null){Job job=active;try{job.placeDirect();if(job.done)active=null;}catch(Exception e){job.checkpoint();job.data.paused=true;job.data.direct=false;tell(server,job.data,"生成中止，已放部分保留："+rootMessage(e)+"。处理冲突后再次执行 /dynasty_build place "+job.data.id+"。");active=null;}}
    }
    private static String rootMessage(Throwable e){while(e.getCause()!=null)e=e.getCause();return e.getMessage()==null?e.getClass().getSimpleName():e.getMessage();}
    @SubscribeEvent public static void stop(ServerStoppingEvent event){
        if(active!=null){active.data.paused=true;active.flush();}active=null;cancelLoading();
    }

    static final class Job {
        final MinecraftServer server;final ServerLevel level;final SculptureSavedData data;final SculptureBlueprint blueprint;
        final SculptureCursor cursor;final BlockState[] palette;final boolean[] fluid;final Map<Integer,Integer> altarIndex=new HashMap<>();
        boolean done;int ticks;
        Job(MinecraftServer server,SculptureSavedData data,SculptureBlueprint b)throws Exception{
            this.server=server;this.data=data;blueprint=b;
            if(!b.manifestSha256.equals(data.hash))throw new IllegalArgumentException("建筑资源（含材质/坐标/祭坛）已更改；拒绝续建到旧检查点");
            level=server.getLevel(ResourceKey.create(Registries.DIMENSION,new ResourceLocation(data.dimension)));
            if(level==null)throw new IllegalArgumentException("目标维度不存在");
            if(data.dimension.equals("dynasty:zhenyuan_arena"))throw new IllegalArgumentException("战斗专用维度禁止安装巨型建筑");
            if(!java.util.Set.of("checking","recovering","placing","fluids","binding").contains(data.phase))throw new IllegalArgumentException("无效施工阶段");
            if(data.placedVoxels.length()>b.volume())throw new IllegalArgumentException("归属回执超出模型范围");
            validateBounds();cursor=new SculptureCursor(data.origin.getX(),data.origin.getY(),data.origin.getZ(),b.width,b.height,b.length);cursor.chunk=data.chunk;cursor.cell=data.cell;
            if(!cursor.valid())throw new IllegalArgumentException("无效施工检查点");
            palette=new BlockState[b.palette.size()];fluid=new boolean[palette.length];
            for(int i=0;i<palette.length;i++){palette[i]=BlockStateParser.parseForBlock(BuiltInRegistries.BLOCK.asLookup(),b.palette.get(i),false).blockState();fluid[i]=!palette[i].getFluidState().isEmpty();}
            for(int i=0;i<b.ritualOwned.size();i++){var cell=b.ritualOwned.get(i);altarIndex.put(cell.x()+cell.z()*b.width+cell.y()*b.width*b.length,i);}
        }
        void validateBounds(){
            BlockPos max=data.origin.offset(blueprint.width-1,blueprint.height-1,blueprint.length-1);
            if(level.isOutsideBuildHeight(data.origin)||level.isOutsideBuildHeight(max))throw new IllegalArgumentException("超过维度高度；请从更低位置建造");
            if(!level.getWorldBorder().isWithinBounds(data.origin)||!level.getWorldBorder().isWithinBounds(max))throw new IllegalArgumentException("超过世界边界");
        }
        void checkpoint(){data.chunk=cursor.chunk;data.cell=cursor.cell;data.setDirty();}
        void flush(){
            checkpoint();
            // Explicit pause/stop only, not the tick hot path. World data first, receipt ledger second.
            level.getChunkSource().save(true);server.overworld().getDataStorage().save();
        }
        void step()throws Exception{
            step(false);
        }
        void placeDirect()throws Exception{
            long started=System.nanoTime();
            // Same preflight, receipts, fluid order and altar binding; only remove pacing.
            // ponytail: this explicitly blocks the server thread; use paced mode on watchdog servers.
            while(!done)step(true);
            LOG.info("Direct sculpture placement completed in {} ms",(System.nanoTime()-started)/1_000_000);
        }
        void step(boolean direct)throws Exception{
            validateBounds();
            if(data.phase.equals("binding")){finish();return;}
            long deadline=System.nanoTime()+TIME_BUDGET_NS;int scanned=0,writes=0,startChunk=cursor.chunk;
            if(cursor.done()){nextPhase();return;}
            // At most one world chunk is requested per tick. Chunk generation itself is Minecraft work.
            level.getChunk(cursor.chunkX(),cursor.chunkZ());
            var entities=level.getEntitiesOfClass(LivingEntity.class,new AABB(cursor.chunkX()*16,level.getMinBuildHeight(),cursor.chunkZ()*16,cursor.chunkX()*16+16,level.getMaxBuildHeight(),cursor.chunkZ()*16+16),e->!e.isSpectator());
            BlockPos.MutableBlockPos pos=new BlockPos.MutableBlockPos();
            do{
                pos.set(cursor.x(),cursor.y(),cursor.z());int x=pos.getX()-data.origin.getX(),y=pos.getY()-data.origin.getY(),z=pos.getZ()-data.origin.getZ(),id=blueprint.at(x,y,z),voxel=x+z*blueprint.width+y*blueprint.width*blueprint.length;
                BlockState current=level.getBlockState(pos);
                if(data.phase.equals("checking")||data.phase.equals("recovering")){
                    if(data.phase.equals("recovering")&&data.placedVoxels.get(voxel)){
                        if(id==0)throw new IllegalStateException("空气格不应拥有施工回执");
                        if(current.isAir()){data.placedVoxels.clear(voxel);data.placed=Math.max(0,data.placed-1);Integer owner=altarIndex.get(voxel);if(owner!=null)data.altarWrites.remove(owner);}
                        else if(!current.equals(palette[id]))throw new IllegalStateException("施工回执位置被改动 "+pos.toShortString()+"；保留玩家改动，拒绝覆盖");
                    }else if(!current.isAir())throw new IllegalStateException("预检发现没有本任务回执的方块 "+pos.toShortString()+"（"+current+"）；即使同材质也不会认领/覆盖。选择空地或人工检查冲突");
                    data.checked++;
                }else if(id!=0&&(data.phase.equals("fluids")==fluid[id])){
                    if(data.placedVoxels.get(voxel)){
                        if(!current.equals(palette[id]))throw new IllegalStateException("已有施工回执与方块不一致 "+pos.toShortString()+"；请 resume 重新核对");
                        cursor.next();scanned++;continue;
                    }
                    // Re-check at the actual write: never overwrite even when preflight was clean.
                    if(!current.isAir())throw new IllegalStateException("位置已被占用 "+pos.toShortString()+"，不会覆盖该方块");
                    for(var entity:entities)if(entity.getBoundingBox().intersects(pos.getX(),pos.getY(),pos.getZ(),pos.getX()+1,pos.getY()+1,pos.getZ()+1))throw new IllegalStateException("有生物/玩家挡在待放方块 "+pos.toShortString());
                    if(!level.setBlock(pos,palette[id],Block.UPDATE_CLIENTS|Block.UPDATE_KNOWN_SHAPE))throw new IllegalStateException("放置被拒绝 "+pos.toShortString());
                    data.placedVoxels.set(voxel);Integer ownerIndex=altarIndex.get(voxel);if(ownerIndex!=null)data.altarWrites.add(ownerIndex);
                    data.placed++;writes++;
                }
                cursor.next();scanned++;
            }while(!cursor.done()&&cursor.chunk==startChunk&&(direct||(scanned<MAX_SCAN&&writes<MAX_WRITES&&System.nanoTime()<deadline)));
            checkpoint();
            if(cursor.done())nextPhase();
        }
        void nextPhase(){
            // Binding may be retried idempotently. Do not persist that phase ahead of world chunks.
            if(data.phase.equals("fluids"))flush();
            data.phase=switch(data.phase){case "checking","recovering"->"placing";case "placing"->"fluids";default->"binding";};
            cursor.chunk=cursor.cell=0;checkpoint();
        }
        void finish(){
            // Ensure placed chunks reach storage before registering ritual cleanup ownership.
            flush();
            if(blueprint.ritualCore!=null){
                if(data.altarWrites.size()!=blueprint.ritualOwned.size())throw new IllegalStateException("祭坛实际新放置归属不完整，拒绝绑定/清理任何未知方块");
                Map<BlockPos,BlockState> owned=new LinkedHashMap<>();Map<Integer,BlockPos> nodes=new LinkedHashMap<>();
                for(int index:data.altarWrites){var c=blueprint.ritualOwned.get(index);owned.put(data.origin.offset(c.x(),c.y(),c.z()),palette[blueprint.at(c.x(),c.y(),c.z())]);}
                for(var n:blueprint.ritualNodes)nodes.put(n.slot(),data.origin.offset(n.x(),n.y(),n.z()));
                int[] c=blueprint.ritualCore;BlockPos core=data.origin.offset(c[0],c[1],c[2]);
                if(!ZhenyuanRitualService.bindImportedAltar(level,core,owned,nodes))throw new IllegalStateException("祭坛绑定验证失败，建筑已保留；检查日志后重复 place 指令重试");
                com.dynasty.ritual.ZhenyuanSceneLighting.mouth(level,core,nodes.values());
                // Persist configured block-entity links too, before clearing the import checkpoint.
                level.getChunkSource().save(true);level.getDataStorage().save();
                tell(server,data,"龙阙已完成，功能祭坛中心 "+core.toShortString()+"。五座供台已连接；只祭坛自有上层会消隐，龙与平台保留。");
            }else tell(server,data,"云栖庄园完成："+data.placed+" 个新方块。池塘、屋顶与内饰已加入，原建筑没有被覆盖。");
            // Persist visit bounds only after successful placement and ritual binding.
            SculptureStorySites.get(level).register(blueprint.id,data.origin,blueprint.width,blueprint.height,blueprint.length);
            level.getDataStorage().save();
            data.clear();server.overworld().getDataStorage().save();done=true;
        }
    }
}
