package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.*;
import com.dynasty.blueprint.combat.*;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.ForgeEventFactory;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.List;

/** Original bronze furnace lion: anchored breath, one-layer fissure and native resisted roar. */
public final class BronzeSuanni extends Monster implements GeoEntity,Combatant {
    public static final String ID="zhenmu_suanni_tonghou";
    public static final SkillDefinition FIRE=new SkillDefinition(451,"suanni_fire",24,60,44,240,0,8,90,.6F,0,true,true,List.of(24,34,44,54,64,74));
    public static final SkillDefinition STOMP=new SkillDefinition(452,"suanni_stomp",10,20,32,200,0,7,0,.6F,0,true,true,List.of(10,14,18,22,26));
    public static final SkillDefinition ROAR=new SkillDefinition(453,"suanni_roar",14,1,45,260,0,4,360,0,1.4,true,true,List.of(14));
    private static final EntityDataAccessor<Integer> SKILL=SynchedEntityData.defineId(BronzeSuanni.class,EntityDataSerializers.INT),PHASE=SynchedEntityData.defineId(BronzeSuanni.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> START=SynchedEntityData.defineId(BronzeSuanni.class,EntityDataSerializers.LONG);
    private final TimedAttack attack=new TimedAttack();
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private long lastCombatTick=-1,nextChoice,deathStart=-1,animationStart=Long.MIN_VALUE;
    private float partial;
    private String site="";
    private BlockPos home;
    private boolean lootDropped,crackStopped;
    public BronzeSuanni(EntityType<? extends BronzeSuanni> type,Level level){super(type,level);xpReward=36;}
    public TimedAttack attack(){return attack;}
    public int skillId(){return entityData.get(SKILL);}
    public long skillStart(){return entityData.get(START);}
    public AttackState phase(){return AttackState.values()[Math.max(0,Math.min(4,entityData.get(PHASE)))];}
    public String encounterSite(){return site;}
    public void bindEncounter(String key){site=key.length()<=256?key:"";if(home==null&&!site.isBlank())home=blockPosition().immutable();}
    public static SkillDefinition skill(int id){return switch(id){case 451->FIRE;case 452->STOMP;case 453->ROAR;default->null;};}
    @Override public Faction faction(){return Faction.CONSTRUCT;}
    @Override public MobRole role(){return MobRole.BEAST;}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(SKILL,0);entityData.define(PHASE,0);entityData.define(START,-1L);}
    @Override protected void registerGoals(){targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));}
    public boolean enemy(LivingEntity e){return e!=null&&e.isAlive()&&!e.isSpectator()&&!Combatant.allied(this,e)&&!(e instanceof Player p&&p.isCreative());}
    public boolean loaded(AABB box){
        if(!Double.isFinite(box.minX+box.maxX+box.minZ+box.maxZ)||box.getXsize()>24||box.getZsize()>24||!level().getWorldBorder().isWithinBounds(box)||box.minY<level().getMinBuildHeight()||box.maxY>=level().getMaxBuildHeight())return false;
        // A20m broad phase can span three chunks: inspect every covered chunk, not just four corners.
        for(int x=net.minecraft.util.Mth.floor(box.minX)>>4;x<=net.minecraft.util.Mth.floor(box.maxX)>>4;x++)for(int z=net.minecraft.util.Mth.floor(box.minZ)>>4;z<=net.minecraft.util.Mth.floor(box.maxZ)>>4;z++)if(!level().hasChunkAt(new BlockPos(x<<4,0,z<<4)))return false;
        return true;
    }
    private void face(Vec3 direction){setYRot((float)Math.toDegrees(Math.atan2(-direction.x,direction.z)));setYHeadRot(getYRot());yBodyRot=getYRot();}
    public boolean startSkill(int id,LivingEntity target){
        var def=skill(id);if(level().isClientSide||!isAlive()||def==null||!enemy(target)||!hasLineOfSight(target)||Math.abs(target.getY()-getY())>3)return false;
        double distance=target.position().subtract(position()).horizontalDistanceSqr();if(distance<def.minRange()*def.minRange()||distance>def.maxRange()*def.maxRange())return false;
        var dir=target.position().subtract(position()).multiply(1,0,1).normalize();if(dir.lengthSqr()<.001)dir=new Vec3(0,0,1);
        if(!attack.tryStart(def,level().getGameTime(),position(),dir,target.getUUID()))return false;if(def==STOMP)crackStopped=false;face(dir);navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);sync();BlueprintVisualEvent.start(this,def,position(),dir,target.getId());return true;
    }
    private void sync(){entityData.set(SKILL,attack.current()==null?0:attack.current().id());entityData.set(START,attack.started());entityData.set(PHASE,attack.state(level().getGameTime()).ordinal());}
    @Override protected void customServerAiStep(){super.customServerAiStep();combat();}
    @Override public void tick(){super.tick();if(!level().isClientSide&&isNoAi())combat();}
    private void stop(int ticks){attack.stun(level().getGameTime(),ticks);navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);clearEffects();BlueprintVisualEvent.cancel(this);sync();}
    private void combat(){
        if(!isAlive())return;long now=level().getGameTime();if(now==lastCombatTick)return;
        if(attack.current()!=null&&lastCombatTick>=0&&(now-lastCombatTick>1||now<lastCombatTick)){attack.cancel();clearEffects();BlueprintVisualEvent.cancel(this);}lastCombatTick=now;
        if(attack.current()!=null){navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);face(attack.direction());attack.advance(now,this::impact);}
        sync();if(isNoAi()||attack.state(now)!=AttackState.IDLE)return;var target=getTarget();if(home!=null&&(blockPosition().distSqr(home)>32*32||target!=null&&target.blockPosition().distSqr(home)>32*32)){setTarget(null);navigation.moveTo(home.getX()+.5,home.getY(),home.getZ()+.5,.7);return;}
        if(!enemy(target)){setTarget(null);return;}if(now>=nextChoice){nextChoice=now+16;if(distanceToSqr(target)<16&&startSkill(453,target)||startSkill(451,target)||startSkill(452,target))return;}navigation.moveTo(target,.7);
    }
    public static double sweep(long age){return Math.max(-45,Math.min(45,-45+(age-24)*90D/59));}
    private Vec3 fixedFacing(){if(!level().isClientSide)return attack.direction();double a=Math.toRadians(getYRot());return new Vec3(-Math.sin(a),0,Math.cos(a));}
    public Vec3 headDirection(long age){var f=fixedFacing();var side=new Vec3(-f.z,0,f.x);double angle=Math.toRadians(sweep(age));return f.scale(Math.cos(angle)).add(side.scale(Math.sin(angle)));}
    /** Actual head pivot(0,27,-12), mouth outlet(0,23,-32), rotated around the cast neck. */
    public Vec3 fireMuzzle(long age){return position().add(fixedFacing().scale(.75)).add(headDirection(age).scale(1.25)).add(0,1.4375,0);}
    public double flameLength(long age){
        var from=fireMuzzle(age);var end=from.add(headDirection(age).scale(8));var box=new AABB(from,end).inflate(2,1,2);if(!loaded(box))return 0;
        var hit=level().clip(new ClipContext(from,end,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this));return hit.getType()==HitResult.Type.MISS?8:Math.max(0,from.distanceTo(hit.getLocation())-.05);
    }
    public Vec3 stompOrigin(){var f=fixedFacing();return position().add(f.scale(13/16D)).add(new Vec3(-f.z,0,f.x).scale(-12/16D));}
    public BlockPos crackFloor(Vec3 at){var base=BlockPos.containing(at);for(int dy=1;dy>=-2;dy--){var feet=base.above(dy);if(!loaded(new AABB(feet).inflate(1)))return null;if(level().getFluidState(feet).isEmpty()&&level().getBlockState(feet.below()).isFaceSturdy(level(),feet.below(),Direction.UP)&&level().isEmptyBlock(feet))return feet;}return null;}
    public void breakAllowedFloor(ServerLevel world,BlockPos pos){
        if(!world.hasChunkAt(pos)||!ForgeEventFactory.getMobGriefingEvent(world,this)||world.getBlockEntity(pos)!=null)return;var state=world.getBlockState(pos);
        if((state.is(Blocks.STONE)||state.is(Blocks.DEEPSLATE)||state.is(Blocks.CRACKED_STONE_BRICKS)||state.is(Blocks.POLISHED_DEEPSLATE))&&ForgeEventFactory.onEntityDestroyBlock(this,pos,state))world.destroyBlock(pos,false,this);
    }
    public List<SuanniEffect> effects(){return level() instanceof ServerLevel world?world.getEntitiesOfClass(SuanniEffect.class,getBoundingBox().inflate(16),e->e.ownedBy(this)):List.of();}
    private void impact(int frame){
        if(!(level() instanceof ServerLevel world)||attack.current()==null||!isAlive())return;var def=attack.current();
        if(def==FIRE){if(frame==24&&effects().size()<6){var jet=EliteContent.SUANNI_FLAME.get().create(world);if(jet!=null){jet.launch(this,fireMuzzle(frame),attack.started());world.addFreshEntity(jet);}}
            var from=fireMuzzle(frame);var dir=headDirection(frame);double reach=flameLength(frame);if(reach<=0||!loaded(new AABB(from,from).inflate(10,1,10)))return;
            for(var victim:CombatGeometry.query(world,from,dir,CombatGeometry.Shape.STRIP,reach,4,90,1,this::enemy).stream().limit(16).toList()){
                if(!isAlive()||attack.current()!=FIRE)return;if(world.clip(new ClipContext(from,victim.getEyePosition(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS)continue;
                if(victim.hurt(damageSources().mobAttack(this),(float)getAttributeValue(Attributes.ATTACK_DAMAGE)*FIRE.damageMultiplier()))victim.setSecondsOnFire(3);
            }return;
        }
        if(def==STOMP){if(crackStopped||effects().size()>=6)return;var point=stompOrigin().add(attack.direction().scale((frame-10)/4+.5));var floor=crackFloor(point);if(floor==null||world.clip(new ClipContext(stompOrigin().add(0,.1,0),new Vec3(point.x,floor.getY()+.1,point.z),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS){crackStopped=true;return;}
            var crack=EliteContent.SUANNI_CRACK.get().create(world);if(crack==null)return;breakAllowedFloor(world,floor.below());double y=world.isEmptyBlock(floor.below())?floor.getY()-1:floor.getY();crack.launch(this,new Vec3(point.x,y,point.z),attack.started());if(world.addFreshEntity(crack))crack.pulse(this);return;
        }
        for(var victim:CombatGeometry.query(world,position(),attack.direction(),CombatGeometry.Shape.CIRCLE,4,0,360,3,e->e!=this&&e.isAlive()&&!(e instanceof Player p&&p.isCreative())).stream().limit(16).toList()){
            if(!isAlive()||attack.current()!=ROAR)return;if(!hasLineOfSight(victim))continue;
            if(victim.isBlocking()){var shield=victim.getUseItem().getItem();victim.stopUsingItem();if(victim instanceof Player p)p.getCooldowns().addCooldown(shield,60);}
            // Native resistance/terrain decide travel distance; do not teleport a victim six metres.
            victim.knockback(ROAR.knockback(),getX()-victim.getX(),getZ()-victim.getZ());
        }
    }
    private void clearEffects(){for(var e:effects().stream().limit(6).toList())e.discard();}
    @Override public boolean hurt(DamageSource source,float amount){float before=getHealth();boolean accepted=super.hurt(source,amount);if(accepted&&!level().isClientSide&&isAlive()&&before-getHealth()>=10&&phase()==AttackState.WINDUP)stop(35);return accepted;}
    @Override public void die(DamageSource source){if(deathStart>=0)return;super.die(source);if(!isDeadOrDying())return;deathStart=level().getGameTime();attack.cancel();navigation.stop();setTarget(null);BlueprintVisualEvent.cancel(this);clearEffects();EliteEncounters.memberDied(this);entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);BlueprintVisualEvent.death(this);}
    @Override protected void dropAllDeathLoot(DamageSource source){if(!lootDropped){lootDropped=true;super.dropAllDeathLoot(source);}}
    @Override protected void tickDeath(){deathTime++;if(!level().isClientSide){deathTime=(int)Math.min(90,Math.max(deathTime,level().getGameTime()-deathStart));if(deathTime>=90)remove(RemovalReason.KILLED);}}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("EliteAttack",attack.save());t.putString("EncounterSite",site);if(home!=null)t.putLong("EncounterHome",home.asLong());t.putLong("LastCombatTick",lastCombatTick);t.putLong("DeathStart",deathStart);t.putBoolean("LootDropped",lootDropped);t.putBoolean("CrackStopped",crackStopped);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);home=null;bindEncounter(t.getString("EncounterSite"));if(t.contains("EncounterHome")){var h=BlockPos.of(t.getLong("EncounterHome"));if(h.distSqr(blockPosition())<=64*64)home=h;}attack.load(t.getCompound("EliteAttack"),BronzeSuanni::skill,level().getGameTime());lastCombatTick=t.contains("LastCombatTick")?t.getLong("LastCombatTick"):-1;deathStart=t.contains("DeathStart")?t.getLong("DeathStart"):-1;lootDropped=t.getBoolean("LootDropped");crackStopped=t.getBoolean("CrackStopped");if(t.getCompound("EliteAttack").getInt("Skill")!=0&&attack.current()==null)clearEffects();if(isDeadOrDying()){attack.cancel();entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);}else sync();}
    public String visualAnimation(){return isDeadOrDying()?"death":switch(skillId()){case 451->"fire";case 452->"stomp";case 453->"roar";default->hurtTime>0?"hurt":getDeltaMovement().horizontalDistanceSqr()>.001?"walk":"idle";};}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<BronzeSuanni>(this,"body",0,state->{partial=state.getPartialTick();var controller=state.getController();if(animationStart!=skillStart()){animationStart=skillStart();controller.forceAnimationReset();}String name=visualAnimation();controller.setAnimation(name.equals("idle")||name.equals("walk")?RawAnimation.begin().thenLoop("animation."+ID+"."+name):RawAnimation.begin().thenPlayAndHold("animation."+ID+"."+name));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}){
        @Override protected double adjustTick(double tick){boolean reset=shouldResetTick;double local=super.adjustTick(tick);return !reset&&getAnimationState()==AnimationController.State.RUNNING&&skillStart()>=0&&(skillId()!=0||isDeadOrDying())?Math.max(0,level().getGameTime()-skillStart()+partial):local;}
    });}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
