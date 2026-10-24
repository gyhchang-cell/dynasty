package com.dynasty.networkqa;

import com.google.gson.*;
import com.dynasty.expansion.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Private automated TCP clients. Server-side fixtures are deliberately identified as fixtures. */
@Mod("dynastynetworkqa")
public final class NetworkAcceptance {
 static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
 static final Path OUT=Path.of(System.getProperty("dynasty.networkqa.output"));
 static final String ROLE=System.getProperty("dynasty.networkqa.role");
 static final boolean HOST=ROLE.equals("host");
 static final List<RegistryObject<MobEffect>> EFFECTS=List.of(ExpansionEffects.YIN,ExpansionEffects.YANG,ExpansionEffects.SHA,ExpansionEffects.THUNDER,ExpansionEffects.SOUL,ExpansionEffects.FROST,ExpansionEffects.BREAK,ExpansionEffects.STAGGER);
 static final List<String> NAMES=List.of("yin_qi","yang_qi","sha_qi","thunder_mark","soul_burn","frost_vein","armor_break","stagger");
 static void write(String file,Object data)throws Exception{Path temp=OUT.resolve(file+".tmp");Files.writeString(temp,JSON.toJson(data));Files.move(temp,OUT.resolve(file),StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);}
 static void marker(String f)throws Exception{Files.writeString(OUT.resolve(f),"ready");}
 static boolean exists(String f){return Files.exists(OUT.resolve(f));}
 static ItemStack item(String id){return new ItemStack(Objects.requireNonNull(ForgeRegistries.ITEMS.getValue(new ResourceLocation("dynasty",id))));}
 static void armor(ServerPlayer p,String set){String[] names={"helmet","chestplate","leggings","boots"};EquipmentSlot[] slots={EquipmentSlot.HEAD,EquipmentSlot.CHEST,EquipmentSlot.LEGS,EquipmentSlot.FEET};for(int i=0;i<4;i++)p.setItemSlot(slots[i],set.isEmpty()?ItemStack.EMPTY:item(set+"_"+names[i]));}
 static Map<String,Object> state(LivingEntity p){var s=new LinkedHashMap<String,Object>();s.put("uuid",p.getUUID().toString());s.put("entity",p.getId());var effects=new TreeMap<String,Object>();for(var e:p.getActiveEffects()){String id=ForgeRegistries.MOB_EFFECTS.getKey(e.getEffect()).toString();if(id.startsWith("dynasty:"))effects.put(id,Map.of("amplifier",e.getAmplifier(),"duration",e.getDuration()));}s.put("effects",effects);var gear=new TreeMap<String,String>();for(var slot:EquipmentSlot.values())gear.put(slot.name(),ForgeRegistries.ITEMS.getKey(p.getItemBySlot(slot).getItem()).toString());s.put("gear",gear);if(p instanceof net.minecraft.world.entity.player.Player player){s.put("activeTrinkets",com.dynasty.DynastyTrinkets.equippedIds(player).stream().sorted().toList());var slots=new TreeMap<String,Object>();top.theillusivec4.curios.api.CuriosApi.getCuriosInventory(player).ifPresent(h->h.getCurios().forEach((id,handler)->{var contents=new ArrayList<String>();for(int i=0;i<handler.getStacks().getSlots();i++)contents.add(ForgeRegistries.ITEMS.getKey(handler.getStacks().getStackInSlot(i).getItem()).toString());slots.put(id,contents);}));s.put("curios",slots);}return s;}
 @Mod.EventBusSubscriber(modid="dynastynetworkqa",value=net.minecraftforge.api.distmarker.Dist.CLIENT)
 public static final class Client {
  static boolean started,done,listening;static int tick,stage=-1,lastAck=-1,wait;static CompletableFuture<?> task;
  static long deadline=System.nanoTime()+1_200_000_000_000L;
  static int pendingCapture=-1,renderFrames,worldFrames;static boolean worldRendered;static Object captureEvidence;
  static String mismatch="";static int newSerial=-1,serialStart;static boolean inputSent;static volatile int pendingStage=-1,pendingAt;static volatile String pendingLabel;
  static final int LAST=48;
  @SubscribeEvent public static void tick(TickEvent.ClientTickEvent ev){if(WeaponProbe.enabled()||done||ev.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();tick++;
   try{
    if(exists("server-FAIL.txt"))throw new AssertionError(Files.readString(OUT.resolve("server-FAIL.txt")));
    if(System.nanoTime()>deadline)throw new AssertionError("timeout stage="+stage+" mismatch="+mismatch);
    if(mc.getOverlay()!=null)return;
    if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
    if(!started&&mc.screen instanceof TitleScreen){
     if(!mc.gameDirectory.getCanonicalPath().equals(System.getProperty("dynasty.networkqa.instance")))throw new AssertionError("Unsafe instance");
     if(!HOST&&!exists("port.txt"))return;started=true;
     if(!HOST){String addr="127.0.0.1:"+Files.readString(OUT.resolve("port.txt")).trim();ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString(addr),new ServerData("Private Network QA",addr,false),false);return;}
     var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
     mc.createWorldOpenFlows().createFreshLevel("cod4-network-"+System.currentTimeMillis(),new LevelSettings("Private QA fixtures",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(77,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
    }
    if(mc.level==null||mc.player==null)return;
    if(exists("server-PASS")){marker(ROLE+"-PASS");if(!HOST||exists("peer-PASS")){done=true;mc.stop();}return;}
    if(task!=null){if(!task.isDone())return;task.join();task=null;}
    var server=mc.getSingleplayerServer();
    if(HOST&&!listening){listening=true;int port;try(var socket=new java.net.ServerSocket(0)){port=socket.getLocalPort();}server.setUsesAuthentication(false);if(!server.publishServer(GameType.CREATIVE,true,port))throw new AssertionError("publishLAN failed");Files.writeString(OUT.resolve("port.txt"),Integer.toString(port));return;}
    if(mc.screen!=null||worldFrames<3)return;marker(ROLE+"-world-rendered");
    if(HOST&&stage<0){if(server.getPlayerList().getPlayerCount()!=2||!exists("peer-world-rendered"))return;stage=0;task=server.submit(()->{
      var players=players(server);if(!(players.get(1).connection.connection.getRemoteAddress() instanceof java.net.InetSocketAddress))throw new AssertionError("Peer must use real TCP");if(players.get(0).getUUID().equals(players.get(1).getUUID()))throw new AssertionError("UUID collision");
      for(int i=0;i<2;i++){var p=players.get(i);if(p.connection==null||!p.connection.connection.isConnected())throw new AssertionError("not network connected");p.teleportTo(server.overworld(),i*3,-60,0,0,0);p.setHealth(p.getMaxHealth());p.getAbilities().invulnerable=true;p.onUpdateAbilities();}
      server.overworld().setDayTime(1000);try{write("connections.json",players.stream().map(p->Map.of("name",p.getGameProfile().getName(),"uuid",p.getUUID().toString(),"remote",p.connection.connection.getRemoteAddress().toString(),"channel",p.connection.connection.getClass().getName())).toList());prepare(server,0);}catch(Exception ex){throw new RuntimeException(ex);}
     });return;}
    if(!HOST&&exists("request-peer-use")&&!inputSent&&mc.player.getMainHandItem().is(item("qi_pill").getItem())){mc.setScreen(null);mc.options.keyUse.setDown(true);var result=mc.gameMode.useItem(mc.player,net.minecraft.world.InteractionHand.MAIN_HAND);write("peer-c2s-input.json",Map.of("action","MultiPlayerGameMode.useItem MAIN_HAND; native held keyUse","result",result.toString(),"clientTick",tick));inputSent=true;}
    if(!HOST&&inputSent&&mc.player.hasEffect(ExpansionEffects.YANG.get()))mc.options.keyUse.setDown(false);
    if(exists("server-stage.json")){
     var expected=JsonParser.parseString(Files.readString(OUT.resolve("server-stage.json"))).getAsJsonObject();int serial=expected.get("stage").getAsInt();if(serial!=newSerial){newSerial=serial;serialStart=tick;}if(serial!=lastAck&&tick-serialStart>400){write(ROLE+"-mismatch.json",Map.of("expected",expected,"localPlayers",mc.level.players().stream().map(NetworkAcceptance::state).toList(),"why",mismatch));throw new AssertionError("stage "+serial+" never synchronized: "+mismatch);}
     if(serial!=lastAck){var observed=new JsonArray();boolean matches=true;StringBuilder why=new StringBuilder();for(var row:expected.getAsJsonArray("players")){var exp=row.getAsJsonObject();var p=mc.level.getPlayerByUUID(UUID.fromString(exp.get("uuid").getAsString()));if(p==null){if(serial==46){observed.add(JSON.toJsonTree(Map.of("uuid",exp.get("uuid").getAsString(),"tracking","outside client view")));continue;}matches=false;why.append("missing entity ");continue;}var actual=JSON.toJsonTree(state(p)).getAsJsonObject();observed.add(actual);if(!exp.get("curios").equals(actual.get("curios"))||!exp.get("activeTrinkets").equals(actual.get("activeTrinkets"))){matches=false;why.append("curios ownership ");}if(!exp.get("gear").equals(actual.get("gear"))){matches=false;why.append("gear ");}
       // Native Minecraft guarantees full active effect packets to the affected player. Remote entity state is recorded separately.
       var vf=com.dynasty.client.Cod3VfxRenderer.class.getDeclaredField("ACTIVE");vf.setAccessible(true);
       @SuppressWarnings("unchecked") var visual=List.copyOf((List<com.dynasty.cod3.Cod3VisualPacket>)vf.get(null));
       var aura=new TreeMap<String,Integer>();for(var packet:visual)if(packet.entityId()==p.getId()&&packet.sequence().matches("status_[1-8]")&&mc.level.getGameTime()-packet.start()<packet.duration())aura.put(NAMES.get(Integer.parseInt(packet.sequence().substring(7))-1),packet.tick());
       actual.add("statusAura",JSON.toJsonTree(aura));
       var expectedAura=new TreeMap<String,Integer>();for(var fx:exp.getAsJsonObject("effects").entrySet()){String key=fx.getKey().substring(8);if(NAMES.contains(key))expectedAura.put(key,fx.getValue().getAsJsonObject().get("amplifier").getAsInt());}
       if(serial==46&&p!=mc.player)expectedAura.clear();if(!aura.equals(expectedAura)){matches=false;why.append("aura "+p.getName().getString()+" expected="+expectedAura+" actual="+aura+" ");}
       if(p==mc.player){var ee=exp.getAsJsonObject("effects");var ae=actual.getAsJsonObject("effects");if(!ee.keySet().equals(ae.keySet())){matches=false;why.append("effect IDs ");}for(String id:ee.keySet())if(ae.has(id)){var a=ae.getAsJsonObject(id);var b=ee.getAsJsonObject(id);if(a.get("amplifier").getAsInt()!=b.get("amplifier").getAsInt()||Math.abs(a.get("duration").getAsInt()-b.get("duration").getAsInt())>100){matches=false;why.append("amp/duration ");}}}
      }
      mismatch=why.toString();if(matches){lastAck=serial;captureEvidence=Map.of("expected",expected,"observed",observed,"clientTick",tick,"selfFullEffectsMatch",true);pendingCapture=serial;wait=0;}
     }
    }
    if(HOST&&stage>=0&&exists("host-ack-"+stage)&&exists("peer-ack-"+stage)&&++wait>12){if(stage==LAST){marker("server-PASS");marker("host-PASS");return;}stage++;int next=stage;task=server.submit(()->{try{prepare(server,next);}catch(Exception ex){throw new RuntimeException(ex);}});}
    if(exists("server-PASS")){marker(ROLE+"-PASS");if(!HOST)mc.stop();}
   }catch(Throwable error){done=true;error.printStackTrace();try{Files.writeString(OUT.resolve(ROLE+"-FAIL.txt"),"stage="+stage+" lastAck="+lastAck+" mismatch="+mismatch+"\n"+error);}catch(Exception ignored){}mc.stop();}
  }
  @SubscribeEvent public static void rendered(TickEvent.RenderTickEvent event){if(WeaponProbe.enabled())return;if(event.phase==TickEvent.Phase.START){worldRendered=false;return;}if(done)return;renderFrames++;if(pendingCapture<0||!worldRendered||Minecraft.getInstance().screen!=null)return;try{int n=pendingCapture;write(ROLE+"-stage-"+n+".json",Map.of("state",captureEvidence,"renderFrame",renderFrames,"captureEvent","RenderTick.END after actual AFTER_LEVEL world draw, no Screen, matching ClientTick","framebufferWidth",Minecraft.getInstance().getMainRenderTarget().width,"framebufferHeight",Minecraft.getInstance().getMainRenderTarget().height));if(n==1||n==17||n>=24)try(var image=Screenshot.takeScreenshot(Minecraft.getInstance().getMainRenderTarget())){image.writeToFile(OUT.resolve(ROLE+"-stage-"+n+".png"));}marker(ROLE+"-ack-"+n);pendingCapture=-1;}catch(Exception ex){try{Files.writeString(OUT.resolve(ROLE+"-FAIL.txt"),ex.toString());}catch(Exception ignored){}}}
  @SubscribeEvent public static void worldRendered(net.minecraftforge.client.event.RenderLevelStageEvent event){if(!WeaponProbe.enabled()&&event.getStage()==net.minecraftforge.client.event.RenderLevelStageEvent.Stage.AFTER_LEVEL){worldFrames++;worldRendered=true;}}
  static List<ServerPlayer> players(net.minecraft.server.MinecraftServer s){return s.getPlayerList().getPlayers().stream().sorted(Comparator.comparing(p->p.getGameProfile().getName())).toList();}
  static void prepare(net.minecraft.server.MinecraftServer s,int n)throws Exception{
   var ps=players(s);var a=ps.get(0);var b=ps.get(1);String label;
   if(n<24){int i=n/3,part=n%3;var e=EFFECTS.get(i);label=NAMES.get(i)+List.of(" apply fixture"," refresh fixture"," remove fixture").get(part);if(part==0){for(var p:ps){p.removeAllEffects();armor(p,"");}ExpansionEffects.apply(a,e,1200);b.addEffect(new MobEffectInstance(e.get(),1200,0));}else if(part==1){ExpansionEffects.apply(a,e,1400);b.addEffect(new MobEffectInstance(e.get(),1500,0));}else for(var p:ps)p.removeAllEffects();}
   else{label=switch(n){case 24->"day tiangang four native yin rejected";case 25->"day remove helmet native yin accepted";case 26->"day re-equip clears existing yin";case 27->"night tiangang loses yin immunity";case 28->"night disha native yang rejected";case 29->"night remove helmet yang accepted";case 30->"night re-equip clears existing yang";case 31->"day disha loses yang immunity";case 32->"yin host two stacks peer one";case 33->"yin host three stacks peer one";case 34->"yin host cap three peer one";case 35->"opposite qi neutralises host only";case 36->"thunder two stacks host one peer";case 37->"third thunder consumes host only";case 38->"native cleanse both";case 39->"independent armor ownership";case 40->"inventory accessories are inactive with Curios";case 41->"host equipped jade pendant only";case 42->"pendant ownership moved to peer only";case 43->"peer native client C2S pill consumption";case 45->"nearby host yin aura baseline";case 46->"peer outside32 blocks and tracking view";case 47->"peer re-enters view sees live host aura";default->"native cleanup";};
    if(n==24||n==28){for(var p:ps){p.removeAllEffects();armor(p,"");}s.overworld().setDayTime(n==24?1000:14000);armor(a,n==24?"tiangang":"disha");}
    if(n==25||n==29)a.setItemSlot(EquipmentSlot.HEAD,ItemStack.EMPTY);
    if(n==26||n==30){armor(a,n==26?"tiangang":"disha");QiConstitution.cleanse(a);}
    if(n==27)s.overworld().setDayTime(14000);if(n==31)s.overworld().setDayTime(1000);
    if(n==24||n==25)a.addEffect(new MobEffectInstance(ExpansionEffects.YIN.get(),1200));
    if(n==28||n==29)a.addEffect(new MobEffectInstance(ExpansionEffects.YANG.get(),1200));
    if(n==32){for(var p:ps){p.removeAllEffects();armor(p,"");}ExpansionEffects.apply(a,ExpansionEffects.YIN,1200);ExpansionEffects.apply(b,ExpansionEffects.YIN,1200);}
    if(n>=32&&n<=34)ExpansionEffects.apply(a,ExpansionEffects.YIN,1200);
    if(n==35)ExpansionEffects.apply(a,ExpansionEffects.YANG,1200);
    if(n==36){for(var p:ps)p.removeAllEffects();ExpansionEffects.apply(a,ExpansionEffects.THUNDER,1200);ExpansionEffects.apply(a,ExpansionEffects.THUNDER,1200);ExpansionEffects.apply(b,ExpansionEffects.THUNDER,1200);}
    if(n==37)ExpansionEffects.apply(a,ExpansionEffects.THUNDER,1200);
    if(n==38)for(var p:ps)p.removeAllEffects();
    if(n==39){armor(a,"tiangang");armor(b,"disha");}
    if(n==40){a.getInventory().add(item("jade_pendant"));b.getInventory().add(item("moon_pendant"));}
    if(n==41)top.theillusivec4.curios.api.CuriosApi.getCuriosInventory(a).orElseThrow(()->new AssertionError("Curios missing")).getStacksHandler("necklace").orElseThrow().getStacks().setStackInSlot(0,item("jade_pendant"));
    if(n==43){for(var p:ps){p.removeAllEffects();armor(p,"");p.setItemSlot(EquipmentSlot.MAINHAND,ItemStack.EMPTY);}b.setGameMode(GameType.SURVIVAL);b.getAbilities().invulnerable=true;b.onUpdateAbilities();b.getInventory().selected=0;var pill=item("qi_pill");pill.setCount(2);b.setItemSlot(EquipmentSlot.MAINHAND,pill);marker("request-peer-use");}
    if(n==45){for(var p:ps)p.removeAllEffects();ExpansionEffects.apply(a,ExpansionEffects.YIN,1200);}
    if(n==46)b.teleportTo(s.overworld(),100,-60,0,90,0);
    if(n==47)b.teleportTo(s.overworld(),3,-60,0,90,0);
    if(n==48)for(var p:ps)p.removeAllEffects();
    if(n==44){for(var p:ps){p.removeAllEffects();p.setItemSlot(EquipmentSlot.MAINHAND,ItemStack.EMPTY);}}
    if(n==42){top.theillusivec4.curios.api.CuriosApi.getCuriosInventory(a).orElseThrow(()->new AssertionError("Curios missing")).getStacksHandler("necklace").orElseThrow().getStacks().setStackInSlot(0,ItemStack.EMPTY);top.theillusivec4.curios.api.CuriosApi.getCuriosInventory(b).orElseThrow(()->new AssertionError("Curios missing")).getStacksHandler("necklace").orElseThrow().getStacks().setStackInSlot(0,item("jade_pendant"));}
   }
   // Assert mechanism expectations independently of the client snapshots.
   if(n==24||n==26)assertEffect(a,ExpansionEffects.YIN.get(),false);
   if(n==25)assertEffect(a,ExpansionEffects.YIN.get(),true);
   if(n==28||n==30)assertEffect(a,ExpansionEffects.YANG.get(),false);
   if(n==29)assertEffect(a,ExpansionEffects.YANG.get(),true);
   if(n>=32&&n<=34){if(a.getEffect(ExpansionEffects.YIN.get()).getAmplifier()!=Math.min(2,n-31)||b.getEffect(ExpansionEffects.YIN.get()).getAmplifier()!=0)throw new AssertionError("stack ownership");}
   if(n==35){assertEffect(a,ExpansionEffects.YIN.get(),false);assertEffect(a,ExpansionEffects.YANG.get(),false);assertEffect(b,ExpansionEffects.YIN.get(),true);}
   if(n==37){assertEffect(a,ExpansionEffects.THUNDER.get(),false);assertEffect(b,ExpansionEffects.THUNDER.get(),true);}
   // Curios and active-id caches update on the next normal tick. Snapshot is refreshed below by the server tick probe.
   pendingStage=n;pendingLabel=label;pendingAt=s.getTickCount();
  }
  @SubscribeEvent public static void serverTick(TickEvent.ServerTickEvent event){if(WeaponProbe.enabled()||!HOST||event.phase!=TickEvent.Phase.END||pendingStage<0)return;var s=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();if(s==null||s.getTickCount()-pendingAt<(pendingStage==43?65:pendingStage==46?35:4))return;try{int n=pendingStage;if(n==27){aDayApplied(s,true);}if(n==31){aDayApplied(s,false);}if(n>=40&&n<=42){var ps=players(s);boolean aj=com.dynasty.DynastyTrinkets.activeIds(ps.get(0)).contains("jade_pendant"),bj=com.dynasty.DynastyTrinkets.activeIds(ps.get(1)).contains("jade_pendant");if(aj!=(n==41)||bj!=(n==42))throw new AssertionError("Curios active ownership "+n+" host="+aj+" peer="+bj);}
     if(n==43){var ps=players(s);if(ps.get(0).hasEffect(ExpansionEffects.YANG.get())||!ps.get(1).hasEffect(ExpansionEffects.YANG.get())||ps.get(1).getMainHandItem().getCount()!=1)throw new AssertionError("Real peer C2S pill did not finish independently");write("server-c2s-result.json",Map.of("peerRemaining",ps.get(1).getMainHandItem().getCount(),"peerQiUntil",ps.get(1).getPersistentData().getLong("cod4QiUntil"),"hostHasYang",false,"peerHasYang",true));}var data=Map.of("stage",n,"label",pendingLabel,"serverTick",s.getTickCount(),"dayTime",s.overworld().getDayTime(),"players",players(s).stream().map(NetworkAcceptance::state).toList());write("server-stage-"+n+".json",data);write("server-stage.json",data);pendingStage=-1;}catch(Throwable ex){try{Files.writeString(OUT.resolve("server-FAIL.txt"),ex.toString());}catch(Exception ignored){}pendingStage=-1;}}
  static void aDayApplied(net.minecraft.server.MinecraftServer s,boolean yin){var a=players(s).get(0);if(s.overworld().isDay()==yin)throw new AssertionError("world daylight did not settle");var effect=yin?ExpansionEffects.YIN.get():ExpansionEffects.YANG.get();a.addEffect(new MobEffectInstance(effect,1200));assertEffect(a,effect,true);}
  static void assertEffect(ServerPlayer p,MobEffect e,boolean expected){if(p.hasEffect(e)!=expected)throw new AssertionError("native effect expectation "+ForgeRegistries.MOB_EFFECTS.getKey(e));}
 }
}
