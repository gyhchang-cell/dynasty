package com.yellowbrossproductions.illageandspillage.entities.projectile;

import com.yellowbrossproductions.illageandspillage.util.EntityUtil;
import com.yellowbrossproductions.illageandspillage.util.ItemRegisterer;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.animal.axolotl.Axolotl;
import net.minecraft.world.entity.projectile.ThrownPotion;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.alchemy.Potion;
import net.minecraft.world.item.alchemy.PotionUtils;
import net.minecraft.world.item.alchemy.Potions;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.AbstractCandleBlock;
import net.minecraft.world.level.block.CampfireBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraft.world.level.gameevent.GameEvent.Context;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.HitResult.Type;

import javax.annotation.Nullable;
import java.util.Iterator;
import java.util.List;

public class DarkPotionEntity extends ThrownPotion {
    public DarkPotionEntity(EntityType<? extends ThrownPotion> p_37527_, Level p_37528_) {
        super(p_37527_, p_37528_);
    }

    protected void onHit(HitResult p_37543_) {
        this.onHit_old(p_37543_);
        if (!this.level().isClientSide) {
            ItemStack $$1 = this.getItem();
            Potion $$2 = PotionUtils.getPotion($$1);
            List<MobEffectInstance> $$3 = PotionUtils.getMobEffects($$1);
            boolean $$4 = $$2 == Potions.WATER && $$3.isEmpty();
            if ($$4) {
                this.applyWater();
            } else if (!$$3.isEmpty()) {
                if (this.isLingering()) {
                    this.makeAreaOfEffectCloud($$1, $$2);
                } else {
                    this.applySplash($$3, p_37543_.getType() == Type.ENTITY ? ((EntityHitResult) p_37543_).getEntity() : null);
                }
            }

            int $$5 = $$2.hasInstantEffects() ? 2007 : 2002;
            this.level().levelEvent($$5, this.blockPosition(), PotionUtils.getColor($$1));
            this.discard();
        }

    }

    private void onHit_old(HitResult p_37260_) {
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

    private void applyWater() {
        AABB $$0 = this.getBoundingBox().inflate(4.0, 2.0, 4.0);
        List<LivingEntity> $$1 = this.level().getEntitiesOfClass(LivingEntity.class, $$0, WATER_SENSITIVE_OR_ON_FIRE);
        if (!$$1.isEmpty()) {

            for (LivingEntity $$2 : $$1) {
                double $$3 = this.distanceToSqr($$2);
                if ($$3 < 16.0 && $$2.isSensitiveToWater()) {
                    $$2.hurt(this.damageSources().indirectMagic(this, this.getOwner()), 1.0F);
                }
            }
        }

        List<Axolotl> $$4 = this.level().getEntitiesOfClass(Axolotl.class, $$0);

        for (Axolotl $$5 : $$4) {
            $$5.rehydrate();
        }

    }

    private void makeAreaOfEffectCloud(ItemStack p_37538_, Potion p_37539_) {
        AreaEffectCloud $$2 = new AreaEffectCloud(this.level(), this.getX(), this.getY(), this.getZ());
        Entity $$3 = this.getOwner();
        if ($$3 instanceof LivingEntity) {
            $$2.setOwner((LivingEntity) $$3);
        }

        $$2.setRadius(3.0F);
        $$2.setRadiusOnUse(-0.5F);
        $$2.setWaitTime(10);
        $$2.setRadiusPerTick(-$$2.getRadius() / (float) $$2.getDuration());
        $$2.setPotion(p_37539_);

        for (MobEffectInstance $$4 : PotionUtils.getCustomEffects(p_37538_)) {
            $$2.addEffect(new MobEffectInstance($$4));
        }

        CompoundTag $$5 = p_37538_.getTag();
        if ($$5 != null && $$5.contains("CustomPotionColor", 99)) {
            $$2.setFixedColor($$5.getInt("CustomPotionColor"));
        }

        this.level().addFreshEntity($$2);
    }

    private void applySplash(List<MobEffectInstance> p_37548_, @Nullable Entity p_37549_) {
        AABB $$2 = this.getBoundingBox().inflate(4.0, 2.0, 4.0);
        List<LivingEntity> $$3 = this.level().getEntitiesOfClass(LivingEntity.class, $$2);
        if (!$$3.isEmpty()) {
            Entity $$4 = this.getEffectSource();
            Iterator<LivingEntity> var6 = $$3.iterator();

            while (true) {
                LivingEntity $$5;
                double $$6;
                do {
                    do {
                        if (!var6.hasNext()) {
                            return;
                        }

                        $$5 = var6.next();
                    } while (!$$5.isAffectedByPotions());

                    $$6 = this.distanceToSqr($$5);
                } while (!($$6 < 16.0));

                double $$7 = 1.0 - Math.sqrt($$6) / 4.0;
                if ($$5 == p_37549_) {
                    $$7 = 1.0;
                }

                for (MobEffectInstance $$8 : p_37548_) {
                    MobEffect $$9 = $$8.getEffect();
                    if ($$9.isInstantenous()) {
                        $$9.applyInstantenousEffect(this, this.getOwner(), $$5, $$8.getAmplifier(), $$7);
                    } else {
                        int $$10 = (int) ($$7 * (double) $$8.getDuration() + 0.5);
                        if ($$10 > 20 && this.getOwner() instanceof Mob && EntityUtil.canHurtThisMob($$5, (Mob) this.getOwner())) {
                            $$5.addEffect(new MobEffectInstance($$9, $$10, $$8.getAmplifier(), $$8.isAmbient(), $$8.isVisible()), $$4);
                        }
                    }
                }
            }
        }
    }

    public boolean isLingering() {
        return this.getItem().is(ItemRegisterer.DARK_LINGER.get());
    }

}
