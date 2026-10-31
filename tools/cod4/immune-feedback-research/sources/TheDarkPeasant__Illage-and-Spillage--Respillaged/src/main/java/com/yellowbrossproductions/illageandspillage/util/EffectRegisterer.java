package com.yellowbrossproductions.illageandspillage.util;

import com.yellowbrossproductions.illageandspillage.effect.*;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class EffectRegisterer {
    public static final DeferredRegister<MobEffect> EFFECTS;
    public static final RegistryObject<MobEffect> DISABILITY;
    public static final RegistryObject<MobEffect> MISCONDUCTION;
    public static final RegistryObject<MobEffect> PRESERVED;
    public static final RegistryObject<MobEffect> MUTATION;
    public static final RegistryObject<MobEffect> WEBBED;

    public EffectRegisterer() {
    }

    static {
        EFFECTS = DeferredRegister.create(ForgeRegistries.MOB_EFFECTS, "illageandspillage");
        DISABILITY = EFFECTS.register("disability", () -> new DisabilityEffect(MobEffectCategory.HARMFUL, 3484199));
        MISCONDUCTION = EFFECTS.register("misconduction", () -> new MisconductionEffect(MobEffectCategory.BENEFICIAL, 3484199));
        PRESERVED = EFFECTS.register("preserved", () -> new PreservedEffect(MobEffectCategory.BENEFICIAL, 3484199));
        MUTATION = EFFECTS.register("mutation", () -> new MutationEffect(MobEffectCategory.HARMFUL, 3484199));
        WEBBED = EFFECTS.register("webbed", () -> new WebbedEffect(MobEffectCategory.HARMFUL, 3484199));
    }
}
