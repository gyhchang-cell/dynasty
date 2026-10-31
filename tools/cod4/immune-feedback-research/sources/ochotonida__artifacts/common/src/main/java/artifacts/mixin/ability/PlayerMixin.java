package artifacts.mixin.ability;

import artifacts.event.ArtifactHooks;
import com.llamalad7.mixinextras.injector.ModifyReceiver;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(Player.class)
public class PlayerMixin {

    // Using ModifyReceiver here to reliably capture the final damage value applied to the entity,
    // after armor and effects. The entity being damaged remains the same.
    @ModifyReceiver(method = "actuallyHurt", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/entity/player/Player;setHealth(F)V"))
    private Player onEntityDamaged(Player instance, float health, ServerLevel level, DamageSource source) {
        ArtifactHooks.beforeLivingDamaged((LivingEntity) (Object) this, source, health);
        return instance;
    }
}
