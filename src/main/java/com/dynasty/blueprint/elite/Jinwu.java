package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.*;
import com.dynasty.blueprint.combat.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.*;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.*;

/** One guarded-site elite; no soldier summons, biome population or extra collision parts. */
public final class Jinwu extends Monster implements GeoEntity,Combatant {
    public static final String ID="pilin_zhijinwu";
    public static final double REAR_SWEEP=1.5,CHARGE_WIDTH=1.5;
    public static final SkillDefinition SWEEP=new SkillDefinition(341,"jinwu_sweep",20,3,30,180,0,4,270,1.2F,.9,false,true,List.of(20));
    public static final SkillDefinition CHARGE=new SkillDefinition(342,"jinwu_charge",16,16,30,180,3,8,0,1.1F,.7,false,true,List.of(16));
    public static final SkillDefinition ORDER=new SkillDefinition(343,"jinwu_order",24,1,35,240,0,12,360,0,0,true,true,List.of(24));
    private static final EntityDataAccessor<Integer> SKILL=SynchedEntityData.defineId(Jinwu.class,EntityDataSerializers.INT),PHASE=SynchedEntityData.defineId(Jinwu.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> START=SynchedEntityData.defineId(Jinwu.class,EntityDataSerializers.LONG);
    private final TimedAttack attack=new TimedAttack();
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private final Set<UUID> charged=new HashSet<>();
    private long nextChoice,deathStart=-1,animationStart=Long.MIN_VALUE;
    private float stagger,partial;
    private boolean lootDropped;
    private String site="";
    public Jinwu(EntityType<? extends Jinwu> type,Level level){super(type,level);xpReward=30;}
    public TimedAttack attack(){return attack;}
    public int skillId(){return entityData.get(SKILL);}
    public long skillStart(){return entityData.get(START);}
    public AttackState phase(){return AttackState.values()[Math.max(0,Math.min(4,entityData.get(PHASE)))];}
    public String encounterSite(){return site;}
    public void bindEncounter(String key){int at=key.indexOf('@'),suffix=at<0?-1:key.indexOf(':',at);site=suffix<0?key:key.substring(0,suffix);if(site.length()>256)site="";}
    public static SkillDefinition skill(int id){return switch(id){case 341->SWEEP;case 342->CHARGE;case 343->ORDER;default->null;};}
    @Override public Faction faction(){return Faction.DYNASTY_ARMY;}
    @Override public MobRole role(){return MobRole.SHIELD;}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(SKILL,0);entityData.define(PHASE,0);entityData.define(START,-1L);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(7,new WaterAvoidingRandomStrollGoal(this,.55));goalSelector.addGoal(8,new LookAtPlayerGoal(this,Player.class,16));goalSelector.addGoal(9,new RandomLookAroundGoal(this));targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));}
    public boolean enemy(LivingEntity e){return e!=null&&e.isAlive()&&!e.isSpectator()&&!Combatant.allied(this,e)&&!(e instanceof Player p&&p.isCreative());}
    public boolean startSkill(int id,LivingEntity victim){
        var def=skill(id);if(level().isClientSide||!isAlive()||def==null||!enemy(victim)||distanceToSqr(victim)>144||!hasLineOfSight(victim))return false;
        if(id==341&&distanceToSqr(victim)>25||id==342&&(distanceToSqr(victim)<9||distanceToSqr(victim)>81))return false;
        Vec3 dir=victim.position().subtract(position()).multiply(1,0,1).normalize();if(dir.lengthSqr()<.001)dir=getLookAngle().multiply(1,0,1).normalize();
        if(!attack.tryStart(def,level().getGameTime(),position(),dir,victim.getUUID()))return false;
        charged.clear();stagger=0;navigation.stop();face(dir);sync();BlueprintVisualEvent.start(this,def,attack.origin(),dir,victim.getId());playSound(id==343?SoundEvents.ANVIL_LAND:SoundEvents.IRON_GOLEM_STEP,.8F,.65F);return true;
    }
    private void face(Vec3 dir){setYRot((float)Math.toDegrees(Math.atan2(-dir.x,dir.z)));setYHeadRot(getYRot());yBodyRot=getYRot();}
    private void sync(){entityData.set(SKILL,attack.current()==null?0:attack.current().id());entityData.set(START,attack.started());entityData.set(PHASE,attack.state(level().getGameTime()).ordinal());}
    @Override protected void customServerAiStep(){super.customServerAiStep();combat();}
    @Override public void tick(){super.tick();if(!level().isClientSide&&isNoAi())combat();}
    private void combat(){
        if(!isAlive())return;long now=level().getGameTime();
        if(attack.current()!=null){
            navigation.stop();var def=attack.current();long age=now-attack.started();
            if(def==CHARGE&&age>=16&&age<32){
                var before=position();move(MoverType.SELF,attack.direction().scale(.5));
                if(horizontalCollision||position().distanceToSqr(before)<.04){stun(40);return;}
                var dir=attack.direction();
                for(var victim:((ServerLevel)level()).getEntitiesOfClass(LivingEntity.class,new AABB(before,position()).inflate(CHARGE_WIDTH*.5,1.8,CHARGE_WIDTH*.5),e->enemy(e)&&!charged.contains(e.getUUID())&&hasLineOfSight(e))) {
                    if(!CombatGeometry.contains(before,dir,CombatGeometry.Shape.STRIP,.5,CHARGE_WIDTH,0,1.8,victim.getBoundingBox()))continue;
                    if(charged.size()>=16)break;charged.add(victim.getUUID());
                    if(victim.hurt(damageSources().mobAttack(this),(float)getAttributeValue(Attributes.ATTACK_DAMAGE)*CHARGE.damageMultiplier())){victim.knockback(CHARGE.knockback(),-dir.x,-dir.z);victim.push(0,.3,0);}
                    if(!isAlive()||attack.current()!=def)return;
                }
            }else{setDeltaMovement(getDeltaMovement().multiply(.1,1,.1));
                if(def==SWEEP&&age<20)for(var e:CombatGeometry.query((ServerLevel)level(),attack.origin(),attack.direction(),CombatGeometry.Shape.SECTOR,SWEEP.maxRange(),0,SWEEP.angleDegrees(),2,this::enemy))if(hasLineOfSight(e)){
                    var pull=position().subtract(e.position()).multiply(1,0,1).normalize().scale(.015);e.push(pull.x,0,pull.z);e.hurtMarked=true;
                }
            }
            attack.advance(now,this::impact);sync();
        }
        if(isNoAi()||attack.state(now)!=AttackState.IDLE||now<nextChoice)return;nextChoice=now+10;var victim=getTarget();if(!enemy(victim)){setTarget(null);return;}
        int[] order=distanceToSqr(victim)<=25?new int[]{343,341,342}:new int[]{342,343};
        for(int id:order)if((id!=343||!soldiers().isEmpty())&&startSkill(id,victim))return;
        navigation.moveTo(victim,.9);
    }
    private List<TemplateMob> soldiers(){return level().getEntitiesOfClass(TemplateMob.class,getBoundingBox().inflate(12),m->m.isAlive()&&m.faction()==faction()&&!site.isBlank()&&m.encounterSite().equals(site)&&distanceToSqr(m)<=144&&hasLineOfSight(m)&&switch(m.kind()){case SWORD,SPEAR,CROSSBOW,SHIELD->true;default->false;}).stream().sorted(Comparator.comparing(TemplateMob::getUUID)).limit(8).toList();}
    private void impact(int frame){
        if(!(level() instanceof ServerLevel world)||attack.current()==null||!isAlive())return;
        if(attack.current()==SWEEP){
            for(var e:CombatGeometry.query(world,attack.origin(),attack.direction(),CombatGeometry.Shape.CIRCLE,SWEEP.maxRange(),0,360,2,this::enemy)){
                boolean front=CombatGeometry.inFront(attack.origin(),attack.direction(),e.position(),SWEEP.angleDegrees());
                if(!front&&e.position().subtract(attack.origin()).horizontalDistanceSqr()>REAR_SWEEP*REAR_SWEEP||!hasLineOfSight(e))continue;
                if(e.hurt(damageSources().mobAttack(this),(float)getAttributeValue(Attributes.ATTACK_DAMAGE)*SWEEP.damageMultiplier())){e.knockback(SWEEP.knockback(),-attack.direction().x,-attack.direction().z);e.push(0,.25,0);}
                if(!isAlive()||attack.current()!=SWEEP)return;
            }
        }else if(attack.current()==ORDER){
            int slot=0;var dir=attack.direction();for(var ally:soldiers()){
                double side=(slot%4-1.5)*.9,rear=1.6+(slot/4)*1.1;slot++;
                ally.rallyUnderJinwu(this,position().subtract(dir.scale(rear)).add(-dir.z*side,0,dir.x*side),world.getGameTime()+60);
                ally.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED,60,0),this);ally.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST,60,0),this);
            }
        }
        playSound(SoundEvents.IRON_GOLEM_ATTACK,1,.65F);
    }
    private void stun(int ticks){attack.stun(level().getGameTime(),ticks);navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);BlueprintVisualEvent.cancel(this);sync();playSound(SoundEvents.ANVIL_LAND,1,.5F);}
    @Override public boolean hurt(DamageSource source,float amount){float before=getHealth();boolean result=super.hurt(source,amount);
        if(result&&isAlive()&&attack.current()==ORDER&&attack.state(level().getGameTime())==AttackState.WINDUP){stagger+=Math.max(0,before-getHealth());if(stagger>=8)stun(40);}return result;}
    @Override public void die(DamageSource source){if(deathStart>=0)return;super.die(source);if(!isDeadOrDying())return;deathStart=level().getGameTime();attack.cancel();navigation.stop();setTarget(null);BlueprintVisualEvent.cancel(this);EliteEncounters.memberDied(this);entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);}
    @Override protected void dropAllDeathLoot(DamageSource source){if(lootDropped)return;lootDropped=true;super.dropAllDeathLoot(source);}
    @Override protected void tickDeath(){deathTime++;if(!level().isClientSide){deathTime=(int)Math.min(70,Math.max(deathTime,level().getGameTime()-deathStart));if(deathTime>=70)remove(RemovalReason.KILLED);}}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("EliteAttack",attack.save());t.putString("EncounterSite",site);t.putLong("DeathStart",deathStart);t.putBoolean("LootDropped",lootDropped);t.putFloat("OrderStagger",stagger);var list=new net.minecraft.nbt.ListTag();for(var id:charged)list.add(net.minecraft.nbt.StringTag.valueOf(id.toString()));t.put("Charged",list);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);bindEncounter(t.getString("EncounterSite"));deathStart=t.contains("DeathStart")?t.getLong("DeathStart"):-1;lootDropped=t.getBoolean("LootDropped");stagger=Math.max(0,Math.min(8,t.getFloat("OrderStagger")));charged.clear();var list=t.getList("Charged",8);for(int i=0;i<Math.min(16,list.size());i++)try{charged.add(UUID.fromString(list.getString(i)));}catch(IllegalArgumentException ignored){}
        attack.load(t.getCompound("EliteAttack"),Jinwu::skill,level().getGameTime());if(isDeadOrDying()){attack.cancel();entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);}else sync();}
    public String visualAnimation(){return isDeadOrDying()?"death":switch(skillId()){case 341->"sweep";case 342->"charge";case 343->"order";default->hurtTime>0||phase()==AttackState.STUN?"hurt":getDeltaMovement().horizontalDistanceSqr()>.001?"walk":"idle";};}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers){controllers.add(new AnimationController<Jinwu>(this,"body",0,state->{partial=state.getPartialTick();var controller=state.getController();if(animationStart!=skillStart()){animationStart=skillStart();controller.forceAnimationReset();}String name=visualAnimation();controller.setAnimation(name.equals("idle")||name.equals("walk")?RawAnimation.begin().thenLoop("animation."+ID+"."+name):RawAnimation.begin().thenPlayAndHold("animation."+ID+"."+name));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}){
        @Override protected double adjustTick(double tick){boolean reset=shouldResetTick;double local=super.adjustTick(tick);return !reset&&getAnimationState()==AnimationController.State.RUNNING&&skillStart()>=0&&(skillId()!=0||isDeadOrDying())?Math.max(0,level().getGameTime()-skillStart()+partial):local;}
    });}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
