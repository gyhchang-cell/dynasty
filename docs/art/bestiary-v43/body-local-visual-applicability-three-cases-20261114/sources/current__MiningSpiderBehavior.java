package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;
import net.minecraft.nbt.CompoundTag;

/** Ceiling contact is physical support, not noclip; impact occurs once on the actual landing tick. */
public final class MiningSpiderBehavior implements ArmyBehaviors.Behavior {
    public static final double IMPACT_RADIUS=3;
    private final TemplateMob mob;
    private boolean dropping;
    MiningSpiderBehavior(TemplateMob mob){this.mob=mob;}
    static boolean supported(net.minecraft.world.level.Level level,Vec3 position,float height){
        for(double x:new double[]{-1,0,1})for(double z:new double[]{-1,0,1}){
            var p=BlockPos.containing(position.add(x,height+.05,z));
            if(!level.hasChunkAt(p)||!level.getBlockState(p).isFaceSturdy(level,p,net.minecraft.core.Direction.DOWN))return false;
        }return true;
    }
    public boolean allows(int id){return id==ArmySkills.SPIDER_DRILL||id==ArmySkills.SPIDER_DROP;}
    public String animation(int id){return id==ArmySkills.SPIDER_DROP?"drop":"attack";}
    public boolean canStart(int id,LivingEntity target){return id!=ArmySkills.SPIDER_DROP||mob.hanging()&&target.getY()<mob.getY()-.5&&target.position().subtract(mob.position()).horizontalDistanceSqr()<6.25;}
    public int choose(LivingEntity target,long now){return canStart(ArmySkills.SPIDER_DROP,target)&&mob.attack().ready(ArmySkills.SPIDER_DROP,now)?ArmySkills.SPIDER_DROP:mob.hanging()?0:ArmySkills.SPIDER_DRILL;}
    public void move(LivingEntity target,long now){if(!mob.hanging())mob.getNavigation().moveTo(target,.9);}
    public void tick(long now){
        if(dropping){
            mob.setHanging(false);mob.setNoGravity(false);
            if(mob.skillId()!=ArmySkills.SPIDER_DROP||now-mob.skillStartTime()>=80){dropping=false;return;}
            if(mob.onGround()){
                dropping=false;hit(IMPACT_RADIUS,360,9.8F,.6);
                if(!mob.isAlive())return;
                ((ServerLevel)mob.level()).sendParticles(ParticleTypes.POOF,mob.getX(),mob.getY()+.1,mob.getZ(),16,1,.1,1,.03);
                mob.playSound(net.minecraft.sounds.SoundEvents.GENERIC_EXPLODE,.7F,1.4F);mob.interruptAttack(20);
            }return;
        }
        boolean ceiling=supported(mob.level(),mob.position(),mob.getBbHeight());
        if(!ceiling&&mob.hanging()&&mob.skillId()==ArmySkills.SPIDER_DROP)mob.cancelAction();
        mob.setHanging(ceiling);mob.setNoGravity(ceiling);
        if(ceiling){
            var target=mob.getTarget();Vec3 travel=Vec3.ZERO;
            if(!mob.isNoAi()&&mob.skillId()==0&&mob.validEnemy(target)){
                var toward=target.position().subtract(mob.position()).multiply(1,0,1);
                if(toward.lengthSqr()>1){var step=toward.normalize().scale(.07);
                    if(supported(mob.level(),mob.position().add(step),mob.getBbHeight()))travel=step;}
            }mob.setDeltaMovement(travel);
        }
    }
    public void impact(SkillDefinition skill,int frame){
        if(skill.id()==ArmySkills.SPIDER_DROP){
            if(!mob.hanging())return;dropping=true;mob.setHanging(false);mob.setNoGravity(false);mob.setDeltaMovement(0,-.65,0);return;
        }hit(skill.maxRange(),skill.angleDegrees(),7,.3);
    }
    private void hit(double radius,double angle,float damage,double knockback){
        var direction=mob.attack().direction();
        for(var target:CombatGeometry.query((ServerLevel)mob.level(),mob.position(),direction,angle==360?CombatGeometry.Shape.CIRCLE:CombatGeometry.Shape.SECTOR,
            radius,1,angle,1.5,e->mob.validEnemy(e)&&mob.hasLineOfSight(e))){
            if(target.hurt(mob.damageSources().mobAttack(mob),damage))target.knockback(knockback,mob.getX()-target.getX(),mob.getZ()-target.getZ());
            if(!mob.isAlive())break;
        }
    }
    public CompoundTag save(){var t=new CompoundTag();t.putBoolean("Dropping",dropping);return t;}
    public void load(CompoundTag t){dropping=t.getBoolean("Dropping")&&mob.skillId()==ArmySkills.SPIDER_DROP&&mob.actionAge(0)<80;}
}
