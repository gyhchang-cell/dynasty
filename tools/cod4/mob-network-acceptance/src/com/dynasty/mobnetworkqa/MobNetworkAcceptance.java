package com.dynasty.mobnetworkqa;
import com.google.gson.*;
import com.dynasty.expansion.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.phys.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import java.nio.file.*;
import java.util.*;

@Mod("dynastymobnetworkqa")
public class MobNetworkAcceptance {
 static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
 static final Path OUT=Path.of(System.getProperty("dynasty.networkqa.output"));
 static final String ROLE=System.getProperty("dynasty.networkqa.role");
 static final boolean HOST=ROLE.equals("host");
 static final boolean FULL=System.getProperty("dynasty.networkqa.suite","states").startsWith("fullpack");
 static final boolean EXPLORE_ONLY=System.getProperty("dynasty.networkqa.suite","").equals("fullpack-explore");
 static int fx,fy,fz;static Vec3 walkA,walkB;static int damageEvents;static Set<UUID> effectivePlayerAttackers=new HashSet<>();
 static void write(String f,Object o)throws Exception{Path t=OUT.resolve(f+".tmp");Files.writeString(t,JSON.toJson(o));Files.move(t,OUT.resolve(f),StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);}
 static Map<String,Object> map(Object... pairs){var m=new LinkedHashMap<String,Object>();for(int i=0;i<pairs.length;i+=2)m.put((String)pairs[i],pairs[i+1]);return m;}
 static boolean exists(String f){return Files.exists(OUT.resolve(f));}
 static void marker(String f)throws Exception{Files.writeString(OUT.resolve(f),"ready");}
 static ItemStack item(String id,int n){return new ItemStack(Objects.requireNonNull(ForgeRegistries.ITEMS.getValue(new ResourceLocation(id.contains(":")?id:"dynasty:"+id))),n);}
 static net.minecraft.server.MinecraftServer server;
 static SecondaryMob mob;static ServerPlayer a,b;static List<ServerPlayer> ps;
 static List<Op> ops=new ArrayList<>();static int op=-1,start;static boolean live,complete,serverReady,readySent;static Set<String> explorationAnchors=new HashSet<>();
 static UUID actor;static int deathEvents,attackEvents,interactEvents;static List<Map<String,Object>> dropEvents=new ArrayList<>();
 static String stolenToken=""; static List<Map<String,Object>> nativeInputs=new ArrayList<>();static Map<String,Integer> loot=new TreeMap<>();static Map<String,Object> before;
 interface Work{void run()throws Exception;}
 interface Check{Map<String,Object> run()throws Exception;}
 record Op(String name,String host,String peer,int waitTicks,Work setup,Check check){}
 static Map<String,Object> check(String key,boolean pass){return Map.of(key,pass);}
 static void add(String name,String host,String peer,int wait,Work setup,Check check){ops.add(new Op(name,host,peer,wait,setup,check));}
 static CompoundTag saved(){return mob.saveWithoutId(new CompoundTag());}
 static int count(ServerPlayer p,String id){return p.getInventory().items.stream().filter(s->ForgeRegistries.ITEMS.getKey(s.getItem()).toString().equals(id)).mapToInt(ItemStack::getCount).sum();}
 static Map<String,Integer> inventory(ServerPlayer p){var m=new TreeMap<String,Integer>();for(var s:p.getInventory().items)if(!s.isEmpty())m.merge(s.save(new CompoundTag()).getString("id")+(s.hasTag()?s.getTag().toString():""),s.getCount(),Integer::sum);return m;}
 static Map<String,Object> player(ServerPlayer p){return Map.of("name",p.getGameProfile().getName(),"uuid",p.getUUID().toString(),"class",p.getClass().getName(),"mode",p.gameMode.getGameModeForPlayer().toString(),"inventory",inventory(p),"health",p.getHealth(),"onGround",p.onGround(),"pos",p.position().toString(),"siteState",EquipmentBehaviors.saved(p).toString());}
 static Map<String,Object> snapshot(){var m=new LinkedHashMap<String,Object>();m.put("serverTick",server.getTickCount());m.put("players",ps.stream().map(MobNetworkAcceptance::player).toList());m.put("mob",mob==null?"none":Map.of("uuid",mob.getUUID().toString(),"type",mob.spec.id(),"alive",mob.isAlive(),"health",mob.getHealth(),"target",mob.getTarget()==null?"none":mob.getTarget().getUUID().toString(),"animation",mob.animation(),"saved",saved().toString(),"noAI",mob.isNoAi()));if(FULL)m.put("naturalWorld",map("dimension",a.level().dimension().location().toString(),"biome",server.overworld().getBiome(a.blockPosition()).unwrapKey().map(k->k.location().toString()).orElse("unknown"),"anchor",List.of(fx,fy,fz),"effectiveDamageEvents",damageEvents,"loadedChunks",server.overworld().getChunkSource().getLoadedChunksCount()));m.put("nativeInputs",List.copyOf(nativeInputs));m.put("effectivePlayerAttackers",effectivePlayerAttackers.stream().map(UUID::toString).sorted().toList());m.put("attackEvents",attackEvents);m.put("interactEvents",interactEvents);m.put("deathEvents",deathEvents);m.put("drops",List.copyOf(dropEvents));m.put("lootLedger",new TreeMap<>(loot));return m;}
 static void hand(ServerPlayer p,String id,int n){p.getInventory().selected=0;var stack=item(id,n);stack.getOrCreateTag().putString("MobQaToken",p.getGameProfile().getName()+"-"+op+"-"+id);p.setItemSlot(EquipmentSlot.MAINHAND,stack);p.containerMenu.broadcastChanges();}
 static void position(){if(FULL){a.teleportTo(server.overworld(),fx-1,fy,fz,0,10);b.teleportTo(server.overworld(),fx+1,fy,fz,0,10);if(mob!=null){mob.teleportTo(fx,fy,fz+2);mob.setDeltaMovement(Vec3.ZERO);mob.getNavigation().stop();}return;}a.teleportTo(server.overworld(),-1,-60,0,0,10);b.teleportTo(server.overworld(),1,-60,0,0,10);mob.teleportTo(0,-60,2);mob.setDeltaMovement(Vec3.ZERO);mob.getNavigation().stop();}
 static void clean(){if(FULL&&mob!=null)mob.discard();var w=server.overworld();for(var e:List.copyOf(w.getEntitiesOfClass(SecondaryMob.class,new AABB(-40,-65,-40,40,0,40))))e.discard();for(var e:w.getEntitiesOfClass(ItemEntity.class,new AABB(-40,-65,-40,40,0,40)))e.discard();for(var p:ps){p.setGameMode(GameType.SURVIVAL);p.getInventory().clearContent();p.removeAllEffects();p.getAttribute(Attributes.MAX_HEALTH).setBaseValue(100000);p.setHealth(100000);p.getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(1);p.getFoodData().setFoodLevel(20);p.getAbilities().invulnerable=false;p.onUpdateAbilities();}deathEvents=attackEvents=interactEvents=0;dropEvents.clear();loot.clear();nativeInputs.clear();effectivePlayerAttackers.clear();}
 static void spawn(String id){clean();mob=SecondaryMobs.TYPES.get(id).get().create(server.overworld());actor=mob.getUUID();mob.setPersistenceRequired();mob.moveTo(FULL?fx:0,FULL?fy:-60,FULL?fz+2:2,180,0);server.overworld().addFreshEntity(mob);position();}
 static boolean target(ServerPlayer p){return mob.getTarget()==p;}
 static void view(){if(mob!=null)mob.setNoAi(true);position();}
 static void killSetup(){
 var st=saved().getCompound("Cod4Stolen");stolenToken=st.getCompound("tag").getString("MobQaToken");
 var table=server.getLootData().getLootTable(mob.getLootTable());
 var params=new net.minecraft.world.level.storage.loot.LootParams.Builder(server.overworld()).withParameter(net.minecraft.world.level.storage.loot.parameters.LootContextParams.THIS_ENTITY,mob).withParameter(net.minecraft.world.level.storage.loot.parameters.LootContextParams.ORIGIN,mob.position()).withParameter(net.minecraft.world.level.storage.loot.parameters.LootContextParams.DAMAGE_SOURCE,a.damageSources().playerAttack(a)).withParameter(net.minecraft.world.level.storage.loot.parameters.LootContextParams.LAST_DAMAGE_PLAYER,a).withParameter(net.minecraft.world.level.storage.loot.parameters.LootContextParams.KILLER_ENTITY,a).withParameter(net.minecraft.world.level.storage.loot.parameters.LootContextParams.DIRECT_KILLER_ENTITY,a).create(net.minecraft.world.level.storage.loot.parameters.LootContextParamSets.ENTITY);
 long seed=1;while(seed<=192&&table.getRandomItems(params,seed).isEmpty())seed++;var n=saved();n.putString("DeathLootTable",mob.getLootTable().toString());n.putLong("DeathLootTableSeed",seed);mob.load(n);
 view();mob.setHealth(1);mob.invulnerableTime=0;for(var p:ps){p.getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(100000);p.getInventory().clearContent();} }
 static boolean ledger(){var total=new TreeMap<String,Integer>();for(var p:ps)inventory(p).forEach((k,v)->total.merge(k,v,Integer::sum));for(var e:server.overworld().getEntitiesOfClass(ItemEntity.class,new AABB(-40,-65,-40,40,0,40))){var s=e.getItem();String k=s.save(new CompoundTag()).getString("id")+(s.hasTag()?s.getTag().toString():"");total.merge(k,s.getCount(),Integer::sum);}return total.equals(loot);}
 static void deathOps(String id){
  add(id+"/simultaneous-C2S-kill","attack","attack",15,()->killSetup(),()->Map.of("exactly_one_native_death_event",deathEvents==1&&!mob.isAlive(),"stolen_token_returned_once",stolenToken.isEmpty()||loot.entrySet().stream().filter(e->e.getKey().contains(stolenToken)).mapToInt(Map.Entry::getValue).sum()==1));
  add(id+"/corpse-no-repeat-after35ticks","none","none",35,()->{},()->check("corpse_does_not_pay_again",deathEvents==1));
  add(id+"/both-pick-up","none","none",45,()->{for(var p:ps)p.teleportTo(server.overworld(),mob.getX(),-60,mob.getZ(),0,0);},()->Map.of("one_death_event",deathEvents==1,"created_equals_both_inventories_plus_remaining_world",ledger(),"positive_loot_observed",!loot.isEmpty()));
 }
 static void build(){
  if(FULL){fullpack();return;}
  if(System.getProperty("dynasty.networkqa.suite", "states").equals("neutral")){freshNeutral();return;}
  if(System.getProperty("dynasty.networkqa.suite", "states").equals("reactions")){supplement();return;}
  for(var spec:SecondaryMobs.SPECS){String id=spec.id();
   add(id+"/natural-host-target","none","none",100,()->{spawn(id);a.teleportTo(server.overworld(),0,-60,0,0,0);b.teleportTo(server.overworld(),5,-60,0,0,0);},()->check("natural_target_definition",spec.neutral()?mob.getTarget()==null:target(a)));
   add(id+"/retarget-peer","none","none",100,()->{a.setGameMode(GameType.SPECTATOR);},()->check("independent_peer_target",spec.neutral()?mob.getTarget()==null:target(b)));
   add(id+"/world-view","view","view",25,()->{a.setGameMode(GameType.SURVIVAL);view();},()->check("two_real_players_and_mob_exist",ps.size()==2&&mob.isAlive()));
   add(id+"/native-attacked","attack","none",12,()->{mob.setNoAi(false);position();mob.setHealth(mob.getMaxHealth());mob.invulnerableTime=0;},()->{boolean flee=Set.of("famished_refugee","herb_picker","snail_maiden").contains(id);return Map.of("native_attack_event",attackEvents>=1,"actual_health_reduced",mob.getHealth()<mob.getMaxHealth(),"neutral_flee_recorded",!spec.neutral()||saved().getInt("Cod4Flee")>0,"noncombatant_clears_target",!flee||mob.getTarget()==null);});
   add(id+"/shell-window-settle","none","none",60,()->mob.setNoAi(true),()->check("alive_before_death",mob.isAlive()));
   deathOps(id);
  }
  specials();
 }
 static void naturalAnchor(int x,int z){
  var w=server.overworld();boolean found=false;var sampled=new ArrayList<Object>();
  search:for(int radius=0;radius<=1024;radius+=16)for(int dx=-radius;dx<=radius;dx+=16)for(int dz=-radius;dz<=radius;dz+=16){if(Math.abs(dx)!=radius&&Math.abs(dz)!=radius)continue;int xx=x+dx,zz=z+dz;int y=w.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,xx,zz);boolean safe=true;
   for(int[] d:new int[][]{{-1,0},{1,0},{0,2},{0,0}}){var p=new BlockPos(xx+d[0],y-1,zz+d[1]);if(!w.getBlockState(p).isSolidRender(w,p)||!w.getFluidState(p).isEmpty()||!w.getBlockState(p.above()).isAir()||!w.getBlockState(p.above(2)).isAir())safe=false;}
   if(sampled.size()<80)sampled.add(map("x",xx,"y",y,"z",zz,"below",w.getBlockState(new BlockPos(xx,y-1,zz)).toString(),"safe",safe));
   if(safe){fx=xx;fy=y;fz=zz;found=true;break search;}
  }try{write("natural-anchor-"+x+"-"+z+".json",map("found",found,"anchor",List.of(fx,fy,fz),"sample",sampled));}catch(Exception ex){throw new RuntimeException(ex);}if(!found)throw new AssertionError("No natural open ground near "+x+","+z);
 }
 static void fullpack(){
  var origin=server.overworld().getSharedSpawnPos();naturalAnchor(origin.getX(),origin.getZ());
  try{write("loaded-mods.json",net.minecraftforge.fml.ModList.get().getMods().stream().map(m->Map.of("id",m.getModId(),"version",m.getVersion().toString())).toList());}catch(Exception e){throw new RuntimeException(e);}
  for(String id:EXPLORE_ONLY?List.<String>of():List.of("bandit_thug","gray_wolf","paper_money_ghost","bat_demon")){
   add("fullpack/"+id+"/natural-terrain-fixture","view","view",40,()->{spawn(id);view();for(var p:ps){hand(p,"minecraft:iron_sword",1);p.setItemSlot(EquipmentSlot.CHEST,new ItemStack(Items.IRON_CHESTPLATE));}damageEvents=0;},()->check("two_players_and_fixture_on_unmodified_terrain",ps.size()==2&&mob.isAlive()));
   add("fullpack/"+id+"/host-native-combat","attack","none",20,()->{mob.setNoAi(false);position();mob.invulnerableTime=0;},()->Map.of("native_attack",attackEvents>=1,"mob_received_damage",mob.getHealth()<mob.getMaxHealth(),"host_effective_damage",effectivePlayerAttackers.contains(a.getUUID())));
   add("fullpack/"+id+"/peer-native-combat","none","attack",20,()->{position();mob.invulnerableTime=0;},()->Map.of("both_native_attackers",nativeInputs.stream().filter(v->v.get("kind").equals("attack")).map(v->v.get("player")).distinct().count()==2,"mob_alive_for_ai",mob.isAlive(),"both_players_effective_damage",effectivePlayerAttackers.contains(a.getUUID())&&effectivePlayerAttackers.contains(b.getUUID())));
   add("fullpack/"+id+"/native-ai-combat","none","none",120,()->{position();mob.setNoAi(false);damageEvents=0;},()->Map.of("actual_effective_damage_observed",damageEvents>0,"both_players_survive",a.isAlive()&&b.isAlive()));
   add("fullpack/"+id+"/battle-world-view","view","view",35,()->view(),()->check("live_render_fixture",mob.isAlive()));
   add("fullpack/"+id+"/native-kill","attack","none",25,()->{view();mob.setHealth(1);mob.invulnerableTime=0;for(var p:ps)p.getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(100000);},()->Map.of("one_native_death",deathEvents==1&&!mob.isAlive(),"both_prior_effective_attackers",effectivePlayerAttackers.contains(a.getUUID())&&effectivePlayerAttackers.contains(b.getUUID()),"designated_host_killer",dropEvents.size()==1&&dropEvents.get(0).get("killer").equals(a.getUUID().toString())));
   add("fullpack/"+id+"/corpse-no-repeat","none","none",40,()->{},()->check("no_duplicate_death",deathEvents==1));
  }
  for(int offset:EXPLORE_ONLY?List.of(256,512):List.of(0,256,512)){
   add("fullpack/explore-"+offset+"/natural-scene","view","view",50,()->{naturalAnchor(origin.getX()+offset,origin.getZ()+offset/2);if(!explorationAnchors.add(fx+","+fy+","+fz))throw new AssertionError("Duplicate exploration anchor");clean();mob=null;view();},()->Map.of("natural_surface",fy>server.overworld().getMinBuildHeight(),"two_players",ps.size()==2));
   add("fullpack/explore-"+offset+"/native-walk","walk","walk",180,()->{walkA=a.position();walkB=b.position();},()->Map.of("host_native_movement",a.position().subtract(walkA).horizontalDistance()>5&&a.onGround(),"peer_native_movement",b.position().subtract(walkB).horizontalDistance()>5&&b.onGround(),"both_survival",a.gameMode.getGameModeForPlayer()==GameType.SURVIVAL&&b.gameMode.getGameModeForPlayer()==GameType.SURVIVAL,"both_alive",a.isAlive()&&b.isAlive(),"distinct_exploration_anchors",explorationAnchors.size()==offset/256+(EXPLORE_ONLY?0:1)));
   add("fullpack/explore-"+offset+"/scene-after-walk","view","view",40,()->view(),()->check("both_clients_still_connected",server.getPlayerList().getPlayerCount()==2));
  }
 }
 static void freshNeutral(){
  for(var spec:SecondaryMobs.SPECS)if(spec.neutral())for(boolean host:List.of(true,false)){String id=spec.id(),label=id+"/fresh-"+(host?"host":"peer");
   add(label+"-fixture","view","view",15,()->{spawn(id);view();},()->check("fresh_actor_has_no_target",mob.getTarget()==null));
   add(label+"-C2S-hit",host?"attack":"none",host?"none":"attack",12,()->{mob.setNoAi(false);mob.setHealth(mob.getMaxHealth()*.2F);mob.invulnerableTime=0;position();},()->Map.of("one_native_attack",attackEvents==1,"flee",saved().getInt("Cod4Flee")>0,"fresh_reactive_neutral_targets_own_attacker",!Set.of("night_watchman","jingwei_bird").contains(id)||target(host?a:b),"passive_neutrals_no_player_damage",!Set.of("famished_refugee","herb_picker","snail_maiden","swindler").contains(id)||(a.getHealth()==100000&&b.getHealth()==100000)));
   add(label+"-synced","snapshot","snapshot",15,()->{var data=saved();mob.load(data);mob.setTarget(null);view();},()->{var c=new LinkedHashMap<String,Object>();for(String role:List.of("host","peer")){var j=JsonParser.parseString(Files.readString(OUT.resolve(role+"-input-"+op+".json"))).getAsJsonObject();c.put(role+"_native_entity_health_synced",Math.abs(j.getAsJsonObject("mobState").get("health").getAsFloat()-mob.getHealth())<.01);}return c;});
  }
 }
 static void supplement(){
  for(var spec:SecondaryMobs.SPECS){String id=spec.id();
   add(id+"/supplement-fixture","view","view",25,()->{spawn(id);view();},()->check("fixture",true));
   add(id+"/low-health-host-C2S","attack","none",12,()->{mob.setNoAi(false);position();mob.setHealth(mob.getMaxHealth()*.2F);mob.invulnerableTime=0;},()->Map.of("flee_after_native_hit",saved().getInt("Cod4Flee")>0,"native_attack_received",attackEvents>=1,"noncombatant_no_player_damage",!Set.of("famished_refugee","herb_picker","snail_maiden","swindler").contains(id)||(a.getHealth()==100000&&b.getHealth()==100000),"noncombatant_target_cleared",!Set.of("famished_refugee","herb_picker","snail_maiden").contains(id)||mob.getTarget()==null,"provoked_neutral_target",!Set.of("night_watchman","jingwei_bird").contains(id)||target(a)));
   add(id+"/natural-shell-and-flee-wait","none","none",60,()->mob.setNoAi(true),()->check("alive",mob.isAlive()));
   add(id+"/low-health-peer-C2S","none","attack",12,()->{mob.setNoAi(false);position();mob.setHealth(mob.getMaxHealth()*.2F);mob.invulnerableTime=0;},()->Map.of("flee_after_peer_hit",saved().getInt("Cod4Flee")>0,"both_native_attacks_received",attackEvents>=2,"noncombatant_no_player_damage",!Set.of("famished_refugee","herb_picker","snail_maiden","swindler").contains(id)||(a.getHealth()==100000&&b.getHealth()==100000),"noncombatant_target_cleared",!Set.of("famished_refugee","herb_picker","snail_maiden").contains(id)||mob.getTarget()==null,"provoked_neutral_existing_target_retained",!Set.of("night_watchman","jingwei_bird").contains(id)||mob.getTarget()!=null));
   add(id+"/both-clients-observe-health","snapshot","snapshot",15,()->{var data=saved();mob.load(data);mob.setTarget(null);view();},()->{var c=new LinkedHashMap<String,Object>();for(String role:List.of("host","peer")){var j=JsonParser.parseString(Files.readString(OUT.resolve(role+"-input-"+op+".json"))).getAsJsonObject();c.put(role+"_native_entity_health_synced",Math.abs(j.getAsJsonObject("mobState").get("health").getAsFloat()-mob.getHealth())<.01);c.put(role+"_both_players_tracked",j.getAsJsonArray("localPlayers").size()==2);}return c;});
  }
  add("swindler-followup/setup","view","view",25,()->{spawn("swindler");view();hand(a,"copper_coin",3);hand(b,"copper_coin",3);},()->check("fixture",true));
  add("swindler-followup/injured","interact","none",12,()->{},()->check("stage1",saved().getInt("Cod4Deception")==1));
  add("swindler-followup/payment","interact","none",12,()->{},()->Map.of("stage2",saved().getInt("Cod4Deception")==2,"paid_one",count(a,"dynasty:copper_coin")==2,"peer_not_charged",count(b,"dynasty:copper_coin")==3,"fake_medicine",count(a,"minecraft:dead_bush")==1));
  add("swindler-followup/other-customer-rejected","none","sneak-interact",12,()->{var fake=a.getInventory().items.stream().filter(s->s.is(Items.DEAD_BUSH)).findFirst().orElseThrow().copy();b.setItemSlot(EquipmentSlot.MAINHAND,fake);},()->check("only_original_customer_can_expose",saved().getInt("Cod4Deception")==2));
  add("swindler-followup/original-customer-exposes","sneak-interact","none",12,()->{int slot=0;for(int i=0;i<a.getInventory().items.size();i++)if(a.getInventory().items.get(i).is(Items.DEAD_BUSH))slot=i;var fake=a.getInventory().items.get(slot);a.getInventory().items.set(slot,a.getMainHandItem());a.setItemSlot(EquipmentSlot.MAINHAND,fake);},()->Map.of("stage3",saved().getInt("Cod4Deception")==3,"flee",saved().getInt("Cod4Flee")>0,"customer_uuid",saved().getUUID("Cod4Customer").equals(a.getUUID())));
  deathOps("swindler-followup-paid-return");

 }
 static void specials(){
  add("feeding/setup","view","view",25,()->{spawn("famished_refugee");view();hand(a,"minecraft:bread",3);hand(b,"minecraft:bread",3);},()->check("fixture",true));
  add("feeding/host","interact","none",15,()->{},()->Map.of("one_bread_consumed",count(a,"minecraft:bread")==2,"friendly",saved().getBoolean("Cod4Friendly"),"peer_unchanged",count(b,"minecraft:bread")==3));
  add("feeding/peer-repeat","none","interact",15,()->{},()->check("no_repeat_cost",count(b,"minecraft:bread")==3));
  add("herb/setup","view","view",25,()->{spawn("herb_picker");view();hand(a,"copper_coin",3);hand(b,"copper_coin",3);},()->check("fixture",true));
  add("herb/host-trade","interact","none",15,()->{},()->Map.of("one_coin",count(a,"dynasty:copper_coin")==2,"two_tea",count(a,ForgeRegistries.ITEMS.getKey(com.dynasty.DynastyItems.TEA.get()).toString())==2,"peer_zero_tea",count(b,ForgeRegistries.ITEMS.getKey(com.dynasty.DynastyItems.TEA.get()).toString())==0));
  add("herb/peer-cooldown","none","interact",15,()->{},()->check("cooldown_no_second_charge",count(b,"dynasty:copper_coin")==3));
  add("herb/wait-native-cooldown","none","none",210,()->{},()->check("cooldown_elapsed",saved().getInt("Cod4Cooldown")==0));
  add("herb/peer-trade","none","interact",15,()->{},()->Map.of("peer_one_coin",count(b,"dynasty:copper_coin")==2,"peer_two_tea",count(b,ForgeRegistries.ITEMS.getKey(com.dynasty.DynastyItems.TEA.get()).toString())==2,"host_still_two",count(a,ForgeRegistries.ITEMS.getKey(com.dynasty.DynastyItems.TEA.get()).toString())==2));
  add("snail/setup","view","view",25,()->{spawn("snail_maiden");view();hand(a,"copper_coin",3);hand(b,"copper_coin",3);},()->check("fixture",true));
  add("snail/trade-request","interact","interact",15,()->{},()->Map.of("requested_trade_has_result",count(a,"dynasty:copper_coin")<3||count(b,"dynasty:copper_coin")<3,"observation_no_defined_trade_entry",count(a,"dynasty:copper_coin")==3&&count(b,"dynasty:copper_coin")==3));
  add("snail/first-hit","attack","none",10,()->{a.getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(1);},()->check("first_hit_reduces_health",mob.getHealth()<mob.getMaxHealth()));
  final float[] shellHealth={0};
  add("snail/shell-reject-hit","none","attack",10,()->{shellHealth[0]=mob.getHealth();b.getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(1);},()->check("shell_rejects_second_hit",mob.getHealth()==shellHealth[0]));
  add("swindler/setup","view","view",25,()->{spawn("swindler");view();hand(a,"copper_coin",3);hand(b,"copper_coin",3);},()->check("fixture",true));
  add("swindler/injured","interact","none",12,()->{},()->check("stage1",saved().getInt("Cod4Deception")==1));
  add("swindler/payment","interact","none",12,()->{},()->Map.of("stage2",saved().getInt("Cod4Deception")==2,"paid_one",count(a,"dynasty:copper_coin")==2,"peer_not_charged",count(b,"dynasty:copper_coin")==3,"fake_medicine",count(a,"minecraft:dead_bush")==1));
  add("swindler/other-customer-rejected","none","sneak-interact",12,()->{var fake=a.getInventory().items.stream().filter(s->s.is(Items.DEAD_BUSH)).findFirst().orElseThrow().copy();b.setItemSlot(EquipmentSlot.MAINHAND,fake);},()->check("only_original_customer_can_expose",saved().getInt("Cod4Deception")==2));
  add("swindler/original-customer-exposes","sneak-interact","none",12,()->{int slot=0;for(int i=0;i<a.getInventory().items.size();i++)if(a.getInventory().items.get(i).is(Items.DEAD_BUSH))slot=i;var fake=a.getInventory().items.get(slot);a.getInventory().items.set(slot,a.getMainHandItem());a.setItemSlot(EquipmentSlot.MAINHAND,fake);},()->Map.of("stage3",saved().getInt("Cod4Deception")==3,"flee",saved().getInt("Cod4Flee")>0,"customer_uuid",saved().getUUID("Cod4Customer").equals(a.getUUID())));
  deathOps("swindler-paid-return");
  for(String id:List.of("red_fox","paper_money_ghost","clockwork_rat")){
   add(id+"/theft-setup","view","view",25,()->{spawn(id);view();if(id.equals("clockwork_rat"))hand(a,"minecraft:diamond",3);else hand(a,id.equals("red_fox")?"minecraft:bread":"copper_coin",3);},()->check("fixture",true));
   add(id+"/natural-theft",id.equals("clockwork_rat")?"drop":"none","none",120,()->{mob.setNoAi(false);a.teleportTo(server.overworld(),0,-60,0.5,0,0);b.teleportTo(server.overworld(),5,-60,0,0,0);},()->Map.of("exactly_one_stored",saved().getCompound("Cod4Stolen").getByte("Count")==1,"peer_not_stolen",b.getInventory().isEmpty(),"host_lost_one",count(a,id.equals("clockwork_rat")?"minecraft:diamond":id.equals("red_fox")?"minecraft:bread":"dynasty:copper_coin")==2));
   deathOps(id+"-stolen-return");
  }
  add("herb-spot/setup","view","view",25,()->{spawn("herb_picker");view();server.overworld().setBlock(new BlockPos(0,-60,2),ForgeRegistries.BLOCKS.getValue(new ResourceLocation("dynasty","herb_spot")).defaultBlockState(),3);mob.teleportTo(0,-60,4);},()->check("fixture",true));
  add("herb-spot/both-start","block","block",15,()->{},()->Map.of("host_started",EquipmentBehaviors.saved(a).contains("site_herb_spot_start"),"peer_started",EquipmentBehaviors.saved(b).contains("site_herb_spot_start")));
  add("herb-spot/early-click","block","block",15,()->{},()->Map.of("host_no_early_reward",count(a,ForgeRegistries.ITEMS.getKey(com.dynasty.DynastyItems.TEA.get()).toString())==0,"peer_no_early_reward",count(b,ForgeRegistries.ITEMS.getKey(com.dynasty.DynastyItems.TEA.get()).toString())==0));
  add("herb-spot/native-1200tick-wait","none","none",1205,()->{},()->check("actual_world_time_elapsed",true));
  add("herb-spot/both-finish","block","block",15,()->{},()->Map.of("host_two_tea",count(a,ForgeRegistries.ITEMS.getKey(com.dynasty.DynastyItems.TEA.get()).toString())==2,"peer_two_tea",count(b,ForgeRegistries.ITEMS.getKey(com.dynasty.DynastyItems.TEA.get()).toString())==2,"both_completed",EquipmentBehaviors.saved(a).getBoolean("site_herb_spot_done")&&EquipmentBehaviors.saved(b).getBoolean("site_herb_spot_done")));
  add("herb-spot/repeat-no-reward","block","block",15,()->{},()->Map.of("host_still_two",count(a,ForgeRegistries.ITEMS.getKey(com.dynasty.DynastyItems.TEA.get()).toString())==2,"peer_still_two",count(b,ForgeRegistries.ITEMS.getKey(com.dynasty.DynastyItems.TEA.get()).toString())==2));
  add("herb-spot/cleanup","none","none",5,()->server.overworld().setBlock(new BlockPos(0,-60,2),Blocks.AIR.defaultBlockState(),3),()->check("cleanup",true));
  add("magpie/setup","view","view",25,()->{spawn("wooden_magpie");view();mob.setHealth(mob.getMaxHealth()-20);hand(a,"qimen_cable",3);hand(b,"qimen_cable",3);},()->check("fixture",true));
  add("magpie/repair","interact","none",15,()->{},()->Map.of("healed20",mob.getHealth()==mob.getMaxHealth(),"cost1",count(a,"dynasty:qimen_cable")==2));
  add("magpie/full-health-repeat","none","interact",15,()->{},()->check("no_repeat_charge",count(b,"dynasty:qimen_cable")==3));
 }
 @Mod.EventBusSubscriber(modid="dynastymobnetworkqa")
 public static class Events{
  @SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST) public static void effectiveDamage(net.minecraftforge.event.entity.living.LivingDamageEvent e){if(!FULL||actor==null||e.getAmount()<=0||e.getSource().getEntity()==null)return;if(e.getSource().getEntity().getUUID().equals(actor)&&e.getEntity() instanceof ServerPlayer)damageEvents++;if(e.getEntity().getUUID().equals(actor)&&e.getSource().getEntity() instanceof ServerPlayer p)effectivePlayerAttackers.add(p.getUUID());}

  @SubscribeEvent public static void attack(net.minecraftforge.event.entity.player.AttackEntityEvent e){if(!e.getEntity().level().isClientSide&&actor!=null&&e.getTarget().getUUID().equals(actor)){attackEvents++;nativeInputs.add(map("kind","attack","tick",server.getTickCount(),"player",e.getEntity().getUUID().toString(),"shift",e.getEntity().isShiftKeyDown(),"hand",e.getEntity().getMainHandItem().save(new CompoundTag()).toString()));}}
  @SubscribeEvent public static void interact(net.minecraftforge.event.entity.player.PlayerInteractEvent.EntityInteract e){if(!e.getEntity().level().isClientSide&&actor!=null&&e.getTarget().getUUID().equals(actor)){interactEvents++;nativeInputs.add(map("kind","interact","tick",server.getTickCount(),"player",e.getEntity().getUUID().toString(),"shift",e.getEntity().isShiftKeyDown(),"hand",e.getEntity().getMainHandItem().save(new CompoundTag()).toString(),"mobStageBefore",saved().getInt("Cod4Deception")));}}
  @SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST,receiveCanceled=true) public static void drops(net.minecraftforge.event.entity.living.LivingDropsEvent e){if(actor==null||!e.getEntity().getUUID().equals(actor))return;deathEvents++;var entries=new ArrayList<Object>();for(var d:e.getDrops()){var s=d.getItem();String k=s.save(new CompoundTag()).getString("id")+(s.hasTag()?s.getTag().toString():"");if(!e.isCanceled())loot.merge(k,s.getCount(),Integer::sum);entries.add(Map.of("uuid",d.getUUID().toString(),"stack",s.save(new CompoundTag()).toString()));}dropEvents.add(Map.of("tick",server.getTickCount(),"cancelled",e.isCanceled(),"killer",e.getSource().getEntity()==null?"none":e.getSource().getEntity().getUUID().toString(),"entries",entries));}
  @SubscribeEvent public static void serverTick(TickEvent.ServerTickEvent ev){if(!HOST||!live||!serverReady||complete||ev.phase!=TickEvent.Phase.END)return;try{
   if(op>=0){if(FULL&&!readySent&&server.getTickCount()-start>=3){readySent=true;for(var p:ps)p.sendSystemMessage(net.minecraft.network.chat.Component.literal("[COD4_FULLPACK_READY_"+op+"]"));write("server-ready-"+op+".json",map("index",op,"preparedTick",start,"markerTick",server.getTickCount(),"players",ps.stream().map(MobNetworkAcceptance::player).toList()));}if(FULL&&server.getTickCount()-start>600)throw new AssertionError("Stage exceeded600 native ticks: "+op+" hostAck="+exists("host-ack-"+op)+" peerAck="+exists("peer-ack-"+op));var o=ops.get(op);if(server.getTickCount()-start<o.waitTicks||!exists("host-ack-"+op)||!exists("peer-ack-"+op))return;var checks=o.check.run();write(String.format("result-%03d.json",op),Map.of("index",op,"name",o.name,"before",before,"after",snapshot(),"checks",checks,"pass",checks.values().stream().allMatch(Boolean.TRUE::equals)));}
   op++;if(op==ops.size()){complete=true;marker("server-COMPLETE");return;}var o=ops.get(op);o.setup.run();before=snapshot();start=server.getTickCount();readySent=false;write("command.json",map("index",op,"name",o.name,"host",o.host,"peer",o.peer,"entity",mob==null?-1:mob.getId(),"uuid",mob==null?"none":mob.getUUID().toString(),"hostHand",a.getMainHandItem().save(new CompoundTag()).toString(),"peerHand",b.getMainHandItem().save(new CompoundTag()).toString(),"hostUUID",a.getUUID().toString(),"peerUUID",b.getUUID().toString(),"hostPos",List.of(a.getX(),a.getY(),a.getZ()),"peerPos",List.of(b.getX(),b.getY(),b.getZ())));
  }catch(Throwable ex){try{write("server-FAIL.json",Map.of("op",op,"error",ex.toString()));}catch(Exception ignored){}complete=true;}}
 }
 @Mod.EventBusSubscriber(modid="dynastymobnetworkqa",value=net.minecraftforge.api.distmarker.Dist.CLIENT)
 public static class Client{
  @SubscribeEvent public static void ready(net.minecraftforge.client.event.ClientChatReceivedEvent.System e){String text=e.getMessage().getString();if(text.matches("\\[COD4_FULLPACK_READY_[0-9]+\\]")){String n=text.substring("[COD4_FULLPACK_READY_".length(),text.length()-1);try{marker(ROLE+"-ready-seen-"+n);}catch(Exception ex){throw new RuntimeException(ex);}}}
  static boolean started,listening,done;static int reconnects;static int ticks,worldFrames,serial=-1,seen=-1,seenAt,walkStartedAt=-1;static boolean draw;static int capture=-1;static long deadline=System.nanoTime()+3_600_000_000_000L;
  @SubscribeEvent public static void tick(TickEvent.ClientTickEvent ev){if(done||ev.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();mc.options.hideGui=true;ticks++;try{
   if(System.nanoTime()>deadline)throw new AssertionError("client timeout "+serial);
   if(exists("server-FAIL.json"))throw new AssertionError(Files.readString(OUT.resolve("server-FAIL.json")));
   if(mc.getOverlay()!=null)return;if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
   if(!started&&mc.screen instanceof TitleScreen){if(!mc.gameDirectory.getCanonicalPath().equals(System.getProperty("dynasty.networkqa.instance")))throw new AssertionError("instance mismatch");if(!HOST&&!exists("port.txt"))return;started=true;if(!HOST){String addr="127.0.0.1:"+Files.readString(OUT.resolve("port.txt")).trim();ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString(addr),new ServerData("Mob private QA",addr,false),false);return;}
    var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(FULL,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);mc.createWorldOpenFlows().createFreshLevel("mob-qa-"+System.currentTimeMillis(),new LevelSettings("Mob private fixtures",GameType.SURVIVAL,false,net.minecraft.world.Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(77,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(FULL?WorldPresets.NORMAL:WorldPresets.FLAT).createWorldDimensions());return;}
   if(!HOST&&mc.level==null&&mc.screen instanceof net.minecraft.client.gui.screens.DisconnectedScreen){
    var reason=new ArrayList<String>();for(var field:mc.screen.getClass().getDeclaredFields())if(net.minecraft.network.chat.Component.class.isAssignableFrom(field.getType())){field.setAccessible(true);reason.add(((net.minecraft.network.chat.Component)field.get(mc.screen)).getString());}
    write("peer-disconnect-"+reconnects+".json",Map.of("reason",reason,"tick",ticks));if(reconnects++>=3)throw new AssertionError("native connection failed "+reason);String addr="127.0.0.1:"+Files.readString(OUT.resolve("port.txt")).trim();ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString(addr),new ServerData("Mob private QA retry",addr,false),false);return;
   }
   if(mc.level==null||mc.player==null)return;
   if(exists("server-COMPLETE")){marker(ROLE+"-COMPLETE");if(!HOST||exists("peer-COMPLETE")){done=true;mc.stop();}return;}
   if(HOST&&!listening){listening=true;server=mc.getSingleplayerServer();int port;try(var socket=new java.net.ServerSocket(0)){port=socket.getLocalPort();}server.setUsesAuthentication(false);if(!server.publishServer(GameType.SURVIVAL,true,port))throw new AssertionError("LAN publish failed");Files.writeString(OUT.resolve("port.txt"),""+port);return;}
   if(mc.screen!=null||worldFrames<3)return;marker(ROLE+"-world-rendered");
   if(HOST&&!live&&server.getPlayerList().getPlayerCount()==2&&exists("peer-world-rendered")){live=true;server.execute(()->{try{ps=server.getPlayerList().getPlayers().stream().sorted(Comparator.comparing(p->p.getGameProfile().getName())).toList();a=ps.get(0);b=ps.get(1);if(!(b.connection.connection.getRemoteAddress() instanceof java.net.InetSocketAddress)||a.getUUID().equals(b.getUUID())||ps.stream().anyMatch(p->p instanceof net.minecraftforge.common.util.FakePlayer))throw new AssertionError("real independent TCP required");write("connections.json",ps.stream().map(p->Map.of("name",p.getGameProfile().getName(),"uuid",p.getUUID().toString(),"class",p.getClass().getName(),"remote",p.connection.connection.getRemoteAddress().toString())).toList());server.overworld().setDayTime(1000);if(!FULL)for(int x=-20;x<=20;x++)for(int z=-20;z<=20;z++)server.overworld().setBlock(new BlockPos(x,-61,z),Blocks.STONE.defaultBlockState(),3);build();write("stage-plan.json",ops.stream().map(o->o.name).toList());serverReady=true;}catch(Throwable ex){try{write("server-FAIL.json",Map.of("error",ex.toString()));}catch(Exception ignored){}}});return;}
   if(!exists("command.json"))return;var c=JsonParser.parseString(Files.readString(OUT.resolve("command.json"))).getAsJsonObject();int n=c.get("index").getAsInt();if(n==serial)return;if(seen!=n){seen=n;seenAt=ticks;walkStartedAt=-1;if(c.get(ROLE).getAsString().startsWith("sneak"))mc.options.keyShift.setDown(true);return;}if(FULL&&!exists(ROLE+"-ready-seen-"+n))return;if(c.get(ROLE).getAsString().equals("walk")){if(walkStartedAt<0)walkStartedAt=ticks;mc.options.keyUp.setDown(ticks-walkStartedAt<126);mc.options.keyJump.setDown(ticks-walkStartedAt<126);if(ticks-walkStartedAt<126)return;}if(ticks-seenAt<6)return;var e=mc.level.getEntity(c.get("entity").getAsInt());String action=c.get(ROLE).getAsString();if(!action.equals("none")&&!c.get("name").getAsString().startsWith("fullpack/explore-")&&e==null){if(ticks-seenAt<100)return;throw new AssertionError("entity unavailable "+n);}
   mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);mc.options.fov().set(85);mc.player.setYRot(0);mc.player.setXRot(15);
   if(FULL&&action.equals("view")){for(String role:List.of("host","peer")){var xyz=c.getAsJsonArray(role+"Pos");var expected=new Vec3(xyz.get(0).getAsDouble(),xyz.get(1).getAsDouble(),xyz.get(2).getAsDouble());var expectedUuid=c.get(role+"UUID").getAsString();if(mc.level.players().stream().noneMatch(p->p.getUUID().toString().equals(expectedUuid)&&p.position().distanceTo(expected)<1)){if(ticks-seenAt>120)throw new AssertionError("View native positions not ready: "+n+" expected="+role+expected+" actual="+mc.level.players().stream().map(p->p.getUUID()+":"+p.position()).toList());return;}}}
   Object result="none";if(action.equals("block"))result=mc.gameMode.useItemOn(mc.player,InteractionHand.MAIN_HAND,new BlockHitResult(new Vec3(.5,-59.7,2.5),Direction.UP,new BlockPos(0,-60,2),false)).toString();if(action.equals("attack"))mc.gameMode.attack(mc.player,e);if(action.equals("interact")||action.equals("sneak-interact")){if(action.startsWith("sneak")){mc.options.keyShift.setDown(true);mc.player.setShiftKeyDown(true);mc.player.connection.send(new net.minecraft.network.protocol.game.ServerboundPlayerCommandPacket(mc.player,net.minecraft.network.protocol.game.ServerboundPlayerCommandPacket.Action.PRESS_SHIFT_KEY));}result=mc.gameMode.interact(mc.player,e,InteractionHand.MAIN_HAND).toString();}if(action.equals("drop"))mc.player.drop(false);
   write(ROLE+"-input-"+n+".json",map("index",n,"name",c.get("name").getAsString(),"action",action,"api",action.equals("attack")?"MultiPlayerGameMode.attack":action.contains("interact")?"MultiPlayerGameMode.interact":action.equals("drop")?"LocalPlayer.drop(false) native C2S":action.equals("walk")?"native keyUp+keyJump for126 client ticks -> native movement packets":action.equals("block")?"MultiPlayerGameMode.useItemOn":"none","result",result,"clientTick",ticks,"selfUUID",mc.player.getUUID().toString(),"nativeReadyMarkerReceived",!FULL||exists(ROLE+"-ready-seen-"+n),"nativeShift",mc.player.isShiftKeyDown(),"entity",e==null?"none":e.getUUID().toString(),"hand",mc.player.getMainHandItem().save(new CompoundTag()).toString(),"inventory",mc.player.getInventory().items.stream().filter(z->!z.isEmpty()).map(z->z.save(new CompoundTag()).toString()).toList(),"mobState",e instanceof SecondaryMob sm?Map.of("health",sm.getHealth(),"animation",sm.animation(),"pos",sm.position().toString(),"alive",sm.isAlive()):Map.of(),"localPlayers",mc.level.players().stream().map(p->Map.of("uuid",p.getUUID().toString(),"class",p.getClass().getName(),"pos",p.position().toString())).toList()));
   mc.options.keyShift.setDown(false);if(action.startsWith("sneak")){mc.player.setShiftKeyDown(false);mc.player.connection.send(new net.minecraft.network.protocol.game.ServerboundPlayerCommandPacket(mc.player,net.minecraft.network.protocol.game.ServerboundPlayerCommandPacket.Action.RELEASE_SHIFT_KEY));}
   serial=n;if(action.equals("view"))capture=n;else marker(ROLE+"-ack-"+n);
  }catch(Throwable ex){done=true;ex.printStackTrace();try{write(ROLE+"-FAIL.json",Map.of("serial",serial,"error",ex.toString()));}catch(Exception ignored){}mc.stop();}}
  @SubscribeEvent public static void world(net.minecraftforge.client.event.RenderLevelStageEvent e){if(e.getStage()==net.minecraftforge.client.event.RenderLevelStageEvent.Stage.AFTER_LEVEL){worldFrames++;draw=true;}}
  @SubscribeEvent public static void render(TickEvent.RenderTickEvent ev){if(ev.phase==TickEvent.Phase.START){draw=false;return;}if(capture<0||!draw||Minecraft.getInstance().screen!=null)return;try{var mc=Minecraft.getInstance();try(var img=Screenshot.takeScreenshot(mc.getMainRenderTarget())){img.writeToFile(OUT.resolve(ROLE+"-view-"+capture+".png"));}write(ROLE+"-render-"+capture+".json",Map.of("event","RenderTick.END after RenderLevel AFTER_LEVEL","worldFrames",worldFrames,"camera","THIRD_PERSON_BACK","trackedPlayers",mc.level.players().size(),"cameraPosition",mc.gameRenderer.getMainCamera().getPosition().toString()));marker(ROLE+"-ack-"+capture);capture=-1;}catch(Exception ex){throw new RuntimeException(ex);}}
 }
}
