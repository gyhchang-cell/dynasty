package com.yellowbrossproductions.illageandspillage.entities.projectile;

import com.yellowbrossproductions.illageandspillage.entities.MagispellerEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.LargeFireball;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraft.world.level.gameevent.GameEvent.Context;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.HitResult.Type;

public class MagiFireballEntity extends LargeFireball {
    private LivingEntity magispeller;

    public MagiFireballEntity(EntityType<? extends LargeFireball> p_37199_, Level p_37200_) {
        super(p_37199_, p_37200_);
    }

    public MagiFireballEntity(EntityType<? extends LargeFireball> p_36817_, double p_36818_, double p_36819_, double p_36820_, double p_36821_, double p_36822_, double p_36823_, Level p_36824_) {
        super(p_36817_, p_36824_);
        this.moveTo(p_36818_, p_36819_, p_36820_, this.getYRot(), this.getXRot());
        this.reapplyPosition();
        double d0 = Math.sqrt(p_36821_ * p_36821_ + p_36822_ * p_36822_ + p_36823_ * p_36823_);
        if (d0 != 0.0) {
            this.xPower = p_36821_ / d0 * 0.1;
            this.yPower = p_36822_ / d0 * 0.1;
            this.zPower = p_36823_ / d0 * 0.1;
        }

    }

    public void tick() {
        if (this.tickCount > 100) {
            this.discard();
        }

        super.tick();
    }

    protected boolean shouldBurn() {
        return false;
    }

    protected void onHit_custom(HitResult p_37260_) {
        HitResult.Type hitresult$type = p_37260_.getType();
        if (hitresult$type == Type.ENTITY) {
            this.onHitEntity((EntityHitResult) p_37260_);
            this.level().gameEvent(GameEvent.PROJECTILE_LAND, p_37260_.getLocation(), Context.of(this, null));
        } else if (hitresult$type == Type.BLOCK) {
            BlockHitResult blockhitresult = (BlockHitResult) p_37260_;
            this.onHitBlock(blockhitresult);
            BlockPos blockpos = blockhitresult.getBlockPos();
            this.level().gameEvent(GameEvent.PROJECTILE_LAND, blockpos, Context.of(this, this.level().getBlockState(blockpos)));
        }

    }

    protected void onHit(HitResult p_37218_) {
        this.onHit_custom(p_37218_);
        if (!this.level().isClientSide) {
            this.level().explode(this.magispeller, this.getX(), this.getY(), this.getZ(), 3.0F, Level.ExplosionInteraction.NONE);
            this.discard();
        }

    }

    public boolean hurt(DamageSource p_36839_, float p_36840_) {
        return (this.tickCount >= 35 || p_36839_.getEntity() instanceof MagispellerEntity) && super.hurt(p_36839_, p_36840_);
    }

    public void setMagispeller(LivingEntity magispeller) {
        this.magispeller = magispeller;
    }
}
