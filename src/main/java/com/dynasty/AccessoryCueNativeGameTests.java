package com.dynasty;

import com.dynasty.expansion.EquipmentBehaviors;
import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;

/** Real native input/tick checks of original effects and their new cosmetic hooks; no client render claim. */
@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class AccessoryCueNativeGameTests {
    private static String cue(String id){return "cod3_accessory_at_"+id;}
    private static ServerPlayer player(GameTestHelper h,String id,String slot,boolean tick){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"accessory-native"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(switch(id){case "jade_bi_disc"->6;case "moon_pendant"->8;case "qilin_horn_charm"->10;case "silk_pouch"->12;case "jade_cicada"->14;default->6;},52,6))));p.setNoGravity(true);p.getFoodData().setFoodLevel(17);
        p.getAttribute(Attributes.MAX_HEALTH).setBaseValue(5000);p.setHealth(5000);p.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.STICK));for(int i=0;i<61;i++)p.tick();
        if(!id.isEmpty())SchoolCombatGameTests.equip(p,slot,new ItemStack(net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty",id))));
        // Native calibration fixture: keep the standing volume clear of adjacent tall structure tests.
        for(var cell:BlockPos.betweenClosed(p.blockPosition().offset(-1,0,-1),p.blockPosition().offset(1,3,1)))h.getLevel().setBlock(cell,net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(),2);
        h.assertTrue(h.getLevel().noCollision(p,p.getBoundingBox()),"Native stationary player has a real clear standing volume");
        h.getLevel().addNewPlayer(p);if(tick)h.onEachTick(()->{if(!p.isRemoved())p.doTick();});return p;
    }
    private static Zombie attacker(GameTestHelper h,ServerPlayer p){var z=new Zombie(h.getLevel());z.setPos(p.position().add(1,0,0));z.setNoAi(true);z.setNoGravity(true);h.getLevel().addFreshEntity(z);return z;}
    private static float hurt(ServerPlayer p,Zombie z){p.invulnerableTime=0;float hp=p.getHealth();p.hurt(p.damageSources().mobAttack(z),100);return hp-p.getHealth();}
    private static void close(ServerPlayer...players){for(var p:players){net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(p));DynastyTrinkets.forget(p);p.discard();}}
    public static final class HealthTrace {
        final UUID owner;final List<String> damage=new ArrayList<>(),ambientHeals=new ArrayList<>();int heals;float healed;
        HealthTrace(ServerPlayer p){owner=p.getUUID();}
        @net.minecraftforge.eventbus.api.SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST)
        public void damage(net.minecraftforge.event.entity.living.LivingDamageEvent e){if(e.getEntity().getUUID().equals(owner))damage.add(e.getSource().getMsgId()+":"+e.getAmount()+":"+e.getSource().getEntity());}
        @net.minecraftforge.eventbus.api.SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST)
        public void heal(net.minecraftforge.event.entity.living.LivingHealEvent e){if(e.getEntity().getUUID().equals(owner)){heals++;healed+=e.getAmount();if(e.getAmount()<2)ambientHeals.add("amount="+e.getAmount()+", effects="+e.getEntity().getActiveEffects()+", stack="+java.util.Arrays.toString(Thread.currentThread().getStackTrace()));}}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_accessory_native_passive",setupTicks=20,timeoutTicks=250)
    public static void actualPlayerTicksGateNightAndWornPassiveCuesAndCicadaHealKeeps180SecondCooldown(GameTestHelper h){
        long day=h.getLevel().getDayTime();var difficulty=h.getLevel().getDifficulty();h.getLevel().getServer().setDifficulty(net.minecraft.world.Difficulty.NORMAL,true);h.getLevel().setDayTime(6000);
        var bi=player(h,"jade_bi_disc","necklace",true);var moon=player(h,"moon_pendant","necklace",true);
        var horn=player(h,"qilin_horn_charm","necklace",true);var silk=player(h,"silk_pouch","belt",true);
        var cicada=player(h,"jade_cicada","charm",true);cicada.setHealth(cicada.getMaxHealth()*.2F);float hp=cicada.getHealth();var trace=new HealthTrace(cicada);net.minecraftforge.common.MinecraftForge.EVENT_BUS.register(trace);
        h.runAfterDelay(65,()->{try{
            h.assertTrue(!bi.getPersistentData().contains(cue("jade_bi_disc"))&&!moon.getPersistentData().contains(cue("moon_pendant")),"Daylight actual native player ticks do not borrow night-only patterns");
            h.assertTrue(horn.getPersistentData().contains(cue("qilin_horn_charm"))&&silk.getPersistentData().contains(cue("silk_pouch")),"Actually worn regeneration/luck and vision/water charms emit their distinct native tick cues");
            h.assertTrue(Math.abs(cicada.getHealth()-hp-cicada.getMaxHealth()*.08F)<.1&&trace.heals==1&&Math.abs(trace.healed-cicada.getMaxHealth()*.08F)<.1&&trace.damage.isEmpty(),"Original low-health native tick heals exactly8percent once, cosmetic hook adds none: health="+cicada.getHealth()+", initial="+hp+", max="+cicada.getMaxHealth()+", ready="+EquipmentBehaviors.saved(cicada)+", cue="+cicada.getPersistentData().getLong(cue("jade_cicada"))+", nativeHealCount="+trace.heals+", nativeHealed="+trace.healed+", nativeDamage="+trace.damage);
            long until=EquipmentBehaviors.saved(cicada).getLong("cicada"),at=cicada.getPersistentData().getLong(cue("jade_cicada"));
            h.assertTrue(until-at==3600,"Original saved heal cooldown remains exactly180seconds at real first proc");
            cicada.setHealth(hp);h.getLevel().setDayTime(18000);
            h.runAfterDelay(65,()->{try{
                h.assertTrue(bi.getPersistentData().contains(cue("jade_bi_disc"))&&moon.getPersistentData().contains(cue("moon_pendant")),"Actual nighttime ticks produce distinct jade-disc and moon patterns");
                h.assertTrue(cicada.getHealth()==hp&&EquipmentBehaviors.saved(cicada).getLong("cicada")==until&&cicada.getPersistentData().getLong(cue("jade_cicada"))==at,"Continued low health neither repeats healing nor restarts the original cooldown or cue: health="+cicada.getHealth()+", expected="+hp+", heals="+trace.heals+", healed="+trace.healed+", damage="+trace.damage+", ambient="+trace.ambientHeals+", pos="+cicada.position()+", difficulty="+h.getLevel().getDifficulty()+", food="+cicada.getFoodData().getFoodLevel()+", until="+EquipmentBehaviors.saved(cicada).getLong("cicada")+", cue="+cicada.getPersistentData().getLong(cue("jade_cicada")));
                SchoolCombatGameTests.equip(bi,"necklace",ItemStack.EMPTY);SchoolCombatGameTests.equip(moon,"necklace",ItemStack.EMPTY);SchoolCombatGameTests.equip(horn,"necklace",ItemStack.EMPTY);SchoolCombatGameTests.equip(silk,"belt",ItemStack.EMPTY);
                long[] previous={bi.getPersistentData().getLong(cue("jade_bi_disc")),moon.getPersistentData().getLong(cue("moon_pendant")),horn.getPersistentData().getLong(cue("qilin_horn_charm")),silk.getPersistentData().getLong(cue("silk_pouch"))};
                h.runAfterDelay(65,()->{try{ServerPlayer[] ps={bi,moon,horn,silk};String[] ids={"jade_bi_disc","moon_pendant","qilin_horn_charm","silk_pouch"};for(int i=0;i<ps.length;i++)h.assertTrue(ps[i].getPersistentData().getLong(cue(ids[i]))==previous[i],"Unequipping ends actual native passive cue: "+ids[i]);h.succeed();}finally{h.getLevel().setDayTime(day);h.getLevel().getServer().setDifficulty(difficulty,true);net.minecraftforge.common.MinecraftForge.EVENT_BUS.unregister(trace);close(bi,moon,horn,silk,cicada);}});
            }catch(Throwable failure){h.getLevel().setDayTime(day);h.getLevel().getServer().setDifficulty(difficulty,true);net.minecraftforge.common.MinecraftForge.EVENT_BUS.unregister(trace);close(bi,moon,horn,silk,cicada);throw failure;}});
        }catch(Throwable failure){h.getLevel().setDayTime(day);h.getLevel().getServer().setDifficulty(difficulty,true);net.minecraftforge.common.MinecraftForge.EVENT_BUS.unregister(trace);close(bi,moon,horn,silk,cicada);throw failure;}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_accessory_native_jade",setupTicks=20,timeoutTicks=80)
    public static void actualNativeHurtOnlyEmitsJadeWardAtLowHealthAndPreservesOriginal12PercentReduction(GameTestHelper h){
        var p=player(h,"jade_pendant","necklace",false);var z=attacker(h,p);
        h.startSequence().thenWaitUntil(()->h.assertTrue(z.tickCount>=2&&h.getLevel().getEntity(z.getUUID())==z,"Actual visible native damage calibration attacker"))
        .thenExecute(()->{try{
            float high=hurt(p,z);h.assertTrue(high>0&&!p.getPersistentData().contains(cue("jade_pendant")),"High-health real hit neither borrows ward cue nor low-health reduction");
            p.setHealth(p.getMaxHealth()*.25F);float low=hurt(p,z);long at=p.getPersistentData().getLong(cue("jade_pendant"));
            h.assertTrue(Math.abs(low/high-.88F)<.002&&p.getPersistentData().contains(cue("jade_pendant")),"Actual low-health native damage retains12percent reduction and emits dedicated ward once");
            hurt(p,z);h.assertTrue(p.getPersistentData().getLong(cue("jade_pendant"))==at,"Same-tick further native hit cannot flood accessory cues");
            SchoolCombatGameTests.equip(p,"necklace",ItemStack.EMPTY);hurt(p,z);h.assertTrue(p.getPersistentData().getLong(cue("jade_pendant"))==at,"Unequipped ward cannot produce another cue");h.succeed();
        }finally{z.discard();close(p);}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_accessory_native_gold",setupTicks=20,timeoutTicks=80)
    public static void actualNativeItemPickupPaysExistingFirstObtainMeritOnceAndEmitsGoldSealOnlyForWornCharm(GameTestHelper h){
        var p=player(h,"gold_seal_charm","charm",false);
        try{
            int before=DynastyStats.getMerit(p);ItemStack stack=new ItemStack(net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty","jade")));
            var first=new ItemEntity(h.getLevel(),p.getX(),p.getY(),p.getZ(),stack.copy());first.setNoPickUpDelay();h.getLevel().addFreshEntity(first);first.playerTouch(p);
            h.assertTrue(first.isRemoved()&&p.getInventory().contains(stack)&&DynastyStats.getMerit(p)>before&&p.getPersistentData().contains(cue("gold_seal_charm")),"Native ItemEntity.playerTouch consumes actual entity, gives item, pays original first reward and emits seal");
            int merit=DynastyStats.getMerit(p);long at=p.getPersistentData().getLong(cue("gold_seal_charm"));
            var repeated=new ItemEntity(h.getLevel(),p.getX(),p.getY(),p.getZ(),stack.copy());repeated.setNoPickUpDelay();h.getLevel().addFreshEntity(repeated);repeated.playerTouch(p);
            h.assertTrue(repeated.isRemoved()&&DynastyStats.getMerit(p)==merit&&p.getPersistentData().getLong(cue("gold_seal_charm"))==at,"Second native pickup keeps old first-obtain seen flag and cannot repay/reflash");
            SchoolCombatGameTests.equip(p,"charm",ItemStack.EMPTY);ItemStack silver=new ItemStack(net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty","silver_ingot")));
            var ordinary=new ItemEntity(h.getLevel(),p.getX(),p.getY(),p.getZ(),silver);ordinary.setNoPickUpDelay();h.getLevel().addFreshEntity(ordinary);ordinary.playerTouch(p);
            h.assertTrue(DynastyStats.getMerit(p)>merit&&p.getPersistentData().getLong(cue("gold_seal_charm"))==at,"New native resource still pays ordinary merit after unequip without a borrowed seal cue");h.succeed();
        }finally{close(p);}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_accessory_native_phoenix",setupTicks=20,timeoutTicks=100)
    public static void actualNativeFireHurtAndFatalHitKeepExistingImmunityLastStandAnd300SecondCooldown(GameTestHelper h){
        var p=player(h,"phoenix_feather_charm","head",false);var z=attacker(h,p);
        h.startSequence().thenWaitUntil(()->h.assertTrue(z.tickCount>=2,"Native stationary attacker visible"))
        .thenExecute(()->{
            float hp=p.getHealth();p.hurt(p.damageSources().onFire(),100);
            h.assertTrue(p.getHealth()==hp&&p.getPersistentData().contains(cue("phoenix_feather_charm")),"Original native fire attack immunity keeps health and emits dedicated feathers");
            h.runAfterDelay(22,()->{try{
                p.invulnerableTime=0;long now=h.getLevel().getGameTime();p.hurt(p.damageSources().mobAttack(z),20000);
                h.assertTrue(p.isAlive()&&Math.abs(p.getHealth()-p.getMaxHealth()*.15F)<.1&&EquipmentBehaviors.saved(p).getLong("lastStand")==now+6000&&p.getPersistentData().getLong(cue("phoenix_feather_charm"))==now,"Actual fatal native hit retains one15percent last stand,300second saved cooldown and refreshed short feathers");
                long until=EquipmentBehaviors.saved(p).getLong("lastStand");hurt(p,z);h.assertTrue(EquipmentBehaviors.saved(p).getLong("lastStand")==until,"Next ordinary native hit does not restart last-stand cooldown");h.succeed();
            }finally{z.discard();close(p);}});
        });
    }
}
