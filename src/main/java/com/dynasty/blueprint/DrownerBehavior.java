package com.dynasty.blueprint;
import com.dynasty.blueprint.combat.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
/** The same entity melts in place; no world water replacement and no forced sinking/teleport. */
final class DrownerBehavior implements ArmyBehaviors.Behavior {
    private final TemplateMob mob;
    DrownerBehavior(TemplateMob mob){this.mob=mob;}
    static boolean deepWater(Level level,BlockPos p){return level.hasChunkAt(p)&&level.getFluidState(p).is(FluidTags.WATER)&&level.getFluidState(p.below()).is(FluidTags.WATER);}
    public boolean allows(int id){return id==ArmySkills.DROWNER_WHIP||id==ArmySkills.DROWNER_POOL;}
    public String animation(int id){return id==ArmySkills.DROWNER_POOL?"pool":"attack";}
    public boolean canStart(int id,LivingEntity target){return deepWater(mob.level(),mob.blockPosition())&&(id!=ArmySkills.DROWNER_POOL||target.isInWater()&&mob.position().subtract(target.position()).horizontalDistanceSqr()<4);}
    public int choose(LivingEntity target,long now){return canStart(ArmySkills.DROWNER_POOL,target)&&mob.attack().ready(ArmySkills.DROWNER_POOL,now)?ArmySkills.DROWNER_POOL:ArmySkills.DROWNER_WHIP;}
    public void move(LivingEntity target,long now){
        if(target.isInWater()&&deepWater(mob.level(),target.blockPosition()))mob.getNavigation().moveTo(target,.9);else mob.getNavigation().stop();
    }
    public void tick(long now){
        if(mob.skillId()!=ArmySkills.DROWNER_POOL)return;
        if(!deepWater(mob.level(),mob.blockPosition())){mob.cancelAction();return;}
        double age=mob.actionAge(0);if(age<24||age>=84)return;
        mob.setDeltaMovement(Vec3.ZERO);if(now%4!=0)return;
        var level=(ServerLevel)mob.level();var centre=mob.attack().origin();
        for(var target:level.getEntitiesOfClass(LivingEntity.class,new AABB(centre.add(-2,-1,-2),centre.add(2,2,2)),e->mob.validEnemy(e)&&e.isInWater()&&mob.hasLineOfSight(e))){
            target.addEffect(new MobEffectInstance(BlueprintEntities.DROWNING_BIND.get(),6),mob);
            // Reserve air instead of stacking suffocation: escape remains possible by swimming sideways.
            if(target.getAirSupply()>40)target.setAirSupply(Math.max(40,target.getAirSupply()-2));
        }
        level.sendParticles(ParticleTypes.BUBBLE,centre.x,centre.y+.1,centre.z,6,1.8,.1,1.8,0);
        var target=mob.resolve(mob.attack().target());
        if(!mob.validEnemy(target)||!target.isInWater()||Math.abs(target.getX()-centre.x)>2||Math.abs(target.getZ()-centre.z)>2)mob.interruptAttack(20);
    }
    public void impact(SkillDefinition skill,int frame){
        if(skill.id()!=ArmySkills.DROWNER_WHIP)return;
        for(var target:CombatGeometry.query((ServerLevel)mob.level(),mob.position(),mob.attack().direction(),CombatGeometry.Shape.SECTOR,3.5,1,65,1.5,e->mob.validEnemy(e)&&mob.hasLineOfSight(e))){
            target.hurt(mob.damageSources().mobAttack(mob),5);if(!mob.isAlive())break;
        }
    }
    public void died(net.minecraft.world.damagesource.DamageSource source){((ServerLevel)mob.level()).sendParticles(ParticleTypes.SPLASH,mob.getX(),mob.getY()+.3,mob.getZ(),20,.8,.2,.8,.02);}
}
