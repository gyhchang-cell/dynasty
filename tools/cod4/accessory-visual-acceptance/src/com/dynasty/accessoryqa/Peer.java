package com.dynasty.accessoryqa;
import com.google.gson.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;
import java.util.*;
@Mod.EventBusSubscriber(modid="dynastyaccessoryqa",value=net.minecraftforge.api.distmarker.Dist.CLIENT)
public final class Peer {
 static final boolean ENABLED=Boolean.getBoolean("dynasty.accessoryqa.peer");
 static final Path HOST=Path.of(System.getProperty("dynasty.accessoryqa.hostout","."));
 static final Path OUT=AccessoryVisualAcceptance.OUT;
 static boolean connected,ready,finished;static String current="",last="";static long consumed=-1;
 static Map<String,Object> rendered=Map.of();static final List<Object> frames=new ArrayList<>();static final Set<Long> shots=new HashSet<>();
 static void write(String name,Object value)throws Exception{AccessoryVisualAcceptance.write(name,value);}
 static Map<String,Object> state(){var m=Minecraft.getInstance();var f=new LinkedHashMap<String,Object>();f.put("tick",m.level.getGameTime());f.put("selfId",m.player.getId());f.put("screen",m.screen==null?"none":m.screen.getClass().getName());f.put("players",m.level.players().stream().map(AccessoryVisualAcceptance::entity).toList());f.put("camera",Probe.v(m.gameRenderer.getMainCamera().getPosition()));f.put("cameraType",m.options.getCameraType().toString());return f;}
 @SubscribeEvent(priority=EventPriority.HIGHEST) public static void start(RenderLevelStageEvent e){if(ENABLED&&!current.isEmpty()&&e.getStage()==RenderLevelStageEvent.Stage.AFTER_SKY)Probe.begin();}
 @SubscribeEvent(priority=EventPriority.LOWEST) public static void end(RenderLevelStageEvent e){if(!ENABLED||current.isEmpty()||e.getStage()!=RenderLevelStageEvent.Stage.AFTER_LEVEL)return;rendered=state();rendered.put("frameSerial",Probe.serial);rendered.put("partialTick",e.getPartialTick());rendered.put("geometry",Probe.geometry);rendered.put("nativePixelDelta",Probe.pixels);rendered.put("activeVisuals",Probe.activeVisuals);rendered.put("glState",Probe.renderState);}
 static void flush()throws Exception{
  write(current+"-frames.json",frames);write(current+"-events.json",Probe.events);
  for(var im:AccessoryVisualAcceptance.Client.images.entrySet())try(var pixels=im.getValue()){pixels.writeToFile(OUT.resolve(im.getKey()));}
  AccessoryVisualAcceptance.Client.images.clear();write(current+"-result.json",Map.of("frames",frames.size(),"events",Probe.events.size()));frames.clear();Probe.events.clear();Probe.current="";current="";rendered=Map.of();
 }
 @SubscribeEvent public static void render(TickEvent.RenderTickEvent e){if(!ENABLED||finished||e.phase!=TickEvent.Phase.END)return;var m=Minecraft.getInstance();try{
  if(m.getOverlay()!=null)return;if(m.screen instanceof AccessibilityOnboardingScreen)m.setScreen(new TitleScreen());
  if(!connected&&m.screen instanceof TitleScreen&&Files.exists(HOST.resolve("port.txt"))){connected=true;String address="127.0.0.1:"+Files.readString(HOST.resolve("port.txt")).trim();ConnectScreen.startConnecting(new TitleScreen(),m,ServerAddress.parseString(address),new ServerData("Private accessory QA",address,false),false);return;}
  if(m.player==null||m.level==null)return;
  if(!ready){ready=true;m.options.setCameraType(CameraType.FIRST_PERSON);m.options.framerateLimit().set(30);m.setScreen(null);write("READY.json",state());Files.writeString(HOST.resolve("peer-READY.json"),OUT.toString());}
  if(!current.isEmpty()&&!rendered.isEmpty()&&Probe.serial!=consumed&&Objects.equals(rendered.get("tick"),m.level.getGameTime())){
   consumed=Probe.serial;var f=new LinkedHashMap<String,Object>(rendered);
   if(AccessoryVisualAcceptance.Client.images.size()<64&&shots.add(m.level.getGameTime())&&(!Probe.geometry.isEmpty()||frames.isEmpty())){String name=current+"-f"+Probe.serial+"-t"+m.level.getGameTime()+".png";AccessoryVisualAcceptance.Client.images.put(name,Screenshot.takeScreenshot(m.getMainRenderTarget()));f.put("screenshot",name);}
   frames.add(f);
  }
  if(!current.isEmpty()&&Files.exists(HOST.resolve(current+"-result.json")))flush();
  var command=HOST.resolve("command.json");if(!Files.exists(command))return;var c=JsonParser.parseString(Files.readString(command)).getAsJsonObject();String id=c.get("id").getAsString();if(id.equals(last)||!current.isEmpty())return;last=id;
  if(c.has("op")&&c.get("op").getAsString().equals("finish")){finished=true;write("FINISHED.json",state());m.stop();return;}
  current=id;Probe.current=id;Probe.pixelProbe=true;Probe.pixelTicks.clear();Probe.savedPairs.clear();Probe.events.clear();frames.clear();shots.clear();rendered=Map.of();write(id+"-command.json",c);Files.writeString(HOST.resolve("peer-"+id+"-READY.json"),"ready");
 }catch(Throwable x){x.printStackTrace();try{write("peer-FAIL.json",Map.of("error",x.toString(),"trace",Arrays.toString(x.getStackTrace())));}catch(Exception ignored){}}}
}
