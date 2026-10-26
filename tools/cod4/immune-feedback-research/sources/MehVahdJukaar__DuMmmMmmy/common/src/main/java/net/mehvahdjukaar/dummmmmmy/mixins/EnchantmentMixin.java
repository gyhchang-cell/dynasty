package net.mehvahdjukaar.dummmmmmy.mixins;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.llamalad7.mixinextras.sugar.Local;
import net.mehvahdjukaar.dummmmmmy.common.TargetDummyEntity;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.enchantment.ConditionalEffect;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.level.storage.loot.LootContext;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;

import java.lang.ref.WeakReference;
import java.util.List;
import java.util.function.Consumer;

@Mixin(Enchantment.class)
public abstract class EnchantmentMixin {


    @WrapOperation(method = {"isImmuneToDamage", "modifyDamageProtection", "runLocationChangedEffects"},
            at = @At(value = "INVOKE", target = "Lnet/minecraft/world/item/enchantment/ConditionalEffect;matches(Lnet/minecraft/world/level/storage/loot/LootContext;)Z"))
    private boolean dummy$entityAwareMatch(ConditionalEffect<?> instance, LootContext context, Operation<Boolean> operation) {
        boolean original = operation.call(instance, context);
        if (original) return true;

        var entity = context.getParamOrNull(LootContextParams.THIS_ENTITY);
        if (entity instanceof TargetDummyEntity e) {
            return e.getMobType().isVulnerableTo((Enchantment) (Object) this);

        }
        return false;
    }

    @Unique
    private static WeakReference<Entity> dummy$entityHack = null;
    @Unique
    private static WeakReference<Enchantment> dummy$enchantmentHack = null;

    @ModifyExpressionValue(method = "applyEffects",
            at = @At(value = "INVOKE", target = "Lnet/minecraft/world/item/enchantment/ConditionalEffect;matches(Lnet/minecraft/world/level/storage/loot/LootContext;)Z"))
    private static boolean dummy$entityAwareMatch2(boolean original, @Local(argsOnly = true) LootContext context) {
        if (dummy$entityHack != null && dummy$entityHack.get() instanceof TargetDummyEntity te && dummy$enchantmentHack != null) {
            original |= te.getMobType().isVulnerableTo(dummy$enchantmentHack.get());
        }
        dummy$entityHack = null;
        dummy$enchantmentHack = null;
        return original;
    }

    @WrapOperation(method = {"modifyEntityFilteredValue", "tick", "onProjectileSpawned", "modifyDamageFilteredValue"},
            at = @At(value = "INVOKE", target = "Lnet/minecraft/world/item/enchantment/Enchantment;applyEffects(Ljava/util/List;Lnet/minecraft/world/level/storage/loot/LootContext;Ljava/util/function/Consumer;)V"))
    private void dummy$entityAwareMatch(List<ConditionalEffect> effects, LootContext context, Consumer applier, Operation<Void> original,
                                        @Local(argsOnly = true) Entity entity) {
        dummy$entityHack = new WeakReference<>(entity);
        dummy$enchantmentHack = new WeakReference<>((Enchantment) (Object) this);
        original.call(effects, context, applier);
    }

}
