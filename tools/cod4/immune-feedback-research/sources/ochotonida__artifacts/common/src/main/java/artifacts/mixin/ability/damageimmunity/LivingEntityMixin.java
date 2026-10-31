package artifacts.mixin.ability.damageimmunity;

import artifacts.registry.ModDataComponents;
import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(LivingEntity.class)
public class LivingEntityMixin {

    @ModifyReturnValue(method = "isInvulnerableTo", at = @At("RETURN"))
    public boolean isInvulnerableTo(boolean original, ServerLevel level, DamageSource source) {
        LivingEntity entity = (LivingEntity) (Object) this;
        return original || ModDataComponents.DAMAGE_IMMUNITY.on(entity)
                .filter(ability -> ability.condition().test(entity) && source.is(ability.tag()))
                .findAny();
    }
}
