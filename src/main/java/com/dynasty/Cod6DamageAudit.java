package com.dynasty;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
/** Opt-in diagnostics: -Ddynasty.damageAudit=true. No gameplay mutation or permanent player reset. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class Cod6DamageAudit {
    private record Sample(LivingEntity victim,float initial,int hits){}
    private static final Map<UUID,Sample> TICK=new HashMap<>();
    @SubscribeEvent(priority=EventPriority.HIGHEST) public static void input(LivingHurtEvent e) {
        if(!Boolean.getBoolean("dynasty.damageAudit")||e.getEntity().level().isClientSide)return;
        var v=e.getEntity();var attacker=e.getSource().getEntity();
        var previous=TICK.get(v.getUUID());if(TICK.size()<256)TICK.put(v.getUUID(),new Sample(v,previous==null?v.getHealth():previous.initial,previous==null?1:previous.hits+1));
        Dynasty.LOGGER.info("[damage-audit input] tick={} victim={} source={} attacker={} raw={} hp={}/{} phase={} weapon={}",v.level().getGameTime(),v.getUUID(),e.getSource().getMsgId(),attacker==null?"none":attacker.getUUID(),e.getAmount(),v.getHealth(),v.getMaxHealth(),v instanceof com.dynasty.ritual.ZhenyuanSovereign b?b.ritualPhase():-1,
                attacker instanceof LivingEntity a?DynastyTrinkets.idOf(DynastySchoolCombat.firingWeapon(e.getSource(),a.getMainHandItem())):"none");
    }
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void output(LivingDamageEvent e) {
        if(Boolean.getBoolean("dynasty.damageAudit")&&!e.getEntity().level().isClientSide)
            Dynasty.LOGGER.info("[damage-audit armour-output] victim={} amount={} absorption={}",e.getEntity().getUUID(),e.getAmount(),e.getEntity().getAbsorptionAmount());
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e) {
        if(e.phase!=TickEvent.Phase.END||TICK.isEmpty())return;
        for(var sample:TICK.values())Dynasty.LOGGER.info("[damage-audit tick-total] victim={} events={} hpDelta={} remaining={}",sample.victim.getUUID(),sample.hits,sample.initial-sample.victim.getHealth(),sample.victim.getHealth());
        TICK.clear();
    }
    private Cod6DamageAudit(){}
}
