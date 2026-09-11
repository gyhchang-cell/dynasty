package com.dynasty.client;

import com.dynasty.TrinketMenu;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;

/**
 * 饰品界面（无贴图，纯绘制）/ trinket screen drawn with plain rectangles.
 */
@SuppressWarnings("null")
public class TrinketScreen extends AbstractContainerScreen<TrinketMenu> {

    public TrinketScreen(TrinketMenu menu, Inventory inventory, Component title) {
        super(menu, inventory, title);
        this.imageWidth = 176;
        this.imageHeight = 166;
        this.inventoryLabelY = TrinketMenu.INV_Y - 12;
    }

    @Override
    protected void renderBg(GuiGraphics graphics, float partialTick, int mouseX, int mouseY) {
        int x = this.leftPos;
        int y = this.topPos;
        graphics.fill(x, y, x + this.imageWidth, y + this.imageHeight, 0xF0181018);
        graphics.fill(x + 2, y + 2, x + this.imageWidth - 2, y + 16, 0xFF6B1F1F);
        // 饰品槽底 / trinket slot backgrounds
        for (int i = 0; i < com.dynasty.DynastyTrinkets.SLOTS; i++) {
            int sx = x + TrinketMenu.TRINKET_X - 1 + i * 18;
            int sy = y + TrinketMenu.TRINKET_Y - 1;
            graphics.fill(sx, sy, sx + 18, sy + 18, 0xFF3A2A1A);
            graphics.fill(sx + 1, sy + 1, sx + 17, sy + 17, 0xFF1A1208);
        }
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(graphics);
        super.render(graphics, mouseX, mouseY, partialTick);
        this.renderTooltip(graphics, mouseX, mouseY);
        graphics.drawString(this.font, "§6✦ 饰品 · 百宝妆匣", this.leftPos + 8, this.topPos + 4, 0xFFFFFFFF, true);
    }

    @Override
    protected void renderLabels(GuiGraphics graphics, int mouseX, int mouseY) {
        graphics.drawString(this.font, this.playerInventoryTitle, 8, this.inventoryLabelY, 0xAAAAAA, false);
    }
}
