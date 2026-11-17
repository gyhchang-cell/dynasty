package com.dynasty;
import com.dynasty.expansion.ExpansionContent;
import com.google.gson.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraftforge.gametest.*;

/** Real native clock; headless supplied inventory/target, no client or natural-acquisition claim. */
@GameTestHolder("dynasty_meteor_boundary_qa") @PrefixGameTestTemplate(false)
public final class MeteorBoundaryGameTests {
 @GameTest(template="bow_ritual_test",setupTicks=20,timeoutTicks=170)
 public static void hammerRejectsEveryInputUntilActualEightyTickCooldownThenPaysOnce(GameTestHelper h){
  var p=WeaponBoundaryGameTests.player(h,"meteor_hammer");var weapon=p.getMainHandItem();
  var cow=new Cow(EntityType.COW,h.getLevel());cow.setPos(p.position().add(2,0,1));cow.setNoAi(true);cow.setNoGravity(true);cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(100000);cow.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);cow.setHealth(100000);h.getLevel().addFreshEntity(cow);
  int[] phase={0};long[] at={0};double[] firstDamage={0};var inputs=new JsonArray();
  h.onEachTick(()->{
   if(p.isRemoved())return;p.doTick();cow.setPos(p.position().add(2,0,1));cow.setDeltaMovement(0,0,0);long now=h.getLevel().getGameTime();
   try{
    if(phase[0]==0){p.gameMode.useItem(p,h.getLevel(),weapon,InteractionHand.MAIN_HAND);at[0]=now;phase[0]=1;}
    else if(phase[0]==1&&now-at[0]==24){p.releaseUsingItem();firstDamage[0]=100000-cow.getHealth();h.assertTrue(firstDamage[0]>0&&weapon.getDamageValue()==3&&p.getCooldowns().isOnCooldown(ExpansionContent.HAMMER.get()),"First native fully charged hammer pays3 durability and starts80tick cooldown");at[0]=now;phase[0]=2;p.gameMode.useItem(p,h.getLevel(),weapon,InteractionHand.MAIN_HAND);h.assertTrue(!p.isUsingItem(),"Same-tick second native use rejected");}
    else if(phase[0]==2){boolean cooling=p.getCooldowns().isOnCooldown(ExpansionContent.HAMMER.get());p.gameMode.useItem(p,h.getLevel(),weapon,InteractionHand.MAIN_HAND);var row=new JsonObject();row.addProperty("elapsed_server_ticks",now-at[0]);row.addProperty("cooldown_before_use",cooling);row.addProperty("using_after_native_input",p.isUsingItem());row.addProperty("durability",weapon.getDamageValue());inputs.add(row);
     h.assertTrue(weapon.getDamageValue()==3&&Math.abs(100000-cow.getHealth()-firstDamage[0])<.1,"Repeated input neither repeats damage nor durability payment");
     if(cooling)h.assertTrue(!p.isUsingItem(),"All still-cooling native input rejected");else{h.assertTrue(now-at[0]==80&&p.isUsingItem(),"Native use resumes exactly80 actual server ticks later: "+row);at[0]=now;phase[0]=3;}
    }else if(phase[0]==3&&now-at[0]==24){p.releaseUsingItem();h.assertTrue(weapon.getDamageValue()==6&&Math.abs((100000-cow.getHealth())-firstDamage[0]*2)<.2,"Second legitimate full charge repeats original damage and pays3 once");var out=new JsonObject();out.add("native_tick_inputs",inputs);out.addProperty("first_damage",firstDamage[0]);out.addProperty("final_health_loss",100000-cow.getHealth());out.addProperty("final_durability",weapon.getDamageValue());out.addProperty("pass",true);WeaponBoundaryGameTests.record("meteor_actual_80_tick_cooldown",out);cow.discard();WeaponBoundaryGameTests.close(p);h.succeed();}
   }catch(Throwable ex){var out=new JsonObject();out.add("native_tick_inputs",inputs);out.addProperty("pass",false);out.addProperty("failure",ex.toString());WeaponBoundaryGameTests.record("meteor_actual_80_tick_cooldown",out);cow.discard();WeaponBoundaryGameTests.close(p);throw ex;}
  });
 }
}
