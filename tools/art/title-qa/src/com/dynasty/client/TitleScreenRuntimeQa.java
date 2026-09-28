package com.dynasty.client;

import com.mojang.blaze3d.pipeline.RenderTarget;
import com.mojang.blaze3d.pipeline.TextureTarget;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.VertexSorting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.client.gui.screens.AccessibilityOnboardingScreen;
import net.minecraft.client.gui.screens.AccessibilityOptionsScreen;
import net.minecraft.client.gui.screens.LanguageSelectScreen;
import net.minecraft.client.gui.screens.OptionsScreen;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.gui.screens.multiplayer.JoinMultiplayerScreen;
import net.minecraft.client.gui.screens.multiplayer.SafetyScreen;
import net.minecraft.client.gui.screens.worldselection.SelectWorldScreen;
import net.minecraft.client.gui.screens.worldselection.CreateWorldScreen;
import net.minecraft.network.chat.Component;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.gui.ModListScreen;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import org.lwjgl.glfw.GLFW;
import org.lwjgl.opengl.GL11;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CompletableFuture;

/** Actual game UI rendering and callback checks in a disposable client, never in the mod jar. */
@Mod.EventBusSubscriber(modid = "dynasty", value = Dist.CLIENT)
public final class TitleScreenRuntimeQa {
    private static final Path OUT = Path.of(System.getProperty("dynasty.titleQa.output", "build/title-screen-qa/results"));
    private static final List<String> RESULTS = new ArrayList<>();
    private static int readyFrames;
    private static boolean ran;
    private static CompletableFuture<Void> languageReload;

    @SubscribeEvent
    public static void frame(TickEvent.RenderTickEvent event) {
        if (!Boolean.getBoolean("dynasty.titleQa") || ran || event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.getOverlay() == null && mc.screen instanceof AccessibilityOnboardingScreen) mc.setScreen(new TitleScreen());
        if (!(mc.screen instanceof TitleScreen) || mc.getOverlay() != null || ++readyFrames < 12) return;
        try {
            // Only this disposable client changes language; the launcher's options are untouched.
            if (languageReload == null && !mc.getLanguageManager().getSelected().equals("zh_cn")) {
                mc.getLanguageManager().setSelected("zh_cn");
                languageReload = mc.reloadResourcePacks();
                return;
            }
            if (languageReload != null) {
                if (!languageReload.isDone()) return;
                languageReload.join();
            }
            ran = true;
            Files.createDirectories(OUT);
            require(mc.level == null, "The QA client has no open world");
            require(mc.screen instanceof DynastyTitleScreen, "ScreenEvent.Opening installed the production title screen");
            int[] art = DynastyTitleScreen.dimensions();
            require(art[0] >= 1000 && art[1] >= 500, "Bundled title artwork loaded: " + art[0] + "x" + art[1]);
            require(!Component.translatable("ui.dynasty.title.path_1").getString().startsWith("ui."), "Menu translations loaded");
            RESULTS.add("Actual Minecraft UI framebuffer captures; no desktop capture and no world was opened.");
            RESULTS.add("GL renderer: " + GL11.glGetString(GL11.GL_RENDERER));
            for (int[] view : new int[][]{{960, 540, 2}, {640, 400, 3}, {427, 240, 2}, {320, 240, 3}, {1280, 720, 2}}) {
                DynastyTitleScreen title = openTitle(mc, view[0], view[1]);
                checkButtons(mc, title, view[0], view[1]);
                capture(mc, title, view[0], view[1], view[2]);
            }
            checkDelegationAndDisabledButtons();
            checkNavigation(mc);
            require(mc.level == null, "All menu checks completed without opening a world");
            var finalTitle = openTitle(mc, 640, 400);
            finalTitle.setFocused(button(finalTitle, "menu.quit"));
            finalTitle.keyPressed(GLFW.GLFW_KEY_ENTER, 0, 0);
            require(!mc.isRunning(), "The actual Quit button stopped the isolated client");
            Files.write(OUT.resolve("PASS.txt"), RESULTS);
        } catch (Throwable error) {
            ran = true;
            try {
                Files.createDirectories(OUT);
                RESULTS.add("FAIL: " + error);
                Files.write(OUT.resolve("FAIL.txt"), RESULTS);
            } catch (Exception ignored) { }
            error.printStackTrace();
            mc.stop();
        }
    }

    private static DynastyTitleScreen openTitle(Minecraft mc, int width, int height) {
        mc.setScreen(new TitleScreen());
        require(mc.screen instanceof DynastyTitleScreen, "Vanilla menu requests receive the Dynasty presentation");
        var title = (DynastyTitleScreen) mc.screen;
        title.resize(mc, width, height);
        require(!title.usesVanillaAppearance(), "Original Realms/Forge overlay layers retained");
        return title;
    }

    private static void checkButtons(Minecraft mc, DynastyTitleScreen title, int width, int height) {
        var baseline = new TitleScreen();
        baseline.init(mc, width, height);
        Set<String> vanilla = new HashSet<>();
        for (var child : baseline.children()) {
            if (child instanceof Button button && !button.getMessage().equals(TitleScreen.COPYRIGHT_TEXT)) {
                vanilla.add(DynastyTitleScreen.key(button.getMessage()));
            }
        }
        Set<String> actual = new HashSet<>();
        List<DynastyTitleScreen.MenuButton> buttons = title.menuButtons();
        for (var button : buttons) {
            actual.add(button.actionKey);
            require(button.active == button.original.active && button.getTooltip() == button.original.getTooltip(),
                    "Original enabled state/tooltip retained: " + button.actionKey);
            require(button.getX() >= 0 && button.getY() >= 0
                            && button.getX() + button.getWidth() <= width && button.getY() + button.getHeight() <= height - 30,
                    width + "x" + height + " button fits: " + button.actionKey);
        }
        require(actual.equals(vanilla), "Every vanilla/Forge action preserved at " + width + "x" + height);
        for (int i = 0; i < buttons.size(); i++) {
            for (int j = i + 1; j < buttons.size(); j++) {
                var a = buttons.get(i);
                var b = buttons.get(j);
                boolean overlap = a.getX() < b.getX() + b.getWidth() && a.getX() + a.getWidth() > b.getX()
                        && a.getY() < b.getY() + b.getHeight() && a.getY() + a.getHeight() > b.getY();
                require(!overlap, "Buttons do not overlap: " + a.actionKey + " / " + b.actionKey);
            }
        }
        Set<Object> reached = new HashSet<>();
        title.setFocused(null);
        for (int i = 0; i < buttons.size() + 3; i++) {
            title.keyPressed(GLFW.GLFW_KEY_TAB, 0, 0);
            reached.add(title.getFocused());
        }
        for (var button : buttons) {
            if (button.active && button.visible) require(reached.contains(button), "Tab reaches " + button.actionKey);
        }
        baseline.removed();
    }

    private static void checkDelegationAndDisabledButtons() {
        int[] calls = {0};
        Button original = Button.builder(Component.translatable("menu.multiplayer"), button -> calls[0]++)
                .bounds(10, 10, 150, 22).tooltip(Tooltip.create(Component.literal("Permission denied"))).build();
        original.active = false;
        var disabled = new DynastyTitleScreen.MenuButton(original, "menu.multiplayer");
        disabled.setFocused(true);
        disabled.mouseClicked(20, 20, 0);
        disabled.keyPressed(GLFW.GLFW_KEY_ENTER, 0, 0);
        require(calls[0] == 0 && disabled.getTooltip() == original.getTooltip(), "Disabled multiplayer cannot activate by mouse or keyboard");
        original.active = true;
        var enabled = new DynastyTitleScreen.MenuButton(original, "menu.multiplayer");
        enabled.setFocused(true);
        enabled.keyPressed(GLFW.GLFW_KEY_ENTER, 0, 0);
        require(calls[0] == 1, "Enter delegates exactly once to the retained original action");
    }

    private static void checkNavigation(Minecraft mc) {
        // These screens can be inspected without joining a server, creating a world, or changing options.
        checkSingleplayer(mc);
        checkDestination(mc, "menu.options", OptionsScreen.class);
        checkDestination(mc, "fml.menu.mods", ModListScreen.class);
        checkDestination(mc, "narrator.button.language", LanguageSelectScreen.class);
        checkDestination(mc, "narrator.button.accessibility", AccessibilityOptionsScreen.class);
        var title = openTitle(mc, 640, 400);
        var multiplayer = button(title, "menu.multiplayer");
        if (multiplayer.active) {
            title.setFocused(multiplayer);
            title.keyPressed(GLFW.GLFW_KEY_ENTER, 0, 0);
            require(mc.screen instanceof JoinMultiplayerScreen || mc.screen instanceof SafetyScreen,
                    "Multiplayer retains its original warning/server selection route");
            mc.screen.onClose();
        } else {
            require(multiplayer.getTooltip() != null, "Multiplayer permission restriction remains explained");
        }
        title = openTitle(mc, 640, 400);
        title.keyPressed(GLFW.GLFW_KEY_F6, 0, 0);
        require(mc.screen instanceof DynastyTitleMenu.VanillaTitleScreen, "F6 opens a functional original title screen");
        require(!(mc.screen instanceof DynastyTitleScreen), "Fallback does not loop into the replacement");
    }

    private static void checkSingleplayer(Minecraft mc) {
        var title = openTitle(mc, 640, 400);
        var singleplayer = button(title, "menu.singleplayer");
        title.mouseClicked(singleplayer.getX() + singleplayer.getWidth() / 2D,
                singleplayer.getY() + singleplayer.getHeight() / 2D, 0);
        // WorldSelectionList.loadLevels intentionally redirects an empty profile to CreateWorldScreen.
        // Verify that real branch without inventing or loading a save just to satisfy the test.
        require(mc.screen instanceof SelectWorldScreen || mc.screen instanceof CreateWorldScreen,
                "Singleplayer opens its real vanilla route: " + mc.screen.getClass().getSimpleName());
        require(mc.level == null, "World-selection/create UI has not opened a world");
        mc.screen.keyPressed(GLFW.GLFW_KEY_ESCAPE, 0, 0);
        require(mc.screen instanceof DynastyTitleScreen, "Escape from singleplayer returns to the themed menu");
    }

    private static void checkDestination(Minecraft mc, String key, Class<? extends Screen> expected) {
        var title = openTitle(mc, 640, 400);
        var button = button(title, key);
        title.mouseClicked(button.getX() + button.getWidth() / 2D, button.getY() + button.getHeight() / 2D, 0);
        require(expected.isInstance(mc.screen), key + " opens " + expected.getSimpleName()
                + " (actual " + mc.screen.getClass().getSimpleName() + ")");
        mc.screen.keyPressed(GLFW.GLFW_KEY_ESCAPE, 0, 0);
        require(mc.screen == title, key + " returns to the same title screen");
    }

    private static DynastyTitleScreen.MenuButton button(DynastyTitleScreen title, String key) {
        return title.menuButtons().stream().filter(button -> button.actionKey.equals(key)).findFirst().orElseThrow();
    }

    private static void capture(Minecraft mc, DynastyTitleScreen title, int width, int height, int scale) throws Exception {
        String name = "title-" + width + "x" + height + "-scale" + scale;
        Matrix4f projection = new Matrix4f(RenderSystem.getProjectionMatrix());
        VertexSorting sorting = RenderSystem.getVertexSorting();
        RenderTarget target = new TextureTarget(width * scale, height * scale, true, Minecraft.ON_OSX);
        var model = RenderSystem.getModelViewStack();
        model.pushPose();
        try {
            target.setClearColor(0, 0, 0, 1);
            target.clear(Minecraft.ON_OSX);
            target.bindWrite(true);
            model.setIdentity();
            model.translate(0, 0, -11000);
            RenderSystem.applyModelViewMatrix();
            RenderSystem.setProjectionMatrix(new Matrix4f().setOrtho(0, width, height, 0, 1000, 21000), VertexSorting.ORTHOGRAPHIC_Z);
            RenderSystem.setShaderColor(1, 1, 1, 1);
            RenderSystem.disableDepthTest();
            RenderSystem.enableBlend();
            RenderSystem.defaultBlendFunc();
            title.setFocused(null);
            GuiGraphics graphics = new GuiGraphics(mc, mc.renderBuffers().bufferSource());
            title.renderWithTooltip(graphics, -100, -100, 0);
            graphics.flush();
            GL11.glFinish();
            require(GL11.glGetError() == GL11.GL_NO_ERROR, name + " has no OpenGL error");
            try (var image = Screenshot.takeScreenshot(target)) {
                int first = image.getPixelRGBA(0, 0);
                long nonBackground = 0;
                for (int y = 0; y < image.getHeight(); y++) for (int x = 0; x < image.getWidth(); x++) {
                    if (image.getPixelRGBA(x, y) != first) nonBackground++;
                }
                require(nonBackground > (long) image.getWidth() * image.getHeight() / 2, name + " contains rendered artwork/UI");
                image.writeToFile(OUT.resolve(name + ".png"));
            }
        } finally {
            model.popPose();
            RenderSystem.applyModelViewMatrix();
            RenderSystem.setProjectionMatrix(projection, sorting);
            RenderSystem.setShaderColor(1, 1, 1, 1);
            target.destroyBuffers();
            mc.getMainRenderTarget().bindWrite(true);
        }
    }

    private static void require(boolean condition, String detail) {
        if (!condition) throw new AssertionError(detail);
        RESULTS.add("PASS: " + detail);
    }
}
