package artifacts.neoforge.mixin.ability.sinking;

import artifacts.registry.ModDataComponents;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(Player.class)
public class PlayerMixin {

    @ModifyExpressionValue(method = "getDestroySpeed(Lnet/minecraft/world/level/block/state/BlockState;Lnet/minecraft/core/BlockPos;)F", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/entity/EntityFluidInteraction;isEyeInFluidMatching(Lnet/minecraft/world/entity/Entity;Lnet/neoforged/neoforge/fluids/InFluidPredicate;)Z"))
    private boolean isDestroySpeedAffectedByWater(boolean isInFluid) {
        Player player = (Player) (Object) this;
        return isInFluid && !ModDataComponents.SINKING.on(player).findAny();
    }
}
