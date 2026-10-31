package com.dynasty.sweepqa;
import com.mojang.brigadier.arguments.*;
import com.google.gson.JsonParser;
import net.minecraft.client.*;
import net.minecraft.commands.Commands;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.*;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.Path;
import java.util.*;

/** Explicit command only. No focus/window/screen calls, world creation, auto-connect or shutdown. */
@Mod.EventBusSubscriber(modid="dynastysweepqa",value=Dist.CLIENT)
public final class SweepClient {
 public static final Map<String,com.mojang.blaze3d.platform.NativeImage> images=new LinkedHashMap<>();
 static final List<Object> frames=new ArrayList<>();
 static boolean active;static int ticks;static String name;static CameraType previous;
 static final Set<Long> captured=new HashSet<>();
 @SubscribeEvent public static void commands(RegisterClientCommandsEvent e){
  e.getDispatcher().register(Commands.literal("sweepqa-client").then(Commands.argument("case",StringArgumentType.word()).then(Commands.argument("target",IntegerArgumentType.integer(0)).then(Commands.argument("view",StringArgumentType.word()).executes(c->{start(StringArgumentType.getString(c,"case"),IntegerArgumentType.getInteger(c,"target"),StringArgumentType.getString(c,"view"),true);return 1;})))));
  e.getDispatcher().register(Commands.literal("sweepqa-watch").then(Commands.argument("case",StringArgumentType.word()).then(Commands.argument("view",StringArgumentType.word()).executes(c->{start(StringArgumentType.getString(c,"case"),-1,StringArgumentType.getString(c,"view"),false);return 1;}))));
 }
 static void start(String id,int target,String view,boolean attack){
  var m=Minecraft.getInstance();if(active||m.player==null||m.level==null||m.gameMode==null)throw new IllegalStateException("Client not idle in private world");
  if(!SweepQA.real(m.gameDirectory.toPath()).equals(SweepQA.real(Path.of(Objects.requireNonNull(System.getProperty("dynasty.sweepqa.instance"))))))throw new IllegalStateException("Wrong private instance");
  if(!id.matches("[a-zA-Z0-9_-]{1,70}")||!Set.of("first","third").contains(view))throw new IllegalArgumentException("case/view");
  var t=m.level.getEntity(target);if(attack&&(!(t instanceof LivingEntity)||!t.isAlive()||m.player.distanceTo(t)>3||!net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(m.player.getMainHandItem().getItem()).toString().equals("dynasty:halberd_fangtian")||m.player.getAttackStrengthScale(0)<.99f))throw new IllegalStateException("Target/weapon/range/full native cooldown not ready");
  var fixturePath=SweepQA.OUT.resolve(id+"-fixture.json");
  com.google.gson.JsonObject fixture;try{fixture=JsonParser.parseString(java.nio.file.Files.readString(fixturePath)).getAsJsonObject();}catch(Exception ex){throw new IllegalStateException("Copy exact server fixture into this private client output first",ex);}
  var identity=fixture.getAsJsonObject("identity");var primary=fixture.getAsJsonArray("targets").get(0).getAsJsonObject();var actor=fixture.getAsJsonObject("actor");
  if(!id.equals(fixture.get("case").getAsString())||!id.equals(identity.get("case").getAsString())||!identity.get("artifact").getAsString().equals(Probe.CLIENT.stamp().get("artifact")))throw new IllegalStateException("Fixture case/QA artifact mismatch");
  if(!Probe.SERVER.current().isEmpty()&&(!Probe.SERVER.current().equals(id)||!Probe.SERVER.stamp().get("binding").equals(identity.get("binding").getAsString())))throw new IllegalStateException("Integrated server fixture mismatch");
  if(attack&&(!actor.get("uuid").getAsString().equals(m.player.getUUID().toString())||primary.get("id").getAsInt()!=target||!primary.get("uuid").getAsString().equals(t.getUUID().toString())||!primary.get("dimension").getAsString().equals(m.level.dimension().location().toString())||!actor.get("dimension").getAsString().equals(m.level.dimension().location().toString())))throw new IllegalStateException("Fixture actor/main UUID/id/dimension mismatch");
  if(java.nio.file.Files.exists(SweepQA.OUT.resolve(id+"-client-frames.json")))throw new IllegalStateException("Case capture already exists");
  Probe.CLIENT.begin(id,identity.get("binding").getAsString(),fixture.get("mode").getAsString());
  name=id;previous=m.options.getCameraType();m.options.setCameraType(view.equals("first")?CameraType.FIRST_PERSON:CameraType.THIRD_PERSON_BACK);
  active=true;Probe.renderActive=true;ticks=0;frames.clear();captured.clear();Probe.pixelProbe=true;Probe.savedPairs.clear();Probe.pixelTicks.clear();Probe.seenHooks.clear();Probe.frameHooks.clear();Probe.meshEnd();
  Probe.event("client-capture-start",Map.of("view",view,"observerOnly",!attack,"player",SweepQA.entity(m.player),"cooldown",m.player.getAttackStrengthScale(0),"fixtureSHA256",CaseLog.sha(fixturePath)));
  if(attack){m.gameMode.attack(m.player,t);m.player.swing(InteractionHand.MAIN_HAND);Probe.event("actual-client-gamemode-attack",Map.of("target",SweepQA.entity(t),"player",SweepQA.entity(m.player)));}
 }
 @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){if(active&&e.phase==TickEvent.Phase.END){ticks++;if(Minecraft.getInstance().level==null)finish("disconnect");}}
 @SubscribeEvent(priority=EventPriority.HIGHEST) public static void begin(RenderLevelStageEvent e){if(active&&e.getStage()==RenderLevelStageEvent.Stage.AFTER_SKY)Probe.begin();}
 @SubscribeEvent(priority=EventPriority.LOWEST) public static void frame(RenderLevelStageEvent e){
  if(!active||e.getStage()!=RenderLevelStageEvent.Stage.AFTER_LEVEL)return;
  var m=Minecraft.getInstance();if(m.level==null||m.player==null){finish("disconnect");return;}
  var row=new LinkedHashMap<String,Object>(Probe.CLIENT.stamp());row.put("hooks",Set.copyOf(Probe.frameHooks));row.put("serial",Probe.serial);row.put("tick",m.level.getGameTime());row.put("ageClientTicks",ticks);row.put("partialTick",e.getPartialTick());row.put("view",m.options.getCameraType().toString());row.put("camera",Probe.v(m.gameRenderer.getMainCamera().getPosition()));row.put("projection",e.getProjectionMatrix().get(new float[16]));row.put("geometry",Probe.geometry);row.put("glState",Probe.renderState);row.put("afterimages",Probe.ghosts);row.put("nativePixelDelta",Probe.pixels);
  if((!Probe.geometry.isEmpty()||!Probe.ghosts.isEmpty()||ticks<3)&&captured.size()<16&&captured.add(m.level.getGameTime())){String f=name+"-frame-"+Probe.serial+".png";images.put(f,Screenshot.takeScreenshot(m.getMainRenderTarget()));row.put("screenshot",f);}frames.add(row);
  if(ticks>=40)finish("bounded-40-client-ticks");
 }
 static void finish(String reason){
  active=false;Probe.renderActive=false;Probe.pixelProbe=false;var m=Minecraft.getInstance();m.options.setCameraType(previous);Probe.event("client-capture-end",Map.of("reason",reason,"ticks",ticks));
  try{SweepQA.write(name+"-client-frames.json",frames);SweepQA.write(name+"-client-events.json",Probe.CLIENT.snapshot());for(var entry:images.entrySet())try(var image=entry.getValue()){image.writeToFile(SweepQA.OUT.resolve(entry.getKey()));}}catch(Exception ex){throw new IllegalStateException(ex);}finally{images.clear();Probe.CLIENT.close();}
  // The complete 40-tick client window is now immutable on disk; a new unique case is permitted.
  // Server lifecycle is separate even in an integrated JVM. No server clear is needed to release this client.
 }
}
