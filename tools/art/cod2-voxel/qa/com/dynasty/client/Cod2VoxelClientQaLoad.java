package com.dynasty.client;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.mojang.blaze3d.platform.NativeImage;
import net.minecraft.client.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.event.GeoRenderEvent;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Actual drawing cost only: disposable world, NoAI, bounded QA-driven velocity. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class Cod2VoxelClientQaLoad {
    private static final boolean ENABLED=Boolean.getBoolean("dynasty.cod2VoxelQa")&&"art-load".equals(System.getProperty("dynasty.cod2VoxelQa.batch"));
    private static final Path OUT=Path.of(System.getProperty("dynasty.cod2VoxelQa.output","build/cod2-art-load"));
    private static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
    private static final String[] IDS={"zuwu_daoshou","juma_changqiangbing","liannu_zhenzu","ludun_jiashi","tiesuo_chihou","zhenwang_zhangqiguan","kuijun_sishi","pijia_panjiang_huwei","shibian_lishi","fufa_jijiu","xianzhen_duantoujiang","qianji_bailian_yanshi","jubi_shigandang","juli_bixi_kuilei","tongbi_feitian_yecha","bazu_digongzhu","baimu_mowu","mingsha_shixie"};
    private static final long DEADLINE=System.nanoTime()+600_000_000_000L;
    private record Snapshot(int phase,long born,Map<UUID,String> ids){}
    private record Frame(double milliseconds,int actualRendered,int actualWalkClips){}
    private static final List<Object> REPORT=new ArrayList<>();
    private static final List<Mob> SERVER_MOBS=new ArrayList<>();
    private static final List<Double> SERVER_TIMES=new ArrayList<>();
    private static final Map<UUID,Double> ACTUAL_DRIVEN_DISTANCE=new HashMap<>();
    private static final Set<UUID> DRAWN=new HashSet<>(),WALK=new HashSet<>(),CHECKED=new HashSet<>();
    private static final Map<UUID,Integer> WALK_OBSERVATIONS=new HashMap<>();
    private static final List<Frame> FRAMES=new ArrayList<>();
    private static boolean started,done,finishing;
    private static int stage=-1;
    private static volatile boolean moving;
    private static volatile long serverBorn;
    private static long serverNano,previousNano;
    private static Snapshot current;
    private static CompletableFuture<Void> setup,reload;
    private static CompletableFuture<Snapshot> pending;
    private static CompletableFuture<Map<String,Object>> result;
    private static ArmorStand camera;

    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(!ENABLED||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Art load deadline");
            if(!started){
                if(!(mc.screen instanceof net.minecraft.client.gui.screens.TitleScreen))return;
                Files.createDirectories(OUT);started=true;mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(4);mc.options.fov().set(65);mc.options.hideGui=true;
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("cod2-art-load-qa",new LevelSettings("Disposable art load",GameType.CREATIVE,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(77,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
            var server=mc.getSingleplayerServer();if(server==null)return;
            if(setup==null){setup=server.submit(()->{
                var world=server.overworld();world.setDayTime(6000);
                for(int x=-35;x<=35;x++)for(int z=-35;z<=35;z++)world.setBlockAndUpdate(new BlockPos(x,-61,z),Blocks.SMOOTH_STONE.defaultBlockState());
                server.getPlayerList().getPlayers().forEach(p->p.teleportTo(world,28,-60,28,0,0));
            });return;}
            if(!setup.isDone())return;setup.join();
            if(finishing){
                if(!result.isDone())return;var row=result.join();row.put("frames",new ArrayList<>(FRAMES));row.put("walkPostRenderObservations",new HashMap<>(WALK_OBSERVATIONS));REPORT.add(row);Files.writeString(OUT.resolve("samples.json"),JSON.toJson(REPORT)+"\n");finishing=false;current=null;
                if(stage==3){finish(mc,null);return;}
                stage++;if(stage==3){reload=mc.reloadResourcePacks();return;}
                int next=stage;pending=server.submit(()->prepare(server,next));return;
            }
            if(stage<0){stage=0;pending=server.submit(()->prepare(server,0));return;}
            if(stage==3&&reload!=null){if(!reload.isDone())return;reload.join();REPORT.add(Map.of("reload","actual Minecraft resource reload"));reload=null;pending=server.submit(()->prepare(server,3));return;}
            if(current==null){if(!pending.isDone())return;current=pending.join();FRAMES.clear();WALK_OBSERVATIONS.clear();CHECKED.clear();previousNano=0;}
            if(camera==null){camera=new ArmorStand(mc.level,0,0,0);camera.setNoGravity(true);camera.setYRot(180);camera.setXRot(3);camera.setYHeadRot(180);mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(camera);}
            camera.setPos(0,-57.2-camera.getEyeHeight(),24);camera.setOldPosAndRot();
        }catch(Throwable e){finish(mc,e);}
    }
    private static Snapshot prepare(MinecraftServer server,int phase){
        for(var mob:SERVER_MOBS)mob.discard();SERVER_MOBS.clear();SERVER_TIMES.clear();ACTUAL_DRIVEN_DISTANCE.clear();moving=phase==2;
        var world=server.overworld();serverBorn=world.getGameTime();var names=new LinkedHashMap<UUID,String>();
        if(phase>0)for(int i=0;i<IDS.length;i++){
            var type=ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("dynasty",IDS[i]));
            if(type==null||!(type.create(world) instanceof Mob mob)||!(mob instanceof GeoEntity))throw new AssertionError("Actual registered Geo mob absent "+IDS[i]);
            mob.moveTo((i%6-2.5)*5.5,-60,-(i/6)*5.0,0,0);mob.setNoAi(true);mob.setNoGravity(true);mob.setPersistenceRequired();mob.setDeltaMovement(0,0,0);world.addFreshEntity(mob);SERVER_MOBS.add(mob);names.put(mob.getUUID(),IDS[i]);
        }
        return new Snapshot(phase,serverBorn,Map.copyOf(names));
    }
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void server(TickEvent.ServerTickEvent event){
        if(!ENABLED||done)return;
        if(event.phase==TickEvent.Phase.START){serverNano=System.nanoTime();return;}
        var mc=Minecraft.getInstance();var server=mc.getSingleplayerServer();if(server==null)return;
        long age=server.overworld().getGameTime()-serverBorn;
        if(moving)for(var mob:SERVER_MOBS){
            double z=(age/80%2==0?.06:-.06);var before=mob.position();var velocity=new net.minecraft.world.phys.Vec3(0,0,z);
            mob.setDeltaMovement(velocity);mob.move(MoverType.SELF,velocity);mob.hasImpulse=true;mob.hurtMarked=true;
            ACTUAL_DRIVEN_DISTANCE.merge(mob.getUUID(),mob.position().distanceTo(before),Double::sum);
        }
        if(age>=80&&age<=380&&serverNano>0)SERVER_TIMES.add((System.nanoTime()-serverNano)/1_000_000.0);
    }
    @SuppressWarnings({"rawtypes","unchecked"})
    @SubscribeEvent public static void actualDraw(GeoRenderEvent.Entity.Post event){
        if(!ENABLED||done||finishing||current==null)return;var entity=event.getEntity();if(!current.ids.containsKey(entity.getUUID()))return;
        try{
            DRAWN.add(entity.getUUID());var animatable=(GeoEntity)entity;var controller=animatable.getAnimatableInstanceCache().getManagerForId(entity.getId()).getAnimationControllers().get("body");
            if(controller.getCurrentAnimation()!=null&&controller.getCurrentAnimation().animation().name().endsWith(".walk")){WALK.add(entity.getUUID());WALK_OBSERVATIONS.merge(entity.getUUID(),1,Integer::sum);}
            if(CHECKED.add(entity.getUUID())){
                GeoEntityRenderer renderer=event.getRenderer();var model=renderer.getGeoModel();if(model.getBone("root").isEmpty())throw new AssertionError("Actual group root not baked");
                try(var stream=Minecraft.getInstance().getResourceManager().open(model.getTextureResource(animatable));var image=NativeImage.read(stream)){if(image.getWidth()!=16||image.getHeight()!=16)throw new AssertionError("Group uses legacy non-16px atlas");}
            }
        }catch(Throwable e){finish(Minecraft.getInstance(),e);}
    }
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void render(TickEvent.RenderTickEvent event){
        if(!ENABLED||done)return;
        if(event.phase==TickEvent.Phase.START){DRAWN.clear();WALK.clear();return;}
        if(finishing||current==null)return;var mc=Minecraft.getInstance();if(mc.level==null||mc.getOverlay()!=null)return;
        try{
            long age=mc.level.getGameTime()-current.born,now=System.nanoTime();if(age<80){previousNano=0;return;}
            int expected=current.phase==0?0:18;if(DRAWN.size()!=expected){
                var missing=current.ids.entrySet().stream().filter(e->!DRAWN.contains(e.getKey())).toList();
                Files.writeString(OUT.resolve("missing-render.json"),JSON.toJson(Map.of("missing",missing,"serverMobs",SERVER_MOBS.stream().map(m->Map.of("uuid",m.getUUID().toString(),"id",ForgeRegistries.ENTITY_TYPES.getKey(m.getType()).toString(),"position",m.position().toString(),"removed",m.isRemoved(),"alive",m.isAlive())).toList()))+"\n");
                throw new AssertionError("Actual submitted group render count "+DRAWN.size()+" expected "+expected+" missing "+missing);
            }
            if(previousNano>0)FRAMES.add(new Frame((now-previousNano)/1_000_000.0,DRAWN.size(),WALK.size()));previousNano=now;
            if(age<380)return;if(FRAMES.size()<300)throw new AssertionError("Too few actual rendered frames");
            if(current.phase==2&&WALK_OBSERVATIONS.size()!=18)throw new AssertionError("Every actual moving model must render its walk clip");
            try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){image.writeToFile(OUT.resolve(String.format("%02d-mixed18-%s.png",stage,stage==0?"empty":stage==1?"idle":stage==2?"qa-driven-walk":"after-reload")));}
            int phase=current.phase;result=mc.getSingleplayerServer().submit(()->{
                var row=new LinkedHashMap<String,Object>();row.put("phase",phase);row.put("scope","Actual geometry drawing; NoAI and QA-driven bounded velocity, not natural AI/combat/TPS acceptance");row.put("actualRegisteredIds",current.ids);row.put("serverTickMilliseconds",new ArrayList<>(SERVER_TIMES));
                if(phase==2&&(ACTUAL_DRIVEN_DISTANCE.size()!=18||ACTUAL_DRIVEN_DISTANCE.values().stream().anyMatch(v->v<1)))throw new AssertionError("Every fixture must actually move through the original collision engine");
                row.put("actualDrivenDistance",new HashMap<>(ACTUAL_DRIVEN_DISTANCE));row.put("actualServerPositions",SERVER_MOBS.stream().map(m->Map.of("uuid",m.getUUID().toString(),"position",m.position().toString(),"alive",m.isAlive())).toList());row.put("clientAge",age);row.put("fpsAtCapture",mc.getFps());return row;
            });finishing=true;
        }catch(Throwable e){finish(mc,e);}
    }
    private static void finish(Minecraft mc,Throwable error){
        if(done)return;done=true;
        try{Files.writeString(OUT.resolve(error==null?"PASS.txt":"FAIL.txt"),error==null?"PASS actual empty/18 idle/18 QA-driven walk/actual reload native drawing observation; every measured loaded frame submitted 18 unique Geo mob renders using 16px textures. NoAI geometry cost only; no natural AI/combat/full TPS claim.\n":"FAIL: "+error+"\n");if(error!=null)try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){image.writeToFile(OUT.resolve("FAILED.png"));}}catch(Exception ignored){}
        mc.stop();
    }
}
