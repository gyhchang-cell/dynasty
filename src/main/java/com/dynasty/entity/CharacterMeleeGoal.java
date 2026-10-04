package com.dynasty.entity;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.InteractionHand;
import java.util.UUID;

/** Server-authoritative, readable melee windup. No new boss skills or damage values. */
public final class CharacterMeleeGoal extends MeleeAttackGoal {
    private final DynastyHumanoidMob fighter;
    private long start=-1,next;
    private UUID victim;
    private boolean resolved;
    public CharacterMeleeGoal(DynastyHumanoidMob fighter,double speed) {super(fighter,speed,true);this.fighter=fighter;}
    @Override protected void checkAndPerformAttack(LivingEntity target,double distance) {
        long now=fighter.level().getGameTime();int duration=fighter.characterAttackDuration();
        if(start>=0) {
            long age=now-start;int impact=Math.round(duration*.5f);
            if(!resolved&&age>=impact) {
                resolved=true;
                if(age<=impact+1&&target.isAlive()&&target.getUUID().equals(victim)&&distance<=getAttackReachSqr(target)
                        &&fighter.getSensing().hasLineOfSight(target))fighter.doHurtTarget(target);
            }
            if(age<duration)return;
            start=-1;victim=null;
        }
        if(now>=next&&distance<=getAttackReachSqr(target)&&fighter.getSensing().hasLineOfSight(target)) {
            start=now;next=now+duration+6;victim=target.getUUID();resolved=false;
            fighter.beginCharacterAttack();fighter.swing(InteractionHand.MAIN_HAND);
        }
    }
    @Override public void stop(){super.stop();start=-1;victim=null;resolved=true;fighter.cancelCharacterAttack();}
}
