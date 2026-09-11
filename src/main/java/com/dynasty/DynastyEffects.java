package com.dynasty;

import com.dynasty.Dynasty;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * Dynasty 状态效果 / Dynasty status effects.
 */
@SuppressWarnings("null")
public class DynastyEffects {

    public static final DeferredRegister<MobEffect> EFFECTS =
            DeferredRegister.create(ForgeRegistries.MOB_EFFECTS, Dynasty.MODID);

    /** 龙威：提升攻击力 / Dragon's Might: bonus attack damage */
    public static final RegistryObject<MobEffect> DRAGON_MIGHT = EFFECTS.register("dragon_might", DragonMightEffect::new);

    /** 铁壁：提升护甲 / Iron Wall: bonus armor */
    public static final RegistryObject<MobEffect> IRON_WALL = EFFECTS.register("iron_wall", IronWallEffect::new);

    /** 疾风：提升移动速度 / Swift Wind: bonus movement speed */
    public static final RegistryObject<MobEffect> SWIFT_WIND = EFFECTS.register("swift_wind", SwiftWindEffect::new);

    /** 威慑：降低攻击力（负面）/ Intimidation: reduced attack damage (harmful) */
    public static final RegistryObject<MobEffect> INTIMIDATION = EFFECTS.register("intimidation", IntimidationEffect::new);

    /** 民心：提升最大生命 / Loyalty: bonus max health */
    public static final RegistryObject<MobEffect> LOYALTY = EFFECTS.register("loyalty", LoyaltyEffect::new);

    /** 天命：提升幸运 / Mandate of Heaven: bonus luck */
    public static final RegistryObject<MobEffect> MANDATE_OF_HEAVEN =
            EFFECTS.register("mandate_of_heaven", MandateOfHeavenEffect::new);

    /** 内伤：降低移动速度（负面）/ Internal Injury: reduced movement speed (harmful) */
    public static final RegistryObject<MobEffect> INTERNAL_INJURY =
            EFFECTS.register("internal_injury", InternalInjuryEffect::new);

    public static class DragonMightEffect extends MobEffect {
        public DragonMightEffect() {
            super(MobEffectCategory.BENEFICIAL, 0xF2C14E);
            addAttributeModifier(Attributes.ATTACK_DAMAGE,
                    "6e0f4b3c-1f4f-4a1c-9a51-2d2b1a7f0c01", 300.0D, AttributeModifier.Operation.ADDITION);
        }
    }

    public static class IronWallEffect extends MobEffect {
        public IronWallEffect() {
            super(MobEffectCategory.BENEFICIAL, 0xC9D2D9);
            addAttributeModifier(Attributes.ARMOR,
                    "6e0f4b3c-1f4f-4a1c-9a51-2d2b1a7f0c02", 20.0D, AttributeModifier.Operation.ADDITION);
        }
    }

    public static class SwiftWindEffect extends MobEffect {
        public SwiftWindEffect() {
            super(MobEffectCategory.BENEFICIAL, 0x7FD8F0);
            addAttributeModifier(Attributes.MOVEMENT_SPEED,
                    "6e0f4b3c-1f4f-4a1c-9a51-2d2b1a7f0c03", 0.05D, AttributeModifier.Operation.ADDITION);
        }
    }

    public static class IntimidationEffect extends MobEffect {
        public IntimidationEffect() {
            super(MobEffectCategory.HARMFUL, 0x9B1B1B);
            addAttributeModifier(Attributes.ATTACK_DAMAGE,
                    "6e0f4b3c-1f4f-4a1c-9a51-2d2b1a7f0c04", -2.0D, AttributeModifier.Operation.ADDITION);
        }
    }

    public static class LoyaltyEffect extends MobEffect {
        public LoyaltyEffect() {
            super(MobEffectCategory.BENEFICIAL, 0xE0B84E);
            addAttributeModifier(Attributes.MAX_HEALTH,
                    "6e0f4b3c-1f4f-4a1c-9a51-2d2b1a7f0c05", 100.0D, AttributeModifier.Operation.ADDITION);
        }
    }

    public static class MandateOfHeavenEffect extends MobEffect {
        public MandateOfHeavenEffect() {
            super(MobEffectCategory.BENEFICIAL, 0xFFD24A);
            addAttributeModifier(Attributes.LUCK,
                    "6e0f4b3c-1f4f-4a1c-9a51-2d2b1a7f0c06", 20.0D, AttributeModifier.Operation.ADDITION);
        }
    }

    public static class InternalInjuryEffect extends MobEffect {
        public InternalInjuryEffect() {
            super(MobEffectCategory.HARMFUL, 0x6B1B1B);
            addAttributeModifier(Attributes.MOVEMENT_SPEED,
                    "6e0f4b3c-1f4f-4a1c-9a51-2d2b1a7f0c07", -0.05D, AttributeModifier.Operation.ADDITION);
        }
    }
}
