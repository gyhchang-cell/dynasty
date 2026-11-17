package artifacts.mixin.ability.posteatingeffects;

import artifacts.component.ability.mobeffect.PostEatingEffect;
import artifacts.event.ArtifactHooks;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.Consumable;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(FoodProperties.class)
public abstract class FoodPropertiesMixin {

    @Inject(method = "onConsume", at = @At("HEAD"))
    public void eat(Level level, LivingEntity user, ItemStack stack, Consumable consumable, CallbackInfo ci) {
        FoodProperties foodProperties = (FoodProperties) (Object) this;
        PostEatingEffect.applyEffects(user, foodProperties);
        ArtifactHooks.applyBoneMealAfterEating(user, foodProperties);
    }
}
