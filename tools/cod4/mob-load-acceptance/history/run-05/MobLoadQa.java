package com.dynasty.mobqa;

import com.dynasty.expansion.*;
import com.google.gson.GsonBuilder;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.model.geom.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.cache.object.GeoBone;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;

/** Isolated QA only: new world, native registered renderers and native enabled mob AI. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class MobLoadQa {
 static final Path OUT=Path.of(System.getProperty("dynasty.mobqa.output","mobqa-missing"));
 static final boolean REMAINING=Boolean.getBoolean("dynasty.mobqa.remaining");
 static String[] remainingPhases(){var result=new ArrayList<String>();result.add("baseline-dry");for(var spec:SecondaryMobs.SPECS)if(!spec.aquatic()&&!Set.of("tree_spirit","locust_swarm","wandering_spirit").contains(spec.id()))result.add(spec.id());result.add("baseline-water");for(var spec:SecondaryMobs.SPECS)if(spec.aquatic()&&!spec.id().equals("crab_soldier"))result.add(spec.id());result.add("baseline-after");result.add("locust_swarm--player-contact");return result.toArray(String[]::new);}
 static String mobId(){return PHASES[phase].split("--")[0];}
 static boolean aquatic(){return PHASES[phase].equals("baseline-water")||SecondaryMobs.SPECS.stream().anyMatch(x->x.id().equals(mobId())&&x.aquatic());}
 static boolean contact(){return PHASES[phase].endsWith("--player-contact");}
 static final String[] PHASES=Boolean.getBoolean("dynasty.mobqa.contactOnly")?new String[]{"baseline-dry","locust_swarm--player-contact"}:REMAINING?remainingPhases():new String[]{"baseline-dry","tree_spirit","locust_swarm","wandering_spirit","baseline-water","crab_soldier","baseline-after"};
 static final List<String> frames=new CopyOnWriteArrayList<>(),ticks=new CopyOnWriteArrayList<>(),attacks=new CopyOnWriteArrayList<>();
 static final List<SecondaryMob> cohort=new ArrayList<>();
 static final Map<Integer,Vec3> starts=new HashMap<>();
 static volatile int phase=-1,age;static volatile boolean ready,done;static boolean started,prepared,geometry;static long lastFrame,renderStart,tickStart;static int waited;static LivingEntity dummy;
 static final Map<String,Object> counts=new LinkedHashMap<>();
 static int renderCount;static final Set<Integer> rendered=new HashSet<>();
 static final int WARM=REMAINING?100:200,SAMPLE=REMAINING?200:400;
 static net.minecraft.world.entity.decoration.ArmorStand cameraMarker;static volatile int cameraId=-1;
 static final List<String> damages=new CopyOnWriteArrayList<>();
 static void checkpoint()throws Exception {Files.write(OUT.resolve("frames.csv"),frames);Files.write(OUT.resolve("ticks.csv"),ticks);Files.write(OUT.resolve("attacks.csv"),attacks);Files.write(OUT.resolve("damage.csv"),damages);write("progress.json",Map.of("completedPhase",phase<PHASES.length?PHASES[phase]:"all","index",phase,"phases",PHASES));}
 static void write(String file,Object value)throws Exception {Files.createDirectories(OUT);Files.writeString(OUT.resolve(file),new GsonBuilder().setPrettyPrinting().create().toJson(value));}
 static void failure(Throwable t){try{Files.createDirectories(OUT);Files.writeString(OUT.resolve("FAIL.txt"),t.toString()+"\n"+Arrays.toString(t.getStackTrace()));}catch(Exception ignored){}done=true;Minecraft.getInstance().stop();}
 @SubscribeEvent public static void client(TickEvent.ClientTickEvent e){
  if(System.getProperty("dynasty.mobqa.output")==null||done||e.phase!=TickEvent.Phase.END)return;
  var mc=Minecraft.getInstance();try{
   if(mc.getOverlay()!=null)return;
   if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
   if(!started&&mc.screen instanceof TitleScreen){
    if(!mc.gameDirectory.getCanonicalPath().contains("/tools/cod4/mob-load-acceptance/.work/run-"))throw new AssertionError("Wrong instance");
    started=true;var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);rules.getRule(GameRules.RULE_WEATHER_CYCLE).set(false,null);
    mc.createWorldOpenFlows().createFreshLevel("mob-load-private-"+System.currentTimeMillis(),new LevelSettings("COD4 read-only mob QA",GameType.CREATIVE,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(20261023L,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
   }
   if(mc.level==null||mc.player==null||++waited<120)return;
   if(!geometry){dumpGeometry(mc);geometry=true;if(Boolean.getBoolean("dynasty.mobqa.geometryOnly")){write("geometry-only-finished.json",Map.of("complete",true,"scope","native baked model probe only; no cohort rerun"));done=true;mc.stop();return;}}
   if(!prepared){prepared=true;mc.getSingleplayerServer().execute(()->{try{prepare(mc.getSingleplayerServer().overworld());ready=true;}catch(Throwable ex){failure(ex);}});}
   mc.options.hideGui=true;
   if(cameraId>=0&&mc.level.getEntity(cameraId)!=null){var camera=mc.level.getEntity(cameraId);camera.moveTo(0,76,25,180,29);camera.yRotO=180;camera.xRotO=29;mc.setCameraEntity(camera);}
  }catch(Throwable ex){failure(ex);}
 }
 static void prepare(ServerLevel l){
  l.setDayTime(6000);l.setWeatherParameters(100000,0,false,false);
  for(int x=-21;x<=21;x++)for(int z=-18;z<=18;z++){
   for(int y=60;y<=63;y++)l.setBlock(new BlockPos(x,y,z),Blocks.STONE.defaultBlockState(),2);
   for(int y=64;y<=71;y++)l.setBlock(new BlockPos(x,y,z),Blocks.AIR.defaultBlockState(),2);
  }
  var p=l.getServer().getPlayerList().getPlayers().get(0);p.teleportTo(l,0,76,25,180,29);p.setNoGravity(true);p.getAbilities().flying=true;p.onUpdateAbilities();
 }
 static void next(ServerLevel l)throws Exception{
  for(var m:cohort)m.discard();cohort.clear();starts.clear();if(dummy!=null)dummy.discard();dummy=null;
  if(phase>=0)checkpoint();
  phase++;age=0;
  if(phase>=PHASES.length){
   ready=false;Files.write(OUT.resolve("frames.csv"),frames);Files.write(OUT.resolve("ticks.csv"),ticks);Files.write(OUT.resolve("attacks.csv"),attacks);
   write("run-finished.json",Map.of("phases",PHASES,"warmupTicks",WARM,"sampleTicks",SAMPLE,"scope",REMAINING?"Remaining26 cohorts100+200 plus locust real-player contact boundary; not all skills or full-pack acceptance":"4 representative cohorts200+400"));
   done=true;Minecraft.getInstance().execute(()->Minecraft.getInstance().stop());return;
  }
  boolean water=REMAINING?aquatic():phase==4||phase==5;
  if(REMAINING){
   // Closed transparent enclosure prevents escape and makes the water cohort fully submerged.
   for(int x=-19;x<=19;x++)for(int z=-17;z<=17;z++)for(int y=64;y<=74;y++){
    boolean border=Math.abs(x)==19||Math.abs(z)==17;boolean roof=y==(water?71:contact()?68:74);
    var block=border||roof?Blocks.GLASS:y<(water?71:64)?Blocks.WATER:Blocks.AIR;
    l.setBlock(new BlockPos(x,y,z),block.defaultBlockState(),2);
   }
  }
  if(!REMAINING)for(int x=-18;x<=18;x++)for(int z=-16;z<=16;z++)for(int y=64;y<=67;y++)l.setBlock(new BlockPos(x,y,z),(water?Blocks.WATER:Blocks.AIR).defaultBlockState(),2);
  var player=l.getServer().getPlayerList().getPlayers().get(0);
  if(contact()){
   player.setGameMode(GameType.SURVIVAL);player.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).setBaseValue(100000);player.setHealth(player.getMaxHealth());player.teleportTo(l,0,66,0,0,0);player.setNoGravity(true);
   cameraMarker=EntityType.ARMOR_STAND.create(l);cameraMarker.moveTo(0,76,25,180,29);cameraMarker.setNoGravity(true);cameraMarker.setInvisible(true);cameraMarker.setInvulnerable(true);l.addFreshEntity(cameraMarker);cameraId=cameraMarker.getId();
  }
  if(PHASES[phase].startsWith("baseline"))return;
  if(!contact()){dummy=EntityType.COW.create(l);dummy.moveTo(0,water?66:64,0,0,0);((Mob)dummy).setNoAi(true);dummy.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).setBaseValue(1000000);dummy.setHealth(1000000);dummy.setNoGravity(water);l.addFreshEntity(dummy);}
  for(int i=0;i<20;i++){
   var m=SecondaryMobs.TYPES.get(mobId()).get().create(l);double x=(i%5-2)*3.1,z=(i/5-1.5)*3.1;
   m.moveTo(x,water?65.5:m.spec.flying()?67:64,z,0,0);m.setPersistenceRequired();m.setInvulnerable(true);m.setTarget(contact()?player:dummy);l.addFreshEntity(m);cohort.add(m);starts.put(m.getId(),m.position());
   if(REMAINING&&Set.of("famished_refugee","herb_picker","swindler","snail_maiden").contains(m.spec.id())){m.setInvulnerable(false);m.hurt(l.damageSources().playerAttack(player),1);}

  }
 }
 @SubscribeEvent public static void server(TickEvent.ServerTickEvent e){
  if(!ready||done)return;
  if(e.phase==TickEvent.Phase.START){tickStart=System.nanoTime();return;}
  try{
   var l=e.getServer().overworld();if(phase<0){frames.add("phase,age,interval_ms,render_ms,rendered_cohort,client_cohort,particles,client_entities");ticks.add("phase,age,tick_ms,alive,no_ai,active_path,moved_025,with_target,projectiles,in_water,fully_submerged,min_y,max_y");attacks.add("phase,age,source,target");damages.add("phase,age,source,target,amount");next(l);return;}
   age++;if(dummy!=null)dummy.setHealth(dummy.getMaxHealth());
   var player=l.getServer().getPlayerList().getPlayers().get(0);if(contact()){player.setHealth(player.getMaxHealth());player.getFoodData().setFoodLevel(20);}
   if(REMAINING&&age%60==0)for(var m:cohort)if(Set.of("famished_refugee","herb_picker","swindler","snail_maiden").contains(m.spec.id())){m.setHealth(m.getMaxHealth());m.hurt(l.damageSources().playerAttack(player),1);}

   if(dummy!=null&&age%80==0)dummy.teleportTo((age/80%2==0?7:-7),(REMAINING?aquatic():phase==5)?66:64,(age/160%2==0?5:-5));
   int alive=0,noai=0,paths=0,moved=0,target=0,inWater=0,submerged=0;double minY=Double.POSITIVE_INFINITY,maxY=Double.NEGATIVE_INFINITY;
   for(var m:cohort){if(m.isAlive())alive++;if(m.isNoAi())noai++;if(!m.getNavigation().isDone())paths++;if(m.position().distanceToSqr(starts.get(m.getId()))>.0625)moved++;if(m.getTarget()!=null)target++;if(m.isInWater())inWater++;if(l.getFluidState(BlockPos.containing(m.getX(),m.getBoundingBox().maxY-.01,m.getZ())).is(net.minecraft.tags.FluidTags.WATER)&&m.isInWater())submerged++;minY=Math.min(minY,m.getY());maxY=Math.max(maxY,m.getY());}
   if(age>WARM){int proj=0;for(var ent:l.getAllEntities())if(ent instanceof SecondaryProjectile)proj++;
    ticks.add(String.format(Locale.ROOT,"%s,%d,%.5f,%d,%d,%d,%d,%d,%d,%d,%d,%.3f,%.3f",PHASES[phase],age,(System.nanoTime()-tickStart)/1e6,alive,noai,paths,moved,target,proj,inWater,submerged,cohort.isEmpty()?0:minY,cohort.isEmpty()?0:maxY));}
   if(age==WARM+SAMPLE/2){int p=phase;Minecraft.getInstance().execute(()->{try{var mc=Minecraft.getInstance();try(var img=Screenshot.takeScreenshot(mc.getMainRenderTarget())){img.writeToFile(OUT.resolve(PHASES[p]+".png"));}}catch(Throwable ex){failure(ex);}});}
   if(age>=WARM+SAMPLE)next(l);
  }catch(Throwable ex){failure(ex);}
 }
 @SubscribeEvent public static void attack(LivingAttackEvent e){if(ready&&!done&&e.getSource().getEntity() instanceof SecondaryMob m)attacks.add(PHASES[phase]+","+age+","+m.spec.id()+","+e.getEntity().getType().toShortString());}
 @SubscribeEvent public static void damage(net.minecraftforge.event.entity.living.LivingDamageEvent e){if(ready&&!done&&e.getSource().getEntity() instanceof SecondaryMob m)damages.add(PHASES[phase]+","+age+","+m.spec.id()+","+e.getEntity().getType().toShortString()+","+e.getAmount());}
 @SubscribeEvent public static void livingRender(net.minecraftforge.client.event.RenderLivingEvent.Post<?,?> e){if(e.getEntity() instanceof SecondaryMob m)rendered.add(m.getId());}
 // Forge per-entity render event emitted by GeckoLib (verified against bytecode); marks actual submitted mob render calls.
 @SubscribeEvent public static void gecko(software.bernie.geckolib.event.GeoRenderEvent.Entity.Pre e){if(e.getEntity() instanceof SecondaryMob m){rendered.add(m.getId());}}
 @SubscribeEvent public static void frame(TickEvent.RenderTickEvent e){
  if(!ready||done||phase<0||phase>=PHASES.length)return;
  if(e.phase==TickEvent.Phase.START){renderStart=System.nanoTime();rendered.clear();return;}
  var mc=Minecraft.getInstance();long now=System.nanoTime();
  if(age>WARM&&mc.level!=null){int client=0;for(var en:mc.level.entitiesForRendering())if(en instanceof SecondaryMob)client++;
   frames.add(String.format(Locale.ROOT,"%s,%d,%.5f,%.5f,%d,%d,%s,%d",PHASES[phase],age,lastFrame==0?0:(now-lastFrame)/1e6,(now-renderStart)/1e6,rendered.size(),client,mc.particleEngine.countParticles(),mc.level.getEntityCount()));}
  lastFrame=now;
 }
 @SuppressWarnings({"rawtypes","unchecked"}) static Map<String,Object> entityGeometry(Minecraft mc,Entity m)throws Exception{
  var r=mc.getEntityRenderDispatcher().getRenderer(m);int[] n={0,0};String resource;
  if(r instanceof GeoEntityRenderer geo){var model=geo.getGeoModel();var loc=model.getModelResource((software.bernie.geckolib.core.animatable.GeoAnimatable)m);resource=loc.toString();var baked=model.getBakedModel(loc);for(var b:(List<GeoBone>)baked.topLevelBones())bones(b,n);}
  else if(r instanceof com.dynasty.client.steve.SteveFighterRenderer steve){
   var model=steve.getModel();var rf=com.dynasty.client.steve.SteveFighterModel.class.getDeclaredField("root");rf.setAccessible(true);var root=(ModelPart)rf.get(model);var pf=ModelPart.Cube.class.getDeclaredField("polygons");pf.setAccessible(true);
   root.visit(new PoseStack(),(pose,path,index,cube)->{n[0]++;try{n[1]+=((Object[])pf.get(cube)).length;}catch(Exception ex){throw new RuntimeException(ex);}});
   resource=com.dynasty.client.steve.SteveFighterModel.definition(net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getKey(m.getType()).getPath()).toString();
  }else throw new AssertionError("Unrecognized renderer "+r.getClass());
  return Map.of("cuboids",n[0],"quads",n[1],"resource",resource,"renderer",r.getClass().getName());
 }
 static void bones(GeoBone b,int[] n){for(var c:b.getCubes()){n[0]++;for(var q:c.quads())if(q!=null)n[1]++;}for(var child:b.getChildBones())bones(child,n);}
 @SuppressWarnings({"rawtypes","unchecked"}) static void dumpGeometry(Minecraft mc)throws Exception{
  var all=new LinkedHashMap<String,Object>();var vanilla=new LinkedHashMap<String,Object>();
  for(String id:List.of("ZOMBIE","VILLAGER","FOX","WOLF","PIG","OCELOT","IRON_GOLEM","SILVERFISH","VEX","DROWNED","COD","TURTLE","SPIDER","BAT","PARROT","CHICKEN","RAVAGER")){
   var key=(ModelLayerLocation)ModelLayers.class.getField(id).get(null);var root=mc.getEntityModels().bakeLayer(key);int[] n={0,0};var f=ModelPart.Cube.class.getDeclaredField("polygons");f.setAccessible(true);
   root.visit(new PoseStack(),(pose,path,index,cube)->{n[0]++;try{n[1]+=((Object[])f.get(cube)).length;}catch(Exception ex){throw new RuntimeException(ex);}});
   vanilla.put(id,Map.of("cuboids",n[0],"quads",n[1],"layer",key.toString(),"method","native bakeLayer + ModelPart.visit; all baked body cubes, excluding equipment/external render layers"));
  }
  for(var spec:SecondaryMobs.SPECS){
   var m=SecondaryMobs.TYPES.get(spec.id()).get().create(mc.level);var info=new LinkedHashMap<String,Object>(entityGeometry(mc,m));info.put("navigation",m.getNavigation().getClass().getName());info.put("flying",spec.flying());info.put("aquatic",spec.aquatic());all.put(spec.id(),info);
  }
  var core=new TreeMap<String,Object>();
  for(var field:com.dynasty.blueprint.BlueprintEntities.class.getFields()){
   if(!net.minecraftforge.registries.RegistryObject.class.isAssignableFrom(field.getType()))continue;
   var obj=((net.minecraftforge.registries.RegistryObject<?>)field.get(null)).get();
   if(!(obj instanceof EntityType<?> type))continue;var entity=type.create(mc.level);
   if(!(entity instanceof com.dynasty.blueprint.TemplateMob))continue;
   core.put(net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getKey(type).getPath(),entityGeometry(mc,entity));
  }
  if(core.size()!=30)throw new AssertionError("Expected exactly30 COD1 basic mobs, got"+core.size());
  write("native-cod1-geometry.json",core);
  write("native-geometry.json",Map.of("secondary",all,"vanilla",vanilla));
 }
}
