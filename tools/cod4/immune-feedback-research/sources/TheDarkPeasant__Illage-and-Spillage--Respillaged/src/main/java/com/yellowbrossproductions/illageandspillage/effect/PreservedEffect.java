package com.yellowbrossproductions.illageandspillage.effect;

import java.util.UUID;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation;

public class PreservedEffect extends MobEffect {
    public static final UUID MODIFIER_UUID = UUID.fromString("637D7064-E92A-486E-8ABE-C2C23A6DD7A9");

    public PreservedEffect(MobEffectCategory type, int liquidColor) {
        super(type, liquidColor);
        this.addAttributeModifier(Attributes.KNOCKBACK_RESISTANCE, MODIFIER_UUID.toString(), 0.7, Operation.ADDITION);
    }
}
