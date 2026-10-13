package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.*;
import com.dynasty.blueprint.combat.*;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.ai.navigation.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.*;
import net.minecraft.world.level.pathfinder.BlockPathTypes;
import net.minecraft.world.phys.*;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.List;

/** A low aquatic shell and fork-claw; all three casts use the existing server clock. */
public final class TideYasha extends Monster implements GeoEntity,Combatant {
    public static final String ID="fubo_xunhai_yecha";
    public static final SkillDefinition WAVE=new SkillDefinition(391,"tide_wave",18,40,24,180,3,14,30,1,.55,true,true,List.of(18));
    public static final SkillDefinition DIVE=new SkillDefinition(392,"tide_dive",30,1,40,240,2,8,360,1.2F,.65,true,true,List.of(30));
    public static final SkillDefinition COMBO=new SkillDefinition(393,"tide_combo",10,34,40,180,0,6,60,.75F,.25,true,true,List.of(19,31,43));
    private static final EntityDataAccessor<Integer> SKILL=SynchedEntityData.defineId(TideYasha.class,EntityDataSerializers.INT),PHASE=SynchedEntityData.defineId(TideYasha.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> START=SynchedEntityData.defineId(TideYasha.class,EntityDataSerializers.LONG);
    private static final EntityDataAccessor<BlockPos> POOL=SynchedEntityData.defineId(TideYasha.class,EntityDataSerializers.BLOCK_POS);
    private final TimedAttack attack=new TimedAttack();
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private long nextChoice,lastCombatTick=-1,deathStart=-1,animationStart=Long.MIN_VALUE;
    private float partial;
    private boolean lootDropped;
    private String site="";
    private BlockPos home;

    public TideYasha(EntityType<? extends TideYasha> type,Level level){super(type,level);xpReward=30;setPathfindingMalus(BlockPathTypes.WATER,0);moveControl=new net.minecraft.world.entity.ai.control.SmoothSwimmingMoveControl(this,60,20,.65F,1F,false);}
    public TimedAttack attack(){return attack;}
    public int skillId(){return entityData.get(SKILL);}
    public long skillStart(){return entityData.get(START);}
    public Vec3 poolPoint(){return Vec3.atBottomCenterOf(entityData.get(POOL)).add(0,.03,0);}
    public AttackState phase(){return AttackState.values()[Math.max(0,Math.min(4,entityData.get(PHASE)))];}
    public String encounterSite(){return site;}
    public void bindEncounter(String key){site=key.length()<=256?key:"";if(home==null&&!site.isEmpty())home=blockPosition().immutable();}
    public static SkillDefinition skill(int id){return switch(id){case 391->WAVE;case 392->DIVE;case 393->COMBO;default->null;};}
    @Override public Faction faction(){return Faction.SPIRITS;}
    @Override public MobRole role(){return MobRole.BEAST;}
    @Override public MobType getMobType(){return MobType.WATER;}
    @Override public boolean canBreatheUnderwater(){return true;}
    @Override protected PathNavigation createNavigation(Level level){return new AmphibiousPathNavigation(this,level);}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(SKILL,0);entityData.define(PHASE,0);entityData.define(START,-1L);entityData.define(POOL,BlockPos.ZERO);}
    @Override protected void registerGoals(){goalSelector.addGoal(8,new LookAtPlayerGoal(this,Player.class,20));targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));}
    public boolean enemy(LivingEntity e){return e!=null&&e.isAlive()&&!e.isSpectator()&&!Combatant.allied(this,e)&&!(e instanceof Player p&&p.isCreative());}

    /** Find a real loaded air/water surface. Lava, solid cells and unbounded drops are rejected. */
    private BlockPos surfaceAt(Vec3 point){
        var base=BlockPos.containing(point);
        for(int dy=2;dy>=-8;dy--){var at=base.above(dy);if(!level().hasChunkAt(at))return null;
            if(level().getBlockState(at.below()).isFaceSturdy(level(),at.below(),Direction.UP)
                &&(level().getBlockState(at).isAir()||level().getFluidState(at).is(FluidTags.WATER)))return at;
        }return null;
    }
    public boolean startSkill(int id,LivingEntity victim){
        var def=skill(id);if(level().isClientSide||!isAlive()||def==null||!enemy(victim)||!hasLineOfSight(victim))return false;
        double range=position().subtract(victim.position()).horizontalDistanceSqr();if(range<def.minRange()*def.minRange()||range>def.maxRange()*def.maxRange())return false;
        var direction=victim.position().subtract(position()).multiply(1,0,1).normalize();if(direction.lengthSqr()<.001)direction=new Vec3(0,0,1);
        var floor=id==392?surfaceAt(victim.position()):null;if(id==392&&(floor==null||Math.abs(floor.getY()-getY())>3))return false;
        if(id==391&&!level().getEntitiesOfClass(TideVortex.class,getBoundingBox().inflate(32),v->v.ownedBy(this)).isEmpty())return false;
        Vec3 origin=id==392?Vec3.atBottomCenterOf(floor).add(0,.03,0):position();
        if(!attack.tryStart(def,level().getGameTime(),origin,direction,victim.getUUID()))return false;
        if(floor!=null)entityData.set(POOL,floor);navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);face(direction);sync();
        BlueprintVisualEvent.start(this,def,origin,direction,victim.getId());return true;
    }
    private void face(Vec3 direction){setXRot(0);setYRot((float)Math.toDegrees(Math.atan2(-direction.x,direction.z)));setYHeadRot(getYRot());yBodyRot=getYRot();}
    private void sync(){entityData.set(SKILL,attack.current()==null?0:attack.current().id());entityData.set(START,attack.started());entityData.set(PHASE,attack.state(level().getGameTime()).ordinal());}
    @Override protected void customServerAiStep(){super.customServerAiStep();combat();}
    @Override public void tick(){super.tick();if(!level().isClientSide&&isNoAi())combat();}
    private void combat(){
        if(!isAlive())return;long now=level().getGameTime();if(now==lastCombatTick)return;
        if(attack.current()!=null&&lastCombatTick>=0&&(now-lastCombatTick>1||now<lastCombatTick)){attack.cancel();BlueprintVisualEvent.cancel(this);}
        lastCombatTick=now;
        if(attack.current()!=null){
            navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);long age=now-attack.started();
            face(attack.current()==DIVE&&age>=30?poolPoint().subtract(position()).multiply(1,0,1).normalize():attack.direction());
            if(attack.current()==DIVE&&age<=20&&attack.target()!=null&&level() instanceof ServerLevel world&&world.getEntity(attack.target()) instanceof LivingEntity target&&enemy(target)){
                var floor=surfaceAt(target.position());if(floor!=null&&Math.abs(floor.getY()-getY())<=3&&position().subtract(Vec3.atBottomCenterOf(floor)).horizontalDistanceSqr()<=64)entityData.set(POOL,floor);
            }
            if(attack.current()==COMBO&&((age>=10&&age<=19)||(age>=22&&age<=31)||(age>=34&&age<=43))){
                var step=attack.direction().scale(.2);var next=position().add(step);
                if(!level().hasChunkAt(BlockPos.containing(next))){attack.stun(now,30);BlueprintVisualEvent.cancel(this);}
                else{var before=position();move(MoverType.SELF,step);if(position().distanceToSqr(before)<.005){attack.stun(now,30);BlueprintVisualEvent.cancel(this);}else if(age==34&&onGround())setDeltaMovement(0,.38,0);}
            }
            attack.advance(now,this::impact);
        }
        sync();if(isNoAi()||attack.state(now)!=AttackState.IDLE)return;
        var target=getTarget();if(home!=null&&(blockPosition().distSqr(home)>32*32||target!=null&&target.blockPosition().distSqr(home)>32*32)){setTarget(null);navigation.moveTo(home.getX()+.5,home.getY(),home.getZ()+.5,.9);return;}
        if(!enemy(target)){setTarget(null);return;}
        if(now>=nextChoice){nextChoice=now+12;double distance=distanceToSqr(target);if(distance<=20.25&&startSkill(393,target)||distance>16&&startSkill(392,target)||startSkill(391,target))return;}
        navigation.moveTo(target,1);
    }
    /** One legal emergence, never a route through walls or a repeated chase teleport. */
    private Vec3 emergence(Vec3 point){
        for(double radius:new double[]{2.2,2.8})for(int i=0;i<12;i++){
            double angle=i*Math.PI/6;var floor=surfaceAt(point.add(Math.cos(angle)*radius,0,Math.sin(angle)*radius));if(floor==null)continue;
            var at=Vec3.atBottomCenterOf(floor);if(Math.abs(at.y-getY())>3||position().distanceToSqr(at)>100||home!=null&&floor.distSqr(home)>32*32)continue;
            if(!level().hasChunkAt(floor.offset(-2,0,-2))||!level().hasChunkAt(floor.offset(2,0,-2))||!level().hasChunkAt(floor.offset(-2,0,2))||!level().hasChunkAt(floor.offset(2,0,2))||!level().noCollision(this,getType().getDimensions().makeBoundingBox(at)))continue;
            if(level().clip(new ClipContext(getEyePosition(),at.add(0,.9,0),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()==HitResult.Type.MISS)return at;
        }return null;
    }
    private void impact(int frame){
        if(!(level() instanceof ServerLevel world)||!isAlive()||attack.current()==null)return;
        if(attack.current()==WAVE){
            if(!world.getEntitiesOfClass(TideVortex.class,getBoundingBox().inflate(32),v->v.ownedBy(this)).isEmpty())return;
            for(int side:new int[]{-1,1}){var vortex=EliteContent.TIDE_VORTEX.get().create(world);if(vortex!=null){vortex.launch(this,position(),attack.direction(),side);world.addFreshEntity(vortex);}}
        }else if(attack.current()==DIVE){
            var point=poolPoint();var at=emergence(point);if(at==null){attack.stun(world.getGameTime(),30);BlueprintVisualEvent.cancel(this);return;}
            teleportTo(at.x,at.y,at.z);face(point.subtract(at).multiply(1,0,1).normalize());setDeltaMovement(0,.3,0);
            for(var target:CombatGeometry.query(world,point,Vec3.ZERO,CombatGeometry.Shape.CIRCLE,2,0,360,3,this::enemy).stream().limit(12).toList()){
                if(!isAlive())return;if(hasLineOfSight(target)&&target.hurt(damageSources().mobAttack(this),(float)getAttributeValue(Attributes.ATTACK_DAMAGE)*DIVE.damageMultiplier()))target.push(0,.65,0);
            }
        }else if(attack.current()==COMBO){
            var direction=attack.direction();var right=new Vec3(-direction.z,0,direction.x);var tip=position().add(right.scale(1.25)).add(direction.scale(.3));
            for(var target:CombatGeometry.query(world,tip,direction,CombatGeometry.Shape.STRIP,2.8,1.2,60,2.5,this::enemy).stream().limit(12).toList()){
                if(!isAlive())return;if(hasLineOfSight(target)&&target.hurt(damageSources().mobAttack(this),(float)getAttributeValue(Attributes.ATTACK_DAMAGE)*(frame==43?1.1F:COMBO.damageMultiplier())))target.knockback(frame==43?.5:.25,getX()-target.getX(),getZ()-target.getZ());
            }
        }
    }
    public void clearOwned(){if(level() instanceof ServerLevel world)world.getEntitiesOfClass(TideVortex.class,getBoundingBox().inflate(48),v->v.ownedBy(this)).forEach(Entity::discard);}
    @Override public boolean hurt(DamageSource source,float amount){float before=getHealth();boolean accepted=super.hurt(source,amount);if(accepted&&!level().isClientSide&&isAlive()&&before-getHealth()>=8&&phase()==AttackState.WINDUP){attack.stun(level().getGameTime(),20);BlueprintVisualEvent.cancel(this);sync();}return accepted;}
    @Override public void die(DamageSource source){if(deathStart>=0)return;super.die(source);if(!isDeadOrDying())return;deathStart=level().getGameTime();attack.cancel();clearOwned();navigation.stop();setTarget(null);BlueprintVisualEvent.cancel(this);EliteEncounters.memberDied(this);entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);BlueprintVisualEvent.death(this);}
    @Override protected void dropAllDeathLoot(DamageSource source){if(!lootDropped){lootDropped=true;super.dropAllDeathLoot(source);}}
    @Override protected void tickDeath(){deathTime++;if(!level().isClientSide){deathTime=(int)Math.min(80,Math.max(deathTime,level().getGameTime()-deathStart));if(deathTime>=80)remove(RemovalReason.KILLED);}}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("EliteAttack",attack.save());t.putString("EncounterSite",site);if(home!=null)t.putLong("EncounterHome",home.asLong());t.putLong("Pool",entityData.get(POOL).asLong());t.putLong("LastCombatTick",lastCombatTick);t.putLong("DeathStart",deathStart);t.putBoolean("LootDropped",lootDropped);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);home=null;bindEncounter(t.getString("EncounterSite"));if(t.contains("EncounterHome")){var at=BlockPos.of(t.getLong("EncounterHome"));if(at.distSqr(blockPosition())<=64*64)home=at;}long now=level().getGameTime();attack.load(t.getCompound("EliteAttack"),TideYasha::skill,now);var pool=t.contains("Pool")?BlockPos.of(t.getLong("Pool")):blockPosition();if(pool.distSqr(blockPosition())<=16*16)entityData.set(POOL,pool);else if(attack.current()==DIVE)attack.cancel();lastCombatTick=t.contains("LastCombatTick")?t.getLong("LastCombatTick"):-1;deathStart=t.contains("DeathStart")?t.getLong("DeathStart"):-1;lootDropped=t.getBoolean("LootDropped");if(isDeadOrDying()){attack.cancel();entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);}else sync();}
    public String visualAnimation(){return isDeadOrDying()?"death":switch(skillId()){case 391->"wave";case 392->"dive";case 393->"combo";default->hurtTime>0?"hurt":getDeltaMovement().horizontalDistanceSqr()>.001?"walk":"idle";};}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<TideYasha>(this,"body",0,state->{partial=state.getPartialTick();var controller=state.getController();if(animationStart!=skillStart()){animationStart=skillStart();controller.forceAnimationReset();}String name=visualAnimation();controller.setAnimation(name.equals("idle")||name.equals("walk")?RawAnimation.begin().thenLoop("animation."+ID+"."+name):RawAnimation.begin().thenPlayAndHold("animation."+ID+"."+name));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}){
        @Override protected double adjustTick(double tick){boolean reset=shouldResetTick;double local=super.adjustTick(tick);return !reset&&getAnimationState()==AnimationController.State.RUNNING&&skillStart()>=0&&(skillId()!=0||isDeadOrDying())?Math.max(0,level().getGameTime()-skillStart()+partial):local;}
    });}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
