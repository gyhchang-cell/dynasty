package artifacts.mixin.ability.infiniteconsumable;

import artifacts.component.ability.SimpleAbility;
import artifacts.registry.ModDataComponents;
import com.llamalad7.mixinextras.injector.ModifyReceiver;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.Consumable;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(Consumable.class)
public class ConsumableMixin {

    @ModifyReceiver(method = "onConsume", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/item/ItemStack;consume(ILnet/minecraft/world/entity/LivingEntity;)V"))
    public ItemStack modifyConsumedStack(ItemStack stack, int amount, LivingEntity owner) {
        SimpleAbility ability = stack.get(ModDataComponents.INFINITE_CONSUMABLE.get());
        if (ability != null && ability.isNonCosmetic()) {
            return stack.copy();
        }
        return stack;
    }
}
