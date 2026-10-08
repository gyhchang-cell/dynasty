package com.dynasty.blueprint;
import com.dynasty.blueprint.combat.*;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.effect.*;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.*;
import java.util.UUID;
/** A collision-respecting grab with a hard altitude/time cap, crouch escape and independent fall protection. */
final class YechaBehavior implements ArmyBehaviors.Behavior {
    private final TemplateMob mob;
    private Vec3 dive=Vec3.ZERO;
    private UUID captive;
    private double baseY;
    private long releaseAt;
    private boolean contacted;
    YechaBehavior(TemplateMob mob){this.mob=mob;}
    public boolean allows(int id){return id==ArmySkills.YECHA_SWIPE||id==ArmySkills.YECHA_GRAB;}
    public String animation(int id){return id==ArmySkills.YECHA_GRAB?"grab":"attack";}
    public int choose(LivingEntity target,long now){return mob.getY()>target.getY()+1&&mob.attack().ready(ArmySkills.YECHA_GRAB,now)?ArmySkills.YECHA_GRAB:ArmySkills.YECHA_SWIPE;}
    public void started(int id,LivingEntity target){if(id==ArmySkills.YECHA_GRAB){release();contacted=false;dive=target.getBoundingBox().getCenter().subtract(mob.position()).normalize();}}
    public void move(LivingEntity target,long now){
        var p=target.position().add(0,2.5,0);var box=mob.getType().getDimensions().makeBoundingBox(p.x,p.y,p.z);
        if(!mob.level().hasChunkAt(BlockPos.containing(p))||!mob.level().noCollision(mob,box))return;
        var path=mob.getNavigation().createPath(p.x,p.y,p.z,0);if(path!=null&&path.canReach())mob.getNavigation().moveTo(path,.9);
    }
    public void impact(SkillDefinition skill,int frame){
        if(skill.id()!=ArmySkills.YECHA_SWIPE)return;
        for(var target:CombatGeometry.query((ServerLevel)mob.level(),mob.position(),mob.attack().direction(),CombatGeometry.Shape.SECTOR,3.2,1,105,1.5,e->mob.validEnemy(e)&&mob.hasLineOfSight(e))){target.hurt(mob.damageSources().mobAttack(mob),7);if(!mob.isAlive())break;}
    }
    public void tick(long now){
        if(captive!=null){
            var target=mob.resolve(captive);
            if(!mob.validEnemy(target)||mob.skillId()!=ArmySkills.YECHA_GRAB||target.isShiftKeyDown()||mob.distanceToSqr(target)>16||!mob.hasLineOfSight(target)||target.getY()>=baseY+6){release();return;}
            if(now>=releaseAt){target.hurt(mob.damageSources().mobAttack(mob),4);target.setDeltaMovement(0,-.2,0);target.hurtMarked=true;release();return;}
            var ceiling=mob.level().clip(new ClipContext(target.getEyePosition(),target.getEyePosition().add(0,.6,0),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,mob));
            if(ceiling.getType()!=HitResult.Type.MISS){release();return;}
            mob.setDeltaMovement(0,mob.getY()<baseY+7?.17:0,0);
            var d=mob.position().subtract(target.position()).multiply(1,0,1);var side=d.lengthSqr()>.25?d.normalize().scale(.08):Vec3.ZERO;
            target.setDeltaMovement(side.x,Math.min(.18,baseY+6-target.getY()),side.z);target.hurtMarked=true;target.fallDistance=0;return;
        }
        if(mob.skillId()!=ArmySkills.YECHA_GRAB)return;
        double age=mob.actionAge(0);if(age<20){mob.setDeltaMovement(Vec3.ZERO);return;}if(age>=36||contacted){mob.setDeltaMovement(mob.getDeltaMovement().scale(.5));return;}
        Vec3 step=dive.scale(.7);var ray=mob.level().clip(new ClipContext(mob.getEyePosition(),mob.getEyePosition().add(step),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,mob));
        if(ray.getType()!=HitResult.Type.MISS||mob.horizontalCollision||mob.verticalCollision){contacted=true;mob.setDeltaMovement(Vec3.ZERO);mob.interruptAttack(24);return;}
        mob.setDeltaMovement(step);var target=mob.resolve(mob.attack().target());
        if(!mob.validEnemy(target)||!mob.hasLineOfSight(target)||!mob.getBoundingBox().inflate(.65).intersects(target.getBoundingBox()))return;
        contacted=true;long immune=target.getPersistentData().getLong("DynastyYechaEscapeUntil");if(immune>now&&immune<=now+240)return;
        if(!target.hurt(mob.damageSources().mobAttack(mob),6)||!mob.isAlive())return;
        captive=target.getUUID();baseY=target.getY();releaseAt=now+40;target.getPersistentData().putLong("DynastyYechaEscapeUntil",now+160);
        target.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING,160),mob);target.fallDistance=0;mob.syncHook(target,releaseAt);
    }
    public void hurtAccepted(DamageSource source,boolean frontal,float damage){if(damage>=3)release();}
    public void died(DamageSource source){release();}
    private void release(){boolean held=captive!=null;var target=mob.resolve(captive);if(target!=null){target.fallDistance=0;target.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING,100),mob);}captive=null;releaseAt=0;mob.syncHook(null,0);if(held&&mob.isAlive())mob.interruptAttack(24);}
    public CompoundTag save(){var t=new CompoundTag();t.putBoolean("Contacted",contacted);t.putDouble("DX",dive.x);t.putDouble("DY",dive.y);t.putDouble("DZ",dive.z);return t;}
    public void load(CompoundTag t){contacted=t.getBoolean("Contacted");dive=new Vec3(t.getDouble("DX"),t.getDouble("DY"),t.getDouble("DZ")).normalize();captive=null;mob.syncHook(null,0);}
}
