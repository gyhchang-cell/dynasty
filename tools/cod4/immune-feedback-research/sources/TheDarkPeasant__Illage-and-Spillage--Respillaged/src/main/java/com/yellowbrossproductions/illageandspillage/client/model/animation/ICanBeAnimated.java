package com.yellowbrossproductions.illageandspillage.client.model.animation;

import net.minecraft.world.entity.AnimationState;

public interface ICanBeAnimated {
    AnimationState getAnimationState(String var1);

    default float getAnimationSpeed() {
        return 1.0F;
    }
}
