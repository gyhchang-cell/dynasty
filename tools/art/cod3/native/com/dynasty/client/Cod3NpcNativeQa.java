package com.dynasty.client;

import com.dynasty.cod3.*;
import com.google.gson.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Disposable art fixtures. Reflection forces poses only in this opt-in test;
 * production entity logic is neither modified nor included in this source set. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class Cod3NpcNativeQa {
    private static final String ROLE=System.getProperty("dynasty.cod3ClientQa.role","");
    private static final boolean HOST=ROLE.equals("host");
    private static final Path ROOT=Path.of(System.getProperty("dynasty.cod3ClientQa.output","build/cod3-client/unset/results"));
    private static final Path OUT=ROOT.resolve(ROLE),COORD=ROOT.resolve("coord");
    private static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
    private record Spec(String role,String state,int angle){}
    private record Stage(int index,String phase,int entity,String uuid,long start){}
    private static final List<Spec> SPECS=new ArrayList<>();
    static{
        for(String role:List.of("baibao_jin","hei_po","mo_jizi","lao_chen","han_chong","qingxuanzi","a_ji","cao_chengfu","hong_ling","chu_nongyu","xiaoyuanzi","sai_banxian","ba_tu","yan_chifeng","huang_laohan")){
            String selected=System.getProperty("dynasty.cod3NpcQa.roles","");
            if(!selected.isBlank()&&!List.of(selected.split(",")).contains(role))continue;
            String clip=System.getProperty("dynasty.cod3NpcQa.state","");
            if(clip.isBlank()||clip.equals("idle"))for(int angle:new int[]{0,45,90,180})SPECS.add(new Spec(role,"idle",angle));
            for(String state:List.of("walk","turn","talk","work","react","rain","night","danger","player_near","player_holds_special"))if(clip.isBlank()||clip.equals(state))SPECS.add(new Spec(role,state,0));
        }
    }
    private static final List<Map<String,Object>> EVIDENCE=new ArrayList<>();
    private static final long DEADLINE=System.nanoTime()+1_200_000_000_000L;
    private static boolean started,done,listener,ready,captured;
    private static int index=-1,observed=-1,settled,shot;
    private static Stage local;
    private static CompletableFuture<Stage> pending;
    private static CompletableFuture<Void> setup,reload;
    private static DynastyNpcEntity fixture;
    private static ArmorStand camera;
    private static EntityDataAccessor<Integer> stateKey;
    private static List<Double> previousPose;
    private static long nextDiagnostic;
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(ROLE.isBlank()||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            if(System.nanoTime()>nextDiagnostic){nextDiagnostic=System.nanoTime()+5_000_000_000L;Files.createDirectories(OUT);Files.writeString(OUT.resolve("state.txt"),"screen="+mc.screen+" level="+(mc.level!=null)+" stage="+index+" observed="+observed);}
            if(System.nanoTime()>DEADLINE)throw new AssertionError("NPC art QA timeout");
            if(started&&!HOST&&mc.screen instanceof DisconnectedScreen)throw new AssertionError("Peer disconnected");
            if(Files.exists(ROOT.resolve(HOST?"peer/FAIL.txt":"host/FAIL.txt")))throw new AssertionError("Other client failed");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                if(!mc.gameDirectory.getCanonicalPath().contains("/build/cod3-client/"))throw new AssertionError("Refusing non-test world");
                Files.createDirectories(OUT);Files.createDirectories(COORD);
                mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(3);mc.options.fov().set(45);mc.options.framerateLimit().set(40);mc.options.hideGui=true;
                if(!HOST&&!Files.exists(COORD.resolve("listening.txt")))return;
                started=true;
                if(!HOST){String address="127.0.0.1:25593";ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString(address),new ServerData("Disposable NPC art QA",address,false),false);}
                else{
                    var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                    mc.createWorldOpenFlows().createFreshLevel("cod3-npc-art",new LevelSettings("Disposable NPC art QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(310,false,false),registry->registry.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());
                }return;
            }
            if(mc.level==null||mc.player==null)return;
            if(mc.screen!=null)mc.setScreen(null);
            if(HOST&&setup==null){var server=mc.getSingleplayerServer();setup=server.submit(()->{
                var world=server.overworld();world.setDayTime(6000);
                for(int x=-12;x<=12;x++)for(int z=-12;z<=12;z++)world.setBlockAndUpdate(new BlockPos(x,-61,z),Blocks.STONE.defaultBlockState());
                // One-block marks give real scale references in the screenshots.
                world.setBlockAndUpdate(new BlockPos(-2,-60,-2),Blocks.WHITE_WOOL.defaultBlockState());
                world.setBlockAndUpdate(new BlockPos(-2,-59,-2),Blocks.GRAY_WOOL.defaultBlockState());
                server.setUsesAuthentication(false);try{server.getConnection().startTcpServerListener(java.net.InetAddress.getByName("127.0.0.1"),25593);}catch(Exception e){throw new RuntimeException(e);}
            });return;}
            if(HOST){
                if(!setup.isDone())return;setup.join();if(!listener){Files.writeString(COORD.resolve("listening.txt"),"art");listener=true;}
                if(index==SPECS.size()-1&&Files.exists(COORD.resolve("complete.txt"))&&Files.exists(ROOT.resolve("peer/PASS.txt"))){finish(mc,null);return;}
                var server=mc.getSingleplayerServer();if(server.getPlayerList().getPlayerCount()<2)return;
                if(pending!=null){if(!pending.isDone())return;local=pending.join();pending=null;publish(local);}
                if(index<0){index=0;pending=server.submit(()->prepare(server,index));return;}
                if(local.phase.equals("READY")&&both("ready",index)){pending=server.submit(()->new Stage(index,"ACTIVE",fixture.getId(),fixture.getUUID().toString(),server.overworld().getGameTime()));return;}
                if(both("captured",index)){
                    if(index==SPECS.size()-1){Files.writeString(COORD.resolve("complete.txt"),"art");if(Files.exists(ROOT.resolve("peer/PASS.txt")))finish(mc,null);}
                    else{index++;pending=server.submit(()->prepare(server,index));}return;
                }
            }else if(Files.exists(COORD.resolve("complete.txt"))){finish(mc,null);return;}
            if(!Files.exists(COORD.resolve("stage.json")))return;
            var stage=JSON.fromJson(Files.readString(COORD.resolve("stage.json")),Stage.class);var spec=SPECS.get(stage.index);
            if(stage.index!=observed){observed=stage.index;settled=0;shot=0;ready=false;captured=false;camera=null;previousPose=null;reload=null;}
            local=stage;
            var entity=mc.level.getEntity(stage.entity);
            if(!(entity instanceof DynastyNpcEntity npc)||!npc.getUUID().toString().equals(stage.uuid)||!npc.role.equals(spec.role)||!npc.state().name().equalsIgnoreCase(spec.state))return;
            if(mc.getEntityRenderDispatcher().getRenderer(npc) instanceof Cod3NpcRenderer renderer){
                for(var b:renderer.getGeoModel().getAnimationProcessor().getRegisteredBones())
                    ((software.bernie.geckolib.cache.object.GeoBone)b).setTrackingMatrices(true);
            }
            if(camera==null){
                double radians=Math.toRadians(spec.angle);
                camera=new ArmorStand(mc.level,4*Math.sin(radians),-60.4,4*Math.cos(radians));camera.setNoGravity(true);
                camera.setYRot(180-spec.angle);camera.setYHeadRot(180-spec.angle);camera.yHeadRotO=180-spec.angle;camera.setXRot(5);camera.setOldPosAndRot();
                mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(camera);
            }
            if(++settled>=20&&!ready){
                // Reload actual assets once after all roles have been exercised.
                if(observed==SPECS.size()-1){if(reload==null){reload=mc.reloadResourcePacks();return;}if(!reload.isDone())return;reload.join();}
                ready=true;Files.writeString(COORD.resolve("ready-"+observed+"-"+ROLE+".txt"),stage.uuid);
            }
        }catch(Throwable error){finish(mc,error);}
    }
    private static Stage prepare(MinecraftServer server,int stage){
        var world=server.overworld();if(fixture!=null)fixture.discard();var spec=SPECS.get(stage);
        fixture=NpcContent.NPCS.get(spec.role).get().create(world);fixture.moveTo(0,-60,0,0,0);fixture.yBodyRot=0;fixture.yBodyRotO=0;fixture.setYHeadRot(0);fixture.yHeadRotO=0;
        fixture.setNoAi(true);fixture.setNoGravity(true);fixture.setInvulnerable(true);world.addFreshEntity(fixture);
        for(var player:server.getPlayerList().getPlayers()){player.setGameMode(GameType.CREATIVE);player.teleportTo(world,-8,-60,8,180,0);}
        forceState(spec.state);
        return new Stage(stage,"READY",fixture.getId(),fixture.getUUID().toString(),world.getGameTime());
    }
    @SuppressWarnings("unchecked") private static void forceState(String state){
        try{if(stateKey==null){var field=DynastyNpcEntity.class.getDeclaredField("STATE");field.setAccessible(true);stateKey=(EntityDataAccessor<Integer>)field.get(null);}
            fixture.getEntityData().set(stateKey,DynastyNpcEntity.State.valueOf(state.toUpperCase(Locale.ROOT)).ordinal());
        }catch(Exception e){throw new RuntimeException(e);}
    }
    @SubscribeEvent public static void serverTick(TickEvent.ServerTickEvent event){
        if(HOST&&!done&&event.phase==TickEvent.Phase.END&&fixture!=null&&index>=0)forceState(SPECS.get(index).state);
    }
    private static void publish(Stage stage)throws Exception{var tmp=COORD.resolve("next.json");Files.writeString(tmp,JSON.toJson(stage));Files.move(tmp,COORD.resolve("stage.json"),StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);}
    private static boolean both(String label,int stage){return Files.exists(COORD.resolve(label+"-"+stage+"-host.txt"))&&Files.exists(COORD.resolve(label+"-"+stage+"-peer.txt"));}
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event){
        if(ROLE.isBlank()||done||event.phase!=TickEvent.Phase.END||captured||!ready||local==null||!local.phase.equals("ACTIVE"))return;
        var mc=Minecraft.getInstance();if(mc.level==null||mc.getOverlay()!=null)return;
        try{
            var spec=SPECS.get(observed);long age=mc.level.getGameTime()-local.start;
            if(age<(shot==0?4:18))return;
            var npc=(DynastyNpcEntity)mc.level.getEntity(local.entity);if(npc==null)throw new AssertionError("Missing NPC");
            if(!(mc.getEntityRenderDispatcher().getRenderer(npc) instanceof Cod3NpcRenderer renderer))throw new AssertionError("Wrong renderer");
            var model=renderer.getGeoModel();
            if(model.getAnimation(npc,"animation.npc."+spec.state)==null)throw new AssertionError("Missing actual animation");
            var controller=npc.getAnimatableInstanceCache().<DynastyNpcEntity>getManagerForId(npc.getId()).getAnimationControllers().get("npc");
            if(controller==null||controller.getCurrentAnimation()==null||!controller.getCurrentAnimation().animation().name().equals("animation.npc."+spec.state))throw new AssertionError("Animation not playing: "+spec);
            List<Double> pose=new ArrayList<>();
            for(String bone:List.of("chest","head","left_upper_arm","right_upper_arm","left_forearm","right_forearm","left_wrist","right_wrist","left_thigh","right_thigh")){
                var b=model.getBone(bone).orElseThrow();pose.add((double)b.getRotX());pose.add((double)b.getRotY());pose.add((double)b.getRotZ());
            }
            String file=String.format(Locale.ROOT,"%03d-%s-%s-%d-%d.png",observed,spec.role,spec.state,spec.angle,shot);
            try(var image=net.minecraft.client.Screenshot.takeScreenshot(mc.getMainRenderTarget())){image.writeToFile(OUT.resolve(file));}
            Map<String,Object> row=new LinkedHashMap<>();row.put("stage",observed);row.put("spec",spec);row.put("uuid",local.uuid);row.put("age",age);row.put("pose",pose);row.put("screenshot",file);row.put("height",npc.getBbHeight());row.put("renderer",renderer.getClass().getName());row.put("animation",controller.getCurrentAnimation().animation().name());row.put("resourceReload",observed==SPECS.size()-1);
            Map<String,Double> grips=new LinkedHashMap<>();
            for(var core:model.getAnimationProcessor().getRegisteredBones()){
                var b=(software.bernie.geckolib.cache.object.GeoBone)core;var parent=b.getParent();
                if(parent!=null&&(parent.getName().equals("left_hand")||parent.getName().equals("right_hand"))){
                    double gap=b.getWorldPosition().distance(parent.getWorldPosition());
                    if(!Double.isFinite(gap)||gap>.2)throw new AssertionError("Hand mount detached: "+spec+" "+b.getName()+" "+gap);
                    grips.put(b.getName(),gap);
                }
            }
            row.put("gripDistancesMetres",grips);
            if(previousPose!=null)row.put("poseDelta",java.util.stream.IntStream.range(0,pose.size()).mapToDouble(i->Math.abs(pose.get(i)-previousPose.get(i))).sum());
            EVIDENCE.add(row);previousPose=pose;shot++;
            int shots=Set.of("idle","walk","work").contains(spec.state)?2:1;
            if(shot>=shots){captured=true;Files.writeString(COORD.resolve("captured-"+observed+"-"+ROLE+".txt"),file);}
        }catch(Throwable error){finish(mc,error);}
    }
    private static void finish(Minecraft mc,Throwable failure){
        if(done)return;done=true;
        try{Files.createDirectories(OUT);Files.writeString(OUT.resolve("evidence.json"),JSON.toJson(EVIDENCE));
            if(failure==null)Files.writeString(OUT.resolve("PASS.txt"),"PASS "+ROLE+": "+SPECS.size()+" in-world stages / "+EVIDENCE.size()+" screenshots; "+SPECS.stream().map(Spec::role).distinct().count()+" NPCs, tested state bindings, resource reload.");
            else{Files.writeString(OUT.resolve("FAIL.txt"),failure.toString());failure.printStackTrace();}
        }catch(Exception e){e.printStackTrace();}
        mc.stop();
    }
}
