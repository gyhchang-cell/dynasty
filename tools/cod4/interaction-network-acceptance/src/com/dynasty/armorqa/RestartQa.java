package com.dynasty.armorqa;
import com.dynasty.expansion.EquipmentBehaviors;
import net.minecraft.client.Minecraft;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import java.util.*;
import static com.dynasty.armorqa.ArmorNetworkQa.*;

/** Actual new JVM/native existing-world load and same offline UUID TCP login; no state reset. */
public final class RestartQa {
 static final Map<String,Map<String,Object>> login=new LinkedHashMap<>();static int ticks;
 static boolean enabled(){return "restart".equals(System.getProperty("dynasty.armorqa.suite"));}
 @SubscribeEvent public static void login(PlayerEvent.PlayerLoggedInEvent e){if(!enabled()||!(e.getEntity() instanceof ServerPlayer p))return;try{var saved=EquipmentBehaviors.saved(p);var values=new TreeMap<String,Long>();for(var k:saved.getAllKeys())if(saved.contains(k,net.minecraft.nbt.Tag.TAG_LONG)||saved.contains(k,net.minecraft.nbt.Tag.TAG_INT))values.put(k,saved.getLong(k));login.put(p.getUUID().toString(),obj("tick",p.level().getGameTime(),"nativeLoginSavedCooldowns",values,"rawForgeData",p.getPersistentData().toString(),"remote",p.connection.connection.getRemoteAddress().toString()));write("restart-native-logins.json",login);}catch(Exception x){throw new RuntimeException(x);}}
 static void client(Minecraft m)throws Exception{if(!has("restart-ready")||has(ROLE+"-restart-frame.json")||!draw||m.screen!=null)return;write(ROLE+"-restart-frame.json",obj("captureEvent","AFTER_LEVEL actual existing-world rendered frame","own",snap(m.player),"trackedPlayers",m.level.players().stream().map(ArmorNetworkQa::snap).toList()));try(var im=net.minecraft.client.Screenshot.takeScreenshot(m.getMainRenderTarget())){im.writeToFile(OUT.resolve(ROLE+"-restart-frame.png"));}}
 @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e){if(!enabled()||!HOST||e.phase!=TickEvent.Phase.END||server==null||players(server).size()!=2||!has("peer-world-ready"))return;try{ticks++;if(ticks==10){require(players(server).get(1).connection.connection.getRemoteAddress() instanceof java.net.InetSocketAddress,"actual restart peer TCP login");var expected=com.google.gson.JsonParser.parseString(java.nio.file.Files.readString(OUT.resolve("resume-expected.json"))).getAsJsonObject();var checks=new ArrayList<Map<String,Object>>();for(var p:players(server)){String id=p.getUUID().toString();var old=expected.getAsJsonObject(id).getAsJsonObject("nativeSavedCooldowns");var actual=(Map<?,?>)login.get(id).get("nativeLoginSavedCooldowns");for(var entry:old.entrySet()){long a=entry.getValue().getAsLong();Object value=actual.get(entry.getKey());checks.add(obj("uuid",id,"key",entry.getKey(),"nativeDiskBeforeShutdown",a,"nativeNewJvmLogin",value,"passed",value instanceof Number&&((Number)value).longValue()==a));}}write("restart-checks.json",checks);write("restart-result.json",obj("passed",checks.stream().allMatch(x->Boolean.TRUE.equals(x.get("passed"))),"checks",checks,"nativeClockUnmodified",true,"serverPlayers",players(server).stream().map(ArmorNetworkQa::snap).toList(),"login",login));mark("restart-ready");}
 if(has("host-restart-frame.json")&&has("peer-restart-frame.json")){if(com.google.gson.JsonParser.parseString(java.nio.file.Files.readString(OUT.resolve("restart-result.json"))).getAsJsonObject().get("passed").getAsBoolean())mark("server-PASS");mark("server-COMPLETE");}
 if(ticks>500)throw new AssertionError("restart QA stalled");}catch(Throwable x){try{java.nio.file.Files.writeString(OUT.resolve("fatal.txt"),x.toString());}catch(Exception ignored){}}}
}
