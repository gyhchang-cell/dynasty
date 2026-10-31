package artifacts.mixin.ability.enderpearlhungercost;

import artifacts.registry.ModDataComponents;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.EnderpearlItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(EnderpearlItem.class)
public abstract class EnderPearlItemMixin extends Item {

    public EnderPearlItemMixin(Properties properties) {
        super(properties);
    }

    @WrapOperation(method = "use", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/item/ItemStack;consume(ILnet/minecraft/world/entity/LivingEntity;)V"))
    private void shouldConsumeEnderPearl(ItemStack stack, int amount, LivingEntity owner, Operation<Void> operation) {
        if (ModDataComponents.ENDER_PEARL_HUNGER_COST.on(owner).findAny() && owner instanceof Player player) {
            int cost = ModDataComponents.ENDER_PEARL_HUNGER_COST.on(player)
                    .minInt(20, ability -> ability.foodCost().get());
            if (player.getFoodData().getFoodLevel() >= cost || player.isCreative()) {
                if (cost > 0 && !player.isCreative()) {
                    player.getFoodData().setFoodLevel(player.getFoodData().getFoodLevel() - cost);
                    owner.level().playSound(
                            null,
                            player.getX(),
                            player.getY(),
                            player.getZ(),
                            SoundEvents.GENERIC_EAT,
                            SoundSource.PLAYERS,
                            0.5F,
                            0.8F + owner.getRandom().nextFloat() * 0.4F
                    );
                }
                ModDataComponents.ENDER_PEARL_HUNGER_COST.on(player).iterate((ability, slot) -> {
                    slot.addCooldown(ability.cooldown().get() * 20);
                    slot.hurtAndBreak(ability.itemDamage().get());
                });
                return;
            }
        }
        operation.call(stack, amount, owner);
    }
}
