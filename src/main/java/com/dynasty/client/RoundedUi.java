package com.dynasty.client;

import net.minecraft.client.gui.GuiGraphics;

/** Rounded geometry in logical GUI pixels; fractional edge coverage avoids coarse cut corners. */
public final class RoundedUi {
    public static void fill(GuiGraphics g, int x, int y, int w, int h, int r, int color) {
        if (w <= 0 || h <= 0) return;
        r = Math.max(0, Math.min(r, Math.min(w, h) / 2));
        if (r == 0) {
            g.fill(x, y, x + w, y + h, color);
            return;
        }
        g.fill(x, y + r, x + w, y + h - r, color);
        for (int row = 0; row < r; row++) {
            // Average coverage at four vertical samples, rather than rounding the circle inward.
            double inset = 0;
            for (int sample = 0; sample < 4; sample++) {
                double dy = r - row - (sample + .5) / 4;
                inset += (r - Math.sqrt(Math.max(0, r * r - dy * dy))) / 4;
            }
            int full = (int) Math.floor(inset);
            int edge = (Math.round((color >>> 24) * (float) (1 - (inset - full))) << 24) | (color & 0xFFFFFF);
            for (int yy : new int[]{y + row, y + h - row - 1}) {
                g.fill(x + full + 1, yy, x + w - full - 1, yy + 1, color);
                g.fill(x + full, yy, x + full + 1, yy + 1, edge);
                g.fill(x + w - full - 1, yy, x + w - full, yy + 1, edge);
            }
        }
    }

    /** Shared jade/bronze menu treatment, including a visible keyboard focus border. */
    static void button(GuiGraphics g, int x, int y, int w, int h, boolean active, boolean focused, boolean primary) {
        int r = Math.min(6, h / 3);
        fill(g, x, y + 2, w, h, r, 0x45030D12);
        fill(g, x, y, w, h, r, !active ? 0x66536A69 : focused ? 0xFFE4C58A : primary ? 0xBCBE9763 : 0x887BA99A);
        fill(g, x + 1, y + 1, w - 2, h - 2, r - 1,
                !active ? 0xF01C3035 : focused ? 0xF03A5C5D : primary ? 0xEF654C37 : 0xE018343C);
        g.fill(x + r + 2, y + 2, x + w - r - 2, y + 3, focused ? 0x557FC2B4 : 0x227FC2B4);
    }

    private RoundedUi() { }
}
