package com.dynasty.journeyqa;

import com.google.gson.*;
import java.nio.file.*;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.*;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

/** No server-side mutations: only observer events and real connected client input/container packets. */
@Mod("dynastyjourneysurvivalqa")
public final class NaturalJourneyClient {
 static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
 static final Gson LINE=new Gson();
 static final Path OUT=Path.of(System.getProperty("dynasty.journey.survival.output"));
 static final long PROCESS_NANO=System.nanoTime();
 static volatile UUID uuid;
 static volatile String commandId="startup";
 static volatile Map<String,Object> server=Map.of();
 static final Queue<String> shots=new ConcurrentLinkedQueue<>();
 static void require(boolean b,String why){if(!b)throw new IllegalStateException(why);}
 static synchronized void write(String file,Object data) {
  try{Path temp=OUT.resolve(file+".pending");Files.writeString(temp,JSON.toJson(data)+"\n");Files.move(temp,OUT.resolve(file),StandardCopyOption.REPLACE_EXISTING);}catch(Exception e){throw new RuntimeException(e);}
 }
 static synchronized void event(String kind,Object data) {
  try{Files.writeString(OUT.resolve("native-events.jsonl"),LINE.toJson(Map.of("utc",Instant.now().toString(),"monotonicNanos",System.nanoTime()-PROCESS_NANO,"command",commandId,"kind",kind,"data",data))+"\n",StandardOpenOption.CREATE,StandardOpenOption.APPEND);}catch(Exception e){throw new RuntimeException(e);}
 }
 static String id(ItemStack s){return ForgeRegistries.ITEMS.getKey(s.getItem()).toString();}
 static List<Integer> pos(BlockPos p){return List.of(p.getX(),p.getY(),p.getZ());}
 static Map<String,Object> stack(ItemStack s){return Map.of("item",id(s),"count",s.getCount(),"damage",s.getDamageValue());}
 static Map<String,Object> player(Player p) {
  var o=new LinkedHashMap<String,Object>();o.put("uuid",p.getUUID().toString());o.put("class",p.getClass().getName());o.put("position",List.of(p.getX(),p.getY(),p.getZ()));o.put("health",p.getHealth());o.put("food",p.getFoodData().getFoodLevel());o.put("saturation",p.getFoodData().getSaturationLevel());o.put("worldTime",p.level().getGameTime());o.put("dayTime",p.level().getDayTime());o.put("dimension",p.level().dimension().location().toString());o.put("onGround",p.onGround());o.put("alive",p.isAlive());o.put("yaw",p.getYRot());o.put("pitch",p.getXRot());o.put("selected",p.getInventory().selected);o.put("main",stack(p.getMainHandItem()));o.put("flying",p.getAbilities().flying);o.put("instabuild",p.getAbilities().instabuild);o.put("noGravity",p.isNoGravity());o.put("inventory",p.getInventory().items.stream().map(NaturalJourneyClient::stack).toList());
  var menu=p.containerMenu;o.put("menuClass",menu.getClass().getName());o.put("menuId",menu.containerId);o.put("carried",stack(menu.getCarried()));o.put("slots",menu.slots.stream().map(s->Map.of("slot",s.index,"stack",stack(s.getItem()),"inventoryIndex",s.getContainerSlot())).toList());
  if(p instanceof ServerPlayer sp){o.put("gameMode",sp.gameMode.getGameModeForPlayer().getName());o.put("permissions2",sp.hasPermissions(2));o.put("quests",quests(sp));}
  return o;
 }
 static Object quests(ServerPlayer p) {
  try {
   Class<?> ft=Class.forName("dev.ftb.mods.ftbquests.quest.ServerQuestFile"), tt=Class.forName("dev.ftb.mods.ftbquests.quest.TeamData"), qt=Class.forName("dev.ftb.mods.ftbquests.quest.Quest"),ot=Class.forName("dev.ftb.mods.ftbquests.quest.QuestObject");
   Object f=ft.getField("INSTANCE").get(null),t=tt.getMethod("get",Player.class).invoke(null,p);if(t==null)return Map.of("ready",false);
   var out=new ArrayList<Object>();
   for(String s:List.of("1000000000010000","1000000000010001","1000000000010002","1000000000010003","1000000000010004","1000000000010020","1000000000010021","1000000000000000","1000000000000001","1000000000000002","1000000000000003")) {
    Object q=ft.getMethod("getQuest",long.class).invoke(f,Long.parseUnsignedLong(s,16));
    out.add(Map.of("id",s,"completed",tt.getMethod("isCompleted",ot).invoke(t,q),"dependenciesComplete",tt.getMethod("areDependenciesComplete",qt).invoke(t,q)));
   }return out;
  }catch(Exception e){return Map.of("error",e.toString());}
 }
 static boolean owned(Player p){return p instanceof ServerPlayer&&p.getUUID().equals(uuid);}
 @Mod.EventBusSubscriber(modid="dynastyjourneysurvivalqa") public static class Observer {
  @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e){if(e.phase!=TickEvent.Phase.END||uuid==null)return;var s=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();if(s==null)return;var p=s.getPlayerList().getPlayer(uuid);if(p!=null&&p.tickCount%10==0){server=player(p);if(p.tickCount%20==0)event("server_observation",server);}}
  @SubscribeEvent public static void block(BlockEvent.BreakEvent e){if(owned(e.getPlayer()))event("native_block_break",Map.of("position",pos(e.getPos()),"block",ForgeRegistries.BLOCKS.getKey(e.getState().getBlock()).toString(),"player",player(e.getPlayer())));}
  @SubscribeEvent public static void pickup(PlayerEvent.ItemPickupEvent e){if(owned(e.getEntity()))event("native_item_pickup",Map.of("original",stack(e.getOriginalEntity().getItem()),"picked",stack(e.getStack()),"entityUUID",e.getOriginalEntity().getUUID().toString(),"position",List.of(e.getOriginalEntity().getX(),e.getOriginalEntity().getY(),e.getOriginalEntity().getZ()),"player",player(e.getEntity())));}
  @SubscribeEvent public static void craft(PlayerEvent.ItemCraftedEvent e){if(owned(e.getEntity()))event("native_item_crafted",Map.of("output",stack(e.getCrafting()),"player",player(e.getEntity())));}
  @SubscribeEvent public static void smelt(PlayerEvent.ItemSmeltedEvent e){if(owned(e.getEntity()))event("native_item_smelted",Map.of("output",stack(e.getSmelting()),"player",player(e.getEntity())));}
  @SubscribeEvent public static void place(BlockEvent.EntityPlaceEvent e){if(e.getEntity() instanceof Player p&&owned(p))event("native_block_place",Map.of("position",pos(e.getPos()),"block",ForgeRegistries.BLOCKS.getKey(e.getPlacedBlock().getBlock()).toString()));}
  @SubscribeEvent public static void drop(EntityJoinLevelEvent e){if(!e.getLevel().isClientSide()&&e.getEntity() instanceof net.minecraft.world.entity.item.ItemEntity item&&uuid!=null){var p=e.getLevel().getPlayerByUUID(uuid);if(p!=null&&p.distanceToSqr(item)<1024)event("natural_item_entity",Map.of("stack",stack(item.getItem()),"entityUUID",item.getUUID().toString(),"position",List.of(item.getX(),item.getY(),item.getZ())));}}
 }
 @Mod.EventBusSubscriber(modid="dynastyjourneysurvivalqa",value=net.minecraftforge.api.distmarker.Dist.CLIENT) public static class Client {
  static boolean started,ready,done;static int ticks,age;static String last="";static JsonObject action;static Map<String,Object> before;static BlockPos target;static String originalBlock;static final Deque<int[]> clicks=new ArrayDeque<>();static final Map<String,Long> tickCategories=new LinkedHashMap<>();
  static void release(Minecraft m){for(var k:List.of(m.options.keyUp,m.options.keyDown,m.options.keyLeft,m.options.keyRight,m.options.keyJump,m.options.keyAttack,m.options.keyUse,m.options.keyShift,m.options.keySprint))k.setDown(false);if(m.gameMode!=null)m.gameMode.stopDestroyBlock();}
  static void look(Minecraft m,Vec3 v){var d=v.subtract(m.player.getEyePosition());m.player.setYRot((float)Math.toDegrees(Math.atan2(-d.x,d.z)));m.player.setXRot((float)-Math.toDegrees(Math.atan2(d.y,Math.sqrt(d.x*d.x+d.z*d.z))));}
  static BlockPos block(JsonArray a){return new BlockPos(a.get(0).getAsInt(),a.get(1).getAsInt(),a.get(2).getAsInt());}
  static Map<String,Object> state(Minecraft m,boolean surroundings) {
   var s=new LinkedHashMap<String,Object>();s.put("utc",Instant.now().toString());s.put("monotonicNanos",System.nanoTime()-PROCESS_NANO);s.put("clientTick",ticks);s.put("paused",m.isPaused());s.put("screen",m.screen==null?"none":m.screen.getClass().getName());s.put("tickCategories",new LinkedHashMap<>(tickCategories));s.put("server",server);
   if(m.player!=null){s.put("client",player(m.player));s.put("camera",m.options.getCameraType().name());s.put("cameraEntityUUID",m.getCameraEntity()==null?"none":m.getCameraEntity().getUUID().toString());if(surroundings)s.put("visible",visible(m));}
   return s;
  }
  static Object visible(Minecraft m) {
   var list=new ArrayList<Object>();var eye=m.player.getEyePosition();BlockPos center=m.player.blockPosition();
   for(BlockPos bp:BlockPos.betweenClosed(center.offset(-10,-4,-10),center.offset(10,6,10))){var b=m.level.getBlockState(bp);if(b.isAir()||b.getCollisionShape(m.level,bp).isEmpty())continue;String id=ForgeRegistries.BLOCKS.getKey(b.getBlock()).toString();if(id.contains("leaves"))continue;var ray=m.level.clip(new ClipContext(eye,bp.getCenter(),ClipContext.Block.OUTLINE,ClipContext.Fluid.NONE,m.player));if(ray.getBlockPos().equals(bp)&&ray.getType()==HitResult.Type.BLOCK)list.add(Map.of("position",pos(bp),"block",id,"distance",eye.distanceTo(ray.getLocation()),"face",ray.getDirection().getName()));}
   return list;
  }
  static void finish(Minecraft m,String outcome){release(m);var after=state(m,true);write(commandId+"-result.json",Map.of("command",action,"outcome",outcome,"before",before,"after",after));shots.add(commandId);action=null;write("current-state.json",after);}
  static void init(Minecraft m,JsonObject a) throws Exception {
   release(m);m.options.setCameraType(CameraType.FIRST_PERSON);action=a;commandId=a.get("id").getAsString();age=0;before=state(m,false);String op=a.get("op").getAsString();event("client_command",Map.of("command",a,"before",before));
   if(op.equals("finish")){write("FINISHED.json",state(m,false));done=true;m.stop();return;}
   if(op.equals("pause")){m.setScreen(new PauseScreen(true));finish(m,"PAUSED_WITH_CLOCK_EXCLUDED");return;}
   if(op.equals("observe")){finish(m,"OBSERVED_ONLY");return;}
   if(op.equals("resume")){m.setScreen(null);finish(m,"RESUMED");return;}
   require(m.player.isAlive(),"Native survival player died; no QA respawn/heal");require(!m.player.getAbilities().instabuild&&!m.player.getAbilities().flying&&!m.player.isNoGravity(),"Unmodified survival abilities");
   if(op.equals("mine")||op.equals("use_block")){m.setScreen(null);target=block(a.getAsJsonArray("position"));look(m,target.getCenter());originalBlock=ForgeRegistries.BLOCKS.getKey(m.level.getBlockState(target).getBlock()).toString();}
   if(op.equals("move")||op.equals("look")){m.setScreen(null);}
   if(op.equals("select")){int slot=a.get("slot").getAsInt();require(slot>=0&&slot<9,"Only actual hotbar slots");m.player.getInventory().selected=slot;}
   if(op.equals("craft")){
    if(m.player.containerMenu instanceof InventoryMenu)m.setScreen(new InventoryScreen(m.player));
    var menu=m.player.containerMenu;require(menu instanceof InventoryMenu||menu instanceof CraftingMenu,"Open actual crafting menu required");int width=menu instanceof InventoryMenu?2:3;require(menu.getCarried().isEmpty(),"Cursor empty before craft");clicks.clear();
    for(var slot:menu.slots)if(slot.index>=1&&slot.index<=width*width)require(slot.getItem().isEmpty(),"Existing grid must be empty");
    Map<Integer,Integer> remaining=new HashMap<>();
    for(var entry:a.getAsJsonArray("grid")){
     var cell=entry.getAsJsonObject();int destination=cell.get("slot").getAsInt();String wanted=cell.get("item").getAsString();require(destination>=1&&destination<=width*width,"Actual grid slot");int source=-1;
     for(var slot:menu.slots)if(slot.container==m.player.getInventory()&&id(slot.getItem()).equals(wanted)&&remaining.getOrDefault(slot.index,slot.getItem().getCount())>0){source=slot.index;remaining.put(source,remaining.getOrDefault(source,slot.getItem().getCount())-1);break;}
     require(source>=0,"Natural inventory lacks "+wanted);clicks.add(new int[]{source,0,0});clicks.add(new int[]{destination,1,0});clicks.add(new int[]{source,0,0});
    }
    clicks.add(new int[]{0,0,1});
   }
   if(op.equals("slot_click")){var menu=m.player.containerMenu;int slot=a.get("slot").getAsInt();require(slot>=0&&slot<menu.slots.size(),"Actual menu slot");m.gameMode.handleInventoryMouseClick(menu.containerId,slot,a.has("button")?a.get("button").getAsInt():0,ClickType.valueOf(a.has("type")?a.get("type").getAsString():"PICKUP"),m.player);}
   if(op.equals("close_menu")){m.player.closeContainer();}
   if(op.equals("submit_task")){Class.forName("dev.ftb.mods.ftbquests.net.SubmitTaskMessage").getConstructor(long.class).newInstance(Long.parseUnsignedLong(a.get("task").getAsString(),16)).getClass().getMethod("sendToServer").invoke(Class.forName("dev.ftb.mods.ftbquests.net.SubmitTaskMessage").getConstructor(long.class).newInstance(Long.parseUnsignedLong(a.get("task").getAsString(),16)));}
  }
  @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){if(e.phase!=TickEvent.Phase.END||done)return;Minecraft m=Minecraft.getInstance();ticks++;
   try {
    if(!started&&m.screen instanceof TitleScreen){require(m.gameDirectory.getCanonicalPath().equals(System.getProperty("dynasty.journey.survival.instance")),"Private survival profile");started=true;m.getWindow().setTitle("COD4 Natural Survival - no QA materials");if(Files.isDirectory(m.gameDirectory.toPath().resolve("saves/natural-journey-20261023"))){m.createWorldOpenFlows().loadLevel(new TitleScreen(),"natural-journey-20261023");return;}m.createWorldOpenFlows().createFreshLevel("natural-journey-20261023",new LevelSettings("COD4 Natural Survival",GameType.SURVIVAL,false,Difficulty.NORMAL,false,new GameRules(),WorldDataConfiguration.DEFAULT),new WorldOptions(20261023L,true,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.NORMAL).createWorldDimensions());return;}
    if(m.player==null||m.level==null||m.gameMode==null)return;uuid=m.player.getUUID();
    String cat=m.isPaused()?"paused":action==null?"idle_or_inspection":Set.of("move","mine","use_block").contains(action.get("op").getAsString())?"active_world_input":"native_menu_or_control";tickCategories.merge(cat,1L,Long::sum);
    if(!ready){if(server.isEmpty())return;ready=true;write("READY.json",state(m,true));shots.add("initial-spawn");}
    if(ticks%20==0)write("live-state.json",state(m,false));
    if(action==null){Path p=OUT.resolve("command.json");if(Files.exists(p)){String raw=Files.readString(p);if(!raw.equals(last)){last=raw;init(m,JsonParser.parseString(raw).getAsJsonObject());}}return;}
    age++;String op=action.get("op").getAsString();
    if(op.equals("look")){look(m,new Vec3(action.get("x").getAsDouble(),action.get("y").getAsDouble(),action.get("z").getAsDouble()));if(age>=3)finish(m,"LOOK_INPUT");}
    else if(op.equals("move")){double x=action.get("x").getAsDouble(),z=action.get("z").getAsDouble();look(m,new Vec3(x,m.player.getEyeY(),z));double dist=Math.hypot(x-m.player.getX(),z-m.player.getZ());m.options.keyUp.setDown(dist>0.7);m.options.keyJump.setDown(m.player.horizontalCollision||m.player.isInWater()||(action.has("jump")&&action.get("jump").getAsBoolean()));if(dist<=0.7||age>=Math.min(200,action.get("ticks").getAsInt()))finish(m,dist<=0.7?"REACHED_BY_NATIVE_MOVEMENT":"MOVEMENT_SEGMENT_ENDED");}
    else if(op.equals("mine")){look(m,target.getCenter());var ray=m.player.pick(m.gameMode.getPickRange(),1,false);if(!ForgeRegistries.BLOCKS.getKey(m.level.getBlockState(target).getBlock()).toString().equals(originalBlock)){finish(m,"NATIVE_BLOCK_CHANGED");return;}require(ray instanceof BlockHitResult hit&&hit.getBlockPos().equals(target),"Target must be in native raycast/reach: "+target+" actual="+ray.getType()+":"+((ray instanceof BlockHitResult b)?b.getBlockPos():ray.getLocation()));m.options.keyAttack.setDown(true);if(age>=300)finish(m,"MINE_TIMEOUT_NOT_CLAIMED");}
    else if(op.equals("use_block")){look(m,target.getCenter());var ray=m.player.pick(m.gameMode.getPickRange(),1,false);require(ray instanceof BlockHitResult hit&&hit.getBlockPos().equals(target),"Use block real reach/raycast");if(age==3){event("native_client_use_block",Map.of("hit",pos(target),"held",stack(m.player.getMainHandItem())));m.gameMode.useItemOn(m.player,InteractionHand.MAIN_HAND,(BlockHitResult)ray);}if(age>=12)finish(m,"NATIVE_USE_PACKET_SENT");}
    else if(op.equals("craft")){if(age%4==0&&!clicks.isEmpty()){int[] click=clicks.removeFirst();var menu=m.player.containerMenu;if(click[0]==0)require(id(menu.getSlot(0).getItem()).equals(action.get("expect").getAsString()),"Native recipe output must match requested existing recipe");m.gameMode.handleInventoryMouseClick(menu.containerId,click[0],click[1],click[2]==1?ClickType.QUICK_MOVE:ClickType.PICKUP,m.player);event("native_container_click",Map.of("slot",click[0],"button",click[1],"type",click[2],"menu",menu.containerId));}if(clicks.isEmpty()&&age%4==3)finish(m,"NATIVE_CRAFT_CLICKS_COMPLETE");}
    else if(age>=12)finish(m,"NATIVE_CONTROL_COMPLETE");
   }catch(Throwable ex){release(m);event("QA_INPUT_FAILURE",Map.of("error",ex.toString()));write(commandId+"-FAIL.json",Map.of("error",ex.toString(),"state",state(m,true)));action=null;m.setScreen(new PauseScreen(true));}
  }
  @SubscribeEvent public static void render(TickEvent.RenderTickEvent e){if(e.phase!=TickEvent.Phase.END||shots.isEmpty())return;var m=Minecraft.getInstance();String label=shots.poll();try(var pixels=Screenshot.takeScreenshot(m.getMainRenderTarget())){pixels.writeToFile(OUT.resolve(label+".png"));}catch(Exception ex){event("screenshot_error",Map.of("label",label,"error",ex.toString()));}}
 }
}
