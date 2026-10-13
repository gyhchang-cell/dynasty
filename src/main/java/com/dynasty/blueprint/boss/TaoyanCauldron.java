package com.dynasty.blueprint.boss;

import com.dynasty.blueprint.BlueprintVisualEvent;
import com.dynasty.blueprint.combat.*;
import com.dynasty.entity.DynastyBossBarSubscriptions;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.*;
import net.minecraft.resources.*;
import net.minecraft.server.level.*;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
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
import java.util.*;

/** Tripod war cauldron and eight-strut second form. Every damaging action uses a server clock. */
public final class TaoyanCauldron extends Monster implements GeoEntity,Combatant {
    public static final String ID="taoyan_zhishi";
    public static final SkillDefinition RAM=new SkillDefinition(501,"taoyan_ram",20,12,56,200,2,14,0,1.3F,1.3,true,true,List.of(20,21,22,23,24,25,26,27,28,29,30,31));
    public static final SkillDefinition WHIP=new SkillDefinition(502,"taoyan_whip",18,30,40,160,0,8,270,1.1F,1.8,true,true,List.of(18,23,28,33,38,43));
    public static final SkillDefinition OIL=new SkillDefinition(503,"taoyan_oil",24,12,60,240,0,14,0,.45F,0,true,true,List.of(24));
    public static final SkillDefinition BELLS=new SkillDefinition(504,"taoyan_bells",20,20,60,240,0,20,360,.35F,0,true,true,List.of(20,25,30,35));
    public static final SkillDefinition SLAM=new SkillDefinition(505,"taoyan_slam",16,20,48,260,3,12,0,1.5F,1.5,true,true,List.of(35));
    public static final SkillDefinition DRINK=new SkillDefinition(506,"taoyan_drink",24,64,32,300,0,20,360,2F,0,true,true,List.of(24,32,40,48,56,64,72,80));
    private static final EntityDataAccessor<Integer> STAGE=SynchedEntityData.defineId(TaoyanCauldron.class,EntityDataSerializers.INT),SKILL=SynchedEntityData.defineId(TaoyanCauldron.class,EntityDataSerializers.INT),PHASE=SynchedEntityData.defineId(TaoyanCauldron.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> START=SynchedEntityData.defineId(TaoyanCauldron.class,EntityDataSerializers.LONG),BORN=SynchedEntityData.defineId(TaoyanCauldron.class,EntityDataSerializers.LONG),SHIFT=SynchedEntityData.defineId(TaoyanCauldron.class,EntityDataSerializers.LONG);
    private static final EntityDataAccessor<Boolean> BOUND=SynchedEntityData.defineId(TaoyanCauldron.class,EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<BlockPos> ARENA_DATA=SynchedEntityData.defineId(TaoyanCauldron.class,EntityDataSerializers.BLOCK_POS);
    private static final EntityDataAccessor<BlockPos> LANDING=SynchedEntityData.defineId(TaoyanCauldron.class,EntityDataSerializers.BLOCK_POS);
    private final TimedAttack attack=new TimedAttack();
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private final ServerBossEvent bar=new ServerBossEvent(Component.translatable("entity.dynasty."+ID),BossEvent.BossBarColor.RED,BossEvent.BossBarOverlay.PROGRESS);
    private final DynastyBossBarSubscriptions subscriptions=new DynastyBossBarSubscriptions(this,bar);
    private final Set<UUID> hitThisAction=new HashSet<>();
    private final Map<UUID,Long> pillarGrace=new HashMap<>();
    private BlockPos arena;
    private long lastCombat=-1,nextChoice,deathStart=-1,animationStamp=Long.MIN_VALUE;
    private String animationKey="";
    private float partial;
    private boolean lootDropped;
    public TaoyanCauldron(EntityType<? extends TaoyanCauldron> type,Level level){super(type,level);xpReward=160;}
    public int form(){return entityData.get(STAGE);}
    public int skillId(){return entityData.get(SKILL);}
    public long skillStart(){return entityData.get(START);}
    public long born(){return entityData.get(BORN);}
    public long shifted(){return entityData.get(SHIFT);}
    public Vec3 landing(){return Vec3.atBottomCenterOf(entityData.get(LANDING));}
    public BlockPos arenaCentre(){return entityData.get(BOUND)?entityData.get(ARENA_DATA):null;}
    public TimedAttack attack(){return attack;}
    public AttackState phase(){return AttackState.values()[Math.max(0,Math.min(4,entityData.get(PHASE)))];}
    public boolean intro(){return born()<0||level().getGameTime()-born()<160;}
    public boolean transition(){return shifted()>=0&&level().getGameTime()-shifted()<64;}
    public void bindArena(BlockPos centre){arena=centre.immutable();entityData.set(ARENA_DATA,arena);entityData.set(BOUND,true);setPersistenceRequired();entityData.set(BORN,level().getGameTime());entityData.set(LANDING,blockPosition());}
    public static SkillDefinition skill(int id){return switch(id){case 501->RAM;case 502->WHIP;case 503->OIL;case 504->BELLS;case 505->SLAM;case 506->DRINK;default->null;};}
    @Override public Faction faction(){return Faction.SPIRITS;}
    @Override public MobRole role(){return MobRole.BEAST;}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(STAGE,1);entityData.define(SKILL,0);entityData.define(PHASE,0);entityData.define(START,-1L);entityData.define(BORN,-1L);entityData.define(SHIFT,-1L);entityData.define(LANDING,BlockPos.ZERO);entityData.define(ARENA_DATA,BlockPos.ZERO);entityData.define(BOUND,false);}
    @Override protected void registerGoals(){targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));}
    public boolean enemy(LivingEntity e){return e!=null&&e.isAlive()&&!e.isSpectator()&&!Combatant.allied(this,e)&&!(e instanceof Player p&&p.isCreative());}
    public boolean loaded(AABB b){if(!Double.isFinite(b.minX+b.maxX+b.minY+b.maxY+b.minZ+b.maxZ)||b.getXsize()>48||b.getZsize()>48||b.minY<level().getMinBuildHeight()||b.maxY>=level().getMaxBuildHeight()||!level().getWorldBorder().isWithinBounds(b))return false;for(int x=net.minecraft.util.Mth.floor(b.minX)>>4;x<=net.minecraft.util.Mth.floor(b.maxX)>>4;x++)for(int z=net.minecraft.util.Mth.floor(b.minZ)>>4;z<=net.minecraft.util.Mth.floor(b.maxZ)>>4;z++)if(!level().hasChunkAt(new BlockPos(x<<4,0,z<<4)))return false;return true;}
    public Vec3 fixedFacing(){if(!level().isClientSide)return attack.direction();double a=Math.toRadians(getYRot());return new Vec3(-Math.sin(a),0,Math.cos(a));}
    private void face(Vec3 d){setYRot((float)Math.toDegrees(Math.atan2(-d.x,d.z)));setYHeadRot(getYRot());yBodyRot=getYRot();}
    public Vec3 whipOrigin(){var f=fixedFacing();return position().add(new Vec3(-f.z,0,f.x).scale(-27/16D)).add(0,15/16D,0);}
    public Vec3 whipDirection(long age){var f=fixedFacing();var side=new Vec3(-f.z,0,f.x);double a=Math.toRadians(Math.max(-135,Math.min(135,-135+(age-18)*270D/29)));return f.scale(Math.cos(a)).add(side.scale(Math.sin(a)));}
    public Vec3 mouth(){var f=fixedFacing();return position().add(f.scale(31/16D)).add(0,34/16D,0);}
    public BlockPos floor(Vec3 at){var base=BlockPos.containing(at);for(int dy=2;dy>=-3;dy--){var p=base.above(dy);if(!loaded(new AABB(p).inflate(1)))return null;if(level().isEmptyBlock(p)&&level().getFluidState(p).isEmpty()&&level().getBlockState(p.below()).isFaceSturdy(level(),p.below(),Direction.UP))return p;}return null;}
    private boolean legalLanding(BlockPos feet){var box=getDimensions(getPose()).makeBoundingBox(feet.getX()+.5,feet.getY(),feet.getZ()+.5);if(!loaded(box)||!level().noCollision(this,box))return false;for(int x=-2;x<=2;x++)for(int z=-2;z<=2;z++)if(!level().getBlockState(feet.offset(x,-1,z)).isFaceSturdy(level(),feet.offset(x,-1,z),Direction.UP)||!level().getFluidState(feet.offset(x,0,z)).isEmpty())return false;return arena==null||feet.distSqr(arena)<=14*14;}
    public boolean startSkill(int id,LivingEntity target){var def=skill(id);if(level().isClientSide||!isAlive()||intro()||transition()||def==null||!enemy(target)||!hasLineOfSight(target)||form()==1&&(id==505||id==506)||Math.abs(target.getY()-getY())>5)return false;double d=target.position().subtract(position()).horizontalDistanceSqr();if(d<def.minRange()*def.minRange()||d>def.maxRange()*def.maxRange())return false;var direction=target.position().subtract(position()).multiply(1,0,1).normalize();if(direction.lengthSqr()<.001)direction=new Vec3(0,0,1);BlockPos land=blockPosition();if(def==RAM){var end=floor(position().add(direction.scale(12)));if(end==null||Math.abs(end.getY()-getY())>.1||!legalLanding(end))return false;}if(def==SLAM){land=floor(target.position());if(land==null||!legalLanding(land))return false;}if(!attack.tryStart(def,level().getGameTime(),position(),direction,target.getUUID()))return false;entityData.set(LANDING,land);hitThisAction.clear();face(direction);navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);sync();BlueprintVisualEvent.start(this,def,def==SLAM?landing():position(),direction,target.getId());return true;}
    private void sync(){entityData.set(SKILL,attack.current()==null?0:attack.current().id());entityData.set(START,attack.current()!=null?attack.started():deathStart>=0?deathStart:transition()?shifted():intro()?born():-1L);entityData.set(PHASE,attack.state(level().getGameTime()).ordinal());}
    public void parried(int ticks){if(isAlive()&&!intro()&&!transition())stop(Math.max(1,Math.min(40,ticks)));}
    private void stop(int ticks){attack.stun(level().getGameTime(),ticks);clearSpells();hitThisAction.clear();navigation.stop();BlueprintVisualEvent.cancel(this);sync();}
    @Override protected void customServerAiStep(){super.customServerAiStep();combat();}
    @Override public void tick(){super.tick();if(!level().isClientSide&&isNoAi())combat();}
    private void combat(){if(!isAlive())return;long now=level().getGameTime();if(now==lastCombat)return;if(born()<0)entityData.set(BORN,now);if(lastCombat>=0&&(now<lastCombat||now-lastCombat>1)&&attack.current()!=null){attack.cancel();clearSpells();hitThisAction.clear();BlueprintVisualEvent.cancel(this);}lastCombat=now;pillarGrace.entrySet().removeIf(e->e.getValue()<now);
        if(intro()){navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);sync();return;}
        if(form()==1&&getHealth()<=getMaxHealth()*.6F){attack.cancel();clearSpells();hitThisAction.clear();BlueprintVisualEvent.cancel(this);entityData.set(STAGE,2);entityData.set(SHIFT,now);getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(.27);navigation.stop();}
        bar.setProgress(Math.max(0,getHealth()/getMaxHealth()));subscriptions.tick();if(transition()){navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);sync();return;}
        if(attack.current()!=null){navigation.stop();face(attack.direction());long age=now-attack.started();if(attack.current()==RAM&&age>=20&&age<=31){var step=attack.direction();var old=position();if(level() instanceof ServerLevel world)breakObstacles(world,getBoundingBox().move(step));var nextFloor=floor(old.add(step));if(nextFloor==null||Math.abs(nextFloor.getY()-old.y)>.1||!legalLanding(nextFloor)){stop(45);return;}move(MoverType.SELF,step);if(position().subtract(old).horizontalDistance()<.98){stop(45);return;}}
            else if(attack.current()==SLAM&&age>=16&&age<=35){double u=(age-15)/20D;var wanted=attack.origin().lerp(landing(),u).add(0,4*Math.sin(Math.PI*u),0);var old=position();move(MoverType.SELF,wanted.subtract(old));if(position().distanceToSqr(wanted)>.06){stop(45);return;}setDeltaMovement(0,0,0);}
            else setDeltaMovement(0,getDeltaMovement().y,0);if(attack.current()==DRINK&&age>=24&&age<88&&now%2==0)pull();attack.advance(now,this::impact);}
        sync();if(isNoAi()||attack.state(now)!=AttackState.IDLE)return;var target=getTarget();if(arena!=null&&(blockPosition().distSqr(arena)>15*15||target!=null&&target.blockPosition().distSqr(arena)>18*18)){setTarget(null);navigation.moveTo(arena.getX()+.5,arena.getY(),arena.getZ()+.5,.7);return;}if(!enemy(target)){setTarget(null);return;}
        if(now>=nextChoice){nextChoice=now+20;int[] choices=form()==1?new int[]{501,502,503,504}:new int[]{505,506,502,501,503,504};for(int i=0;i<choices.length;i++){int id=choices[(i+Math.floorMod(tickCount/20,choices.length))%choices.length];if(startSkill(id,target))return;}}navigation.moveTo(target,.7);
    }
    public List<CauldronGroundSpell> spells(){return level() instanceof ServerLevel world?world.getEntitiesOfClass(CauldronGroundSpell.class,getBoundingBox().inflate(24),s->s.ownedBy(this)):List.of();}
    private void clearSpells(){for(var s:spells().stream().limit(8).toList())s.discard();}
    public DamageSource crushing(){var key=ResourceKey.create(Registries.DAMAGE_TYPE,new ResourceLocation("dynasty","taoyan_crushing"));return new DamageSource(level().registryAccess().registryOrThrow(Registries.DAMAGE_TYPE).getHolderOrThrow(key),this);}
    private boolean hurtOne(LivingEntity target,float multiplier,boolean crush,double knockback){if(!isAlive()||!enemy(target))return false;if(target.hurt(crush?crushing():damageSources().mobAttack(this),(float)getAttributeValue(Attributes.ATTACK_DAMAGE)*multiplier)){if(crush&&target.isBlocking()){var item=target.getUseItem().getItem();target.stopUsingItem();if(target instanceof Player p)p.getCooldowns().addCooldown(item,60);}if(knockback>0)target.knockback(knockback,getX()-target.getX(),getZ()-target.getZ());if(form()==2&&crush&&(skillId()==501||skillId()==505))target.setSecondsOnFire(3);return true;}return false;}
    private void impact(int frame){if(!(level() instanceof ServerLevel world)||!isAlive()||attack.current()==null)return;var def=attack.current();
        if(def==RAM){for(var e:CombatGeometry.query(world,position(),attack.direction(),CombatGeometry.Shape.STRIP,3.4,4,0,3,this::enemy).stream().limit(16).toList()){if(hitThisAction.size()>=32)return;if(hasLineOfSight(e)&&hitThisAction.add(e.getUUID()))hurtOne(e,RAM.damageMultiplier(),true,RAM.knockback());}return;}
        if(def==WHIP){for(var e:CombatGeometry.query(world,whipOrigin(),whipDirection(frame),CombatGeometry.Shape.STRIP,4.5,.9,0,1,this::enemy).stream().limit(16).toList()){if(hitThisAction.size()>=32)return;if(world.clip(new ClipContext(whipOrigin(),e.getEyePosition(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()==HitResult.Type.MISS&&hitThisAction.add(e.getUUID())){if(hurtOne(e,WHIP.damageMultiplier(),false,WHIP.knockback()))e.addEffect(new MobEffectInstance(CauldronPitContent.BLEED.get(),100));}}return;}
        if(def==OIL){var at=floor(position().add(attack.direction().scale(4)));if(at!=null&&loaded(new AABB(at).inflate(6,1,6))&&spells().size()<8){var spell=CauldronPitContent.OIL_POOL.get().create(world);if(spell!=null){spell.launch(this,Vec3.atBottomCenterOf(at),attack.direction());world.addFreshEntity(spell);}}return;}
        if(def==BELLS){var centre=arena==null?position():Vec3.atBottomCenterOf(arena);if(!loaded(new AABB(centre,centre).inflate(20,4,20)))return;for(var e:CombatGeometry.query(world,centre,attack.direction(),CombatGeometry.Shape.CIRCLE,20,0,360,4,this::enemy).stream().limit(16).toList()){if(!isAlive())return;if(hasLineOfSight(e)){hurtOne(e,BELLS.damageMultiplier(),false,0);if(e instanceof Player p)p.causeFoodExhaustion(1.5F);}}return;}
        if(def==SLAM){for(var e:CombatGeometry.query(world,position(),attack.direction(),CombatGeometry.Shape.CIRCLE,4,0,360,3,this::enemy).stream().limit(16).toList())if(hasLineOfSight(e))hurtOne(e,SLAM.damageMultiplier(),true,SLAM.knockback());for(int i=0;i<6&&spells().size()<8;i++){double a=i*Math.PI/3;var spell=CauldronPitContent.FIRE_CRACK.get().create(world);if(spell!=null){spell.launch(this,position(),new Vec3(Math.cos(a),0,Math.sin(a)));world.addFreshEntity(spell);}}return;}
        for(var e:CombatGeometry.query(world,mouth(),attack.direction(),CombatGeometry.Shape.CIRCLE,1.3,0,360,2,this::enemy).stream().limit(16).toList())if(hasLineOfSight(e))hurtOne(e,DRINK.damageMultiplier(),true,0);
    }
    private void pull(){if(!(level() instanceof ServerLevel world)||!loaded(getBoundingBox().inflate(20,3,20)))return;for(var e:world.getEntitiesOfClass(LivingEntity.class,getBoundingBox().inflate(20,3,20),this::enemy).stream().limit(16).toList()){if(!isAlive()||attack.current()!=DRINK)return;var delta=mouth().subtract(e.position()).multiply(1,0,1);if(delta.lengthSqr()>20*20||delta.lengthSqr()<.2||pillarGrace.getOrDefault(e.getUUID(),-1L)>=level().getGameTime()||!hasLineOfSight(e))continue;var velocity=e.getDeltaMovement().add(delta.normalize().scale(.075));if(velocity.horizontalDistance()>.35)velocity=velocity.multiply(.35/velocity.horizontalDistance(),1,.35/velocity.horizontalDistance());e.setDeltaMovement(velocity);e.hurtMarked=true;}}
    public boolean braceAtPillar(ServerPlayer player,BlockPos hit){if(arena==null||skillId()!=506||phase()!=AttackState.ACTIVE||!enemy(player)||player.distanceToSqr(Vec3.atCenterOf(hit))>6.5*6.5||pillarGrace.getOrDefault(player.getUUID(),-1L)>=level().getGameTime())return false;boolean real=false;for(int i=0;i<12;i++){var base=CauldronPitPiece.pillar(arena,i);if(hit.getX()==base.getX()&&hit.getZ()==base.getZ()&&hit.getY()>=base.getY()&&hit.getY()<=base.getY()+4&&level().getBlockState(hit).is(Blocks.BONE_BLOCK)){real=true;break;}}if(!real||player.getMainHandItem().isEmpty())return false;var away=player.position().subtract(position()).multiply(1,0,1).normalize();player.setDeltaMovement(away.scale(.9).add(0,.2,0));player.hurtMarked=true;if(pillarGrace.size()>=16)pillarGrace.remove(pillarGrace.keySet().iterator().next());pillarGrace.put(player.getUUID(),level().getGameTime()+24);return true;}
    private void breakObstacles(ServerLevel world,AABB box){if(arena==null||!loaded(box)||!ForgeEventFactory.getMobGriefingEvent(world,this))return;int budget=96;for(var p:BlockPos.betweenClosed(BlockPos.containing(box.minX,box.minY,box.minZ),BlockPos.containing(box.maxX,box.maxY,box.maxZ))){if(--budget<0)return;if(p.distSqr(arena)>15*15||world.getBlockEntity(p)!=null)continue;var state=world.getBlockState(p);if((state.is(Blocks.STONE)||state.is(Blocks.CRACKED_STONE_BRICKS)||state.is(Blocks.DIRT)||state.is(Blocks.COBBLESTONE))&&ForgeEventFactory.onEntityDestroyBlock(this,p,state))world.destroyBlock(p,false,this);}}
    @Override public boolean hurt(DamageSource source,float amount){if(!level().isClientSide&&(intro()||transition())&&!source.is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY))return false;float before=getHealth();boolean accepted=super.hurt(source,amount);if(accepted&&!level().isClientSide&&isAlive()&&before-getHealth()>=35&&phase()==AttackState.WINDUP)stop(50);return accepted;}
    @Override public void startSeenByPlayer(ServerPlayer p){super.startSeenByPlayer(p);subscriptions.startSeenByPlayer(p);}
    @Override public void stopSeenByPlayer(ServerPlayer p){super.stopSeenByPlayer(p);subscriptions.stopSeenByPlayer(p);}
    @Override public void remove(RemovalReason reason){subscriptions.clear();if(!level().isClientSide&&isAlive()&&reason.shouldDestroy()){clearSpells();CauldronPits.destroyed(this);}super.remove(reason);}
    @Override public void die(DamageSource source){if(deathStart>=0)return;super.die(source);if(!isDeadOrDying())return;deathStart=level().getGameTime();attack.cancel();clearSpells();hitThisAction.clear();pillarGrace.clear();navigation.stop();setTarget(null);subscriptions.clear();BlueprintVisualEvent.cancel(this);sync();CauldronPits.confirmedDeath(this);BlueprintVisualEvent.death(this);}
    @Override protected void dropAllDeathLoot(DamageSource source){if(!lootDropped){lootDropped=true;super.dropAllDeathLoot(source);}}
    @Override protected void tickDeath(){deathTime++;if(!level().isClientSide){deathTime=(int)Math.min(200,Math.max(deathTime,level().getGameTime()-deathStart));if(deathTime>=200)remove(RemovalReason.KILLED);}}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("TaoyanAttack",attack.save());t.putInt("TaoyanForm",form());t.putLong("TaoyanBorn",born());t.putLong("TaoyanShift",shifted());t.putLong("TaoyanLastCombat",lastCombat);t.putLong("TaoyanDeath",deathStart);t.putLong("TaoyanLanding",entityData.get(LANDING).asLong());t.putBoolean("TaoyanLootDropped",lootDropped);if(arena!=null)t.putLong("TaoyanArena",arena.asLong());var ids=new net.minecraft.nbt.ListTag();for(var id:hitThisAction){var n=new CompoundTag();n.putUUID("Id",id);ids.add(n);}t.put("TaoyanHitIds",ids);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);arena=t.contains("TaoyanArena")?BlockPos.of(t.getLong("TaoyanArena")):null;if(arena!=null&&arena.distSqr(blockPosition())>64*64)arena=null;entityData.set(BOUND,arena!=null);entityData.set(ARENA_DATA,arena==null?BlockPos.ZERO:arena);entityData.set(STAGE,t.getInt("TaoyanForm")==2?2:1);entityData.set(BORN,t.contains("TaoyanBorn")?Math.min(level().getGameTime(),t.getLong("TaoyanBorn")):level().getGameTime());long shift=t.contains("TaoyanShift")?t.getLong("TaoyanShift"):-1L;entityData.set(SHIFT,form()==2&&shift>=0&&shift<=level().getGameTime()?shift:-1L);entityData.set(LANDING,t.contains("TaoyanLanding")?BlockPos.of(t.getLong("TaoyanLanding")):blockPosition());lastCombat=t.contains("TaoyanLastCombat")?t.getLong("TaoyanLastCombat"):-1;deathStart=t.contains("TaoyanDeath")?t.getLong("TaoyanDeath"):-1;lootDropped=t.getBoolean("TaoyanLootDropped");attack.load(t.getCompound("TaoyanAttack"),TaoyanCauldron::skill,level().getGameTime());hitThisAction.clear();for(var row:t.getList("TaoyanHitIds",10)){var n=(CompoundTag)row;if(n.hasUUID("Id")&&hitThisAction.size()<32)hitThisAction.add(n.getUUID("Id"));}pillarGrace.clear();if(landing().distanceToSqr(position())>32*32||t.getCompound("TaoyanAttack").getInt("Skill")!=0&&attack.current()==null){attack.cancel();clearSpells();}if(isDeadOrDying()){attack.cancel();clearSpells();}if(form()==2)getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(.27);sync();}
    public String visualAnimation(){if(isDeadOrDying())return "death";if(intro())return "intro";if(transition())return "transition";return switch(skillId()){case 501->"ram";case 502->"whip";case 503->"oil";case 504->"bells";case 505->"slam";case 506->"drink";default->hurtTime>0?"hurt":getDeltaMovement().horizontalDistanceSqr()>.001?"walk":"idle";};}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<TaoyanCauldron>(this,"body",0,s->{partial=s.getPartialTick();var controller=s.getController();String name=visualAnimation();long stamp=isDeadOrDying()?skillStart():intro()?born():transition()?shifted():skillStart();String key=form()+"/"+name;if(stamp!=animationStamp||!key.equals(animationKey)){animationStamp=stamp;animationKey=key;controller.forceAnimationReset();}controller.setAnimation(name.equals("idle")||name.equals("walk")?RawAnimation.begin().thenLoop("animation."+ID+"."+name):RawAnimation.begin().thenPlayAndHold("animation."+ID+"."+name));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}){
        @Override protected double adjustTick(double tick){boolean reset=shouldResetTick;double local=super.adjustTick(tick);return !reset&&getAnimationState()==AnimationController.State.RUNNING&&animationStamp>=0&&(skillId()!=0||intro()||transition()||isDeadOrDying())?Math.max(0,level().getGameTime()-animationStamp+partial):local;}
    });}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
