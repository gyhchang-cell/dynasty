package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.SkillDefinition;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/** One normal-collision flying body; the existing attack clock owns AIM/DIVE/PASS/RECOVER. */
final class LanternBatBehavior implements ArmyBehaviors.Behavior {
    private final TemplateMob mob;
    private Vec3 course=Vec3.ZERO;
    private boolean contact, coldFlare;
    private long circleUntil;
    LanternBatBehavior(TemplateMob mob){this.mob=mob;circleUntil=mob.level().getGameTime()+40;}
    public boolean allows(int id){return id==ArmySkills.BAT_DIVE||id==ArmySkills.BAT_GLARE;}
    public String animation(int id){return id==ArmySkills.BAT_GLARE?"glare":"attack";}
    public int choose(LivingEntity target,long now){
        if(now<circleUntil)return 0;
        return mob.attack().ready(ArmySkills.BAT_GLARE,now)&&mob.distanceToSqr(target)<=100?ArmySkills.BAT_GLARE:ArmySkills.BAT_DIVE;
    }
    public boolean canStart(int id,LivingEntity target){return id!=ArmySkills.BAT_DIVE||mob.getY()>target.getY()+1;}
    public void started(int id,LivingEntity target){
        contact=false;course=target.getBoundingBox().getCenter().subtract(mob.position()).normalize();
        circleUntil=mob.level().getGameTime()+90;
    }
    public void move(LivingEntity target,long now){
        double angle=now*.045+(mob.getId()%13)*.4;
        for(int i=0;i<4;i++){
            double a=angle+i*Math.PI/2;var p=target.position().add(Math.cos(a)*4,3+i%2,Math.sin(a)*4);
            var box=mob.getType().getDimensions().makeBoundingBox(p.x,p.y,p.z);
            if(!mob.level().hasChunkAt(BlockPos.containing(box.minX,box.minY,box.minZ))||!mob.level().hasChunkAt(BlockPos.containing(box.maxX,box.maxY,box.maxZ))
                ||!mob.level().getWorldBorder().isWithinBounds(box)||!mob.level().noCollision(mob,box))continue;
            var path=mob.getNavigation().createPath(p.x,p.y,p.z,0);
            if(path!=null&&path.canReach()){mob.getNavigation().moveTo(path,1.1);return;}
        }
    }
    public void tick(long now){
        if(mob.skillId()!=ArmySkills.BAT_DIVE)return;
        double age=mob.actionAge(0);
        if(age<18){mob.setDeltaMovement(mob.getDeltaMovement().scale(.3));return;}
        if(age>=40){mob.setDeltaMovement(0,.12,0);return;}
        Vec3 step=course.scale(age<32?.65:.4);
        var ray=mob.level().clip(new ClipContext(mob.getEyePosition(),mob.getEyePosition().add(step),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,mob));
        if(ray.getType()!=HitResult.Type.MISS||mob.horizontalCollision||mob.verticalCollision){
            mob.setDeltaMovement(Vec3.ZERO);mob.interruptAttack(20);return;
        }
        mob.setDeltaMovement(step);
        // PASS never steers after a moving victim and cannot produce a second contact.
        var target=mob.resolve(mob.attack().target());
        if(age<32&&!contact&&mob.validEnemy(target)&&mob.hasLineOfSight(target)&&mob.getBoundingBox().inflate(.25).intersects(target.getBoundingBox())){
            contact=true;
            if(target.hurt(mob.damageSources().mobAttack(mob),5))target.addEffect(new MobEffectInstance(BlueprintEntities.LANTERN_GLARE.get(),20,1),mob);
        }
    }
    static boolean facing(LivingEntity target,Vec3 light){
        var delta=light.subtract(target.getEyePosition());
        return delta.lengthSqr()<.01||target.getLookAngle().dot(delta.normalize())>.65;
    }
    public void impact(SkillDefinition skill,int frame){
        if(skill.id()!=ArmySkills.BAT_GLARE)return;
        var level=(ServerLevel)mob.level();
        for(var target:level.getEntitiesOfClass(LivingEntity.class,mob.getBoundingBox().inflate(10),
                e->mob.validEnemy(e)&&mob.distanceToSqr(e)<=100&&mob.hasLineOfSight(e)&&facing(e,mob.getEyePosition()))){
            target.addEffect(new MobEffectInstance(BlueprintEntities.LANTERN_GLARE.get(),60,1),mob);
            if(target==mob.resolve(mob.attack().target()))
                level.getEntitiesOfClass(Zombie.class,mob.getBoundingBox().inflate(12),z->z.isAlive()&&!z.isNoAi()&&z.getTarget()==null
                    &&z.canAttack(target)&&z.hasLineOfSight(target)&&z.distanceToSqr(mob)<=144).stream().limit(6).forEach(z->z.setTarget(target));
        }
        level.sendParticles(ParticleTypes.SOUL_FIRE_FLAME,mob.getX(),mob.getY()+.2,mob.getZ(),12,.35,.25,.35,.01);
    }
    public void tickDead(long now){
        if(coldFlare)return;
        var level=(ServerLevel)mob.level();
        if(mob.onGround()){
            coldFlare=true;level.sendParticles(ParticleTypes.SOUL_FIRE_FLAME,mob.getX(),mob.getY()+.1,mob.getZ(),18,.6,.15,.6,.015);
        }else if(now%4==0)level.sendParticles(ParticleTypes.SOUL_FIRE_FLAME,mob.getX(),mob.getY()+.6,mob.getZ(),2,.25,.15,.25,0);
    }
    public CompoundTag save(){var t=new CompoundTag();t.putDouble("CourseX",course.x);t.putDouble("CourseY",course.y);t.putDouble("CourseZ",course.z);
        t.putBoolean("Contact",contact);t.putBoolean("ColdFlare",coldFlare);t.putLong("CircleUntil",circleUntil);return t;}
    public void load(CompoundTag t){course=new Vec3(t.getDouble("CourseX"),t.getDouble("CourseY"),t.getDouble("CourseZ")).normalize();
        contact=t.getBoolean("Contact");coldFlare=t.getBoolean("ColdFlare");circleUntil=Math.min(t.getLong("CircleUntil"),mob.level().getGameTime()+90);}
}
