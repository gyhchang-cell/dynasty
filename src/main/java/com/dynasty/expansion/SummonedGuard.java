package com.dynasty.expansion;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Three pieces lease one shrimp; four lease shrimp plus crab. No paid-roster records are involved. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class SummonedGuard {
    public static void maintain(ServerPlayer p,int count) {
        int pieces=EquipmentBehaviors.pieces(p,"draco_king");count=Math.min(pieces>=4?2:1,Math.max(0,count));
        if(pieces<3||count==0||!p.isInWater())return;
        var n=EquipmentBehaviors.saved(p);long now=p.level().getGameTime();
        if(now<n.getLong("guardsUntil"))return;
        long generation=n.getLong("guardGeneration")+1;
        int spawned=0;
        for(int i=0;i<count;i++) {
            var guard=(i==0?SecondaryMobs.SHRIMP.get():SecondaryMobs.TYPES.get("crab_soldier").get()).create(p.level());if(guard==null)continue;
            boolean placed=false;
            // A blocked preferred tile must not consume the entire thirty-second lease.
            for(int ring=1;ring<=3&&!placed;ring++)for(int x=-ring;x<=ring&&!placed;x++)for(int z=-ring;z<=ring&&!placed;z++){
                if(Math.max(Math.abs(x),Math.abs(z))!=ring)continue;
                var pos=p.blockPosition().offset(x,0,z);
                if(!p.level().hasChunkAt(pos)||!p.level().getFluidState(pos).is(net.minecraft.tags.FluidTags.WATER))continue;
                guard.moveTo(pos.getX()+.5,p.getY(),pos.getZ()+.5,0,0);
                placed=p.level().noCollision(guard);
            }
            if(!placed)continue;
            guard.getPersistentData().putUUID("cod4Summoner",p.getUUID());guard.getPersistentData().putLong("cod4Expires",now+600);
            guard.getPersistentData().putLong("cod4GuardGeneration",generation);guard.getPersistentData().putInt("cod4MinPieces",i==0?3:4);
            if(p.level().addFreshEntity(guard))spawned++;
        }
        if(spawned>0){n.putLong("guardsUntil",now+600);n.putLong("guardGeneration",generation);}
    }
    public static void tick(SecondaryMob mob) {
        var n=mob.getPersistentData();var owner=mob.level().getPlayerByUUID(n.getUUID("cod4Summoner"));
        int minimum=n.contains("cod4MinPieces")?n.getInt("cod4MinPieces"):3;
        if(owner==null || !owner.isAlive() || EquipmentBehaviors.pieces(owner,"draco_king")<minimum || mob.level().getGameTime()>=n.getLong("cod4Expires")
                ||n.getLong("cod4GuardGeneration")!=EquipmentBehaviors.saved(owner).getLong("guardGeneration")){mob.discard();return;}
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
