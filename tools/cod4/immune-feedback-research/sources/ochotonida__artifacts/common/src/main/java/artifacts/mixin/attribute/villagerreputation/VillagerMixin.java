package artifacts.mixin.attribute.villagerreputation;

import artifacts.registry.ModAttributes;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import net.minecraft.world.entity.npc.villager.Villager;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(Villager.class)
public abstract class VillagerMixin {

    @ModifyExpressionValue(method = "updateSpecialPrices", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/entity/npc/villager/Villager;getPlayerReputation(Lnet/minecraft/world/entity/player/Player;)I"))
    private int increaseReputation(int original, Player player) {
        return original + (int) player.getAttributeValue(ModAttributes.VILLAGER_REPUTATION);
    }
}
