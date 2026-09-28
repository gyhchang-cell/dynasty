package com.dynasty.client;

import com.dynasty.Dynasty;
import com.mojang.blaze3d.platform.NativeImage;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.realmsclient.gui.screens.RealmsNotificationsScreen;
import net.minecraft.SharedConstants;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.Renderable;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.contents.TranslatableContents;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraftforge.client.ForgeHooksClient;
import net.minecraftforge.client.gui.TitleScreenModUpdateIndicator;
import net.minecraftforge.fml.ModList;
import org.lwjgl.glfw.GLFW;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Local artwork and responsive typography around the original Minecraft/Forge menu actions. */
public final class DynastyTitleScreen extends TitleScreen {
    static final ResourceLocation BACKGROUND = new ResourceLocation(Dynasty.MODID, "textures/gui/title/imperial-dawn.png");
    private static final int GOLD = 0xFFE4C58A;
    private static final int PAPER = 0xFFF6EEDB;
    private static volatile int[] backgroundSize;
    private final Map<String, MenuButton> actions = new LinkedHashMap<>();
    private RealmsNotificationsScreen realmsLayer;
    private TitleScreenModUpdateIndicator updateLayer;
    private AbstractWidget copyright;
    private Layout layout;
    private boolean vanillaAppearance;

    @Override
    protected void init() {
        actions.clear();
        super.init();
        // Read existing vanilla layers by type, never obfuscated field names. If an upstream
        // version changes this contract, leave the fully functional original menu intact.
        try {
            realmsLayer = vanillaLayer(RealmsNotificationsScreen.class);
            updateLayer = vanillaLayer(TitleScreenModUpdateIndicator.class);
            vanillaAppearance = false;
        } catch (ReflectiveOperationException | RuntimeException error) {
            vanillaAppearance = true;
            Dynasty.LOGGER.warn("[Dynasty] Keeping the vanilla title screen: menu overlay access unavailable", error);
            return;
        }

        for (var child : new ArrayList<>(children())) {
            if (!(child instanceof Button original)) continue;
            if (original.getMessage().equals(COPYRIGHT_TEXT)) {
                copyright = original;
                continue;
            }
            String key = key(original.getMessage());
            MenuButton decorated = new MenuButton(original, key);
            removeWidget(original);
            addRenderableWidget(decorated);
            actions.put(key, decorated);
        }
        layout = Layout.forSize(width, height);
        arrange();
        // Forge's indicator holds the original Mods button; keep that anchor in sync.
        MenuButton mods = actions.get("fml.menu.mods");
        if (mods != null) mods.syncOriginalBounds();
    }

    private <T> T vanillaLayer(Class<T> type) throws ReflectiveOperationException {
        for (Field field : TitleScreen.class.getDeclaredFields()) {
            if (field.getType() == type) {
                field.setAccessible(true);
                return type.cast(field.get(this));
            }
        }
        throw new NoSuchFieldException(type.getSimpleName());
    }

    private void arrange() {
        int x = layout.x;
        int w = layout.width;
        int y = layout.menuY;
        int gap = layout.gap;
        int half = (w - gap) / 2;
        // Demo mode uses vanilla's play/reset controls and their original enabled state.
        place("menu.singleplayer", x, y, w, layout.buttonHeight);
        place("menu.playdemo", x, y, w, layout.buttonHeight);
        y += layout.buttonHeight + gap;
        place("menu.multiplayer", x, y, w, layout.buttonHeight);
        place("menu.resetdemo", x, y, w, layout.buttonHeight);
        y += layout.buttonHeight + gap;
        place("fml.menu.mods", x, y, half, layout.smallHeight);
        place("menu.options", x + half + gap, y, w - half - gap, layout.smallHeight);
        y += layout.smallHeight + gap;
        place("menu.online", x, y, half, layout.smallHeight);
        place("menu.quit", x + half + gap, y, w - half - gap, layout.smallHeight);
        y += layout.smallHeight + gap;
        place("narrator.button.language", x, y, half, layout.utilityHeight);
        place("narrator.button.accessibility", x + half + gap, y, w - half - gap, layout.utilityHeight);
        if (copyright != null) {
            copyright.setX(Math.max(8, width - copyright.getWidth() - 12));
            copyright.setY(height - 17);
        }
    }

    private void place(String key, int x, int y, int w, int h) {
        MenuButton button = actions.get(key);
        if (button != null) {
            button.setX(x);
            button.setY(y);
            button.setWidth(w);
            button.setHeight(h);
        }
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        if (vanillaAppearance || layout == null) {
            super.render(graphics, mouseX, mouseY, partialTick);
            return;
        }
        renderArtwork(graphics);
        renderLettering(graphics);
        ForgeHooksClient.renderMainMenu(this, graphics, font, width, height, 0xFF000000);
        for (Renderable renderable : renderables) renderable.render(graphics, mouseX, mouseY, partialTick);
        MenuButton realms = actions.get("menu.online");
        if (realms != null && realmsLayer != null) {
            // Vanilla notification icons have a fixed title-layout anchor. Translate that
            // existing layer to the retained Realms button, without another service client.
            int dx = realms.getX() + realms.getWidth() - 20 - (width / 2 + 80);
            int dy = realms.getY() + 2 - (height / 4 + 98);
            graphics.pose().pushPose();
            graphics.pose().translate(dx, dy, 0);
            realmsLayer.render(graphics, mouseX - dx, mouseY - dy, partialTick);
            graphics.pose().popPose();
        }
        if (updateLayer != null) updateLayer.render(graphics, mouseX, mouseY, partialTick);
        // Preserve vanilla's warning on the uncommon 32-bit runtime as well.
        if (!minecraft.is64Bit()) {
            graphics.drawCenteredString(font, Component.translatable("title.32bit.deprecation"), width / 2, 4, PAPER);
        }
    }

    private void renderArtwork(GuiGraphics g) {
        g.fill(0, 0, width, height, 0xFF081D23);
        int[] size = dimensions();
        if (size[0] > 0 && size[1] > 0) {
            float scale = Math.max((float) width / size[0], (float) height / size[1]);
            int drawWidth = (int) Math.ceil(size[0] * scale);
            int drawHeight = (int) Math.ceil(size[1] * scale);
            // Fit without distortion; a slight right bias protects the dragon in narrow windows.
            int x = Math.round((width - drawWidth) * .58F);
            int y = (height - drawHeight) / 2;
            RenderSystem.enableBlend();
            g.blit(BACKGROUND, x, y, drawWidth, drawHeight, 0, 0, size[0], size[1], size[0], size[1]);
        }
        // The gradient stays local to the controls so bright art never hurts text contrast.
        int shadeEnd = Math.min(width, layout.x + layout.width + (layout.compact ? 34 : 90));
        for (int x = 0; x < shadeEnd; x += 3) {
            float t = (float) x / shadeEnd;
            int alpha = Math.round(184 * (1 - t * t));
            g.fill(x, 0, Math.min(x + 3, shadeEnd), height, (alpha << 24) | 0x06171D);
        }
        g.fillGradient(0, height - 70, width, height, 0x00030C13, 0xDC030C13);
        int margin = layout.compact ? 6 : 11;
        g.fill(margin, margin, width - margin, margin + 1, 0x667DAB9A);
        g.fill(margin, height - margin - 1, width - margin, height - margin, 0x665C9385);
        corner(g, margin, margin, 1, 1);
        corner(g, width - margin - 1, margin, -1, 1);
        corner(g, margin, height - margin - 1, 1, -1);
        corner(g, width - margin - 1, height - margin - 1, -1, -1);
    }

    private static void corner(GuiGraphics g, int x, int y, int sx, int sy) {
        int length = 14;
        g.fill(Math.min(x, x + sx * length), y, Math.max(x, x + sx * length) + 1, y + 1, 0xCCDCBB7C);
        g.fill(x, Math.min(y, y + sy * length), x + 1, Math.max(y, y + sy * length) + 1, 0xCCDCBB7C);
    }

    private void renderLettering(GuiGraphics g) {
        int x = layout.x;
        int y = layout.titleY;
        g.drawString(font, Component.translatable("ui.dynasty.title.eyebrow"), x + 1, y, 0xFF93B6AC, false);
        g.pose().pushPose();
        g.pose().translate(x - 1, y + 15, 0);
        g.pose().scale(layout.titleScale, layout.titleScale, 1);
        g.drawString(font, "王朝", 1, 1, 0xFF10242A, false);
        g.drawString(font, "王朝", 0, 0, GOLD, false);
        g.pose().popPose();
        int englishY = y + 15 + Math.round(9 * layout.titleScale) + 3;
        int cursor = x + 2;
        for (char letter : "DYNASTY".toCharArray()) {
            g.drawString(font, String.valueOf(letter), cursor, englishY, PAPER, false);
            cursor += font.width(String.valueOf(letter)) + (layout.compact ? 3 : 5);
        }
        g.fill(x, englishY + 13, x + layout.width, englishY + 14, 0x996C9587);
        if (!layout.compact) {
            g.drawString(font, Component.translatable("ui.dynasty.title.tagline"), x, englishY + 22, 0xFFC9D3C1, false);
        }
        g.drawString(font, Component.translatable("ui.dynasty.title.vanilla_hint"), x, height - 33, 0xFF95A69A, false);
        String version = "DYNASTY " + ModList.get().getModContainerById(Dynasty.MODID)
                .map(mod -> mod.getModInfo().getVersion().toString()).orElse("")
                + "  /  " + SharedConstants.getCurrentVersion().getName();
        if (width >= 570 && height >= 320) {
            int right = width - 25;
            for (int i = 0; i < 4; i++) {
                Component text = Component.translatable("ui.dynasty.title.path_" + (i + 1));
                g.drawString(font, text, right - font.width(text), height - 110 + i * 15, 0xFFE0DECB, true);
            }
            g.drawString(font, version, right - font.width(version), height - 35, 0xFFAEB8AA, true);
        }
    }

    @Override
    public boolean keyPressed(int key, int scanCode, int modifiers) {
        if (key == GLFW.GLFW_KEY_F6) {
            minecraft.setScreen(new DynastyTitleMenu.VanillaTitleScreen());
            return true;
        }
        return super.keyPressed(key, scanCode, modifiers);
    }

    static void invalidateBackground() { backgroundSize = null; }

    static int[] dimensions() {
        if (backgroundSize == null) {
            try (var stream = Minecraft.getInstance().getResourceManager().open(BACKGROUND);
                 NativeImage image = NativeImage.read(stream)) {
                backgroundSize = new int[]{image.getWidth(), image.getHeight()};
            } catch (Exception error) {
                backgroundSize = new int[]{0, 0};
                Dynasty.LOGGER.warn("[Dynasty] Title artwork unavailable; using the local ink background", error);
            }
        }
        return backgroundSize;
    }

    static String key(Component message) {
        return message.getContents() instanceof TranslatableContents translated
                ? translated.getKey() : message.getString();
    }

    List<MenuButton> menuButtons() { return List.copyOf(actions.values()); }
    boolean usesVanillaAppearance() { return vanillaAppearance; }

    record Layout(int x, int width, int titleY, float titleScale, int menuY, int buttonHeight,
                  int smallHeight, int utilityHeight, int gap, boolean compact) {
        static Layout forSize(int width, int height) {
            boolean compact = width < 460 || height < 300;
            int gap = Mth.clamp(height / 85, 4, 7);
            int button = Mth.clamp(height / 20, 20, 29);
            int small = Mth.clamp(button - 3, 18, 25);
            int utility = 18;
            int w = Math.min(width - 32, Mth.clamp(Math.round(width * .29F), 166, 246));
            int x = Mth.clamp(Math.round(width * .075F), 16, 100);
            float titleScale = compact ? 3.8F : Mth.clamp(height / 70F, 4.3F, 7.8F);
            int titleHeight = 15 + Math.round(titleScale * 9) + 3 + (compact ? 22 : 44);
            int menuHeight = button * 2 + small * 2 + utility + gap * 4;
            int titleY = Math.max(12, (height - 37 - titleHeight - menuHeight) / 2);
            return new Layout(x, w, titleY, titleScale, titleY + titleHeight,
                    button, small, utility, gap, compact);
        }
    }

    /** The original button remains the authority for actions, including multiplayer gates. */
    static final class MenuButton extends Button {
        final Button original;
        final String actionKey;

        MenuButton(Button original, String key) {
            super(original.getX(), original.getY(), original.getWidth(), original.getHeight(),
                    shortLabel(original.getMessage(), key), button -> original.onPress(), DEFAULT_NARRATION);
            this.original = original;
            this.actionKey = key;
            active = original.active;
            visible = original.visible;
            setTooltip(original.getTooltip());
        }

        private static Component shortLabel(Component original, String key) {
            return switch (key) {
                case "narrator.button.language" -> Component.translatable("ui.dynasty.title.language");
                case "narrator.button.accessibility" -> Component.translatable("ui.dynasty.title.accessibility");
                default -> original;
            };
        }

        void syncOriginalBounds() {
            original.setX(getX());
            original.setY(getY());
            original.setWidth(getWidth());
            original.setHeight(getHeight());
        }

        @Override
        protected void renderWidget(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
            var font = Minecraft.getInstance().font;
            boolean focus = isHoveredOrFocused() && active;
            boolean primary = actionKey.equals("menu.singleplayer") || actionKey.equals("menu.playdemo");
            boolean utility = actionKey.startsWith("narrator.button.");
            int x = getX(), y = getY(), w = getWidth(), h = getHeight();
            int fill = utility ? (focus ? 0xC02A4547 : 0x7010252B)
                    : primary ? (focus ? 0xF09F3C31 : 0xE57E302A) : (focus ? 0xE3325155 : 0xCB102C32);
            g.fill(x, y, x + w, y + h, fill);
            int line = focus ? 0xFFE1C18C : active ? 0xA49E9875 : 0x80556664;
            g.fill(x, y, x + w, y + 1, line);
            g.fill(x, y + h - 1, x + w, y + h, line);
            g.fill(x, y, x + 1, y + h, line);
            g.fill(x + w - 1, y, x + w, y + h, line);
            if (focus) g.fill(x + 3, y + 3, x + 5, y + h - 3, GOLD);
            int color = active ? (focus ? 0xFFFFF6DD : PAPER) : 0xFF7C8C87;
            // Font fitting prevents long translated labels from escaping half-width buttons.
            float scale = Math.min(1, (float) (w - 16) / Math.max(1, font.width(getMessage())));
            g.pose().pushPose();
            g.pose().translate(x + w / 2F, y + (h - font.lineHeight * scale) / 2F, 0);
            g.pose().scale(scale, scale, 1);
            g.drawString(font, getMessage(), -font.width(getMessage()) / 2, 0, color, false);
            g.pose().popPose();
        }
    }
}
