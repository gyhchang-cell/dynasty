package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.monster.AbstractIllager;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.ForgeEventFactory;
import net.minecraftforge.event.entity.EntityTeleportEvent;

import javax.annotation.Nullable;

public class FakeMagispellerEntity extends AbstractIllager {
    private Mob owner;
    private int waitTimeFaker;

    public FakeMagispellerEntity(EntityType<? extends AbstractIllager> p_i48556_1_, Level p_i48556_2_) {
        super(p_i48556_1_, p_i48556_2_);
        this.xpReward = 0;
    }

    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(2, new Raider.HoldGroundAttackGoal(this, 10.0F));
        this.goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.0, false));
        this.goalSelector.addGoal(8, new RandomStrollGoal(this, 0.6));
        this.goalSelector.addGoal(9, new LookAtPlayerGoal(this, Player.class, 15.0F, 1.0F));
        this.goalSelector.addGoal(10, new LookAtPlayerGoal(this, Mob.class, 15.0F));
        this.targetSelector.addGoal(1, (new HurtByTargetGoal(this, Raider.class)).setAlertOthers());
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
    }

    public boolean canBeAffected(MobEffectInstance p_21197_) {
        return false;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.3499999940395355).add(Attributes.MAX_HEALTH, 250.0).add(Attributes.ATTACK_DAMAGE, 5.0).add(Attributes.FOLLOW_RANGE, 32.0);
    }

    protected void customServerAiStep() {
        super.customServerAiStep();
        Entity entity = this.getTarget();
        if (this.random.nextInt(10) == 0 && entity != null && this.distanceToSqr(entity) > 1024.0) {
            this.teleportTowards(entity);
        }

    }

    public boolean causeFallDamage(float p_225503_1_, float p_225503_2_, DamageSource p_147189_) {
        return false;
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
    }

    public void applyRaidBuffs(int p_213660_1_, boolean p_213660_2_) {
    }

    protected float getStandingEyeHeight(Pose p_213348_1_, EntityDimensions p_213348_2_) {
        return 1.66F;
    }

    public void tick() {
        if (this.hurtTime == 10) {
            this.kill();
        }

        if (this.getOwner() != null) {
            this.setTarget(this.getOwner().getTarget());
        }

        ++this.waitTimeFaker;
        super.tick();
    }

    public void die(DamageSource p_70645_1_) {
        this.deathTime = 19;
        super.die(p_70645_1_);
    }

    public boolean doHurtTarget(Entity p_70652_1_) {
        if (!this.level().isClientSide && this.random.nextInt(3) != 0) {
            this.teleportTowards(p_70652_1_);
        }

        return this.waitTimeFaker >= 20 && super.doHurtTarget(p_70652_1_);
    }

    @Nullable
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor p_213386_1_, DifficultyInstance p_213386_2_, MobSpawnType p_213386_3_, @Nullable SpawnGroupData p_213386_4_, @Nullable CompoundTag p_213386_5_) {
        RandomSource randomsource = p_213386_1_.getRandom();
        this.populateDefaultEquipmentSlots(randomsource, p_213386_2_);
        this.populateDefaultEquipmentEnchantments(randomsource, p_213386_2_);
        return super.finalizeSpawn(p_213386_1_, p_213386_2_, p_213386_3_, p_213386_4_, p_213386_5_);
    }

    public boolean canJoinRaid() {
        return false;
    }

    public SoundEvent getCelebrateSound() {
        return IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_CELEBRATE.get();
    }

    protected SoundEvent getAmbientSound() {
        return IllageAndSpillageSoundEvents.ENTITY_FAKER_AMBIENT.get();
    }

    protected SoundEvent getHurtSound(DamageSource p_184601_1_) {
        return IllageAndSpillageSoundEvents.ENTITY_FAKER_DEATH.get();
    }

    protected SoundEvent getDeathSound() {
        return IllageAndSpillageSoundEvents.ENTITY_FAKER_DEATH.get();
    }

    protected void populateDefaultEquipmentSlots(RandomSource random, DifficultyInstance p_34286_) {
        this.setItemSlot(EquipmentSlot.MAINHAND, new ItemStack(Items.IRON_AXE));
        this.setDropChance(EquipmentSlot.MAINHAND, 0.0F);
        this.setItemSlot(EquipmentSlot.OFFHAND, new ItemStack(Items.CROSSBOW));
        this.setDropChance(EquipmentSlot.OFFHAND, 0.0F);
    }

    public void tryToTeleportToEntity(@Nullable Entity entity) {
        if (entity != null) {
            for (int i = 0; i < 64; ++i) {
                if (!this.level().isClientSide && this.teleportTowards(entity)) {
                    break;
                }
            }
        }

    }

    private boolean teleportTowards(Entity p_70816_1_) {
        Vec3 vector3d = new Vec3(this.getX() - p_70816_1_.getX(), this.getY(0.5) - p_70816_1_.getEyeY(), this.getZ() - p_70816_1_.getZ());
        vector3d = vector3d.normalize();
        double d1 = this.getX() + (this.random.nextDouble() - 0.5) * 8.0 - vector3d.x * 16.0;
        double d2 = this.getY() + (double) (this.random.nextInt(16) - 8) - vector3d.y * 16.0;
        double d3 = this.getZ() + (this.random.nextDouble() - 0.5) * 8.0 - vector3d.z * 16.0;
        return this.teleport(d1, d2, d3);
    }

    private boolean teleport(double p_70825_1_, double p_70825_3_, double p_70825_5_) {
        BlockPos.MutableBlockPos blockpos$mutable = new BlockPos.MutableBlockPos(p_70825_1_, p_70825_3_, p_70825_5_);

        while (blockpos$mutable.getY() > 0 && !this.level().getBlockState(blockpos$mutable).blocksMotion()) {
            blockpos$mutable.move(Direction.DOWN);
        }

        BlockState blockstate = this.level().getBlockState(blockpos$mutable);
        boolean flag = blockstate.blocksMotion();
        boolean flag1 = blockstate.getFluidState().is(FluidTags.WATER);
        if (flag && !flag1) {
            EntityTeleportEvent.EnderEntity event = ForgeEventFactory.onEnderTeleport(this, p_70825_1_, p_70825_3_, p_70825_5_);
            if (event.isCanceled()) {
                return false;
            } else {
                boolean flag2 = this.randomTeleport(event.getTargetX(), event.getTargetY(), event.getTargetZ(), true);
                if (flag2 && !this.isSilent()) {
                    this.level().playSound(null, this.xo, this.yo, this.zo, SoundEvents.ENDERMAN_TELEPORT, this.getSoundSource(), 1.0F, 1.0F);
                    this.playSound(SoundEvents.ENDERMAN_TELEPORT, 1.0F, 1.0F);
                }

                return flag2;
            }
        } else {
            return false;
        }
    }

    public Mob getOwner() {
        return this.owner;
    }

    public void setOwner(Mob owner) {
        this.owner = owner;
    }
}
