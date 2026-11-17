package com.dynasty.client;
import com.dynasty.client.steve.*;
import com.dynasty.blueprint.*;
import com.dynasty.entity.DynastyHumanoidMob;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.*;
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

/** Muted disposable art fixture. Uses real inventory, bow-use state and synchronized attack clocks. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class Cod1CreatureQa {
 static final boolean ON=Boolean.getBoolean("dynasty.cod1CreatureQa");
 static final Path OUT=Path.of(System.getProperty("dynasty.cod1CreatureQa.output","build/steve-fighters-qa"));
 static final String ONLY=System.getProperty("dynasty.cod1CreatureQa.only", "");
 static boolean started,done,captured,actionStarted;static int stage=-1,wait;static Mob fixture;static int entityId;static CompletableFuture<Integer> pending;static CompletableFuture<?> action;
 static final String[] IDS={"gudu_tianzhunv","yinyang_liandan_fangshi","fubo_xunhai_yecha","banshan_jiazhou_shikuang","mojia_jueying_cike","hanshan_tongjia_juyuan","qingdeng_panguan_guichai","liefeng_jindiao_yushi","zhenmu_suanni_tonghou"};
 static final int[] SKILLS={373,381,391,403,412,421,432,441,451};
 static final String[] VIEWS={"front","45","side","back","action"};static final List<String> LOG=new ArrayList<>();
 @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
  if(!ON||done||e.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();
  try{
   if(mc.getOverlay()!=null)return;if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
   if(!started&&mc.screen instanceof TitleScreen){
    if(!mc.gameDirectory.getAbsolutePath().contains("/build/boss-eight-native/cod1-v32"))throw new AssertionError("Not isolated QA");
    started=true;Files.createDirectories(OUT);mc.options.renderDistance().set(3);mc.options.fov().set(40);mc.options.pauseOnLostFocus=false;
    GameRules rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
    var settings=new LevelSettings("Cod1 creatures art",GameType.CREATIVE,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT);
    mc.createWorldOpenFlows().createFreshLevel("fighters-"+System.currentTimeMillis(),settings,new WorldOptions(42,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
   }
   if(mc.level==null||mc.player==null)return;
   if(stage<0||captured){stage++;while(!ONLY.isEmpty()&&stage<IDS.length*5&&!IDS[stage/5].equals(ONLY))stage++;captured=false;actionStarted=false;wait=0;if(stage>=IDS.length*5){finish(mc,null);return;}pending=mc.getSingleplayerServer().submit(()->prepare(mc));return;}
   if(!pending.isDone())return;entityId=pending.join();if(!(mc.level.getEntity(entityId) instanceof Mob mob))return;
   if(mc.screen!=null)mc.setScreen(null);if(wait++==0)camera(mc);
   // Art capture only: follow real skill movement; do not pin the creature or change its attack.
   if(stage%5==4&&mc.getCameraEntity()!=null){
    var cam=mc.getCameraEntity();double a=Math.toRadians(45),r=10;
    cam.setPos(mob.getX()+Math.sin(a)*r,mob.getY()+1.75-cam.getEyeHeight(),mob.getZ()+Math.cos(a)*r);cam.setOldPosAndRot();
   }
   if(stage%5==4&&wait>=32&&!actionStarted){actionStarted=true;action=mc.getSingleplayerServer().submit(()->beginAction(mc));}
   if(actionStarted&&action.isDone())action.join();

  }catch(Throwable t){finish(mc,t);}
 }
 static int prepare(Minecraft mc){
  var server=mc.getSingleplayerServer();var world=server.overworld();world.setDayTime(6000);for(int cx=-1;cx<=1;cx++)for(int cz=-1;cz<=1;cz++)world.setChunkForced(cx,cz,true);
  var remove=new ArrayList<Entity>();for(var e:world.getAllEntities())if(!(e instanceof net.minecraft.server.level.ServerPlayer))remove.add(e);remove.forEach(Entity::discard);
  for(int x=-10;x<=10;x++)for(int z=-10;z<=10;z++){
   world.setBlockAndUpdate(new BlockPos(x,-61,z),(Math.floorMod(x+z,6)==0?Blocks.STONE_BRICKS:Blocks.GRASS_BLOCK).defaultBlockState());for(int y=-60;y<-54;y++)world.setBlockAndUpdate(new BlockPos(x,y,z),Blocks.AIR.defaultBlockState());
  }
  String id=IDS[stage/5];var type=net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("dynasty",id));fixture=(Mob)type.create(world);fixture.moveTo(0,-60,0,0,0);fixture.setNoAi(true);fixture.setSilent(true);fixture.setPersistenceRequired();world.addFreshEntity(fixture);
  for(var p:server.getPlayerList().getPlayers())p.teleportTo(world,-2,-60,0,180,0);
  return fixture.getId();
 }
 static void beginAction(Minecraft mc){
  try{
   var world=mc.getSingleplayerServer().overworld();var cow=EntityType.COW.create(world);
   cow.moveTo(0,-60,6,180,0);cow.setNoAi(true);cow.setSilent(true);cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(10000);cow.setHealth(10000);
   cow.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.INVISIBILITY,2000,0,false,false));world.addFreshEntity(cow);
   // NoAI fixtures do not run the ordinary locomotion step. Set only their grounded fixture state after validating a real floor.
   if(!world.getBlockState(fixture.blockPosition().below()).isFaceSturdy(world,fixture.blockPosition().below(),Direction.UP))throw new AssertionError("Fixture has no supporting floor");
   fixture.setOnGround(true);
   int skill=SKILLS[stage/5];boolean ok=(Boolean)fixture.getClass().getMethod("startSkill",int.class,LivingEntity.class).invoke(fixture,skill,cow);
   if(!ok)throw new AssertionError("Existing skill rejected "+IDS[stage/5]+" "+skill+" ground="+fixture.onGround()+" pos="+fixture.position()+" tick="+fixture.tickCount+" sight="+fixture.hasLineOfSight(cow)+" allied="+com.dynasty.blueprint.combat.Combatant.allied(fixture,cow));
   LOG.add(IDS[stage/5]+" synchronized existing skill="+skill);
  }catch(ReflectiveOperationException e){throw new RuntimeException(e);}
 }
 static void camera(Minecraft mc){double angle=switch(stage%5){case 1,4->45;case 2->90;case 3->180;default->0;};double a=Math.toRadians(angle),r=10.0;
  var cam=new ArmorStand(mc.level,Math.sin(a)*r,-60,Math.cos(a)*r);cam.setPos(cam.getX(),-58.25-cam.getEyeHeight(),cam.getZ());cam.setYRot((float)(180-angle));cam.setXRot(3);cam.setYHeadRot(cam.getYRot());cam.yHeadRotO=cam.getYRot();cam.setOldPosAndRot();mc.options.setCameraType(CameraType.FIRST_PERSON);mc.options.hideGui=true;mc.setCameraEntity(cam);
 }
 @SubscribeEvent public static void render(TickEvent.RenderTickEvent e){
  if(!ON||done||captured||stage<0||e.phase!=TickEvent.Phase.END||wait<(stage==0?120:32))return;var mc=Minecraft.getInstance();
  try{
   if(!(mc.level.getEntity(entityId) instanceof Mob mob))return;var renderer=mc.getEntityRenderDispatcher().getRenderer(mob);if(!(renderer instanceof software.bernie.geckolib.renderer.GeoEntityRenderer))throw new AssertionError("Wrong creature binding "+renderer);
   String id=IDS[stage/5];String label=id+"-"+VIEWS[stage%5];
   for(var path:List.of(new ResourceLocation("dynasty","geo/blueprint/elite/"+id+".geo.json"),new ResourceLocation("dynasty","textures/entity/blueprint/elite/"+id+".png")))try(var stream=mc.getResourceManager().getResourceOrThrow(path).open()){if(stream.readAllBytes().length==0)throw new AssertionError("Empty resource");}

   try(var shot=Screenshot.takeScreenshot(mc.getMainRenderTarget())){
    int green=0;for(int yy=shot.getHeight()*2/3;yy<shot.getHeight();yy+=30)for(int xx=0;xx<shot.getWidth();xx+=30){int c=shot.getPixelRGBA(xx,yy);if((c>>8&255)>(c&255)*1.05&&(c>>8&255)>(c>>16&255)*1.1)green++;}
    if(green<20){if(wait>300)throw new AssertionError("Scene not loaded "+label);return;}
    if(stage%5==4){
     int frame=Math.min(144,wait-34);if(frame<0||frame%4!=0)return;
     var frames=OUT.resolve("frames/"+id);Files.createDirectories(frames);shot.writeToFile(frames.resolve(String.format("%03d.png",frame)));
     LOG.add(id+" frame="+frame+" clientTick="+mob.tickCount+(mob instanceof TemplateMob t?" actionTick="+t.actionAge(0):""));
     if(frame>=16&&!Files.exists(OUT.resolve(String.format("%02d-%s.png",stage,label))))shot.writeToFile(OUT.resolve(String.format("%02d-%s.png",stage,label)));
     if(frame<144)return;
    }else shot.writeToFile(OUT.resolve(String.format("%02d-%s.png",stage,label)));
   }
   LOG.add(label+" renderer="+renderer.getClass().getSimpleName()+" bowUse="+mob.isUsingItem());Files.writeString(OUT.resolve("progress.txt"),String.join("\n",LOG));captured=true;
  }catch(Throwable t){finish(mc,t);}
 }
 static void finish(Minecraft mc,Throwable t){if(done)return;done=true;try{Files.createDirectories(OUT);Files.writeString(OUT.resolve(t==null?"PASS.txt":"FAIL.txt"),String.join("\n",LOG)+"\n"+(t==null?"PASS: "+(ONLY.isEmpty()?IDS.length*5:5)+" native binding/views, "+(ONLY.isEmpty()?IDS.length:1)+" synchronized-clock sequences (AI disabled, grounded fixtures). Natural combat remains separate verification.":t.toString()));}catch(Exception ignored){}if(t!=null)t.printStackTrace();mc.stop();}
}
