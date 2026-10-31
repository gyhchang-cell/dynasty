package dev.melix.damagenumbers.client.gui;

import dev.melix.damagenumbers.client.config.DamageNumbersConfig;
import dev.melix.damagenumbers.client.config.DamageNumbersConfig.ColorMode;
import dev.melix.damagenumbers.client.config.DamageNumbersConfig.ColorPaint;
import dev.melix.damagenumbers.client.config.DamageNumbersConfig.Snapshot;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

final class ColorPickerScreen extends Screen {
    private static final int HUE_STEPS = 12;
    private static final int TONE_COLUMNS = 8;
    private static final int TONE_ROWS = 5;
    private static final int ACCENT = 0xFF58A6FF;
    private static final int BORDER = 0xFF555B66;
    private static final int TEXT = 0xFFF4F6F8;
    private static final int MUTED = 0xFFA6ADB8;

    private final DamageNumbersConfigScreen parent;
    private final Target target;
    private final DamageNumbersConfig config = DamageNumbersConfig.get();
    private final List<Swatch> hueSwatches = new ArrayList<>();
    private final List<ToneSwatch> toneSwatches = new ArrayList<>();
    private EditBox hexBox;
    private int selectedColor;
    private float selectedHue;
    private boolean updatingHex;

    ColorPickerScreen(DamageNumbersConfigScreen parent, Target target) {
        super(Component.translatable(target.translationKey));
        this.parent = parent;
        this.target = target;
        Snapshot style = config.snapshot();
        selectedColor = switch (target) {
            case FILL_FIRST -> style.fill().firstArgb();
            case FILL_SECOND -> style.fill().secondArgb();
            case UNDERLAY -> style.border().firstArgb();
        };
        selectedHue = rgbToHue(selectedColor);
    }

    @Override
    protected void init() {
        hueSwatches.clear();
        toneSwatches.clear();
        int left = panelLeft();
        int top = panelTop();
        int innerWidth = panelWidth() - 40;

        int hueY = top + 40;
        int hueGap = 2;
        int hueWidth = (innerWidth - hueGap * (HUE_STEPS - 1)) / HUE_STEPS;
        for (int index = 0; index < HUE_STEPS; index++) {
            float hue = index / (float) HUE_STEPS;
            int x = left + 20 + index * (hueWidth + hueGap);
            int color = hsvToArgb(hue, 0.9F, 1.0F);
            hueSwatches.add(new Swatch(x, hueY, hueWidth, 11, color, hue));
            addRenderableWidget(FlatButton.create(Component.empty(), button -> selectedHue = hue)
                    .bounds(x, hueY, hueWidth, 11).build());
        }

        int toneY = top + 68;
        int toneGap = 2;
        int toneWidth = (innerWidth - toneGap * (TONE_COLUMNS - 1)) / TONE_COLUMNS;
        int toneHeight = 11;
        for (int row = 0; row < TONE_ROWS; row++) {
            float value = 1.0F - row / (float) (TONE_ROWS - 1);
            for (int column = 0; column < TONE_COLUMNS; column++) {
                float saturation = column / (float) (TONE_COLUMNS - 1);
                int x = left + 20 + column * (toneWidth + toneGap);
                int y = toneY + row * (toneHeight + toneGap);
                ToneSwatch swatch = new ToneSwatch(x, y, toneWidth, toneHeight, saturation, value);
                toneSwatches.add(swatch);
                addRenderableWidget(FlatButton.create(Component.empty(), button ->
                                chooseColor(hsvToArgb(selectedHue, saturation, value)))
                        .bounds(x, y, toneWidth, toneHeight).build());
            }
        }

        int previewY = top + 153;
        hexBox = new EditBox(font, left + 92, previewY, panelWidth() - 112, 20,
                Component.translatable("damage_numbers.color_picker.hex"));
        hexBox.setMaxLength(7);
        hexBox.setValue(hex(selectedColor));
        hexBox.setResponder(this::readHex);
        addRenderableWidget(hexBox);

        int buttonY = top + 177;
        int buttonWidth = (panelWidth() - 46) / 2;
        addRenderableWidget(FlatButton.create(Component.translatable("gui.cancel"), button -> onClose())
                .bounds(left + 20, buttonY, buttonWidth, 20).build());
        addRenderableWidget(FlatButton.create(Component.translatable("damage_numbers.color_picker.apply"), button -> applyColor())
                .bounds(left + 26 + buttonWidth, buttonY, buttonWidth, 20).accent().build());
    }

    private void chooseColor(int color) {
        selectedColor = color;
        updatingHex = true;
        hexBox.setValue(hex(color));
        updatingHex = false;
    }

    private void readHex(String value) {
        if (updatingHex) {
            return;
        }
        String normalized = value.startsWith("#") ? value.substring(1) : value;
        if (normalized.length() != 6) {
            return;
        }
        try {
            selectedColor = 0xFF000000 | Integer.parseInt(normalized, 16);
            selectedHue = rgbToHue(selectedColor);
        } catch (NumberFormatException ignored) {
        }
    }

    private void applyColor() {
        Snapshot style = config.snapshot();
        switch (target) {
            case FILL_FIRST -> config.setFill(style.fill().mode() == ColorMode.SOLID
                    ? ColorPaint.solid(selectedColor)
                    : ColorPaint.gradient(selectedColor, style.fill().secondArgb()));
            case FILL_SECOND -> config.setFill(ColorPaint.gradient(style.fill().firstArgb(), selectedColor));
            case UNDERLAY -> config.setUnderlayColor(selectedColor);
        }
        config.save();
        ScreenNavigator.open(minecraft, parent);
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor graphics, int mouseX, int mouseY, float partialTick) {
        graphics.fill(0, 0, width, height, 0xE8000000);
        int left = panelLeft();
        int top = panelTop();
        graphics.fill(left, top, left + panelWidth(), top + 207, 0xFF171A20);
        super.extractRenderState(graphics, mouseX, mouseY, partialTick);

        drawBorder(graphics, left, top, panelWidth(), 207, ACCENT, 2);
        graphics.centeredText(font, title, width / 2, top + 10, TEXT);
        graphics.text(font, Component.translatable("damage_numbers.color_picker.hue"), left + 20,
                top + 27, MUTED, false);
        graphics.text(font, Component.translatable("damage_numbers.color_picker.tone"), left + 20,
                top + 55, MUTED, false);
        for (Swatch swatch : hueSwatches) {
            graphics.fill(swatch.x(), swatch.y(), swatch.x() + swatch.width(), swatch.y() + swatch.height(),
                    swatch.color());
            if (hueDistance(selectedHue, swatch.hue()) < 0.045F) {
                drawBorder(graphics, swatch.x() - 1, swatch.y() - 1, swatch.width() + 2,
                        swatch.height() + 2, 0xFFFFFFFF, 1);
            }
        }
        for (ToneSwatch swatch : toneSwatches) {
            int color = hsvToArgb(selectedHue, swatch.saturation(), swatch.value());
            graphics.fill(swatch.x(), swatch.y(), swatch.x() + swatch.width(), swatch.y() + swatch.height(), color);
            if ((color & 0x00FFFFFF) == (selectedColor & 0x00FFFFFF)) {
                drawBorder(graphics, swatch.x() - 1, swatch.y() - 1, swatch.width() + 2,
                        swatch.height() + 2, 0xFFFFFFFF, 1);
            }
        }

        int previewY = top + 153;
        graphics.text(font, Component.translatable("damage_numbers.color_picker.preview"), left + 20,
                previewY - 10, MUTED, false);
        graphics.fill(left + 20, previewY, left + 78, previewY + 20, selectedColor);
        drawBorder(graphics, left + 20, previewY, 58, 20, BORDER, 1);
    }

    @Override
    public void onClose() {
        ScreenNavigator.open(minecraft, parent);
    }

    private int panelWidth() {
        return Math.min(330, width - 16);
    }

    private int panelLeft() {
        return (width - panelWidth()) / 2;
    }

    private int panelTop() {
        return Math.max(6, (height - 207) / 2);
    }

    private static String hex(int argb) {
        return String.format(Locale.ROOT, "#%06X", argb & 0x00FFFFFF);
    }

    private static float hueDistance(float first, float second) {
        float distance = Math.abs(first - second);
        return Math.min(distance, 1.0F - distance);
    }

    private static float rgbToHue(int argb) {
        float red = (argb >> 16 & 0xFF) / 255.0F;
        float green = (argb >> 8 & 0xFF) / 255.0F;
        float blue = (argb & 0xFF) / 255.0F;
        float max = Math.max(red, Math.max(green, blue));
        float min = Math.min(red, Math.min(green, blue));
        float delta = max - min;
        if (delta <= 1.0E-5F) {
            return 0.0F;
        }
        float hue;
        if (max == red) {
            hue = ((green - blue) / delta) % 6.0F;
        } else if (max == green) {
            hue = (blue - red) / delta + 2.0F;
        } else {
            hue = (red - green) / delta + 4.0F;
        }
        return ((hue / 6.0F) + 1.0F) % 1.0F;
    }

    private static int hsvToArgb(float hue, float saturation, float value) {
        float scaled = ((hue % 1.0F) + 1.0F) % 1.0F * 6.0F;
        int sector = (int) Math.floor(scaled);
        float fraction = scaled - sector;
        float p = value * (1.0F - saturation);
        float q = value * (1.0F - saturation * fraction);
        float t = value * (1.0F - saturation * (1.0F - fraction));
        float red;
        float green;
        float blue;
        switch (sector % 6) {
            case 0 -> { red = value; green = t; blue = p; }
            case 1 -> { red = q; green = value; blue = p; }
            case 2 -> { red = p; green = value; blue = t; }
            case 3 -> { red = p; green = q; blue = value; }
            case 4 -> { red = t; green = p; blue = value; }
            default -> { red = value; green = p; blue = q; }
        }
        return 0xFF000000 | Math.round(red * 255.0F) << 16
                | Math.round(green * 255.0F) << 8 | Math.round(blue * 255.0F);
    }

    private static void drawBorder(GuiGraphicsExtractor graphics, int x, int y, int width, int height, int color,
                                   int thickness) {
        graphics.fill(x, y, x + width, y + thickness, color);
        graphics.fill(x, y + height - thickness, x + width, y + height, color);
        graphics.fill(x, y, x + thickness, y + height, color);
        graphics.fill(x + width - thickness, y, x + width, y + height, color);
    }

    enum Target {
        FILL_FIRST("damage_numbers.color_picker.first"),
        FILL_SECOND("damage_numbers.color_picker.second"),
        UNDERLAY("damage_numbers.color_picker.underlay");

        private final String translationKey;

        Target(String translationKey) {
            this.translationKey = translationKey;
        }
    }

    private record Swatch(int x, int y, int width, int height, int color, float hue) {
    }

    private record ToneSwatch(int x, int y, int width, int height, float saturation, float value) {
    }
}
