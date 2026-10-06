package com.dynasty.blueprint;

import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

/** Actual attack-speed debuff, not mining fatigue or a client camera/input lock. */
public final class SpiritChillEffect extends MobEffect {
    public SpiritChillEffect(){
        super(MobEffectCategory.HARMFUL,0x7DD9E8);
        addAttributeModifier(Attributes.ATTACK_SPEED,"c978cba0-63fd-4c19-9e78-b2aa8c394598",-.25,AttributeModifier.Operation.MULTIPLY_TOTAL);
    }
}
