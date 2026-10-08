package com.dynasty.army;
import com.dynasty.*;
import com.dynasty.entity.ImperialSoldier;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
/** Existing equipped trinkets, scoped to the validated owner's own troops. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class ArmySupport {
    public static void snapshot(ServerPlayer p,List<ImperialSoldier> troops) {
        var ids=DynastyTrinkets.activeIds(p);
        for(var s:troops)if(ArmyRoster.valid(s,p)) {
            var n=s.getPersistentData();n.putBoolean("ArmyDrum",ids.contains("war_drum_charm"));
            n.putBoolean("ArmyBanner",ids.contains("war_banner_charm"));n.putBoolean("ArmyVolley",ids.contains("drum_beater"));
            n.putBoolean("ArmyShield",ids.contains("tiger_crest"));
        }
    }
    public static ServerPlayer owner(net.minecraft.world.damagesource.DamageSource source) {
        if(source.getEntity() instanceof ImperialSoldier s&&s.getOwner() instanceof ServerPlayer p&&p.isAlive()
                &&p.distanceToSqr(s)<64*64&&ArmyRoster.valid(s,p))return p;
        return source.getEntity() instanceof ServerPlayer p?p:null;
    }
    @SubscribeEvent(priority=EventPriority.HIGHEST) public static void hurt(LivingHurtEvent e) {
        if(e.getSource().getDirectEntity() instanceof net.minecraft.world.entity.projectile.AbstractArrow a
                &&a.getPersistentData().hasUUID("ArmyShotOwner")&&owner(e.getSource())==null) {e.setCanceled(true);return;}
        if(e.getSource().getEntity() instanceof ImperialSoldier soldier) {
            var p=owner(e.getSource());if(p==null&&soldier.getPersistentData().hasUUID("ArmySoldier")){e.setCanceled(true);return;}
            if(soldier.isAlliedTo(e.getEntity())){e.setCanceled(true);return;}
            if(p!=null){e.getEntity().setLastHurtByPlayer(p);if(soldier.getPersistentData().getBoolean("ArmyDrum"))e.setAmount(e.getAmount()*1.12f);}
        }
        if(e.getEntity() instanceof ImperialSoldier s&&s.getPersistentData().hasUUID("ArmySoldier")&&s.getPersistentData().getInt("ArmyRole")==2) {
            var attacker=e.getSource().getSourcePosition();
            if(attacker!=null) {
                double angle=Math.toRadians(s.getPersistentData().getFloat("ArmyYaw"));
                var front=new net.minecraft.world.phys.Vec3(-Math.sin(angle),0,Math.cos(angle));
                if(attacker.subtract(s.position()).normalize().dot(front)>.35)e.setAmount(e.getAmount()*(s.getPersistentData().getBoolean("ArmyShield")?.55f:.7f));
            }
        }
    }
    private ArmySupport(){}
}
