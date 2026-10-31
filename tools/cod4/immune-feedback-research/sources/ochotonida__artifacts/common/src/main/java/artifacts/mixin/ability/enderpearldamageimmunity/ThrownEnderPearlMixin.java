package artifacts.mixin.ability.enderpearldamageimmunity;

import artifacts.registry.ModDataComponents;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.projectile.throwableitemprojectile.ThrownEnderpearl;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(ThrownEnderpearl.class)
public class ThrownEnderPearlMixin {

    @WrapOperation(method = "onHit", at = @At(value = "INVOKE", target = "Lnet/minecraft/server/level/ServerPlayer;hurtServer(Lnet/minecraft/server/level/ServerLevel;Lnet/minecraft/world/damagesource/DamageSource;F)Z"))
    private boolean shouldApplyDamage(ServerPlayer player, ServerLevel level, DamageSource source, float damage, Operation<Boolean> original) {
        if (!ModDataComponents.ENDER_PEARL_DAMAGE_IMMUNITY.on(player).findAny()) {
            return original.call(player, level, source, damage);
        } else {
            return false;
        }
    }
}
