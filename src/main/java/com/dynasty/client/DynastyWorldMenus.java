package com.dynasty.client;

import com.dynasty.Dynasty;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractButton;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.components.Renderable;
import net.minecraft.client.gui.components.TabButton;
import net.minecraft.client.gui.components.tabs.TabNavigationBar;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.worldselection.CreateWorldScreen;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Presentation only: every original input, value, tooltip and narration owner stays in place. */
@Mod.EventBusSubscriber(modid = Dynasty.MODID, value = Dist.CLIENT)
public final class DynastyWorldMenus {
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void beforeRender(ScreenEvent.Render.Pre event) {
        Screen screen = event.getScreen();
        if (!(screen instanceof CreateWorldScreen) || Boolean.getBoolean("dynasty.vanillaMenu")) return;
        restore(screen); // Also recovers if a previous render was interrupted.
        for (int i = 0; i < screen.renderables.size(); i++) {
            Renderable source = screen.renderables.get(i);
            if (source instanceof AbstractButton button) screen.renderables.set(i, new Control(button));
            else if (source instanceof EditBox edit) screen.renderables.set(i, new Input(edit));
            else if (source instanceof TabNavigationBar tabs) screen.renderables.set(i, new Tabs(tabs));
        }
        screen.renderables.add(0, new Backdrop(screen));
    }

    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public static void afterRender(ScreenEvent.Render.Post event) {
        if (event.getScreen() instanceof CreateWorldScreen) restore(event.getScreen());
    }

    // Restore before input is dispatched. TabManager removes the original renderable when a tab
    // changes: retaining a permanent wrapper would leave stale controls drawn over the next tab.
    private static void restore(Screen screen) {
        screen.renderables.removeIf(r -> r instanceof Backdrop);
        for (int i = 0; i < screen.renderables.size(); i++) {
            if (screen.renderables.get(i) instanceof Decoration decoration)
                screen.renderables.set(i, decoration.original());
        }
    }

    private interface Decoration extends Renderable { Renderable original(); }

    private record Control(AbstractButton source) implements Decoration {
        @Override public Renderable original() { return source; }
        @Override public void render(GuiGraphics g, int mx, int my, float partial) {
            hiddenRender(g, source, mx, my, partial);
            if (!source.visible) return;
            String key = DynastyTitleScreen.key(source.getMessage());
            boolean primary = key.equals("selectWorld.create");
            RoundedUi.button(g, source.getX(), source.getY(), source.getWidth(), source.getHeight(),
                    source.active, source.isHoveredOrFocused() && source.active, primary);
            source.renderString(g, Minecraft.getInstance().font, source.active ? 0xFFF6EEDB : 0xFF84918D);
        }
    }

    private record Input(EditBox source) implements Decoration {
        @Override public Renderable original() { return source; }
        @Override public void render(GuiGraphics g, int mx, int my, float partial) {
            if (!source.visible) return;
            int x = source.getX(), y = source.getY(), w = source.getWidth(), h = source.getHeight();
            RoundedUi.fill(g, x, y, w, h, 4, source.isFocused() ? 0xFFE4C58A : 0xFF749F93);
            RoundedUi.fill(g, x + 1, y + 1, w - 2, h - 2, 3, 0xFF0B2027);
            hiddenRender(g, source, mx, my, partial);
            // These two vanilla creation fields are bordered by default. Render their original
            // text/caret with the same inner width and inset, then restore all input geometry.
            source.setBordered(false);
            source.setX(x + 4);
            source.setY(y + (h - 8) / 2);
            source.setWidth(w - 8);
            try { source.renderWidget(g, mx, my, partial); }
            finally {
                source.setX(x);
                source.setY(y);
                source.setWidth(w);
                source.setBordered(true);
            }
        }
    }

    private record Tabs(TabNavigationBar source) implements Decoration {
        @Override public Renderable original() { return source; }
        @Override public void render(GuiGraphics g, int mx, int my, float partial) {
            for (var child : source.children()) {
                if (!(child instanceof TabButton tab)) continue;
                hiddenRender(g, tab, mx, my, partial);
                if (!tab.visible) continue;
                int x = tab.getX() + 2, y = tab.getY() + 3, w = tab.getWidth() - 4, h = tab.getHeight() - 5;
                RoundedUi.fill(g, x, y, w, h, 4,
                        tab.isSelected() ? 0xEE355853 : tab.isHoveredOrFocused() ? 0xCC29464B : 0x88142C34);
                if (tab.isSelected()) g.fill(x + 9, y + h - 2, x + w - 9, y + h - 1, 0xFFE4C58A);
                tab.renderString(g, Minecraft.getInstance().font, tab.isSelected() ? 0xFFF6EEDB : 0xFFB6C8BF);
            }
        }
    }

    private static void hiddenRender(GuiGraphics g, AbstractWidget original, int mx, int my, float partial) {
        // Let vanilla update hover and schedule its real tooltip, while suppressing its square skin.
        g.enableScissor(0, 0, 0, 0);
        try { original.render(g, mx, my, partial); }
        finally { g.disableScissor(); }
    }

    private record Backdrop(Screen screen) implements Renderable {
        @Override public void render(GuiGraphics g, int mx, int my, float partial) {
            int w = screen.width, h = screen.height;
            g.fill(0, 0, w, h, 0xFF081D23);
            int[] size = DynastyTitleScreen.dimensions();
            if (size[0] > 0 && size[1] > 0) {
                float scale = Math.max((float) w / size[0], (float) h / size[1]);
                int dw = (int) Math.ceil(size[0] * scale), dh = (int) Math.ceil(size[1] * scale);
                RenderSystem.enableBlend();
                g.blit(DynastyTitleScreen.BACKGROUND, (w - dw) / 2, (h - dh) / 2,
                        dw, dh, 0, 0, size[0], size[1], size[0], size[1]);
            }
            g.fill(0, 0, w, h, 0x9407141C);
            int cardWidth = Math.min(w - 12, 354), cardX = (w - cardWidth) / 2;
            RoundedUi.fill(g, cardX, 29, cardWidth, Math.max(0, h - 71), 7, 0xE80D252C);
            g.fill(cardX + 12, 30, cardX + cardWidth - 12, 31, 0x7797B4A0);
            g.fill(0, h - 36, w, h, 0xE8081C24);
            g.fill(0, h - 37, w, h - 36, 0x777DAA96);
            if (w >= 530) {
                g.drawString(Minecraft.getInstance().font, "DYNASTY", 12, h - 24, 0xFFDDBE80, false);
                g.fill(12, h - 11, 53, h - 10, 0x777DAA96);
            }
        }
    }

    private DynastyWorldMenus() { }
}
