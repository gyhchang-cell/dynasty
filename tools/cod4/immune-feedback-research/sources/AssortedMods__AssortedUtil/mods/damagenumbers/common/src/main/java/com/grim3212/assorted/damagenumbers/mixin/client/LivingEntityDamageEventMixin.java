package com.grim3212.assorted.damagenumbers.mixin.client;

import com.grim3212.assorted.damagenumbers.client.damage.DamageNumbers;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Only watches: neither loader has an event for a damage packet reaching the client. */
@Mixin(LivingEntity.class)
public class LivingEntityDamageEventMixin {

    @Inject(method = "handleDamageEvent", at = @At("HEAD"))
    private void assorteddamagenumbers_rememberDamageSource(DamageSource source, CallbackInfo ci) {
        DamageNumbers.onDamageEvent((LivingEntity) (Object) this, source);
    }
}
