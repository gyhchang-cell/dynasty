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
        default void hurtAccepted(DamageSource source,boolean frontal){}
        default boolean evade(DamageSource source){return false;}
        default boolean canInterrupt(){return true;}
        default CompoundTag save(){return new CompoundTag();}
        default void load(CompoundTag tag){}
        default String animation(int id){return switch(id){case ArmySkills.BRACE->"brace";case ArmySkills.ROLL->"roll";
            case ArmySkills.GRAPPLE->"grapple";case ArmySkills.KNEE->"knee";case ArmySkills.DETONATE->"detonate";
            case ArmySkills.CHILD_CURSE->"curse";case ArmySkills.AXE_COUNTER->"counter";case ArmySkills.GHOST_PHASE->"phase";default->"attack";};}
    }
    static Behavior create(TemplateMob mob,TemplateMob.Kind kind){return switch(kind){
        case SPEAR->new Spear(mob);case CROSSBOW->new Crossbow(mob);case SCOUT->new Scout(mob);
        case POWDER->new Powder(mob);case FLAG->new Flag(mob);case AXE_GUARD->new AxeGuard(mob);case GHOST->new Ghost(mob);case CORPSE->new Corpse(mob);case CHILD->new ShroudChild(mob);default->null;};}
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
    /** Player look direction is sampled only on the server; a single turn cancels this cast. */
    static boolean observing(LivingEntity observer,LivingEntity subject){
        Vec3 toward=subject.getEyePosition().subtract(observer.getEyePosition());
        return toward.lengthSqr()<.01||observer.getLookAngle().dot(toward.normalize())>.6&&observer.hasLineOfSight(subject);
    }
    private static final class ShroudChild extends Base {
        ShroudChild(TemplateMob mob){super(mob);}
        public boolean allows(int id){return id==ArmySkills.CHILD_LAUGH||id==ArmySkills.CHILD_CURSE;}
        private boolean behindPlayer(LivingEntity target){
            return target instanceof net.minecraft.server.level.ServerPlayer&&target.getLookAngle()
                .dot(mob.getEyePosition().subtract(target.getEyePosition()).normalize())<-.35;
        }
        public boolean canStart(int id,LivingEntity target){return id!=ArmySkills.CHILD_CURSE||behindPlayer(target);}
        public int choose(LivingEntity target,long now){
            return behindPlayer(target)&&mob.attack().ready(ArmySkills.CHILD_CURSE,now)?ArmySkills.CHILD_CURSE:ArmySkills.CHILD_LAUGH;
        }
        public void started(int id,LivingEntity target){mob.playSound(SoundEvents.VEX_CHARGE,.45F,1.7F);}
        public void tick(long now){
            if(mob.skillId()!=ArmySkills.CHILD_CURSE)return;
            var target=victim();
            if(!mob.validEnemy(target)||mob.distanceToSqr(target)>100||!mob.hasLineOfSight(target)||observing(target,mob)){
                mob.cancelAction();return;
            }
            if(now%5==0)level().sendParticles(net.minecraft.core.particles.ParticleTypes.END_ROD,
                target.getX(),target.getY()+.15,target.getZ(),3,.4,.08,.4,.005);
        }
        public void impact(SkillDefinition skill,int frame){
            if(skill.id()==ArmySkills.CHILD_CURSE){
                var target=victim();
                if(target instanceof net.minecraft.server.level.ServerPlayer player&&mob.validEnemy(player)
                        &&mob.distanceToSqr(player)<=100&&mob.hasLineOfSight(player)&&!observing(player,mob)){
                    player.addEffect(new MobEffectInstance(BlueprintEntities.SOUL_BIND.get(),30,0),mob);
                    int food=player.getFoodData().getFoodLevel();player.getFoodData().setFoodLevel(Math.max(0,food-(int)Math.ceil(food*.1)));
                }
                return;
            }
            for(var target:CombatGeometry.query(level(),mob.position(),mob.attack().direction(),CombatGeometry.Shape.CIRCLE,
                    6,1,360,2,e->mob.validEnemy(e)&&mob.hasLineOfSight(e))){
                target.hurt(mob.damageSources().indirectMagic(mob,mob),2);
                if(target instanceof net.minecraft.server.level.ServerPlayer&&observing(target,mob))
                    target.addEffect(new MobEffectInstance(BlueprintEntities.LANTERN_GLARE.get(),16,0),mob);
            }
            for(int i=0;i<16;i++){double a=i*Math.PI/8;level().sendParticles(net.minecraft.core.particles.ParticleTypes.END_ROD,
                mob.getX()+Math.cos(a)*2,mob.getY()+.8,mob.getZ()+Math.sin(a)*2,1,0,0,0,0);}
        }
        public void move(LivingEntity target,long now){
            mob.setSprinting(false);
            Vec3 away=mob.position().subtract(target.position()).multiply(1,0,1).normalize();
            Vec3 point=mob.distanceToSqr(target)<16?mob.position().add(away.scale(3))
                :target.position().subtract(target.getLookAngle().multiply(1,0,1).normalize().scale(4));
            navigate(point,.85);
        }
        public void died(DamageSource source){mob.playSound(SoundEvents.ALLAY_DEATH,.55F,1.35F);}
    }
    private static final class Corpse extends Base {
        long spillCooldown, nextBound;
        Corpse(TemplateMob mob){super(mob);}
        public boolean allows(int id){return id==ArmySkills.CORPSE_SMASH;}
        public int choose(LivingEntity target,long now){return ArmySkills.CORPSE_SMASH;}
        public void impact(SkillDefinition skill,int frame){
            hit(skill,CombatGeometry.Shape.CONE,1.3,1.5F,.7,false);
            var floor=level().getBlockState(mob.blockPosition().below());
            if(!floor.isAir())level().sendParticles(new net.minecraft.core.particles.BlockParticleOption(
                net.minecraft.core.particles.ParticleTypes.BLOCK,floor),mob.getX(),mob.getY()+.1,mob.getZ(),18,1,.15,1,.08);
            mob.playSound(SoundEvents.ZOMBIE_ATTACK_IRON_DOOR,.7F,.6F);
        }
        public void move(LivingEntity target,long now){
            boolean rush=mob.distanceToSqr(target)>9&&mob.hasLineOfSight(target);
            mob.setSprinting(rush);mob.getNavigation().moveTo(target,rush?1.65:.8);
            if(rush&&mob.onGround()&&now>=nextBound&&!mob.getNavigation().isDone()){
                Vec3 direction=target.position().subtract(mob.position()).multiply(1,0,1).normalize();
                mob.setDeltaMovement(direction.scale(.33).add(0,.25,0));mob.hasImpulse=true;nextBound=now+14;
            }
        }
        public void tick(long now){if(!mob.validEnemy(mob.getTarget())||mob.skillId()!=0)mob.setSprinting(false);}
        public void hurtAccepted(DamageSource source,boolean frontal){
            long now=level().getGameTime();if(now<spillCooldown)return;
            spillCooldown=now+25;
            // Damage-triggered bounded query only; three patches shared by nearby corpses.
            if(level().getEntitiesOfClass(CorpseMiasma.class,mob.getBoundingBox().inflate(8)).size()>=3)return;
            var floor=mob.blockPosition();
            for(int i=0;i<6;i++,floor=floor.below()){
                if(!level().hasChunkAt(floor))return;
                if(!level().getBlockState(floor.below()).isFaceSturdy(level(),floor.below(),net.minecraft.core.Direction.UP)
                        ||!level().getBlockState(floor).getCollisionShape(level(),floor).isEmpty()||!level().getFluidState(floor).isEmpty())continue;
                var cloud=new CorpseMiasma(BlueprintEntities.CORPSE_MIASMA.get(),level());
                cloud.moveTo(mob.getX(),floor.getY()+.02,mob.getZ());cloud.setOwner(mob);cloud.activate(now);
                level().addFreshEntity(cloud);
                level().sendParticles(net.minecraft.core.particles.ParticleTypes.WITCH,mob.getX(),mob.getY()+1,mob.getZ(),9,.5,.5,.5,0);
                return;
            }
        }
        public void tickDead(long now){if(mob.actionAge(0)>=16&&mob.actionAge(0)<17)
            level().sendParticles(net.minecraft.core.particles.ParticleTypes.LARGE_SMOKE,mob.getX(),mob.getY()+1,mob.getZ(),24,.7,.6,.7,.035);}
        public CompoundTag save(){var tag=new CompoundTag();tag.putLong("SpillCooldown",spillCooldown);tag.putLong("NextBound",nextBound);return tag;}
        public void load(CompoundTag tag){spillCooldown=tag.getLong("SpillCooldown");nextBound=tag.getLong("NextBound");}
    }
    private static final class Ghost extends Base {
        boolean evadeReady;
        Ghost(TemplateMob mob){super(mob);}
        public boolean allows(int id){return id==ArmySkills.GHOST_THRUST||id==ArmySkills.GHOST_PHASE;}
        public boolean canStart(int id,LivingEntity target){return id!=ArmySkills.GHOST_PHASE||evadeReady;}
        public boolean canInterrupt(){return !mob.isPhased();}
        public int choose(LivingEntity target,long now){return ArmySkills.GHOST_THRUST;}
        public boolean evade(DamageSource source){
            if(source.is(DamageTypeTags.BYPASSES_INVULNERABILITY))return false;
            if(mob.isPhased())return true;
            long now=level().getGameTime();
            if(!(source.getDirectEntity() instanceof LivingEntity attacker)||source.getEntity()!=attacker
                    ||!mob.validEnemy(attacker)||source.is(DamageTypeTags.IS_PROJECTILE)
                    ||mob.distanceToSqr(attacker)>256||!mob.hasLineOfSight(attacker)
                    ||!mob.attack().ready(ArmySkills.GHOST_PHASE,now)||mob.attack().state(now)==AttackState.STUN
                    ||mob.getRandom().nextFloat()>=.35F)return false;
            Vec3 landing=phaseLanding(mob,attacker);if(landing==null)return false;
            evadeReady=true;mob.cancelAction();boolean started=mob.startSkill(ArmySkills.GHOST_PHASE,attacker);evadeReady=false;
            if(!started)return false;
            level().sendParticles(net.minecraft.core.particles.ParticleTypes.SOUL,mob.getX(),mob.getY()+.9,mob.getZ(),8,.2,.5,.2,.02);
            mob.teleportTo(landing.x,landing.y,landing.z);mob.setDeltaMovement(Vec3.ZERO);mob.setTarget(attacker);
            mob.playSound(SoundEvents.SOUL_ESCAPE,.6F,.8F);return true;
        }
        public void impact(SkillDefinition skill,int frame){
            if(skill.id()!=ArmySkills.GHOST_THRUST)return;
            for(var target:CombatGeometry.query(level(),mob.position(),mob.attack().direction(),CombatGeometry.Shape.STRIP,
                    3.8,.4,30,1.6,e->mob.validEnemy(e)&&mob.hasLineOfSight(e))){
                target.invulnerableTime=0;
                if(target.hurt(mob.damageSources().indirectMagic(mob,mob),(float)mob.getAttributeValue(Attributes.ATTACK_DAMAGE)))
                    target.addEffect(new MobEffectInstance(BlueprintEntities.SPIRIT_CHILL.get(),60,0),mob);
                if(!mob.isAlive()||mob.attack().current()!=skill)return;
            }
        }
    }
    /** Only two side directions and three floor heights; no unloaded chunk access or solid-wall crossing. */
    static Vec3 phaseLanding(TemplateMob mob,LivingEntity attacker){
        var level=(ServerLevel)mob.level();
        Vec3 forward=attacker.getLookAngle().multiply(1,0,1).normalize();
        if(forward.lengthSqr()<.001)forward=mob.position().subtract(attacker.position()).multiply(1,0,1).normalize();
        if(forward.lengthSqr()<.001)return null;
        for(int side:new int[]{1,-1})for(int dy:new int[]{0,1,-1}){
            Vec3 candidate=attacker.position().add(-forward.z*3*side,dy,forward.x*3*side);
            var pos=net.minecraft.core.BlockPos.containing(candidate);
            candidate=new Vec3(candidate.x,pos.getY(),candidate.z);
            var box=mob.getType().getDimensions().makeBoundingBox(candidate.x,candidate.y,candidate.z);
            if(!level.hasChunkAt(pos)||!level.hasChunkAt(net.minecraft.core.BlockPos.containing(box.minX,box.minY,box.minZ))
                    ||!level.hasChunkAt(net.minecraft.core.BlockPos.containing(box.maxX,box.maxY,box.maxZ))
                    ||!level.getWorldBorder().isWithinBounds(box)||!level.getFluidState(pos).isEmpty()
                    ||!com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,pos,box))continue;
            if(!level.getEntitiesOfClass(LivingEntity.class,box,e->e.isAlive()&&e instanceof com.dynasty.DynastyBossCombat.BarHolder).isEmpty())continue;
            var line=level.clip(new net.minecraft.world.level.ClipContext(mob.getEyePosition(),candidate.add(0,mob.getEyeHeight(),0),
                net.minecraft.world.level.ClipContext.Block.COLLIDER,net.minecraft.world.level.ClipContext.Fluid.NONE,mob));
            if(line.getType()==net.minecraft.world.phys.HitResult.Type.MISS)return candidate;
        }
        return null;
    }
    private static final class AxeGuard extends Base {
        int frontalHits;long windowUntil;UUID counterTarget;boolean armed;
        private static final UUID POISE=UUID.fromString("1b39c378-634a-4cc0-a94d-caf66b3f88e2");
        AxeGuard(TemplateMob mob){super(mob);}
        public boolean allows(int id){return id==ArmySkills.AXE_CLAMP||id==ArmySkills.AXE_COUNTER;}
        public boolean canStart(int id,LivingEntity target){return id!=ArmySkills.AXE_COUNTER||armed;}
        public int choose(LivingEntity target,long now){return armed?ArmySkills.AXE_COUNTER:ArmySkills.AXE_CLAMP;}
        public boolean canInterrupt(){return mob.skillId()!=ArmySkills.AXE_COUNTER;}
        public void hurtAccepted(DamageSource source,boolean frontal){
            long now=level().getGameTime();
            if(!frontal||!(source.getEntity() instanceof LivingEntity attacker)||!mob.validEnemy(attacker)
                    ||armed||!mob.attack().ready(ArmySkills.AXE_COUNTER,now))return;
            if(now>=windowUntil){frontalHits=0;windowUntil=now+60;}
            if(++frontalHits>=3){
                frontalHits=0;armed=true;counterTarget=attacker.getUUID();
                mob.cancelAction();mob.startSkill(ArmySkills.AXE_COUNTER,attacker);
            }
        }
        public void started(int id,LivingEntity target){if(id==ArmySkills.AXE_COUNTER){armed=false;counterTarget=null;setPoise(true);}}
        private void setPoise(boolean active){
            var attr=mob.getAttribute(Attributes.KNOCKBACK_RESISTANCE);
            if(active&&attr.getModifier(POISE)==null)attr.addTransientModifier(new net.minecraft.world.entity.ai.attributes.AttributeModifier(
                POISE,"Guard counter poise",1,net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADDITION));
            else if(!active)attr.removeModifier(POISE);
        }
        public void tick(long now){
            setPoise(mob.skillId()==ArmySkills.AXE_COUNTER&&mob.attack().current()!=null);
            if(now>=windowUntil){frontalHits=0;armed=false;counterTarget=null;}
            if(armed&&mob.attack().current()==null){
                var target=mob.resolve(counterTarget);
                if(mob.validEnemy(target))mob.startSkill(ArmySkills.AXE_COUNTER,target);
            }
            if(mob.skillId()==ArmySkills.AXE_COUNTER&&mob.actionAge(0)<10&&now%2==0)
                level().sendParticles(net.minecraft.core.particles.ParticleTypes.WAX_ON,mob.getX(),mob.getY()+1.2,mob.getZ(),5,.6,.6,.6,.02);
        }
        public void impact(SkillDefinition skill,int frame){
            hit(skill,skill.id()==ArmySkills.AXE_COUNTER?CombatGeometry.Shape.CIRCLE:CombatGeometry.Shape.SECTOR,
                1,skill.damageMultiplier(),skill.knockback(),false);
        }
        public void move(LivingEntity target,long now){
            mob.setSprinting(false);double distance=mob.distanceToSqr(target);
            if(distance>30){super.move(target,now);return;}
            Vec3 forward=target.position().subtract(mob.position()).multiply(1,0,1).normalize();
            double side=(mob.getUUID().getLeastSignificantBits()&1)==0?1:-1;
            navigate(target.position().add(forward.scale(-2.6)).add(-forward.z*side,0,forward.x*side),.8);
        }
        public void died(DamageSource source){setPoise(false);}
        public void tickDead(long now){if(mob.deathTime==30){
            level().sendParticles(new net.minecraft.core.particles.BlockParticleOption(net.minecraft.core.particles.ParticleTypes.BLOCK,
                level().getBlockState(mob.blockPosition().below())),mob.getX(),mob.getY()+.1,mob.getZ(),20,.8,.1,.8,.05);
            mob.playSound(SoundEvents.IRON_GOLEM_DEATH,.8F,.6F);
        }}
        public CompoundTag save(){var t=new CompoundTag();t.putInt("FrontalHits",frontalHits);t.putLong("WindowUntil",windowUntil);t.putBoolean("CounterArmed",armed);if(counterTarget!=null)t.putUUID("CounterTarget",counterTarget);return t;}
        public void load(CompoundTag tag){
            windowUntil=Math.min(level().getGameTime()+60,tag.getLong("WindowUntil"));
            frontalHits=windowUntil>level().getGameTime()?Math.max(0,Math.min(2,tag.getInt("FrontalHits"))):0;
            armed=windowUntil>level().getGameTime()&&tag.getBoolean("CounterArmed");
            counterTarget=tag.hasUUID("CounterTarget")?tag.getUUID("CounterTarget"):null;
            setPoise(mob.skillId()==ArmySkills.AXE_COUNTER&&mob.isAlive());
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
        UUID linked, assaultAnchor, cachedPowder;long expires, nextAssaultScan;boolean kneeSpent;
        Scout(TemplateMob mob){super(mob);}
        public boolean allows(int id){return id==ArmySkills.CUT||id==ArmySkills.GRAPPLE||id==ArmySkills.KNEE;}
        private TemplateMob assaultPowder(LivingEntity target,long now){
            if(now>=nextAssaultScan){
                nextAssaultScan=now+20;
                cachedPowder=level().getEntitiesOfClass(TemplateMob.class,mob.getBoundingBox().inflate(16),
                    e->e.kind()==TemplateMob.Kind.POWDER&&e.isAlive()&&e.isPossessed()&&e.getTarget()==target
                        &&mob.distanceToSqr(e)<=256&&mob.hasLineOfSight(e)&&e.hasLineOfSight(target))
                    .stream().min(java.util.Comparator.comparingDouble(e->e.distanceToSqr(target)))
                    .map(TemplateMob::getUUID).orElse(null);
            }
            var found=mob.resolve(cachedPowder);
            return found instanceof TemplateMob powder&&powder.isAlive()&&powder.isPossessed()
                &&powder.getTarget()==target&&mob.distanceToSqr(powder)<=256?powder:null;
        }
        public int choose(LivingEntity target,long now){
            if(assaultPowder(target,now)!=null)return mob.distanceToSqr(target)>=64?ArmySkills.GRAPPLE:0;
            return mob.distanceToSqr(target)>64?ArmySkills.GRAPPLE:ArmySkills.CUT;
        }
        public void started(int id,LivingEntity target){if(id==ArmySkills.GRAPPLE){linked=null;assaultAnchor=null;expires=0;kneeSpent=false;mob.syncHook(null,-1);}}
        public void impact(SkillDefinition skill,int frame){
            if(skill.id()==ArmySkills.CUT)hit(skill,CombatGeometry.Shape.SECTOR,1,.65F,.15,true);
            else if(skill.id()==ArmySkills.KNEE)hit(skill,CombatGeometry.Shape.SECTOR,.5,1.2F,.5,false);
            else{var enemy=victim();if(mob.validEnemy(enemy)&&mob.hasLineOfSight(enemy))TemplateProjectile.shootArmy(mob,enemy,true);}
        }
        public void hookHit(LivingEntity target){if(mob.skillId()!=ArmySkills.GRAPPLE||!mob.validEnemy(target)||mob.distanceToSqr(target)>400)return;
            linked=target.getUUID();expires=level().getGameTime()+30;
            var powder=assaultPowder(target,level().getGameTime());
            assaultAnchor=powder==null?null:powder.getUUID();mob.syncHook(target,expires);}
        public void tick(long now){
            if(linked==null)return;var target=mob.resolve(linked);
            if(now>=expires||mob.skillId()!=ArmySkills.GRAPPLE||!mob.validEnemy(target)||mob.distanceToSqr(target)>400||!mob.hasLineOfSight(target)){linked=null;mob.syncHook(null,-1);return;}
            mob.syncHook(target,expires); // Resolve loaded UUIDs before publishing a current runtime entity ID.
            if(assaultAnchor!=null){
                var anchor=mob.resolve(assaultAnchor);
                if(!(anchor instanceof TemplateMob powder)||!powder.isAlive()||!powder.isPossessed()
                        ||powder.getTarget()!=target||powder.distanceToSqr(target)>256||!powder.hasLineOfSight(target)
                        ||target instanceof com.dynasty.DynastyBossCombat.BarHolder){
                    linked=null;mob.syncHook(null,-1);return;
                }
                Vec3 toward=powder.position().subtract(target.position()).multiply(1,0,1);
                if(toward.horizontalDistanceSqr()<5.76){linked=null;mob.syncHook(null,-1);return;}
                double resistance=Math.max(0,Math.min(1,target.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE)));
                Vec3 pull=toward.normalize().scale(.28*(1-resistance));
                if(pull.lengthSqr()<.0001||!level().hasChunkAt(net.minecraft.core.BlockPos.containing(target.position().add(pull)))
                        ||!level().noCollision(target,target.getBoundingBox().move(pull))){linked=null;mob.syncHook(null,-1);return;}
                target.setSprinting(false);
                target.setDeltaMovement(pull.x,Math.max(-.2,Math.min(.1,target.getDeltaMovement().y)),pull.z);
                target.hurtMarked=true; // Vanilla velocity packet reaches the affected player and observers.
                return;
            }
            Vec3 delta=target.position().subtract(mob.position());
            if(delta.horizontalDistanceSqr()<4.4){
                linked=null;mob.syncHook(null,-1);if(!kneeSpent){
                    kneeSpent=true;
                    // Arrival time varies with range/collision. Start a new synchronized
                    // knee timeline at actual arrival instead of damaging at a fixed grapple age.
                    mob.cancelAction();mob.startSkill(ArmySkills.KNEE,target);
                }
            }else{
                Vec3 pull=delta.normalize().scale(.64);pull=new Vec3(pull.x,Math.max(-.15,Math.min(.2,pull.y)),pull.z);
                if(level().noCollision(mob,mob.getBoundingBox().move(pull)))mob.setDeltaMovement(pull);
                else {linked=null;mob.syncHook(null,-1);}
            }
        }
        public void move(LivingEntity target,long now){
            mob.setSprinting(true);Vec3 toward=target.position().subtract(mob.position()).multiply(1,0,1).normalize();
            var powder=assaultPowder(target,now);
            if(powder!=null){
                Vec3 pressure=target.position().subtract(powder.position()).multiply(1,0,1).normalize();
                double side=(mob.getUUID().getLeastSignificantBits()&1)==0?1:-1;
                navigate(target.position().add(pressure.scale(8)).add(-pressure.z*4*side,0,pressure.x*4*side),1.25);return;
            }
            if(mob.distanceToSqr(target)>9)navigate(target.position().add(-toward.z*2.5,0,toward.x*2.5),1.25);
            else super.move(target,now);
        }
        public CompoundTag save(){var t=new CompoundTag();if(linked!=null)t.putUUID("Linked",linked);if(assaultAnchor!=null)t.putUUID("AssaultAnchor",assaultAnchor);t.putLong("Expires",expires);t.putBoolean("KneeSpent",kneeSpent);return t;}
        public void load(CompoundTag tag){linked=tag.hasUUID("Linked")?tag.getUUID("Linked"):null;expires=tag.getLong("Expires");kneeSpent=tag.getBoolean("KneeSpent");
            assaultAnchor=tag.hasUUID("AssaultAnchor")?tag.getUUID("AssaultAnchor"):null;
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
                mob.cancelAction();mob.startSkill(ArmySkills.DETONATE,enemy);
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
