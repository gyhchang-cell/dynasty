package com.yellowbrossproductions.illageandspillage.entities.projectile;

import com.yellowbrossproductions.illageandspillage.Config;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.SmallFireball;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseFireBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.event.ForgeEventFactory;

public class IgniterFireballEntity extends SmallFireball {
    public IgniterFireballEntity(EntityType<? extends SmallFireball> p_37364_, Level p_37365_) {
        super(p_37364_, p_37365_);
    }

    public IgniterFireballEntity(Level p_37375_, LivingEntity p_37376_, double p_37377_, double p_37378_, double p_37379_) {
        super(p_37375_, p_37376_, p_37377_, p_37378_, p_37379_);
    }

    public IgniterFireballEntity(Level p_37367_, double p_37368_, double p_37369_, double p_37370_, double p_37371_, double p_37372_, double p_37373_) {
        super(p_37367_, p_37368_, p_37369_, p_37370_, p_37371_, p_37372_, p_37373_);
    }

    protected void onHitBlock(BlockHitResult p_37384_) {
        BlockState blockstate = this.level().getBlockState(p_37384_.getBlockPos());
        blockstate.onProjectileHit(this.level(), blockstate, p_37384_, this);
        if (Config.CommonConfig.igniter_canBurnBlocks.get() && !this.level().isClientSide && ForgeEventFactory.getMobGriefingEvent(this.level(), this)) {
            BlockPos blockpos = p_37384_.getBlockPos().relative(p_37384_.getDirection());
            if (this.level().isEmptyBlock(blockpos)) {
                this.level().setBlockAndUpdate(blockpos, BaseFireBlock.getState(this.level(), blockpos));
            }
        }

    }
}
