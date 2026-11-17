package com.yellowbrossproductions.illageandspillage.effect;

import com.google.common.collect.ImmutableList;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ItemStack;

import java.util.List;
import java.util.UUID;

public class WebbedEffect extends MobEffect {
    public static final UUID MODIFIER_UUID = UUID.fromString("637D7064-EBBA-486E-3ABE-C2C23A6DD7A9");

    public WebbedEffect(MobEffectCategory type, int liquidColor) {
        super(type, liquidColor);
        this.addAttributeModifier(Attributes.MOVEMENT_SPEED, MODIFIER_UUID.toString(), -0.8, Operation.MULTIPLY_BASE);
    }

    @Override
    public List<ItemStack> getCurativeItems() {
        return ImmutableList.of();
    }
}
