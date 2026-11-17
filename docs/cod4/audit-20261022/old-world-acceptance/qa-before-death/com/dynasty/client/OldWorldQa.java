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
 static boolean started,done;static int ticks,worldTicks;static CompletableFuture<JsonObject> receipt;
 static final long DEADLINE=System.nanoTime()+240_000_000_000L;
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
   var result=receipt.join();Files.writeString(OUT.resolve("native-owner.json"),G.toJson(result));
   try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){image.writeToFile(OUT.resolve("native-world.png"));}
   Files.writeString(OUT.resolve("ENTRY.txt"),"Actual connected owner in cloned pre-existing world; no items/effects/tasks granted by QA. Native process shutdown follows. Not yet an inventory-preservation assertion.\n");done=true;mc.stop();
  }catch(Throwable ex){done=true;ex.printStackTrace();try{Files.createDirectories(OUT);Files.writeString(OUT.resolve("FAIL.txt"),ex.toString());}catch(Exception ignored){}mc.stop();}
 }
}
