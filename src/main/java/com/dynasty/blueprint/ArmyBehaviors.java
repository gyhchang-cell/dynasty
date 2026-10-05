package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.phys.Vec3;
import java.util.UUID;

/** Profession strategies reuse the validated lifecycle/clock instead of duplicating five Mob ticks. */
public final class ArmyBehaviors {
    public interface Behavior {
        boolean allows(int id);
        int choose(LivingEntity target,long now);
        void impact(SkillDefinition skill,int frame);
        void move(LivingEntity target,long now);
        default boolean canStart(int id,LivingEntity target){return true;}
        default void started(int id,LivingEntity target){}
        default void tick(long now){}
        default void died(DamageSource source){}
        default void tickDead(long now){}
        default void hookHit(LivingEntity target){}
        default CompoundTag save(){return new CompoundTag();}
        default void load(CompoundTag tag){}
        default String animation(int id){return switch(id){case ArmySkills.BRACE->"brace";case ArmySkills.ROLL->"roll";
            case ArmySkills.GRAPPLE->"grapple";case ArmySkills.KNEE->"knee";case ArmySkills.DETONATE->"detonate";default->"attack";};}
    }
    static Behavior create(TemplateMob mob,TemplateMob.Kind kind){return switch(kind){
        case SPEAR->new Spear(mob);case CROSSBOW->new Crossbow(mob);case SCOUT->new Scout(mob);
        case POWDER->new Powder(mob);case FLAG->new Flag(mob);default->null;};}
    private ArmyBehaviors(){}
    public static boolean charging(LivingEntity target,Vec3 position){
        Vec3 velocity=target.getVehicle()==null?target.getDeltaMovement():target.getVehicle().getDeltaMovement();
        Vec3 approach=position.subtract(target.position()).multiply(1,0,1).normalize();
        return (target.isSprinting()||target.isPassenger())&&velocity.horizontalDistanceSqr()>.025
            &&velocity.multiply(1,0,1).normalize().dot(approach)>.72;
    }
    private abstract static class Base implements Behavior {
        final TemplateMob mob;
        UUID shield;long formationScan=-1;java.util.List<UUID> crossbows=java.util.List.of();
        Base(TemplateMob mob){this.mob=mob;}
        ServerLevel level(){return (ServerLevel)mob.level();}
        LivingEntity victim(){return mob.resolve(mob.attack().target());}
        TemplateMob formationShield(long now){
            if(now>=formationScan){
                formationScan=now+20;
                var units=level().getEntitiesOfClass(TemplateMob.class,mob.getBoundingBox().inflate(12),
                    e->e.isAlive()&&e.faction()==mob.faction()&&mob.distanceToSqr(e)<=144);
                shield=units.stream().filter(e->e.kind()==TemplateMob.Kind.SHIELD).min(java.util.Comparator.comparingDouble(mob::distanceToSqr)).map(TemplateMob::getUUID).orElse(null);
                crossbows=units.stream().filter(e->e.kind()==TemplateMob.Kind.CROSSBOW).sorted(java.util.Comparator.comparing(TemplateMob::getUUID))
                    .limit(8).map(TemplateMob::getUUID).toList();
            }
            var leader=mob.resolve(shield);
            return leader instanceof TemplateMob ally&&ally.kind()==TemplateMob.Kind.SHIELD&&mob.distanceToSqr(ally)<=144?ally:null;
        }
        Vec3 formationSpot(TemplateMob leader,LivingEntity target,boolean spear){
            Vec3 forward=target.position().subtract(leader.position()).multiply(1,0,1).normalize();
            int index=crossbows.indexOf(mob.getUUID());double side=spear?1.25:index%2==0?-.55:.55;
            return leader.position().add(forward.scale(-2)).add(-forward.z*side,0,forward.x*side);
        }
        @Override public void move(LivingEntity target,long now){mob.setSprinting(false);mob.getNavigation().moveTo(target,1);}
        void navigate(Vec3 point,double speed){
            var path=mob.getNavigation().createPath(point.x,point.y,point.z,0);
            if(path!=null&&path.canReach())mob.getNavigation().moveTo(path,speed);
        }
        int hit(SkillDefinition skill,CombatGeometry.Shape shape,double width,float damage,double knockback,boolean bleed){
            int count=0;Vec3 at=mob.position(),dir=mob.attack().direction();
            for(var target:CombatGeometry.query(level(),at,dir,shape,skill.maxRange(),width,skill.angleDegrees(),1.6,
                    e->mob.validEnemy(e)&&mob.hasLineOfSight(e))){
                target.invulnerableTime=0;
                if(target.hurt(mob.damageSources().mobAttack(mob),(float)mob.getAttributeValue(Attributes.ATTACK_DAMAGE)*damage)){
                    count++;target.knockback(knockback,-dir.x,-dir.z);
                    if(bleed)target.addEffect(new MobEffectInstance(MobEffects.WITHER,40,0),mob);
                }
                if(!mob.isAlive()||mob.attack().current()!=skill)break;
            }
            return count;
        }
    }
    private static final class Spear extends Base {
        boolean braceSpent;
        Spear(TemplateMob mob){super(mob);}
        public boolean allows(int id){return id==ArmySkills.THRUST||id==ArmySkills.BRACE;}
        public int choose(LivingEntity target,long now){return charging(target,mob.position())&&mob.distanceToSqr(target)<36
            &&mob.attack().ready(ArmySkills.BRACE,now)?ArmySkills.BRACE:ArmySkills.THRUST;}
        public boolean canStart(int id,LivingEntity target){return id!=ArmySkills.BRACE||charging(target,mob.position());}
        public void started(int id,LivingEntity target){if(id==ArmySkills.BRACE)braceSpent=false;}
        public void impact(SkillDefinition skill,int frame){if(skill.id()==ArmySkills.THRUST)hit(skill,CombatGeometry.Shape.STRIP,.42,1,.9,false);}
        public void tick(long now){
            if(braceSpent||mob.skillId()!=ArmySkills.BRACE||mob.attack().state(now)!=AttackState.ACTIVE)return;
            var target=victim();var skill=mob.attack().current();
            if(!mob.validEnemy(target)||!mob.hasLineOfSight(target)||!CombatGeometry.contains(mob.position(),mob.attack().direction(),
                    CombatGeometry.Shape.STRIP,3.5,.42,25,1.6,target.getBoundingBox()))return;
            braceSpent=true;target.invulnerableTime=0;
            if(target.hurt(mob.damageSources().mobAttack(mob),(float)mob.getAttributeValue(Attributes.ATTACK_DAMAGE)*3)){
                target.setSprinting(false);target.stopUsingItem();target.knockback(1.1,-mob.attack().direction().x,-mob.attack().direction().z);
                target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,40,4),mob);
                if(target instanceof TemplateMob other)other.interruptAttack(40);
            }
        }
        public void move(LivingEntity target,long now){
            if(mob.distanceToSqr(target)<4)navigate(mob.position().add(mob.position().subtract(target.position()).multiply(1,0,1).normalize().scale(2)),1);
            else{var leader=formationShield(now);if(leader!=null)navigate(formationSpot(leader,target,true),1);else super.move(target,now);}
        }
        public CompoundTag save(){var t=new CompoundTag();t.putBoolean("BraceSpent",braceSpent);return t;}
        public void load(CompoundTag tag){braceSpent=tag.getBoolean("BraceSpent");}
    }
    private static final class Crossbow extends Base {
        Crossbow(TemplateMob mob){super(mob);}
        public boolean allows(int id){return id==ArmySkills.VOLLEY||id==ArmySkills.ROLL;}
        public boolean canStart(int id,LivingEntity target){
            if(id!=ArmySkills.VOLLEY||formationShield(level().getGameTime())==null)return true;
            // Stagger the two soldiers' windups, not their clocks or the player's movement.
            // Scan membership every20 ticks; inspect at most eight cached loaded UUIDs.
            for(UUID idOfAlly:crossbows){var ally=mob.resolve(idOfAlly);
                if(ally instanceof TemplateMob other&&other!=mob&&other.getTarget()==target&&other.skillId()==ArmySkills.VOLLEY&&other.actionAge(0)<7)return false;}
            return true;
        }
        public int choose(LivingEntity target,long now){return mob.distanceToSqr(target)<16&&mob.attack().ready(ArmySkills.ROLL,now)?ArmySkills.ROLL:ArmySkills.VOLLEY;}
        public void impact(SkillDefinition skill,int frame){
            if(skill.id()==ArmySkills.VOLLEY){var enemy=victim();if(mob.validEnemy(enemy)&&mob.distanceToSqr(enemy)<=576&&mob.hasLineOfSight(enemy)){
                TemplateProjectile.shootArmy(mob,enemy,false);mob.playSound(SoundEvents.CROSSBOW_SHOOT,.65F,.85F);}}
            else if(skill.impactTicks().indexOf(frame)==0){
                Vec3 back=mob.attack().direction().scale(-.27);
                if(level().noCollision(mob,mob.getBoundingBox().move(back)))mob.setDeltaMovement(back.x,.18,back.z);
            }else if(skill.impactTicks().indexOf(frame)==1)ArmyCaltrop.spawn(mob);
        }
        public void tick(long now){
            if(mob.skillId()==ArmySkills.ROLL&&mob.attack().state(now)==AttackState.ACTIVE&&mob.actionAge(0)>6&&mob.actionAge(0)<14){
                Vec3 back=mob.attack().direction().scale(-.25);
                if(level().noCollision(mob,mob.getBoundingBox().move(back)))mob.setDeltaMovement(back.x,mob.getDeltaMovement().y,back.z);
            }
        }
        public void move(LivingEntity target,long now){
            double distance=mob.distanceToSqr(target);
            if(distance<49)navigate(mob.position().add(mob.position().subtract(target.position()).multiply(1,0,1).normalize().scale(4)),1);
            else{var leader=formationShield(now);
                if(leader!=null){Vec3 spot=formationSpot(leader,target,false);if(mob.position().distanceToSqr(spot)>.5)navigate(spot,1);else mob.getNavigation().stop();}
                else if(distance>400||!mob.hasLineOfSight(target))super.move(target,now);else mob.getNavigation().stop();}
        }
    }
    private static final class Scout extends Base {
        UUID linked;long expires;boolean kneeSpent;
        Scout(TemplateMob mob){super(mob);}
        public boolean allows(int id){return id==ArmySkills.CUT||id==ArmySkills.GRAPPLE||id==ArmySkills.KNEE;}
        public int choose(LivingEntity target,long now){return mob.distanceToSqr(target)>64?ArmySkills.GRAPPLE:ArmySkills.CUT;}
        public void started(int id,LivingEntity target){if(id==ArmySkills.GRAPPLE){linked=null;expires=0;kneeSpent=false;mob.syncHook(null,-1);}}
        public void impact(SkillDefinition skill,int frame){
            if(skill.id()==ArmySkills.CUT)hit(skill,CombatGeometry.Shape.SECTOR,1,.65F,.15,true);
            else if(skill.id()==ArmySkills.KNEE)hit(skill,CombatGeometry.Shape.SECTOR,.5,1.2F,.5,false);
            else{var enemy=victim();if(mob.validEnemy(enemy)&&mob.hasLineOfSight(enemy))TemplateProjectile.shootArmy(mob,enemy,true);}
        }
        public void hookHit(LivingEntity target){if(mob.skillId()!=ArmySkills.GRAPPLE||!mob.validEnemy(target)||mob.distanceToSqr(target)>400)return;
            linked=target.getUUID();expires=level().getGameTime()+30;mob.syncHook(target,expires);}
        public void tick(long now){
            if(linked==null)return;var target=mob.resolve(linked);
            if(now>=expires||mob.skillId()!=ArmySkills.GRAPPLE||!mob.validEnemy(target)||mob.distanceToSqr(target)>400||!mob.hasLineOfSight(target)){linked=null;mob.syncHook(null,-1);return;}
            mob.syncHook(target,expires); // Resolve loaded UUIDs before publishing a current runtime entity ID.
            Vec3 delta=target.position().subtract(mob.position());
            if(delta.horizontalDistanceSqr()<4.4){
                linked=null;mob.syncHook(null,-1);if(!kneeSpent){
                    kneeSpent=true;
                    // Arrival time varies with range/collision. Start a new synchronized
                    // knee timeline at actual arrival instead of damaging at a fixed grapple age.
                    mob.attack().cancel();mob.startSkill(ArmySkills.KNEE,target);
                }
            }else{
                Vec3 pull=delta.normalize().scale(.64);pull=new Vec3(pull.x,Math.max(-.15,Math.min(.2,pull.y)),pull.z);
                if(level().noCollision(mob,mob.getBoundingBox().move(pull)))mob.setDeltaMovement(pull);
                else {linked=null;mob.syncHook(null,-1);}
            }
        }
        public void move(LivingEntity target,long now){
            mob.setSprinting(true);Vec3 toward=target.position().subtract(mob.position()).multiply(1,0,1).normalize();
            if(mob.distanceToSqr(target)>9)navigate(target.position().add(-toward.z*2.5,0,toward.x*2.5),1.25);
            else super.move(target,now);
        }
        public CompoundTag save(){var t=new CompoundTag();if(linked!=null)t.putUUID("Linked",linked);t.putLong("Expires",expires);t.putBoolean("KneeSpent",kneeSpent);return t;}
        public void load(CompoundTag tag){linked=tag.hasUUID("Linked")?tag.getUUID("Linked"):null;expires=tag.getLong("Expires");kneeSpent=tag.getBoolean("KneeSpent");
            if(expires<=mob.level().getGameTime()||expires>mob.level().getGameTime()+30)linked=null;}
    }
    private static final class Powder extends Base {
        int nearTicks;long lastTick=-1,deadExplosionAt=-1;boolean exploded,smallExplosion;
        Powder(TemplateMob mob){super(mob);}
        public boolean allows(int id){return id==ArmySkills.STAB||id==ArmySkills.DETONATE;}
        public int choose(LivingEntity target,long now){return ArmySkills.STAB;}
        public void tick(long now){
            var enemy=mob.getTarget();boolean close=mob.validEnemy(enemy)&&mob.distanceToSqr(enemy)<9&&mob.hasLineOfSight(enemy);
            if(!close||lastTick>=0&&now-lastTick!=1)resetFuse();lastTick=now;
            nearTicks=close?Math.min(60,nearTicks+1):0;
            if(nearTicks>=40&&mob.skillId()!=ArmySkills.DETONATE&&mob.attack().ready(ArmySkills.DETONATE,now)){
                mob.attack().cancel();mob.startSkill(ArmySkills.DETONATE,enemy);
            }
        }
        private void resetFuse(){
            nearTicks=0;
            // tryStart reserves a cooldown immediately. A broken fuse never spent its blast,
            // so retaining that reservation would suppress the next continuous three seconds.
            mob.attack().resetCooldown(ArmySkills.DETONATE);
            if(mob.skillId()==ArmySkills.DETONATE&&mob.isAlive())mob.interruptAttack(1);
        }
        public void impact(SkillDefinition skill,int frame){
            if(skill.id()==ArmySkills.STAB)hit(skill,CombatGeometry.Shape.SECTOR,1,.6F,.1,false);
            else if(nearTicks>=59){explode(4,3.5F);mob.hurt(mob.damageSources().genericKill(),Float.MAX_VALUE);}
        }
        void explode(double radius,float multiplier){
            if(exploded)return;exploded=true;
            for(var enemy:CombatGeometry.query(level(),mob.position(),new Vec3(0,0,1),CombatGeometry.Shape.CIRCLE,radius,0,360,2,
                    e->mob.validEnemy(e)&&mob.hasLineOfSight(e))){
                enemy.hurt(mob.damageSources().explosion(mob,mob),(float)mob.getAttributeValue(Attributes.ATTACK_DAMAGE)*multiplier);
                Vec3 away=enemy.position().subtract(mob.position()).normalize();enemy.knockback(1.4,-away.x,-away.z);enemy.setSecondsOnFire(3);
            }
            // No Level.explode: player builds, terrain and protected mechanisms are never touched.
            level().sendParticles(net.minecraft.core.particles.ParticleTypes.EXPLOSION,mob.getX(),mob.getY()+.7,mob.getZ(),8,.7,.45,.7,.04);
            mob.playSound(SoundEvents.GENERIC_EXPLODE,1,.8F);
        }
        public void died(DamageSource source){smallExplosion=source.is(DamageTypeTags.IS_PROJECTILE);deadExplosionAt=level().getGameTime()+(smallExplosion?30:1);}
        public void tickDead(long now){if(deadExplosionAt>=0&&now>=deadExplosionAt)explode(smallExplosion?2.5:4,smallExplosion?2F:3.5F);}
        public void move(LivingEntity target,long now){mob.setSprinting(true);mob.getNavigation().moveTo(target,1.3);}
        public CompoundTag save(){var t=new CompoundTag();t.putInt("NearTicks",nearTicks);t.putLong("LastTick",lastTick);t.putLong("DeadExplosionAt",deadExplosionAt);t.putBoolean("Exploded",exploded);t.putBoolean("SmallExplosion",smallExplosion);return t;}
        public void load(CompoundTag tag){resetFuse();lastTick=-1;deadExplosionAt=tag.contains("DeadExplosionAt")?tag.getLong("DeadExplosionAt"):-1;exploded=tag.getBoolean("Exploded");
            // Never discharge a missed explosion frame when an unloaded corpse is restored.
            smallExplosion=tag.getBoolean("SmallExplosion");if(deadExplosionAt>=0&&deadExplosionAt<mob.level().getGameTime())exploded=true;}
    }
    private static final class Flag extends Base {
        Flag(TemplateMob mob){super(mob);}
        public boolean allows(int id){return id==ArmySkills.SLAM;}
        public int choose(LivingEntity target,long now){return ArmySkills.SLAM;}
        public void tick(long now){if((now+mob.getId())%20!=0)return;
            for(var ally:level().getEntitiesOfClass(LivingEntity.class,mob.getBoundingBox().inflate(12),
                    e->e.isAlive()&&e instanceof Combatant c&&c.faction()==mob.faction()&&c.role()!=MobRole.BEAST&&mob.distanceToSqr(e)<=144))
                ally.addEffect(new MobEffectInstance(BlueprintEntities.JUNHUN_AURA.get(),40,0,false,true,true),mob);
            if(now%80==0)mob.playSound(SoundEvents.NOTE_BLOCK_BASEDRUM.value(),.45F,.65F);
        }
        public void impact(SkillDefinition skill,int frame){hit(skill,CombatGeometry.Shape.CIRCLE,0,1,.65,false);}
    }
}
