package com.dynasty.entity;

import com.dynasty.DynastyStats;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
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
import net.minecraft.world.entity.ai.goal.RangedBowAttackGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.monster.RangedAttackMob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;

/**
 * 王朝普通生物集合：大臣、刺客、弓兵、锦衣卫、叛军、年兽。
 * Dynasty standard mobs: Minister, Assassin, Archer, Royal Guard, Rebel Soldier and the Nian Beast.
 */
public final class DynastyMobs {

    private DynastyMobs() {
    }

    /** 大臣：友方文官，右键可获得朝堂建议并提升忠诚。 */
    public static class Minister extends PathfinderMob {

        private static final String[] ADVICE = {
                "天下之大，黎民为贵；广施仁政，方可长治久安。",
                "府库须充实，玉矿与朱砂不可不采。",
                "科举取士，国之根本；可考校才学以授官阶。",
                "边境须置禁军，虎符调兵，方能御敌于外。",
                "丹药可延年，然不可妄服；天命自在人心。",
                "若民怨沸腾，叛军将起；宜先抚民而后用兵。",
        };

        public Minister(EntityType<? extends Minister> type, Level level) {
            super(type, level);
        }

        public static AttributeSupplier.Builder createAttributes() {
            return Mob.createMobAttributes()
                    .add(Attributes.MAX_HEALTH, 1024.0D)
                    .add(Attributes.MOVEMENT_SPEED, 0.28D)
                    .add(Attributes.FOLLOW_RANGE, 24.0D);
        }

        @Override
        public boolean removeWhenFarAway(double distance) {
            return false;
        }

        @Override
        protected void registerGoals() {
            this.goalSelector.addGoal(0, new FloatGoal(this));
            this.goalSelector.addGoal(5, new RandomStrollGoal(this, 0.8D));
            this.goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 10.0F));
            this.goalSelector.addGoal(7, new RandomLookAroundGoal(this));
            this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        }

        @Override
        protected InteractionResult mobInteract(Player player, InteractionHand hand) {
            if (!this.level().isClientSide && player instanceof ServerPlayer serverPlayer) {
                serverPlayer.sendSystemMessage(Component.literal("§6[大臣] §r"
                        + ADVICE[this.getRandom().nextInt(ADVICE.length)]));
                DynastyStats.addLoyalty(serverPlayer, 2);
                serverPlayer.addEffect(new MobEffectInstance(MobEffects.ABSORPTION, 20 * 60, 0));
                com.dynasty.DynastyQuestManager.notifyEvent(serverPlayer, "minister");
                this.playSound(SoundEvents.VILLAGER_YES, 1.0F, 1.0F);
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }
    }

    /** 刺客：高速隐身杀手。 */
    public static class Assassin extends DynastyHumanoidMob {

        public Assassin(EntityType<? extends Assassin> type, Level level) {
            super(type, level);
            this.xpReward = 12;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return stats(1024.0D, 900.0D, 0.36D, 20.0D, 40.0D);
        }

        @Override
        protected void registerGoals() {
            this.goalSelector.addGoal(0, new FloatGoal(this));
            this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.4D, true));
            this.goalSelector.addGoal(7, new RandomStrollGoal(this, 1.0D));
            this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 12.0F));
            this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
            this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
            this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        }

        @Override
        protected void customServerAiStep() {
            super.customServerAiStep();
            if (this.getTarget() == null && this.tickCount % 100 == 0) {
                this.addEffect(new MobEffectInstance(MobEffects.INVISIBILITY, 120, 0, false, false));
            }
            if (this.getTarget() != null) {
                this.removeEffect(MobEffects.INVISIBILITY);
            }
        }

        @Override
        public boolean doHurtTarget(net.minecraft.world.entity.Entity target) {
            boolean hit = super.doHurtTarget(target);
            if (hit && target instanceof LivingEntity living) {
                living.addEffect(new MobEffectInstance(MobEffects.POISON, 80, 0));
            }
            return hit;
        }
    }

    /** 弓兵：远程齐射的帝国射手。 */
    public static class Archer extends DynastyHumanoidMob implements RangedAttackMob {

        public Archer(EntityType<? extends Archer> type, Level level) {
            super(type, level);
            this.xpReward = 10;
            this.setItemSlot(net.minecraft.world.entity.EquipmentSlot.MAINHAND, new ItemStack(Items.BOW));
        }

        public static AttributeSupplier.Builder createAttributes() {
            return stats(1024.0D, 300.0D, 0.28D, 20.0D, 32.0D);
        }

        @Override
        protected void registerGoals() {
            this.goalSelector.addGoal(0, new FloatGoal(this));
            this.goalSelector.addGoal(2, new RangedBowAttackGoal<>(this, 1.0D, 20, 16.0F));
            this.goalSelector.addGoal(7, new RandomStrollGoal(this, 0.9D));
            this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 12.0F));
            this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
            this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
            this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        }

        @Override
        public void performRangedAttack(LivingEntity target, float velocity) {
            Arrow arrow = new Arrow(this.level(), this);
            double dx = target.getX() - this.getX();
            double dy = target.getEyeY() - 0.2D - arrow.getY();
            double dz = target.getZ() - this.getZ();
            double horizontal = Math.sqrt(dx * dx + dz * dz);
            arrow.shoot(dx, dy + horizontal * 0.2D, dz, 1.6F, 8.0F);
            arrow.setBaseDamage(4.0D);
            this.playSound(SoundEvents.SKELETON_SHOOT, 1.0F, 1.0F / (this.getRandom().nextFloat() * 0.4F + 0.8F));
            this.level().addFreshEntity(arrow);
        }
    }

    /** 锦衣卫：重甲近卫，血量与击退抗性极高。 */
    public static class RoyalGuard extends DynastyHumanoidMob {

        public RoyalGuard(EntityType<? extends RoyalGuard> type, Level level) {
            super(type, level);
            this.xpReward = 20;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return Monster.createMonsterAttributes()
                    .add(Attributes.MAX_HEALTH, 1024.0D)
                    .add(Attributes.ATTACK_DAMAGE, 600.0D)
                    .add(Attributes.MOVEMENT_SPEED, 0.30D)
                    .add(Attributes.ARMOR, 20.0D)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.85D)
                    .add(Attributes.FOLLOW_RANGE, 32.0D);
        }

        @Override
        protected void registerGoals() {
            this.goalSelector.addGoal(0, new FloatGoal(this));
            this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.25D, true));
            this.goalSelector.addGoal(7, new RandomStrollGoal(this, 0.85D));
            this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 12.0F));
            this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
            this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
            this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        }
    }

    /** 叛军：民怨沸腾时揭竿而起的起义军。 */
    public static class RebelSoldier extends DynastyHumanoidMob {

        public RebelSoldier(EntityType<? extends RebelSoldier> type, Level level) {
            super(type, level);
            this.setRebel(true);
            this.xpReward = 14;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return stats(1024.0D, 400.0D, 0.30D, 20.0D, 40.0D);
        }

        @Override
        protected void registerGoals() {
            this.goalSelector.addGoal(0, new FloatGoal(this));
            this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.2D, true));
            this.goalSelector.addGoal(7, new RandomStrollGoal(this, 0.9D));
            this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 12.0F));
            this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
            this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
            this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
            this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, ImperialSoldier.class, true));
        }
    }

    /** 年兽：春节出现的凶兽，惧怕爆竹（爆炸伤害加倍）。 */
    public static class NianBeast extends DynastyHumanoidMob {

        public NianBeast(EntityType<? extends NianBeast> type, Level level) {
            super(type, level);
            this.xpReward = 80;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return Monster.createMonsterAttributes()
                    .add(Attributes.MAX_HEALTH, 1024.0D)
                    .add(Attributes.ATTACK_DAMAGE, 700.0D)
                    .add(Attributes.MOVEMENT_SPEED, 0.30D)
                    .add(Attributes.ARMOR, 20.0D)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.9D)
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
            this.goalSelector.addGoal(0, new FloatGoal(this));
            this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.15D, true));
            this.goalSelector.addGoal(7, new RandomStrollGoal(this, 0.9D));
            this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 16.0F));
            this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
            this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
            this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        }

        @Override
        public boolean hurt(net.minecraft.world.damagesource.DamageSource source, float amount) {
            if (source.is(net.minecraft.tags.DamageTypeTags.IS_EXPLOSION)) {
                // 爆竹驱兽 / firecrackers scare the beast away
                amount *= 2.0F;
                this.playSound(SoundEvents.FIREWORK_ROCKET_BLAST, 2.0F, 0.6F);
            }
            return super.hurt(source, amount);
        }
    }
}
