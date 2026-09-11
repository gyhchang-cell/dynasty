package com.dynasty;

import com.dynasty.Dynasty;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.item.alchemy.Potion;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * Dynasty 定制药水（可在酿造台酿造）。
 * Dynasty custom potions (brewed in a brewing stand).
 */
@SuppressWarnings("null")
public class DynastyPotions {

    public static final DeferredRegister<Potion> POTIONS =
            DeferredRegister.create(ForgeRegistries.POTIONS, Dynasty.MODID);

    /** 龙威药水 / Potion of Dragon's Might */
    public static final RegistryObject<Potion> DRAGON_MIGHT = POTIONS.register("dragon_might",
            () -> new Potion(new MobEffectInstance(DynastyEffects.DRAGON_MIGHT.get(), 20 * 180, 0)));

    /** 铁壁药水 / Potion of Iron Wall */
    public static final RegistryObject<Potion> IRON_WALL = POTIONS.register("iron_wall",
            () -> new Potion(new MobEffectInstance(DynastyEffects.IRON_WALL.get(), 20 * 180, 0)));

    /** 疾风药水 / Potion of Swift Wind */
    public static final RegistryObject<Potion> SWIFT_WIND = POTIONS.register("swift_wind",
            () -> new Potion(new MobEffectInstance(DynastyEffects.SWIFT_WIND.get(), 20 * 180, 0)));

    /** 威慑药水（负面）/ Potion of Intimidation (harmful) */
    public static final RegistryObject<Potion> INTIMIDATION = POTIONS.register("intimidation",
            () -> new Potion(new MobEffectInstance(DynastyEffects.INTIMIDATION.get(), 20 * 90, 0)));

    /** 民心药水 / Potion of Loyalty */
    public static final RegistryObject<Potion> LOYALTY = POTIONS.register("loyalty",
            () -> new Potion(new MobEffectInstance(DynastyEffects.LOYALTY.get(), 20 * 180, 0)));

    /** 天命药水 / Potion of Mandate of Heaven */
    public static final RegistryObject<Potion> MANDATE_OF_HEAVEN = POTIONS.register("mandate_of_heaven",
            () -> new Potion(new MobEffectInstance(DynastyEffects.MANDATE_OF_HEAVEN.get(), 20 * 180, 0)));
}
