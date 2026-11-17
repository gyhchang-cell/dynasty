package com.dynasty.accessoryqa;
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

@Mod("dynastyaccessoryqa")
public final class AccessoryVisualAcceptance {
 static final Path OUT=Path.of(System.getProperty("dynasty.accessoryqa.output"));
 static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
 static void write(String n,Object o)throws Exception{Files.writeString(OUT.resolve(n),JSON.toJson(o));}
 static String id(ItemStack s){return ForgeRegistries.ITEMS.getKey(s.getItem()).toString();}
 static ItemStack item(String s){return new ItemStack(Objects.requireNonNull(ForgeRegistries.ITEMS.getValue(new ResourceLocation(s.contains(":")?s:"dynasty:"+s))));}
 static String text(JsonObject c,String k,String fallback){return c.has(k)?c.get(k).getAsString():fallback;}
 static int num(JsonObject c,String k,int fallback){return c.has(k)?c.get(k).getAsInt():fallback;}
 static boolean flag(JsonObject c,String k){return c.has(k)&&c.get(k).getAsBoolean();}
 static final List<LivingEntity> targets=new ArrayList<>();
 static void equip(ServerPlayer p,String slot,ItemStack stack){
 top.theillusivec4.curios.api.CuriosApi.getCuriosInventory(p).resolve().orElseThrow().getStacksHandler(slot).orElseThrow().getStacks().setStackInSlot(0,stack);Probe.event("native-curios-fixture",Map.of("slot",slot,"stack",id(stack),"owner",p.getId()));
 }
 static final List<BlockPos> blocks=new ArrayList<>();
 static Object entity(Entity e){var d=new LinkedHashMap<String,Object>();d.put("id",e.getId());d.put("uuid",e.getUUID().toString());d.put("type",ForgeRegistries.ENTITY_TYPES.getKey(e.getType()).toString());d.put("pos",Probe.v(e.position()));d.put("velocity",Probe.v(e.getDeltaMovement()));d.put("onGround",e.onGround());d.put("alive",e.isAlive());d.put("onFire",e.isOnFire());d.put("inWater",e.isInWater());d.put("underWater",e.isUnderWater());d.put("swimming",e.isSwimming());d.put("sprinting",e.isSprinting());d.put("yaw",e.getYRot());d.put("pitch",e.getXRot());if(e instanceof LivingEntity l){d.put("health",l.getHealth());d.put("maxHealth",l.getMaxHealth());d.put("effects",l.getActiveEffects().stream().map(x->Map.of("effect",ForgeRegistries.MOB_EFFECTS.getKey(x.getEffect()).toString(),"amplifier",x.getAmplifier(),"duration",x.getDuration())).toList());d.put("armor",l.getArmorValue());if(l instanceof ServerPlayer player){d.put("activeAccessories",com.dynasty.DynastyTrinkets.activeIds(player));d.put("cooldowns",com.dynasty.expansion.EquipmentBehaviors.saved(player).toString());d.put("merit",com.dynasty.DynastyStats.getMerit(player));}d.put("speed",l.getAttributeValue(Attributes.MOVEMENT_SPEED));d.put("held",id(l.getMainHandItem()));d.put("armorItems",java.util.stream.StreamSupport.stream(l.getArmorSlots().spliterator(),false).map(AccessoryVisualAcceptance::id).toList());}return d;}
 @Mod.EventBusSubscriber(modid="dynastyaccessoryqa") public static final class Server {
  @SubscribeEvent(priority=EventPriority.HIGHEST) public static void hurtInput(LivingHurtEvent e){if(!e.getEntity().level().isClientSide)Probe.event("native-hurt-input",Map.of("tick",e.getEntity().level().getGameTime(),"target",entity(e.getEntity()),"amount",e.getAmount(),"source",e.getSource().getMsgId(),"fire",e.getSource().is(net.minecraft.tags.DamageTypeTags.IS_FIRE)));}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void heal(LivingHealEvent e){if(!e.getEntity().level().isClientSide)Probe.event("native-heal",Map.of("tick",e.getEntity().level().getGameTime(),"target",entity(e.getEntity()),"amount",e.getAmount(),"cancelled",e.isCanceled()));}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void pickup(net.minecraftforge.event.entity.player.EntityItemPickupEvent e){Probe.event("native-pickup",Map.of("tick",e.getEntity().level().getGameTime(),"owner",e.getEntity().getId(),"item",id(e.getItem().getItem()),"entity",e.getItem().getId()));}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void effectAdded(MobEffectEvent.Added e){if(!e.getEntity().level().isClientSide)Probe.event("native-effect-added",Map.of("tick",e.getEntity().level().getGameTime(),"target",entity(e.getEntity()),"effect",ForgeRegistries.MOB_EFFECTS.getKey(e.getEffectInstance().getEffect()).toString()));}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void effectApplicable(MobEffectEvent.Applicable e){if(!e.getEntity().level().isClientSide)Probe.event("native-effect-applicable",Map.of("tick",e.getEntity().level().getGameTime(),"target",entity(e.getEntity()),"result",e.getResult().toString(),"effect",ForgeRegistries.MOB_EFFECTS.getKey(e.getEffectInstance().getEffect()).toString()));}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void effectRemove(MobEffectEvent.Remove e){if(!e.getEntity().level().isClientSide)Probe.event("native-effect-remove",Map.of("tick",e.getEntity().level().getGameTime(),"target",entity(e.getEntity()),"effect",ForgeRegistries.MOB_EFFECTS.getKey(e.getEffect()).toString(),"cancelled",e.isCanceled()));}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void attack(AttackEntityEvent e){if(!e.getEntity().level().isClientSide)Probe.event("native-server-attack",Map.of("tick",e.getEntity().level().getGameTime(),"weapon",id(e.getEntity().getMainHandItem()),"target",entity(e.getTarget()),"cancelled",e.isCanceled()));}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void damage(LivingDamageEvent e){if(e.getEntity().level().isClientSide)return;var d=new LinkedHashMap<String,Object>();d.put("tick",e.getEntity().level().getGameTime());d.put("target",entity(e.getEntity()));d.put("amount",e.getAmount());d.put("cancelled",e.isCanceled());d.put("source",e.getSource().getMsgId());d.put("direct",e.getSource().getDirectEntity()==null?null:entity(e.getSource().getDirectEntity()));d.put("owner",e.getSource().getEntity()==null?null:e.getSource().getEntity().getId());d.put("originalWeapon",id(EquipmentFeedback.sourceWeapon(e)));Probe.event("native-server-damage",d);}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void arrow(EntityJoinLevelEvent e){if(!e.getLevel().isClientSide&&e.getEntity() instanceof AbstractArrow a){Probe.event("native-server-arrow",Map.of("tick",e.getLevel().getGameTime(),"arrow",entity(a),"owner",a.getOwner()==null?-1:a.getOwner().getId(),"data",a.getPersistentData().toString()));}}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void impact(ProjectileImpactEvent e){if(!e.getEntity().level().isClientSide)Probe.event("native-projectile-impact",Map.of("tick",e.getEntity().level().getGameTime(),"projectile",entity(e.getEntity()),"hit",e.getRayTraceResult().getType().toString(),"pos",Probe.v(e.getRayTraceResult().getLocation()),"cancelled",e.isCanceled()));}
  @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e){if(e.phase!=TickEvent.Phase.END||Probe.current.isEmpty())return;var s=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();if(s==null)return;var p=s.getPlayerList().getPlayers().get(0);Probe.event("server-tick",Map.of("tick",s.overworld().getGameTime(),"player",entity(p),"using",p.isUsingItem(),"useTicks",p.getTicksUsingItem(),"held",id(p.getMainHandItem()),"targets",targets.stream().map(AccessoryVisualAcceptance::entity).toList()));}
 }
 @Mod.EventBusSubscriber(modid="dynastyaccessoryqa",value=net.minecraftforge.api.distmarker.Dist.CLIENT) public static final class Client {
  static boolean started,ready,done,triggered,released,listening;
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
   for(String slot:List.of("necklace","charm","head","belt"))equip(p,slot,ItemStack.EMPTY);
   p.getAttribute(Attributes.MAX_HEALTH).setBaseValue(5000);p.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);p.setHealth(p.getMaxHealth());p.setGameMode(GameType.SURVIVAL);p.getFoodData().setFoodLevel(17);p.teleportTo(l,0,-60,0,0,12);p.setDeltaMovement(Vec3.ZERO);
   l.setDayTime(6000);l.setWeatherParameters(10000,0,false,false);
   for(int x=-8;x<=8;x++)for(int z=-8;z<=10;z++){for(int y=-60;y<=-56;y++)l.setBlockAndUpdate(new BlockPos(x,y,z),Blocks.AIR.defaultBlockState());block(l,x,-61,z,Blocks.STONE.defaultBlockState());}
   for(var peer:p.server.getPlayerList().getPlayers())if(!peer.getUUID().equals(p.getUUID())){boolean front=text(c,"camera","").endsWith("FRONT");peer.teleportTo(l,2.2,-60,front?4:-4,(float)Math.toDegrees(Math.atan2(2.2,front?-4:4)),8);peer.setGameMode(GameType.SURVIVAL);peer.getInventory().clearContent();peer.setHealth(peer.getMaxHealth());}
   String id=text(c,"item","");LivingEntity t;
   if(id.equals("dragon_scale_charm"))t=(LivingEntity)ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("dynasty:dragon_king")).create(l);
   else t=new net.minecraft.world.entity.monster.Zombie(l);
   ((Mob)t).setNoAi(true);((Mob)t).setPersistenceRequired();t.getAttribute(Attributes.MAX_HEALTH).setBaseValue(100000);t.setHealth(t.getMaxHealth());t.setPos(-1.7,-60,.8);t.setItemSlot(EquipmentSlot.HEAD,new ItemStack(Items.IRON_HELMET));if(t.getAttribute(Attributes.ATTACK_DAMAGE)!=null)t.getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(2);l.addFreshEntity(t);targets.add(t);primary=t.getId();
   try{write(text(c,"id","")+"-fixture.json",Map.of("configuration",c,"player",entity(p),"target",entity(t),"boundary","actual Curios slot fixture; native tick/pickup/fire/mob attack/C2S primary attack trigger; no fake accessory feedback"));}catch(Exception ex){throw new RuntimeException(ex);}
  }
  static Map<String,Object> state(Minecraft m){var r=new LinkedHashMap<String,Object>();r.put("tick",m.level==null?-1:m.level.getGameTime());r.put("clientTick",ticks);r.put("age",age);r.put("screen",m.screen==null?"none":m.screen.getClass().getName());r.put("cameraType",m.options.getCameraType().toString());r.put("maxFps",m.options.framerateLimit().get());r.put("camera",Probe.v(m.gameRenderer.getMainCamera().getPosition()));r.put("player",m.player==null?null:entity(m.player));r.put("triggered",triggered);r.put("using",m.player!=null&&m.player.isUsingItem());r.put("overlay",m.getOverlay()==null?"none":m.getOverlay().getClass().getName());r.put("useTicks",m.player==null?0:m.player.getTicksUsingItem());r.put("activeVisuals",Probe.activeVisuals);r.put("targets",m.level==null?List.of():targets.stream().map(t->m.level.getEntity(t.getId())).filter(Objects::nonNull).map(AccessoryVisualAcceptance::entity).toList());return r;}
  @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){if(done||Boolean.getBoolean("dynasty.accessoryqa.peer")||e.phase!=TickEvent.Phase.END)return;ticks++;var m=Minecraft.getInstance();try{
   if(active==null||m.player==null)return;if(task!=null){if(!task.isDone())return;task.join();task=null;settle=0;}
   if(!triggered){if(++settle<40||!Files.exists(OUT.resolve("peer-"+text(active,"id","")+"-READY.json")))return;org.lwjgl.glfw.GLFW.glfwFocusWindow(m.getWindow().getWindow());m.setScreen(null);m.mouseHandler.grabMouse();m.options.setCameraType(CameraType.valueOf(text(active,"camera","THIRD_PERSON_BACK")));m.options.framerateLimit().set(num(active,"fps",30));m.player.setYRot(0);m.player.setXRot(12);triggered=true;age=0;Probe.current=text(active,"id","");server(p->{equip(p,text(active,"slot","charm"),item(text(active,"item","jade_cicada")));if(text(active,"item","").equals("jade_cicada"))p.setHealth(p.getMaxHealth()*.2F);});return;}
   age++;String item=text(active,"item","");
   if(age==10){
    if(item.equals("jade_pendant"))server(p->{p.setHealth(p.getMaxHealth()*.25F);boolean hit=((Mob)targets.get(0)).doHurtTarget(p);Probe.event("native-mob-attack",Map.of("accepted",hit,"owner",p.getId(),"actor",targets.get(0).getId(),"healthAfter",p.getHealth()));});
    if(item.equals("gold_seal_charm"))server(p->{var drop=new net.minecraft.world.entity.item.ItemEntity(p.level(),p.getX(),p.getY(),p.getZ(),item("jade"));drop.setNoPickUpDelay();p.level().addFreshEntity(drop);Probe.event("native-item-spawn",Map.of("id",drop.getId(),"item","dynasty:jade"));});
    if(item.equals("phoenix_feather_charm"))server(p->block(p.serverLevel(),0,-60,0,Blocks.FIRE.defaultBlockState()));
    if(item.equals("dragon_scale_charm")){var t=m.level.getEntity(primary);m.gameMode.attack(m.player,t);m.player.swing(InteractionHand.MAIN_HAND);Probe.event("native-c2s-attack",Map.of("target",entity(t),"distance",m.player.distanceTo(t)));}
   }
   if(item.equals("fox_tail_charm")&&age%22==10&&age<1100)server(p->{boolean hit=((Mob)targets.get(0)).doHurtTarget(p);Probe.event("native-mob-attack",Map.of("accepted",hit,"owner",p.getId(),"actor",targets.get(0).getId(),"healthAfter",p.getHealth()));});
   if(age==20&&(item.equals("jade_bi_disc")||item.equals("moon_pendant"))){m.player.connection.sendCommand("time set night");Probe.event("native-c2s-time",Map.of("age",age,"time","night"));}
   if(age==6&&item.equals("jade_cicada"))m.player.setYRot(25);
   if(age==45&&(item.equals("qilin_horn_charm")||item.equals("jade_bi_disc")||item.equals("moon_pendant")))m.options.setCameraType(m.options.getCameraType()==CameraType.THIRD_PERSON_FRONT?CameraType.THIRD_PERSON_BACK:CameraType.THIRD_PERSON_FRONT);
   if(age==90&&!item.equals("fox_tail_charm"))server(p->equip(p,text(active,"slot","charm"),ItemStack.EMPTY));
  }catch(Throwable x){failure(x);}}
  @SubscribeEvent(priority=EventPriority.HIGHEST) public static void levelBegin(RenderLevelStageEvent e){if(e.getStage()==RenderLevelStageEvent.Stage.AFTER_SKY&&active!=null)Probe.begin();}
  @SubscribeEvent(priority=EventPriority.LOWEST) public static void levelEnd(RenderLevelStageEvent e){if(e.getStage()!=RenderLevelStageEvent.Stage.AFTER_LEVEL||active==null)return;var m=Minecraft.getInstance();rendered=state(m);rendered.put("partialTick",e.getPartialTick());rendered.put("frameSerial",Probe.serial);rendered.put("geometry",Probe.geometry);rendered.put("glState",Probe.renderState);rendered.put("afterimages",Probe.ghosts);rendered.put("nativePixelDelta",Probe.pixels);rendered.put("projection",e.getProjectionMatrix().get(new float[16]));worldSerial=Probe.serial;}
  @SubscribeEvent public static void render(TickEvent.RenderTickEvent e){if(done||Boolean.getBoolean("dynasty.accessoryqa.peer")||e.phase!=TickEvent.Phase.END)return;var m=Minecraft.getInstance();try{
   if(!ready&&++startupFrames%30==0){org.lwjgl.glfw.GLFW.glfwSetWindowTitle(m.getWindow().getWindow(),"COD4 Accessory Visual QA - "+OUT.getFileName());org.lwjgl.glfw.GLFW.glfwFocusWindow(m.getWindow().getWindow());write("startup-state.json",Map.of("screen",m.screen==null?"none":m.screen.getClass().getName(),"overlay",m.getOverlay()==null?"none":m.getOverlay().getClass().getName(),"frames",startupFrames));try(var pixels=Screenshot.takeScreenshot(m.getMainRenderTarget())){pixels.writeToFile(OUT.resolve("startup.png"));}}
   if(m.getOverlay()!=null)return;if(m.screen instanceof AccessibilityOnboardingScreen)m.setScreen(new TitleScreen());
   if(!started&&m.screen instanceof TitleScreen){started=true;if(!m.gameDirectory.getCanonicalPath().equals(System.getProperty("dynasty.accessoryqa.instance")))throw new AssertionError("private instance");write("loaded-mods.json",net.minecraftforge.fml.ModList.get().getMods().stream().map(x->Map.of("id",x.getModId(),"version",x.getVersion().toString())).toList());var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);m.createWorldOpenFlows().createFreshLevel("accessory-visual-"+System.currentTimeMillis(),new LevelSettings("COD4 Native Visual QA",GameType.SURVIVAL,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(93,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;}
   if(m.player==null||m.level==null)return;if(!listening){listening=true;var server=m.getSingleplayerServer();server.setUsesAuthentication(false);int port;try(var socket=new java.net.ServerSocket(0)){port=socket.getLocalPort();}if(!server.publishServer(GameType.SURVIVAL,true,port))throw new AssertionError("QA LAN failed");Files.writeString(OUT.resolve("port.txt"),Integer.toString(port));}if(!ready){if(++renderFrames<120)return;ready=true;m.setScreen(null);write("READY.json",state(m));}
   if(active!=null&&triggered&&worldSerial==Probe.serial&&worldSerial!=consumedSerial&&!rendered.isEmpty()&&java.util.Objects.equals(rendered.get("tick"),m.level.getGameTime())){
    consumedSerial=worldSerial;
    var f=new LinkedHashMap<String,Object>(rendered);long now=System.nanoTime();f.put("frameIntervalMs",lastFrameNano==0?0:(now-lastFrameNano)/1e6);lastFrameNano=now;
    boolean effect=!Probe.geometry.isEmpty()||age%25==0;long tick=m.level.getGameTime();
    if((effect||age==0||age==num(active,"duration",65)-2)&&images.size()<64&&captured.add(tick)){
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
