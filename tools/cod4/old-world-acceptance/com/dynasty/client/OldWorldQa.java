package com.dynasty.client;
import com.google.gson.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.*;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraft.nbt.CompoundTag;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class OldWorldQa {
 static final Path OUT=Path.of(System.getProperty("dynasty.oldWorldQa.output"));
 static boolean started,done;static int deathPhase;static boolean keepInventoryBefore;static int ticks,worldTicks;static CompletableFuture<JsonObject> receipt;
 static final long DEADLINE=System.nanoTime()+240_000_000_000L;
 @SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST)
 public static void actualClone(net.minecraftforge.event.entity.player.PlayerEvent.Clone e){
  if(!Boolean.getBoolean("dynasty.oldWorldQa.death")||!e.isWasDeath())return;
  try{
   Files.createDirectories(OUT);var row=new JsonObject();
   row.addProperty("wasDeath",true);row.addProperty("oldEntityId",e.getOriginal().getId());row.addProperty("newEntityId",e.getEntity().getId());
   row.addProperty("original",e.getOriginal().getPersistentData().toString());row.addProperty("cloned",e.getEntity().getPersistentData().toString());
   Files.writeString(OUT.resolve("actual-native-clone.json"),G.toJson(row));
  }catch(Exception ex){throw new IllegalStateException(ex);}
 }
 static final Gson G=new GsonBuilder().setPrettyPrinting().create();
 @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
  if(!Boolean.getBoolean("dynasty.oldWorldQa")||done||e.phase!=TickEvent.Phase.END)return;
  var mc=Minecraft.getInstance();
  try{
   if(System.nanoTime()>DEADLINE)throw new AssertionError("Old-world entry timed out; screen="+mc.screen);
   if(!started&&(mc.screen instanceof TitleScreen||mc.screen instanceof AccessibilityOnboardingScreen)){
    if(!mc.gameDirectory.getCanonicalPath().contains("/build/cod4-old-world-20261023/"))throw new AssertionError("Private clone required");
    Files.createDirectories(OUT);started=true;mc.options.pauseOnLostFocus=false;
    mc.createWorldOpenFlows().loadLevel(new TitleScreen(),"legacy-copy");return;
   }
   if(!started)return;
   if(mc.screen instanceof BackupConfirmScreen screen){
    for(var child:screen.children())if(child instanceof Button b&&b.getMessage().getString().equals(Component.translatable("selectWorld.backupJoinSkipButton").getString())){b.onPress();return;}
   }
   if(mc.screen instanceof ConfirmScreen screen&&(screen.getTitle().getString().equals(Component.translatable("selectWorld.warning.experimental.title").getString())||screen.getTitle().getString().equals(Component.translatable("selectWorld.backupQuestion.experimental").getString()))){
    for(var child:screen.children())if(child instanceof Button b&&(b.getMessage().getString().equals(CommonComponents.GUI_PROCEED.getString())||b.getMessage().getString().equals(CommonComponents.GUI_YES.getString()))){b.onPress();return;}
   }
   if(deathPhase==1){
    if(mc.screen instanceof DeathScreen screen){
     for(var child:screen.children())if(child instanceof Button b&&b.active&&b.getMessage().getString().equals(Component.translatable("deathScreen.respawn").getString())){
      try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){image.writeToFile(OUT.resolve("native-death.png"));}
      Files.writeString(OUT.resolve("native-respawn-input.txt"),"Native DeathScreen Respawn button onPress sends actual client respawn C2S; no manual Clone callback.\n");
      b.onPress();deathPhase=2;worldTicks=0;receipt=null;return;
     }
    }return;
   }
   if(mc.level==null||mc.player==null){
    if(++ticks%40==0)Files.writeString(OUT.resolve("loading.txt"),String.valueOf(mc.screen));return;
   }
   if(mc.screen instanceof PauseScreen)mc.setScreen(null);
   if(mc.screen!=null||++worldTicks<240)return;
   if(receipt==null){receipt=mc.getSingleplayerServer().submit(()->{
    var player=mc.getSingleplayerServer().getPlayerList().getPlayer(mc.player.getUUID());
    if(player==null)throw new AssertionError("Actual connected owner missing");
    var obj=new JsonObject();obj.addProperty("uuid",player.getUUID().toString());obj.addProperty("gameTime",player.level().getGameTime());obj.addProperty("nativeConnection",player.connection!=null);
    var items=new JsonArray();for(var stack:player.getInventory().items)if(!stack.isEmpty()){
     var row=new JsonObject();row.addProperty("id",ForgeRegistries.ITEMS.getKey(stack.getItem()).toString());row.addProperty("count",stack.getCount());row.addProperty("nbt",stack.save(new CompoundTag()).toString());items.add(row);
    }obj.add("inventory",items);obj.addProperty("forgeData",player.getPersistentData().toString());
    obj.addProperty("fullPlayerNbt",player.saveWithoutId(new CompoundTag()).toString());
    return obj;
   });return;}
   if(!receipt.isDone())return;
   var result=receipt.join();
   if(Boolean.getBoolean("dynasty.oldWorldQa.death")&&deathPhase==0){
    Files.writeString(OUT.resolve("before-death.json"),G.toJson(result));
    mc.getSingleplayerServer().submit(()->{
     var server=mc.getSingleplayerServer();var player=server.getPlayerList().getPlayer(mc.player.getUUID());
     keepInventoryBefore=server.getGameRules().getBoolean(net.minecraft.world.level.GameRules.RULE_KEEPINVENTORY);
     server.getGameRules().getRule(net.minecraft.world.level.GameRules.RULE_KEEPINVENTORY).set(true,server);
     player.kill();
    });deathPhase=1;return;
   }
   if(deathPhase==2){
    if(Boolean.getBoolean("dynasty.oldWorldQa.expectProgressFix")){
     var pre=com.google.gson.JsonParser.parseString(Files.readString(OUT.resolve("before-death.json"))).getAsJsonObject();
     var before=net.minecraft.nbt.TagParser.parseTag(pre.get("forgeData").getAsString());
     var after=net.minecraft.nbt.TagParser.parseTag(result.get("forgeData").getAsString());
     for(String key:new String[]{"dq_p_18","dynasty_merit","dynasty_rank","dynasty_loyalty","dynasty_manual_given"})
      if(before.contains(key)&&!java.util.Objects.equals(before.get(key),after.get(key)))throw new AssertionError("Permanent progress changed across real C2S respawn: "+key+" before="+before.get(key)+" after="+after.get(key));
     var observed=com.google.gson.JsonParser.parseString(Files.readString(OUT.resolve("actual-native-clone.json"))).getAsJsonObject();
     var clone=net.minecraft.nbt.TagParser.parseTag(observed.get("cloned").getAsString());
     for(String transientKey:new String[]{"cod4Still","cod4ContinuousSteps","cod3_was_low","cod3_visual_set"})
      if(clone.contains(transientKey))throw new AssertionError("Transient field copied into actual native Clone: "+transientKey);
     Files.writeString(OUT.resolve("PROGRESS-FIX-PASS.txt"),"Five pre-existing permanent fields survive native death/real C2S respawn; sampled transient movement/visual fields absent at actual Clone. More systems require separate evidence.\n");
    }
    mc.getSingleplayerServer().submit(()->{var server=mc.getSingleplayerServer();server.getGameRules().getRule(net.minecraft.world.level.GameRules.RULE_KEEPINVENTORY).set(keepInventoryBefore,server);}).join();
    Files.writeString(OUT.resolve("death-fixture.txt"),"Only private copy keepInventory temporarily enabled before native server kill; restored after real client respawn. No progress/items/effects granted by QA.\n");
   }
   Files.writeString(OUT.resolve("native-owner.json"),G.toJson(result));
   try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){image.writeToFile(OUT.resolve("native-world.png"));}
   Files.writeString(OUT.resolve("ENTRY.txt"),"Actual connected owner in cloned pre-existing world; no items/effects/tasks granted by QA. Native process shutdown follows. Not yet an inventory-preservation assertion.\n");done=true;mc.stop();
  }catch(Throwable ex){done=true;ex.printStackTrace();try{Files.createDirectories(OUT);Files.writeString(OUT.resolve("FAIL.txt"),ex.toString());}catch(Exception ignored){}mc.stop();}
 }
}
