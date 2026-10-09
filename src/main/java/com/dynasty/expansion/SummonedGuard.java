package com.dynasty.expansion;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Bounded, expiring guards reuse the crab entity. Saved leases prevent unloaded-chunk duplication. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class SummonedGuard {
    public static void maintain(ServerPlayer p,int count) {
        if(!p.isInWater())return;
        var n=EquipmentBehaviors.saved(p);long now=p.level().getGameTime();
        if(now<n.getLong("guardsUntil"))return;
        n.putLong("guardsUntil",now+600);
        for(int i=0;i<count;i++) {
            var guard=SecondaryMobs.TYPES.get("crab_soldier").get().create(p.level());if(guard==null)continue;
            guard.moveTo(p.getX()+i*2-1,p.getY(),p.getZ()+1,0,0);
            if(!p.level().noCollision(guard))continue;
            guard.getPersistentData().putUUID("cod4Summoner",p.getUUID());guard.getPersistentData().putLong("cod4Expires",now+600);
            p.level().addFreshEntity(guard);
        }
    }
    public static void tick(SecondaryMob mob) {
        var n=mob.getPersistentData();var owner=mob.level().getPlayerByUUID(n.getUUID("cod4Summoner"));
        if(owner==null || !owner.isAlive() || EquipmentBehaviors.pieces(owner,"draco_king")<3 || mob.level().getGameTime()>=n.getLong("cod4Expires")){mob.discard();return;}
        if(mob.getTarget()==owner || mob.getTarget()!=null && mob.isAlliedTo(mob.getTarget()))mob.setTarget(null);
        if(mob.tickCount%20==0) {
            var targets=mob.level().getEntitiesOfClass(LivingEntity.class,mob.getBoundingBox().inflate(8),e->e instanceof Enemy && e!=mob && !e.isAlliedTo(owner) && !mob.isAlliedTo(e));
            mob.setTarget(targets.isEmpty()?null:targets.get(0));
            if(mob.getTarget()==null)mob.getNavigation().moveTo(owner,1.1);
        }
    }
    @SubscribeEvent public static void drops(LivingDropsEvent e){if(e.getEntity().getPersistentData().hasUUID("cod4Summoner"))e.getDrops().clear();}
    @SubscribeEvent public static void xp(LivingExperienceDropEvent e){if(e.getEntity().getPersistentData().hasUUID("cod4Summoner"))e.setDroppedExperience(0);}
    private SummonedGuard() { }
}
