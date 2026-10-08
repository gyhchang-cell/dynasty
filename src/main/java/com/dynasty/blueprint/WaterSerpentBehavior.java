package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.CombatGeometry;
import com.dynasty.blueprint.combat.SkillDefinition;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.phys.Vec3;
import java.util.UUID;

/** One amphibious body. Coils use the existing action clock and finite, collision-respecting velocity. */
final class WaterSerpentBehavior implements ArmyBehaviors.Behavior {
    private final TemplateMob mob;
    private UUID captive;
    private BlockPos water;
    private long releaseAt;
    private int escapeTicks;
    WaterSerpentBehavior(TemplateMob mob){this.mob=mob;}
    private ServerLevel level(){return (ServerLevel)mob.level();}
    public boolean allows(int id){return id==ArmySkills.SERPENT_BITE||id==ArmySkills.SERPENT_COIL;}
    public String animation(int id){return id==ArmySkills.SERPENT_COIL?"coil":"attack";}
    public boolean canStart(int id,LivingEntity target){return id!=ArmySkills.SERPENT_COIL||deepWater(target)!=null;}
    public int choose(LivingEntity target,long now){
        return mob.distanceToSqr(target)<=10.24&&mob.attack().ready(ArmySkills.SERPENT_COIL,now)&&deepWater(target)!=null
            ?ArmySkills.SERPENT_COIL:ArmySkills.SERPENT_BITE;
    }
    public void move(LivingEntity target,long now){
        mob.getNavigation().moveTo(target,mob.isInWater()?1.35:1.1);
        // Vanilla ground MoveControl does not pitch up through water; use bounded buoyancy toward the path node.
        if(mob.isInWater()&&!mob.getNavigation().isDone()){
            double dy=Math.max(-.08,Math.min(.08,(target.getY()-mob.getY())*.04));
            var velocity=mob.getDeltaMovement();mob.setDeltaMovement(velocity.x,dy,velocity.z);
        }
    }
    /** Only loaded blocks, only at cast selection/contact, at most 147 candidates. Never a world scan. */
    private BlockPos deepWater(LivingEntity target){
        var at=target.blockPosition();BlockPos nearest=null;double distance=Double.MAX_VALUE;
        for(int x=-3;x<=3;x++)for(int z=-3;z<=3;z++)for(int y=-1;y<=1;y++){
            var p=at.offset(x,y,z);
            if(!level().hasChunkAt(p)||!level().hasChunkAt(p.below())
                ||!level().getFluidState(p).is(FluidTags.WATER)||!level().getFluidState(p.below()).is(FluidTags.WATER))continue;
            double d=p.distSqr(at);if(d<distance){distance=d;nearest=p;}
        }
        return nearest;
    }
    public void started(int id,LivingEntity target){if(id==ArmySkills.SERPENT_COIL){release();water=deepWater(target);}}
    public void impact(SkillDefinition skill,int frame){
        var target=mob.resolve(mob.attack().target());
        if(!mob.validEnemy(target)||!mob.hasLineOfSight(target)||!CombatGeometry.contains(mob.position(),mob.attack().direction(),
            CombatGeometry.Shape.SECTOR,skill.maxRange(),.9,skill.angleDegrees(),1.5,target.getBoundingBox()))return;
        if(skill.id()==ArmySkills.SERPENT_COIL&&(water==null||deepWater(target)==null))return;
        if(!target.hurt(mob.damageSources().mobAttack(mob),(float)mob.getAttributeValue(Attributes.ATTACK_DAMAGE)*skill.damageMultiplier()))return;
        if(!mob.isAlive()||mob.attack().current()!=skill)return;
        if(skill.id()==ArmySkills.SERPENT_BITE){target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,40,0),mob);return;}
        // A different coil cannot extend an existing hold. A short immunity window prevents alternating captures.
        long now=level().getGameTime();var data=target.getPersistentData();
        long immunity=data.getLong("DynastyColdPoolEscapeUntil");
        if(target.hasEffect(BlueprintEntities.COLD_POOL_COIL.get())||immunity>now&&immunity<=now+200)return;
        captive=target.getUUID();releaseAt=now+24;escapeTicks=0;
        data.putLong("DynastyColdPoolEscapeUntil",now+100);
        target.stopUsingItem();target.addEffect(new MobEffectInstance(BlueprintEntities.COLD_POOL_COIL.get(),24),mob);
        mob.syncHook(target,releaseAt);
    }
    public void tick(long now){
        if(mob.isInWater()&&mob.tickCount%10==0)level().sendParticles(ParticleTypes.BUBBLE,mob.getX(),mob.getY()+.2,mob.getZ(),2,.2,.05,.2,0);
        if(captive==null)return;
        var target=mob.resolve(captive);
        if(!mob.isAlive()||!mob.validEnemy(target)||now>=releaseAt||mob.skillId()!=ArmySkills.SERPENT_COIL
                ||!target.hasEffect(BlueprintEntities.COLD_POOL_COIL.get())||mob.distanceToSqr(target)>16||!mob.hasLineOfSight(target)
                ||water==null||!level().hasChunkAt(water)||!level().getFluidState(water).is(FluidTags.WATER)){release();return;}
        escapeTicks=target.isShiftKeyDown()?escapeTicks+1:0;
        if(escapeTicks>=5){release();return;}
        Vec3 toward=Vec3.atCenterOf(water).subtract(target.position()).multiply(1,0,1);
        if(toward.lengthSqr()>.25){
            Vec3 old=target.getDeltaMovement(),pull=toward.normalize().scale(.045);
            Vec3 horizontal=new Vec3(old.x+pull.x,0,old.z+pull.z);
            if(horizontal.lengthSqr()>.0324)horizontal=horizontal.normalize().scale(.18);
            target.setDeltaMovement(horizontal.x,old.y,horizontal.z);target.hurtMarked=true;
        }
        level().sendParticles(ParticleTypes.SPLASH,target.getX(),target.getY()+.7,target.getZ(),2,.25,.2,.25,0);
    }
    public void hurtAccepted(DamageSource source,boolean frontal,float damage){if(damage>=2)release();}
    public void died(DamageSource source){release();}
    private void release(){
        boolean held=captive!=null;
        var target=mob.resolve(captive);
        if(target!=null)target.removeEffect(BlueprintEntities.COLD_POOL_COIL.get());
        captive=null;water=null;releaseAt=0;escapeTicks=0;mob.syncHook(null,0);
        if(held&&mob.isAlive()&&mob.skillId()==ArmySkills.SERPENT_COIL)mob.interruptAttack(21);
    }
    // Deliberately do not serialize the captive: unloading never resumes forced movement.
    // The independently timed effect expires within 24 ticks; attack cooldown persists in TimedAttack.
}
