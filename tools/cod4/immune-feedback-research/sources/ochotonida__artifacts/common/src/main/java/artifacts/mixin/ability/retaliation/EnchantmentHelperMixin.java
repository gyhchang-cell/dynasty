package artifacts.mixin.ability.retaliation;

import artifacts.event.ArtifactHooks;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(EnchantmentHelper.class)
public class EnchantmentHelperMixin {

    @Inject(method = "doPostAttackEffectsWithItemSource", at = @At("HEAD"))
    private static void doPostAttackEffects(ServerLevel serverLevel, Entity victim, DamageSource damageSource, ItemStack source, CallbackInfo ci) {
        if (victim instanceof LivingEntity livingEntity) {
            ArtifactHooks.doPostAttackEffects(livingEntity, damageSource);
        }
    }
}
