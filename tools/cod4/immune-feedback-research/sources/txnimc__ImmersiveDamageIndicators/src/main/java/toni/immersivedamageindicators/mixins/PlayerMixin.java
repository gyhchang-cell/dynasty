package toni.immersivedamageindicators.mixins;

import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import toni.immersivedamageindicators.ImmersiveDamageIndicators;

@Mixin(Player.class)
public class PlayerMixin {

    @Inject(method = "attack", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/entity/player/Player;getAttackStrengthScale(F)F"))
    private void onAttack(Entity target, CallbackInfo ci) {
        var localPlayer = (Player) (Object) this;
        ImmersiveDamageIndicators.LAST_ATTACK_SWING.put(localPlayer.getUUID(), localPlayer.getAttackStrengthScale(0.5F));
    }


    @Inject(method = "attack", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/entity/player/Player;crit(Lnet/minecraft/world/entity/Entity;)V"))
    private void onCrit(Entity target, CallbackInfo ci) {
        var localPlayer = (Player) (Object) this;
        ImmersiveDamageIndicators.LAST_ATTACK_SWING.put(localPlayer.getUUID(), 1.1f);
    }
}
