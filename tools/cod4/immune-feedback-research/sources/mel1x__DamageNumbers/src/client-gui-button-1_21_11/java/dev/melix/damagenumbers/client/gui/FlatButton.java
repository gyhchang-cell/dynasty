package dev.melix.damagenumbers.client.gui;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.narration.NarrationElementOutput;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.network.chat.Component;

final class FlatButton extends AbstractWidget {
    private final OnPress onPress;
    private final boolean accent;
    private final boolean transparent;

    private FlatButton(int x, int y, int width, int height, Component message, OnPress onPress, boolean accent,
                       boolean transparent) {
        super(x, y, width, height, message);
        this.onPress = onPress;
        this.accent = accent;
        this.transparent = transparent;
    }

    static Builder create(Component message, OnPress onPress) {
        return new Builder(message, onPress);
    }

    @Override
    public void onClick(MouseButtonEvent event, boolean doubleClick) {
        onPress.onPress(this);
    }

    @Override
    protected void renderWidget(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        int background = transparent ? (isHoveredOrFocused() ? 0x332B313B : 0x00000000)
                : !active ? 0xFF14171C
                : accent ? (isHoveredOrFocused() ? 0xFF3D8BD0 : 0xFF2F76B7)
                : isHoveredOrFocused() ? 0xFF2B313B : 0xFF20252D;
        int text = active ? 0xFFF1F4F8 : 0xFF737B86;
        if (background != 0) {
            graphics.fill(getX(), getY(), getRight(), getBottom(), background);
        }
        graphics.drawCenteredString(Minecraft.getInstance().font, getMessage(),
                getX() + getWidth() / 2, getY() + Math.max(1, (getHeight() - 8) / 2), text);
    }

    @Override
    protected void updateWidgetNarration(NarrationElementOutput output) {
        defaultButtonNarrationText(output);
    }

    @FunctionalInterface
    interface OnPress {
        void onPress(FlatButton button);
    }

    static final class Builder {
        private final Component message;
        private final OnPress onPress;
        private int x;
        private int y;
        private int width;
        private int height;
        private boolean accent;
        private boolean transparent;

        private Builder(Component message, OnPress onPress) {
            this.message = message;
            this.onPress = onPress;
        }

        Builder bounds(int x, int y, int width, int height) {
            this.x = x;
            this.y = y;
            this.width = width;
            this.height = height;
            return this;
        }

        Builder accent() {
            this.accent = true;
            return this;
        }

        Builder transparent() {
            this.transparent = true;
            return this;
        }

        FlatButton build() {
            return new FlatButton(x, y, width, height, message, onPress, accent, transparent);
        }
    }
}
