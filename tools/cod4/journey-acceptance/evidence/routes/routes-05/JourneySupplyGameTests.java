package com.dynasty.expansion;

import com.dynasty.DynastyKeju;
import com.dynasty.DynastyTrinketOnHit;
import java.util.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.*;
import net.minecraft.world.level.GameRules;
import net.minecraftforge.gametest.*;
import static com.dynasty.expansion.JourneyRouteGameTests.*;

/** Actual native use ticks from paid recipe output; no direct finishUsingItem or clock backdating. */
@GameTestHolder("dynasty_journey_routes_qa") @PrefixGameTestTemplate(false)
public final class JourneySupplyGameTests {
    @GameTestGenerator public static Collection<TestFunction> cases() {
        var tests=new ArrayList<TestFunction>();int n=0xe;
        for(String id:List.of("regen_pill","qi_pill","antidote_pill","zhuangyuan_wine","marching_wine","soul_incense","guide_incense","army_ration")) {
            int quest=n++;
            tests.add(new TestFunction("route_supplies","supply_route."+id,"dynasty_journey_routes_qa:bow_ritual_test",1320,20,true,h->exercise(h,id,quest)));
        }
        return tests;
    }
    static void exercise(GameTestHelper h,String id,int quest) {
        var r=new Route(h,"food_"+id);var p=r.p;
        r.report.addProperty("food_scope","Paid recipe -> original FTB craft objective -> cancelled native use -> full native use -> original effect/cooldown expiry. Script drives one ServerPlayer.doTick per world tick; no rendered animation/network/client claim.");
        r.prefix(q(quest),Set.of());r.craft("dynasty:cod4/"+id);r.submit(q(quest));
        if(r.count("dynasty:"+id)<2)r.craft("dynasty:cod4/"+id);
        int craftedTotal=r.count("dynasty:"+id);
        var held=r.take("dynasty:"+id);held.grow(1);r.take("dynasty:"+id);
        var displaced=p.getMainHandItem().copy();p.setItemInHand(InteractionHand.MAIN_HAND,held);
        if(!displaced.isEmpty())h.assertTrue(p.getInventory().add(displaced),"Preserve displaced carried stock when selecting paid food");
        h.assertTrue(r.count("dynasty:"+id)==craftedTotal,"Selecting food must not delete or duplicate paid recipe output");
        p.setNoGravity(true);p.setOnGround(true);h.getLevel().addNewPlayer(p);
        h.getLevel().getGameRules().getRule(GameRules.RULE_NATURAL_REGENERATION).set(false,h.getLevel().getServer());
        p.getAttribute(Attributes.MAX_HEALTH).setBaseValue(100);p.setHealth(40);p.getFoodData().setFoodLevel(10);p.getFoodData().setSaturation(0);
        if(id.equals("antidote_pill"))p.addEffect(new MobEffectInstance(MobEffects.POISON,2000,0));
        if(id.equals("soul_incense")){ExpansionEffects.apply(p,ExpansionEffects.YIN,2000);ExpansionEffects.apply(p,ExpansionEffects.SOUL,2000);}
        var mob=new Zombie(h.getLevel());mob.setNoAi(true);mob.setNoGravity(true);mob.setSilent(true);mob.setPos(p.position().add(2,0,0));
        mob.getAttribute(Attributes.MAX_HEALTH).setBaseValue(5000);mob.setHealth(5000);h.getLevel().addFreshEntity(mob);r.cleanup.add(mob::discard);
        if(id.equals("soul_incense"))mob.setTarget(p);
        var fixture=r.row("qa_scenario");fixture.addProperty("description","100 max/40 current HP, hunger10, zero saturation, natural regeneration disabled; no-AI undead target; poison or Yin/Soul only for respective remedy. No duration/deadline fields changed.");
        var metrics=new com.google.gson.JsonObject();r.report.add("food_measurements",metrics);
        int[] tick={0};long[] started={-1},finished={-1};float[] beforeHp={0},baseline={0};
        int total=r.count("dynasty:"+id);Item food=held.getItem();
        metrics.addProperty("native_use_duration",held.getUseDuration());metrics.addProperty("native_use_animation",held.getUseAnimation().name());
        h.assertTrue(held.getUseDuration()==32,"Original full food/drink use duration");
        h.assertTrue(held.getUseAnimation()==(id.endsWith("wine")?UseAnim.DRINK:UseAnim.EAT),"Original use animation enum (not a visual claim)");
        h.onEachTick(()->{
            if(p.isRemoved())return;
            p.setOnGround(true);p.doTick();p.setOnGround(true);int t=++tick[0];
            if(t==1){
                if(id.equals("marching_wine"))baseline[0]=hit(p,mob);
                p.gameMode.useItem(p,h.getLevel(),p.getMainHandItem(),InteractionHand.MAIN_HAND);
                h.assertTrue(p.isUsingItem(),"Native survival use really started");
            }
            if(t==9){
                h.assertTrue(p.isUsingItem()&&r.count("dynasty:"+id)==total&&!p.getCooldowns().isOnCooldown(food),"Partial use has no payment or cooldown");
                p.stopUsingItem();metrics.addProperty("cancelled_after_native_ticks",8);metrics.addProperty("cancelled_use_kept_all_items",true);
            }
            if(t==11){
                beforeHp[0]=p.getHealth();p.gameMode.useItem(p,h.getLevel(),p.getMainHandItem(),InteractionHand.MAIN_HAND);
                h.assertTrue(p.isUsingItem(),"Native use restarts after cancellation");started[0]=h.getLevel().getGameTime();
            }
            if(started[0]>=0&&finished[0]<0&&!p.isUsingItem()) {
                long elapsed=h.getLevel().getGameTime()-started[0];h.assertTrue(elapsed==32,"Exactly32 actual world ticks complete native use, got "+elapsed);
                finished[0]=h.getLevel().getGameTime();h.assertTrue(r.count("dynasty:"+id)==total-1,"One paid crafted output consumed");
                h.assertTrue(p.getCooldowns().isOnCooldown(food),"Native use installed original cooldown");
                metrics.addProperty("completed_use_server_ticks",elapsed);metrics.addProperty("consumed_count",1);
                metrics.addProperty("health_before",beforeHp[0]);metrics.addProperty("health_after",p.getHealth());
                switch(id) {
                    case "regen_pill" -> {h.assertTrue(p.getHealth()>=beforeHp[0]+11.99F&&p.hasEffect(MobEffects.REGENERATION),"Actual12percent heal plus native regeneration");metrics.addProperty("regeneration_ticks",p.getEffect(MobEffects.REGENERATION).getDuration());}
                    case "qi_pill" -> {h.assertTrue(EquipmentBehaviors.qiActive(p)&&p.getPersistentData().getInt("cod4Rage")==2,"Actual pill enables shared Qi and adds two rage");h.assertTrue(DynastyTrinketOnHit.advanceCombo(p,mob)==1,"Start existing shared combo");}
                    case "antidote_pill" -> h.assertTrue(!p.hasEffect(MobEffects.POISON),"Native poison removed on use");
                    case "zhuangyuan_wine" -> {h.assertTrue(DynastyKeju.answerDurationMillis(p)==36000,"Original exam answer duration really gains20percent");metrics.addProperty("exam_answer_ms_active",DynastyKeju.answerDurationMillis(p));}
                    case "marching_wine" -> {float boosted=hit(p,mob);h.assertTrue(boosted>baseline[0]&&p.hasEffect(ExpansionEffects.YANG.get())&&p.hasEffect(MobEffects.CONFUSION),"Native undead primary hit gains Yang damage with original nausea cost");metrics.addProperty("baseline_primary_damage",baseline[0]);metrics.addProperty("yang_primary_damage",boosted);}
                    case "soul_incense" -> h.assertTrue(!p.hasEffect(ExpansionEffects.YIN.get())&&!p.hasEffect(ExpansionEffects.SOUL.get())&&mob.getTarget()==null,"Actual statuses cleansed and nearby undead target cleared");
                    case "guide_incense" -> {var mark=p.getPersistentData().getCompound("cod4Guide");metrics.addProperty("natural_structure_locator_found",!mark.isEmpty());if(!mark.isEmpty()){h.assertTrue(mark.getLong("Until")==h.getLevel().getGameTime()+1200,"Original real locator created timed marker");metrics.addProperty("located_block_pos",mark.getLong("Target"));}}
                    case "army_ration" -> {h.assertTrue(p.getFoodData().getFoodLevel()==20&&p.hasEffect(MobEffects.SATURATION),"Original nutrition10 and200tick saturation");metrics.addProperty("food_after",p.getFoodData().getFoodLevel());metrics.addProperty("saturation_effect_ticks",p.getEffect(MobEffects.SATURATION).getDuration());}
                }
                p.gameMode.useItem(p,h.getLevel(),p.getMainHandItem(),InteractionHand.MAIN_HAND);
                h.assertTrue(!p.isUsingItem()&&r.count("dynasty:"+id)==total-1,"Original cooldown blocks immediate native repeat use");
                var row=r.row("native_food_use_completed");row.addProperty("item","dynasty:"+id);row.addProperty("elapsed_server_ticks",elapsed);r.flush();
            }
            if(finished[0]<0)return;long elapsed=h.getLevel().getGameTime()-finished[0];
            if(elapsed==2&&id.equals("qi_pill"))h.assertTrue(DynastyTrinketOnHit.advanceCombo(p,mob)==3,"Existing shared combo advances by two after actual pill use");
            if(elapsed==10&&id.equals("antidote_pill"))p.addEffect(new MobEffectInstance(MobEffects.POISON,2000,0));
            if(elapsed==12&&id.equals("antidote_pill"))h.assertTrue(!p.hasEffect(MobEffects.POISON),"Native tick remedy clears reapplied poison inside600tick window");
            if(elapsed==102) {
                if(id.equals("regen_pill"))h.assertTrue(!p.hasEffect(MobEffects.REGENERATION)&&p.getHealth()>beforeHp[0]+12,"Actual regeneration healed over time then expired");
                if(id.equals("marching_wine")){h.assertTrue(!p.hasEffect(ExpansionEffects.YANG.get())&&!p.hasEffect(MobEffects.CONFUSION),"Both native timed effects expired");float after=hit(p,mob);h.assertTrue(Math.abs(after-baseline[0])<.02,"Post-expiry native primary damage restored");metrics.addProperty("expired_primary_damage",after);}
            }
            if(elapsed==202) {
                if(id.equals("qi_pill")) {
                    metrics.addProperty("qi_active_after202ticks",EquipmentBehaviors.qiActive(p));
                    metrics.addProperty("rage_after202ticks",p.getPersistentData().getInt("cod4Rage"));
                    h.assertTrue(!EquipmentBehaviors.qiActive(p),"Original Qi deadline ends the combo benefit at200ticks");
                }
                if(id.equals("army_ration"))h.assertTrue(!p.hasEffect(MobEffects.SATURATION),"Saturation expires after actual200ticks");
            }
            // Original refresh() prunes idle rage only every20 player ticks; it is not an immediate deadline callback.
            if(elapsed==222&&id.equals("qi_pill")) {
                metrics.addProperty("rage_after222ticks",p.getPersistentData().getInt("cod4Rage"));
                h.assertTrue(p.getPersistentData().getInt("cod4Rage")==0,"Original periodic equipment refresh cleans expired pill rage");
            }
            if(elapsed==602&&id.equals("antidote_pill"))p.addEffect(new MobEffectInstance(MobEffects.POISON,2000,0));
            if(elapsed==604&&id.equals("antidote_pill"))h.assertTrue(p.hasEffect(MobEffects.POISON),"Poison is accepted after actual600tick protection expires");
            int cooldown=id.equals("guide_incense")?1200:200;
            if(elapsed==cooldown-2)h.assertTrue(p.getCooldowns().isOnCooldown(food),"Cooldown lasts full original interval");
            if(elapsed==cooldown+2) {h.assertTrue(!p.getCooldowns().isOnCooldown(food),"Cooldown expires through native ticks");metrics.addProperty("cooldown_expired_by_ticks",elapsed);}
            int end=switch(id){case "guide_incense","zhuangyuan_wine"->1222;case "antidote_pill"->610;case "qi_pill"->230;default->210;};
            if(elapsed==end) {
                if(id.equals("zhuangyuan_wine")){h.assertTrue(DynastyKeju.answerDurationMillis(p)==30000,"Actual1200ticks remove exam timing benefit");metrics.addProperty("exam_answer_ms_expired",DynastyKeju.answerDurationMillis(p));}
                if(id.equals("guide_incense"))h.assertTrue(!p.getPersistentData().contains("cod4Guide"),"Native player tick removes elapsed marker");
                h.assertTrue(r.count("dynasty:"+id)==total-1,"Expiry never consumes or duplicates another paid item");
                var row=r.row("native_food_lifetime_complete");row.addProperty("item","dynasty:"+id);row.addProperty("observed_server_ticks_after_use",elapsed);r.finish();
            }
        });
    }
    static float hit(net.minecraft.server.level.ServerPlayer p,Zombie target) {
        target.invulnerableTime=0;float before=target.getHealth();p.setSprinting(false);p.attack(target);return before-target.getHealth();
    }
}
