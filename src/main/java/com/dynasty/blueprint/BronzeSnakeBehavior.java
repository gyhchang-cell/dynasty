package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.phys.Vec3;

/** Two heads, one body/health pool; direction and breath cone lock before contact. */
final class BronzeSnakeBehavior implements ArmyBehaviors.Behavior {
    private final TemplateMob mob;
    private long breathUntil;
    BronzeSnakeBehavior(TemplateMob mob){this.mob=mob;}
    static boolean breath(int id){return id==ArmySkills.BRONZE_FIRE||id==ArmySkills.BRONZE_POISON;}
    public boolean allows(int id){return id>=ArmySkills.BRONZE_FRONT_STAB&&id<=ArmySkills.BRONZE_POISON;}
    public String animation(int id){return switch(id){case ArmySkills.BRONZE_REAR_STAB->"rear_attack";case ArmySkills.BRONZE_FIRE->"fire";case ArmySkills.BRONZE_POISON->"poison";default->"attack";};}
    private boolean behind(LivingEntity target){
        Vec3 forward=Vec3.directionFromRotation(0,mob.yBodyRot);
        return target.position().subtract(mob.position()).multiply(1,0,1).dot(forward)<0;
    }
    public boolean canStart(int id,LivingEntity target){return !breath(id)||mob.level().getGameTime()>=breathUntil;}
    public void started(int id,LivingEntity target){if(breath(id))breathUntil=mob.level().getGameTime()+180;}
    public int choose(LivingEntity target,long now){
        boolean rear=behind(target);
        if(now>=breathUntil&&mob.distanceToSqr(target)<=25)return rear?ArmySkills.BRONZE_POISON:ArmySkills.BRONZE_FIRE;
        return rear?ArmySkills.BRONZE_REAR_STAB:ArmySkills.BRONZE_FRONT_STAB;
    }
    public void move(LivingEntity target,long now){mob.getNavigation().moveTo(target,.9);}
    public void impact(SkillDefinition skill,int frame){
        var direction=mob.attack().direction();boolean cloud=breath(skill.id());
        for(var target:CombatGeometry.query((ServerLevel)mob.level(),mob.attack().origin(),direction,CombatGeometry.Shape.SECTOR,
            skill.maxRange(),1,skill.angleDegrees(),1.3,e->mob.validEnemy(e)&&mob.hasLineOfSight(e))){
            if(target.hurt(mob.damageSources().mobAttack(mob),cloud?2.4F:6F)){
                if(skill.id()==ArmySkills.BRONZE_FIRE)target.setSecondsOnFire(2);
                if(skill.id()==ArmySkills.BRONZE_POISON)target.addEffect(new MobEffectInstance(MobEffects.POISON,45),mob);
            }
            if(!mob.isAlive()||mob.attack().current()!=skill)break;
        }
    }
    public CompoundTag save(){var tag=new CompoundTag();tag.putLong("BreathUntil",breathUntil);return tag;}
    public void load(CompoundTag tag){breathUntil=Math.min(tag.getLong("BreathUntil"),mob.level().getGameTime()+180);}
}
