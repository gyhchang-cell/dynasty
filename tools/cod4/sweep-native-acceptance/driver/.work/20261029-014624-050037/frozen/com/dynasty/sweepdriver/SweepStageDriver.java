package com.dynasty.sweepdriver;

import com.dynasty.sweepqa.CaseLog;
import com.dynasty.sweepqa.Probe;
import com.google.gson.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.storage.LevelResource;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ClientChatReceivedEvent;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Single opt-in bridge. No production event/receipt/damage mutation; no process launch or new world. */
@Mod("dynastysweepdriver")
@Mod.EventBusSubscriber(modid="dynastysweepdriver",value=Dist.CLIENT)
public final class SweepStageDriver {
 public SweepStageDriver(){}
 static final boolean ENABLED=Boolean.getBoolean("dynasty.sweepdriver.enabled");
 static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
 static boolean initialized,owned,host,opening,listening,connecting,done,stopping,clearSent;
 static String role,run,planSha,phase="bootstrap",caseId="",mode="",view="",binding="",fixtureHash="",stable="";
 static Path bridge,root,hostOut,peerOut,ownOut,world;
 static JsonObject plan,command,fixture;
 static int ticks,frames,phaseTick,index=-1,stableTicks;
 static long started,phaseAt,stopAt;
 static final Set<String> readyMessages=new HashSet<>();
 static CompletableFuture<?> work;
 static Schedule schedule;

 /** Pure JDK schedule, independently executable without loading Minecraft or this outer class. */
 public static final class Schedule {
  public final String prefix;
  public int index=-1,viewIndex,negative;
  public final int[] attempts={0,0};
  public final String[] positives={"",""};
  public boolean finished;
  private String issued="";
  public Schedule(String prefix){if(!prefix.matches("[a-zA-Z0-9-]{1,30}"))throw new IllegalArgumentException("run ID");this.prefix=prefix;}
  public Map<String,Object> next(){
   if(finished||!issued.isEmpty())throw new IllegalStateException("Already finished or stage outstanding");
   if(viewIndex<2&&attempts[viewIndex]>=6)throw new IllegalStateException("AGE1_NOT_OBSERVED_WITHIN_6_ATTEMPTS_"+(viewIndex==0?"first":"third"));index++;
   String v=viewIndex==0?"first":"third",m="success",cal="";
   if(viewIndex<2){if(attempts[viewIndex]>=6)throw new IllegalStateException("AGE1_NOT_OBSERVED_WITHIN_6_ATTEMPTS_"+v);attempts[viewIndex]++;}
   else {if(negative>=6)throw new IllegalStateException("Negative bound");v=negative%2==0?"first":"third";m=List.of("cancel-attack","cancel-damage","invulnerable").get(negative/2);cal=positives[negative%2];}
   String id=prefix+"-s"+String.format(java.util.Locale.ROOT,"%02d",index)+"-"+v;
   issued=id;return Map.of("index",index,"case",id,"mode",m,"view",v,"calibration",cal);
  }
  public void finish(String id,boolean boundaryCandidate){
   if(!issued.equals(id)||issued.isEmpty())throw new IllegalStateException("Stage finish identity/order");issued="";
   if(viewIndex<2){if(boundaryCandidate){positives[viewIndex]=id;viewIndex++;}}
   else {negative++;if(negative==6)finished=true;}
  }
 }
 static void require(boolean b,String message){if(!b)throw new IllegalStateException(message);}
 static String text(JsonObject j,String k){return j.get(k).getAsString();}
 static JsonObject read(Path file)throws Exception{return JsonParser.parseString(Files.readString(file)).getAsJsonObject();}
 static Path real(String path)throws Exception{Path p=Path.of(path);require(p.isAbsolute(),"Absolute private paths required");return p.toRealPath();}
 static void write(String name,Object data)throws Exception{Path temp=bridge.resolve(name+"."+role+".tmp");Files.writeString(temp,JSON.toJson(data));Files.move(temp,bridge.resolve(name),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}
 static Map<String,Object> stamp(){var d=new LinkedHashMap<String,Object>();d.put("run",run);d.put("plan_sha256",planSha);d.put("role",role);d.put("qa_process_session",Probe.CLIENT.stamp().get("session"));d.put("driver_tick",ticks);d.put("phase",phase);d.put("index",index);d.put("case",caseId);return d;}
 static void log(String kind,Object data)throws Exception{var d=stamp();d.put("kind",kind);d.put("data",data);Files.writeString(bridge.resolve(role+"-driver.jsonl"),JSON.toJson(d).replace("\n","")+"\n",StandardOpenOption.CREATE,StandardOpenOption.APPEND);}
 static void enter(String p)throws Exception{phase=p;phaseAt=System.nanoTime();phaseTick=ticks;stable="";stableTicks=0;log("phase",p);}
 static boolean exists(String name){return Files.isRegularFile(bridge.resolve(name));}
 static boolean valid(String name)throws Exception{if(!exists(name))return false;var j=read(bridge.resolve(name));require(run.equals(text(j,"run"))&&planSha.equals(text(j,"plan_sha256")),"Stale/foreign marker: "+name);if(name.matches("(server-ready|peer-arm-sent|peer-input-ready|host-watch-start|peer-capture-complete|peer-ack|result)-[0-9]+\\.json"))require(j.get("index").getAsInt()==index&&caseId.equals(text(j,"case")),"Stage marker identity: "+name);return true;}
 static void mark(String name)throws Exception{write(name,stamp());}
 static boolean stableFile(Path file)throws Exception{
  if(!Files.isRegularFile(file))return false;
  String digest=CaseLog.sha(file);if(!digest.equals(stable)){stable=digest;stableTicks=1;return false;}
  if(++stableTicks<2)return false;
  try{JsonParser.parseString(Files.readString(file));return true;}catch(JsonParseException partial){return false;}
 }
 /** Raw imports have one writer per role; readiness is published only after exact-byte verification. */
 public static final class RawImport {
  public static String sha(Path p)throws Exception{return java.util.HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(p)));}
  public static void copy(Path from,Path to)throws Exception{
   if(from.equals(to))return;byte[] bytes=Files.readAllBytes(from);String digest=sha(from);
   if(Files.exists(to)){if(!digest.equals(sha(to)))throw new IllegalStateException("Refuse mismatched existing evidence: "+to);return;}
   Path temp=to.resolveSibling(to.getFileName()+".import.tmp");Files.write(temp,bytes,StandardOpenOption.CREATE_NEW);
   // CREATE_NEW via Files.copy refuses an existing destination, including a competing importer.
   // No consumer ready marker is emitted until this copy and SHA check complete.
   Files.copy(temp,to);if(!digest.equals(sha(to)))throw new IllegalStateException("Raw evidence SHA import mismatch");Files.delete(temp);
  }
 }
 static void copyExact(Path from,Path to)throws Exception{RawImport.copy(from,to);}
 static void init(Minecraft mc)throws Exception{
  role=Objects.requireNonNull(System.getProperty("dynasty.sweepdriver.role"));require(Set.of("host","peer").contains(role),"role");host=role.equals("host");
  bridge=real(Objects.requireNonNull(System.getProperty("dynasty.sweepdriver.bridge")));Path file=bridge.resolve("plan.json");plan=read(file);planSha=CaseLog.sha(file);run=text(plan,"run");schedule=host?new Schedule(run):null;
  root=real(text(plan,"private_root"));require(bridge.startsWith(root)&&!bridge.equals(root),"Bridge outside private root");
  var marker=read(root.resolve("sweep-driver-private.json"));require(run.equals(text(marker,"run"))&&planSha.equals(text(marker,"plan_sha256")),"Missing exact private-root/plan binding");
  Path hi=real(text(plan,"host_instance")),pi=real(text(plan,"peer_instance"));hostOut=real(text(plan,"host_output"));peerOut=real(text(plan,"peer_output"));ownOut=host?hostOut:peerOut;
  require(!hi.equals(pi)&&!hostOut.equals(peerOut),"Distinct role instances/outputs required");
  for(Path p:List.of(hi,pi,hostOut,peerOut))require(p.startsWith(root)&&!p.equals(root),"Role path escaped private root");
  require(mc.gameDirectory.toPath().toRealPath().equals(host?hi:pi)&&ownOut.equals(com.dynasty.sweepqa.SweepQA.OUT.toRealPath()),"Private instance/output mismatch");
  require(text(plan,"qa_sha256").equals(Probe.CLIENT.stamp().get("artifact")),"Wrong QA03 artifact");
  var mods=net.minecraftforge.fml.ModList.get();require(text(plan,"driver_sha256").equals(CaseLog.sha(mods.getModFileById("dynastysweepdriver").getFile().getFilePath())),"Wrong driver artifact");
  require(text(plan,"production_sha256").equals(CaseLog.sha(mods.getModFileById("dynasty").getFile().getFilePath())),"Wrong private production artifact");
  String save=text(plan,"saved_world");require(save.matches("[a-zA-Z0-9 _-]{1,100}"),"Single existing private save name required");world=hi.resolve("saves").resolve(save).toRealPath();require(world.startsWith(hi.resolve("saves").toRealPath())&&Files.isRegularFile(world.resolve("level.dat")),"Existing copied world required");
  // Do not install a second window hook: coordinator supplies its already verified hidden bootstrap.
  long window=mc.getWindow().getWindow();require(GLFW.glfwGetWindowAttrib(window,GLFW.GLFW_VISIBLE)==GLFW.GLFW_FALSE&&GLFW.glfwGetWindowAttrib(window,GLFW.GLFW_FOCUSED)==GLFW.GLFW_FALSE,"Window must already be hidden/unfocused");
  Files.writeString(bridge.resolve(role+"-session.json"),JSON.toJson(stamp()),StandardOpenOption.CREATE_NEW);
  owned=true;initialized=true;started=phaseAt=System.nanoTime();log("driver-enabled",Map.of("world",world.toString(),"bootstrap_existing_world",plan.get("bootstrap_existing_world").getAsBoolean(),"creates_world",false,"window_hidden",true,"window_unfocused",true));
 }
 static void chat(Minecraft mc,String command)throws Exception{
  require(mc.player!=null&&mc.player.connection!=null,"No native client connection");
  // Same call made by ChatScreen.handleChatInput: Forge local-command interception or signed native C2S command packet.
  mc.player.connection.sendCommand(command);log("native-client-chat-command",command);
 }
 @SubscribeEvent public static void ready(ClientChatReceivedEvent.System e){if(!ENABLED||!initialized||done)return;String s=e.getMessage().getString();if(s.startsWith("[COD4_SWEEP_READY_"+run+"_")&&readyMessages.size()<64)readyMessages.add(s);}
 @SubscribeEvent public static void frame(RenderLevelStageEvent e){if(ENABLED&&e.getStage()==RenderLevelStageEvent.Stage.AFTER_LEVEL)frames++;}
 static void bootstrap(Minecraft mc)throws Exception{
  if(mc.getOverlay()!=null)return;
  if(mc.screen instanceof net.minecraftforge.client.gui.LoadingErrorScreen)throw new IllegalStateException("Forge warning/error: no automatic bypass");
  if(mc.screen instanceof DisconnectedScreen)throw new IllegalStateException("Disconnected; no blind reconnect");
  if(mc.level==null||mc.player==null){
   if(!plan.get("bootstrap_existing_world").getAsBoolean())return;
   if(mc.screen instanceof TitleScreen){
    if(host&&!opening){opening=true;mc.createWorldOpenFlows().loadLevel(new TitleScreen(),world.getFileName().toString());}
    if(!host&&!connecting&&valid("port.json")){connecting=true;String port=Files.readString(bridge.resolve("port.txt")).trim();require(port.matches("[0-9]{1,5}")&&port.equals(text(read(bridge.resolve("port.json")),"port")),"Port binding");String address="127.0.0.1:"+port;ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString(address),new ServerData("Private sweep bridge",address,false),false);}
   }return;
  }
  require(mc.player.getUUID().toString().equals(text(plan,role+"_uuid")),"Unexpected role UUID");
  require(mc.gameMode.getPlayerMode()==GameType.SURVIVAL,"Native survival fixture required");
  if(host&&!listening){
   var server=Objects.requireNonNull(mc.getSingleplayerServer());require(server.getWorldPath(LevelResource.ROOT).toRealPath().equals(world),"Loaded world is not selected private copy");listening=true;
   if(!server.isPublished()){int port;try(var socket=new java.net.ServerSocket(0)){port=socket.getLocalPort();}server.setUsesAuthentication(false);require(server.publishServer(GameType.SURVIVAL,true,port),"LAN publish");}
   String port=""+server.getPort();Files.writeString(bridge.resolve("port.txt"),port,StandardOpenOption.CREATE_NEW);var d=stamp();d.put("port",port);write("port.json",d);
  }
  if(mc.screen!=null||frames<3)return;
  if(!exists(role+"-world-rendered"))mark(role+"-world-rendered");
  if(!host){enter("peer-command");return;}
  if(!valid("peer-world-rendered"))return;
  if(work==null){var server=mc.getSingleplayerServer();work=server.submit(()->{
   try{var ps=server.getPlayerList().getPlayers();require(ps.size()==2&&ps.stream().noneMatch(p->p instanceof net.minecraftforge.common.util.FakePlayer),"Two real clients required");ServerPlayer a=server.getPlayerList().getPlayer(UUID.fromString(text(plan,"host_uuid"))),b=server.getPlayerList().getPlayer(UUID.fromString(text(plan,"peer_uuid")));require(a!=null&&b!=null&&a!=b&&b.connection.connection.getRemoteAddress() instanceof java.net.InetSocketAddress,"Real independent TCP peer");write("connections.json",Map.of("run",run,"plan_sha256",planSha,"players",ps.stream().map(p->Map.of("uuid",p.getUUID().toString(),"class",p.getClass().getName(),"remote",p.connection.connection.getRemoteAddress().toString())).toList()));}catch(Exception x){throw new IllegalStateException(x);}
  });return;}
  if(!work.isDone())return;work.join();work=null;next();
 }
 static void next()throws Exception{
  if(schedule.finished){stop("ACTION_MATRIX_CAPTURED_ANALYSIS_AND_VISUAL_PENDING");return;}
  var row=new LinkedHashMap<String,Object>(schedule.next());index=(Integer)row.get("index");caseId=(String)row.get("case");mode=(String)row.get("mode");view=(String)row.get("view");row.put("run",run);row.put("plan_sha256",planSha);require(!exists("command-"+index+".json"),"Refuse stage overwrite");write("command-"+index+".json",row);write("command.json",row);enter("host-fixture");
 }
 static void loadCommand(JsonObject c)throws Exception{index=c.get("index").getAsInt();caseId=text(c,"case");mode=text(c,"mode");view=text(c,"view");require(index>=0&&index<18&&caseId.matches("[a-zA-Z0-9-]{1,70}")&&Set.of("first","third").contains(view)&&Set.of("success","cancel-attack","cancel-damage","invulnerable").contains(mode),"Bad stage");command=c;}
 static void importFixture()throws Exception{
  Path file=hostOut.resolve(caseId+"-fixture.json");fixture=read(file);fixtureHash=CaseLog.sha(file);var fi=fixture.getAsJsonObject("identity");binding=text(fi,"binding");
  require(caseId.equals(text(fixture,"case"))&&mode.equals(text(fixture,"mode"))&&text(plan,"peer_uuid").equals(text(fixture.getAsJsonObject("actor"),"uuid"))&&text(plan,"qa_sha256").equals(text(fi,"artifact"))&&caseId.equals(text(fi,"case")),"Fixture identity mismatch");
  copyExact(file,ownOut.resolve(caseId+"-fixture.json"));var d=stamp();d.put("fixture_sha256",fixtureHash);d.put("binding",binding);write(role+"-import-"+index+".json",d);
 }
 static boolean captureDone(Path output)throws Exception{
  Path file=output.resolve(caseId+"-client-events.json");if(!Files.isRegularFile(file)||!Files.isRegularFile(output.resolve(caseId+"-client-frames.json")))return false;
  JsonArray events;try{events=JsonParser.parseString(Files.readString(file)).getAsJsonArray();}catch(JsonParseException partial){return false;}
  for(var x:events){var e=x.getAsJsonObject();if(text(e,"kind").equals("client-capture-end")){require(text(e,"case").equals(caseId)&&text(e,"binding").equals(binding)&&text(e,"artifact").equals(text(plan,"qa_sha256")),"Capture identity");var d=e.getAsJsonObject("data");require(text(d,"reason").equals("bounded-40-client-ticks")&&d.get("ticks").getAsInt()>=40,"Incomplete capture");return true;}}return false;
 }
 static void hostTick(Minecraft mc)throws Exception{
  if(phase.equals("host-fixture")){
   if(!valid("peer-arm-sent-"+index+".json")||!stableFile(hostOut.resolve(caseId+"-fixture.json")))return;importFixture();
   var server=mc.getSingleplayerServer();work=server.submit(()->{
    try{require(caseId.equals(Probe.SERVER.current())&&binding.equals(Probe.SERVER.stamp().get("binding")),"Native server arm not current");var d=stamp();d.put("binding",binding);d.put("fixture_sha256",fixtureHash);d.put("server_tick",server.getTickCount());write("server-ready-"+index+".json",d);for(var p:server.getPlayerList().getPlayers())p.sendSystemMessage(Component.literal("[COD4_SWEEP_READY_"+run+"_"+index+"_"+binding+"]"));}catch(Exception ex){throw new IllegalStateException(ex);}
   });enter("host-watch");return;
  }
  if(phase.equals("host-watch")){
   if(work!=null){if(!work.isDone())return;work.join();work=null;}
   if(!readyMessages.contains("[COD4_SWEEP_READY_"+run+"_"+index+"_"+binding+"]")||!valid("peer-input-ready-"+index+".json"))return;
   chat(mc,"sweepqa-watch "+caseId+" "+view);require(Probe.CLIENT.current().equals(caseId),"Watch command not accepted");mark("host-watch-start-"+index+".json");enter("host-capture");return;
  }
  if(phase.equals("host-capture")){
   if(!valid("peer-capture-complete-"+index+".json")||!captureDone(hostOut)||!Probe.CLIENT.current().isEmpty()||!postAttackCoverage())return;
   chat(mc,"sweepqa dump");enter("host-dump");return;
  }
  if(phase.equals("host-dump")){
   if(!stableFile(hostOut.resolve(caseId+"-server-events.json")))return;chat(mc,"sweepqa clear");enter("host-clear");return;
  }
  if(phase.equals("host-clear")){
   if(!Probe.SERVER.current().isEmpty()||!stableFile(hostOut.resolve(caseId+"-server-events.json")))return;
   copyExact(hostOut.resolve(caseId+"-server-events.json"),peerOut.resolve(caseId+"-server-events.json"));
   boolean candidate=classify();var d=stamp();d.put("mode",mode);d.put("view",view);d.put("age1_candidate_only",candidate);d.put("calibration",mode.equals("success")?"":schedule.positives[view.equals("first")?0:1]);d.put("overall_acceptance",false);d.put("fixture_sha256",fixtureHash);d.put("server_events_sha256",CaseLog.sha(hostOut.resolve(caseId+"-server-events.json")));write("result-"+index+".json",d);schedule.finish(caseId,candidate);enter("host-ack");return;
  }
  if(phase.equals("host-ack")){if(valid("peer-ack-"+index+".json"))next();}
 }
 static boolean postAttackCoverage(){
  var records=JSON.toJsonTree(Probe.SERVER.snapshot()).getAsJsonArray();int attack=-1;var before=new HashSet<Integer>();var after=new HashSet<Integer>();
  for(var x:records){var e=x.getAsJsonObject();if(!caseId.equals(text(e,"case")))continue;String k=text(e,"kind");if(k.equals("server-native-attack"))attack=e.getAsJsonObject("data").get("cycle").getAsInt();if(k.equals("receipt-before-exact-consumer"))before.add(e.getAsJsonObject("data").get("cycle").getAsInt());if(k.equals("receipt-after-exact-consumer"))after.add(e.getAsJsonObject("data").get("cycle").getAsInt());}
  if(attack<0)return false;for(int n=attack+1;n<=attack+20;n++)if(!before.contains(n)||!after.contains(n))return false;return true;
 }
 static boolean entity(JsonObject a,JsonObject b){return text(a,"uuid").equals(text(b,"uuid"))&&a.get("id").getAsInt()==b.get("id").getAsInt()&&text(a,"dimension").equals(text(b,"dimension"));}
 static boolean classify()throws Exception{
  var server=JsonParser.parseString(Files.readString(hostOut.resolve(caseId+"-server-events.json"))).getAsJsonArray();var client=JsonParser.parseString(Files.readString(peerOut.resolve(caseId+"-client-events.json"))).getAsJsonArray();var frames=JsonParser.parseString(Files.readString(peerOut.resolve(caseId+"-client-frames.json"))).getAsJsonArray();
  boolean age1=false,damaged=false,geometry=false;int cues=0,attacks=0,inputs=0;long consumed=-1,cueStart=-2;var hooks=new HashSet<String>();var primary=fixture.getAsJsonArray("targets").get(0).getAsJsonObject();var actor=fixture.getAsJsonObject("actor");
  for(var x:server){var e=x.getAsJsonObject();require(text(e,"case").equals(caseId)&&text(e,"binding").equals(binding),"Foreign server record");String kind=text(e,"kind");require(!kind.equals("probe-error"),"Server probe failure");
   if(kind.equals("server-native-attack")){var d=e.getAsJsonObject("data");require(entity(d.getAsJsonObject("actor"),actor)&&entity(d.getAsJsonObject("target"),primary)&&d.get("cancelled").getAsBoolean()==mode.equals("cancel-attack"),"Native server attack identity/cancel state");attacks++;}
   if(kind.equals("receipt-before-exact-consumer"))for(var y:e.getAsJsonObject("data").getAsJsonArray("rows")){var r=y.getAsJsonObject();require(entity(r.getAsJsonObject("main"),primary)&&entity(r.getAsJsonObject("actor"),actor),"Receipt identity");if(r.get("age").getAsInt()==1&&r.get("consumedNow").getAsLong()-r.get("produced").getAsLong()==1&&r.get("capturedLevelMatchesActor").getAsBoolean()&&r.get("capturedLevelMatchesMain").getAsBoolean()){age1=true;consumed=r.get("consumedNow").getAsLong();}}
   if(kind.equals("server-final-targets"))for(var y:e.getAsJsonArray("data")){var t=y.getAsJsonObject();for(var start:fixture.getAsJsonArray("targets"))if(text(start.getAsJsonObject(),"uuid").equals(text(t,"uuid"))&&t.get("health").getAsDouble()<start.getAsJsonObject().get("health").getAsDouble())damaged=true;}
  }
  for(var x:client){var e=x.getAsJsonObject();require(text(e,"case").equals(caseId)&&text(e,"binding").equals(binding),"Foreign client record");String kind=text(e,"kind");require(!kind.equals("probe-error"),"Client probe failure");
   if(kind.equals("actual-client-gamemode-attack")){var d=e.getAsJsonObject("data");require(entity(d.getAsJsonObject("player"),actor)&&entity(d.getAsJsonObject("target"),primary),"Native input actor/main");inputs++;}
   if(kind.equals("loaded-render-hook"))hooks.add(e.get("data").getAsString());
   if(kind.equals("actual-s2c-handle")){var p=e.getAsJsonObject("data");if(text(p,"sequence").equals("equipment_confirmed_fangtian_sweep")){require(p.get("entity").getAsInt()==actor.get("id").getAsInt()&&text(p,"dimension").equals(text(actor,"dimension")),"Cue owner/dimension");cues++;cueStart=p.get("start").getAsLong();}}
  }
  for(var f:frames){var g=f.getAsJsonObject().getAsJsonObject("geometry");if(g.has("FangtianSweep")&&g.getAsJsonArray("FangtianSweep").size()>0)geometry=true;}
  require(attacks==1&&inputs==1&&hooks.containsAll(Set.of("FangtianSweep.before","FangtianSweep.after","Cod3Vfx.before","Cod3Vfx.after")),"Native attack or live hooks missing");
  // Progression hint only: the complete existing analyze.py remains authoritative for all mechanical evidence.
  if(mode.equals("success")){require(cues==1&&damaged&&geometry,"Genuine positive cue/damage/geometry missing");if(age1)require(cueStart==consumed,"Age1 cue start does not match consumer");return age1;}
  require(cues==0&&!damaged&&!geometry,"Negative control has cue/damage/geometry");return false;
 }
 static void peerTick(Minecraft mc)throws Exception{
  if(phase.equals("peer-command")){
   if(!valid("command.json"))return;var c=read(bridge.resolve("command.json"));int n=c.get("index").getAsInt();if(n==index)return;require(n==index+1,"Nonmonotonic stage");loadCommand(c);chat(mc,"sweepqa arm "+caseId+" "+mode);mark("peer-arm-sent-"+index+".json");enter("peer-ready");return;
  }
  if(phase.equals("peer-ready")){
   if(!valid("server-ready-"+index+".json")||!stableFile(hostOut.resolve(caseId+"-fixture.json")))return;
   importFixture();var ready=read(bridge.resolve("server-ready-"+index+".json"));require(binding.equals(text(ready,"binding"))&&fixtureHash.equals(text(ready,"fixture_sha256")),"Native-ready fixture SHA/nonce mismatch");
   if(!readyMessages.contains("[COD4_SWEEP_READY_"+run+"_"+index+"_"+binding+"]"))return;
   var target=fixture.getAsJsonArray("targets").get(0).getAsJsonObject();var e=mc.level.getEntity(target.get("id").getAsInt());
   if(e==null||!e.getUUID().toString().equals(text(target,"uuid"))||mc.player.distanceTo(e)>3||mc.player.getAttackStrengthScale(0)<.99f||!net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(mc.player.getMainHandItem().getItem()).toString().equals("dynasty:halberd_fangtian"))return;
   require(mc.player.getUUID().toString().equals(text(fixture.getAsJsonObject("actor"),"uuid")),"Wrong native actor");mark("peer-input-ready-"+index+".json");enter("peer-attack");return;
  }
  if(phase.equals("peer-attack")){
   if(!valid("host-watch-start-"+index+".json"))return;
   int id=fixture.getAsJsonArray("targets").get(0).getAsJsonObject().get("id").getAsInt();chat(mc,"sweepqa-client "+caseId+" "+id+" "+view);require(Probe.CLIENT.current().equals(caseId),"Native local attack command rejected");mark("peer-input-"+index+".json");enter("peer-capture");return;
  }
  if(phase.equals("peer-capture")){
   if(!Probe.CLIENT.current().isEmpty()||!captureDone(peerOut))return;mark("peer-capture-complete-"+index+".json");enter("peer-result");return;
  }
  if(phase.equals("peer-result")){if(!valid("result-"+index+".json"))return;mark("peer-ack-"+index+".json");enter("peer-command");}
 }
 static void stop(String reason)throws Exception{if(stopping)return;stopping=true;stopAt=System.nanoTime();log("bounded-stop",reason);if(host){var d=stamp();d.put("status",reason);d.put("overall_acceptance",false);write("server-COMPLETE",d);}}
 static void stopping(Minecraft mc)throws Exception{
  if(host&&!clearSent&&mc.player!=null&&!Probe.SERVER.current().isEmpty()){clearSent=true;chat(mc,"sweepqa clear");}
  if(!host){mark("peer-COMPLETE");done=true;mc.stop();return;}
  if(!Probe.SERVER.current().isEmpty()&&System.nanoTime()-stopAt<5_000_000_000L)return;
  if(valid("peer-COMPLETE")||System.nanoTime()-stopAt>=10_000_000_000L){mark("host-COMPLETE");done=true;mc.stop();}
 }
 @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
  if(!ENABLED||done||e.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();ticks++;
  try{
   if(!initialized)init(mc);
   if(stopping){stopping(mc);return;}
   if(valid("server-COMPLETE")){stop(text(read(bridge.resolve("server-COMPLETE")),"status"));return;}
   if(exists("abort.json")||exists("external-stop-request.txt")){stop("ABORT_OR_EXTERNAL_STOP_REVIEW_EVIDENCE");return;}
   require(System.nanoTime()-started<900_000_000_000L,"900 second overall bound");require(System.nanoTime()-phaseAt<(phase.equals("bootstrap")?240_000_000_000L:60_000_000_000L)&&ticks-phaseTick<(phase.equals("bootstrap")?6000:1000),"Stage deadline: "+phase);
   if(ticks%40==0)write(role+"-heartbeat.json",stamp());
   if(phase.equals("bootstrap")){bootstrap(mc);return;}
   require(mc.level!=null&&mc.player!=null,"World disconnected during case");
   if(host)hostTick(mc);else peerTick(mc);
  }catch(Throwable x){
   try{if(bridge!=null){var d=stamp();d.put("error",x.toString());write(role+"-FAIL.json",d);write("abort.json",d);}if(owned){stop("DRIVER_FAILURE_REVIEW_RAW_EVIDENCE");}else done=true;}catch(Throwable ignored){done=true;}
  }
 }
}
