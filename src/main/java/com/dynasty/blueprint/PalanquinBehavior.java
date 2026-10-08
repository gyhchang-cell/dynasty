package com.dynasty.blueprint;
import com.dynasty.blueprint.combat.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.*;
import net.minecraft.world.phys.Vec3;
import java.util.UUID;
/** Four bearers are bones in one entity. The cabin hold never teleports, mounts or redirects a player's view. */
final class PalanquinBehavior implements ArmyBehaviors.Behavior {
    private final TemplateMob mob;
    private UUID captive;
    private long expires,nextBite;
    private int escape;
    PalanquinBehavior(TemplateMob mob){this.mob=mob;}
    public boolean allows(int id){return id==ArmySkills.PALANQUIN_BUMP||id==ArmySkills.PALANQUIN_HOLD;}
    public String animation(int id){return id==ArmySkills.PALANQUIN_HOLD?"hold":"attack";}
    public int choose(LivingEntity target,long now){return mob.attack().ready(ArmySkills.PALANQUIN_HOLD,now)?ArmySkills.PALANQUIN_HOLD:ArmySkills.PALANQUIN_BUMP;}
    public void move(LivingEntity target,long now){mob.getNavigation().moveTo(target,1);}
    public void impact(SkillDefinition skill,int frame){
        var target=mob.resolve(mob.attack().target());if(!mob.validEnemy(target)||!mob.hasLineOfSight(target)||!CombatGeometry.contains(mob.position(),mob.attack().direction(),CombatGeometry.Shape.SECTOR,3,1,80,1.5,target.getBoundingBox()))return;
        if(skill.id()==ArmySkills.PALANQUIN_BUMP){if(target.hurt(mob.damageSources().mobAttack(mob),7))target.knockback(.5,mob.getX()-target.getX(),mob.getZ()-target.getZ());return;}
        long now=mob.level().getGameTime(),immune=target.getPersistentData().getLong("DynastyPalanquinEscapeUntil");if(immune>now&&immune<=now+240)return;
        if(!target.hurt(mob.damageSources().mobAttack(mob),2)||!mob.isAlive())return;
        captive=target.getUUID();expires=now+40;nextBite=now+10;escape=0;target.getPersistentData().putLong("DynastyPalanquinEscapeUntil",now+160);mob.syncHook(target,expires);
    }
    public void tick(long now){
        if(captive==null)return;var target=mob.resolve(captive);
        if(!mob.validEnemy(target)||now>=expires||mob.skillId()!=ArmySkills.PALANQUIN_HOLD||mob.distanceToSqr(target)>10.24||!mob.hasLineOfSight(target)){release();return;}
        escape=target.isShiftKeyDown()?escape+1:0;if(escape>=5){release();return;}
        target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,6,1),mob);
        var d=mob.position().subtract(target.position()).multiply(1,0,1);
        if(d.lengthSqr()>2.25){var v=target.getDeltaMovement();var pull=d.normalize().scale(.04);var horizontal=new Vec3(v.x+pull.x,0,v.z+pull.z);if(horizontal.lengthSqr()>.0144)horizontal=horizontal.normalize().scale(.12);target.setDeltaMovement(horizontal.x,v.y,horizontal.z);target.hurtMarked=true;}
        if(now>=nextBite){nextBite=now+10;target.hurt(mob.damageSources().indirectMagic(mob,mob),2);}
        if(now%5==0)((ServerLevel)mob.level()).sendParticles(ParticleTypes.SOUL,target.getX(),target.getY()+.4,target.getZ(),2,.2,.2,.2,.01);
    }
    public void hurtAccepted(DamageSource source,boolean frontal,float damage){if(damage>=3)release();}
    public void died(DamageSource source){release();}
    public void tickDead(long now){if(now%4==0)((ServerLevel)mob.level()).sendParticles(ParticleTypes.SOUL_FIRE_FLAME,mob.getX(),mob.getY()+.8,mob.getZ(),4,.8,.5,.8,.02);}
    private void release(){boolean held=captive!=null;captive=null;expires=0;mob.syncHook(null,0);if(held&&mob.isAlive()&&mob.skillId()==ArmySkills.PALANQUIN_HOLD)mob.interruptAttack(20);}
    // Captive deliberately is not persisted: unloading leaves only a six-tick debuff, never resumed control.
}
