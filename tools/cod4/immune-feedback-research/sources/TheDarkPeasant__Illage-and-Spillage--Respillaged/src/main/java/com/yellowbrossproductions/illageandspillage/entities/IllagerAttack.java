package com.yellowbrossproductions.illageandspillage.entities;

import net.minecraft.world.entity.LivingEntity;

public interface IllagerAttack {
    default LivingEntity getOwner() {
        return null;
    }
}