package artifacts.mixin.attribute.flatulence;

import artifacts.event.ArtifactHooks;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(Entity.class)
public abstract class EntityMixin {

    @Shadow
    public abstract boolean isShiftKeyDown();

    @Inject(method = "setShiftKeyDown", at = @At("HEAD"))
    private void setShiftKeyDown(boolean shiftKeyDown, CallbackInfo ci) {
        Entity self = (Entity) (Object) this;
        if (shiftKeyDown && !isShiftKeyDown() && self instanceof LivingEntity livingEntity) {
            ArtifactHooks.fart(livingEntity);
        }
    }
}
