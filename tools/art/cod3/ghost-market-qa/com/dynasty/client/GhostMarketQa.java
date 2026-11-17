package com.dynasty.client;
import com.dynasty.cod3.*;
import com.google.gson.GsonBuilder;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.*;
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
/** Silent disposable actual ghost-market dimension; dry flat underworld fixture, never places the market NBT. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class GhostMarketQa {
 private static final Path OUT=Path.of(System.getProperty("dynasty.auroraQa.output"));
 private static final List<String> RESULTS=new ArrayList<>();private static final List<Map<String,Object>> VIEWS=new ArrayList<>();
 private static final ResourceKey<Level> DIM=ResourceKey.create(Registries.DIMENSION,new ResourceLocation("dynasty","underworld"));
 private static final String[] LABELS={"front","45","right","left","back","near","far","minimal","day","rain","ground-eye","after-reload","inside","outside-region","late-observer","bad-ground","expired","two-packets-single-city","overworld-cleanup","market-regression","lod-crossfade"};
 private static int stage,settle;private static boolean started,hidden,done,configured;private static CompletableFuture<Void> prepare,weather,reload;private static Cod3VisualPacket original,current,market;private static final long DEADLINE=System.nanoTime()+540_000_000_000L;
 private static boolean absent(int v){return v==8||v==12||v==13||v==15||v==16||v==18||v==19;}
 private static long age(int v){return v==14?1350:v==16?1800:900;}
 private static long day(int v){return v==8?6000:18000;}
 private static void require(boolean b,String s){if(!b)throw new AssertionError(s);RESULTS.add("PASS "+s);}
 private static net.minecraft.world.level.chunk.ChunkGenerator terrain(net.minecraft.core.RegistryAccess r){
  var settings=net.minecraft.world.level.levelgen.flat.FlatLevelGeneratorSettings.getDefault(r.lookupOrThrow(Registries.BIOME),r.lookupOrThrow(Registries.STRUCTURE_SET),r.lookupOrThrow(Registries.PLACED_FEATURE));settings.getLayersInfo().clear();settings.getLayersInfo().add(new net.minecraft.world.level.levelgen.flat.FlatLayerInfo(126,Blocks.STONE));settings.getLayersInfo().add(new net.minecraft.world.level.levelgen.flat.FlatLayerInfo(1,Blocks.SAND));settings.updateLayers();
  return new net.minecraft.world.level.levelgen.FlatLevelSource(settings.withBiomeAndLayers(settings.getLayersInfo(),Optional.empty(),r.lookupOrThrow(Registries.BIOME).getOrThrow(Biomes.DESERT)));
 }
 @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
  if(!Boolean.getBoolean("dynasty.ghostMarketQa")||done||e.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();
  try{
   Files.createDirectories(OUT);if(!hidden){GLFW.glfwHideWindow(mc.getWindow().getWindow());hidden=true;mc.options.getSoundSourceOptionInstance(net.minecraft.sounds.SoundSource.MASTER).set(0.0);}
   if(System.nanoTime()>DEADLINE)throw new AssertionError("palace QA deadline");if(mc.getOverlay()!=null)return;if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
   if(!started&&mc.screen instanceof TitleScreen){started=true;mc.options.pauseOnLostFocus=false;mc.options.hideGui=true;mc.options.fov().set(55);mc.options.bobView().set(false);mc.options.renderDistance().set(12);mc.options.cloudStatus().set(CloudStatus.OFF);mc.options.framerateLimit().set(40);var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);rules.getRule(GameRules.RULE_WEATHER_CYCLE).set(false,null);
    mc.createWorldOpenFlows().createFreshLevel("ghost-market-qa",new LevelSettings("Disposable palace QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(1518,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions().replaceOverworldGenerator(r,terrain(r)));return;}
   if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
   if(prepare==null){prepare=mc.getSingleplayerServer().submit(()->{var server=mc.getSingleplayerServer();var l=server.getLevel(DIM);require(l!=null,"actual production underworld dimension");l.getServer().overworld().setDayTime(18000);l.setRainLevel(0);l.setWeatherParameters(6000,6000,false,false);
    for(int x=-4;x<=4;x++)for(int z=-4;z<=4;z++)l.getChunk(x,z);
    var center=new BlockPos(0,190,0);for(int x=-22;x<=21;x++)for(int z=-30;z<=29;z++)for(int y=-1;y<l.getMaxBuildHeight()-190;y++)l.setBlock(center.offset(x,y,z),y==-1?Blocks.STONE.defaultBlockState():Blocks.AIR.defaultBlockState(),2);
    var data=new ScenicEvents();require(data.start(l,22,new Vec3(0,190,0)),"production ghost market starts on actual dry underworld floor");original=data.packets(l,new Vec3(0,190,0)).get(0);require(original.scale()==1&&original.duration()==1800&&original.entityId()==-1,"native nonphysical x1 90-second packet");require(l.getBlockState(center.above(3)).isAir(),"server contains no phantom shop blocks");
    var overworld=server.overworld();overworld.setDayTime(18000);overworld.setRainLevel(0);for(int x=-4;x<=4;x++)for(int z=-4;z<=4;z++)overworld.getChunk(x,z);var markets=new ScenicEvents();require(markets.start(overworld,14,new Vec3(0,63,0)),"unchanged market supported by actual desert");market=markets.packets(overworld,new Vec3(0,63,0)).get(0);var player=server.getPlayerList().getPlayers().get(0);player.setGameMode(GameType.SPECTATOR);player.teleportTo(l,0,200,-72,0,20);
   });return;}
   if(!prepare.isDone())return;prepare.join();
   if(stage>=LABELS.length*2){clear();require(active().isEmpty(),"scene cleanup");require(ScenicGhostMarketSite.soundVolume(900,1800,0,1)<=.025&&ScenicGhostMarketSite.soundVolume(900,1800,65,1)==0,"quiet market cue range without playback");Files.write(OUT.resolve("PASS.txt"),RESULTS);Files.writeString(OUT.resolve("views.json"),new GsonBuilder().setPrettyPrinting().create().toJson(VIEWS));done=true;mc.stop();return;}
   int v=stage/2;if(v==11&&reload==null){clear();reload=mc.reloadResourcePacks();return;}if(reload!=null&&!reload.isDone())return;if(reload!=null)reload.join();
   if(!configured){clear();configured=true;settle=0;mc.options.particles().set(v==7?ParticleStatus.MINIMAL:ParticleStatus.ALL);double angle=Math.toRadians(v==1||v>=5?45:v==2?90:v==3?-90:v==4?180:0),radius=v==20?Math.sqrt(10000-81):v==6?144:v==13?280:v==5?42:v==12?12:64;var origin=v==19?market.origin():original.origin();var target=origin.add(0,v==19?9:v==10?1.62:4,0);var at=v==12?origin.add(6,3,-8):target.add(Math.sin(angle)*radius,v==10?0:5,-Math.cos(angle)*radius);double horizontal=Math.hypot(target.x-at.x,target.z-at.z);float yaw=(float)Math.toDegrees(Math.atan2(-(target.x-at.x),target.z-at.z)),pitch=(float)-Math.toDegrees(Math.atan2(target.y-at.y,horizontal));final Vec3 camera=at;double eye=mc.player.getEyeHeight();weather=mc.getSingleplayerServer().submit(()->{var server=mc.getSingleplayerServer();var l=v==18||v==19?server.overworld():server.getLevel(DIM);l.getServer().overworld().setDayTime(day(v));l.setWeatherParameters(6000,6000,v==9,false);l.setRainLevel(v==9?1:0);server.getPlayerList().getPlayers().get(0).teleportTo(l,camera.x,camera.y-eye,camera.z,yaw,pitch);});mc.setCameraEntity(mc.player);}
   if(!weather.isDone())return;weather.join();if(!mc.level.dimension().equals(v==18||v==19?Level.OVERWORLD:DIM))return;mc.level.setDayTime(day(v));mc.level.setRainLevel(v==9?1:0);mc.level.setThunderLevel(0);
   if(stage%2==1&&settle==0){long a=age(v);var o=v==19?market:original;current=new Cod3VisualPacket(o.dimension(),o.template(),-1,o.seed(),mc.level.getGameTime()-a,o.duration(),1,v==15?o.origin().add(0,1,0):o.origin(),o.direction(),o.sequence(),(int)a);Cod3VfxRenderer.receive(current);Cod3VfxRenderer.receive(current);require(active().size()<=1,"duplicate sync is idempotent "+LABELS[v]);if(v==17)Cod3VfxRenderer.receive(new Cod3VisualPacket(current.dimension(),current.template(),-1,current.seed()+1,current.start(),1800,1,current.origin(),current.direction(),current.sequence(),current.tick()));}
   settle++;
  }catch(Throwable t){fail(t);}
 }
 @SuppressWarnings("unchecked") private static List<Cod3VisualPacket> active()throws Exception{var f=Cod3VfxRenderer.class.getDeclaredField("ACTIVE");f.setAccessible(true);return (List<Cod3VisualPacket>)f.get(null);}
 private static void clear()throws Exception{active().clear();ScenicGhostMarketRenderer.clear();ScenicGhostMarketSound.clear();ScenicGhostMarketLights.clear();ScenicMirageRenderer.clear();ScenicMirageSound.clear();}
 @SubscribeEvent public static void capture(TickEvent.RenderTickEvent e){if(!Boolean.getBoolean("dynasty.ghostMarketQa")||done||e.phase!=TickEvent.Phase.END||settle<60||stage>=LABELS.length*2)return;
  try{var mc=Minecraft.getInstance();int v=stage/2;String label=LABELS[v];require(GL11.glGetError()==GL11.GL_NO_ERROR,"GL state "+stage);try(var im=Screenshot.takeScreenshot(mc.getMainRenderTarget())){im.writeToFile(OUT.resolve(String.format(Locale.ROOT,"%02d-%s-%s.png",stage,label,stage%2==0?"off":"on")));}
   if(stage%2==1){require(ScenicGhostMarketRenderer.lastDrawnFaces==(absent(v)||v==6||v==7?0:5564),"actual ghost-market atlas face draw count "+label+" = "+ScenicGhostMarketRenderer.lastDrawnFaces+" dimension="+mc.level.dimension()+" anchor="+original.origin());require(ScenicGhostMarketRenderer.lastLightQuads==(absent(v)?0:v==7?24:v==6||v==20?36:48),"actual anchored ghost flames "+label+" = "+ScenicGhostMarketRenderer.lastLightQuads);if(v==13||v==16||v==18)require(active().isEmpty(),"outside/expiry/wrong dimension packet cleanup "+label);if(v==19)require(ScenicMirageRenderer.lastDrawnFaces==7370,"shared atlas mesh preserves actual market faces");require(mc.options.getSoundSourceVolume(net.minecraft.sounds.SoundSource.MASTER)==0,"silent "+label);VIEWS.add(Map.of("view",label,"actualDrawnFaces",ScenicGhostMarketRenderer.lastDrawnFaces,"ghostLightQuads",ScenicGhostMarketRenderer.lastLightQuads,"anchor",original.origin().toString(),"camera",mc.gameRenderer.getMainCamera().getPosition().toString(),"fixture","actual underworld dimension; dry flat platform, no template placement"));}
   stage++;settle=0;configured=false;
  }catch(Throwable t){fail(t);}
 }
 private static void fail(Throwable t){if(done)return;done=true;try{Files.createDirectories(OUT);Files.writeString(OUT.resolve("FAIL.txt"),t.toString()+"\n"+Arrays.toString(t.getStackTrace()));}catch(Exception ignored){}t.printStackTrace();Minecraft.getInstance().stop();}
}
