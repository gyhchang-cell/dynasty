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
            if(key.equals("menu.options")) decorated.customAction=()->minecraft.setScreen(new SettingsHub(this));
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
        for (MenuButton button : actions.values()) button.visible=false;
        String[] keys = {minecraft.isDemo()?"menu.playdemo":"menu.singleplayer",minecraft.isDemo()?"menu.resetdemo":"menu.multiplayer","menu.options","menu.quit"};
        for(int i=0;i<keys.length;i++) {
            int offset=i<2?0:12;
            place(keys[i],x+offset,y,w-offset*2,layout.buttonHeight);
            y+=layout.buttonHeight+gap;
        }
        if (copyright != null) {
            copyright.setX(Math.max(8, width - copyright.getWidth() - 12));
            copyright.setY(height - 17);
        }
    }

    private void place(String key, int x, int y, int w, int h) {
        MenuButton button = actions.get(key);
        if (button != null) {
            button.visible = true;
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
        Component wordmark = Component.literal("DYNASTY").withStyle(style -> style.withFont(new ResourceLocation(Dynasty.MODID, "title")));
        float wordScale = Math.min(1.6F, (float) layout.width / Math.max(1, font.width(wordmark)));
        g.pose().pushPose();
        g.pose().translate(x, y + 15, 0);
        g.pose().scale(wordScale, wordScale, 1);
        g.drawString(font, wordmark, 0, 0, GOLD, false);
        g.pose().popPose();
        int ruleY = layout.menuY - 12;
        g.fill(x, ruleY, x + 24, ruleY + 1, GOLD);
        g.fill(x + 29, ruleY, x + layout.width, ruleY + 1, 0x556C9587);
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
            int gap = compact ? 4 : 6;
            int button = compact ? 23 : 27;
            int small = compact ? 19 : 22;
            int utility = 16;
            int w = Math.min(width - 40, Mth.clamp(Math.round(width * .30F), 148, 208));
            int x = Mth.clamp(Math.round(width * .075F), 16, 100);
            int menuHeight = button * 4 + gap * 3;
            int titleHeight = compact ? 62 : 75;
            int titleY = Math.max(12, (height - 42 - titleHeight - menuHeight) / 2);
            return new Layout(x, w, titleY, 1, titleY + titleHeight,
                    button, small, utility, gap, compact);
        }
    }

    private static final class SettingsHub extends net.minecraft.client.gui.screens.Screen {
        final DynastyTitleScreen parent;
        SettingsHub(DynastyTitleScreen p){super(Component.literal("设置与更多"));parent=p;}
        @Override protected void init(){
            int w=Math.min(220,width-40),x=(width-w)/2,y=Math.max(38,(height-176)/2);
            for(String key:List.of("menu.options","fml.menu.mods","menu.online","narrator.button.language","narrator.button.accessibility")){
                MenuButton source=parent.actions.get(key);if(source==null)continue;
                MenuButton b=new MenuButton(source.original,key);b.setX(x);b.setY(y);b.setWidth(w);b.setHeight(24);addRenderableWidget(b);y+=29;
            }
            Button back=Button.builder(Component.literal("返回"),b->onClose()).bounds(x,y,w,20).build();
            addRenderableWidget(new MenuButton(back,"back"));
        }
        @Override public void onClose(){minecraft.setScreen(parent);}
        @Override public void render(GuiGraphics g,int x,int y,float partial){parent.renderArtwork(g);RoundedUi.fill(g,width/2-126,12,252,height-24,14,0xDA10282E);g.drawCenteredString(font,title,width/2,21,PAPER);super.render(g,x,y,partial);}
    }

    /** The original button remains the authority for actions, including multiplayer gates. */
    static final class MenuButton extends Button {
        final Button original;
        final String actionKey;
        Runnable customAction;
        @Override public void onPress(){if(customAction!=null)customAction.run();else super.onPress();}

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

            RoundedUi.fill(g,x,y+2,w,h,h/2,0x35000000);
            RoundedUi.fill(g,x,y,w,h,h/2,focus?0xDD476769:primary?0xCF72503C:0xAA18353D);
            if(focus) RoundedUi.fill(g,x+10,y+3,w-20,1,0,0x7799CBC8);
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
