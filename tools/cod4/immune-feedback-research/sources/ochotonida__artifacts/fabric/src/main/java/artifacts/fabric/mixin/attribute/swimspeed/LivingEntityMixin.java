package artifacts.fabric.mixin.attribute.swimspeed;

import artifacts.registry.ModAttributes;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

@Mixin(LivingEntity.class)
public abstract class LivingEntityMixin {

    @ModifyArg(method = "jumpInLiquid", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/phys/Vec3;add(DDD)Lnet/minecraft/world/phys/Vec3;"), index = 1)
    private double increaseSwimUpSpeed(double y) {
        return getIncreasedSwimSpeed(y);
    }

    @ModifyArg(method = "travelInWater", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/entity/LivingEntity;moveRelative(FLnet/minecraft/world/phys/Vec3;)V"))
    private float increaseSwimSpeed(float speed) {
        return (float) getIncreasedSwimSpeed(speed);
    }

    @Unique
    private double getIncreasedSwimSpeed(double speed) {
        // noinspection ConstantConditions
        return speed * ((LivingEntity) (Object) this).getAttributeValue(ModAttributes.SWIM_SPEED);
    }
}
