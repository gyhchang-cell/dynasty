package com.dynasty.entity;

import com.dynasty.DynastyItems;
import com.dynasty.DynastyStats;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.FlyingMob;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomFlyingGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.SmallFireball;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * 王朝神兽：麒麟、凤凰、九尾狐。
 * Dynasty mythical beasts: the Qilin, the Phoenix and the Nine-tailed Fox.
 */
public final class DynastyBeasts {

    private DynastyBeasts() {
    }

    /** 麒麟：祥瑞之兽，平常温和，受击则反击；喂食仙桃可获忠诚。 */
    public static class Qilin extends PathfinderMob {

        public Qilin(EntityType<? extends Qilin> type, Level level) {
            super(type, level);
            this.xpReward = 40;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return Mob.createMobAttributes()
                    .add(Attributes.MAX_HEALTH, 1024.0D)
                    .add(Attributes.ATTACK_DAMAGE, 500.0D)
                    .add(Attributes.MOVEMENT_SPEED, 0.34D)
                    .add(Attributes.ARMOR, 20.0D)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.6D)
                    .add(Attributes.FOLLOW_RANGE, 32.0D);
        }

        @Override
        public boolean removeWhenFarAway(double distance) {
            return false;
        }

        @Override
        protected void registerGoals() {
            this.goalSelector.addGoal(0, new FloatGoal(this));
            this.goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.25D, true));
            this.goalSelector.addGoal(6, new RandomStrollGoal(this, 1.0D));
            this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 12.0F));
            this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
            this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
            this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Monster.class, true));
        }

        @Override
        protected InteractionResult mobInteract(Player player, InteractionHand hand) {
            if (!this.level().isClientSide && player instanceof ServerPlayer serverPlayer
                    && player.getItemInHand(hand).is(DynastyItems.IMMORTAL_PEACH.get())) {
                this.heal(20.0F);
                player.getItemInHand(hand).shrink(1);
                DynastyStats.addLoyalty(serverPlayer, 3);
                serverPlayer.sendSystemMessage(Component.literal("§d[麒麟] §r祥瑞降临，民心 +3"));
                com.dynasty.DynastyQuestManager.notifyEvent(serverPlayer, "qilin");
                this.playSound(SoundEvents.HORSE_EAT, 1.0F, 0.8F);
                return InteractionResult.CONSUME;
            }
            return super.mobInteract(player, hand);
        }

        @Override
        protected void customServerAiStep() {
            super.customServerAiStep();
            if (this.level() instanceof ServerLevel serverLevel && this.tickCount % 40 == 0) {
                serverLevel.sendParticles(ParticleTypes.HAPPY_VILLAGER,
                        this.getX(), this.getY() + 1.4D, this.getZ(), 4, 0.4D, 0.4D, 0.4D, 0.0D);
            }
        }
    }

    /** 凤凰：浴火之鸟，飞行并喷射火焰。 */
    public static class Phoenix extends FlyingMob {

        private int fireCooldown = 60;

        public Phoenix(EntityType<? extends Phoenix> type, Level level) {
            super(type, level);
            this.xpReward = 60;
            this.moveControl = new net.minecraft.world.entity.ai.control.FlyingMoveControl(this, 20, true);
            this.navigation = new net.minecraft.world.entity.ai.navigation.FlyingPathNavigation(this, level);
        }

        public static AttributeSupplier.Builder createAttributes() {
            return Mob.createMobAttributes()
                    .add(Attributes.MAX_HEALTH, 1024.0D)
                    .add(Attributes.ATTACK_DAMAGE, 600.0D)
                    .add(Attributes.MOVEMENT_SPEED, 0.32D)
                    .add(Attributes.FLYING_SPEED, 0.32D)
                    .add(Attributes.ARMOR, 20.0D)
                    .add(Attributes.FOLLOW_RANGE, 40.0D);
        }

        @Override
        public boolean fireImmune() {
            return true;
        }

        @Override
        public boolean requiresCustomPersistence() {
            return true;
        }

        @Override
        protected void registerGoals() {
            this.goalSelector.addGoal(2, new FlyingMeleeGoal());
            this.goalSelector.addGoal(5, new FlyingWanderGoal());
            this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 20.0F));
            this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
            this.targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Player.class, true));
        }

        @Override
        public boolean hurt(net.minecraft.world.damagesource.DamageSource source, float amount) {
            if (source.getEntity() instanceof LivingEntity attacker && attacker != this) {
                this.setTarget(attacker);
            }
            return super.hurt(source, amount);
        }

        /** 空中游荡 / casual flying wander */
        private class FlyingWanderGoal extends net.minecraft.world.entity.ai.goal.Goal {

            private int cooldown;

            @Override
            public boolean canUse() {
                return Phoenix.this.getTarget() == null && --this.cooldown <= 0;
            }

            @Override
            public void start() {
                this.cooldown = 80 + Phoenix.this.getRandom().nextInt(80);
                double dx = Phoenix.this.getX() + (Phoenix.this.getRandom().nextDouble() - 0.5D) * 24.0D;
                double dy = Phoenix.this.getY() + (Phoenix.this.getRandom().nextDouble() - 0.5D) * 10.0D;
                double dz = Phoenix.this.getZ() + (Phoenix.this.getRandom().nextDouble() - 0.5D) * 24.0D;
                Phoenix.this.getNavigation().moveTo(dx, dy, dz, 1.0D);
            }
        }

        /** 飞行近战目标（FlyingMob 无法使用 MeleeAttackGoal）/ flying melee goal */
        private class FlyingMeleeGoal extends net.minecraft.world.entity.ai.goal.Goal {

            FlyingMeleeGoal() {
                this.setFlags(java.util.EnumSet.of(net.minecraft.world.entity.ai.goal.Goal.Flag.MOVE,
                        net.minecraft.world.entity.ai.goal.Goal.Flag.LOOK));
            }

            @Override
            public boolean canUse() {
                LivingEntity target = Phoenix.this.getTarget();
                return target != null && target.isAlive();
            }

            @Override
            public boolean canContinueToUse() {
                return canUse();
            }

            @Override
            public void tick() {
                LivingEntity target = Phoenix.this.getTarget();
                if (target == null) {
                    return;
                }
                Phoenix.this.getLookControl().setLookAt(target, 30.0F, 30.0F);
                Phoenix.this.getNavigation().moveTo(target, 1.4D);
                if (Phoenix.this.distanceToSqr(target) < 6.0D) {
                    Phoenix.this.doHurtTarget(target);
                }
            }
        }

        @Override
        protected void customServerAiStep() {
            super.customServerAiStep();
            LivingEntity target = this.getTarget();
            if (target != null && --this.fireCooldown <= 0) {
                this.fireCooldown = 70;
                Vec3 dir = new Vec3(target.getX() - this.getX(), target.getEyeY() - this.getEyeY(),
                        target.getZ() - this.getZ()).normalize();
                SmallFireball fireball = new SmallFireball(this.level(), this,
                        dir.x * 1.4D, dir.y * 1.4D, dir.z * 1.4D);
                fireball.moveTo(this.getX(), this.getEyeY() - 0.4D, this.getZ(), 0.0F, 0.0F);
                this.level().addFreshEntity(fireball);
                this.playSound(SoundEvents.BLAZE_SHOOT, 1.5F, 1.3F);
            }
        }
    }

    /** 九尾狐：幻术妖狐，受击会瞬移，攻击附带缓慢。 */
    public static class NineTailedFox extends PathfinderMob {

        public NineTailedFox(EntityType<? extends NineTailedFox> type, Level level) {
            super(type, level);
            this.xpReward = 45;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return Mob.createMobAttributes()
                    .add(Attributes.MAX_HEALTH, 1024.0D)
                    .add(Attributes.ATTACK_DAMAGE, 650.0D)
                    .add(Attributes.MOVEMENT_SPEED, 0.40D)
                    .add(Attributes.ARMOR, 20.0D)
                    .add(Attributes.FOLLOW_RANGE, 40.0D);
        }

        @Override
        public boolean requiresCustomPersistence() {
            return true;
        }

        @Override
        protected void registerGoals() {
            this.goalSelector.addGoal(0, new FloatGoal(this));
            this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.5D, true));
            this.goalSelector.addGoal(6, new RandomStrollGoal(this, 1.1D));
            this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 16.0F));
            this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
            this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
            this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        }

        @Override
        public boolean doHurtTarget(Entity target) {
            boolean hit = super.doHurtTarget(target);
            if (hit && target instanceof LivingEntity living) {
                living.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 1));
            }
            return hit;
        }

        @Override
        public boolean hurt(net.minecraft.world.damagesource.DamageSource source, float amount) {
            boolean hurt = super.hurt(source, amount);
            if (hurt && !this.level().isClientSide && this.getRandom().nextInt(3) == 0) {
                // 幻术瞬移 / illusionary teleport
                for (int i = 0; i < 16; i++) {
                    double dx = this.getX() + (this.getRandom().nextDouble() - 0.5D) * 16.0D;
                    double dz = this.getZ() + (this.getRandom().nextDouble() - 0.5D) * 16.0D;
                    double dy = this.getY() + (this.getRandom().nextDouble() - 0.5D) * 8.0D;
                    if (this.randomTeleport(dx, dy, dz, true)) {
                        this.playSound(SoundEvents.ENDERMAN_TELEPORT, 1.0F, 1.4F);
                        break;
                    }
                }
            }
            return hurt;
        }
    }
}
