package com.dynasty.blueprint;
import com.dynasty.blueprint.combat.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.effect.*;
import net.minecraft.world.phys.Vec3;
/** Sixteen visual segments share a single real body, ordinary collision and one combat clock. */
final class CentipedeBehavior implements ArmyBehaviors.Behavior {
    private final TemplateMob mob;
    CentipedeBehavior(TemplateMob mob){this.mob=mob;}
    public boolean allows(int id){return id==ArmySkills.CENTIPEDE_BITE||id==ArmySkills.CENTIPEDE_GAZE;}
    public String animation(int id){return id==ArmySkills.CENTIPEDE_GAZE?"gaze":"attack";}
    public int choose(LivingEntity target,long now){return mob.attack().ready(ArmySkills.CENTIPEDE_GAZE,now)?ArmySkills.CENTIPEDE_GAZE:ArmySkills.CENTIPEDE_BITE;}
    public void move(LivingEntity target,long now){if(!mob.hanging())mob.getNavigation().moveTo(target,1.1);}
    public void tick(long now){
        boolean ceiling=MiningSpiderBehavior.supported(mob.level(),mob.position(),mob.getBbHeight());
        mob.setHanging(ceiling);mob.setNoGravity(ceiling);
        if(ceiling){
            Vec3 movement=Vec3.ZERO;var target=mob.getTarget();
            if(!mob.isNoAi()&&mob.skillId()==0&&mob.validEnemy(target)){
                var d=target.position().subtract(mob.position()).multiply(1,0,1);
                if(d.lengthSqr()>1){var step=d.normalize().scale(.1);if(MiningSpiderBehavior.supported(mob.level(),mob.position().add(step),mob.getBbHeight()))movement=step;}
            }mob.setDeltaMovement(movement);
        }else if(mob.horizontalCollision&&mob.getTarget()!=null&&mob.skillId()==0)mob.setDeltaMovement(mob.getDeltaMovement().x,.18,mob.getDeltaMovement().z);
    }
    public void impact(SkillDefinition skill,int frame){
        if(skill.id()==ArmySkills.CENTIPEDE_GAZE){
            for(var target:((ServerLevel)mob.level()).getEntitiesOfClass(LivingEntity.class,mob.getBoundingBox().inflate(8),e->mob.validEnemy(e)&&mob.distanceToSqr(e)<=64&&mob.hasLineOfSight(e)&&LanternBatBehavior.facing(e,mob.position().add(0,mob.getBbHeight(),0)))){
                target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,60,3),mob);
                target.addEffect(new MobEffectInstance(BlueprintEntities.LANTERN_GLARE.get(),60,2),mob);
            }return;
        }
        for(var target:CombatGeometry.query((ServerLevel)mob.level(),mob.position(),mob.attack().direction(),CombatGeometry.Shape.SECTOR,2.8,1,70,1.3,e->mob.validEnemy(e)&&mob.hasLineOfSight(e))){
            if(target.hurt(mob.damageSources().indirectMagic(mob,mob),5))target.addEffect(new MobEffectInstance(MobEffects.POISON,60),mob);
            if(!mob.isAlive())break;
        }
    }
}
