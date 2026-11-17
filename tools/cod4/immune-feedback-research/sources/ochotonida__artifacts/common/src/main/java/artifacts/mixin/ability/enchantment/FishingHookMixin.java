package artifacts.mixin.ability.enchantment;

import artifacts.event.ArtifactHooks;
import net.minecraft.world.entity.projectile.FishingHook;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(FishingHook.class)
public abstract class FishingHookMixin {

    @Inject(method = "retrieve", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/level/storage/loot/LootTable;getRandomItems(Lnet/minecraft/world/level/storage/loot/LootParams;)Lit/unimi/dsi/fastutil/objects/ObjectArrayList;"))
    private void onItemFished(ItemStack rod, CallbackInfoReturnable<Integer> cir) {
        FishingHook self = (FishingHook) (Object) this;
        if (self.getPlayerOwner() != null) {
            ArtifactHooks.onItemFished(self.getPlayerOwner());
        }
    }
}
