package com.uavwaffle.creaturesofpetrichor.entity.custom;

import com.uavwaffle.creaturesofpetrichor.entity.custom.goal.PetrichorMeleeAttackGoal;
import com.uavwaffle.creaturesofpetrichor.entity.custom.type.PetrichorAttackingEntity;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.NotNull;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.Animation;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

public class DirewolfEntity extends PetrichorAttackingEntity {

    public static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.direwolf.idle");
    public static final RawAnimation WALK = RawAnimation.begin().thenLoop("animation.direwolf.walk");
    public static final RawAnimation ATTACK_ANIMATION = RawAnimation.begin().then("animation.direwolf.attack", Animation.LoopType.PLAY_ONCE);


    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);
    public DirewolfEntity(EntityType<? extends Monster> pEntityType, Level pLevel) {
        super(pEntityType, pLevel, ATTACK_ANIMATION, 13);
        this.setMaxUpStep(1.0F);
    }

    public static AttributeSupplier.Builder createAttributes(){
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 14.0D)
                .add(Attributes.ATTACK_DAMAGE, 4.0f)
                .add(Attributes.MOVEMENT_SPEED, 0.4f)
                .add(Attributes.FOLLOW_RANGE, 30.0D);
    }

    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(7, new WaterAvoidingRandomStrollGoal(this, 1.0D));
        this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 30.0F));
        this.goalSelector.addGoal(8, new RandomLookAroundGoal(this));
        this.addBehaviourGoals();
    }
    protected void addBehaviourGoals() {
        this.goalSelector.addGoal(4, new PetrichorMeleeAttackGoal(this, 1.08d, true));
        this.goalSelector.addGoal(3, new LeapAtTargetGoal(this, 0.4F));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }



        @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {


        controllers.add(new AnimationController<>(this, "Walk/Idle", 5, state -> state.setAndContinue(state.isMoving() ? WALK : IDLE)));
        controllers.add(new AnimationController<>(this, "AttackController", state -> PlayState.STOP).triggerableAnim("Attack", ATTACK_ANIMATION));

    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }

    @Override
    protected float getStandingEyeHeight(@NotNull Pose pPose, @NotNull EntityDimensions pSize) {
        return 1.3f;
    }

    /* SOUNDS */
    @Override
    protected SoundEvent getAmbientSound() {
        return SoundEvents.WOLF_GROWL;
    }
    @Override
    protected @NotNull SoundEvent getHurtSound(@NotNull DamageSource pDamageSource) {
        return SoundEvents.WOLF_HURT;
    }
    @Override
    protected @NotNull SoundEvent getDeathSound() {
        return SoundEvents.WOLF_DEATH;
    }
}
