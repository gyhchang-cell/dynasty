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
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.List;

/** A sliding possessed ledger: named finite pen, five real ink cuts and a back-breakable circle. */
public final class LampJudge extends Monster implements GeoEntity,Combatant {
    public static final String ID="qingdeng_panguan_guichai";
    public static final SkillDefinition NAME=new SkillDefinition(431,"judge_name",40,12,40,260,0,28,0,1.8F,.1,true,true,List.of(40));
    public static final SkillDefinition STROKES=new SkillDefinition(432,"judge_strokes",10,40,34,220,0,6,0,.75F,.2,true,true,List.of(10,18,26,34,42));
    public static final SkillDefinition CAGE=new SkillDefinition(433,"judge_cage",16,160,36,300,0,2.5,360,0,0,true,true,List.of(16));
    private static final EntityDataAccessor<Integer> SKILL=SynchedEntityData.defineId(LampJudge.class,EntityDataSerializers.INT),PHASE=SynchedEntityData.defineId(LampJudge.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> START=SynchedEntityData.defineId(LampJudge.class,EntityDataSerializers.LONG);
    private static final EntityDataAccessor<BlockPos> LAND=SynchedEntityData.defineId(LampJudge.class,EntityDataSerializers.BLOCK_POS);
    private static final EntityDataAccessor<Float> MARK_Y=SynchedEntityData.defineId(LampJudge.class,EntityDataSerializers.FLOAT),LAND_X=SynchedEntityData.defineId(LampJudge.class,EntityDataSerializers.FLOAT),LAND_Z=SynchedEntityData.defineId(LampJudge.class,EntityDataSerializers.FLOAT);
    private final TimedAttack attack=new TimedAttack();
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private long lastCombatTick=-1,nextChoice,deathStart=-1,animationStart=Long.MIN_VALUE;
    private float partial;
    private String site="";
    private BlockPos home;
    private boolean lootDropped;
    public LampJudge(EntityType<? extends LampJudge> type,Level level){super(type,level);xpReward=30;}
    public TimedAttack attack(){return attack;}
    public int skillId(){return entityData.get(SKILL);}
    public long skillStart(){return entityData.get(START);}
    public Vec3 mark(){return Vec3.atBottomCenterOf(entityData.get(LAND)).add(entityData.get(LAND_X),entityData.get(MARK_Y),entityData.get(LAND_Z));}
    public AttackState phase(){return AttackState.values()[Math.max(0,Math.min(4,entityData.get(PHASE)))];}
    public String encounterSite(){return site;}
    public void bindEncounter(String key){site=key.length()<=256?key:"";if(home==null&&!site.isBlank())home=blockPosition().immutable();}
    public static SkillDefinition skill(int id){return switch(id){case 431->NAME;case 432->STROKES;case 433->CAGE;default->null;};}
    @Override public Faction faction(){return Faction.SPIRITS;}
    @Override public MobRole role(){return MobRole.SUPPORT;}
    @Override public MobType getMobType(){return MobType.UNDEAD;}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(SKILL,0);entityData.define(PHASE,0);entityData.define(START,-1L);entityData.define(LAND,BlockPos.ZERO);entityData.define(LAND_X,0F);entityData.define(MARK_Y,0F);entityData.define(LAND_Z,0F);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(8,new LookAtPlayerGoal(this,Player.class,20));targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));}
    public boolean enemy(LivingEntity e){return e!=null&&e.isAlive()&&!e.isSpectator()&&!Combatant.allied(this,e)&&!(e instanceof Player p&&p.isCreative());}
    private boolean loaded(AABB box){for(double x:new double[]{box.minX,box.maxX})for(double z:new double[]{box.minZ,box.maxZ})if(!level().hasChunkAt(BlockPos.containing(x,box.minY,z)))return false;return level().getWorldBorder().isWithinBounds(box);}
    private BlockPos cageFloor(Vec3 point){
        var base=BlockPos.containing(point);for(int dy=2;dy>=-3;dy--){var feet=base.above(dy);var box=new AABB(point.x-3.5,feet.getY(),point.z-3.5,point.x+3.5,feet.getY()+3,point.z+3.5);if(!loaded(box))return null;
            boolean floor=true;
            for(int x=-3;x<=3;x++)for(int z=-3;z<=3;z++)if(x*x+z*z<=10){var cell=BlockPos.containing(point.x+x,feet.getY(),point.z+z);if(!level().getBlockState(cell.below()).isFaceSturdy(level(),cell.below(),Direction.UP)||!level().getFluidState(cell).isEmpty())floor=false;}
            if(floor&&level().noCollision(this,box))return feet;
        }return null;
    }
    private void face(Vec3 direction){setYRot((float)Math.toDegrees(Math.atan2(-direction.x,direction.z)));setYHeadRot(getYRot());yBodyRot=getYRot();}
    private void markAt(Vec3 point){var block=BlockPos.containing(point);entityData.set(LAND,block);entityData.set(LAND_X,(float)(point.x-block.getX()-.5));entityData.set(MARK_Y,(float)(point.y-block.getY()));entityData.set(LAND_Z,(float)(point.z-block.getZ()-.5));}
    public boolean startSkill(int id,LivingEntity target){
        var def=skill(id);if(level().isClientSide||!isAlive()||def==null||!enemy(target)||!hasLineOfSight(target)||Math.abs(target.getY()-getY())>3)return false;
        double distance=target.position().subtract(position()).horizontalDistanceSqr();if(distance>def.maxRange()*def.maxRange())return false;
        var dir=target.position().subtract(position()).multiply(1,0,1).normalize();if(dir.lengthSqr()<.001)dir=new Vec3(0,0,1);
        var floor=def==CAGE?cageFloor(target.position()):null;if(def==CAGE&&(floor==null||home!=null&&floor.distSqr(home)>32*32))return false;
        if(!attack.tryStart(def,level().getGameTime(),position(),dir,target.getUUID()))return false;
        markAt(def==CAGE?new Vec3(target.getX(),floor.getY(),target.getZ()):target.position());face(dir);navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);sync();BlueprintVisualEvent.start(this,def,mark(),dir,target.getId());return true;
    }
    private void sync(){entityData.set(SKILL,attack.current()==null?0:attack.current().id());entityData.set(START,attack.started());entityData.set(PHASE,attack.state(level().getGameTime()).ordinal());}
    @Override protected void customServerAiStep(){super.customServerAiStep();combat();}
    @Override public void tick(){super.tick();if(!level().isClientSide&&isNoAi())combat();}
    private void stop(int ticks){clearSpells(true);attack.stun(level().getGameTime(),ticks);BlueprintVisualEvent.cancel(this);setDeltaMovement(0,getDeltaMovement().y,0);sync();}
    private void combat(){
        if(!isAlive())return;long now=level().getGameTime();if(now==lastCombatTick)return;
        if(attack.current()!=null&&lastCombatTick>=0&&(now-lastCombatTick>1||now<lastCombatTick)){attack.cancel();clearSpells(false);BlueprintVisualEvent.cancel(this);}lastCombatTick=now;
        if(attack.current()!=null){var def=attack.current();long age=now-attack.started();face(attack.direction());
            if(def!=CAGE||age<16||age>=176){navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);}
            if(def==NAME&&age<=35){var e=attack.target()==null?null:((ServerLevel)level()).getEntity(attack.target());if(!(e instanceof LivingEntity target)||!enemy(target)||distanceToSqr(target)>64*64||!loaded(target.getBoundingBox())){stop(25);return;}markAt(target.position());}
            if(def==CAGE&&age>=16&&age<176&&!isNoAi())navigation.moveTo(mark().x,mark().y,mark().z,.6);
            if(def==CAGE&&age==176)clearSpells(true);
            attack.advance(now,this::impact);
        }
        sync();if(isNoAi()||attack.state(now)!=AttackState.IDLE)return;var target=getTarget();if(home!=null&&(blockPosition().distSqr(home)>32*32||target!=null&&target.blockPosition().distSqr(home)>32*32)){setTarget(null);navigation.moveTo(home.getX()+.5,home.getY(),home.getZ()+.5,.7);return;}
        if(!enemy(target)){setTarget(null);return;}if(now>=nextChoice){nextChoice=now+16;double range=distanceToSqr(target);if(range<6.25&&startSkill(433,target)||range>25&&startSkill(431,target)||startSkill(432,target))return;}navigation.moveTo(target,.8);
    }
    private void impact(int frame){
        if(!(level() instanceof ServerLevel world)||attack.current()==null||!isAlive())return;var def=attack.current();
        if(world.getEntitiesOfClass(JudgeSpell.class,getBoundingBox().inflate(68),e->e.ownedBy(this)).size()>=7)return;
        var type=def==NAME?EliteContent.JUDGE_PEN.get():def==STROKES?EliteContent.JUDGE_STROKE.get():EliteContent.JUDGE_CAGE.get();
        var spell=type.create(world);if(spell==null)return;
        Vec3 at;Vec3 direction=attack.direction();
        if(def==NAME)at=mark().add(0,5,0);
        else if(def==STROKES){double angle=Math.toRadians(((frame-10)/8-2)*10);var side=new Vec3(-direction.z,0,direction.x);direction=direction.scale(Math.cos(angle)).add(side.scale(Math.sin(angle)));at=position().add(side.scale(-1.25)).add(attack.direction().scale(-.25)).add(direction.scale(2.3125)).add(0,1.125,0);}
        else at=mark();
        if(!loaded(new AABB(at.x-3.5,at.y,at.z-3.5,at.x+3.5,at.y+5,at.z+3.5))){stop(25);return;}
        spell.launch(this,at,direction);world.addFreshEntity(spell);
    }
    public void breakCage(){if(!level().isClientSide&&attack.current()==CAGE)stop(35);}
    private void clearSpells(boolean cageOnly){if(level() instanceof ServerLevel world)for(var spell:world.getEntitiesOfClass(JudgeSpell.class,getBoundingBox().inflate(68),e->e.ownedBy(this)&&(!cageOnly||e.cage())).stream().limit(7).toList())spell.discard();}
    @Override public boolean hurt(DamageSource source,float amount){float before=getHealth();boolean accepted=super.hurt(source,amount);if(accepted&&!level().isClientSide&&isAlive()){
        if(attack.current()==CAGE&&phase()==AttackState.ACTIVE&&source.getEntity() instanceof LivingEntity attacker&&attacker.position().subtract(position()).multiply(1,0,1).normalize().dot(attack.direction())<-.5)breakCage();
        else if(before-getHealth()>=8&&phase()==AttackState.WINDUP)stop(25);
    }return accepted;}
    @Override public void die(DamageSource source){if(deathStart>=0)return;super.die(source);if(!isDeadOrDying())return;deathStart=level().getGameTime();attack.cancel();navigation.stop();setTarget(null);BlueprintVisualEvent.cancel(this);clearSpells(false);EliteEncounters.memberDied(this);entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);BlueprintVisualEvent.death(this);}
    @Override protected void dropAllDeathLoot(DamageSource source){if(!lootDropped){lootDropped=true;super.dropAllDeathLoot(source);}}
    @Override protected void tickDeath(){deathTime++;if(!level().isClientSide){deathTime=(int)Math.min(84,Math.max(deathTime,level().getGameTime()-deathStart));if(deathTime>=84)remove(RemovalReason.KILLED);}}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("EliteAttack",attack.save());t.putString("EncounterSite",site);if(home!=null)t.putLong("EncounterHome",home.asLong());t.putLong("Landing",entityData.get(LAND).asLong());t.putFloat("LandingX",entityData.get(LAND_X));t.putFloat("LandingZ",entityData.get(LAND_Z));t.putFloat("MarkY",entityData.get(MARK_Y));t.putLong("LastCombatTick",lastCombatTick);t.putLong("DeathStart",deathStart);t.putBoolean("LootDropped",lootDropped);}
    @Override public void readAdditionalSaveData(CompoundTag t){
        super.readAdditionalSaveData(t);home=null;bindEncounter(t.getString("EncounterSite"));
        if(t.contains("EncounterHome")){var saved=BlockPos.of(t.getLong("EncounterHome"));if(saved.distSqr(blockPosition())<=64*64)home=saved;}
        attack.load(t.getCompound("EliteAttack"),LampJudge::skill,level().getGameTime());
        var land=t.contains("Landing")?BlockPos.of(t.getLong("Landing")):blockPosition();float ox=t.getFloat("LandingX"),oz=t.getFloat("LandingZ"),oy=t.getFloat("MarkY");
        if(land.distSqr(blockPosition())<=64*64&&Float.isFinite(ox)&&Float.isFinite(oz)&&Float.isFinite(oy)&&Math.abs(ox)<=.51&&Math.abs(oz)<=.51&&oy>=0&&oy<1){entityData.set(LAND,land);entityData.set(LAND_X,ox);entityData.set(LAND_Z,oz);entityData.set(MARK_Y,oy);}else attack.cancel();
        lastCombatTick=t.contains("LastCombatTick")?t.getLong("LastCombatTick"):-1;deathStart=t.contains("DeathStart")?t.getLong("DeathStart"):-1;lootDropped=t.getBoolean("LootDropped");
        if(isDeadOrDying()){attack.cancel();entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);}else sync();
    }
    public String visualAnimation(){return isDeadOrDying()?"death":switch(skillId()){case 431->"name";case 432->"strokes";case 433->"cage";default->hurtTime>0?"hurt":getDeltaMovement().horizontalDistanceSqr()>.001?"walk":"idle";};}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<LampJudge>(this,"body",0,state->{partial=state.getPartialTick();var controller=state.getController();if(animationStart!=skillStart()){animationStart=skillStart();controller.forceAnimationReset();}String name=visualAnimation();controller.setAnimation(name.equals("idle")||name.equals("walk")?RawAnimation.begin().thenLoop("animation."+ID+"."+name):RawAnimation.begin().thenPlayAndHold("animation."+ID+"."+name));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}){
        @Override protected double adjustTick(double tick){boolean reset=shouldResetTick;double local=super.adjustTick(tick);return !reset&&getAnimationState()==AnimationController.State.RUNNING&&skillStart()>=0&&(skillId()!=0||isDeadOrDying())?Math.max(0,level().getGameTime()-skillStart()+partial):local;}
    });}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
