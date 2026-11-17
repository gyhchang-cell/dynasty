package artifacts.fabric.mixin.ability;

import artifacts.event.ArtifactHooks;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

// TODO: move some of these mixins to common
@Mixin(value = LivingEntity.class)
public abstract class LivingEntityMixin {

    @Inject(at = @At("TAIL"), method = "tick")
    private void tick(CallbackInfo info) {
        LivingEntity self = (LivingEntity) (Object) this;
        if (self.isRemoved()) {
            return;
        }
        ArtifactHooks.livingUpdate(self);
    }
}
