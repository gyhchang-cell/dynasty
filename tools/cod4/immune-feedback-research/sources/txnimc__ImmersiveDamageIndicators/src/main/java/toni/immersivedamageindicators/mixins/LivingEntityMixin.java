package toni.immersivedamageindicators.mixins;

import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import toni.immersivedamageindicators.ImmersiveDamageIndicators;
import toni.immersivedamageindicators.foundation.ParticleRegistry;
import toni.immersivedamageindicators.foundation.config.AllConfigs;

@Mixin(LivingEntity.class)
public class LivingEntityMixin {
    private float lastHealth = 0;
    private float damageTaken = 0;
    private boolean particleDisplayedThisTick = false;

    @Inject(method = "tick", at = @At("HEAD"))
    public void onTick(CallbackInfo ci) {
        LivingEntity inst = (LivingEntity) (Object) this;
        if (!inst.level().isClientSide()) return;

        if (particleDisplayedThisTick) {
            particleDisplayedThisTick = false;
        }

        LivingEntity entity = (LivingEntity) (Object) this;
        float currentHealth = entity.getHealth();

        if (lastHealth > currentHealth && !particleDisplayedThisTick) {
            damageTaken = lastHealth - currentHealth;
        }

        lastHealth = currentHealth;
    }

    @Inject(method = "tick", at = @At("TAIL"))
    public void afterTick(CallbackInfo ci) {
        LivingEntity inst = (LivingEntity) (Object) this;
        if (!inst.level().isClientSide()) return;
        if (inst.getLastDamageSource() == null) return;
        if (!(inst.getLastDamageSource().getEntity() instanceof LocalPlayer)) return;

        double x = inst.getX();
        double y = inst.getY();
        double z = inst.getZ();

        if (!particleDisplayedThisTick && damageTaken > 0) {
            Minecraft client = Minecraft.getInstance();
            LocalPlayer player = (LocalPlayer) inst.getLastDamageSource().getEntity();

            client.level.addParticle(
                ParticleRegistry.DAMAGE_PARTICLE,
                x,
                y,
                z,
                damageTaken,
                0xFFFFFF,
                ImmersiveDamageIndicators.LAST_ATTACK_SWING.getOrDefault(player.getUUID(), 0f)
            ); damageTaken = 0; particleDisplayedThisTick = true;
        }
    }
}