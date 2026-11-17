package artifacts.mixin.attribute.villagerreputation;

import artifacts.registry.ModDataComponents;
import net.minecraft.world.entity.npc.villager.AbstractVillager;
import net.minecraft.world.entity.npc.villager.Villager;
import net.minecraft.world.item.trading.MerchantOffer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(AbstractVillager.class)
public abstract class AbstractVillagerMixin {

    @Inject(method = "notifyTrade", at = @At("RETURN"))
    private void onTrade(MerchantOffer offer, CallbackInfo ci) {
        // Villager reputation attribute only affects villagers
        // noinspection ConstantValue
        if ((Object) this instanceof Villager villager && villager.getTradingPlayer() != null) {
            ModDataComponents.DAMAGE_ON_TRADE.on(villager.getTradingPlayer())
                    .iterate((component, slot) -> slot.hurtAndBreak(component.get()));
        }
    }
}
