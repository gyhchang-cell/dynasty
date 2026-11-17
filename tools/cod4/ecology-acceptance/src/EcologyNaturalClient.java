package com.dynasty.expansion;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraft.world.InteractionHand;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;
import java.util.UUID;
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class EcologyNaturalClient {
 private static boolean started;private static int ticks;
 @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
  if(!Boolean.getBoolean("ecology.client")||e.phase!=TickEvent.Phase.END)return;
  var mc=Minecraft.getInstance();var out=Path.of(System.getProperty("ecology.liveOutput"));
  try{
   if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
   if(!started&&mc.screen instanceof TitleScreen&&Files.exists(out.resolve("listening.txt"))){
    if(!mc.gameDirectory.getCanonicalPath().contains("/tools/cod4/ecology-acceptance/.work/client-build/client-live-run1"))throw new IllegalStateException("Isolated client required");
    started=true;mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(3);mc.options.simulationDistance().set(3);
    var address="127.0.0.1:25587";ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString(address),new ServerData("Isolated ecology QA",address,false),false);return;
   }
   if(started&&mc.screen instanceof DisconnectedScreen&&++ticks%200==0&&!Files.exists(out.resolve("stop-client.txt"))){var address="127.0.0.1:25587";ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString(address),new ServerData("Isolated ecology QA",address,false),false);return;}
   if(mc.player==null||mc.level==null)return;
   if(mc.screen instanceof PauseScreen)mc.setScreen(null);
   if(++ticks%20==0)Files.writeString(out.resolve("client-status.txt"),"connected UUID="+mc.player.getUUID()+" tick="+mc.level.getGameTime()+" pos="+mc.player.position()+"\n");
   if(Files.exists(out.resolve("stop-client.txt"))){mc.stop();return;}
   if(ticks%20==0&&mc.player.getInventory().items.stream().filter(net.minecraft.world.item.ItemStack::isEmpty).count()<8){
    var junk=java.util.Set.of("minecraft:bone","minecraft:gunpowder","minecraft:arrow","minecraft:rotten_flesh","minecraft:string","minecraft:spider_eye","minecraft:feather","minecraft:kelp","minecraft:potato","minecraft:bow");
    for(int slot=9;slot<=44;slot++){var stack=mc.player.inventoryMenu.getSlot(slot).getItem();if(junk.contains(net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(stack.getItem()).toString())){
     Files.writeString(out.resolve("client-junk-throws.jsonl"),"{\"tick\":"+mc.level.getGameTime()+",\"slot\":"+slot+",\"item\":\""+net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(stack.getItem())+"\",\"count\":"+stack.getCount()+",\"method\":\"native ClickType.THROW to QA world, not deletion\"}\n",StandardOpenOption.CREATE,StandardOpenOption.APPEND);
     mc.gameMode.handleInventoryMouseClick(mc.player.inventoryMenu.containerId,slot,1,net.minecraft.world.inventory.ClickType.THROW,mc.player);break;
    }}
   }
   if(ticks%14!=0||!Files.exists(out.resolve("attack-target.txt")))return;
   var id=UUID.fromString(Files.readString(out.resolve("attack-target.txt")).trim());
   for(var entity:mc.level.entitiesForRendering())if(entity.getUUID().equals(id)&&entity.isAlive()&&mc.player.distanceToSqr(entity)<16){
    var delta=entity.getEyePosition().subtract(mc.player.getEyePosition());mc.player.setYRot((float)(Math.atan2(delta.z,delta.x)*180/Math.PI)-90);mc.player.setXRot((float)(-Math.atan2(delta.y,Math.sqrt(delta.x*delta.x+delta.z*delta.z))*180/Math.PI));
    mc.gameMode.attack(mc.player,entity);mc.player.swing(InteractionHand.MAIN_HAND);Files.writeString(out.resolve("client-attacks.jsonl"),"{\"target\":\""+id+"\",\"client_tick\":"+mc.level.getGameTime()+",\"target_health\":"+(entity instanceof net.minecraft.world.entity.LivingEntity living?living.getHealth():-1)+",\"distance_squared\":"+mc.player.distanceToSqr(entity)+"}\n",StandardOpenOption.CREATE,StandardOpenOption.APPEND);break;
   }
  }catch(Throwable t){t.printStackTrace();try{Files.writeString(out.resolve("client-error.txt"),t.toString());}catch(Exception ignored){}mc.stop();}
 }
}
