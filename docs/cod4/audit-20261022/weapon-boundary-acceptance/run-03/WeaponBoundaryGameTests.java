package com.dynasty;

import com.dynasty.expansion.*;
import com.google.gson.*;
import com.mojang.authlib.GameProfile;
import java.nio.file.*;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.*;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.*;

/** Private QA. Real server ticks and native use/release, supplied fixtures; no TCP-client claim. */
@GameTestHolder("dynasty_weapon_boundary_qa") @PrefixGameTestTemplate(false)
@net.minecraftforge.fml.common.Mod.EventBusSubscriber(modid="dynasty")
public final class WeaponBoundaryGameTests {
 static final JsonArray RESULTS=new JsonArray();
 static final Map<String,JsonObject> MEASUREMENTS=new HashMap<>();
 static int sequence;
 static final net.minecraft.server.level.TicketType<UUID> TICKET=net.minecraft.server.level.TicketType.create("weapon_boundary",UUID::compareTo);
 static final Map<UUID,List<net.minecraft.world.level.ChunkPos>> TICKETS=new HashMap<>();
 static final Map<UUID,JsonObject> DAMAGE=new HashMap<>();
 @net.minecraftforge.eventbus.api.SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.HIGHEST)
 public static void incoming(net.minecraftforge.event.entity.living.LivingHurtEvent e){var row=DAMAGE.get(e.getEntity().getUUID());if(row!=null&&e.getSource().getDirectEntity() instanceof AbstractArrow){row.addProperty("incoming_arrow_damage",e.getAmount());row.addProperty("actual_arrow_entity",e.getSource().getDirectEntity().getId());}}
 @net.minecraftforge.eventbus.api.SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST)
 public static void finalDamage(net.minecraftforge.event.entity.living.LivingDamageEvent e){var row=DAMAGE.get(e.getEntity().getUUID());if(row!=null&&e.getSource().getDirectEntity() instanceof AbstractArrow)row.addProperty("native_final_damage",e.getAmount());}
 static void record(String name,JsonObject data){
  data.addProperty("case",name);RESULTS.add(data);
  try{Files.writeString(Path.of(System.getProperty("dynasty.weaponBoundary.output")),new GsonBuilder().setPrettyPrinting().create().toJson(RESULTS));}
  catch(Exception ex){throw new RuntimeException(ex);}
 }
 static ServerPlayer player(GameTestHelper h,String weapon){
  var base=h.absolutePos(new BlockPos(5,3,5)).offset((++sequence)*32,20,0);
  h.getLevel().getChunkAt(base);h.getLevel().getChunkAt(base.south(16));
  for(var cell:BlockPos.betweenClosed(base.offset(-3,-1,-2),base.offset(3,5,16)))h.getLevel().setBlock(cell,Blocks.AIR.defaultBlockState(),2);
  for(var cell:BlockPos.betweenClosed(base.offset(-3,0,12),base.offset(3,4,12)))h.getLevel().setBlock(cell,Blocks.STONE.defaultBlockState(),2);
  var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"weapon-boundary"));
  p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
  p.setGameMode(GameType.SURVIVAL);p.setPos(base.getCenter());p.setNoGravity(true);p.setYRot(0);p.setXRot(0);
  p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.item(weapon)));
  var chunks=new ArrayList<net.minecraft.world.level.ChunkPos>();var center=p.chunkPosition();
  for(int x=center.x-1;x<=center.x+1;x++)for(int z=center.z-1;z<=center.z+1;z++){var chunk=new net.minecraft.world.level.ChunkPos(x,z);chunks.add(chunk);h.getLevel().getChunkSource().addRegionTicket(TICKET,chunk,2,p.getUUID(),true);h.getLevel().getChunk(x,z);}
  TICKETS.put(p.getUUID(),chunks);p.getFoodData().setFoodLevel(17);h.getLevel().addNewPlayer(p);return p;
 }
 static void close(ServerPlayer p){p.stopUsingItem();net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(p));DynastyTrinkets.forget(p);var chunks=TICKETS.remove(p.getUUID());if(chunks!=null)for(var chunk:chunks)p.serverLevel().getChunkSource().removeRegionTicket(TICKET,chunk,2,p.getUUID(),true);p.discard();}
 static void crossbow(GameTestHelper h,boolean siege){
  var p=player(h,siege?"siege_crossbow":"repeating_crossbow");var weapon=p.getMainHandItem();int count=siege?1:3;
  p.getInventory().setItem(10,new ItemStack(ExpansionContent.AMMO.get(siege?"heavy_bolt":"repeating_bolt").get(),count*3));
  int[] phase={0},cycle={0};long[] at={0};var rows=new JsonArray();
  h.onEachTick(()->{
   if(p.isRemoved())return;p.doTick();long now=h.getLevel().getGameTime();
   try{
    if(phase[0]==0){p.gameMode.useItem(p,h.getLevel(),weapon,InteractionHand.MAIN_HAND);at[0]=now;phase[0]=1;}
    else if(phase[0]==1&&now-at[0]>=32){
     p.releaseUsingItem();h.assertTrue(CrossbowItem.isCharged(weapon),"Native full charge yields loaded magazine");
     h.assertTrue(weapon.getOrCreateTag().getList("cod4Magazine",10).size()==count,"Each new magazine has original shot count");
     p.gameMode.useItem(p,h.getLevel(),weapon,InteractionHand.MAIN_HAND);at[0]=now;phase[0]=2;
    }else if(phase[0]==2&&now-at[0]>=24){
     cycle[0]++;var arrows=h.getLevel().getEntitiesOfClass(AbstractArrow.class,p.getBoundingBox().inflate(24),a->a.getOwner()==p);
     var row=new JsonObject();row.addProperty("cycle",cycle[0]);row.addProperty("gameTime",now);row.addProperty("projectiles",arrows.size());row.addProperty("remaining_ammo",p.getInventory().getItem(10).getCount());row.addProperty("durability",weapon.getDamageValue());rows.add(row);
     h.assertTrue(arrows.size()==count,"Native held fire emits finite original shot count each cycle: "+row);
     h.assertTrue(!CrossbowItem.isCharged(weapon)&&weapon.getOrCreateTag().getList("cod4Magazine",10).isEmpty(),"Actual firing exhausts magazine");
     h.assertTrue(weapon.getDamageValue()==count*cycle[0]&&p.getInventory().getItem(10).getCount()==count*(3-cycle[0]),"Repeated loading pays exact finite ammo/durability");
     arrows.forEach(Entity::discard);
     if(cycle[0]==3){var out=new JsonObject();out.add("cycles",rows);out.addProperty("pass",true);record(siege?"siege_three_reload_cycles":"repeating_three_reload_cycles",out);close(p);h.succeed();}
     else phase[0]=0;
    }
   }catch(Throwable ex){var out=new JsonObject();out.add("cycles",rows);out.addProperty("pass",false);out.addProperty("failure",ex.toString());record(siege?"siege_three_reload_cycles":"repeating_three_reload_cycles",out);close(p);throw ex;}
  });
 }
 @GameTest(template="bow_ritual_test",batch="boundary_repeating",setupTicks=20,timeoutTicks=230)
 public static void repeatedNativeReloadAndFiniteAmmo(GameTestHelper h){crossbow(h,false);}
 @GameTest(template="bow_ritual_test",batch="boundary_siege",setupTicks=20,timeoutTicks=230)
 public static void siegeNativeReloadAndFiniteAmmo(GameTestHelper h){crossbow(h,true);}
 static void tether(GameTestHelper h,boolean claw){
  String id=claw?"flying_claw":"rope_dart";var p=player(h,id);var weapon=p.getMainHandItem();
  var z=new Zombie(h.getLevel());z.setPos(p.position().add(0,0,6));z.setNoAi(true);z.setNoGravity(true);h.getLevel().addFreshEntity(z);
  long[] at={0};int[] phase={0};var rows=new JsonArray();
  h.onEachTick(()->{
   if(p.isRemoved())return;p.doTick();z.setPos(p.position().add(0,0,6));z.setDeltaMovement(0,0,0);long now=h.getLevel().getGameTime();
   try{
    if(phase[0]==0){p.gameMode.useItem(p,h.getLevel(),weapon,InteractionHand.MAIN_HAND);at[0]=now;phase[0]=1;h.assertTrue(weapon.getDamageValue()==1,"Initial native contact pays once");}
    else if(phase[0]==1){
     var cooling=p.getCooldowns().isOnCooldown(weapon.getItem());int before=weapon.getDamageValue();p.gameMode.useItem(p,h.getLevel(),weapon,InteractionHand.MAIN_HAND);
     var row=new JsonObject();row.addProperty("elapsed_server_ticks",now-at[0]);row.addProperty("cooldown_before_use",cooling);row.addProperty("durability",weapon.getDamageValue());rows.add(row);
     if(cooling)h.assertTrue(weapon.getDamageValue()==before,"Every native input while real cooldown remains is rejected");
     else{h.assertTrue(now-at[0]==40&&weapon.getDamageValue()==2,"Exactly at original40 native ticks next contact succeeds: "+row);var out=new JsonObject();out.add("native_tick_inputs",rows);out.addProperty("pass",true);record(id+"_cooldown_boundary",out);z.discard();close(p);h.succeed();}
    }
   }catch(Throwable ex){var out=new JsonObject();out.add("native_tick_inputs",rows);out.addProperty("pass",false);out.addProperty("failure",ex.toString());record(id+"_cooldown_boundary",out);z.discard();close(p);throw ex;}
  });
 }
 @GameTest(template="bow_ritual_test",batch="boundary_rope",setupTicks=20,timeoutTicks=100)
 public static void ropeUsesActualCooldownClock(GameTestHelper h){tether(h,false);}
 @GameTest(template="bow_ritual_test",batch="boundary_claw",setupTicks=20,timeoutTicks=100)
 public static void clawUsesActualCooldownClock(GameTestHelper h){tether(h,true);}
 @GameTest(template="bow_ritual_test",batch="boundary_morale",setupTicks=20,timeoutTicks=110)
 public static void siegeActuallyHalvesMoraleAndKeepsFiringIdentityAfterSwitch(GameTestHelper h){
  var ps=new ArrayList<ServerPlayer>();var targets=new ArrayList<LivingEntity>();var rows=new JsonArray();int[] phase={0};long[] at={0};
  for(boolean siege:new boolean[]{false,true}){
   String id=siege?"siege_crossbow":"repeating_crossbow";var p=player(h,id);ps.add(p);
   var target=(LivingEntity)net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getValue(new net.minecraft.resources.ResourceLocation("dynasty:royal_guard")).create(h.getLevel());
   target.setPos(p.position().add(0,0,5));target.setNoGravity(true);if(target instanceof Mob mob)mob.setNoAi(true);
   target.getAttribute(Attributes.MAX_HEALTH).setBaseValue(100000);target.getAttribute(Attributes.ARMOR).setBaseValue(0);target.getAttribute(Attributes.ARMOR_TOUGHNESS).setBaseValue(0);target.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);target.setHealth(100000);
   h.getLevel().addFreshEntity(target);targets.add(target);var row=new JsonObject();row.addProperty("weapon",id);row.addProperty("morale",DynastyBalance.mobToughness(target.getType()));row.addProperty("weapon_bonus",DynastyBalance.weaponBonus(id));DAMAGE.put(target.getUUID(),row);rows.add(row);
   p.getInventory().setItem(10,new ItemStack(ExpansionContent.AMMO.get(siege?"heavy_bolt":"repeating_bolt").get(),1));
  }
  h.onEachTick(()->{
   if(ps.get(0).isRemoved())return;ps.forEach(ServerPlayer::doTick);long now=h.getLevel().getGameTime();
   try{
    if(phase[0]==0){for(var p:ps)p.gameMode.useItem(p,h.getLevel(),p.getMainHandItem(),InteractionHand.MAIN_HAND);at[0]=now;phase[0]=1;}
    else if(phase[0]==1&&now-at[0]>=32){for(var p:ps){p.releaseUsingItem();p.gameMode.useItem(p,h.getLevel(),p.getMainHandItem(),InteractionHand.MAIN_HAND);}at[0]=now;phase[0]=2;}
    else if(phase[0]==2){
     boolean allSwitched=true;for(var p:ps){if(!p.getMainHandItem().is(Items.STICK)){var shots=h.getLevel().getEntitiesOfClass(AbstractArrow.class,p.getBoundingBox().inflate(24),a->a.getOwner()==p);if(shots.isEmpty())allSwitched=false;else{p.stopUsingItem();p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.STICK));}}}
     if(allSwitched){phase[0]=3;at[0]=now;}
    }else if(phase[0]==3&&now-at[0]>=16){
     for(int i=0;i<2;i++){var target=targets.get(i);var row=DAMAGE.get(target.getUUID());h.assertTrue(row.has("native_final_damage")&&row.has("incoming_arrow_damage"),"Real fired projectile must physically hit target: "+row);
      double morale=row.get("morale").getAsDouble(),raw=row.get("incoming_arrow_damage").getAsDouble()+row.get("weapon_bonus").getAsDouble();double expected=raw*(1-morale*(i==1?.5:1));double lost=100000-target.getHealth();
      row.addProperty("expected_original_pipeline_damage",expected);row.addProperty("actual_health_loss",lost);row.addProperty("held_item_at_hit",ps.get(i).getMainHandItem().getDescriptionId());row.addProperty("armor_break_effect",target.hasEffect(ExpansionEffects.BREAK.get()));
      h.assertTrue(Math.abs(row.get("native_final_damage").getAsDouble()-expected)<.1&&Math.abs(lost-expected)<.1,"Siege halves actual original morale reduction; repeating preserves full reduction after both switch held item: "+row);
     }
     var out=new JsonObject();out.add("actual_projectile_hits",rows);out.addProperty("pass",true);record("actual_siege_morale_penetration_and_snapshot",out);targets.forEach(t->{DAMAGE.remove(t.getUUID());t.discard();});ps.forEach(WeaponBoundaryGameTests::close);h.succeed();
    }
   }catch(Throwable ex){var out=new JsonObject();out.add("actual_projectile_hits",rows);out.addProperty("pass",false);out.addProperty("failure",ex.toString());record("actual_siege_morale_penetration_and_snapshot",out);targets.forEach(t->{DAMAGE.remove(t.getUUID());t.discard();});ps.forEach(WeaponBoundaryGameTests::close);throw ex;}
  });
 }
}
