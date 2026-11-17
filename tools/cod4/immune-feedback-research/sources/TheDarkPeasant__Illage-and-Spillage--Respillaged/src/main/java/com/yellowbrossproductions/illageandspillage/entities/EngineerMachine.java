package com.yellowbrossproductions.illageandspillage.entities;

import net.minecraft.world.entity.LivingEntity;

public interface EngineerMachine {
    LivingEntity getOwner();

    void setOwner(LivingEntity entity);
}