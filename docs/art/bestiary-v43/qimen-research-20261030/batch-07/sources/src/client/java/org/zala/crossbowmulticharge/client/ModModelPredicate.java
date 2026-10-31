package org.zala.crossbowmulticharge.client;

import net.minecraft.client.item.ClampedModelPredicateProvider;
import net.minecraft.client.item.ModelPredicateProviderRegistry;
import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;
import net.minecraft.item.Items;
import net.minecraft.nbt.NbtCompound;
import net.minecraft.nbt.NbtElement;
import net.minecraft.nbt.NbtList;
import net.minecraft.util.Identifier;
import org.zala.crossbowmulticharge.Crossbowmulticharge;

public class ModModelPredicate {
    public static void register(String id, Item item, ClampedModelPredicateProvider provider) {
        Identifier predicateID = new Identifier(id);
        ModelPredicateProviderRegistry.register(item, predicateID, provider);
    }

    public static void initialize() {
        register("firework", Items.CROSSBOW, (itemStack, clientWorld, livingEntity, seed) -> {
            NbtCompound nbtCompound = itemStack.getNbt();
            if (nbtCompound != null && nbtCompound.contains("ChargedProjectiles", NbtElement.LIST_TYPE)) {
                NbtList nbtList = nbtCompound.getList("ChargedProjectiles", NbtElement.COMPOUND_TYPE);
                if (nbtList != null) {
                    return ItemStack.fromNbt(nbtList.getCompound((!nbtList.isEmpty()) ? nbtList.size()-1 : 0)).isOf(Items.FIREWORK_ROCKET) ? 1 : 0;
                }
            }
            return 0;
        });
    }
}
