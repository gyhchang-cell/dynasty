package artifacts.mixin.ability.equipabletotem.client;

import artifacts.component.ability.EquipableTotem;
import net.minecraft.client.multiplayer.ClientPacketListener;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(ClientPacketListener.class)
public class ClientPacketListenerMixin {

    // Finds the totem item to display to the player
    @Inject(method = "findTotem", at = @At("HEAD"), cancellable = true)
    private static void findTotem(Player player, CallbackInfoReturnable<ItemStack> cir) {
        ItemStack totem = EquipableTotem.findTotem(player);

        if (totem != null) {
            cir.setReturnValue(totem); // early return intended!
        }
    }
}
