package com.dynasty.client;

import com.dynasty.cod3.*;
import com.google.gson.GsonBuilder;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;
import org.lwjgl.opengl.GL11;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Disposable, silent, hidden client; real player camera and production GeckoLib draw. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class XuanwuQa {
    private static final Path OUT=Path.of(System.getProperty("dynasty.auroraQa.output"));
    private static final List<String> RESULTS=new ArrayList<>();
    private static final List<Map<String,Object>> VIEWS=new ArrayList<>();
    private static final Vec3 ANCHOR=new Vec3(0,63,0);
    private static final String[] LABELS={"front","45","right","left","back","full-near","far","minimal","paddle-forward","paddle-back","night","rain","after-reload","inside-model","outside-region","dry-land","late-observer","high-anchor","emerging","sinking"};
    private static final int[] ANGLES={180,135,90,-90,0};
    private static int stage,settle;private static boolean started,hidden,done,configured;
    private static CompletableFuture<Void> prepare,weather,reload;
    private static Cod3VisualPacket original,received;
    private static int[] baseline;
    private static final long DEADLINE=System.nanoTime()+540_000_000_000L;
    private static boolean absent(int v){return v==11||v==13||v==14||v==15;}
    private static long age(int v){return v==8?150:v==9?190:v==16?1250:v==18?0:v==19?1720:320;}
    private static long day(int v){return v==10?18000:6000;}
    private static net.minecraft.world.level.chunk.ChunkGenerator terrain(net.minecraft.core.RegistryAccess registry){
        var settings=net.minecraft.world.level.levelgen.flat.FlatLevelGeneratorSettings.getDefault(registry.lookupOrThrow(Registries.BIOME),registry.lookupOrThrow(Registries.STRUCTURE_SET),registry.lookupOrThrow(Registries.PLACED_FEATURE));
        settings.getLayersInfo().clear();settings.getLayersInfo().add(new net.minecraft.world.level.levelgen.flat.FlatLayerInfo(111,net.minecraft.world.level.block.Blocks.STONE));settings.getLayersInfo().add(new net.minecraft.world.level.levelgen.flat.FlatLayerInfo(16,net.minecraft.world.level.block.Blocks.WATER));settings.updateLayers();
        return new net.minecraft.world.level.levelgen.FlatLevelSource(settings);
    }
    private static void require(boolean b,String s){if(!b)throw new AssertionError(s);RESULTS.add("PASS "+s);}
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
        if(!Boolean.getBoolean("dynasty.xuanwuQa")||done||e.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            Files.createDirectories(OUT);
            if(!hidden){GLFW.glfwHideWindow(mc.getWindow().getWindow());hidden=true;mc.options.getSoundSourceOptionInstance(net.minecraft.sounds.SoundSource.MASTER).set(0.0);}
            if(System.nanoTime()>DEADLINE)throw new AssertionError("xuanwu QA deadline");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                started=true;mc.options.pauseOnLostFocus=false;mc.options.hideGui=true;mc.options.fov().set(55);mc.options.bobView().set(false);mc.options.renderDistance().set(12);mc.options.cloudStatus().set(CloudStatus.OFF);mc.options.framerateLimit().set(40);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);rules.getRule(GameRules.RULE_WEATHER_CYCLE).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("xuanwu-qa",new LevelSettings("Disposable xuanwu QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(1518,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions().replaceOverworldGenerator(r,terrain(r)));return;
            }
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
            if(prepare==null){prepare=mc.getSingleplayerServer().submit(()->{
                var l=mc.getSingleplayerServer().overworld();l.setDayTime(1000);var data=new ScenicEvents();
                require(data.start(l,10,ANCHOR),"production ScenicEvents starts xuanwu");original=data.packets(l,ANCHOR).get(0);
                require(original.duration()==1800&&original.scale()==4,"native 90-second x4 packet contract");
                mc.getSingleplayerServer().getPlayerList().getPlayers().get(0).setGameMode(GameType.SPECTATOR);
            });return;}
            if(!prepare.isDone())return;prepare.join();
            if(stage>=LABELS.length*2){
                clear();require(active().isEmpty(),"scene cleanup");Files.write(OUT.resolve("PASS.txt"),RESULTS);Files.writeString(OUT.resolve("views.json"),new GsonBuilder().setPrettyPrinting().create().toJson(VIEWS));done=true;mc.stop();return;
            }
            int v=stage/2;
            if(v==12&&reload==null){clear();reload=mc.reloadResourcePacks();return;}
            if(reload!=null&&!reload.isDone())return;if(reload!=null)reload.join();
            if(!configured){
                clear();configured=true;settle=0;mc.options.particles().set(v==7?ParticleStatus.MINIMAL:ParticleStatus.ALL);
                double angle=Math.toRadians(v<5?ANGLES[v]:135),radius=v==6?140:v==14?280:64;
                // Center on the flight at capture age; camera remains fixed during each off/on pair.
                double travel=0;
                Vec3 target=ANCHOR.add(0,8,travel),at=target.add(Math.sin(angle)*radius,2,-Math.cos(angle)*radius);
                if(v==15){target=target.add(160,0,0);at=at.add(160,0,0);}
                if(v==5)at=ANCHOR.add(26,9,-8);
                if(v==13){at=ANCHOR.add(0,1,travel);target=at.add(0,0,16);}
                double horizontal=Math.hypot(target.x-at.x,target.z-at.z);
                float yaw=(float)Math.toDegrees(Math.atan2(-(target.x-at.x),target.z-at.z));
                float pitch=(float)-Math.toDegrees(Math.atan2(target.y-at.y,horizontal));
                final Vec3 camera=at;double eye=mc.player.getEyeHeight();
                weather=mc.getSingleplayerServer().submit(()->{
                    var l=mc.getSingleplayerServer().overworld();l.setDayTime(day(v));l.setWeatherParameters(6000,6000,v==11,false);
                    l.setBlock(new net.minecraft.core.BlockPos(160,63,0),net.minecraft.world.level.block.Blocks.STONE.defaultBlockState(),3);
                    var player=mc.getSingleplayerServer().getPlayerList().getPlayers().get(0);player.teleportTo(l,camera.x,camera.y-eye,camera.z,yaw,pitch);
                });mc.setCameraEntity(mc.player);
            }
            if(!weather.isDone())return;weather.join();mc.level.setDayTime(day(v));mc.level.setRainLevel(v==11?1:0);mc.level.setThunderLevel(0);
            if(stage%2==1&&settle==0){
                long age=age(v);var p=new Cod3VisualPacket(original.dimension(),original.template(),-1,original.seed(),mc.level.getGameTime()-age,original.duration(),original.scale(),v==15?ANCHOR.add(160,0,0):v==17?ANCHOR.add(0,80,0):original.origin(),original.direction(),original.sequence(),(int)age);
                received=p;Cod3VfxRenderer.receive(p);Cod3VfxRenderer.receive(p);require(active().size()==1,"duplicate sync single xuanwu "+LABELS[v]);
            }
            settle++;
        }catch(Throwable t){fail(t);}
    }
    @SuppressWarnings("unchecked") private static List<Cod3VisualPacket> active()throws Exception{var f=Cod3VfxRenderer.class.getDeclaredField("ACTIVE");f.setAccessible(true);return (List<Cod3VisualPacket>)f.get(null);}
    @SuppressWarnings("unchecked") private static ScenicModels.Actor drawnActor()throws Exception{var f=ScenicModels.class.getDeclaredField("ACTORS");f.setAccessible(true);return ((Map<Cod3VisualPacket,ScenicModels.Actor>)f.get(null)).values().iterator().next();}
    private static double expectedWing(double tick)throws Exception{
        try(var input=Minecraft.getInstance().getResourceManager().open(new net.minecraft.resources.ResourceLocation("dynasty","animations/scenic/mountain_xuanwu.animation.json"));var reader=new java.io.InputStreamReader(input)){
            var animation=com.google.gson.JsonParser.parseReader(reader).getAsJsonObject().getAsJsonObject("animations").getAsJsonObject("animation.scenic.idle");
            double phase=(tick/20)%animation.get("animation_length").getAsDouble();
            var track=animation.getAsJsonObject("bones").getAsJsonObject("fore_left").getAsJsonObject("rotation");
            var times=track.keySet().stream().sorted(Comparator.comparingDouble(Double::parseDouble)).toList();
            for(int i=1;i<times.size();i++){double a=Double.parseDouble(times.get(i-1)),b=Double.parseDouble(times.get(i));
                if(phase<=b){double start=track.getAsJsonArray(times.get(i-1)).get(1).getAsDouble(),end=track.getAsJsonArray(times.get(i)).get(1).getAsDouble();return Math.toRadians(start+(end-start)*(phase-a)/(b-a));}}
            throw new AssertionError("unbounded animation phase");
        }
    }
    private static void clear()throws Exception{active().clear();ScenicModels.clear();}
    @SubscribeEvent public static void capture(TickEvent.RenderTickEvent e){
        if(!Boolean.getBoolean("dynasty.xuanwuQa")||done||e.phase!=TickEvent.Phase.END||settle<60||stage>=LABELS.length*2)return;
        try{
            var mc=Minecraft.getInstance();int v=stage/2;String label=LABELS[v];require(GL11.glGetError()==GL11.GL_NO_ERROR,"GL state "+stage);
            try(var im=Screenshot.takeScreenshot(mc.getMainRenderTarget())){
                im.writeToFile(OUT.resolve(String.format(Locale.ROOT,"%02d-%s-%s.png",stage,label,stage%2==0?"off":"on")));
                int[] pixels=new int[im.getWidth()*im.getHeight()];int rigPixels=0;
                for(int y=0;y<im.getHeight();y++)for(int x=0;x<im.getWidth();x++){
                    int i=y*im.getWidth()+x,b=im.getPixelRGBA(x,y);pixels[i]=b;
                    if(stage%2==1){int a=baseline[i],r=b&255,g=b>>8&255,blue=b>>16&255;
                        int delta=Math.abs(r-(a&255))+Math.abs(g-(a>>8&255))+Math.abs(blue-(a>>16&255));
                        if(delta>45&&g>blue-6&&r>blue-12)rigPixels++;
                    }
                }
                if(stage%2==0)baseline=pixels;
                else{
                    var surface=ScenicXuanwuWater.surface(mc.level,received);
                    require(v==14||(v==11||v==15?surface==null:surface!=null&&surface.y==63),"actual loaded waterline / weather / land gate "+label+" = "+surface);
                    require(absent(v)?rigPixels<50:rigPixels>150,(absent(v)?"absent":"visible")+" xuanwu pixels "+label+" = "+rigPixels);
                    String lod=ScenicModels.lod((v==17?ANCHOR.add(0,80,0):ANCHOR).distanceTo(mc.gameRenderer.getMainCamera().getPosition()),v==7);
                    if(!absent(v)){
                        var model=ScenicModels.renderer("mountain_xuanwu",lod).getGeoModel();var bones=model.getAnimationProcessor().getRegisteredBones();
                        require(bones.size()==15,"15 real GeckoLib bones "+label);
                        double motion=bones.stream().mapToDouble(b->Math.abs(b.getRotX())+Math.abs(b.getRotY())+Math.abs(b.getRotZ())).sum();require(motion>.01,"real animated joints "+label);
                        var wing=bones.stream().filter(b->b.getName().equals("fore_left")).findFirst().orElseThrow();
                        var actor=drawnActor();require(Math.abs(-wing.getRotY()-expectedWing(actor.tick))<.06,"exported keyframe matches packet clock beyond first loop "+label+" age="+actor.tick+" wing="+-wing.getRotY());
                        VIEWS.add(Map.of("view",label,"lod",lod,"rigPixels",rigPixels,"paddleY",-wing.getRotY(),"age",actor.tick,"boneMotion",motion,"actualCamera",mc.gameRenderer.getMainCamera().getPosition().toString()));
                    }
                    if(v==12)for(String detail:List.of("","_medium","_far")){
                        var actor=new ScenicModels.Actor("mountain_xuanwu",0);var model=ScenicModels.renderer("mountain_xuanwu",detail).getGeoModel();
                        require(!model.getBakedModel(model.getModelResource(actor)).topLevelBones().isEmpty()&&model.getAnimation(actor,"animation.scenic.idle")!=null,"reload real model + animation "+detail);
                    }
                }
            }
            stage++;configured=false;settle=0;
        }catch(Throwable t){fail(t);}
    }
    private static void fail(Throwable t){done=true;t.printStackTrace();try{Files.writeString(OUT.resolve("FAIL.txt"),t.toString());Files.write(OUT.resolve("partial.txt"),RESULTS);}catch(Exception ignored){}Minecraft.getInstance().stop();}
}
