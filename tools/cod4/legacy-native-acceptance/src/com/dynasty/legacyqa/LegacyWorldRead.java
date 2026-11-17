package com.dynasty.legacyqa;

import com.google.gson.GsonBuilder;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.AccessibilityOnboardingScreen;
import net.minecraft.client.gui.screens.BackupConfirmScreen;
import net.minecraft.client.gui.screens.ConfirmScreen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.network.chat.CommonComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.storage.LevelResource;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import org.lwjgl.glfw.GLFW;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

/** One opt-in old-world read/save session; no fixture grants, Clone, death or player input. */
@Mod.EventBusSubscriber(modid = "dynastylegacyqa", value = Dist.CLIENT)
public final class LegacyWorldRead {
    private static final String SESSION = UUID.randomUUID().toString();
    private static boolean done, started, trusted, announced;
    private static long deadline;
    private static int worldTicks;
    private static Path instance, output;
    private static CompletableFuture<Map<String, Object>> future;

    private static String hash(Path p) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(p)));
    }
    private static void write(String suffix, Object row) throws Exception {
        Files.writeString(output.resolve("world-read-" + SESSION + "-" + suffix + ".json"),
                new GsonBuilder().setPrettyPrinting().create().toJson(row) + "\n", StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE);
    }
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e) {
        if (done || e.phase != TickEvent.Phase.END || !Boolean.getBoolean("dynasty.legacyqa.worldRead")) return;
        Minecraft mc = Minecraft.getInstance();
        try {
            if (!trusted) {
                instance = Path.of(System.getProperty("dynasty.legacyqa.instance")).toRealPath();
                output = Path.of(System.getProperty("dynasty.legacyqa.output")).toRealPath();
                Path root = Path.of(System.getProperty("dynasty.legacyqa.root")).toRealPath();
                if (!root.getFileName().toString().equals("cod4-legacy-native-20261102") || !root.getParent().getFileName().toString().equals("build")
                        || !instance.startsWith(root) || !output.startsWith(root) || instance.equals(root) || output.equals(root)
                        || instance.startsWith(output) || output.startsWith(instance)
                        || !mc.gameDirectory.toPath().toRealPath().equals(instance)) throw new IllegalStateException("Private client directory binding failed");
                trusted = true; deadline = System.nanoTime() + 240_000_000_000L;
            }
            long window = mc.getWindow().getWindow();
            if (GLFW.glfwGetWindowAttrib(window, GLFW.GLFW_VISIBLE) != GLFW.GLFW_FALSE
                    || GLFW.glfwGetWindowAttrib(window, GLFW.GLFW_FOCUSED) != GLFW.GLFW_FALSE)
                throw new IllegalStateException("Native window is not hidden and unfocused; no world entry allowed");
            if (!announced) {
                Files.writeString(output.resolve("controller-start.json"), new GsonBuilder().create().toJson(
                        Map.of("session", SESSION, "pid", ProcessHandle.current().pid(), "instance", instance.toString(),
                                "world_loaded", false, "acceptance", false)) + "\n", StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE);
                announced = true;
            }
            if (Files.exists(output.resolve("stop-client.txt"))) {
                write("stopped", Map.of("external_normal_stop_requested", true, "native_acceptance", false));
                done = true; mc.stop(); return;
            }
            if (System.nanoTime() > deadline) throw new IllegalStateException("World-read240s timeout; screen=" + mc.screen);
            if (!started && (mc.screen instanceof TitleScreen || mc.screen instanceof AccessibilityOnboardingScreen)) {
                Path world = instance.resolve("saves/legacy-copy");
                if (!world.toRealPath().equals(world) || !Files.isRegularFile(world.resolve("level.dat"))) throw new IllegalStateException("Existing canonical owned old-world copy required");
                started = true;
                mc.createWorldOpenFlows().loadLevel(new TitleScreen(), "legacy-copy");
                return;
            }
            if (!started) return;
            if (mc.screen instanceof BackupConfirmScreen screen) {
                for (var child : screen.children()) if (child instanceof Button b && b.active
                        && b.getMessage().getString().equals(Component.translatable("selectWorld.backupJoinSkipButton").getString())) { b.onPress(); return; }
            }
            if (mc.screen instanceof ConfirmScreen screen && (screen.getTitle().getString().equals(Component.translatable("selectWorld.warning.experimental.title").getString())
                    || screen.getTitle().getString().equals(Component.translatable("selectWorld.backupQuestion.experimental").getString()))) {
                for (var child : screen.children()) if (child instanceof Button b && b.active && (b.getMessage().getString().equals(CommonComponents.GUI_PROCEED.getString())
                        || b.getMessage().getString().equals(CommonComponents.GUI_YES.getString()))) { b.onPress(); return; }
            }
            if (mc.level == null || mc.player == null || mc.screen != null || ++worldTicks < 100) return;
            if (future == null) {
                var server = mc.getSingleplayerServer();
                if (server == null) throw new IllegalStateException("Owned integrated server required");
                UUID uuid = mc.player.getUUID();
                if (!uuid.equals(UUID.fromString("380df991-f603-344c-a090-369bad2a924a"))) throw new IllegalStateException("Actual historical owner UUID required");
                future = server.submit(() -> {
                    try {
                        if (!server.getWorldPath(LevelResource.ROOT).toRealPath().equals(instance.resolve("saves/legacy-copy"))) throw new IllegalStateException("Actual world-root binding failed");
                        var player = server.getPlayerList().getPlayer(uuid);
                        if (server.getPlayerList().getPlayerCount() != 1 || player == null || player.connection == null) throw new IllegalStateException("Single connected historical owner required");
                        Map<String, Object> row = new LinkedHashMap<>();
                        row.put("session", SESSION); row.put("pid", ProcessHandle.current().pid()); row.put("uuid", uuid.toString());
                        row.put("game_time", player.level().getGameTime()); row.put("world", server.getWorldPath(LevelResource.ROOT).toRealPath().toString());
                        row.put("native_connection", true); row.put("inventory_snbt", player.getInventory().save(new ListTag()).toString());
                        row.put("forge_data_snbt", player.getPersistentData().toString()); row.put("full_player_snbt", player.saveWithoutId(new CompoundTag()).toString());
                        var aliases = new ArrayList<Object>();
                        for (String key : new String[]{"dynasty:quest_ledger", "dynasty:healing_talisman"}) {
                            var item = ForgeRegistries.ITEMS.getValue(new ResourceLocation(key));
                            aliases.add(Map.of("old_name", key, "resolved_canonical", String.valueOf(item == null ? null : ForgeRegistries.ITEMS.getKey(item))));
                        }
                        row.put("active_alias_lookups", aliases);
                        row.put("candidate_sha256", hash(ModList.get().getModFileById("dynasty").getFile().getFilePath()));
                        row.put("qa_sha256", hash(ModList.get().getModFileById("dynastylegacyqa").getFile().getFilePath()));
                        row.put("status", "NATIVE_WORLD_READ_CAPTURED_COMPARISON_AND_SAVE_REOPEN_PENDING"); row.put("native_acceptance", false);
                        return row;
                    } catch (Exception ex) { throw new IllegalStateException(ex); }
                });
                return;
            }
            if (!future.isDone()) return;
            var result = future.join();
            result.put("client_game_time", mc.level.getGameTime()); result.put("client_uuid", mc.player.getUUID().toString());
            result.put("window_visible", false); result.put("window_focused", false);
            write("capture", result); done = true; mc.stop();
        } catch (Throwable ex) {
            done = true;
            if (trusted) {
                try { write("failure", Map.of("error", ex.toString(), "native_acceptance", false)); }
                catch (Exception outputFailure) { ex.addSuppressed(outputFailure); }
                // The real game directory was already bound before stopping this owned instance.
                mc.stop();
            }
            ex.printStackTrace();
        }
    }
}
