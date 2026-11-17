package com.dynasty.client;
import com.dynasty.cod3.*;
import com.google.gson.GsonBuilder;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.*;
import net.minecraft.world.level.biome.Biomes;
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
/** Silent disposable canyon. No statue entity or structure placement. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class StoneGodQa {
 private static final Path OUT=Path.of(System.getProperty("dynasty.auroraQa.output"));
 private static final List<String> RESULTS=new ArrayList<>();private static final List<Map<String,Object>> VIEWS=new ArrayList<>();
 private static final String[] LABELS={"front","45","right","left","back","near","far","minimal","day","rain","after-dawn","after-reload","inside","outside-region","late-observer","bad-ground","expired","axe-charge","axe-return","normal-eye-height","medium"};
 private static int stage,settle;private static boolean started,hidden,done,configured;private static CompletableFuture<Void> prepare,weather,reload;private static Cod3VisualPacket original,current;private static final long DEADLINE=System.nanoTime()+540_000_000_000L;
 private static boolean absent(int v){return v>=8&&v<=10||v==12||v==13||v==15||v==16;}
 private static long age(int v){return v==14?950:v==16?1200:v==17?10:v==18?35:600;}
 private static long day(int v){return v==8?6000:v==10?2400:900;}
 private static void require(boolean b,String s){if(!b)throw new AssertionError(s);RESULTS.add("PASS "+s);}
 private static net.minecraft.world.level.chunk.ChunkGenerator terrain(net.minecraft.core.RegistryAccess r){
  var settings=net.minecraft.world.level.levelgen.flat.FlatLevelGeneratorSettings.getDefault(r.lookupOrThrow(Registries.BIOME),r.lookupOrThrow(Registries.STRUCTURE_SET),r.lookupOrThrow(Registries.PLACED_FEATURE));settings.getLayersInfo().clear();settings.getLayersInfo().add(new net.minecraft.world.level.levelgen.flat.FlatLayerInfo(127,Blocks.STONE));settings.updateLayers();
  return new net.minecraft.world.level.levelgen.FlatLevelSource(settings);
 }
 @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
  if(!Boolean.getBoolean("dynasty.stoneGodQa")||done||e.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();
  try{
   Files.createDirectories(OUT);if(!hidden){GLFW.glfwHideWindow(mc.getWindow().getWindow());hidden=true;mc.options.getSoundSourceOptionInstance(net.minecraft.sounds.SoundSource.MASTER).set(0.0);}
   if(System.nanoTime()>DEADLINE)throw new AssertionError("stone god QA deadline");if(mc.getOverlay()!=null)return;if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
   if(!started&&mc.screen instanceof TitleScreen){started=true;mc.options.pauseOnLostFocus=false;mc.options.hideGui=true;mc.options.fov().set(55);mc.options.bobView().set(false);mc.options.renderDistance().set(12);mc.options.cloudStatus().set(CloudStatus.OFF);mc.options.framerateLimit().set(40);var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);rules.getRule(GameRules.RULE_WEATHER_CYCLE).set(false,null);
    mc.createWorldOpenFlows().createFreshLevel("stone-god-qa",new LevelSettings("Disposable stone god QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(1518,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions().replaceOverworldGenerator(r,terrain(r)));return;}
   if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
   if(prepare==null){prepare=mc.getSingleplayerServer().submit(()->{var l=mc.getSingleplayerServer().overworld();l.setDayTime(900);l.setRainLevel(0);l.setWeatherParameters(6000,6000,false,false);for(int x=-4;x<=4;x++)for(int z=-4;z<=4;z++)l.getChunk(x,z);for(int side:new int[]{-1,1})for(int x=34;x<=38;x++)for(int z=-12;z<=44;z++)for(int y=63;y<71;y++)l.setBlock(new BlockPos(x*side,y,z),Blocks.STONE.defaultBlockState(),2);var data=new ScenicEvents();require(data.start(l,6,new Vec3(0,63,0)),"production statue starts on actual supported canyon");original=data.packets(l,new Vec3(0,63,0)).get(0);require(original.scale()==1&&original.duration()==1200&&original.entityId()==-1,"native nonphysical x1 60-second packet");require(l.getBlockState(BlockPos.containing(original.origin()).above(5)).isAir(),"server contains no physical statue");mc.getSingleplayerServer().getPlayerList().getPlayers().get(0).setGameMode(GameType.SPECTATOR);});return;}
   if(!prepare.isDone())return;prepare.join();
   if(stage>=LABELS.length*2){clear();require(active().isEmpty(),"scene cleanup");require(ScenicStoneGodSite.soundVolume(600,1200,0,1)<=.08&&ScenicStoneGodSite.soundVolume(600,1200,97,1)==0,"quiet stone/metal cue range without playback");Files.write(OUT.resolve("PASS.txt"),RESULTS);Files.writeString(OUT.resolve("views.json"),new GsonBuilder().setPrettyPrinting().create().toJson(VIEWS));done=true;mc.stop();return;}
   int v=stage/2;if(v==11&&reload==null){clear();reload=mc.reloadResourcePacks();return;}if(reload!=null&&!reload.isDone())return;if(reload!=null)reload.join();
   if(!configured){clear();configured=true;settle=0;mc.options.particles().set(v==7?ParticleStatus.MINIMAL:ParticleStatus.ALL);double angle=Math.toRadians(v==1||v>=5&&v!=19?45:v==2?90:v==3?-90:v==4?180:0),radius=v==20?112:v==6?140:v==13?280:v==5?48:v==12?12:72;angle+=Math.PI;var target=original.origin().add(0,16,0);var at=original.origin().add(Math.sin(angle)*radius,v==19?1.62:18,-Math.cos(angle)*radius);double horizontal=Math.hypot(target.x-at.x,target.z-at.z);float yaw=(float)Math.toDegrees(Math.atan2(-(target.x-at.x),target.z-at.z)),pitch=(float)-Math.toDegrees(Math.atan2(target.y-at.y,horizontal));final Vec3 camera=at;double eye=mc.player.getEyeHeight();weather=mc.getSingleplayerServer().submit(()->{var l=mc.getSingleplayerServer().overworld();l.setDayTime(day(v));l.setWeatherParameters(6000,6000,v==9,false);l.setRainLevel(v==9?1:0);mc.getSingleplayerServer().getPlayerList().getPlayers().get(0).teleportTo(l,camera.x,camera.y-eye,camera.z,yaw,pitch);});mc.setCameraEntity(mc.player);}
   if(!weather.isDone())return;weather.join();mc.level.setDayTime(day(v));mc.level.setRainLevel(v==9?1:0);mc.level.setThunderLevel(0);
   if(stage%2==1&&settle==0){long a=age(v);current=new Cod3VisualPacket(original.dimension(),original.template(),-1,original.seed(),mc.level.getGameTime()-a,original.duration(),1,v==15?original.origin().add(0,10,0):original.origin(),original.direction(),original.sequence(),(int)a);Cod3VfxRenderer.receive(current);Cod3VfxRenderer.receive(current);require(active().size()<=1,"duplicate sync is idempotent "+LABELS[v]);}
   settle++;
  }catch(Throwable t){fail(t);}
 }
 @SuppressWarnings("unchecked") private static List<Cod3VisualPacket> active()throws Exception{var f=Cod3VfxRenderer.class.getDeclaredField("ACTIVE");f.setAccessible(true);return (List<Cod3VisualPacket>)f.get(null);}
 private static void clear()throws Exception{active().clear();ScenicModels.clear();ScenicStoneGodGround.clear();ScenicStoneGodSound.clear();}
 @SubscribeEvent public static void capture(TickEvent.RenderTickEvent e){if(!Boolean.getBoolean("dynasty.stoneGodQa")||done||e.phase!=TickEvent.Phase.END||settle<60||stage>=LABELS.length*2)return;
  try{var mc=Minecraft.getInstance();int v=stage/2;String label=LABELS[v];require(GL11.glGetError()==GL11.GL_NO_ERROR,"GL state "+stage);try(var im=Screenshot.takeScreenshot(mc.getMainRenderTarget())){im.writeToFile(OUT.resolve(String.format(Locale.ROOT,"%02d-%s-%s.png",stage,label,stage%2==0?"off":"on")));}
   if(stage%2==1){
    if(v==8||v==9||v==10||v==15)require(actors().isEmpty(),"visibility/actual ground gate creates no model "+label);
    if(v==13||v==16)require(active().isEmpty(),"outside/expiry packet cleanup "+label);
    if(v==12)require(ScenicStoneGodSite.alpha(600,1200,12,1)==0,"near statue fades before screen coverage");
    if(!absent(v)){
     require(actors().size()==1,"exactly one actual stone actor "+label);var actor=actors().values().iterator().next();var renderer=ScenicModels.renderer("stone_god",actor.lod);var model=renderer.getGeoModel();var bones=model.getAnimationProcessor().getRegisteredBones();require(bones.size()==19,"actual 19 Gecko bones "+label);
     var waist=bones.stream().filter(b->b.getName().equals("waist")).findFirst().orElseThrow();double expected=expectedWaist(actor.tick);require(Math.abs(-waist.getRotY()-expected)<.02,"actual exported absolute-age waist animation "+label+" tick="+actor.tick+" actual="+-waist.getRotY()+" expected="+expected);
     var axe=(software.bernie.geckolib.cache.object.GeoBone)bones.stream().filter(b->b.getName().equals("axe")).findFirst().orElseThrow();require(axe.getParent().getName().equals("right_hand"),"real weapon follows gripping hand "+label);
     for(String name:List.of("left_foot","right_foot")){var foot=bones.stream().filter(b->b.getName().equals(name)).findFirst().orElseThrow();require(Math.abs(foot.getPosY())+Math.abs(foot.getRotX())+Math.abs(foot.getRotY())+Math.abs(foot.getRotZ())<1e-6,"actual stationary foot "+name+" "+label);}
     require(ScenicStoneGodGround.valid(mc.level,current),"actual client canyon support and axe clearance "+label);
     var pose=new com.mojang.blaze3d.vertex.PoseStack();renderer.preRender(pose,actor,model.getBakedModel(model.getModelResource(actor)),mc.renderBuffers().bufferSource(),null,false,0,15728880,0,1,1,1,1);var m=pose.last().pose();require(Math.abs(m.m30())+Math.abs(m.m31())+Math.abs(m.m32())<1e-6,"actual authored feet origin without block-center offset "+label);
     VIEWS.add(Map.of("view",label,"lod",actor.lod,"absoluteAge",actor.tick,"actualWaistY",-waist.getRotY(),"anchor",original.origin().toString(),"camera",mc.gameRenderer.getMainCamera().getPosition().toString(),"fixture","flat stone canyon with two explicit 8m sides; no statue entity"));
    }
    require(mc.options.getSoundSourceVolume(net.minecraft.sounds.SoundSource.MASTER)==0,"silent "+label);
   }
   stage++;settle=0;configured=false;
  }catch(Throwable t){fail(t);}
 }
 @SuppressWarnings("unchecked") private static Map<Cod3VisualPacket,ScenicModels.Actor> actors()throws Exception{var f=ScenicModels.class.getDeclaredField("ACTORS");f.setAccessible(true);return (Map<Cod3VisualPacket,ScenicModels.Actor>)f.get(null);}
 private static double expectedWaist(double tick)throws Exception{
  try(var reader=new java.io.InputStreamReader(StoneGodQa.class.getResourceAsStream("/assets/dynasty/animations/scenic/stone_god.animation.json"))){var keys=com.google.gson.JsonParser.parseReader(reader).getAsJsonObject().getAsJsonObject("animations").getAsJsonObject("animation.scenic.idle").getAsJsonObject("bones").getAsJsonObject("waist").getAsJsonObject("rotation");var frames=new TreeMap<Double,Double>();for(var e:keys.entrySet())frames.put(Double.parseDouble(e.getKey()),e.getValue().getAsJsonArray().get(1).getAsDouble());double at=(tick/20)%8;var a=frames.floorEntry(at);var b=frames.ceilingEntry(at);return Math.toRadians(a.getKey().equals(b.getKey())?a.getValue():a.getValue()+(b.getValue()-a.getValue())*(at-a.getKey())/(b.getKey()-a.getKey()));}
 }
 private static void fail(Throwable t){if(done)return;done=true;try{Files.createDirectories(OUT);Files.writeString(OUT.resolve("FAIL.txt"),t.toString()+"\n"+Arrays.toString(t.getStackTrace()));}catch(Exception ignored){}t.printStackTrace();Minecraft.getInstance().stop();}
}
