package com.yellowbrossproductions.illageandspillage.entities.projectile;

import com.yellowbrossproductions.illageandspillage.init.ModEntityTypes;
import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.packet.ParticlePacket;
import com.yellowbrossproductions.illageandspillage.util.EntityUtil;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.projectile.AbstractHurtingProjectile;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.PacketDistributor;

import java.util.List;

public class AxeEntity extends AbstractHurtingProjectile {
    public Mob shooter = null;
    private boolean canExplode = false;

    public AxeEntity(EntityType<? extends AbstractHurtingProjectile> p_36833_, Level p_36834_) {
        super(p_36833_, p_36834_);
    }

    public AxeEntity(Level p_181151_, LivingEntity p_181152_, double p_181153_, double p_181154_, double p_181155_) {
        super(ModEntityTypes.Axe.get(), p_181152_, p_181153_, p_181154_, p_181155_, p_181151_);
        this.setOwner(p_181152_);
    }

    @Override
    public void tick() {


        this.setInvulnerable(true);

        if (this.canExplode) {
            this.explode(1.0D);
            if (!this.level().isClientSide) {
                this.discard();
            }
        }

        this.makeParticles();

        if (this.tickCount >= 100) {
            if (!this.level().isClientSide) {
                this.discard();
            }
        }

        super.tick();
        this.setYRot(this.getYHeadRot());
        this.setYHeadRot(this.getYRot());
    }

    @Override
    protected boolean shouldBurn() {
        return false;
    }

    @Override
    protected void onHitEntity(EntityHitResult p_37259_) {
        super.onHitEntity(p_37259_);
        Entity attacker = this.shooter != null ? this.shooter : this;
        boolean canHurt = attacker == this || EntityUtil.canHurtThisMob(p_37259_.getEntity(), this.shooter);
        if (canHurt) {
            this.canExplode = true;
        }
    }

    protected void onHit(HitResult p_37406_) {
        super.onHit(p_37406_);
        if (!(p_37406_ instanceof EntityHitResult)) {
            this.canExplode = true;
        }
    }

    public void makeParticles() {
        if (!this.level().isClientSide) {
            for (ServerPlayer serverPlayer : ((ServerLevel) this.level()).players()) {
                if (serverPlayer.distanceToSqr(this) < 4096.0D) {
                    ParticlePacket packet = new ParticlePacket();

                    for (int i = 0; i < 1; ++i) {
                        double d0 = (-0.5 + this.random.nextGaussian());
                        double d1 = (-0.5 + this.random.nextGaussian());
                        double d2 = (-0.5 + this.random.nextGaussian());
                        packet.queueParticle(ParticleTypes.CRIT, false, new Vec3(this.getRandomX(1.0D), this.getRandomY(), this.getRandomZ(1.0D)), new Vec3(d0, d1, d2));
                    }

                    PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> serverPlayer), packet);
                }
            }
        }
    }

    public void makeExplodeParticles() {
        if (!this.level().isClientSide) {
            for (ServerPlayer serverPlayer : ((ServerLevel) this.level()).players()) {
                if (serverPlayer.distanceToSqr(this) < 4096.0D) {
                    ParticlePacket packet = new ParticlePacket();

                    for (int i = 0; i < 10; ++i) {
                        double d0 = (-0.5 + this.random.nextGaussian());
                        double d1 = (-0.5 + this.random.nextGaussian());
                        double d2 = (-0.5 + this.random.nextGaussian());
                        packet.queueParticle(ParticleTypes.POOF, false, new Vec3(this.getRandomX(1.0D), this.getRandomY(), this.getRandomZ(1.0D)), new Vec3(d0, d1, d2));
                    }
                    for (int i = 0; i < 20; ++i) {
                        double d0 = (-0.5 + this.random.nextGaussian());
                        double d1 = (-0.5 + this.random.nextGaussian());
                        double d2 = (-0.5 + this.random.nextGaussian());
                        packet.queueParticle(ParticleTypes.CRIT, false, new Vec3(this.getRandomX(1.0D), this.getRandomY(), this.getRandomZ(1.0D)), new Vec3(d0, d1, d2));
                    }
                    for (int i = 0; i < 6; ++i) {
                        double d0 = (-0.5 + this.random.nextGaussian());
                        double d1 = (-0.5 + this.random.nextGaussian());
                        double d2 = (-0.5 + this.random.nextGaussian());
                        packet.queueParticle(ParticleTypes.EXPLOSION, false, new Vec3(this.getRandomX(1.0D), this.getRandomY(), this.getRandomZ(1.0D)), new Vec3(d0, d1, d2));
                    }

                    PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> serverPlayer), packet);
                }
            }
        }
    }

    @Override
    public boolean isPickable() {
        return false;
    }

    @Override
    public boolean isAttackable() {
        return false;
    }

    public void setShooter(Mob shooter) {
        this.shooter = shooter;
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        return source.is(DamageTypes.GENERIC_KILL) && super.hurt(source, amount);
    }

    private void explode(double size) {
        List<Entity> list = this.level().getEntities(this, new AABB(this.getX() - size, this.getY() - size, this.getZ() - size, this.getX() + size, this.getY() + size, this.getZ() + size), Entity::isAlive);

        Entity attacker = this.shooter != null ? this.shooter : this;
        this.makeExplodeParticles();
        this.playSound(SoundEvents.PLAYER_ATTACK_CRIT, 2.0F, 1.0F);
        for (Entity entity : list) {
            if (entity instanceof LivingEntity living && entity != attacker) {
                if (entity.isAlive() && !entity.isInvulnerable() && !entity.isSpectator()) {
                    living.hurt(damageSources().thrown(living, attacker), 8.0F);
                    living.invulnerableTime = 0;
                    EntityUtil.disableShield(living, 200);
                }
            }
        }
    }
}
