package artifacts.mixin.item.umbrella;

import artifacts.item.UmbrellaHelper;
import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(Entity.class)
public abstract class EntityMixin {

    @ModifyReturnValue(method = "isInRain", at = @At("RETURN"))
    private boolean blockRain(boolean original) {
        if ((Object) this instanceof LivingEntity entity) {
            return original && !UmbrellaHelper.isHoldingUmbrellaUpright(entity, true);
        }
        return original;
    }
}
