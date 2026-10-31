package dev.melix.damagenumbers.client.gui;

import dev.melix.damagenumbers.client.config.DamageNumbersConfig;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

final class SavePresetScreen extends Screen {
    private static final int PANEL_WIDTH = 320;
    private static final int PANEL_HEIGHT = 142;

    private final DamageNumbersConfigScreen parent;
    private final String editingId;
    private final String initialName;
    private EditBox nameBox;
    private FlatButton saveButton;

    SavePresetScreen(DamageNumbersConfigScreen parent) {
        this(parent, null, "");
    }

    SavePresetScreen(DamageNumbersConfigScreen parent, String editingId, String initialName) {
        super(Component.translatable(editingId == null
                ? "damage_numbers.save_preset.title" : "damage_numbers.rename_preset.title"));
        this.parent = parent;
        this.editingId = editingId;
        this.initialName = initialName;
    }

    @Override
    protected void init() {
        int left = (width - PANEL_WIDTH) / 2;
        int top = (height - PANEL_HEIGHT) / 2;
        nameBox = new EditBox(font, left + 20, top + 54, PANEL_WIDTH - 40, 22,
                Component.translatable("damage_numbers.save_preset.name"));
        nameBox.setMaxLength(32);
        nameBox.setHint(Component.translatable("damage_numbers.save_preset.name_hint"));
        nameBox.setValue(initialName);
        addRenderableWidget(nameBox);

        saveButton = addRenderableWidget(FlatButton.create(Component.translatable(editingId == null
                                ? "damage_numbers.save_preset.confirm" : "damage_numbers.rename_preset.confirm"),
                        button -> savePreset())
                .bounds(left + 20, top + 98, 132, 22).accent().build());
        addRenderableWidget(FlatButton.create(Component.translatable("gui.cancel"), button -> onClose())
                .bounds(left + PANEL_WIDTH - 152, top + 98, 132, 22).build());
        nameBox.setFocused(true);
        saveButton.active = false;
    }

    @Override
    public void tick() {
        saveButton.active = !nameBox.getValue().trim().isEmpty();
    }

    private void savePreset() {
        String name = nameBox.getValue().trim();
        if (name.isEmpty()) {
            return;
        }
        if (editingId == null) {
            DamageNumbersConfig.get().savePreset(name);
        } else {
            DamageNumbersConfig.get().renamePreset(editingId, name);
        }
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
        graphics.drawCenteredString(font, title, width / 2, top + 17, 0xFFF4F6F8);
        graphics.drawString(font, Component.translatable(editingId == null
                        ? "damage_numbers.save_preset.description" : "damage_numbers.rename_preset.description"),
                left + 20, top + 36, 0xFFA6ADB8, false);
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

