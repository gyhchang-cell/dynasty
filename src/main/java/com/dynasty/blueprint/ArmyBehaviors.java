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
        default void hurtAccepted(DamageSource source,boolean frontal,float healthLost){hurtAccepted(source,frontal);}
        default boolean evade(DamageSource source){return false;}
        default boolean canInterrupt(){return true;}
        default boolean preventFatal(DamageSource source,float damage){return false;}
        default CompoundTag save(){return new CompoundTag();}
        default void load(CompoundTag tag){}
        default String animation(int id){return switch(id){case ArmySkills.BRACE->"brace";case ArmySkills.ROLL->"roll";
            case ArmySkills.GRAPPLE->"grapple";case ArmySkills.KNEE->"knee";case ArmySkills.DETONATE->"detonate";
            case ArmySkills.SCORPION_EMERGE->"emerge";case ArmySkills.SCORPION_SONG->"song";case ArmySkills.TREE_WAKE->"wake";case ArmySkills.TREE_ROOTS->"roots";case ArmySkills.TOAD_LEAP->"leap";case ArmySkills.TOAD_BURST->"burst";case ArmySkills.SKULL_BLOOD->"blood";case ArmySkills.PAPER_SHED->"shed";case ArmySkills.CHILD_CURSE->"curse";case ArmySkills.AXE_COUNTER->"counter";case ArmySkills.GHOST_PHASE->"phase";default->"attack";};}
    }
    static Behavior create(TemplateMob mob,TemplateMob.Kind kind){return switch(kind){
        case STONE_GUARD->new StoneGuardBehavior(mob);case SERPENT->new WaterSerpentBehavior(mob);case SPEAR->new Spear(mob);case CROSSBOW->new Crossbow(mob);case SCOUT->new Scout(mob);
        case POWDER->new Powder(mob);case FLAG->new Flag(mob);case AXE_GUARD->new AxeGuard(mob);case GHOST->new Ghost(mob);case CORPSE->new Corpse(mob);case CHILD->new ShroudChild(mob);case PAPER->new PaperSwordsman(mob);case SKULL->new FlyingSkull(mob);case TOAD->new RedToad(mob);case TREE->new TreeSpirit(mob);case SCORPION->new SandScorpion(mob);default->null;};}
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
    private static final class SandScorpion extends Base {
        UUID clamped;long surfaceUntil,nextSandCheck;
        SandScorpion(TemplateMob mob){super(mob);}
        public boolean allows(int id){return id==ArmySkills.SCORPION_EMERGE||id==ArmySkills.SCORPION_CLAW||id==ArmySkills.SCORPION_SONG;}
        public boolean canStart(int id,LivingEntity target){return id==ArmySkills.SCORPION_EMERGE?mob.burrowed():!mob.burrowed();}
        public int choose(LivingEntity target,long now){
            if(mob.burrowed())return mob.distanceToSqr(target)<=20.25?ArmySkills.SCORPION_EMERGE:0;
            return mob.distanceToSqr(target)<=25&&mob.attack().ready(ArmySkills.SCORPION_SONG,now)?ArmySkills.SCORPION_SONG:ArmySkills.SCORPION_CLAW;
        }
        public void tick(long now){
            if(now<nextSandCheck)return;nextSandCheck=now+10;
            boolean sand=mob.onGround()&&level().getBlockState(mob.blockPosition().below()).is(net.minecraft.tags.BlockTags.SAND)&&!mob.isInWater();
            var target=mob.getTarget();
            if(mob.burrowed()&&!sand){
                // Harmless self-targeted emergence retains the ordinary persisted action clock,
                // even if terrain changes when no enemy is visible.
                mob.startSkill(ArmySkills.SCORPION_EMERGE,mob);
            }else if(!mob.isNoAi()&&sand&&!mob.burrowed()&&now>=surfaceUntil&&mob.skillId()==0
                    &&(!mob.validEnemy(target)||mob.distanceToSqr(target)>36))mob.setBurrowed(true);
        }
        public void started(int id,LivingEntity target){
            if(id==ArmySkills.SCORPION_EMERGE){mob.setBurrowed(false);surfaceUntil=level().getGameTime()+100;}
            if(id==ArmySkills.SCORPION_CLAW)clamped=null;
        }
        public void move(LivingEntity target,long now){
            mob.setSprinting(mob.burrowed());
            if(mob.burrowed()){mob.getNavigation().moveTo(target,1.45);return;}
            var toward=target.position().subtract(mob.position()).multiply(1,0,1).normalize();
            double side=(now/20%2==0?1:-1)*1.1;
            navigate(target.position().subtract(toward.scale(2)).add(-toward.z*side,0,toward.x*side),1.1);
        }
        public void impact(SkillDefinition skill,int frame){
            if(skill.id()==ArmySkills.SCORPION_EMERGE)return;
            if(skill.id()==ArmySkills.SCORPION_SONG){
                mob.playSound(SoundEvents.AMETHYST_BLOCK_RESONATE,1.2F,1.8F);
                for(var target:level().getEntitiesOfClass(net.minecraft.server.level.ServerPlayer.class,mob.getBoundingBox().inflate(5),p->mob.validEnemy(p)&&mob.distanceToSqr(p)<=25&&mob.hasLineOfSight(p))){
                    target.addEffect(new MobEffectInstance(MobEffects.CONFUSION,140));
                    target.addEffect(new MobEffectInstance(MobEffects.DIG_SLOWDOWN,100,1));
                    target.addEffect(new MobEffectInstance(BlueprintEntities.SAND_RESONANCE.get(),100));
                }
                return;
            }
            var target=victim();if(!mob.validEnemy(target)||!mob.hasLineOfSight(target)||mob.distanceToSqr(target)>9)return;
            if(frame==12){
                if(!CombatGeometry.contains(mob.position(),mob.attack().direction(),CombatGeometry.Shape.SECTOR,3,1.4,80,1.6,target.getBoundingBox()))return;
                if(target.hurt(mob.damageSources().mobAttack(mob),3)){clamped=target.getUUID();target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,12,4),mob);}
            }else if(frame==20&&target.getUUID().equals(clamped)){
                target.invulnerableTime=0;
                if(target.hurt(mob.damageSources().mobAttack(mob),5))target.addEffect(new MobEffectInstance(MobEffects.POISON,60),mob);
                clamped=null;
            }
        }
        public CompoundTag save(){var t=new CompoundTag();t.putLong("SurfaceUntil",surfaceUntil);if(clamped!=null)t.putUUID("Clamped",clamped);return t;}
        public void load(CompoundTag t){surfaceUntil=t.getLong("SurfaceUntil");clamped=t.hasUUID("Clamped")?t.getUUID("Clamped"):null;}
    }

    private static final class TreeSpirit extends Base {
        net.minecraft.core.BlockPos rootPoint=net.minecraft.core.BlockPos.ZERO;
        boolean waking;long nextWakeScan;
        TreeSpirit(TemplateMob mob){super(mob);}
        public boolean allows(int id){return id==ArmySkills.TREE_WAKE||id==ArmySkills.TREE_SWEEP||id==ArmySkills.TREE_ROOTS;}
        public boolean canStart(int id,LivingEntity target){return mob.treeAwake()&&(id!=ArmySkills.TREE_WAKE||waking);}
        public int choose(LivingEntity target,long now){
            if(!mob.treeAwake())return 0;
            return mob.distanceToSqr(target)>9&&mob.attack().ready(ArmySkills.TREE_ROOTS,now)?ArmySkills.TREE_ROOTS:ArmySkills.TREE_SWEEP;
        }
        private void awaken(LivingEntity target){
            if(mob.treeAwake()||!mob.validEnemy(target))return;
            mob.setTreeAwake(true);mob.setTarget(target);waking=true;
            try{mob.startSkill(ArmySkills.TREE_WAKE,target);}finally{waking=false;}
            mob.playSound(SoundEvents.WOOD_BREAK,.9F,.55F);
        }
        public void tick(long now){
            if(mob.skillId()==ArmySkills.TREE_ROOTS&&mob.actionAge(0)<28&&now%5==0&&level().hasChunkAt(rootPoint))
                level().sendParticles(new net.minecraft.core.particles.BlockParticleOption(net.minecraft.core.particles.ParticleTypes.BLOCK,net.minecraft.world.level.block.Blocks.DIRT.defaultBlockState()),rootPoint.getX()+.5,rootPoint.getY()+.1,rootPoint.getZ()+.5,5,.6,.03,.6,.015);
            if(mob.treeAwake()||now<nextWakeScan)return;nextWakeScan=now+10;
            var enemy=mob.getTarget();if(mob.validEnemy(enemy)&&mob.distanceToSqr(enemy)<=25&&mob.hasLineOfSight(enemy)){awaken(enemy);return;}
            level().getEntitiesOfClass(net.minecraft.server.level.ServerPlayer.class,mob.getBoundingBox().inflate(5),p->mob.validEnemy(p)&&mob.distanceToSqr(p)<=25&&mob.hasLineOfSight(p))
                .stream().min(java.util.Comparator.comparingDouble(mob::distanceToSqr)).ifPresent(this::awaken);
        }
        public void hurtAccepted(DamageSource source,boolean frontal){
            if(source.getEntity() instanceof LivingEntity living)awaken(living);
        }
        public void move(LivingEntity target,long now){
            mob.setSprinting(false);if(!mob.treeAwake()){mob.getNavigation().stop();return;}mob.getNavigation().moveTo(target,.7);
        }
        public void started(int id,LivingEntity target){
            if(id==ArmySkills.TREE_ROOTS)rootPoint=target.blockPosition();
        }
        public void impact(SkillDefinition skill,int frame){
            if(skill.id()==ArmySkills.TREE_WAKE)return;
            if(skill.id()==ArmySkills.TREE_SWEEP){hit(skill,CombatGeometry.Shape.SECTOR,1.4,1,.65,false);return;}
            if(!level().hasChunkAt(rootPoint)||!level().getFluidState(rootPoint).isEmpty()
                    ||!level().getBlockState(rootPoint.below()).isFaceSturdy(level(),rootPoint.below(),net.minecraft.core.Direction.UP))return;
            Vec3 at=Vec3.atBottomCenterOf(rootPoint);
            if(level().clip(new net.minecraft.world.level.ClipContext(mob.getEyePosition(),at.add(0,.5,0),net.minecraft.world.level.ClipContext.Block.COLLIDER,net.minecraft.world.level.ClipContext.Fluid.NONE,mob)).getType()!=net.minecraft.world.phys.HitResult.Type.MISS)return;
            var box=BlueprintEntities.ROOT_SNARE.get().getDimensions().makeBoundingBox(at.x,at.y,at.z);
            if(!level().noCollision(null,box)||level().getEntitiesOfClass(RootSnare.class,box.inflate(16)).size()>=2)return;
            var cage=new RootSnare(BlueprintEntities.ROOT_SNARE.get(),level());cage.setPos(at);cage.activate(mob);level().addFreshEntity(cage);
        }
        public CompoundTag save(){var t=new CompoundTag();t.putLong("RootPoint",rootPoint.asLong());return t;}
        public void load(CompoundTag t){rootPoint=net.minecraft.core.BlockPos.of(t.getLong("RootPoint"));}
    }

    private static final class RedToad extends Base {
        Vec3 tongueDirection=new Vec3(0,0,1),landing=Vec3.ZERO;
        UUID pulled;long pullUntil,burstUntil;boolean leaping,landed;
        RedToad(TemplateMob mob){super(mob);}
        public boolean allows(int id){return id==ArmySkills.TOAD_TONGUE||id==ArmySkills.TOAD_LEAP||id==ArmySkills.TOAD_BURST;}
        public boolean canStart(int id,LivingEntity target){
            if(id==ArmySkills.TOAD_BURST)return level().getGameTime()<burstUntil;
            return (mob.onGround()||mob.isInWater())&&(id!=ArmySkills.TOAD_LEAP||mob.distanceToSqr(target)>12.25);
        }
        public int choose(LivingEntity target,long now){
            if(now<burstUntil&&mob.attack().ready(ArmySkills.TOAD_BURST,now))return ArmySkills.TOAD_BURST;
            return mob.distanceToSqr(target)<=25?ArmySkills.TOAD_TONGUE:ArmySkills.TOAD_LEAP;
        }
        public void move(LivingEntity target,long now){mob.getNavigation().stop();mob.setSprinting(false);}
        public void started(int id,LivingEntity target){
            if(id==ArmySkills.TOAD_TONGUE){
                tongueDirection=target.position().add(0,Math.min(.55,target.getBbHeight()*.5),0).subtract(mob.position().add(0,.55,0)).normalize();
                mob.setTongueReach(5);
            }
            if(id==ArmySkills.TOAD_LEAP){
                Vec3 delta=target.position().subtract(mob.position()).multiply(1,0,1);
                landing=mob.position().add(delta.normalize().scale(Math.min(6,delta.length())));leaping=false;landed=false;
            }
        }
        public void tick(long now){
            if(leaping&&!landed&&mob.actionAge(0)>12&&(mob.onGround()||mob.isInWater())){
                landed=true;leaping=false;
                for(var enemy:CombatGeometry.query(level(),mob.position(),Vec3.ZERO,CombatGeometry.Shape.CIRCLE,1.8,0,360,1.4,
                    e->mob.validEnemy(e)&&mob.hasLineOfSight(e)))enemy.hurt(mob.damageSources().mobAttack(mob),4);
                level().sendParticles(net.minecraft.core.particles.ParticleTypes.POOF,mob.getX(),mob.getY()+.1,mob.getZ(),8,.6,.05,.6,.02);
            }
            if(mob.skillId()!=ArmySkills.TOAD_LEAP)leaping=false;
            if(pulled==null)return;
            var target=mob.resolve(pulled);
            if(now>=pullUntil||!mob.validEnemy(target)||mob.skillId()!=ArmySkills.TOAD_TONGUE||mob.distanceToSqr(target)>36||!mob.hasLineOfSight(target)){
                if(target!=null&&now>=pullUntil){target.setDeltaMovement(target.getDeltaMovement().multiply(0,1,0));target.hurtMarked=true;}
                pulled=null;return;
            }
            double resistance=Math.max(0,Math.min(1,target.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE)));
            Vec3 delta=mob.position().subtract(target.position()).multiply(1,0,1);
            if(delta.lengthSqr()<2.25){pulled=null;return;}
            Vec3 step=delta.normalize().scale(.22*(1-resistance));
            if(!level().hasChunkAt(net.minecraft.core.BlockPos.containing(target.position().add(step)))||!level().noCollision(target,target.getBoundingBox().move(step))){pulled=null;return;}
            target.setDeltaMovement(step.x,target.getDeltaMovement().y,step.z);target.hurtMarked=true;
        }
        public void impact(SkillDefinition skill,int frame){
            if(skill.id()==ArmySkills.TOAD_LEAP){
                Vec3 delta=landing.subtract(mob.position()).multiply(1,0,1);
                if(!level().hasChunkAt(net.minecraft.core.BlockPos.containing(landing)))return;
                // Vanilla gravity and air drag integrate this impulse; no teleport or noclip.
                mob.setOnGround(false);mob.setDeltaMovement(delta.scale(1/8.68).add(0,.65,0));mob.hasImpulse=true;leaping=true;return;
            }
            if(skill.id()==ArmySkills.TOAD_BURST){
                burstUntil=0;
                int existing=level().getEntitiesOfClass(TemplateProjectile.class,mob.getBoundingBox().inflate(16),p->p.armyMode()==3).size();
                int shots=Math.min(6,Math.max(0,12-existing));
                for(int i=0;i<shots;i++)TemplateProjectile.shootVenom(mob,i*Math.PI/3);
                return;
            }
            Vec3 from=mob.position().add(0,.55,0),end=from.add(tongueDirection.scale(5));
            var wall=level().clip(new net.minecraft.world.level.ClipContext(from,end,net.minecraft.world.level.ClipContext.Block.COLLIDER,
                net.minecraft.world.level.ClipContext.Fluid.NONE,mob));
            if(wall.getType()!=net.minecraft.world.phys.HitResult.Type.MISS)end=wall.getLocation();
            LivingEntity hit=null;double nearest=from.distanceToSqr(end);
            for(var candidate:level().getEntitiesOfClass(LivingEntity.class,new net.minecraft.world.phys.AABB(from,end).inflate(.25),e->e!=mob&&e.isAlive()&&!e.isSpectator())){
                var point=candidate.getBoundingBox().inflate(.15).clip(from,end);
                if(point.isPresent()&&from.distanceToSqr(point.get())<nearest){nearest=from.distanceToSqr(point.get());hit=candidate;}
            }
            mob.setTongueReach((float)Math.sqrt(nearest));
            if(mob.validEnemy(hit)&&hit.hurt(mob.damageSources().mobAttack(mob),(float)mob.getAttributeValue(Attributes.ATTACK_DAMAGE))
                    &&!(hit instanceof com.dynasty.DynastyBossCombat.BarHolder)){
                pulled=hit.getUUID();pullUntil=level().getGameTime()+6;
            }
        }
        public void hurtAccepted(DamageSource source,boolean frontal,float healthLost){
            if(healthLost>=6&&mob.attack().ready(ArmySkills.TOAD_BURST,level().getGameTime()))burstUntil=level().getGameTime()+80;
        }
        public CompoundTag save(){var t=new CompoundTag();t.putDouble("TongueX",tongueDirection.x);t.putDouble("TongueY",tongueDirection.y);t.putDouble("TongueZ",tongueDirection.z);
            t.putDouble("LandX",landing.x);t.putDouble("LandY",landing.y);t.putDouble("LandZ",landing.z);t.putBoolean("Leaping",leaping);t.putBoolean("Landed",landed);
            t.putLong("BurstUntil",burstUntil);t.putLong("PullUntil",pullUntil);if(pulled!=null)t.putUUID("Pulled",pulled);return t;}
        public void load(CompoundTag t){tongueDirection=new Vec3(t.getDouble("TongueX"),t.getDouble("TongueY"),t.getDouble("TongueZ")).normalize();
            landing=new Vec3(t.getDouble("LandX"),t.getDouble("LandY"),t.getDouble("LandZ"));leaping=t.getBoolean("Leaping");landed=t.getBoolean("Landed");
            burstUntil=t.getLong("BurstUntil");pullUntil=t.getLong("PullUntil");pulled=t.hasUUID("Pulled")&&pullUntil>level().getGameTime()?t.getUUID("Pulled"):null;}
    }

    private static final class FlyingSkull extends Base {
        Vec3 divePoint=Vec3.ZERO;boolean launched,contact;
        FlyingSkull(TemplateMob mob){super(mob);}
        public boolean allows(int id){return id==ArmySkills.SKULL_DIVE||id==ArmySkills.SKULL_BLOOD;}
        public boolean canStart(int id,LivingEntity target){
            return mob.getY()-target.getY()>=3 && (id!=ArmySkills.SKULL_BLOOD||mob.position().subtract(target.position()).horizontalDistanceSqr()<=9);
        }
        public int choose(LivingEntity target,long now){return mob.attack().ready(ArmySkills.SKULL_BLOOD,now)
            &&canStart(ArmySkills.SKULL_BLOOD,target)?ArmySkills.SKULL_BLOOD:ArmySkills.SKULL_DIVE;}
        public void started(int id,LivingEntity target){
            if(id==ArmySkills.SKULL_DIVE){divePoint=target.position().add(0,.65,0);launched=false;contact=false;}
        }
        public void move(LivingEntity target,long now){
            mob.setSprinting(false);
            // Twelve short collision probes per existing ten-tick movement budget.
            for(int dy:new int[]{4,3,5})for(int side:new int[]{0,1,-1,2}){
                double angle=(now/60.0)+side*Math.PI/2;
                Vec3 desired=target.position().add(side==0?0:Math.cos(angle)*2,dy,side==0?0:Math.sin(angle)*2);
                var box=mob.getType().getDimensions().makeBoundingBox(desired.x,desired.y,desired.z);
                if(!level().hasChunkAt(net.minecraft.core.BlockPos.containing(desired))
                        ||!level().hasChunkAt(net.minecraft.core.BlockPos.containing(box.minX,box.minY,box.minZ))
                        ||!level().hasChunkAt(net.minecraft.core.BlockPos.containing(box.maxX,box.maxY,box.maxZ))||!level().getWorldBorder().isWithinBounds(box)
                        ||!level().noCollision(mob,box))continue;
                var path=mob.getNavigation().createPath(desired.x,desired.y,desired.z,0);
                if(path!=null&&path.canReach()){mob.getNavigation().moveTo(path,1);return;}
            }
        }
        public void tick(long now){
            if(mob.skillId()!=ArmySkills.SKULL_DIVE||!launched)return;
            double age=mob.actionAge(0);
            if(age<14||age>=26||contact){mob.setDeltaMovement(mob.getDeltaMovement().scale(.5));return;}
            Vec3 delta=divePoint.subtract(mob.position());
            if(delta.lengthSqr()<.06||mob.horizontalCollision||mob.verticalCollision){launched=false;mob.setDeltaMovement(Vec3.ZERO);return;}
            var ray=level().clip(new net.minecraft.world.level.ClipContext(mob.getEyePosition(),mob.getEyePosition().add(delta.normalize().scale(.85)),
                net.minecraft.world.level.ClipContext.Block.COLLIDER,net.minecraft.world.level.ClipContext.Fluid.NONE,mob));
            if(ray.getType()!=net.minecraft.world.phys.HitResult.Type.MISS){launched=false;mob.setDeltaMovement(Vec3.ZERO);return;}
            mob.setDeltaMovement(delta.normalize().scale(Math.min(.8,delta.length())));
            var target=victim();
            if(mob.validEnemy(target)&&mob.getBoundingBox().inflate(.3).intersects(target.getBoundingBox())&&mob.hasLineOfSight(target)){
                contact=true;target.hurt(mob.damageSources().mobAttack(mob),(float)mob.getAttributeValue(Attributes.ATTACK_DAMAGE));
                mob.setDeltaMovement(0,.25,0);
            }
        }
        public void impact(SkillDefinition skill,int frame){
            if(skill.id()==ArmySkills.SKULL_DIVE){launched=true;return;}
            var origin=mob.blockPosition();net.minecraft.core.BlockPos floor=null;
            for(int d=0;d<8;d++){
                var p=origin.below(d);
                if(!level().hasChunkAt(p))return;
                if(level().getBlockState(p).isFaceSturdy(level(),p,net.minecraft.core.Direction.UP)){floor=p.above();break;}
            }
            if(floor==null||!level().getFluidState(floor).isEmpty()
                    ||level().getEntitiesOfClass(SkullBloodPool.class,new net.minecraft.world.phys.AABB(floor).inflate(8)).size()>=3)return;
            var pool=new SkullBloodPool(BlueprintEntities.SKULL_BLOOD_POOL.get(),level());pool.setPos(floor.getX()+.5,floor.getY()+.03,floor.getZ()+.5);
            pool.setOwner(mob);pool.activate(now());level().addFreshEntity(pool);
            for(int i=0;i<8;i++){var p=mob.position().lerp(pool.position(),i/7D);level().sendParticles(new net.minecraft.core.particles.DustParticleOptions(new org.joml.Vector3f(.2F,.03F,.04F),.8F),p.x,p.y,p.z,1,.03,0,.03,0);}
        }
        private long now(){return level().getGameTime();}
        public CompoundTag save(){var tag=new CompoundTag();tag.putDouble("DiveX",divePoint.x);tag.putDouble("DiveY",divePoint.y);tag.putDouble("DiveZ",divePoint.z);tag.putBoolean("Launched",launched);tag.putBoolean("Contact",contact);return tag;}
        public void load(CompoundTag tag){divePoint=new Vec3(tag.getDouble("DiveX"),tag.getDouble("DiveY"),tag.getDouble("DiveZ"));launched=tag.getBoolean("Launched")&&Double.isFinite(divePoint.lengthSqr());contact=tag.getBoolean("Contact");}
    }

    private static final class PaperSwordsman extends Base {
        long substitutionUntil;boolean substituting;
        PaperSwordsman(TemplateMob mob){super(mob);}
        public boolean allows(int id){return id==ArmySkills.PAPER_SLASH||id==ArmySkills.PAPER_SHED;}
        public boolean canStart(int id,LivingEntity target){return id!=ArmySkills.PAPER_SHED||substituting;}
        public int choose(LivingEntity target,long now){return ArmySkills.PAPER_SLASH;}
        public void tick(long now){if(mob.getTarget()==null||!mob.getTarget().isAlive()||mob.skillId()!=0)mob.setSprinting(false);}
        public void move(LivingEntity target,long now){
            mob.setSprinting(true);
            Vec3 forward=target.position().subtract(mob.position()).multiply(1,0,1).normalize();
            double side=((now/20+mob.getId())&1)==0?1.5:-1.5;
            Vec3 next=mob.distanceToSqr(target)>16?mob.position().add(forward.scale(3)).add(-forward.z*side,0,forward.x*side):target.position();
            navigate(next,1.25);
        }
        public void impact(SkillDefinition skill,int frame){
            if(skill.id()!=ArmySkills.PAPER_SLASH)return;
            for(var target:CombatGeometry.query(level(),mob.position(),mob.attack().direction(),CombatGeometry.Shape.SECTOR,
                    skill.maxRange(),1,skill.angleDegrees(),1.6,e->mob.validEnemy(e)&&mob.hasLineOfSight(e))){
                if(target.hurt(mob.damageSources().mobAttack(mob),(float)mob.getAttributeValue(Attributes.ATTACK_DAMAGE)))
                    //60 ticks gives a real delayed damage tick after the slash's invulnerability window.
                    target.addEffect(new MobEffectInstance(MobEffects.WITHER,60,0),mob);
                if(!mob.isAlive()||mob.attack().current()!=skill)return;
            }
        }
        public boolean preventFatal(DamageSource source,float damage){
            long now=level().getGameTime();
            if(damage<mob.getHealth()||now<substitutionUntil||source.is(DamageTypeTags.BYPASSES_INVULNERABILITY))return false;
            LivingEntity target=source.getEntity() instanceof LivingEntity living?living:mob.getTarget();
            if(!mob.validEnemy(target)||mob.distanceToSqr(target)>256)return false;
            Vec3 landing=paperLanding(mob,target);if(landing==null)return false;
            Vec3 origin=mob.position();substitutionUntil=now+1200;mob.cancelAction();mob.setHealth(Math.max(1,mob.getHealth()));
            mob.teleportTo(landing.x,landing.y,landing.z);mob.setDeltaMovement(Vec3.ZERO);mob.setTarget(target);
            // One ordinary action epoch synchronizes the re-form clip to all trackers.
            mob.attack().endStun(now);substituting=true;
            try {mob.startSkill(ArmySkills.PAPER_SHED,target);} finally {substituting=false;}
            level().sendParticles(new net.minecraft.core.particles.ItemParticleOption(net.minecraft.core.particles.ParticleTypes.ITEM,
                new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.PAPER)),origin.x,origin.y+.8,origin.z,18,.25,.6,.12,.025);
            mob.playSound(SoundEvents.BOOK_PAGE_TURN,.8F,.6F);return true;
        }
        public CompoundTag save(){var tag=new CompoundTag();tag.putLong("SubstitutionUntil",substitutionUntil);return tag;}
        public void load(CompoundTag tag){substitutionUntil=Math.min(level().getGameTime()+1200,Math.max(0,tag.getLong("SubstitutionUntil")));}
    }
    /** Nine bounded candidate columns: directly behind, then either rear diagonal. Never loads chunks. */
    static Vec3 paperLanding(TemplateMob mob,LivingEntity target){
        var level=(ServerLevel)mob.level();Vec3 forward=target.getLookAngle().multiply(1,0,1).normalize();
        if(forward.lengthSqr()<.001)return null;
        for(double angle:new double[]{0,Math.PI/4,-Math.PI/4})for(int dy:new int[]{0,1,-1}){
            Vec3 back=forward.yRot((float)angle).scale(-5),candidate=target.position().add(back).add(0,dy,0);
            var pos=net.minecraft.core.BlockPos.containing(candidate);candidate=new Vec3(candidate.x,pos.getY(),candidate.z);
            var box=mob.getType().getDimensions().makeBoundingBox(candidate.x,candidate.y,candidate.z);
            if(!level.hasChunkAt(pos)||!level.hasChunkAt(net.minecraft.core.BlockPos.containing(box.minX,box.minY,box.minZ))
                    ||!level.hasChunkAt(net.minecraft.core.BlockPos.containing(box.maxX,box.maxY,box.maxZ))
                    ||!level.getWorldBorder().isWithinBounds(box)||!level.getFluidState(pos).isEmpty()
                    ||!com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,pos,box)
                    ||!level.getEntitiesOfClass(LivingEntity.class,box,e->e!=mob&&e.isAlive()).isEmpty())continue;
            var line=level.clip(new net.minecraft.world.level.ClipContext(target.getEyePosition(),candidate.add(0,mob.getEyeHeight(),0),
                net.minecraft.world.level.ClipContext.Block.COLLIDER,net.minecraft.world.level.ClipContext.Fluid.NONE,mob));
            if(line.getType()==net.minecraft.world.phys.HitResult.Type.MISS)return candidate;
        }
        return null;
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
