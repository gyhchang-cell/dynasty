package com.dynasty;

import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;

import java.util.List;

/**
 * 饰品槽菜单：6 个饰品槽 + 玩家背包。关闭时自动写回玩家数据。
 * Trinket menu: six accessory slots plus the player inventory; saved on close.
 */
@SuppressWarnings("null")
public class TrinketMenu extends AbstractContainerMenu {

    public static final int TRINKET_X = 8;
    public static final int TRINKET_Y = 20;
    public static final int INV_Y = 84;
    public static final int HOTBAR_Y = 142;

    private final SimpleContainer container;
    private final Player owner;

    /** 服务端：从玩家数据读取 / server side: loaded from the player's data */
    public TrinketMenu(int windowId, Inventory inventory) {
        this(windowId, inventory, DynastyTrinkets.load(inventory.player));
    }

    public TrinketMenu(int windowId, Inventory inventory, List<ItemStack> items) {
        super(DynastyMenus.TRINKET_MENU.get(), windowId);
        this.owner = inventory.player;
        SimpleContainer simple = new SimpleContainer(DynastyTrinkets.SLOTS);
        for (int i = 0; i < DynastyTrinkets.SLOTS; i++) {
            simple.setItem(i, i < items.size() ? items.get(i) : ItemStack.EMPTY);
        }
        this.container = simple;

        for (int i = 0; i < DynastyTrinkets.SLOTS; i++) {
            this.addSlot(new Slot(simple, i, TRINKET_X + i * 18, TRINKET_Y) {
                @Override
                public boolean mayPlace(ItemStack stack) {
                    return DynastyTrinkets.isAccessory(stack);
                }
            });
        }
        for (int row = 0; row < 3; row++) {
            for (int col = 0; col < 9; col++) {
                this.addSlot(new Slot(inventory, col + row * 9 + 9, 8 + col * 18, INV_Y + row * 18));
            }
        }
        for (int col = 0; col < 9; col++) {
            this.addSlot(new Slot(inventory, col, 8 + col * 18, HOTBAR_Y));
        }
    }

    @Override
    public ItemStack quickMoveStack(Player player, int index) {
        ItemStack copy = ItemStack.EMPTY;
        Slot slot = this.slots.get(index);
        if (slot != null && slot.hasItem()) {
            ItemStack stack = slot.getItem();
            copy = stack.copy();
            if (index < DynastyTrinkets.SLOTS) {
                if (!this.moveItemStackTo(stack, DynastyTrinkets.SLOTS, this.slots.size(), true)) {
                    return ItemStack.EMPTY;
                }
            } else if (DynastyTrinkets.isAccessory(stack)) {
                if (!this.moveItemStackTo(stack, 0, DynastyTrinkets.SLOTS, false)) {
                    return ItemStack.EMPTY;
                }
            } else {
                return ItemStack.EMPTY;
            }
            if (stack.isEmpty()) {
                slot.setByPlayer(ItemStack.EMPTY);
            } else {
                slot.setChanged();
            }
        }
        return copy;
    }

    @Override
    public boolean stillValid(Player player) {
        return true;
    }

    @Override
    public void removed(Player player) {
        super.removed(player);
        if (!player.level().isClientSide()) {
            java.util.List<ItemStack> items = new java.util.ArrayList<>();
            for (int i = 0; i < DynastyTrinkets.SLOTS; i++) {
                items.add(this.container.getItem(i));
            }
            DynastyTrinkets.save(player, items);
        }
    }

    public Player owner() {
        return this.owner;
    }
}
