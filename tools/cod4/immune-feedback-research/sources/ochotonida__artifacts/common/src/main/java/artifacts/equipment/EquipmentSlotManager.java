package artifacts.equipment;

import artifacts.component.Equipable;
import artifacts.registry.ModDataComponents;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.util.Unit;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.Consumable;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.LinkedHashSet;
import java.util.Set;
import java.util.function.BiFunction;
import java.util.function.Consumer;

public class EquipmentSlotManager {

    private static final Set<EquipmentSlotProvider> SLOT_PROVIDERS = new LinkedHashSet<>();

    public static void register(EquipmentSlotProvider integration) {
        SLOT_PROVIDERS.add(integration);
    }

    public static void iterateEquipment(@Nullable LivingEntity entity, boolean skipItemsOnCooldown, boolean skipDisabledItems, Consumer<ItemStack> consumer) {
        reduceEquipment(entity, skipItemsOnCooldown, skipDisabledItems, Unit.INSTANCE, (_, slotAccess) -> {
            consumer.accept(slotAccess.get());
            return Unit.INSTANCE;
        });
    }

    public static <ACC> ACC reduceEquipment(@Nullable LivingEntity entity, boolean skipItemsOnCooldown, boolean skipDisabledItems, ACC init, BiFunction<ACC, EquipmentSlotAccess, ACC> f) {
        return reduceEquipment(entity, init, ((slotAccess, acc) -> {
            boolean checkCooldown = !skipItemsOnCooldown || !slotAccess.isOnCooldown(entity);
            boolean checkDisabled = !skipDisabledItems || !slotAccess.isDisabledOrBroken();
            if (checkCooldown && checkDisabled) {
                return f.apply(acc, slotAccess);
            }
            return acc;
        }));
    }

    protected static <ACC> ACC reduceEquipment(@Nullable LivingEntity entity, ACC init, BiFunction<EquipmentSlotAccess, ACC, ACC> f) {
        if (entity != null) {
            for (EquipmentSlotProvider slotProvider : SLOT_PROVIDERS) {
                init = slotProvider.reduceEquipment(entity, init, f);
            }
        }
        return init;
    }

    public static boolean tryEquipAccessory(LivingEntity entity, ItemStack stack) {
        for (EquipmentSlotProvider slotProvider : SLOT_PROVIDERS) {
            if (slotProvider.tryEquip(entity, stack, false).isEmpty()) {
                return true;
            }
        }
        return false;
    }

    public static InteractionResult tryEquipFromUse(LivingEntity entity, InteractionHand hand) {
        ItemStack stack = entity.getItemInHand(hand);
        Equipable equipable = stack.get(ModDataComponents.EQUIPABLE.get());
        Consumable consumable = stack.get(DataComponents.CONSUMABLE);
        if (equipable != null && (consumable == null || !consumable.canConsume(entity, stack))) {
            // try equipping in an empty slot first, otherwise swap if allowed
            ItemStack result = tryEquipFromUse(entity, stack, false);
            if (result == stack && equipable.swappable()) {
                result = tryEquipFromUse(entity, stack, true);
            }
            if (result != stack) {
                playEquipSound(entity, equipable.equipSound());
                entity.setItemInHand(hand, result.copy());
                return entity.level().isClientSide() ? InteractionResult.SUCCESS : InteractionResult.SUCCESS_SERVER;
            }
        }
        return InteractionResult.PASS;
    }

    private static ItemStack tryEquipFromUse(LivingEntity entity, ItemStack stack, boolean allowSwapping) {
        for (EquipmentSlotProvider slotProvider : SLOT_PROVIDERS) {
            ItemStack result = slotProvider.tryEquip(entity, stack, allowSwapping);
            if (result != stack) {
                return result;
            }
        }
        return stack;
    }

    private static void playEquipSound(LivingEntity entity, Holder<SoundEvent> equipSound) {
        Vec3 pos = entity.position();
        entity.level().playSound(entity, pos.x, pos.y, pos.z, equipSound, entity.getSoundSource(), 1F, 1F);
    }
}
