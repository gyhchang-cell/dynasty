package com.dynasty.client;

import com.dynasty.cod3.*;
import com.google.gson.GsonBuilder;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
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

/** Controlled liquid fixtures in a disposable world. Never opens an existing save. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class GhostShipQa {
    private static final Path OUT=Path.of(System.getProperty("dynasty.auroraQa.output"));
    private static final List<String> RESULTS=new ArrayList<>();
    private static final List<Map<String,Object>> VIEWS=new ArrayList<>();
    private static final String[] LABELS={"front","45","right","left","back","near","far","minimal","sail-a","sail-b","day","dry","after-reload","inside-hull","outside-region","bad-waterline","late-observer","underworld-fog","underworld-day","return-overworld"};
    private static final int[] ANGLES={180,135,90,-90,0};
    private static int stage,settle;private static boolean started,hidden,done,configured;
    private static CompletableFuture<Void> prepare,weather,reload,underPrepare;
    private static Cod3VisualPacket original,underOriginal,current;
    private static final long DEADLINE=System.nanoTime()+540_000_000_000L;
    private static boolean under(int v){return v==17||v==18;}
    private static boolean absent(int v){return v==10||v==11||v==13||v==14||v==15||v==18;}
    private static long age(int v){return v==8?350:v==9?420:v==16?950:600;}
    private static long day(int v){return v==10||v==18?6000:18000;}
    private static void require(boolean b,String s){if(!b)throw new AssertionError(s);RESULTS.add("PASS "+s);}
    private static net.minecraft.world.level.chunk.ChunkGenerator terrain(net.minecraft.core.RegistryAccess r){
        var settings=net.minecraft.world.level.levelgen.flat.FlatLevelGeneratorSettings.getDefault(r.lookupOrThrow(Registries.BIOME),r.lookupOrThrow(Registries.STRUCTURE_SET),r.lookupOrThrow(Registries.PLACED_FEATURE));
        settings.getLayersInfo().clear();settings.getLayersInfo().add(new net.minecraft.world.level.levelgen.flat.FlatLayerInfo(111,Blocks.STONE));settings.getLayersInfo().add(new net.minecraft.world.level.levelgen.flat.FlatLayerInfo(16,Blocks.WATER));settings.updateLayers();return new net.minecraft.world.level.levelgen.FlatLevelSource(settings);
    }
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
        if(!Boolean.getBoolean("dynasty.ghostShipQa")||done||e.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            Files.createDirectories(OUT);
            if(!hidden){GLFW.glfwHideWindow(mc.getWindow().getWindow());hidden=true;mc.options.getSoundSourceOptionInstance(net.minecraft.sounds.SoundSource.MASTER).set(0.0);}
            if(System.nanoTime()>DEADLINE)throw new AssertionError("ghost ship QA deadline");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                started=true;mc.options.pauseOnLostFocus=false;mc.options.hideGui=true;mc.options.fov().set(55);mc.options.bobView().set(false);mc.options.renderDistance().set(12);mc.options.cloudStatus().set(CloudStatus.OFF);mc.options.framerateLimit().set(40);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);rules.getRule(GameRules.RULE_WEATHER_CYCLE).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("ghost-ship-qa",new LevelSettings("Disposable ghost ship QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(1518,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions().replaceOverworldGenerator(r,terrain(r)));return;
            }
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
            if(prepare==null){prepare=mc.getSingleplayerServer().submit(()->{
                var l=mc.getSingleplayerServer().overworld();l.setDayTime(18000);l.setRainLevel(1);l.setWeatherParameters(6000,6000,true,false);
                for(int x=-4;x<=4;x++)for(int z=-4;z<=4;z++)l.getChunk(x,z);
                var data=new ScenicEvents();require(data.start(l,3,new Vec3(0,63,0)),"production ship starts only on actual controlled deep water");original=data.packets(l,new Vec3(0,63,0)).get(0);
                require(original.duration()==1200&&original.scale()==1,"native 60-second x1 packet");
                mc.getSingleplayerServer().getPlayerList().getPlayers().get(0).setGameMode(GameType.SPECTATOR);
            });return;}
            if(!prepare.isDone())return;prepare.join();
            if(stage>=LABELS.length*2){
                require(ScenicGhostShipRoute.soundVolume(original,600,0,1)<=.06&&ScenicGhostShipRoute.soundVolume(original,600,41,1)==0,"quiet cue capped and local without playback");
                clear();require(active().isEmpty(),"world and scene cleanup");Files.write(OUT.resolve("PASS.txt"),RESULTS);Files.writeString(OUT.resolve("views.json"),new GsonBuilder().setPrettyPrinting().create().toJson(VIEWS));done=true;mc.stop();return;
            }
            int v=stage/2;
            if(v==17&&underPrepare==null){clear();underPrepare=mc.getSingleplayerServer().submit(()->{
                var key=ResourceKey.create(Registries.DIMENSION,new ResourceLocation("dynasty","underworld"));var l=mc.getSingleplayerServer().getLevel(key);require(l!=null,"actual registered underworld exists");
                l.setDayTime(18000);l.setRainLevel(0);
                // Explicit native fixture, not claimed to be a naturally generated river.
                for(int x=-48;x<=48;x++)for(int z=-48;z<=48;z++)for(int y=197;y<=199;y++)l.setBlock(new BlockPos(x,y,z),Blocks.WATER.defaultBlockState(),2);
                var data=new ScenicEvents();require(data.start(l,3,new Vec3(0,200,0)),"underworld no-rain route uses real liquid, not an invented fog weather flag");underOriginal=data.packets(l,new Vec3(0,200,0)).get(0);
            });return;}
            if(underPrepare!=null&&!underPrepare.isDone())return;if(underPrepare!=null)underPrepare.join();
            if(v==12&&reload==null){clear();reload=mc.reloadResourcePacks();return;}
            if(reload!=null&&!reload.isDone())return;if(reload!=null)reload.join();
            if(!configured){
                clear();configured=true;settle=0;mc.options.particles().set(v==7?ParticleStatus.MINIMAL:ParticleStatus.ALL);
                current=under(v)?underOriginal:original;double angle=Math.toRadians(v<5?ANGLES[v]:135),radius=v==6?142:v==14?280:v==5?22:48;
                Vec3 atShip=ScenicGhostShipRoute.position(current,age(v)+40),target=atShip.add(0,4,0),at=target.add(Math.sin(angle)*radius,1,-Math.cos(angle)*radius);
                if(v==13){at=atShip.add(0,1,0);target=at.add(0,0,16);}
                double horizontal=Math.hypot(target.x-at.x,target.z-at.z);float yaw=(float)Math.toDegrees(Math.atan2(-(target.x-at.x),target.z-at.z)),pitch=(float)-Math.toDegrees(Math.atan2(target.y-at.y,horizontal));
                final Vec3 camera=at;double eye=mc.player.getEyeHeight();
                weather=mc.getSingleplayerServer().submit(()->{
                    var key=ResourceKey.create(Registries.DIMENSION,new ResourceLocation(current.dimension()));var l=mc.getSingleplayerServer().getLevel(key);
                    l.setDayTime(day(v));l.setWeatherParameters(6000,6000,!under(v)&&v!=11,false);l.setRainLevel(!under(v)&&v!=11?1:0);
                    mc.getSingleplayerServer().getPlayerList().getPlayers().get(0).teleportTo(l,camera.x,camera.y-eye,camera.z,yaw,pitch);
                });mc.setCameraEntity(mc.player);
            }
            if(!weather.isDone())return;weather.join();if(!mc.level.dimension().location().toString().equals(current.dimension()))return;
            mc.level.setDayTime(day(v));mc.level.setRainLevel(!under(v)&&v!=11?1:0);mc.level.setThunderLevel(0);
            if(stage%2==1&&settle==0){
                if(v==17||v==19)require(active().isEmpty(),"dimension transition cleared old scene "+LABELS[v]);
                long age=age(v);var p=new Cod3VisualPacket(current.dimension(),current.template(),-1,current.seed(),mc.level.getGameTime()-age,current.duration(),current.scale(),v==15?current.origin().add(0,20,0):current.origin(),current.direction(),current.sequence(),(int)age);
                Cod3VfxRenderer.receive(p);Cod3VfxRenderer.receive(p);require(active().size()==1,"duplicate sync has single ship "+LABELS[v]);
            }
            settle++;
        }catch(Throwable t){fail(t);}
    }
    @SuppressWarnings("unchecked") private static List<Cod3VisualPacket> active()throws Exception{var f=Cod3VfxRenderer.class.getDeclaredField("ACTIVE");f.setAccessible(true);return (List<Cod3VisualPacket>)f.get(null);}
    @SuppressWarnings("unchecked") private static Map<Cod3VisualPacket,ScenicModels.Actor> actors()throws Exception{var f=ScenicModels.class.getDeclaredField("ACTORS");f.setAccessible(true);return (Map<Cod3VisualPacket,ScenicModels.Actor>)f.get(null);}
    private static void clear()throws Exception{active().clear();ScenicModels.clear();ScenicGhostShipSound.clear();}
    private static double expectedSail(double tick){double s=(tick/20)%8;double[] values={-1.4,0,1.4,0,-1.4};int segment=Math.min(3,(int)(s/2));return Math.toRadians(-18+values[segment]+(values[segment+1]-values[segment])*(s-segment*2)/2);}
    @SubscribeEvent public static void capture(TickEvent.RenderTickEvent e){
        if(!Boolean.getBoolean("dynasty.ghostShipQa")||done||e.phase!=TickEvent.Phase.END||settle<60||stage>=LABELS.length*2)return;
        try{
            var mc=Minecraft.getInstance();int v=stage/2;String label=LABELS[v];require(GL11.glGetError()==GL11.GL_NO_ERROR,"GL state "+stage);
            try(var im=Screenshot.takeScreenshot(mc.getMainRenderTarget())){im.writeToFile(OUT.resolve(String.format(Locale.ROOT,"%02d-%s-%s.png",stage,label,stage%2==0?"off":"on")));}
            if(stage%2==1){
                if(v==10||v==11||v==15||v==18)require(actors().isEmpty(),"day/dry/invalid-liquid gate does not create model "+label);
                if(v==14)require(active().isEmpty(),"outside region removes packet");
                if(v==13)require(ScenicGhostShipRoute.alpha(current,age(v),1,1)==0,"inside hull does not cover screen");
                if(!absent(v)){
                    require(actors().size()==1,"production draws exactly one ship "+label);var actor=actors().values().iterator().next();
                    var model=ScenicModels.renderer("ghost_ship",actor.lod).getGeoModel();var bones=model.getAnimationProcessor().getRegisteredBones();require(bones.size()==8,"8 actual GeckoLib bones "+label);
                    var sail=bones.stream().filter(b->b.getName().equals("main_sail")).findFirst().orElseThrow();require(Math.abs(-sail.getRotY()-expectedSail(actor.tick))<.02,"8s exported animation continues at absolute packet age "+label+" age="+actor.tick+" actual="+-sail.getRotY()+" expected="+expectedSail(actor.tick));
                    require(ScenicGhostShipWater.valid(mc.level,current),"loaded route actually liquid "+label);
                    var originPose=new com.mojang.blaze3d.vertex.PoseStack();var renderer=ScenicModels.renderer("ghost_ship",actor.lod);
                    renderer.preRender(originPose,actor,model.getBakedModel(model.getModelResource(actor)),mc.renderBuffers().bufferSource(),null,false,0,15728880,0,1,1,1,1);
                    var transform=originPose.last().pose();require(Math.abs(transform.m30())<1e-6&&Math.abs(transform.m31())<1e-6&&Math.abs(transform.m32())<1e-6,"actual GeckoLib preRender keeps authored zero-waterline without block-center offset "+label);
                    VIEWS.add(Map.of("view",label,"lod",actor.lod,"age",actor.tick,"sailY",-sail.getRotY(),"camera",mc.gameRenderer.getMainCamera().getPosition().toString(),"origin",current.origin().toString(),"fixture",under(v)?"controlled water pool in actual underworld dimension":"controlled flat deep-water world"));
                }
                if(v==12)for(String detail:List.of("","_medium","_far")){var actor=new ScenicModels.Actor("ghost_ship",0);var model=ScenicModels.renderer("ghost_ship",detail).getGeoModel();require(!model.getBakedModel(model.getModelResource(actor)).topLevelBones().isEmpty()&&model.getAnimation(actor,"animation.scenic.idle")!=null,"resource reload real ship "+detail);}
            }
            stage++;configured=false;settle=0;
        }catch(Throwable t){fail(t);}
    }
    private static void fail(Throwable t){done=true;t.printStackTrace();try{Files.writeString(OUT.resolve("FAIL.txt"),t.toString());Files.write(OUT.resolve("partial.txt"),RESULTS);}catch(Exception ignored){}Minecraft.getInstance().stop();}
}
