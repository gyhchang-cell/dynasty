package com.yellowbrossproductions.illageandspillage.entities.projectile;

import com.yellowbrossproductions.illageandspillage.init.ModEntityTypes;
import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.packet.ParticlePacket;
import com.yellowbrossproductions.illageandspillage.util.EffectRegisterer;
import com.yellowbrossproductions.illageandspillage.util.ItemRegisterer;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.AbstractHurtingProjectile;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.PacketDistributor;

import java.util.Iterator;

public class BoneEntity extends AbstractHurtingProjectile {
    public boolean isGoopy;

    public BoneEntity(EntityType<? extends AbstractHurtingProjectile> p_36833_, Level p_36834_) {
        super(p_36833_, p_36834_);
    }

    public BoneEntity(Level p_181151_, LivingEntity p_181152_, double p_181153_, double p_181154_, double p_181155_) {
        super(ModEntityTypes.Bone.get(), p_181152_, p_181153_, p_181154_, p_181155_, p_181151_);
        this.setOwner(p_181152_);
    }

    @Override
    public void tick() {
        this.setInvulnerable(true);

        if (this.isGoopy) {
            this.makeMutationParticles();
        }

        if (this.tickCount >= 100) {
            if (!this.level().isClientSide) {
                this.discard();
            }
        }

        super.tick();
    }

    @Override
    protected ParticleOptions getTrailParticle() {
        return new ItemParticleOption(ParticleTypes.ITEM, ItemRegisterer.GREENBONE.get().getDefaultInstance());
    }

    @Override
    protected boolean shouldBurn() {
        return false;
    }

    @Override
    protected void onHitEntity(EntityHitResult p_37386_) {
        super.onHitEntity(p_37386_);
        if (!this.level().isClientSide) {
            Entity entity = p_37386_.getEntity();
            Entity entity1 = this.getOwner();
            entity.invulnerableTime = 0;
            if (entity.hurt(this.damageSources().thrown(this, entity1), 6.0F) && entity instanceof LivingEntity && this.isGoopy) {
                ((LivingEntity) entity).addEffect(new MobEffectInstance(EffectRegisterer.MUTATION.get(), 100, 1));
            }
            if (entity1 instanceof LivingEntity) {
                this.doEnchantDamageEffects((LivingEntity) entity1, entity);
            }

            this.explode();
        }
    }

    protected void onHit(HitResult p_37406_) {
        super.onHit(p_37406_);
        if (!(p_37406_ instanceof EntityHitResult)) {
            this.explode();
        }
    }

    public void makeMutationParticles() {
        if (!this.level().isClientSide) {
            Iterator<ServerPlayer> var1 = ((ServerLevel) this.level()).players().iterator();

            while (true) {
                ServerPlayer serverPlayer;
                do {
                    if (!var1.hasNext()) {
                        return;
                    }

                    serverPlayer = var1.next();
                } while (!(serverPlayer.distanceToSqr(this) < 4096.0));

                ParticlePacket packet = new ParticlePacket();

                packet.queueParticle(ParticleTypes.ENTITY_EFFECT, false, this.getRandomX(1.0), this.getY(), this.getRandomZ(1.0), 0.208, 0.102, 0.153);

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeExplodeParticles() {
        if (!this.level().isClientSide) {
            for (ServerPlayer serverPlayer : ((ServerLevel) this.level()).players()) {
                if (serverPlayer.distanceToSqr(this) < 4096.0D) {
                    ParticlePacket packet = new ParticlePacket();

                    for (int i = 0; i < 40; ++i) {
                        double d0 = (-0.5 + this.random.nextGaussian());
                        double d1 = (-0.5 + this.random.nextGaussian());
                        double d2 = (-0.5 + this.random.nextGaussian());
                        packet.queueParticle(new ItemParticleOption(ParticleTypes.ITEM, ItemRegisterer.GREENBONE.get().getDefaultInstance()), false, new Vec3(this.getRandomX(1.0D), this.getRandomY(), this.getRandomZ(1.0D)), new Vec3(d0, d1, d2));
                    }

                    packet.queueParticle(ParticleTypes.EXPLOSION, false, new Vec3(this.getBoundingBox().getCenter().x, this.getBoundingBox().getCenter().y, this.getBoundingBox().getCenter().z), new Vec3(0, 0, 0));

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

    @Override
    public boolean hurt(DamageSource source, float amount) {
        return source.is(DamageTypes.GENERIC_KILL) && super.hurt(source, amount);
    }

    private void explode() {
        this.makeExplodeParticles();
        this.playSound(SoundEvents.PLAYER_ATTACK_CRIT, 2.0F, 1.0F);

        if (!this.level().isClientSide) {
            this.discard();
        }
    }
}
