package com.dynasty.armorqa;

import com.dynasty.expansion.EquipmentBehaviors;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.DeathScreen;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.inventory.ClickType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.core.BlockPos;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import java.util.*;
import static com.dynasty.armorqa.ArmorNetworkQa.*;

/** Native two-client death/respawn: fixture gear, real C2S inventory and respawn packets. */
public final class DeathQa {
 static int stage, ticks, localStage=-1, clicks, inputAge;static boolean respawnSent;
 static final List<Map<String,Object>> trace=new ArrayList<>();
 static final Map<UUID,Map<String,Long>> old=new LinkedHashMap<>();
 static boolean enabled(){return "death".equals(System.getProperty("dynasty.armorqa.suite"));}
 static void record(String what)throws Exception{trace.add(obj("event",what,"tick",server.overworld().getGameTime(),"players",players(server).stream().map(ArmorNetworkQa::snap).toList()));write("death-trace-live.json",trace);server.getPlayerList().saveAll();}
 static void supply(ServerPlayer p,String set){String[] suffix={"helmet","chestplate","leggings","boots"};for(int i=0;i<4;i++)p.getInventory().setItem(9+i,item(set+"_"+suffix[i]));p.inventoryMenu.broadcastChanges();}
 static void stage(int n)throws Exception{stage=n;ticks=0;write("death-command.json",Map.of("stage",n));}
 static void client(Minecraft m)throws Exception{
  if(!has("death-command.json"))return;
  int n=com.google.gson.JsonParser.parseString(java.nio.file.Files.readString(OUT.resolve("death-command.json"))).getAsJsonObject().get("stage").getAsInt();
  if(n!=localStage){localStage=n;clicks=0;inputAge=0;respawnSent=false;if(n==1||n==3||n==6)m.setScreen(new InventoryScreen(m.player));}
  inputAge++;
  if((n==1||n==6)&&inputAge%4==0){if(clicks<4){m.gameMode.handleInventoryMouseClick(m.player.inventoryMenu.containerId,9+clicks,0,ClickType.QUICK_MOVE,m.player);clicks++;}else{m.setScreen(null);mark(ROLE+"-death-equipped-"+n);}}
  if(n==3&&inputAge%4==0){if(clicks<4){m.gameMode.handleInventoryMouseClick(m.player.inventoryMenu.containerId,5+clicks,0,ClickType.QUICK_MOVE,m.player);clicks++;}else{m.setScreen(null);mark(ROLE+"-death-unworn");}}
  if((n==4||n==7)&&m.screen instanceof DeathScreen&&!respawnSent){write(ROLE+"-native-death-screen.json",Map.of("screen",m.screen.getClass().getName(),"playerDead",!m.player.isAlive()));respawnSent=true;m.player.respawn();mark(ROLE+"-native-respawn-C2S");}
  if(n==7&&m.player.isAlive()&&m.screen==null&&!has(ROLE+"-death-capture.json")&&draw){write(ROLE+"-death-capture.json",obj("captureEvent","AFTER_LEVEL real rendered world","own",snap(m.player),"trackedPlayers",m.level.players().stream().map(ArmorNetworkQa::snap).toList()));try(var im=net.minecraft.client.Screenshot.takeScreenshot(m.getMainRenderTarget())){im.writeToFile(OUT.resolve(ROLE+"-death-capture.png"));}}
 }
 @SubscribeEvent(priority=EventPriority.LOWEST) public static void clone(PlayerEvent.Clone e){if(!enabled()||e.getEntity().level().isClientSide)return;try{trace.add(obj("event","actual Forge PlayerEvent.Clone","wasDeath",e.isWasDeath(),"originalRawForgeData",e.getOriginal().getPersistentData().toString(),"newRawForgeData",e.getEntity().getPersistentData().toString(),"uuid",e.getEntity().getUUID().toString(),"tick",e.getEntity().level().getGameTime()));write("death-clones.json",trace.stream().filter(x->x.get("event").equals("actual Forge PlayerEvent.Clone")).toList());}catch(Exception x){throw new RuntimeException(x);}}
 @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e){if(!enabled()||!HOST||e.phase!=TickEvent.Phase.END||server==null||players(server).size()!=2||!has("peer-world-ready"))return;
  try{ticks++;var ps=players(server);var h=ps.get(0);var p=ps.get(1);
   if(stage==0){server.overworld().getGameRules().getRule(GameRules.RULE_KEEPINVENTORY).set(true,server);for(var x:ps){reset(x);x.teleportTo(server.overworld(),x==h?4.5:.5,-60,.5,0,0);supply(x,x==h?"zhuque":"draco_king");}
    for(int x=-3;x<=3;x++)for(int z=-3;z<=3;z++)for(int y=-60;y<=-59;y++)change(new BlockPos(x,y,z),Blocks.WATER.defaultBlockState());
    top.theillusivec4.curios.api.CuriosApi.getCuriosInventory(h).orElseThrow(()->new AssertionError("Curios missing")).getStacksHandler("charm").orElseThrow().getStacks().setStackInSlot(0,item("jade_cicada"));record("QA equipment and water supplied; native clock unchanged");stage(1);return;}
   if(stage==1&&has("host-death-equipped-1")&&has("peer-death-equipped-1")&&EquipmentBehaviors.pieces(h,"zhuque")==4&&EquipmentBehaviors.pieces(p,"draco_king")==4){h.setHealth(1);h.invulnerableTime=0;BossCooldownProbe.engage(h);record("native Boss AI engagement, first lethal-save opportunity; no direct hurt or cooldown assignment");stage(10);return;}
   if(stage==10&&EquipmentBehaviors.saved(h).getLong("lastStand")>0){require(h.isAlive(),"First Boss lethal save must preserve life");BossCooldownProbe.freeze();BossCooldownProbe.firstSave(h);record("Native Boss hurt triggered first save; AI frozen after actual hit for deterministic C2S progression");stage(2);return;}
   if(stage==2&&ticks>=40&&EquipmentBehaviors.saved(h).getLong("cicada")>0&&EquipmentBehaviors.saved(p).getLong("guardsUntil")>0){for(var x:ps){var n=EquipmentBehaviors.saved(x);old.put(x.getUUID(),Map.of("lastStand",n.getLong("lastStand"),"cicada",n.getLong("cicada"),"guardsUntil",n.getLong("guardsUntil"),"guardGeneration",n.getLong("guardGeneration")));}write("death-before-cooldowns.json",old);record("before native unequip and death; raw save deadlines");stage(3);return;}
   if(stage==3&&has("host-death-unworn")&&has("peer-death-unworn")&&ticks>=35){record("C2S unequipped; transient grants and owner summons revoked before death");stage(4);for(var x:ps){x.invulnerableTime=0;x.hurt(x.damageSources().generic(),1000000);}return;}
   if(stage==4&&has("host-native-respawn-C2S")&&has("peer-native-respawn-C2S")&&ps.stream().allMatch(ServerPlayer::isAlive)&&ticks>=30){record("after actual two clients death-screen respawn C2S and native PlayerList respawn");var c=new ArrayList<Map<String,Object>>();for(var x:ps){var before=old.get(x.getUUID());var now=EquipmentBehaviors.saved(x);for(var k:before.keySet())c.add(Map.of("uuid",x.getUUID().toString(),"key",k,"before",before.get(k),"after",now.getLong(k),"passed",before.get(k)==now.getLong(k)));c.add(Map.of("uuid",x.getUUID().toString(),"key","transient grants not copied","passed",WINDOW_KEYS.stream().noneMatch(k->x.getPersistentData().contains(k))));x.teleportTo(server.overworld(),x==h?4.5:.5,-60,.5,0,0);supply(x,x==h?"zhuque":"draco_king");}write("death-respawn-checks.json",c);stage(6);return;}
   if(stage==6&&has("host-death-equipped-6")&&has("peer-death-equipped-6")&&ticks>=35){h.setHealth(1);h.invulnerableTime=0;BossCooldownProbe.engage(h);stage(11);return;}
   if(stage==11&&!h.isAlive()){BossCooldownProbe.freeze();var check=new ArrayList<Map<String,Object>>();check.add(Map.of("name","lastStand cannot bypass through death before original deadline","passed",!h.isAlive(),"originalDeadline",old.get(h.getUUID()).get("lastStand"),"actualTick",server.overworld().getGameTime()));check.add(Map.of("name","guard lease and generation unchanged after death and C2S re-equip","passed",EquipmentBehaviors.saved(p).getLong("guardsUntil")==old.get(p.getUUID()).get("guardsUntil")&&EquipmentBehaviors.saved(p).getLong("guardGeneration")==old.get(p.getUUID()).get("guardGeneration")));write("death-no-bypass-checks.json",check);record("second actual Boss AI lethal hit before original deadline caused death; no early save proc");stage(7);return;}
   if(stage==7){if(has("host-death-capture.json")&&has("peer-death-capture.json")){boolean pass=BossCooldownProbe.finish();for(var f:List.of("death-respawn-checks.json","death-no-bypass-checks.json"))for(var c:com.google.gson.JsonParser.parseString(java.nio.file.Files.readString(OUT.resolve(f))).getAsJsonArray())pass&=c.getAsJsonObject().get("passed").getAsBoolean();if(pass)mark("server-PASS");mark("server-COMPLETE");stage=8;}}
   if(ticks>700&&stage<8)throw new AssertionError("native death suite stalled stage="+stage);
  }catch(Throwable x){try{record("failure "+x);java.nio.file.Files.writeString(OUT.resolve("fatal.txt"),x.toString());}catch(Exception ignored){}stage=8;}
 }
}
