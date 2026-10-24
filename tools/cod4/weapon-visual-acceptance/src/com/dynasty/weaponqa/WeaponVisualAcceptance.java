package com.dynasty.weaponqa;
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

@Mod("dynastyweaponqa")
public final class WeaponVisualAcceptance {
 static final Path OUT=Path.of(System.getProperty("dynasty.weaponqa.output"));
 static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
 static void write(String n,Object o)throws Exception{Files.writeString(OUT.resolve(n),JSON.toJson(o));}
 static String id(ItemStack s){return ForgeRegistries.ITEMS.getKey(s.getItem()).toString();}
 static ItemStack item(String s){return new ItemStack(Objects.requireNonNull(ForgeRegistries.ITEMS.getValue(new ResourceLocation(s.contains(":")?s:"dynasty:"+s))));}
 static String text(JsonObject c,String k,String fallback){return c.has(k)?c.get(k).getAsString():fallback;}
 static int num(JsonObject c,String k,int fallback){return c.has(k)?c.get(k).getAsInt():fallback;}
 static boolean flag(JsonObject c,String k){return c.has(k)&&c.get(k).getAsBoolean();}
 static final List<LivingEntity> targets=new ArrayList<>();
 static final List<BlockPos> blocks=new ArrayList<>();
 static Object entity(Entity e){var d=new LinkedHashMap<String,Object>();d.put("id",e.getId());d.put("uuid",e.getUUID().toString());d.put("type",ForgeRegistries.ENTITY_TYPES.getKey(e.getType()).toString());d.put("pos",Probe.v(e.position()));d.put("velocity",Probe.v(e.getDeltaMovement()));d.put("onGround",e.onGround());d.put("alive",e.isAlive());d.put("inWater",e.isInWater());d.put("underWater",e.isUnderWater());d.put("swimming",e.isSwimming());d.put("sprinting",e.isSprinting());d.put("yaw",e.getYRot());d.put("pitch",e.getXRot());if(e instanceof LivingEntity l){d.put("health",l.getHealth());d.put("maxHealth",l.getMaxHealth());d.put("effects",l.getActiveEffects().stream().map(x->Map.of("effect",ForgeRegistries.MOB_EFFECTS.getKey(x.getEffect()).toString(),"amplifier",x.getAmplifier(),"duration",x.getDuration())).toList());d.put("armor",l.getArmorValue());}return d;}
 @Mod.EventBusSubscriber(modid="dynastyweaponqa") public static final class Server {
  @SubscribeEvent(priority=EventPriority.HIGHEST) public static void sweepReceipt(TickEvent.ServerTickEvent e){
   if(e.phase!=TickEvent.Phase.END||Probe.current.isEmpty())return;
   try{var cl=com.dynasty.cod3.FangtianSweep.class;var f=cl.getDeclaredField("PENDING");f.setAccessible(true);var pending=(java.util.List<?>)f.get(null);
    for(Object r:pending){var d=new LinkedHashMap<String,Object>();for(String k:List.of("tick","secondary","primaryDamage","health")){var a=r.getClass().getDeclaredField(k);a.setAccessible(true);d.put(k,a.get(r));}var a=r.getClass().getDeclaredField("main");a.setAccessible(true);var main=(LivingEntity)a.get(r);d.put("currentHealth",main.getHealth());d.put("now",main.level().getGameTime());d.put("targetAlive",main.isAlive());Probe.event("native-sweep-receipt-before-end",d);}
   }catch(Exception ex){Probe.event("probe-error",ex.toString());}
  }
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void attack(AttackEntityEvent e){if(!e.getEntity().level().isClientSide)Probe.event("native-server-attack",Map.of("tick",e.getEntity().level().getGameTime(),"weapon",id(e.getEntity().getMainHandItem()),"target",entity(e.getTarget()),"cancelled",e.isCanceled()));}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void damage(LivingDamageEvent e){if(e.getEntity().level().isClientSide)return;var d=new LinkedHashMap<String,Object>();d.put("tick",e.getEntity().level().getGameTime());d.put("target",entity(e.getEntity()));d.put("amount",e.getAmount());d.put("cancelled",e.isCanceled());d.put("source",e.getSource().getMsgId());d.put("direct",e.getSource().getDirectEntity()==null?null:entity(e.getSource().getDirectEntity()));d.put("owner",e.getSource().getEntity()==null?null:e.getSource().getEntity().getId());d.put("originalWeapon",id(EquipmentFeedback.sourceWeapon(e)));Probe.event("native-server-damage",d);}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void arrow(EntityJoinLevelEvent e){if(!e.getLevel().isClientSide&&e.getEntity() instanceof AbstractArrow a){Probe.event("native-server-arrow",Map.of("tick",e.getLevel().getGameTime(),"arrow",entity(a),"owner",a.getOwner()==null?-1:a.getOwner().getId(),"data",a.getPersistentData().toString()));}}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void impact(ProjectileImpactEvent e){if(!e.getEntity().level().isClientSide)Probe.event("native-projectile-impact",Map.of("tick",e.getEntity().level().getGameTime(),"projectile",entity(e.getEntity()),"hit",e.getRayTraceResult().getType().toString(),"pos",Probe.v(e.getRayTraceResult().getLocation()),"cancelled",e.isCanceled()));}
  @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e){if(e.phase!=TickEvent.Phase.END||Probe.current.isEmpty())return;var s=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();if(s==null)return;var p=s.getPlayerList().getPlayers().get(0);Probe.event("server-tick",Map.of("tick",s.overworld().getGameTime(),"player",entity(p),"using",p.isUsingItem(),"useTicks",p.getTicksUsingItem(),"held",id(p.getMainHandItem()),"targets",targets.stream().map(WeaponVisualAcceptance::entity).toList()));}
 }
 @Mod.EventBusSubscriber(modid="dynastyweaponqa",value=net.minecraftforge.api.distmarker.Dist.CLIENT) public static final class Client {
  static boolean started,ready,done,triggered,released;
  static int ticks,age,settle,renderFrames,startupFrames;static String last="";static JsonObject active;
  static CompletableFuture<?> task;static int primary=-1;
  static final List<Object> frames=new ArrayList<>();
  static final Map<String,com.mojang.blaze3d.platform.NativeImage> images=new LinkedHashMap<>();
  static Set<Long> captured=new HashSet<>();static long lastFrameNano,worldSerial;static Map<String,Object> rendered=Map.of();
  static void server(java.util.function.Consumer<ServerPlayer> fn){var m=Minecraft.getInstance();var uid=m.player.getUUID();task=m.getSingleplayerServer().submit(()->fn.accept(m.getSingleplayerServer().getPlayerList().getPlayer(uid)));}
  static void block(ServerLevel l,int x,int y,int z,net.minecraft.world.level.block.state.BlockState b){var p=new BlockPos(x,y,z);l.setBlockAndUpdate(p,b);blocks.add(p);}
  static void fixture(ServerPlayer p,JsonObject c){
   var l=p.serverLevel();for(var t:targets)t.discard();targets.clear();for(var b:blocks)l.setBlockAndUpdate(b,Blocks.AIR.defaultBlockState());blocks.clear();
   for(var a:l.getEntitiesOfClass(AbstractArrow.class,new AABB(-100,-80,-100,100,100,100)))a.discard();
   p.stopUsingItem();p.removeAllEffects();p.getInventory().clearContent();p.setGameMode(GameType.SURVIVAL);p.getInventory().selected=0;p.getFoodData().setFoodLevel(20);p.setHealth(p.getMaxHealth());
   p.teleportTo(l,0,-60,0,0,8);p.setDeltaMovement(Vec3.ZERO);p.setItemInHand(flag(c,"offhand")?InteractionHand.OFF_HAND:InteractionHand.MAIN_HAND,item(text(c,"item","tie_jian")));p.getCooldowns().removeCooldown(item(text(c,"item","tie_jian")).getItem());p.getInventory().setItem(9,new ItemStack(Items.ARROW,64));
   l.setDayTime(text(c,"light","day").equals("night")?18000:6000);l.setWeatherParameters(10000,0,false,false);
   var ground=switch(text(c,"ground","stone")){case "sand"->Blocks.SAND.defaultBlockState();case "grass"->Blocks.GRASS_BLOCK.defaultBlockState();default->Blocks.STONE.defaultBlockState();};
   for(int x=-8;x<=8;x++)for(int z=-8;z<=30;z++)block(l,x,-61,z,ground);
   String scene=text(c,"scene","open");
   if(scene.equals("water"))for(int x=-5;x<=5;x++)for(int z=-4;z<=12;z++)for(int y=-60;y<=-59;y++)block(l,x,y,z,Blocks.WATER.defaultBlockState());
   if(scene.equals("occlusion"))for(int y=-60;y<=-56;y++)for(int z=1;z<=4;z++)block(l,-2,y,z,Blocks.STONE.defaultBlockState());
   if(scene.equals("glass"))for(int y=-60;y<=-56;y++)for(int z=1;z<=4;z++)block(l,-2,y,z,Blocks.CYAN_STAINED_GLASS.defaultBlockState());
   if(scene.equals("tight-ceiling"))for(int x=-1;x<=1;x++)for(int z=1;z<=4;z++)block(l,x,-59,z,Blocks.STONE_SLAB.defaultBlockState().setValue(net.minecraft.world.level.block.SlabBlock.TYPE,net.minecraft.world.level.block.state.properties.SlabType.TOP));
   if(scene.equals("ceiling"))for(int x=-1;x<=1;x++)for(int z=1;z<=4;z++)block(l,x,-58,z,Blocks.STONE.defaultBlockState());
   int count=num(c,"targets",1);for(int i=0;i<count;i++){
    LivingEntity t;
    String targetType=text(c,"target","minecraft:cow");
    if(targetType.equals("minecraft:cow"))t=flag(c,"mobile")?new Cow(EntityType.COW,l){@Override protected void registerGoals(){}}:new Cow(EntityType.COW,l);
    else t=(LivingEntity)Objects.requireNonNull(ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation(targetType))).create(l);
    if(t instanceof Mob mob){mob.setNoAi(!flag(c,"mobile"));mob.setPersistenceRequired();}t.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000000);t.setHealth(t.getMaxHealth());t.setPos(i==0?0:(i%2==0?1.1:-1.1),-60,num(c,"distance",text(c,"kind","attack").equals("bow")?18:2)+.25+i*.3);t.getPersistentData().putBoolean("weaponQA",true);
    if(flag(c,"armor")){t.setItemSlot(EquipmentSlot.CHEST,new ItemStack(Items.DIAMOND_CHESTPLATE));t.setItemSlot(EquipmentSlot.LEGS,new ItemStack(Items.DIAMOND_LEGGINGS));}
    if(t instanceof net.minecraft.world.entity.boss.enderdragon.EnderDragon dragon){dragon.setNoAi(false);dragon.setPos(0,-53,8);dragon.getPhaseManager().setPhase(net.minecraft.world.entity.boss.enderdragon.phases.EnderDragonPhase.HOVERING);}
    if(flag(c,"noDamage"))t.setInvulnerable(true);l.addFreshEntity(t);targets.add(t);if(i==0)primary=t.getId();
   }
   try{write(text(c,"id","")+"-fixture.json",Map.of("case",c,"player",entity(p),"targets",targets.stream().map(WeaponVisualAcceptance::entity).toList(),"note","QA supplied neutral mobs/items and plain collision planes; native health/damage/velocity unchanged during action"));}catch(Exception ex){throw new RuntimeException(ex);}
  }
  static Map<String,Object> state(Minecraft m){var r=new LinkedHashMap<String,Object>();r.put("tick",m.level==null?-1:m.level.getGameTime());r.put("clientTick",ticks);r.put("age",age);r.put("screen",m.screen==null?"none":m.screen.getClass().getName());r.put("cameraType",m.options.getCameraType().toString());r.put("maxFps",m.options.framerateLimit().get());r.put("camera",Probe.v(m.gameRenderer.getMainCamera().getPosition()));r.put("player",m.player==null?null:entity(m.player));r.put("triggered",triggered);r.put("using",m.player!=null&&m.player.isUsingItem());r.put("useTicks",m.player==null?0:m.player.getTicksUsingItem());r.put("targets",m.level==null?List.of():targets.stream().map(t->m.level.getEntity(t.getId())).filter(Objects::nonNull).map(WeaponVisualAcceptance::entity).toList());return r;}
  @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){if(done||e.phase!=TickEvent.Phase.END)return;ticks++;var m=Minecraft.getInstance();try{
   if(active==null||m.player==null)return;if(task!=null){if(!task.isDone())return;task.join();task=null;settle=0;}
   if(!triggered){if(++settle==15&&text(active,"target","").equals("minecraft:ender_dragon")){var uid=m.player.getUUID();m.getSingleplayerServer().execute(()->{var p=m.getSingleplayerServer().getPlayerList().getPlayer(uid);var d=(net.minecraft.world.entity.boss.enderdragon.EnderDragon)targets.get(0);var h=d.head;p.teleportTo(p.serverLevel(),h.getX(),h.getY()-.5,h.getZ()-2.25,0,8);});}if(settle<24)return;var hand=flag(active,"offhand")?InteractionHand.OFF_HAND:InteractionHand.MAIN_HAND;if(!id(m.player.getItemInHand(hand)).equals("dynasty:"+text(active,"item","tie_jian")))return;
    m.setScreen(null);org.lwjgl.glfw.GLFW.glfwFocusWindow(m.getWindow().getWindow());m.mouseHandler.grabMouse();m.options.setCameraType(CameraType.valueOf(text(active,"camera","FIRST_PERSON")));m.options.framerateLimit().set(num(active,"fps",60));m.player.setYRot(0);m.player.setXRot(num(active,"pitch",text(active,"kind","attack").equals("bow")?-2:8));triggered=true;age=0;Probe.current=text(active,"id","");
    var target=m.level.getEntity(primary);if(target instanceof net.minecraft.world.entity.boss.enderdragon.EnderDragon dragon)target=dragon.head;String kind=text(active,"kind","attack");
    if(kind.equals("attack")){if(target==null)throw new IllegalStateException("Native target untracked");m.gameMode.attack(m.player,target);m.player.swing(InteractionHand.MAIN_HAND);Probe.event("native-c2s-attack",Map.of("target",entity(target),"weapon",id(m.player.getMainHandItem()),"distance",m.player.distanceTo(target)));}
    else {m.options.keyUse.setDown(true);var result=m.gameMode.useItem(m.player,hand);Probe.event("native-c2s-use",Map.of("weapon",id(m.player.getItemInHand(hand)),"hand",hand.toString(),"result",result.toString()));}
    return;
   }
   age++;
   if(flag(active,"move")){m.options.keyUp.setDown(age<30);m.options.keySprint.setDown(age<30);if(age==3)m.player.setYRot(25);}
   if(active.has("viewYaw")&&age==num(active,"viewAt",2))m.player.setYRot(num(active,"viewYaw",20));
   if(flag(active,"removeSpeed")&&age==4){m.player.connection.sendCommand("effect clear @s minecraft:speed");Probe.event("native-c2s-effect-clear",Map.of("effect","minecraft:speed"));}
   if(flag(active,"reload")&&age==3){m.reloadResourcePacks();Probe.event("native-resource-reload",Map.of("age",age));}
   if(!released&&age>=num(active,"hold",24)){int actual=m.player.getTicksUsingItem();m.options.keyUse.setDown(false);if(m.player.isUsingItem())m.gameMode.releaseUsingItem(m.player);released=true;Probe.event("native-c2s-release",Map.of("age",age,"useTicks",actual));}
  }catch(Throwable x){failure(x);}}
  @SubscribeEvent(priority=EventPriority.HIGHEST) public static void levelBegin(RenderLevelStageEvent e){if(e.getStage()==RenderLevelStageEvent.Stage.AFTER_SKY&&active!=null)Probe.begin();}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void levelEnd(RenderLevelStageEvent e){if(e.getStage()!=RenderLevelStageEvent.Stage.AFTER_LEVEL||active==null)return;var m=Minecraft.getInstance();rendered=state(m);rendered.put("partialTick",e.getPartialTick());rendered.put("frameSerial",Probe.serial);rendered.put("geometry",Probe.geometry);rendered.put("glState",Probe.renderState);rendered.put("afterimages",Probe.ghosts);rendered.put("nativePixelDelta",Probe.pixels);rendered.put("projection",e.getProjectionMatrix().get(new float[16]));worldSerial=Probe.serial;}
  @SubscribeEvent public static void render(TickEvent.RenderTickEvent e){if(done||e.phase!=TickEvent.Phase.END)return;var m=Minecraft.getInstance();try{
   if(!ready&&++startupFrames%30==0){org.lwjgl.glfw.GLFW.glfwSetWindowTitle(m.getWindow().getWindow(),"COD4 Weapon Visual QA - "+OUT.getFileName());org.lwjgl.glfw.GLFW.glfwFocusWindow(m.getWindow().getWindow());write("startup-state.json",Map.of("screen",m.screen==null?"none":m.screen.getClass().getName(),"overlay",m.getOverlay()==null?"none":m.getOverlay().getClass().getName(),"frames",startupFrames));try(var pixels=Screenshot.takeScreenshot(m.getMainRenderTarget())){pixels.writeToFile(OUT.resolve("startup.png"));}}
   if(m.getOverlay()!=null)return;if(m.screen instanceof AccessibilityOnboardingScreen)m.setScreen(new TitleScreen());
   if(!started&&m.screen instanceof TitleScreen){started=true;if(!m.gameDirectory.getCanonicalPath().equals(System.getProperty("dynasty.weaponqa.instance")))throw new AssertionError("private instance");write("loaded-mods.json",net.minecraftforge.fml.ModList.get().getMods().stream().map(x->Map.of("id",x.getModId(),"version",x.getVersion().toString())).toList());var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);m.createWorldOpenFlows().createFreshLevel("weapon-visual-"+System.currentTimeMillis(),new LevelSettings("COD4 Native Visual QA",GameType.SURVIVAL,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(93,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;}
   if(m.player==null||m.level==null)return;if(!ready){if(++renderFrames<120)return;ready=true;m.setScreen(null);write("READY.json",state(m));}
   if(active!=null&&triggered&&worldSerial==Probe.serial&&!rendered.isEmpty()){
    var f=new LinkedHashMap<String,Object>(rendered);long now=System.nanoTime();f.put("frameIntervalMs",lastFrameNano==0?0:(now-lastFrameNano)/1e6);lastFrameNano=now;
    boolean effect=!Probe.geometry.isEmpty()||!Probe.ghosts.isEmpty();long tick=m.level.getGameTime();
    if((effect||age==0||age==num(active,"duration",65)-2)&&images.size()<32&&captured.add(tick)){
     String name=text(active,"id","")+"-f"+Probe.serial+"-t"+tick+".png";images.put(name,Screenshot.takeScreenshot(m.getMainRenderTarget()));f.put("screenshot",name);
    }
    frames.add(f);
    if(age>=num(active,"duration",65)){m.options.keyUse.setDown(false);m.options.keyUp.setDown(false);m.options.keySprint.setDown(false);String name=text(active,"id","");Probe.current="";write(name+"-frames.json",frames);write(name+"-events.json",Probe.events);for(var im:images.entrySet())try(var p=im.getValue()){p.writeToFile(OUT.resolve(im.getKey()));}images.clear();write(name+"-result.json",Map.of("state",state(m),"frames",frames.size(),"events",Probe.events.size()));active=null;frames.clear();Probe.events.clear();rendered=Map.of();return;}
   }
   if(active!=null)return;Path command=OUT.resolve("command.json");if(!Files.exists(command))return;var c=JsonParser.parseString(Files.readString(command)).getAsJsonObject();String name=c.get("id").getAsString();if(name.equals(last))return;last=name;Files.copy(command,OUT.resolve(name+"-command.json"));
   if(text(c,"op","case").equals("finish")){write("FINISHED.json",state(m));done=true;m.stop();return;}
   active=c;Probe.pixelProbe=flag(c,"pixels");Probe.pixelTicks.clear();Probe.savedPairs.clear();triggered=false;released=false;age=0;settle=0;captured.clear();frames.clear();Probe.events.clear();lastFrameNano=0;m.setScreen(null);m.options.keyUse.setDown(false);m.options.setCameraType(CameraType.FIRST_PERSON);server(p->fixture(p,c));
  }catch(Throwable x){failure(x);}}
  static void failure(Throwable x){x.printStackTrace();try{write(last+"-FAIL.json",Map.of("error",x.toString(),"trace",Arrays.toString(x.getStackTrace())));}catch(Exception ignored){}Probe.current="";active=null;}
 }
}
