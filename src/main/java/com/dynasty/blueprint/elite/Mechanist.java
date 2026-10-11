package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.BlueprintVisualEvent;
import com.dynasty.blueprint.combat.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.List;

public final class Mechanist extends Monster implements GeoEntity,Combatant {
    public static final String ID="qianji_bailian_yanshi";
    public static final SkillDefinition NET=new SkillDefinition(321,"mechanist_net",14,4,24,140,0,4,100,1,0,true,true,List.of(14));
    public static final SkillDefinition WHEELS=new SkillDefinition(322,"mechanist_wheels",10,40,25,160,0,9,360,1,0,true,true,List.of(10));
    public static final SkillDefinition SPIDERS=new SkillDefinition(323,"mechanist_spiders",20,1,35,240,0,12,360,1,0,true,true,List.of(20));
    private static final EntityDataAccessor<Integer> SKILL=SynchedEntityData.defineId(Mechanist.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> PHASE=SynchedEntityData.defineId(Mechanist.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> START=SynchedEntityData.defineId(Mechanist.class,EntityDataSerializers.LONG);
    private final TimedAttack attack=new TimedAttack();
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private long deathStart=-1,nextChoice,animationStart=Long.MIN_VALUE;
    private boolean lootDropped;
    private int choice;
    private String site="";
    private float partial;
    public Mechanist(EntityType<? extends Mechanist> type,Level level){super(type,level);xpReward=28;}
    public TimedAttack attack(){return attack;}
    public int skillId(){return entityData.get(SKILL);}
    public long skillStart(){return entityData.get(START);}
    public AttackState phase(){return AttackState.values()[Math.max(0,Math.min(4,entityData.get(PHASE)))];}
    public String encounterSite(){return site;}
    public void bindEncounter(String value){site=value.length()<=256?value:"";}
    public static SkillDefinition skill(int id){return switch(id){case 321->NET;case 322->WHEELS;case 323->SPIDERS;default->null;};}
    @Override public Faction faction(){return Faction.CONSTRUCT;}
    @Override public MobRole role(){return MobRole.RANGED;}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(SKILL,0);entityData.define(PHASE,0);entityData.define(START,-1L);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(7,new WaterAvoidingRandomStrollGoal(this,.6));
        goalSelector.addGoal(8,new LookAtPlayerGoal(this,Player.class,16));goalSelector.addGoal(9,new RandomLookAroundGoal(this));
        targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));}
    public boolean enemy(LivingEntity e){return e!=null&&e.isAlive()&&!e.isSpectator()&&!Combatant.allied(this,e)&&!(e instanceof Player p&&p.isCreative());}
    public boolean startSkill(int id,LivingEntity victim){
        var def=skill(id);if(level().isClientSide||!isAlive()||def==null||!enemy(victim)||distanceToSqr(victim)>144||!hasLineOfSight(victim))return false;
        if(id==NET.id()&&distanceToSqr(victim)>25)return false;
        if(id==WHEELS.id()&&distanceToSqr(victim)>100)return false;
        var forward=victim.position().subtract(position()).multiply(1,0,1).normalize();if(forward.lengthSqr()<.001)forward=getLookAngle().multiply(1,0,1).normalize();
        if(!attack.tryStart(def,level().getGameTime(),position(),forward,victim.getUUID()))return false;
        navigation.stop();setYRot((float)Math.toDegrees(Math.atan2(-forward.x,forward.z)));setYHeadRot(getYRot());yBodyRot=getYRot();sync();
        BlueprintVisualEvent.start(this,def,attack.origin(),forward,victim.getId());playSound(id==321?SoundEvents.NOTE_BLOCK_HARP.value():SoundEvents.PISTON_EXTEND,.8F,id==321?1.6F:.7F);return true;
    }
    @Override protected void customServerAiStep(){super.customServerAiStep();combat();}
    @Override public void tick(){super.tick();if(!level().isClientSide&&isNoAi())combat();}
    private void combat(){
        if(!isAlive())return;long now=level().getGameTime();
        if(attack.current()!=null){navigation.stop();setDeltaMovement(getDeltaMovement().multiply(.2,1,.2));attack.advance(now,this::impact);sync();}
        if(isNoAi()||attack.state(now)!=AttackState.IDLE||now<nextChoice)return;nextChoice=now+10;
        var target=getTarget();if(!enemy(target)){setTarget(null);return;}
        int[] order=distanceToSqr(target)<=25?new int[]{321,322,323}:new int[]{322,323};
        for(int n=0;n<order.length;n++)if(startSkill(order[Math.floorMod(choice+n,order.length)],target)){choice++;return;}
        if(distanceToSqr(target)>81)navigation.moveTo(target,.9);
        else if(distanceToSqr(target)<9){var retreat=position().subtract(target.position()).multiply(1,0,1).normalize();navigation.moveTo(getX()+retreat.x*3,getY(),getZ()+retreat.z*3,.9);}
    }
    private void sync(){entityData.set(SKILL,attack.current()==null?0:attack.current().id());entityData.set(START,attack.started());entityData.set(PHASE,attack.state(level().getGameTime()).ordinal());}
    private void impact(int frame){
        if(!(level() instanceof ServerLevel world)||attack.current()==null||!isAlive())return;
        if(attack.current()==NET){
            for(var hit:CombatGeometry.query(world,attack.origin(),attack.direction(),CombatGeometry.Shape.SECTOR,4,0,100,2, e->enemy(e)&&hasLineOfSight(e)))
                hit.addEffect(new MobEffectInstance(EliteContent.THREAD_NET.get(),50,0,false,true,true),this);
        }else if(attack.current()==WHEELS){
            int count=world.getEntitiesOfClass(MechanistWheel.class,getBoundingBox().inflate(24),w->w.ownedBy(this)).size();
            for(int side:new int[]{-1,1})if(count++<2){var wheel=EliteContent.WHEEL.get().create(world);if(wheel!=null){wheel.launch(this,attack.direction(),side);world.addFreshEntity(wheel);}}
        }else{
            int count=world.getEntitiesOfClass(ClockworkSpider.class,getBoundingBox().inflate(24),s->s.ownedBy(this)&&s.isAlive()).size();
            for(int n=0;n<4&&count<4;n++,count++){var spider=EliteContent.SPIDER.get().create(world);if(spider!=null){spider.launch(this,attack.target(),n);world.addFreshEntity(spider);}}
        }
        playSound(SoundEvents.PISTON_CONTRACT,.9F,.7F);
    }
    @Override public boolean hurt(DamageSource source,float amount){
        boolean rear=source.getEntity() instanceof LivingEntity attacker&&!CombatGeometry.inFront(position(),getLookAngle(),attacker.position(),180);
        float before=getHealth();boolean accepted=super.hurt(source,amount);
        if(accepted&&isAlive()&&rear&&before-getHealth()>=6&&attack.state(level().getGameTime())==AttackState.WINDUP){attack.stun(level().getGameTime(),32);BlueprintVisualEvent.cancel(this);sync();}return accepted;
    }
    @Override public void die(DamageSource source){
        if(deathStart>=0)return;super.die(source);if(!isDeadOrDying())return;deathStart=level().getGameTime();attack.cancel();navigation.stop();setTarget(null);
        if(level() instanceof ServerLevel world){BlueprintVisualEvent.cancel(this);EliteEncounters.memberDied(this);
            world.getEntitiesOfClass(MechanistWheel.class,getBoundingBox().inflate(32),w->w.ownedBy(this)).forEach(Entity::discard);
            world.getEntitiesOfClass(ClockworkSpider.class,getBoundingBox().inflate(32),s->s.ownedBy(this)).forEach(Entity::discard);}
        entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);
    }
    @Override protected void dropAllDeathLoot(DamageSource source){if(lootDropped)return;lootDropped=true;super.dropAllDeathLoot(source);}
    @Override protected void tickDeath(){deathTime++;if(!level().isClientSide){deathTime=(int)Math.min(60,Math.max(deathTime,level().getGameTime()-deathStart));if(deathTime>=60)remove(RemovalReason.KILLED);}}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("EliteAttack",attack.save());t.putString("EncounterSite",site);t.putLong("DeathStart",deathStart);t.putBoolean("LootDropped",lootDropped);t.putInt("Choice",choice);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);bindEncounter(t.getString("EncounterSite"));choice=t.getInt("Choice");lootDropped=t.getBoolean("LootDropped");deathStart=t.contains("DeathStart")?t.getLong("DeathStart"):-1;
        attack.load(t.getCompound("EliteAttack"),Mechanist::skill,level().getGameTime());
        if(isDeadOrDying()){attack.cancel();entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);deathTime=(int)Math.min(60,Math.max(0,level().getGameTime()-deathStart));}else sync();}
    public String visualAnimation(){return isDeadOrDying()?"death":switch(skillId()){case 321->"net";case 322->"wheels";case 323->"spiders";default->hurtTime>0||phase()==AttackState.STUN?"hurt":getDeltaMovement().horizontalDistanceSqr()>.001?"walk":"idle";};}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<Mechanist>(this,"body",0,state->{var clip=visualAnimation();partial=state.getPartialTick();var controller=state.getController();if(animationStart!=skillStart()){animationStart=skillStart();controller.forceAnimationReset();}
        controller.setAnimation(clip.equals("idle")||clip.equals("walk")?RawAnimation.begin().thenLoop("animation."+ID+"."+clip):RawAnimation.begin().thenPlayAndHold("animation."+ID+"."+clip));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}){
            @Override protected double adjustTick(double tick){boolean reset=shouldResetTick;double local=super.adjustTick(tick);if(reset||getAnimationState()!=AnimationController.State.RUNNING)return local;return skillStart()>=0&&(skillId()!=0||isDeadOrDying())?Math.max(0,level().getGameTime()-skillStart()+partial):local;}
        });}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
