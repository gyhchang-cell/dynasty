package dev.melix.damagenumbers.client.gui;

import dev.melix.damagenumbers.client.config.DamageNumbersConfig;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

final class DeletePresetScreen extends Screen {
    private static final int PANEL_WIDTH = 320;
    private static final int PANEL_HEIGHT = 118;
    private final DamageNumbersConfigScreen parent;
    private final String presetId;
    private final String presetName;

    DeletePresetScreen(DamageNumbersConfigScreen parent, String presetId, String presetName) {
        super(Component.translatable("damage_numbers.delete_preset.title"));
        this.parent = parent;
        this.presetId = presetId;
        this.presetName = presetName;
    }

    @Override
    protected void init() {
        int left = (width - PANEL_WIDTH) / 2;
        int top = (height - PANEL_HEIGHT) / 2;
        int buttonWidth = (PANEL_WIDTH - 46) / 2;
        addRenderableWidget(FlatButton.create(Component.translatable("gui.cancel"), button -> onClose())
                .bounds(left + 20, top + 76, buttonWidth, 22).build());
        addRenderableWidget(FlatButton.create(Component.translatable("damage_numbers.delete_preset.confirm"),
                        button -> deletePreset())
                .bounds(left + 26 + buttonWidth, top + 76, buttonWidth, 22).accent().build());
    }

    private void deletePreset() {
        DamageNumbersConfig.get().deletePreset(presetId);
        minecraft.setScreen(parent);
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        graphics.fill(0, 0, width, height, 0xE8000000);
        int left = (width - PANEL_WIDTH) / 2;
        int top = (height - PANEL_HEIGHT) / 2;
        graphics.fill(left, top, left + PANEL_WIDTH, top + PANEL_HEIGHT, 0xFF171A20);
        super.render(graphics, mouseX, mouseY, partialTick);
        drawBorder(graphics, left, top, PANEL_WIDTH, PANEL_HEIGHT, 0xFF58A6FF, 2);
        graphics.drawCenteredString(font, title, width / 2, top + 15, 0xFFF4F6F8);
        graphics.drawCenteredString(font, Component.translatable("damage_numbers.delete_preset.description",
                presetName), width / 2, top + 42, 0xFFA6ADB8);
    }

    @Override
    public void onClose() {
        minecraft.setScreen(parent);
    }

    private static void drawBorder(GuiGraphics graphics, int x, int y, int width, int height, int color,
                                   int thickness) {
        graphics.fill(x, y, x + width, y + thickness, color);
        graphics.fill(x, y + height - thickness, x + width, y + height, color);
        graphics.fill(x, y, x + thickness, y + height, color);
        graphics.fill(x + width - thickness, y, x + width, y + height, color);
    }
}
