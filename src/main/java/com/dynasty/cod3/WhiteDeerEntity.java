package com.dynasty.cod3;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.*;
import net.minecraft.sounds.*;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.EnumSet;

/** Slow, non-rideable quadruped. The herb is part of the head rig, never an item drop. */
public final class WhiteDeerEntity extends PathfinderMob implements GeoEntity {
    public enum Pose {IDLE,WALK,GRAZE,LOOK_BACK,STARTLED}
    private static final EntityDataAccessor<Integer> POSE=SynchedEntityData.defineId(WhiteDeerEntity.class,EntityDataSerializers.INT);
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private BlockPos home;
    private long frightenedUntil;
    private int disturbance;
    public WhiteDeerEntity(EntityType<? extends WhiteDeerEntity> t,Level l){super(t,l);setPersistenceRequired();}
    public static AttributeSupplier.Builder attributes(){return createMobAttributes().add(Attributes.MAX_HEALTH,16).add(Attributes.MOVEMENT_SPEED,.16).add(Attributes.FOLLOW_RANGE,16);}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(POSE,0);}
    public Pose pose(){return Pose.values()[entityData.get(POSE)];}
    public int disturbance(){return disturbance;}
    public boolean frightened(){return level().getGameTime()<frightenedUntil;}
    public void startle(){disturbance++;frightenedUntil=level().getGameTime()+200;getNavigation().stop();}
    @Override public boolean hurt(net.minecraft.world.damagesource.DamageSource source,float amount){if(!level().isClientSide)startle();return super.hurt(source,amount);}
    @Override public InteractionResult mobInteract(Player p,InteractionHand hand){
        if(hand!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;
        if(p instanceof ServerPlayer sp){
            if(WhiteDeerTrail.claimed(sp))WhiteDeerSanctuary.enter(sp);
            else {startle();p.displayClientMessage(Component.translatable("cod3.dynasty.deer.quiet"),true);}
        }
        return InteractionResult.sidedSuccess(level().isClientSide);
    }
    public static boolean morning(ServerLevel l){long day=Math.floorMod(l.getDayTime(),24000);return day<=2000;}
    public static boolean habitat(ServerLevel l,BlockPos p){return l.dimension()==Level.OVERWORLD&&morning(l)&&l.getBiome(p).is(net.minecraft.world.level.biome.Biomes.BAMBOO_JUNGLE)
            &&l.hasChunkAt(p)&&l.canSeeSky(p)&&l.getBlockState(p.below()).is(BlockTags.ANIMALS_SPAWNABLE_ON)&&l.getMaxLocalRawBrightness(p)>8
            &&l.getEntitiesOfClass(WhiteDeerEntity.class,new net.minecraft.world.phys.AABB(p).inflate(48),Entity::isAlive).size()<2;}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(2,new TrailGoal());goalSelector.addGoal(7,new RandomStrollGoal(this,.35,60));goalSelector.addGoal(9,new RandomLookAroundGoal(this));}
    @Override public void tick(){
        super.tick();if(level().isClientSide)return;
        if(home==null)home=blockPosition();
        if(tickCount%10==0){Pose next=frightened()?Pose.STARTLED:!getNavigation().isDone()?Pose.WALK:tickCount%240<40?Pose.LOOK_BACK:tickCount%240<100?Pose.GRAZE:Pose.IDLE;entityData.set(POSE,next.ordinal());}
        if(level() instanceof ServerLevel l&&morning(l)&&tickCount%40==0)l.sendParticles(ParticleTypes.CLOUD,getX(),getY()+.1,getZ(),1,.7,.02,.7,0);
        if(tickCount%160==0)level().playSound(null,blockPosition(),SoundEvents.AMETHYST_BLOCK_CHIME,SoundSource.NEUTRAL,.5f,1.4f);
    }
    private final class TrailGoal extends Goal {
        private Player follower;private int waypoint,wait;
        TrailGoal(){setFlags(EnumSet.of(Flag.MOVE,Flag.LOOK));}
        @Override public boolean requiresUpdateEveryTick(){return true;}
        public boolean canUse(){if(frightened()||level().dimension()!=Level.OVERWORLD)return false;follower=level().getNearestPlayer(WhiteDeerEntity.this,12);return follower!=null&&follower.isShiftKeyDown()&&!follower.isSpectator();}
        public boolean canContinueToUse(){return follower!=null&&follower.isAlive()&&follower.level()==level()&&follower.isShiftKeyDown()&&distanceToSqr(follower)<144&&!frightened();}
        public void start(){wait=0;}
        public void stop(){follower=null;getNavigation().stop();}
        public void tick(){
            if(home==null)return;
            if(!getNavigation().isDone())return;
            if(wait++<40){getLookControl().setLookAt(follower,30,25);return;}
            wait=0;
            // Eight broad waypoints keep the slow trail inside already loaded terrain.
            int[][] ring={{8,0},{8,8},{0,8},{-8,8},{-8,0},{-8,-8},{0,-8},{8,-8}};
            var step=ring[Math.floorMod(waypoint++,ring.length)];var target=home.offset(step[0],0,step[1]);
            if(!level().hasChunkAt(target))return;
            for(int dy=2;dy>=-2;dy--){var at=target.offset(0,dy,0);if(level().getBlockState(at.below()).isSolid()&&level().getBlockState(at).isAir()&&level().getBlockState(at.above()).isAir()){
                // Vanilla travel applies the requested speed to both movement
                // input and acceleration. .35 stalled below the tiny-motion
                // cutoff; .8 still stays comfortably below player sneak speed.
                var path=getNavigation().createPath(at,0);if(path!=null&&path.canReach())getNavigation().moveTo(path,.8);return;
            }}
        }
    }
    @Override public void addAdditionalSaveData(CompoundTag n){super.addAdditionalSaveData(n);if(home!=null)n.putLong("TrailHome",home.asLong());n.putLong("FrightenedUntil",frightenedUntil);n.putInt("Disturbance",disturbance);}
    @Override public void readAdditionalSaveData(CompoundTag n){super.readAdditionalSaveData(n);home=n.contains("TrailHome")?BlockPos.of(n.getLong("TrailHome")):null;frightenedUntil=n.getLong("FrightenedUntil");disturbance=n.getInt("Disturbance");}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar r){r.add(new AnimationController<>(this,"deer",5,e->{e.getController().setAnimation(RawAnimation.begin().thenLoop("animation.white_deer."+pose().name().toLowerCase(java.util.Locale.ROOT)));return PlayState.CONTINUE;}));}
}
