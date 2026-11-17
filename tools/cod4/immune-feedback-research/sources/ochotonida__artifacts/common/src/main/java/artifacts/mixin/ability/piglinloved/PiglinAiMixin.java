package artifacts.mixin.ability.piglinloved;

import artifacts.registry.ModDataComponents;
import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.piglin.PiglinAi;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(PiglinAi.class)
public abstract class PiglinAiMixin {

    @ModifyReturnValue(method = "isWearingSafeArmor", at = @At("RETURN"))
    private static boolean isWearingGold(boolean original, LivingEntity livingEntity) {
        return original || ModDataComponents.PIGLIN_LOVED.on(livingEntity).findAny();
    }
}
