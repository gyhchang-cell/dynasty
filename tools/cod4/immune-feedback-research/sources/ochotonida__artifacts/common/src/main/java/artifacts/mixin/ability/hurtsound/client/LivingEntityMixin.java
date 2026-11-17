package artifacts.mixin.ability.hurtsound.client;

import artifacts.event.ArtifactHooks;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(LivingEntity.class)
public abstract class LivingEntityMixin {

    @Shadow
    protected abstract float getSoundVolume();

    @Shadow
    public abstract float getVoicePitch();

    @Inject(method = "handleDamageEvent", at = @At(value = "HEAD"))
    private void onClientPlayHurtSound(DamageSource source, CallbackInfo ci) {
        ArtifactHooks.onPlaySoundAtEntity((LivingEntity) (Object) this, this.getSoundVolume(), this.getVoicePitch());
    }
}
