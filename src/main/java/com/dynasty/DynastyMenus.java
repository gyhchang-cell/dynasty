package com.dynasty;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.common.extensions.IForgeMenuType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.ArrayList;
import java.util.List;

/** 菜单注册（饰品槽）/ menu registry for the trinket pouch. */
@SuppressWarnings("null")
public final class DynastyMenus {

    private DynastyMenus() {
    }

    public static final DeferredRegister<MenuType<?>> MENUS =
            DeferredRegister.create(ForgeRegistries.MENU_TYPES, Dynasty.MODID);

    public static final RegistryObject<MenuType<TrinketMenu>> TRINKET_MENU = MENUS.register("trinkets",
            () -> IForgeMenuType.create((windowId, inventory, data) ->
                    new TrinketMenu(windowId, inventory, read(data))));

    public static void write(FriendlyByteBuf buf, List<ItemStack> items) {
        for (int i = 0; i < DynastyTrinkets.SLOTS; i++) {
            ItemStack stack = i < items.size() ? items.get(i) : ItemStack.EMPTY;
            buf.writeItem(stack);
        }
    }

    public static List<ItemStack> read(FriendlyByteBuf buf) {
        List<ItemStack> items = new ArrayList<>();
        for (int i = 0; i < DynastyTrinkets.SLOTS; i++) {
            items.add(buf.readItem());
        }
        return items;
    }
}
