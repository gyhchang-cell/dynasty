package de.njlent.damagenumbers.mixin;

import de.njlent.damagenumbers.modules.combat.DamageNumbersModule;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(LivingEntity.class)
public abstract class LivingEntityMixin {
    @Unique
    private float damagenumbers$previousHealth = 0.0F;

    @Inject(method = "tick()V", at = @At("TAIL"))
    private void damagenumbers$onTick(CallbackInfo info) {
        LivingEntity entity = (LivingEntity) (Object) this;
        if (!entity.level().isClientSide()) return;

        float oldHealth = damagenumbers$previousHealth;
        float newHealth = entity.getHealth();

        if (oldHealth != newHealth) {
            damagenumbers$previousHealth = newHealth;
            DamageNumbersModule.onEntityHealthChange(entity, oldHealth, newHealth);
        }
    }
}
