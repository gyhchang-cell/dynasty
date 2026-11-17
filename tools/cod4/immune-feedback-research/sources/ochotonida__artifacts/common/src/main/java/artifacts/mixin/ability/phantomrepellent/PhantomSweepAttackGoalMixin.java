package artifacts.mixin.ability.phantomrepellent;

import artifacts.registry.ModDataComponents;
import com.llamalad7.mixinextras.injector.ModifyReceiver;
import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import net.minecraft.core.Holder;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.animal.feline.CatSoundVariants;
import net.minecraft.world.entity.monster.Phantom;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(targets = "net.minecraft.world.entity.monster.Phantom$PhantomSweepAttackGoal")
public class PhantomSweepAttackGoalMixin {

    @Unique
    private Phantom artifacts$phantom;

    @ModifyReceiver(method = "canContinueToUse", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/entity/monster/Phantom;getTarget()Lnet/minecraft/world/entity/LivingEntity;"))
    private Phantom canContinueToUse(Phantom instance) {
        artifacts$phantom = instance;
        return instance;
    }

    @ModifyReturnValue(method = "canContinueToUse", at = @At("RETURN"))
    private boolean hissAtPhantom(boolean original) {
        if (artifacts$phantom != null && original) {
            LivingEntity target = artifacts$phantom.getTarget();
            if (target != null && artifacts$phantom.distanceToSqr(target) < 16 * 16
                    && ModDataComponents.PHANTOM_REPELLENT.on(target).findAny()
            ) {
                Holder<SoundEvent> hiss = SoundEvents.CAT_SOUNDS.get(CatSoundVariants.SoundSet.CLASSIC).adultSounds().hissSound();
                target.level().playSound(null, target.getX(), target.getY(), target.getZ(), hiss, target.getSoundSource(), 1F, 1F);
                return false;
            }
        }
        return original;
    }
}
