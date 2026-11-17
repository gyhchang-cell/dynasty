package com.dynasty.weaponqa.mixin;
import com.dynasty.weaponqa.Probe;
import com.dynasty.cod3.FangtianSweep;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.damagesource.*;
@Mixin(targets="com.dynasty.cod3.FangtianSweep",remap=false)
public abstract class SweepSourceProbe {
 @Inject(method="begin",at=@At("HEAD"),remap=false)
 private static void qa$begin(LivingEntity a,LivingEntity t,DamageSource source,CallbackInfoReturnable<FangtianSweep.Receipt> ci){
  var m=new java.util.LinkedHashMap<String,Object>();m.put("now",a.level().getGameTime());m.put("sourcePlayerAttack",source.is(DamageTypes.PLAYER_ATTACK));m.put("directActor",source.getDirectEntity()==a);m.put("synthetic",com.dynasty.DynastyTrinketOnHit.isSyntheticDamage());
  if(a instanceof net.minecraft.server.level.ServerPlayer p){m.put("observedPrimary",com.dynasty.DynastySchoolCombat.observedPrimary(p,t));m.put("primaryItem",net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(com.dynasty.DynastySchoolCombat.primaryStack(p,t).getItem()).toString());}
  try{var f=FangtianSweep.class.getDeclaredField("STARTS");f.setAccessible(true);var starts=(java.util.List<?>)f.get(null);var list=new java.util.ArrayList<Object>();for(Object s:starts){var d=new java.util.LinkedHashMap<String,Object>();for(String k:java.util.List.of("player","main","tick")){var sf=s.getClass().getDeclaredField(k);sf.setAccessible(true);var v=sf.get(s);d.put(k,v instanceof net.minecraft.world.entity.Entity e?e.getId():v);}list.add(d);}m.put("nativeStarts",list);}catch(Exception ex){m.put("error",ex.toString());}
  Probe.event("native-sweep-begin",m);
 }
 @Inject(method="begin",at=@At("RETURN"),remap=false)
 private static void qa$return(LivingEntity a,LivingEntity t,DamageSource source,CallbackInfoReturnable<FangtianSweep.Receipt> ci){Probe.event("native-sweep-begin-result",java.util.Map.of("receipt",ci.getReturnValue()!=null,"now",a.level().getGameTime()));}
}
