package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.AttackState;
import com.dynasty.blueprint.combat.CombatGeometry;
import com.dynasty.blueprint.combat.Combatant;
import com.dynasty.blueprint.combat.CenteredGroundNavigation;
import com.dynasty.blueprint.combat.ShieldCoverMoveControl;
import com.dynasty.blueprint.combat.Faction;
import com.dynasty.blueprint.combat.MobRole;
import com.dynasty.blueprint.combat.SkillDefinition;
import com.dynasty.blueprint.combat.TacticalMemory;
import com.dynasty.blueprint.combat.TimedAttack;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.navigation.WallClimberNavigation;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.pathfinder.Path;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.HitResult;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.Comparator;
import java.util.EnumSet;
import java.util.List;
import java.util.UUID;

/** Validated template lifecycle; additional army professions compose their own server actions. */
public final class TemplateMob extends Monster implements GeoEntity, Combatant {
    public enum Kind { SWORD, SHIELD, PRIEST, BEAST, SPEAR, CROSSBOW, SCOUT, POWDER, FLAG, AXE_GUARD, GHOST, CORPSE, CHILD, PAPER, SKULL, TOAD, TREE, SCORPION, SERPENT, STONE_GUARD, CLOCKWORK_DOG, BRONZE_SNAKE, MINING_SPIDER, LANTERN_BAT, BLIND_FISH, DROWNER }
    private static final EntityDataAccessor<Boolean> BURROWED=SynchedEntityData.defineId(TemplateMob.class,EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> TREE_AWAKE=SynchedEntityData.defineId(TemplateMob.class,EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Float> TONGUE_REACH = SynchedEntityData.defineId(TemplateMob.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Integer> SKILL = SynchedEntityData.defineId(TemplateMob.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> PHASE = SynchedEntityData.defineId(TemplateMob.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> START = SynchedEntityData.defineId(TemplateMob.class, EntityDataSerializers.LONG);
    private static final EntityDataAccessor<Float> SPEED = SynchedEntityData.defineId(TemplateMob.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Integer> BUFF_TARGET = SynchedEntityData.defineId(TemplateMob.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> CLIMBING = SynchedEntityData.defineId(TemplateMob.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> POSSESSED = SynchedEntityData.defineId(TemplateMob.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Byte> CLIMB_FACE = SynchedEntityData.defineId(TemplateMob.class, EntityDataSerializers.BYTE);
    private static final EntityDataAccessor<Float> CLIMB_DISTANCE = SynchedEntityData.defineId(TemplateMob.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Long> CLIMB_START = SynchedEntityData.defineId(TemplateMob.class, EntityDataSerializers.LONG);
    private static final EntityDataAccessor<Integer> HOOK_TARGET = SynchedEntityData.defineId(TemplateMob.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> HOOK_EXPIRES = SynchedEntityData.defineId(TemplateMob.class, EntityDataSerializers.LONG);
    private static final UUID FORMATION_SPEED = UUID.fromString("10f91bd5-2b86-4fe6-a038-a340a0461011");
    private final Kind kind;
    private final ArmyBehaviors.Behavior army;
    private final TimedAttack attack = new TimedAttack();
    private final TacticalMemory tactics = new TacticalMemory();
    private final AnimatableInstanceCache animationCache = GeckoLibUtil.createInstanceCache(this);
    private UUID supportCandidate, possessedAlly, possessor;
    private long possessedUntil, linkUntil, nextTacticalScan, nextMovement, coverUntil, deathStarted = -1;
    private boolean formation, lootDropped;
    private float animationPartial;
    private long lastAnimationStart = Long.MIN_VALUE;
    private Vec3 leapDestination = Vec3.ZERO;
    private BlockPos highGround;
    private String encounterSite="";
    public String encounterSite(){return encounterSite;}
    public void bindEncounter(String key){
        int at=key.indexOf('@'),suffix=at<0?-1:key.indexOf(':',at);
        encounterSite=(suffix<0?key:key.substring(0,suffix));
        if(encounterSite.length()>256)encounterSite="";
        if(kind==Kind.CLOCKWORK_DOG)restrictTo(blockPosition(),12);
    }
    @Override public boolean canBeAffected(net.minecraft.world.effect.MobEffectInstance effect){
        if(kind==Kind.CLOCKWORK_DOG&&(effect.getEffect()==net.minecraft.world.effect.MobEffects.POISON
            ||effect.getEffect()==net.minecraft.world.effect.MobEffects.WITHER||effect.getEffect()==com.dynasty.DynastyEffects.INTERNAL_INJURY.get()))return false;
        return super.canBeAffected(effect);
    }

    public TemplateMob(EntityType<? extends TemplateMob> type, Level level, Kind kind) {
        super(type, level);
        this.kind = kind;
        this.army = ArmyBehaviors.create(this,kind);
        if(kind==Kind.CLOCKWORK_DOG)goalSelector.getAvailableGoals().stream().map(net.minecraft.world.entity.ai.goal.WrappedGoal::getGoal)
            .filter(g->g instanceof WaterAvoidingRandomStrollGoal).toList().forEach(goalSelector::removeGoal);
        this.xpReward = kind == Kind.SHIELD ? 8 : 5;
        setMaxUpStep(kind == Kind.BEAST ? 1.0F : .6F);
        if(kind==Kind.BRONZE_SNAKE)this.navigation=new net.minecraft.world.entity.ai.navigation.WallClimberNavigation(this,level);
        if (kind == Kind.BEAST) this.navigation = new com.dynasty.blueprint.combat.SummitClimberNavigation(this, level);
        else if(kind==Kind.TREE){
            goalSelector.getAvailableGoals().stream().map(net.minecraft.world.entity.ai.goal.WrappedGoal::getGoal)
                .filter(g->g instanceof WaterAvoidingRandomStrollGoal||g instanceof LookAtPlayerGoal||g instanceof RandomLookAroundGoal)
                .toList().forEach(goalSelector::removeGoal);
        }
        else if (kind == Kind.TOAD || kind == Kind.SERPENT || kind == Kind.DROWNER) {
            if(kind==Kind.SERPENT||kind==Kind.DROWNER)goalSelector.getAvailableGoals().stream().map(net.minecraft.world.entity.ai.goal.WrappedGoal::getGoal)
                .filter(g->g instanceof FloatGoal).toList().forEach(goalSelector::removeGoal);
            this.navigation=new net.minecraft.world.entity.ai.navigation.AmphibiousPathNavigation(this,level);
            setPathfindingMalus(net.minecraft.world.level.pathfinder.BlockPathTypes.WATER,0);
            setPathfindingMalus(net.minecraft.world.level.pathfinder.BlockPathTypes.WATER_BORDER,0);
            goalSelector.getAvailableGoals().stream().map(net.minecraft.world.entity.ai.goal.WrappedGoal::getGoal)
                .filter(g->g instanceof WaterAvoidingRandomStrollGoal).toList().forEach(goalSelector::removeGoal);
        }
        else if (kind == Kind.SKULL || kind == Kind.LANTERN_BAT || kind == Kind.BLIND_FISH) {
            this.navigation = new net.minecraft.world.entity.ai.navigation.FlyingPathNavigation(this,level);
            this.moveControl = new net.minecraft.world.entity.ai.control.FlyingMoveControl(this,16,true);
            setNoGravity(true);
            goalSelector.getAvailableGoals().stream().map(net.minecraft.world.entity.ai.goal.WrappedGoal::getGoal)
                .filter(g->g instanceof WaterAvoidingRandomStrollGoal).toList().forEach(goalSelector::removeGoal);
            goalSelector.addGoal(5,new net.minecraft.world.entity.ai.goal.WaterAvoidingRandomFlyingGoal(this,.65));
        }
        else if (kind == Kind.SHIELD || kind == Kind.CHILD) {
            this.navigation = new CenteredGroundNavigation(this, level);
            this.moveControl = new ShieldCoverMoveControl(this);
        }
    }

    public Kind kind() { return kind; }
    public String blueprintId() {
        return switch (kind) {
            case SWORD -> "zuwu_daoshou"; case SHIELD -> "ludun_jiashi";
            case PRIEST -> "fufa_jijiu"; case BEAST -> "shanjing_shanxiao";
            case SPEAR -> "juma_changqiangbing"; case CROSSBOW -> "liannu_zhenzu";
            case SCOUT -> "tiesuo_chihou"; case POWDER -> "kuijun_sishi"; case FLAG -> "zhenwang_zhangqiguan";
            case AXE_GUARD -> "pijia_panjiang_huwei";
            case GHOST -> "yinbing_guizu";
            case CORPSE -> "shibian_lishi";
            case CHILD -> "fuhun_baibu_tongzi";
            case PAPER -> "zhiren_jianke";
            case SKULL -> "muxue_feilu";
            case TOAD -> "chimu_zhuha";
            case TREE -> "kumu_shujing";
            case SCORPION -> "mingsha_shixie";
            case SERPENT -> "bishui_xuanjiao_youzi";
            case STONE_GUARD -> "jubi_shigandang";
            case CLOCKWORK_DOG -> "xunshan_mujiaquan";
            case BRONZE_SNAKE -> "qingtong_shuangtoushekui";
            case MINING_SPIDER -> "bazu_digongzhu";
            case LANTERN_BAT -> "youdeng_guimianfu";
            case BLIND_FISH -> "xueju_mangguyu";
            case DROWNER -> "shashui_funigui";
        };
    }
    @Override public Faction faction() { return (kind==Kind.STONE_GUARD||kind==Kind.CLOCKWORK_DOG||kind==Kind.BRONZE_SNAKE||kind==Kind.MINING_SPIDER)?Faction.CONSTRUCT: (kind == Kind.BEAST || kind == Kind.TOAD || kind == Kind.TREE || kind == Kind.SCORPION || kind == Kind.SERPENT || kind == Kind.LANTERN_BAT || kind == Kind.BLIND_FISH) ? Faction.WOODLAND : kind == Kind.AXE_GUARD ? Faction.REBELS : (kind == Kind.GHOST || kind == Kind.CORPSE || kind == Kind.CHILD || kind == Kind.PAPER || kind == Kind.SKULL || kind == Kind.DROWNER) ? Faction.SPIRITS : Faction.DYNASTY_ARMY; }
    @Override public MobRole role() {
        return switch (kind) { case SWORD,SPEAR,SCOUT,POWDER,AXE_GUARD,GHOST,CORPSE,PAPER,DROWNER -> MobRole.MELEE; case SHIELD -> MobRole.SHIELD;
            case PRIEST,FLAG,CHILD -> MobRole.SUPPORT; case CROSSBOW,SKULL,LANTERN_BAT,BLIND_FISH -> MobRole.RANGED; case BEAST,TOAD,TREE,SCORPION,SERPENT,STONE_GUARD,CLOCKWORK_DOG,BRONZE_SNAKE,MINING_SPIDER -> MobRole.BEAST; };
    }
    public TimedAttack attack() { return attack; }
    public int skillId() { return entityData.get(SKILL); }
    public long skillStartTime() { return entityData.get(START); }
    public float skillSpeed() { return entityData.get(SPEED); }
    public int buffTargetId() { return entityData.get(BUFF_TARGET); }
    public boolean hanging(){return kind==Kind.MINING_SPIDER&&entityData.get(CLIMBING);}
    void setHanging(boolean value){entityData.set(CLIMBING,value);}
    public boolean burrowed(){return entityData.get(BURROWED);}
    void setBurrowed(boolean state){entityData.set(BURROWED,state);}
    public boolean treeAwake(){return entityData.get(TREE_AWAKE);}
    void setTreeAwake(boolean awake){entityData.set(TREE_AWAKE,awake);}
    public float tongueReach(){return entityData.get(TONGUE_REACH);}
    void setTongueReach(float reach){entityData.set(TONGUE_REACH,net.minecraft.util.Mth.clamp(reach,0,5));}
    public int hookTargetId() { return entityData.get(HOOK_TARGET); }
    public long hookExpires() { return entityData.get(HOOK_EXPIRES); }
    void syncHook(LivingEntity target,long expires) {
        if(level().isClientSide)return;
        entityData.set(HOOK_TARGET,target==null?-1:target.getId());
        entityData.set(HOOK_EXPIRES,target==null?-1:expires);
    }
    /** Non-player potion maps are not a client synchronization contract. Visual state is explicit. */
    public boolean isPossessed() { return entityData.get(POSSESSED); }
    /** Server-measured horizontal direction INTO the wall, not its outward surface normal. */
    public Direction climbFace() { int face = entityData.get(CLIMB_FACE); return face < 0 ? null : Direction.from2DDataValue(face); }
    public float climbContactDistance() { return entityData.get(CLIMB_DISTANCE); }
    public long climbStartTime() { return entityData.get(CLIMB_START); }
    public boolean isCoveringBackline() {
        return kind == Kind.SHIELD && isAlive() && skillId() == 0 && !navigation.isDone()
                && level().getGameTime() < coverUntil && validEnemy(getTarget());
    }
    public AttackState skillPhase() { return AttackState.values()[Math.min(AttackState.values().length - 1, Math.max(0, entityData.get(PHASE)))]; }
    public float actionAge(float partialTick) { return skillStartTime() < 0 ? 0 : Math.max(0, level().getGameTime() - skillStartTime() + partialTick) * skillSpeed(); }

    @Override protected void defineSynchedData() {
        super.defineSynchedData(); entityData.define(BURROWED,false); entityData.define(TREE_AWAKE,false); entityData.define(TONGUE_REACH,5F); entityData.define(SKILL, 0); entityData.define(PHASE, AttackState.IDLE.ordinal());
        entityData.define(START, -1L); entityData.define(SPEED, 1F); entityData.define(BUFF_TARGET, -1); entityData.define(CLIMBING, false); entityData.define(POSSESSED, false);
        entityData.define(CLIMB_FACE, (byte)-1); entityData.define(CLIMB_DISTANCE, 0F); entityData.define(CLIMB_START, -1L);
        entityData.define(HOOK_TARGET,-1); entityData.define(HOOK_EXPIRES,-1L);
    }
    @Override protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new CombatGoal());
        goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, .65));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 12));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }
    @Override public void setTarget(LivingEntity target) {
        if (target != null && (target == this || target instanceof Combatant c && c.faction() == faction())) return;
        super.setTarget(target);
    }

    boolean validEnemy(LivingEntity other) {
        return other != null && other.isAlive() && !other.isSpectator() && !Combatant.allied(this, other)
                && !(other instanceof Player player && (player.isCreative() || player.isSpectator()));
    }
    private boolean validSupport(LivingEntity ally) {
        return ally != null && ally != this && ally.isAlive() && ally instanceof Combatant c
                && c.faction() == faction() && c.role() != MobRole.SUPPORT && c.role() != MobRole.BEAST
                && distanceToSqr(ally) <= 16 * 16 && hasLineOfSight(ally);
    }
    LivingEntity resolve(UUID id) {
        return id != null && level() instanceof ServerLevel server && server.getEntity(id) instanceof LivingEntity living ? living : null;
    }

    /** The same validation gates AI and operator/GameTest starts; no client can request a damage frame. */
    public boolean startSkill(int id, LivingEntity target) {
        if (level().isClientSide || !isAlive() || isRemoved() || !allows(id)) return false;
        SkillDefinition base = TemplateSkills.byId(id);
        if (base == null || (id == ArmySkills.SCORPION_EMERGE && target == this ? false : id == TemplateSkills.POSSESSION ? !validSupport(target) : !validEnemy(target))) return false;
        double range = distanceTo(target);
        if (range < base.minRange() || range > (id == ArmySkills.AXE_COUNTER ? 40 : base.maxRange()) || id != ArmySkills.SCORPION_EMERGE && base.requiresSight() && !hasLineOfSight(target)) return false;
        if (id == TemplateSkills.ROCK_THROW && !onHighGround(target)) return false;
        if (army != null && !army.canStart(id,target)) return false;
        Vec3 direction = target.position().subtract(position()).multiply(1, 0, 1).normalize();
        if (direction.lengthSqr() < .0001) direction = getLookAngle().multiply(1, 0, 1).normalize();
        // A fuse uses real elapsed time, not attack speed: three consecutive close seconds.
        float speed = id != ArmySkills.DETONATE && id != ArmySkills.AXE_COUNTER && id != ArmySkills.CHILD_CURSE && id != ArmySkills.SKULL_DIVE && id != ArmySkills.SKULL_BLOOD && id != ArmySkills.TOAD_LEAP && id != ArmySkills.SERPENT_COIL && id != ArmySkills.SERPENT_BITE && id != ArmySkills.STONE_SLAM && id != ArmySkills.STONE_UPPERCUT && id != ArmySkills.DOG_BITE && id != ArmySkills.DOG_ALARM && kind != Kind.BRONZE_SNAKE && kind != Kind.MINING_SPIDER && kind != Kind.LANTERN_BAT && kind != Kind.BLIND_FISH && kind != Kind.DROWNER && hasEffect(BlueprintEntities.BINGSHA_POSSESSION.get()) ? 1.3F : 1F;
        SkillDefinition effective = TemplateSkills.accelerated(base, speed);
        if (!attack.tryStart(effective, level().getGameTime(), position(), direction, target.getUUID())) return false;
        if(army!=null)army.started(id,target);
        entityData.set(SPEED, speed);
        coverUntil = 0;
        entityData.set(SKILL, id); entityData.set(START, attack.started()); entityData.set(PHASE, AttackState.WINDUP.ordinal());
        navigation.stop(); face(direction);
        if (id == TemplateSkills.POSSESSION) entityData.set(BUFF_TARGET, target.getId());
        if (id == TemplateSkills.POUNCE) {
            Vec3 towards = target.position().subtract(position()).multiply(1, 0, 1);
            leapDestination = position().add(towards.normalize().scale(Math.min(5.6, towards.length())));
        }
        BlueprintVisualEvent.start(this, effective, attack.origin(), attack.direction(), target.getId());
        playSound(kind == Kind.BEAST ? SoundEvents.FOX_AGGRO : kind == Kind.PRIEST ? SoundEvents.EVOKER_PREPARE_ATTACK : SoundEvents.PLAYER_ATTACK_SWEEP,
                .6F, kind == Kind.SHIELD ? .65F : 1F);
        return true;
    }
    private boolean allows(int id) {
        return switch (kind) {
            case SWORD -> id == TemplateSkills.SWORD_COMBO;
            case SHIELD -> id == TemplateSkills.SHIELD_COMBO;
            case PRIEST -> id == TemplateSkills.TALISMAN_VOLLEY || id == TemplateSkills.POSSESSION;
            case BEAST -> id == TemplateSkills.POUNCE || id == TemplateSkills.ROCK_THROW;
            default -> army != null && army.allows(id);
        };
    }

    @Override protected void customServerAiStep() {
        super.customServerAiStep();
        tickCombat();
    }
    private boolean poolDimensions;
    public boolean waterPool(){return kind==Kind.DROWNER&&isAlive()&&skillId()==ArmySkills.DROWNER_POOL&&actionAge(0)>=24&&actionAge(0)<84;}
    @Override public net.minecraft.world.entity.EntityDimensions getDimensions(net.minecraft.world.entity.Pose pose){
        return waterPool()?net.minecraft.world.entity.EntityDimensions.scalable(3.8F,.3F):super.getDimensions(pose);
    }
    @Override public void tick() {
        super.tick();
        if(kind==Kind.DROWNER&&poolDimensions!=waterPool()){poolDimensions=waterPool();refreshDimensions();}
        // NoAI disables autonomous selection, but explicitly started server actions still have a clock.
        if (!level().isClientSide && isNoAi()) tickCombat();
    }
    private void tickCombat() {
        if (!isAlive()) return;
        long now = level().getGameTime();
        if(army!=null)army.tick(now);
        if(!isAlive())return;
        if (now >= nextTacticalScan) { nextTacticalScan = now + 20; updateTactics(now); }
        if (possessedUntil > 0) {
            LivingEntity source = resolve(possessor);
            // An unloaded ally could not receive releaseSupport when its priest died or
            // changed links. Reconcile once both are loaded; a missing UUID alone is not death.
            if (now >= possessedUntil || source != null && (!source.isAlive()
                    || source instanceof TemplateMob priest && !getUUID().equals(priest.possessedAlly)))
                clearPossession();
        }
        entityData.set(POSSESSED, hasEffect(BlueprintEntities.BINGSHA_POSSESSION.get()));
        LivingEntity linked = resolve(possessedAlly);
        if (linkUntil > 0 && (now >= linkUntil || linked != null && !validSupport(linked))) releaseSupport();
        if (linked != null && linkUntil > now) entityData.set(BUFF_TARGET, linked.getId());
        if (attack.current() != null) {
            face(attack.direction());
            navigation.stop();
            if (skillId() != TemplateSkills.POUNCE && skillId() != ArmySkills.ROLL && skillId() != ArmySkills.GRAPPLE && skillId() != ArmySkills.SKULL_DIVE && skillId() != ArmySkills.BAT_DIVE && skillId() != ArmySkills.TOAD_LEAP)
                setDeltaMovement(getDeltaMovement().multiply(.35, 1, .35));
            attack.advance(now, this::impact);
            // Damage callbacks (e.g. thorns) may synchronously enter die(). Do not erase its
            // authoritative death clock or cancel the death visual that die() has just sent.
            if (!isAlive()) return;
            if (attack.current() == null && skillId() != 0) finishAction();
        }
        entityData.set(PHASE, attack.state(now).ordinal());
        if(kind==Kind.BRONZE_SNAKE){
            boolean bars=false;
            if(horizontalCollision)for(var d:Direction.Plane.HORIZONTAL)for(int y=0;y<2;y++){
                var p=blockPosition().relative(d).above(y);
                if(level().hasChunkAt(p)&&level().getBlockState(p).is(net.minecraft.world.level.block.Blocks.IRON_BARS))bars=true;
            }
            entityData.set(CLIMBING,bars&&isAlive());
            if(bars&&getTarget()!=null&&getTarget().getY()>getY()+.5&&skillId()==0)setDeltaMovement(getDeltaMovement().x,.18,getDeltaMovement().z);
        }
        if (kind == Kind.BEAST) {
            entityData.set(CLIMBING, horizontalCollision && getTarget() != null);
            updateClimbContact();
            if (onClimbable() && getTarget() != null && (highGround != null || getTarget().getY() > getY() + .5))
                setDeltaMovement(getDeltaMovement().x, .22, getDeltaMovement().z);
        }
    }

    private void clearClimbContact() {
        entityData.set(CLIMB_FACE, (byte)-1);
        entityData.set(CLIMB_DISTANCE, 0F);
        entityData.set(CLIMB_START, -1L);
    }

    /** Bounded real collision probes; renderers never guess a wall from the enemy's position.
     * No new navigation, movement or camera constraint is introduced. Only changed metadata
     * is synchronized, and distance is quantized to stop sub-pixel network jitter. */
    private void updateClimbContact() {
        if (!entityData.get(CLIMBING) || !isAlive()) { clearClimbContact(); return; }
        Direction previous = climbFace(), best = null;
        double reach = getBbWidth() * .5 + .18, bestDistance = Double.POSITIVE_INFINITY;
        for (Direction direction : Direction.Plane.HORIZONTAL) {
            // Include the lower collision edge as the forequarters crest a ledge. The
            // body-height probes can already be above the block while feet still climb it.
            for (double height : new double[]{.025, getBbHeight() * .35, getBbHeight() * .8}) {
                Vec3 from = position().add(0, height, 0);
                Vec3 to = from.add(direction.getStepX() * reach, 0, direction.getStepZ() * reach);
                if (!level().hasChunkAt(BlockPos.containing(to))) continue;
                var hit = level().clip(new ClipContext(from, to, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this));
                if (hit.getType() != HitResult.Type.BLOCK || hit.getDirection().getAxis() == Direction.Axis.Y) continue;
                Direction intoWall = hit.getDirection().getOpposite();
                double distance = hit.getLocation().subtract(from).horizontalDistance();
                if (distance < .001 || distance > reach) continue;
                // At inside corners prefer the established face within one texel to avoid flips.
                if (best == null || distance < bestDistance - 1.0 / 16
                        || Math.abs(distance - bestDistance) <= 1.0 / 16 && intoWall == previous) {
                    best = intoWall; bestDistance = distance;
                }
            }
        }
        if (best == null) {
            // horizontalCollision describes the preceding travel step. Once the whole
            // bounding box clears the lip it must not retain a phantom wall attachment.
            entityData.set(CLIMBING, false);
        if(kind==Kind.MINING_SPIDER)setNoGravity(false); clearClimbContact(); return;
        }
        if (previous != best || climbStartTime() < 0) entityData.set(CLIMB_START, level().getGameTime());
        entityData.set(CLIMB_FACE, (byte)best.get2DDataValue());
        entityData.set(CLIMB_DISTANCE, (float)(Math.round(bestDistance * 64) / 64.0));
    }

    private void updateTactics(long now) {
        if (!(level() instanceof ServerLevel server)) return;
        if (kind == Kind.SWORD) {
            List<TemplateMob> shields = server.getEntitiesOfClass(TemplateMob.class, getBoundingBox().inflate(12),
                    e -> e.isAlive() && e.kind == Kind.SHIELD && distanceToSqr(e) <= 144
                            && Combatant.allied(this, e) && hasLineOfSight(e));
            formation = !shields.isEmpty();
            AttributeInstance movement = getAttribute(Attributes.MOVEMENT_SPEED);
            if (movement != null) {
                if (formation && movement.getModifier(FORMATION_SPEED) == null)
                    movement.addTransientModifier(new AttributeModifier(FORMATION_SPEED, "Shield formation", .3, AttributeModifier.Operation.MULTIPLY_TOTAL));
                if (!formation) movement.removeModifier(FORMATION_SPEED);
            }
            for (TemplateMob shield : shields) {
                LivingEntity marked = shield.tactics.target(server, now);
                if (validEnemy(marked) && distanceToSqr(marked) <= 24 * 24 && hasLineOfSight(marked)) { setTarget(marked); break; }
            }
        } else if (kind == Kind.PRIEST) {
            supportCandidate = server.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(16),
                            e -> validSupport(e) && !e.hasEffect(BlueprintEntities.BINGSHA_POSSESSION.get()))
                    .stream().max(Comparator.<LivingEntity>comparingInt(e -> assaultSupport(e) ? 1 : 0)
                            .thenComparingDouble(e -> assaultSupport(e) ? -e.distanceToSqr(getTarget())
                                    : e.getAttributeValue(Attributes.ATTACK_DAMAGE)))
                    .map(Entity::getUUID).orElse(null);
        } else if ((kind == Kind.SCOUT || kind == Kind.POWDER) && attack.current() == null) {
            // Reuse the priest's live possession link as a short-lived assault signal.
            // Never redirect an attack already in flight or retain a cross-world player cache.
            server.getEntitiesOfClass(TemplateMob.class, getBoundingBox().inflate(16),
                            e -> e.kind == Kind.PRIEST && e.isAlive() && e.linkUntil > now
                                    && distanceToSqr(e) <= 256 && hasLineOfSight(e)
                                    && e.resolve(e.possessedAlly) instanceof TemplateMob powder
                                    && powder.kind == Kind.POWDER && powder.isAlive() && powder.isPossessed()
                                    && validEnemy(e.getTarget()) && distanceToSqr(e.getTarget()) <= 28 * 28
                                    && hasLineOfSight(e.getTarget()))
                    .stream().min(Comparator.comparingDouble(this::distanceToSqr))
                    .ifPresent(priest -> setTarget(priest.getTarget()));
        } else if (kind == Kind.SHIELD && validEnemy(getTarget()) && attack.state(now) == AttackState.IDLE) {
            coverBackline();
        } else if (kind == Kind.BEAST && validEnemy(getTarget()) && distanceToSqr(getTarget()) > 64) {
            // Keep a chosen summit while ascending. Re-scanning only dy=2..5 halfway up
            // used to forget a narrow pillar as soon as its top became just one block higher.
            if (highGround == null || !validHighGround(highGround) || highGround.distSqr(blockPosition()) > 100)
                highGround = findHighGround();
        }
    }

    private boolean assaultSupport(LivingEntity ally) {
        return validEnemy(getTarget()) && ally instanceof TemplateMob mob && mob.kind == Kind.POWDER
                && mob.getTarget() == getTarget();
    }

    private void coverBackline() {
        LivingEntity enemy = getTarget();
        Vec3 towardEnemy = enemy.position().subtract(position()).multiply(1, 0, 1).normalize();
        level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(12), e -> e != this && e.isAlive() && distanceToSqr(e) <= 144
                        && e instanceof Combatant c && c.faction() == faction() && (c.role() == MobRole.RANGED || c.role() == MobRole.SUPPORT)
                        && e.position().subtract(position()).dot(towardEnemy) < .5 && hasLineOfSight(e))
                .stream().min(Comparator.comparingDouble(this::distanceToSqr)).ifPresent(ally -> {
                    Vec3 intercept = ally.position().add(enemy.position().subtract(ally.position()).multiply(1, 0, 1).normalize().scale(1.8));
                    Path path = navigation.createPath(intercept.x, intercept.y, intercept.z, 0);
                    // Failed paths must not make a shield walk through a wall toward an unreachable cover point.
                    if (path != null && path.canReach()) {
                        navigation.moveTo(path, 1); nextMovement = level().getGameTime() + 20;
                        coverUntil = level().getGameTime() + 22;
                    }
                    if(Boolean.getBoolean("dynasty.blueprint.coverTrace"))com.dynasty.Dynasty.LOGGER.info(
                        "[blueprint-cover-plan] tick={} guard={} ally={} desired={} onGround={} reachable={} pathTarget={} nextMove={} until={}",
                        level().getGameTime(),position(),ally.position(),intercept,onGround(),path!=null&&path.canReach(),
                        path==null?"none":path.getTarget(),nextMovement,coverUntil);
                });
    }

    private BlockPos findHighGround() {
        BlockPos best = null;
        // Every integer column matters: checkerboard sampling misses lone tree trunks
        // and narrow stone pillars. This bounded search still runs only every 20 ticks.
        for (int dx = -5; dx <= 5; dx++) for (int dz = -5; dz <= 5; dz++) {
            if (dx * dx + dz * dz > 32) continue;
            for (int dy = 5; dy >= 2; dy--) {
                BlockPos feet = blockPosition().offset(dx, dy, dz);
                if (!level().hasChunkAt(feet)) continue;
                if (validHighGround(feet)) {
                    if (best == null || feet.distSqr(blockPosition()) < best.distSqr(blockPosition())) best = feet;
                    break;
                }
            }
        }
        return best;
    }
    private boolean validHighGround(BlockPos feet) {
        return level().hasChunkAt(feet) && level().getBlockState(feet.below()).isSolidRender(level(), feet.below())
                && level().isEmptyBlock(feet) && level().isEmptyBlock(feet.above())
                && level().noCollision(this, getDimensions(getPose()).makeBoundingBox(feet.getX()+.5, feet.getY(), feet.getZ()+.5));
    }
    private boolean onHighGround(LivingEntity target) {
        return getY() > target.getY() + 1.5 && (onGround() || onClimbable())
                && !level().getBlockState(blockPosition().below()).isAir();
    }

    private void impact(int frame) {
        SkillDefinition current = attack.current();
        if (current == null || !isAlive()) return;
        LivingEntity victim = resolve(attack.target());
        int index = current.impactTicks().indexOf(frame);
        switch (current.id()) {
            case TemplateSkills.SWORD_COMBO -> melee(current, 1, .2, false, false);
            case TemplateSkills.SHIELD_COMBO -> melee(current, index == 0 ? .6F : 1.3F, index == 0 ? .85 : .15, index == 0, false);
            case TemplateSkills.TALISMAN_VOLLEY -> {
                if (validEnemy(victim) && distanceToSqr(victim) <= 24 * 24 && hasLineOfSight(victim)) {
                    TemplateProjectile.shoot(this, victim, false, (float)getAttributeValue(Attributes.ATTACK_DAMAGE));
                    playSound(SoundEvents.BLAZE_SHOOT, .5F, 1.4F);
                }
            }
            case TemplateSkills.POSSESSION -> {
                if (validSupport(victim)) applySupport(victim);
                else entityData.set(BUFF_TARGET, -1);
            }
            case TemplateSkills.POUNCE -> {
                if (index == 0) {
                    Vec3 movement = leapDestination.subtract(position()).multiply(.14, 0, .14);
                    setDeltaMovement(movement.x, .48, movement.z); hasImpulse = true;
                } else melee(current, 1.15F, .35, false, true);
            }
            case TemplateSkills.ROCK_THROW -> {
                if (validEnemy(victim) && distanceToSqr(victim) <= 24 * 24 && hasLineOfSight(victim))
                    TemplateProjectile.shoot(this, victim, true, (float)getAttributeValue(Attributes.ATTACK_DAMAGE) * 1.1F);
            }
            default -> { }
        }
        if(army!=null)army.impact(current,frame);
    }

    private void melee(SkillDefinition skill, float multiplier, double knockback, boolean handoff, boolean tear) {
        if (!(level() instanceof ServerLevel server)) return;
        double range = kind == Kind.BEAST ? 2.2 : skill.maxRange();
        Vec3 origin = kind == Kind.BEAST ? position() : attack.origin();
        for (LivingEntity hit : CombatGeometry.query(server, origin, attack.direction(), CombatGeometry.Shape.SECTOR,
                range, 1, skill.angleDegrees(), 1.6, e -> validEnemy(e) && hasLineOfSight(e))) {
            // Separate authored contacts in a combo are separate attacks, not duplicate tick damage.
            hit.invulnerableTime = 0;
            if (hit.hurt(damageSources().mobAttack(this), (float)getAttributeValue(Attributes.ATTACK_DAMAGE) * multiplier)) {
                hit.knockback(knockback, -attack.direction().x, -attack.direction().z);
                if (handoff) tactics.mark(hit, level().getGameTime(), 80);
                if (tear) hit.addEffect(new MobEffectInstance(MobEffects.WITHER, 45, 0), this);
            }
            if (!isAlive() || attack.current() != skill) return;
        }
        playSound(kind == Kind.SHIELD ? SoundEvents.SHIELD_BLOCK : SoundEvents.PLAYER_ATTACK_SWEEP, .8F, .85F);
    }

    private void applySupport(LivingEntity target) {
        releaseSupport();
        target.addEffect(new MobEffectInstance(BlueprintEntities.BINGSHA_POSSESSION.get(), 160, 0, false, true, true), this);
        possessedAlly = target.getUUID(); linkUntil = level().getGameTime() + 160; entityData.set(BUFF_TARGET, target.getId());
        if (target instanceof TemplateMob mob) { mob.possessor = getUUID(); mob.possessedUntil = linkUntil; mob.entityData.set(POSSESSED, true); }
    }
    private void releaseSupport() {
        LivingEntity ally = resolve(possessedAlly);
        if (ally instanceof TemplateMob mob && getUUID().equals(mob.possessor)) mob.clearPossession();
        possessedAlly = null; linkUntil = 0; entityData.set(BUFF_TARGET, -1);
    }
    private void clearPossession() {
        removeEffect(BlueprintEntities.BINGSHA_POSSESSION.get()); possessor = null; possessedUntil = 0; entityData.set(POSSESSED, false);
    }
    public void interruptAttack(int stunTicks) {
        if (level().isClientSide || !isAlive()) return;
        if (army != null && !army.canInterrupt()) return;
        int duration=hasEffect(BlueprintEntities.JUNHUN_AURA.get())?Math.max(1,stunTicks/2):stunTicks;
        attack.stun(level().getGameTime(), duration); finishAction(); entityData.set(PHASE, AttackState.STUN.ordinal());
    }
    /** Cancel both the server clock and its tracked animation, including a failed follow-up start. */
    void cancelAction() {
        if (level().isClientSide) return;
        attack.cancel(); finishAction(); entityData.set(PHASE, attack.state(level().getGameTime()).ordinal());
    }
    private void finishAction() {
        entityData.set(SKILL, 0); entityData.set(START, -1L); entityData.set(SPEED, 1F);
        syncHook(null,-1);
        if (linkUntil == 0) entityData.set(BUFF_TARGET, -1);
        BlueprintVisualEvent.cancel(this);
    }
    private void face(Vec3 direction) {
        if(kind==Kind.BRONZE_SNAKE&&(skillId()==ArmySkills.BRONZE_REAR_STAB||skillId()==ArmySkills.BRONZE_POISON))direction=direction.scale(-1);
        float yaw = (float)(Math.atan2(direction.z, direction.x) * 180 / Math.PI) - 90;
        setYRot(yaw); yBodyRot = yaw; yHeadRot = yaw;
    }

    @Override public boolean hurt(DamageSource source, float amount) {
        if (level().isClientSide) return false;
        if (amount > 0 && isAlive() && army != null && army.evade(source)) return false;
        Entity direct = source.getDirectEntity();
        boolean projectile = source.is(DamageTypeTags.IS_PROJECTILE) || direct instanceof Projectile;
        Vec3 sourcePosition = direct == null ? source.getSourcePosition() : direct.position();
        boolean frontal = sourcePosition != null && CombatGeometry.inFront(position(), getLookAngle(), sourcePosition, 120);
        if (kind == Kind.SHIELD && frontal) {
            if (projectile) {
                if (direct instanceof Projectile) direct.discard();
                playSound(SoundEvents.SHIELD_BLOCK, .7F, .7F); return false;
            }
            if (direct instanceof LivingEntity && source.getEntity() == direct) amount *= .2F;
        }
        if (!isAlive()) return false;
        if (kind == Kind.SWORD && formation && direct instanceof AbstractArrow) amount *= .8F;
        float before=getHealth();
        boolean damaged = super.hurt(source, amount);
        if (damaged && isAlive() && army != null) army.hurtAccepted(source, frontal, Math.max(0,before-getHealth()));
        if (damaged && isAlive() && attack.current() != null && attack.current().interruptible()
                && attack.state(level().getGameTime()) == AttackState.WINDUP && amount >= Math.max(3, getMaxHealth() * .08F))
            interruptAttack(10);
        return damaged;
    }
    public boolean preventPaperFatal(DamageSource source,float damage) {
        return kind==Kind.PAPER && !level().isClientSide && isAlive() && army.preventFatal(source,damage);
    }
    @Override public boolean onClimbable() {
        // A dead wall-climber must fall under ordinary gravity. Keeping the last synchronized
        // climbing flag would continue vanilla's wall boost / slow-fall during its death clip.
        if (kind == Kind.BEAST || kind == Kind.BRONZE_SNAKE) return isAlive() && (entityData.get(CLIMBING) || super.onClimbable());
        return super.onClimbable();
    }
    @Override public boolean canBreatheUnderwater(){return kind==Kind.TOAD||kind==Kind.SERPENT||kind==Kind.DROWNER||super.canBreatheUnderwater();}
    @Override public boolean checkSpawnObstruction(net.minecraft.world.level.LevelReader reader){
        return (kind==Kind.TOAD||kind==Kind.SERPENT||kind==Kind.DROWNER)?reader.isUnobstructed(this):super.checkSpawnObstruction(reader);
    }
    @Override public void travel(Vec3 input) {
        if(kind==Kind.TREE&&!treeAwake()&&isAlive()){
            setDeltaMovement(0,getDeltaMovement().y,0);super.travel(Vec3.ZERO);return;
        }
        if((kind==Kind.TOAD||kind==Kind.SERPENT||kind==Kind.DROWNER)&&isAlive()&&isInWater()&&isControlledByLocalInstance()){
            moveRelative(.1F,input);move(net.minecraft.world.entity.MoverType.SELF,getDeltaMovement());
            setDeltaMovement(getDeltaMovement().scale(.8));calculateEntityAnimation(false);return;
        }
        if ((kind != Kind.SKULL && kind != Kind.LANTERN_BAT && kind != Kind.BLIND_FISH) || !isAlive() || isInWater() || isInLava()) {
            super.travel(input); return;
        }
        // FlyingMoveControl supplies vertical input; ground travel uses ground friction
        // and cannot provide a controlled ascent after the bite. Keep normal collision.
        if (isControlledByLocalInstance()) {
            moveRelative(.1F, input);
            move(net.minecraft.world.entity.MoverType.SELF, getDeltaMovement());
            setDeltaMovement(getDeltaMovement().scale(.85));
        }
        calculateEntityAnimation(true);
    }

    @Override public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return kind == Kind.BEAST || kind == Kind.TOAD ? super.causeFallDamage(Math.max(0, distance - 5), multiplier, source) : super.causeFallDamage(distance, multiplier, source);
    }
    @Override public boolean canBeCollidedWith() { return kind == Kind.SHIELD && !isRemoved(); }
    @Override public net.minecraft.world.entity.MobType getMobType() {
        return kind == Kind.CORPSE || kind == Kind.SKULL ? net.minecraft.world.entity.MobType.UNDEAD : super.getMobType();
    }
    public boolean isPhased() { return kind == Kind.GHOST && skillId() == ArmySkills.GHOST_PHASE && actionAge(0) < 6 && isAlive(); }
    @Override public boolean canBeHitByProjectile() { return !isPhased() && (kind == Kind.SHIELD && !isRemoved() || super.canBeHitByProjectile()); }
    @Override public boolean isPickable() { return !isPhased() && super.isPickable(); }
    @Override public boolean isPushable() { return kind != Kind.GHOST && (kind!=Kind.TREE||treeAwake()) && super.isPushable(); }
    @Override public void push(Entity other) {
        if (kind != Kind.GHOST || other instanceof com.dynasty.DynastyBossCombat.BarHolder) super.push(other);
    }
    @Override protected void doPush(Entity other) {
        if (kind != Kind.GHOST || other instanceof com.dynasty.DynastyBossCombat.BarHolder) super.doPush(other);
    }
    @Override public boolean canCollideWith(Entity other) {
        return kind == Kind.GHOST ? other instanceof com.dynasty.DynastyBossCombat.BarHolder && other.isAlive() : super.canCollideWith(other);
    }

    @Override public void die(DamageSource source) {
        if (deathStarted >= 0) return;
        super.die(source);
        if (!isDeadOrDying()) return;
        if(kind==Kind.SKULL||kind==Kind.LANTERN_BAT||kind==Kind.BLIND_FISH)setNoGravity(false);
        deathStarted = level().getGameTime(); attack.cancel(); navigation.stop(); setTarget(null); releaseSupport(); clearPossession();
        syncHook(null,-1);
        entityData.set(CLIMBING, false);
        if(kind==Kind.MINING_SPIDER)setNoGravity(false);
        clearClimbContact();
        entityData.set(SKILL, 0); entityData.set(START, deathStarted); entityData.set(SPEED, 1F);
        BlueprintVisualEvent.cancel(this);
        BlueprintVisualEvent.death(this);
        if(!level().isClientSide&&army!=null)army.died(source);
    }
    public int deathDuration() { return kind == Kind.PAPER ? 10 : kind == Kind.SHIELD ? 200 : kind == Kind.SWORD ? 60 : 44; }
    void onArmyHookHit(LivingEntity target,long epoch) {
        if(!level().isClientSide&&army!=null&&isAlive()&&skillId()==ArmySkills.GRAPPLE&&skillStartTime()==epoch)
            army.hookHit(target);
    }
    @Override protected void dropAllDeathLoot(DamageSource source) {
        if (lootDropped) return;
        lootDropped = true; super.dropAllDeathLoot(source);
    }
    @Override protected void tickDeath() {
        ++deathTime;
        if(!level().isClientSide&&army!=null)army.tickDead(level().getGameTime());
        if (!level().isClientSide && deathStarted >= 0)
            deathTime = (int)Math.min(240, Math.max(deathTime, level().getGameTime() - deathStarted));
        if (kind == Kind.SHIELD) setDeltaMovement(Vec3.ZERO);
        int duration = deathDuration();
        if (deathTime >= duration && !level().isClientSide && !isRemoved()) {
            level().broadcastEntityEvent(this, (byte)60); remove(RemovalReason.KILLED);
        }
    }
    @Override protected boolean isAffectedByFluids() { return !(kind == Kind.SHIELD && isDeadOrDying()) && super.isAffectedByFluids(); }

    @Override public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putString("BlueprintEncounterSite",encounterSite);
        if(kind==Kind.CLOCKWORK_DOG&&hasRestriction())tag.putLong("ClockworkPatrolHome",getRestrictCenter().asLong());
        tag.putBoolean("Burrowed",burrowed());
        tag.putBoolean("TreeAwake",treeAwake());tag.putFloat("TongueReach",tongueReach()); tag.put("BlueprintAttack", attack.save()); tag.putFloat("BlueprintSpeed", skillSpeed());
        tag.putBoolean("BlueprintLootDropped", lootDropped); tag.putLong("BlueprintDeathStart", deathStarted); tag.putInt("BlueprintDeathTicks", deathTime);
        tag.putLong("PossessedUntil", possessedUntil); tag.putLong("LinkUntil", linkUntil);
        if (possessor != null) tag.putUUID("Possessor", possessor);
        if (possessedAlly != null) tag.putUUID("PossessedAlly", possessedAlly);
        tag.putDouble("LeapX", leapDestination.x); tag.putDouble("LeapY", leapDestination.y); tag.putDouble("LeapZ", leapDestination.z);
        if(army!=null)tag.put("ArmyActionState",army.save());
    }
    @Override public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        encounterSite=tag.getString("BlueprintEncounterSite");if(encounterSite.length()>256)encounterSite="";
        if(kind==Kind.CLOCKWORK_DOG&&tag.contains("ClockworkPatrolHome"))restrictTo(BlockPos.of(tag.getLong("ClockworkPatrolHome")),12);
        setBurrowed(tag.getBoolean("Burrowed"));
        setTreeAwake(tag.getBoolean("TreeAwake"));
        setTongueReach(tag.contains("TongueReach")?tag.getFloat("TongueReach"):5);
        float speed = tag.getFloat("BlueprintSpeed") > 1 ? 1.3F : 1F;
        entityData.set(SPEED, speed);
        attack.load(tag.getCompound("BlueprintAttack"), id -> {
            SkillDefinition def = TemplateSkills.byId(id); return def != null && allows(id) ? TemplateSkills.accelerated(def, speed) : null;
        }, level().getGameTime());
        entityData.set(SKILL, attack.current() == null ? 0 : attack.current().id()); entityData.set(START, attack.started());
        entityData.set(PHASE, attack.state(level().getGameTime()).ordinal());
        lootDropped = tag.getBoolean("BlueprintLootDropped"); deathStarted = tag.contains("BlueprintDeathStart") ? tag.getLong("BlueprintDeathStart") : -1;
        deathTime = Math.max(0, tag.getInt("BlueprintDeathTicks"));
        if (isDeadOrDying()) { attack.cancel(); entityData.set(SKILL, 0); entityData.set(START, deathStarted); }
        possessor = tag.hasUUID("Possessor") ? tag.getUUID("Possessor") : null;
        possessedAlly = tag.hasUUID("PossessedAlly") ? tag.getUUID("PossessedAlly") : null;
        possessedUntil = tag.getLong("PossessedUntil"); linkUntil = tag.getLong("LinkUntil");
        if (possessedUntil > 0 && level().getGameTime() >= possessedUntil) clearPossession();
        entityData.set(POSSESSED, hasEffect(BlueprintEntities.BINGSHA_POSSESSION.get()));
        LivingEntity ally = resolve(possessedAlly); if (ally != null) entityData.set(BUFF_TARGET, ally.getId());
        leapDestination = new Vec3(tag.getDouble("LeapX"), tag.getDouble("LeapY"), tag.getDouble("LeapZ"));
        if(encounterSite.isBlank()&&level() instanceof ServerLevel server){
            // Upgrade old structure members once on load, using the existing persisted UUID ledger.
            for(var marker:BlueprintSpawnState.get(server).markers.values())if(marker.members.contains(getUUID())){bindEncounter(marker.key);break;}
        }
        if(army!=null)army.load(tag.getCompound("ArmyActionState"));
    }

    public String visualAnimation() {
        if (isDeadOrDying()) return "death";
        if(kind==Kind.SCORPION&&burrowed())return "burrow";
        if(kind==Kind.TREE&&!treeAwake())return "camouflage";
        if (hurtTime > 0 && skillId() == 0) return "hurt";
        if(army!=null&&skillId()!=0)return army.animation(skillId());
        if (skillId() == TemplateSkills.POSSESSION) return "buff";
        if (skillId() == TemplateSkills.ROCK_THROW) return "rock";
        if (skillId() == TemplateSkills.POUNCE) return "skill";
        if (skillId() != 0) return "attack";
        if (kind == Kind.BEAST && onClimbable() && climbFace() != null) return "climb";
        if(kind==Kind.BRONZE_SNAKE&&onClimbable())return "climb";
        if (getDeltaMovement().horizontalDistanceSqr() > .001) return isSprinting() ? "run" : "walk";
        return "idle";
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return animationCache; }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<TemplateMob>(this, "body", 0, state -> {
            String animation = visualAnimation();
            animationPartial = state.getPartialTick();
            if (lastAnimationStart != skillStartTime()) {
                lastAnimationStart = skillStartTime(); state.getController().forceAnimationReset();
            }
            RawAnimation sequence = RawAnimation.begin();
            String key = "animation." + blueprintId() + "." + animation;
            return state.setAndContinue(animation.equals("burrow") || animation.equals("camouflage") || animation.equals("idle") || animation.equals("walk") || animation.equals("run") || animation.equals("climb")
                    ? sequence.thenLoop(key) : sequence.thenPlayAndHold(key));
        }) {
            @Override protected double adjustTick(double tick) {
                boolean resetting = shouldResetTick;
                double local = super.adjustTick(tick);
                // GeckoLib polls a new queued clip only at transition tick zero. Replacing that
                // zero with a nonzero server age leaves the old idle clip installed forever.
                if (resetting || getAnimationState() != AnimationController.State.RUNNING) return local;
                if (kind == Kind.BEAST && climbFace() != null && climbStartTime() >= 0 && skillId() == 0 && isAlive())
                    return Math.max(0, level().getGameTime() - climbStartTime() + animationPartial);
                // Late observers seek to the authoritative contact frame instead of restarting the clip.
                return skillStartTime() >= 0 && (skillId() != 0 || isDeadOrDying()) ? actionAge(animationPartial) : local;
            }
        });
    }
    @Override protected SoundEvent getAmbientSound() { return kind == Kind.TOAD ? SoundEvents.FROG_AMBIENT : kind == Kind.BEAST ? SoundEvents.FOX_AMBIENT : null; }
    @Override protected SoundEvent getHurtSound(DamageSource source) { return kind==Kind.LANTERN_BAT?SoundEvents.BAT_HURT:kind==Kind.BLIND_FISH?SoundEvents.COD_HURT:kind==Kind.DROWNER?SoundEvents.DROWNED_HURT:kind == Kind.SCORPION ? SoundEvents.STONE_HIT : kind == Kind.TREE ? SoundEvents.WOOD_HIT : kind == Kind.TOAD ? SoundEvents.FROG_HURT : kind == Kind.BEAST ? SoundEvents.FOX_HURT : kind == Kind.CHILD ? SoundEvents.ALLAY_HURT : kind == Kind.PAPER ? SoundEvents.BOOK_PAGE_TURN : kind == Kind.SKULL ? SoundEvents.SKELETON_HURT : SoundEvents.PLAYER_HURT; }
    @Override protected SoundEvent getDeathSound() { return kind==Kind.LANTERN_BAT?SoundEvents.BAT_DEATH:kind==Kind.BLIND_FISH?SoundEvents.COD_DEATH:kind==Kind.DROWNER?SoundEvents.DROWNED_DEATH:kind == Kind.SCORPION ? SoundEvents.STONE_BREAK : kind == Kind.TREE ? SoundEvents.WOOD_BREAK : kind == Kind.TOAD ? SoundEvents.FROG_DEATH : kind == Kind.BEAST ? SoundEvents.FOX_DEATH : kind == Kind.CHILD ? SoundEvents.ALLAY_DEATH : kind == Kind.PAPER ? SoundEvents.FIRE_EXTINGUISH : kind == Kind.SKULL ? SoundEvents.SKELETON_DEATH : SoundEvents.ZOMBIE_DEATH; }
    @Override protected void playStepSound(BlockPos pos, net.minecraft.world.level.block.state.BlockState state) {
        if (kind == Kind.GHOST || kind == Kind.CHILD || kind == Kind.SKULL || kind == Kind.LANTERN_BAT || kind == Kind.BLIND_FISH) return;
        if(kind==Kind.SCORPION){playSound(burrowed()?SoundEvents.SAND_STEP:SoundEvents.STONE_STEP,.3F,1.4F);return;}
        if(kind==Kind.TREE){if(treeAwake())playSound(SoundEvents.WOOD_STEP,.45F,.65F);return;}
        if (kind == Kind.PAPER) playSound(SoundEvents.BOOK_PAGE_TURN, .2F, 1.6F);
        else if (kind == Kind.AXE_GUARD) playSound(SoundEvents.ARMOR_EQUIP_IRON, .35F, .65F);
        else super.playStepSound(pos, state);
    }

    private final class CombatGoal extends Goal {
        CombatGoal() { setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK)); }
        @Override public boolean canUse() { return validEnemy(getTarget()); }
        @Override public boolean canContinueToUse() { return canUse(); }
        @Override public boolean requiresUpdateEveryTick() { return true; }
        @Override public void stop() { navigation.stop(); setSprinting(false); }
        @Override public void tick() {
            LivingEntity target = getTarget();
            if (!validEnemy(target)) return;
            long now = level().getGameTime();
            if(kind==Kind.TREE&&!treeAwake()){navigation.stop();return;}
            getLookControl().setLookAt(target, 30, 30);
            if (attack.state(now) != AttackState.IDLE) { navigation.stop(); return; }
            // Goal selection precedes customServerAiStep. At a twenty-tick scan boundary
            // the old chase used to overwrite the validated cover path before it could
            // be refreshed; at its endpoint it also chased out of the guarded position.
            // Keep the finite server-owned cover plan higher priority than chase, but
            // a close enemy still has priority for the authored shield counter.
            // Navigation still advances normally; no position, velocity or player lock.
            if(kind==Kind.SHIELD&&now<coverUntil&&distanceToSqr(target)>6.25)return;
            if(army!=null){
                int id=army.choose(target,now);
                if(id>0&&attack.ready(id,now)&&startSkill(id,target))return;
                if(now>=nextMovement){nextMovement=now+10;army.move(target,now);}
                return;
            }
            if (kind == Kind.PRIEST && attack.ready(TemplateSkills.POSSESSION, now)
                    && startSkill(TemplateSkills.POSSESSION, resolve(supportCandidate))) return;
            double distance = distanceTo(target);
            // Goal selection runs before customServerAiStep. Acquire the summit before the
            // first chase can carry us away from a nearby narrow climbing opportunity.
            if (kind == Kind.BEAST && distance > 8 && highGround == null) highGround = findHighGround();
            int skill = kind == Kind.SWORD ? TemplateSkills.SWORD_COMBO : kind == Kind.SHIELD ? TemplateSkills.SHIELD_COMBO
                    : kind == Kind.PRIEST ? TemplateSkills.TALISMAN_VOLLEY : distance > 8 ? TemplateSkills.ROCK_THROW : TemplateSkills.POUNCE;
            boolean ascending = kind == Kind.BEAST && highGround != null && !onHighGround(target);
            if (!ascending && attack.ready(skill, now) && startSkill(skill, target)) return;
            if (now < nextMovement) return;
            nextMovement = now + 10;
            if (kind == Kind.PRIEST && distance < 6) {
                Vec3 retreat = position().add(position().subtract(target.position()).multiply(1, 0, 1).normalize().scale(4));
                Path path = navigation.createPath(retreat.x, retreat.y, retreat.z, 0);
                if (path != null && path.canReach()) navigation.moveTo(path, 1);
            } else if (ascending) {
                navigation.moveTo(highGround.getX() + .5, highGround.getY(), highGround.getZ() + .5, 1.1);
            } else if (kind != Kind.PRIEST || distance > 18 || !hasLineOfSight(target)) {
                setSprinting(kind == Kind.SWORD && distance < 5 || kind == Kind.BEAST);
                navigation.moveTo(target, isSprinting() ? 1.25 : 1);
            } else navigation.stop();
        }
    }
}
