package com.dynasty.statusqa;
import com.google.gson.*;
import com.dynasty.cod3.EquipmentFeedback;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.*;
import net.minecraftforge.event.entity.*;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.event.entity.player.*;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

@Mod("dynastystatusqa")
public final class StatusVisualAcceptance {
 static final Path OUT=Path.of(System.getProperty("dynasty.statusqa.output"));
 static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
 static void write(String n,Object o)throws Exception{Files.writeString(OUT.resolve(n),JSON.toJson(o));}
 static String id(ItemStack s){return ForgeRegistries.ITEMS.getKey(s.getItem()).toString();}
 static ItemStack item(String s){return new ItemStack(Objects.requireNonNull(ForgeRegistries.ITEMS.getValue(new ResourceLocation(s.contains(":")?s:"dynasty:"+s))));}
 static String text(JsonObject c,String k,String fallback){return c.has(k)?c.get(k).getAsString():fallback;}
 static int num(JsonObject c,String k,int fallback){return c.has(k)?c.get(k).getAsInt():fallback;}
 static boolean flag(JsonObject c,String k){return c.has(k)&&c.get(k).getAsBoolean();}
 static final List<LivingEntity> targets=new ArrayList<>();
 static final List<BlockPos> blocks=new ArrayList<>();
 static Object entity(Entity e){var d=new LinkedHashMap<String,Object>();d.put("id",e.getId());d.put("uuid",e.getUUID().toString());d.put("type",ForgeRegistries.ENTITY_TYPES.getKey(e.getType()).toString());d.put("pos",Probe.v(e.position()));d.put("velocity",Probe.v(e.getDeltaMovement()));d.put("onGround",e.onGround());d.put("alive",e.isAlive());d.put("onFire",e.isOnFire());d.put("inWater",e.isInWater());d.put("underWater",e.isUnderWater());d.put("swimming",e.isSwimming());d.put("sprinting",e.isSprinting());d.put("yaw",e.getYRot());d.put("pitch",e.getXRot());if(e instanceof LivingEntity l){d.put("health",l.getHealth());d.put("maxHealth",l.getMaxHealth());d.put("effects",l.getActiveEffects().stream().map(x->Map.of("effect",ForgeRegistries.MOB_EFFECTS.getKey(x.getEffect()).toString(),"amplifier",x.getAmplifier(),"duration",x.getDuration())).toList());d.put("armor",l.getArmorValue());d.put("speed",l.getAttributeValue(Attributes.MOVEMENT_SPEED));d.put("held",id(l.getMainHandItem()));d.put("armorItems",java.util.stream.StreamSupport.stream(l.getArmorSlots().spliterator(),false).map(StatusVisualAcceptance::id).toList());}return d;}
 @Mod.EventBusSubscriber(modid="dynastystatusqa") public static final class Server {
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void effectAdded(MobEffectEvent.Added e){if(!e.getEntity().level().isClientSide)Probe.event("native-effect-added",Map.of("tick",e.getEntity().level().getGameTime(),"target",entity(e.getEntity()),"effect",ForgeRegistries.MOB_EFFECTS.getKey(e.getEffectInstance().getEffect()).toString()));}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void effectApplicable(MobEffectEvent.Applicable e){if(!e.getEntity().level().isClientSide)Probe.event("native-effect-applicable",Map.of("tick",e.getEntity().level().getGameTime(),"target",entity(e.getEntity()),"result",e.getResult().toString(),"effect",ForgeRegistries.MOB_EFFECTS.getKey(e.getEffectInstance().getEffect()).toString()));}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void effectRemove(MobEffectEvent.Remove e){if(!e.getEntity().level().isClientSide)Probe.event("native-effect-remove",Map.of("tick",e.getEntity().level().getGameTime(),"target",entity(e.getEntity()),"effect",ForgeRegistries.MOB_EFFECTS.getKey(e.getEffect()).toString(),"cancelled",e.isCanceled()));}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void attack(AttackEntityEvent e){if(!e.getEntity().level().isClientSide)Probe.event("native-server-attack",Map.of("tick",e.getEntity().level().getGameTime(),"weapon",id(e.getEntity().getMainHandItem()),"target",entity(e.getTarget()),"cancelled",e.isCanceled()));}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void damage(LivingDamageEvent e){if(e.getEntity().level().isClientSide)return;var d=new LinkedHashMap<String,Object>();d.put("tick",e.getEntity().level().getGameTime());d.put("target",entity(e.getEntity()));d.put("amount",e.getAmount());d.put("cancelled",e.isCanceled());d.put("source",e.getSource().getMsgId());d.put("direct",e.getSource().getDirectEntity()==null?null:entity(e.getSource().getDirectEntity()));d.put("owner",e.getSource().getEntity()==null?null:e.getSource().getEntity().getId());d.put("originalWeapon",id(EquipmentFeedback.sourceWeapon(e)));Probe.event("native-server-damage",d);}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void arrow(EntityJoinLevelEvent e){if(!e.getLevel().isClientSide&&e.getEntity() instanceof AbstractArrow a){Probe.event("native-server-arrow",Map.of("tick",e.getLevel().getGameTime(),"arrow",entity(a),"owner",a.getOwner()==null?-1:a.getOwner().getId(),"data",a.getPersistentData().toString()));}}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void impact(ProjectileImpactEvent e){if(!e.getEntity().level().isClientSide)Probe.event("native-projectile-impact",Map.of("tick",e.getEntity().level().getGameTime(),"projectile",entity(e.getEntity()),"hit",e.getRayTraceResult().getType().toString(),"pos",Probe.v(e.getRayTraceResult().getLocation()),"cancelled",e.isCanceled()));}
  @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e){if(e.phase!=TickEvent.Phase.END||Probe.current.isEmpty())return;var s=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();if(s==null)return;var p=s.getPlayerList().getPlayers().get(0);Probe.event("server-tick",Map.of("tick",s.overworld().getGameTime(),"player",entity(p),"using",p.isUsingItem(),"useTicks",p.getTicksUsingItem(),"held",id(p.getMainHandItem()),"targets",targets.stream().map(StatusVisualAcceptance::entity).toList()));}
 }
 @Mod.EventBusSubscriber(modid="dynastystatusqa",value=net.minecraftforge.api.distmarker.Dist.CLIENT) public static final class Client {
  static boolean started,ready,done,triggered,released;
  static int ticks,age,settle,renderFrames,startupFrames;static String last="";static JsonObject active;
  static CompletableFuture<?> task;static int primary=-1;
  static final List<Object> frames=new ArrayList<>();
  static final Map<String,com.mojang.blaze3d.platform.NativeImage> images=new LinkedHashMap<>();
  static Set<Long> captured=new HashSet<>();static long lastFrameNano,worldSerial,consumedSerial=-1;static Map<String,Object> rendered=Map.of();
  static void server(java.util.function.Consumer<ServerPlayer> fn){var m=Minecraft.getInstance();var uid=m.player.getUUID();task=m.getSingleplayerServer().submit(()->fn.accept(m.getSingleplayerServer().getPlayerList().getPlayer(uid)));}
  static void block(ServerLevel l,int x,int y,int z,net.minecraft.world.level.block.state.BlockState b){var p=new BlockPos(x,y,z);l.setBlockAndUpdate(p,b);blocks.add(p);}
  static void fixture(ServerPlayer p,JsonObject c){
   var l=p.serverLevel();for(var t:targets)t.discard();targets.clear();for(var b:blocks)l.setBlockAndUpdate(b,Blocks.AIR.defaultBlockState());blocks.clear();
   p.stopUsingItem();p.clearFire();p.removeAllEffects();p.getInventory().clearContent();for(var slot:EquipmentSlot.values())if(slot.getType()==EquipmentSlot.Type.ARMOR)p.setItemSlot(slot,ItemStack.EMPTY);
   p.setGameMode(GameType.SURVIVAL);p.getFoodData().setFoodLevel(20);p.teleportTo(l,0,-60,0,0,16);p.setDeltaMovement(Vec3.ZERO);
   l.setDayTime(text(c,"light","day").equals("night")?18000:6000);l.setWeatherParameters(10000,0,false,false);
   for(int x=-8;x<=8;x++)for(int z=-8;z<=10;z++){for(int y=-60;y<=-56;y++)l.setBlockAndUpdate(new BlockPos(x,y,z),Blocks.AIR.defaultBlockState());block(l,x,-61,z,Blocks.STONE.defaultBlockState());}
   String set=text(c,"set","");if(!set.isEmpty()){p.setItemSlot(EquipmentSlot.HEAD,item(set+"_helmet"));p.setItemSlot(EquipmentSlot.CHEST,item(set+"_chestplate"));p.setItemSlot(EquipmentSlot.LEGS,item(set+"_leggings"));p.setItemSlot(EquipmentSlot.FEET,item(set+"_boots"));}p.setHealth(p.getMaxHealth());
   LivingEntity t=text(c,"effect","").equals("frost_vein")?new Cow(EntityType.COW,l){@Override protected void registerGoals(){}}:(LivingEntity)ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("dynasty:royal_guard")).create(l);((Mob)t).setNoAi(!text(c,"effect","").equals("frost_vein"));((Mob)t).setPersistenceRequired();t.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);t.setHealth(200);t.setPos(-1.7,-60,1.4);t.addTag("statusqa");l.addFreshEntity(t);targets.add(t);primary=t.getId();
   try{write(text(c,"id","")+"-fixture.json",Map.of("configuration",c,"player",entity(p),"target",entity(t),"trigger","vanilla C2S /effect command invokes actual server effect event and original status/immune dispatch; no synthetic feedback packet"));}catch(Exception ex){throw new RuntimeException(ex);}
  }
  static void command(String command){var m=Minecraft.getInstance();Probe.event("native-c2s-command",Map.of("command",command,"tick",m.level.getGameTime(),"age",age));m.player.connection.sendCommand(command);}
  static void applyStatus(JsonObject c){String effect=text(c,"effect","yin_qi");command("effect give @s dynasty:"+effect+" 6 "+num(c,"amplifier",0));command("effect give @e[tag=statusqa] dynasty:"+effect+" 6 "+num(c,"amplifier",0));}
  static Map<String,Object> state(Minecraft m){var r=new LinkedHashMap<String,Object>();r.put("tick",m.level==null?-1:m.level.getGameTime());r.put("clientTick",ticks);r.put("age",age);r.put("screen",m.screen==null?"none":m.screen.getClass().getName());r.put("cameraType",m.options.getCameraType().toString());r.put("maxFps",m.options.framerateLimit().get());r.put("camera",Probe.v(m.gameRenderer.getMainCamera().getPosition()));r.put("player",m.player==null?null:entity(m.player));r.put("triggered",triggered);r.put("using",m.player!=null&&m.player.isUsingItem());r.put("overlay",m.getOverlay()==null?"none":m.getOverlay().getClass().getName());r.put("useTicks",m.player==null?0:m.player.getTicksUsingItem());r.put("activeVisuals",Probe.activeVisuals);r.put("targets",m.level==null?List.of():targets.stream().map(t->m.level.getEntity(t.getId())).filter(Objects::nonNull).map(StatusVisualAcceptance::entity).toList());return r;}
  @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){if(done||e.phase!=TickEvent.Phase.END)return;ticks++;var m=Minecraft.getInstance();try{
   if(active==null||m.player==null)return;if(task!=null){if(!task.isDone())return;task.join();task=null;settle=0;}
   if(!triggered){if(++settle<30)return;org.lwjgl.glfw.GLFW.glfwFocusWindow(m.getWindow().getWindow());m.setScreen(null);m.mouseHandler.grabMouse();m.options.setCameraType(CameraType.THIRD_PERSON_BACK);m.options.framerateLimit().set(num(active,"fps",60));m.player.setYRot(0);m.player.setXRot(16);triggered=true;age=0;Probe.current=text(active,"id","");applyStatus(active);return;}
   age++;
   if(flag(active,"move")){m.options.keyLeft.setDown(age>=5&&age<13);}
   String phase=text(active,"phase","clear");
   if(phase.equals("swap")){
    boolean yin=text(active,"effect","").equals("yin_qi");String set=yin?"tiangang":"disha";
    if(age==20)command("time set "+(yin?"day":"night"));
    if(age==40){command("item replace entity @s armor.head with minecraft:air");command("effect give @s dynasty:"+text(active,"effect","")+" 6 0");}
    if(age==60)command("item replace entity @s armor.head with dynasty:"+set+"_helmet");
    if(age==80)command("time set "+(yin?"night":"day"));
    if(age==82)command("effect give @s dynasty:"+text(active,"effect","")+" 6 0");
   }else if(age==25&&(phase.equals("fire")||phase.equals("warm")||phase.equals("cold"))){
    server(p->{var l=p.serverLevel();for(var e1:List.of((LivingEntity)p,targets.get(0))){var pos=e1.blockPosition();if(phase.equals("fire")){block(l,pos.getX(),pos.getY(),pos.getZ(),Blocks.FIRE.defaultBlockState());}
     else{for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++)block(l,pos.getX()+dx,pos.getY(),pos.getZ()+dz,Blocks.WATER.defaultBlockState());if(phase.equals("warm"))block(l,pos.getX()+1,pos.getY()-1,pos.getZ(),Blocks.MAGMA_BLOCK.defaultBlockState());}}
     Probe.event("native-environment-fixture",Map.of("phase",phase,"tick",l.getGameTime()));});
   }else if(phase.equals("clear")&&age==40){command("effect clear @s dynasty:"+text(active,"effect","yin_qi"));command("effect clear @e[tag=statusqa] dynasty:"+text(active,"effect","yin_qi"));}
  }catch(Throwable x){failure(x);}}
  @SubscribeEvent(priority=EventPriority.HIGHEST) public static void levelBegin(RenderLevelStageEvent e){if(e.getStage()==RenderLevelStageEvent.Stage.AFTER_SKY&&active!=null)Probe.begin();}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void levelEnd(RenderLevelStageEvent e){if(e.getStage()!=RenderLevelStageEvent.Stage.AFTER_LEVEL||active==null)return;var m=Minecraft.getInstance();rendered=state(m);rendered.put("partialTick",e.getPartialTick());rendered.put("frameSerial",Probe.serial);rendered.put("geometry",Probe.geometry);rendered.put("glState",Probe.renderState);rendered.put("afterimages",Probe.ghosts);rendered.put("nativePixelDelta",Probe.pixels);rendered.put("projection",e.getProjectionMatrix().get(new float[16]));worldSerial=Probe.serial;}
  @SubscribeEvent public static void render(TickEvent.RenderTickEvent e){if(done||e.phase!=TickEvent.Phase.END)return;var m=Minecraft.getInstance();try{
   if(!ready&&++startupFrames%30==0){org.lwjgl.glfw.GLFW.glfwSetWindowTitle(m.getWindow().getWindow(),"COD4 Status Visual QA - "+OUT.getFileName());org.lwjgl.glfw.GLFW.glfwFocusWindow(m.getWindow().getWindow());write("startup-state.json",Map.of("screen",m.screen==null?"none":m.screen.getClass().getName(),"overlay",m.getOverlay()==null?"none":m.getOverlay().getClass().getName(),"frames",startupFrames));try(var pixels=Screenshot.takeScreenshot(m.getMainRenderTarget())){pixels.writeToFile(OUT.resolve("startup.png"));}}
   if(m.getOverlay()!=null)return;if(m.screen instanceof AccessibilityOnboardingScreen)m.setScreen(new TitleScreen());
   if(!started&&m.screen instanceof TitleScreen){started=true;if(!m.gameDirectory.getCanonicalPath().equals(System.getProperty("dynasty.statusqa.instance")))throw new AssertionError("private instance");write("loaded-mods.json",net.minecraftforge.fml.ModList.get().getMods().stream().map(x->Map.of("id",x.getModId(),"version",x.getVersion().toString())).toList());var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);m.createWorldOpenFlows().createFreshLevel("status-visual-"+System.currentTimeMillis(),new LevelSettings("COD4 Native Visual QA",GameType.SURVIVAL,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(93,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;}
   if(m.player==null||m.level==null)return;if(!ready){if(++renderFrames<120)return;ready=true;m.setScreen(null);write("READY.json",state(m));}
   if(active!=null&&triggered&&worldSerial==Probe.serial&&worldSerial!=consumedSerial&&!rendered.isEmpty()&&java.util.Objects.equals(rendered.get("tick"),m.level.getGameTime())){
    consumedSerial=worldSerial;
    var f=new LinkedHashMap<String,Object>(rendered);long now=System.nanoTime();f.put("frameIntervalMs",lastFrameNano==0?0:(now-lastFrameNano)/1e6);lastFrameNano=now;
    boolean effect=age%5==0||age<12||age==19||age==21||age==39||age==41||age==59||age==61||age==79||age==81;long tick=m.level.getGameTime();
    if((effect||age==0||age==num(active,"duration",65)-2)&&images.size()<48&&captured.add(tick)){
     String name=text(active,"id","")+"-f"+Probe.serial+"-t"+tick+".png";images.put(name,Screenshot.takeScreenshot(m.getMainRenderTarget()));f.put("screenshot",name);
    }
    frames.add(f);
    if(age>=num(active,"duration",65)){m.options.keyLeft.setDown(false);m.options.keyUse.setDown(false);m.options.keyUp.setDown(false);m.options.keySprint.setDown(false);String name=text(active,"id","");Probe.current="";write(name+"-frames.json",frames);write(name+"-events.json",Probe.events);for(var im:images.entrySet())try(var p=im.getValue()){p.writeToFile(OUT.resolve(im.getKey()));}images.clear();write(name+"-result.json",Map.of("state",state(m),"frames",frames.size(),"events",Probe.events.size()));active=null;frames.clear();Probe.events.clear();rendered=Map.of();return;}
   }
   if(active!=null)return;Path command=OUT.resolve("command.json");if(!Files.exists(command))return;var c=JsonParser.parseString(Files.readString(command)).getAsJsonObject();String name=c.get("id").getAsString();if(name.equals(last))return;last=name;Files.copy(command,OUT.resolve(name+"-command.json"));
   if(text(c,"op","case").equals("finish")){write("FINISHED.json",state(m));done=true;m.stop();return;}
   active=c;Probe.pixelProbe=flag(c,"pixels");Probe.pixelTicks.clear();Probe.savedPairs.clear();triggered=false;released=false;age=0;settle=0;captured.clear();frames.clear();Probe.events.clear();lastFrameNano=0;m.setScreen(null);m.options.keyUse.setDown(false);m.options.setCameraType(CameraType.FIRST_PERSON);server(p->fixture(p,c));
  }catch(Throwable x){failure(x);}}
  static void failure(Throwable x){x.printStackTrace();try{write(last+"-FAIL.json",Map.of("error",x.toString(),"trace",Arrays.toString(x.getStackTrace())));}catch(Exception ignored){}Probe.current="";active=null;}
 }
}
