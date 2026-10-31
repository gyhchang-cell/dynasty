package artifacts.fabric.mixin.attribute.eatingspeed;

import artifacts.event.ArtifactHooks;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(LivingEntity.class)
public abstract class LivingEntityMixin {

    @ModifyExpressionValue(method = "startUsingItem", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/item/ItemStack;getUseDuration(Lnet/minecraft/world/entity/LivingEntity;)I"))
    private int decreaseDrinkingDuration(int original, InteractionHand hand) {
        LivingEntity entity = (LivingEntity) (Object) this;
        return ArtifactHooks.modifyUseDuration(original, entity.getItemInHand(hand), entity);
    }
}
