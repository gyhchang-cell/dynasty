package artifacts.mixin.compat.apoli.condition.type.entity;

import artifacts.item.UmbrellaHelper;
import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import com.llamalad7.mixinextras.sugar.Local;
import io.github.apace100.apoli.condition.type.entity.ExposedToSunEntityConditionType;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(ExposedToSunEntityConditionType.class)
public abstract class ExposedToSunEntityConditionTypeMixin {

	@ModifyReturnValue(method = "test(Lio/github/apace100/apoli/condition/context/EntityConditionContext;)Z", at = @At("RETURN"), remap = false)
	private boolean accountForUprightUmbrella(boolean original, @Local(name = "entity") Entity entity) {
		return original && !UmbrellaHelper.isHoldingUmbrellaUpright(entity, true);
	}
}
