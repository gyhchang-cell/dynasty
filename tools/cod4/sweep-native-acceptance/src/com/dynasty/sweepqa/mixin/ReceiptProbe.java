package com.dynasty.sweepqa.mixin;
import com.dynasty.sweepqa.*;
import com.dynasty.cod3.FangtianSweep;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraftforge.event.TickEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
import java.util.*;

/** Reads the actual queue immediately around the production consumer; never mutates it. */
@Mixin(value=FangtianSweep.class,remap=false)
public abstract class ReceiptProbe {
 private static Object field(Object r,String key)throws Exception{var f=r.getClass().getDeclaredField(key);f.setAccessible(true);return f.get(r);}
 private static void snapshot(String stage){if(Probe.SERVER.current().isEmpty())return;try{var f=FangtianSweep.class.getDeclaredField("PENDING");f.setAccessible(true);var list=(List<?>)f.get(null);var rows=new ArrayList<Object>();for(Object r:list){var p=(net.minecraft.server.level.ServerPlayer)field(r,"player");var t=(LivingEntity)field(r,"main");long tick=(Long)field(r,"tick"),now=p.level().getGameTime();var row=new LinkedHashMap<String,Object>();row.put("identity",System.identityHashCode(r));row.put("produced",tick);row.put("consumedNow",now);row.put("age",now-tick);row.put("actor",SweepQA.entity(p));row.put("main",SweepQA.entity(t));row.put("capturedLevelMatchesActor",field(r,"level")==p.serverLevel());row.put("capturedLevelMatchesMain",field(r,"level")==t.level());for(String k:List.of("health","secondary","primaryDamage"))row.put(k,field(r,k));row.put("stamp",p.getPersistentData().contains("cod3_confirmed_sweep_at")?p.getPersistentData().getLong("cod3_confirmed_sweep_at"):null);rows.add(row);}Probe.SERVER.event(stage,Map.of("cycle",SweepQA.cycle(),"now",SweepQA.actorTick(),"rows",rows));}catch(Exception ex){Probe.SERVER.event("probe-error",ex.toString());}}
 @Inject(method="begin",at=@At("RETURN"),remap=false) private static void begin(LivingEntity a,LivingEntity t,DamageSource s,CallbackInfoReturnable<FangtianSweep.Receipt> ci){if(!(a instanceof net.minecraft.server.level.ServerPlayer))return;Probe.SERVER.event("receipt-begin-result",Map.of("actor",SweepQA.entity(a),"main",SweepQA.entity(t),"receipt",ci.getReturnValue()!=null,"source",s.getMsgId(),"owner",SweepQA.entity(s.getEntity()),"direct",SweepQA.entity(s.getDirectEntity())));}
 @Inject(method="finish",at=@At("RETURN"),remap=false) private static void finish(FangtianSweep.Receipt r,CallbackInfo ci){if(r!=null)snapshot("receipt-finish-queue");}
 @Inject(method="tick",at=@At("HEAD"),remap=false) private static void before(TickEvent.ServerTickEvent e,CallbackInfo ci){if(e.phase==TickEvent.Phase.END)snapshot("receipt-before-exact-consumer");}
 @Inject(method="tick",at=@At("RETURN"),remap=false) private static void after(TickEvent.ServerTickEvent e,CallbackInfo ci){if(e.phase==TickEvent.Phase.END)snapshot("receipt-after-exact-consumer");}
}
