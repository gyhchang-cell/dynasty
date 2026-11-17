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
/** Silent disposable desert. The template is never placed in the server world. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class GreatWallQa {
 private static final Path OUT=Path.of(System.getProperty("dynasty.auroraQa.output"));
 private static final List<String> RESULTS=new ArrayList<>();private static final List<Map<String,Object>> VIEWS=new ArrayList<>();
 private static final String[] LABELS={"front","45","right","left","back","near","far","minimal","noon","clear","after-dawn","after-reload","inside","outside-region","late-observer","bad-ground","expired","two-packets-single-wall","lod-crossfade","ground-eye"};
 private static int stage,settle;private static boolean started,hidden,done,configured;private static CompletableFuture<Void> prepare,weather,reload;private static Cod3VisualPacket original,current;private static final long DEADLINE=System.nanoTime()+540_000_000_000L;
 private static boolean absent(int v){return v>=8&&v<=10||v==12||v==13||v==15||v==16;}
 private static long age(int v){return v==14?1000:v==16?1200:600;}
 private static long day(int v){return v==8?6000:v==10?2800:600;}
 private static void require(boolean b,String s){if(!b)throw new AssertionError(s);RESULTS.add("PASS "+s);}
 private static net.minecraft.world.level.chunk.ChunkGenerator terrain(net.minecraft.core.RegistryAccess r){
  var settings=net.minecraft.world.level.levelgen.flat.FlatLevelGeneratorSettings.getDefault(r.lookupOrThrow(Registries.BIOME),r.lookupOrThrow(Registries.STRUCTURE_SET),r.lookupOrThrow(Registries.PLACED_FEATURE));settings.getLayersInfo().clear();settings.getLayersInfo().add(new net.minecraft.world.level.levelgen.flat.FlatLayerInfo(126,Blocks.STONE));settings.getLayersInfo().add(new net.minecraft.world.level.levelgen.flat.FlatLayerInfo(1,Blocks.GRASS_BLOCK));settings.updateLayers();
  return new net.minecraft.world.level.levelgen.FlatLevelSource(settings.withBiomeAndLayers(settings.getLayersInfo(),Optional.empty(),r.lookupOrThrow(Registries.BIOME).getOrThrow(Biomes.PLAINS)));
 }
 @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
  if(!Boolean.getBoolean("dynasty.greatWallQa")||done||e.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();
  try{
   Files.createDirectories(OUT);if(!hidden){GLFW.glfwHideWindow(mc.getWindow().getWindow());hidden=true;mc.options.getSoundSourceOptionInstance(net.minecraft.sounds.SoundSource.MASTER).set(0.0);}
   if(System.nanoTime()>DEADLINE)throw new AssertionError("mirage QA deadline");if(mc.getOverlay()!=null)return;if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
   if(!started&&mc.screen instanceof TitleScreen){started=true;mc.options.pauseOnLostFocus=false;mc.options.hideGui=true;mc.options.fov().set(55);mc.options.bobView().set(false);mc.options.renderDistance().set(12);mc.options.cloudStatus().set(CloudStatus.OFF);mc.options.framerateLimit().set(40);var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);rules.getRule(GameRules.RULE_WEATHER_CYCLE).set(false,null);
    mc.createWorldOpenFlows().createFreshLevel("great-wall-qa",new LevelSettings("Disposable mirage QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(1518,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions().replaceOverworldGenerator(r,terrain(r)));return;}
   if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
   if(prepare==null){prepare=mc.getSingleplayerServer().submit(()->{var l=mc.getSingleplayerServer().overworld();l.setDayTime(900);l.setRainLevel(1);l.setWeatherParameters(6000,6000,true,false);for(int x=-4;x<=4;x++)for(int z=-4;z<=4;z++)l.getChunk(x,z);var structure=l.registryAccess().registryOrThrow(Registries.STRUCTURE).get(new net.minecraft.resources.ResourceLocation("dynasty","ruined_battlefield"));var piece=new com.dynasty.structure.BattlefieldPiece(new BlockPos(-16,62,-96));var cp=new ChunkPos(-1,-6);l.getChunk(cp.x,cp.z).setStartForStructure(structure,new net.minecraft.world.level.levelgen.structure.StructureStart(structure,cp,0,new net.minecraft.world.level.levelgen.structure.pieces.PiecesContainer(List.of(piece))));var data=new ScenicEvents();require(data.start(l,18,new Vec3(0,63,0)),"production wall starts on actual battlefield ground");original=data.packets(l,new Vec3(0,63,0)).get(0);require(original.scale()==1&&original.duration()==1200&&original.entityId()==-1,"native nonphysical x1 60-second packet");require(l.getBlockState(BlockPos.containing(original.origin()).above(5)).isAir(),"server contains no phantom wall");mc.getSingleplayerServer().getPlayerList().getPlayers().get(0).setGameMode(GameType.SPECTATOR);});return;}
   if(!prepare.isDone())return;prepare.join();
   if(stage>=LABELS.length*2){clear();require(active().isEmpty(),"scene cleanup");require(ScenicGreatWallSite.soundVolume(900,1200,0,1)<=.035&&ScenicGreatWallSite.soundVolume(900,1200,129,1)==0,"quiet horn cue range without playback");Files.write(OUT.resolve("PASS.txt"),RESULTS);Files.writeString(OUT.resolve("views.json"),new GsonBuilder().setPrettyPrinting().create().toJson(VIEWS));done=true;mc.stop();return;}
   int v=stage/2;if(v==11&&reload==null){clear();reload=mc.reloadResourcePacks();return;}if(reload!=null&&!reload.isDone())return;if(reload!=null)reload.join();
   if(!configured){clear();configured=true;settle=0;mc.options.particles().set(v==7?ParticleStatus.MINIMAL:ParticleStatus.ALL);double angle=Math.toRadians(v==1||v>=5?45:v==2?90:v==3?-90:v==4?180:0),radius=v==18?Math.sqrt(10000-196):v==6?140:v==13?280:v==5?42:v==12?3:64;var target=original.origin().add(0,v==12?0:v==19?1.62:9,0);var at=target.add(Math.sin(angle)*radius,v==19?0:5,-Math.cos(angle)*radius);double horizontal=Math.hypot(target.x-at.x,target.z-at.z);float yaw=(float)Math.toDegrees(Math.atan2(-(target.x-at.x),target.z-at.z)),pitch=(float)-Math.toDegrees(Math.atan2(target.y-at.y,horizontal));final Vec3 camera=at;double eye=mc.player.getEyeHeight();weather=mc.getSingleplayerServer().submit(()->{var l=mc.getSingleplayerServer().overworld();l.setDayTime(day(v));l.setWeatherParameters(6000,6000,v!=9,false);l.setRainLevel(v==9?0:1);mc.getSingleplayerServer().getPlayerList().getPlayers().get(0).teleportTo(l,camera.x,camera.y-eye,camera.z,yaw,pitch);});mc.setCameraEntity(mc.player);}
   if(!weather.isDone())return;weather.join();mc.level.setDayTime(day(v));mc.level.setRainLevel(v==9?0:1);mc.level.setThunderLevel(0);
   if(stage%2==1&&settle==0){long a=age(v);current=new Cod3VisualPacket(original.dimension(),original.template(),-1,original.seed(),mc.level.getGameTime()-a,original.duration(),1,v==15?original.origin().add(0,10,0):original.origin(),original.direction(),original.sequence(),(int)a);Cod3VfxRenderer.receive(current);Cod3VfxRenderer.receive(current);require(active().size()<=1,"duplicate sync is idempotent "+LABELS[v]);if(v==17)Cod3VfxRenderer.receive(new Cod3VisualPacket(current.dimension(),current.template(),-1,current.seed()+1,current.start(),1200,1,current.origin(),current.direction(),current.sequence(),current.tick()));}
   settle++;
  }catch(Throwable t){fail(t);}
 }
 @SuppressWarnings("unchecked") private static List<Cod3VisualPacket> active()throws Exception{var f=Cod3VfxRenderer.class.getDeclaredField("ACTIVE");f.setAccessible(true);return (List<Cod3VisualPacket>)f.get(null);}
 private static void clear()throws Exception{active().clear();ScenicGreatWallRenderer.clear();ScenicGreatWallSound.clear();}
 @SubscribeEvent public static void capture(TickEvent.RenderTickEvent e){if(!Boolean.getBoolean("dynasty.greatWallQa")||done||e.phase!=TickEvent.Phase.END||settle<60||stage>=LABELS.length*2)return;
  try{var mc=Minecraft.getInstance();int v=stage/2;String label=LABELS[v];require(GL11.glGetError()==GL11.GL_NO_ERROR,"GL state "+stage);try(var im=Screenshot.takeScreenshot(mc.getMainRenderTarget())){im.writeToFile(OUT.resolve(String.format(Locale.ROOT,"%02d-%s-%s.png",stage,label,stage%2==0?"off":"on")));}
   if(stage%2==1){require(ScenicGreatWallRenderer.lastDrawnFaces==(absent(v)?0:(v==6||v==7?flagFaces():v==18?5320+flagFaces():5320)),"actual vanilla atlas face draw count "+label+" = "+ScenicGreatWallRenderer.lastDrawnFaces+" visibility="+ScenicGreatWallSite.visibility(mc.level)+" biome="+mc.level.getBiome(BlockPos.containing(original.origin())).unwrapKey()+" centerHeight="+mc.level.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING,0,0)+" anchor="+original.origin());if(v==13||v==16)require(active().isEmpty(),"outside/expiry packet cleanup "+label);require(mc.options.getSoundSourceVolume(net.minecraft.sounds.SoundSource.MASTER)==0,"silent "+label);VIEWS.add(Map.of("view",label,"actualDrawnFaces",ScenicGreatWallRenderer.lastDrawnFaces,"anchor",original.origin().toString(),"camera",mc.gameRenderer.getMainCamera().getPosition().toString(),"fixture","flat plains with registered battlefield start, no template placement"));}
   stage++;settle=0;configured=false;
  }catch(Throwable t){fail(t);}
 }
 private static int flagFaces()throws Exception{try(var r=Minecraft.getInstance().getResourceManager().openAsReader(new net.minecraft.resources.ResourceLocation("dynasty","scenic/great_wall_echo_flags.json"))){return com.google.gson.JsonParser.parseReader(r).getAsJsonObject().getAsJsonArray("exposedFaces").size();}}
 private static void fail(Throwable t){if(done)return;done=true;try{Files.createDirectories(OUT);Files.writeString(OUT.resolve("FAIL.txt"),t.toString()+"\n"+Arrays.toString(t.getStackTrace()));}catch(Exception ignored){}t.printStackTrace();Minecraft.getInstance().stop();}
}
