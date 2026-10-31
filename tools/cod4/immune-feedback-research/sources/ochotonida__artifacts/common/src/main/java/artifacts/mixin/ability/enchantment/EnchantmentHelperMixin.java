package artifacts.mixin.ability.enchantment;

import artifacts.platform.PlatformServices;
import artifacts.registry.ModDataComponents;
import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.Enchantments;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(EnchantmentHelper.class)
public class EnchantmentHelperMixin {

    @ModifyReturnValue(method = "getFishingTimeReduction", at = @At("RETURN"))
    private static float increaseFishingTimeReduction(float original, ServerLevel serverLevel, ItemStack rod, Entity fisher) {
        // Lure >5 breaks fishing, don't return more than 25 unless original was more than 25
        if (original > 25) {
            return original;
        }
        if (PlatformServices.getPlatformHelper().isFishingRod(rod) && fisher instanceof LivingEntity livingEntity) {
            return Math.min(25, original + 5 * ModDataComponents.ENCHANTMENT_LEVEL_MODIFIERS.on(livingEntity)
                    .filter(ability -> ability.enchantment().equals(Enchantments.LURE))
                    .sumInt(ability -> ability.amount().get()));
        }
        return original;
    }

    @ModifyReturnValue(method = "getFishingLuckBonus", at = @At("RETURN"))
    private static int increaseFishingLuckBonus(int original, ServerLevel serverLevel, ItemStack rod, Entity fisher) {
        if (PlatformServices.getPlatformHelper().isFishingRod(rod) && fisher instanceof LivingEntity livingEntity) {
            return original + ModDataComponents.ENCHANTMENT_LEVEL_MODIFIERS.on(livingEntity)
                    .filter(ability -> ability.enchantment().equals(Enchantments.LUCK_OF_THE_SEA))
                    .sumInt(ability -> ability.amount().get());
        }
        return original;
    }
}
