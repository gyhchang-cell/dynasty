package com.dynasty.legacyqa;

import com.google.gson.GsonBuilder;
import com.mojang.brigadier.arguments.StringArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.TagParser;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.storage.LevelResource;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.server.ServerLifecycleHooks;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

/** Observes real native events. It never invokes Clone, changes progress, kills or respawns a player. */
@Mod("dynastylegacyqa")
@Mod.EventBusSubscriber(modid = "dynastylegacyqa")
public final class LegacyNativeQa {
    private static final String SESSION = UUID.randomUUID().toString();
    private static final String CANDIDATE = "e5a78244082214ab5fd76eb35bbb42151e3ec7bd8bc13afee3bc58ea4fe3a669";
    private static final String CONTRACT = "8b75878379fa8740a274b8f63021834af6bbeb2ef25a004997c34ce84dc92a01";
    private static final String FIELDS = "269e730f3106206e6e827f4cf87ac04f889e0ee83d6a89c6dca9b4e524043c61";
    private static Path root, instance, output;
    private static CompoundTag fieldTypes;
    private static String artifact;
    private static Case current;

    public LegacyNativeQa() throws Exception {
        if (!Boolean.getBoolean("dynasty.legacyqa.enabled")) throw new IllegalStateException("Explicit QA opt-in required");
        root = real(requiredPath("root"));
        if (!root.getFileName().toString().equals("cod4-legacy-native-20261102")
                || !root.getParent().getFileName().toString().equals("build")) throw new IllegalStateException("Private build root required");
        instance = real(requiredPath("instance"));
        output = real(requiredPath("output"));
        if (!instance.startsWith(root) || instance.equals(root) || !output.startsWith(root)
                || output.equals(root) || output.startsWith(instance) || instance.startsWith(output)) throw new IllegalStateException("Separate private instance and output required");
        Path contract = real(requiredPath("contract")), fields = real(requiredPath("fields"));
        if (!hash(contract).equals(CONTRACT) || !hash(fields).equals(FIELDS)) throw new IllegalStateException("Audited contract/fixture drift");
        fieldTypes = TagParser.parseTag(Files.readString(fields));
        if (fieldTypes.getAllKeys().size() != 107) throw new IllegalStateException("107-field independent contract required");
        Path dynasty = ModList.get().getModFileById("dynasty").getFile().getFilePath();
        Path qa = ModList.get().getModFileById("dynastylegacyqa").getFile().getFilePath();
        if (!Files.isRegularFile(dynasty) || !hash(dynasty).equals(CANDIDATE) || !Files.isRegularFile(qa)) throw new IllegalStateException("Packed current candidate and QA jars required");
        artifact = hash(qa);
        write("session-" + SESSION + ".json", Map.of("session", SESSION, "pid", ProcessHandle.current().pid(),
                "candidate_sha256", CANDIDATE, "qa_sha256", artifact, "contract_sha256", CONTRACT,
                "fields_sha256", FIELDS, "instance", instance.toString(), "output", output.toString(), "runtime_acceptance", false));
    }

    private static Path requiredPath(String key) {
        Path p = Path.of(Objects.requireNonNull(System.getProperty("dynasty.legacyqa." + key), key));
        if (!p.isAbsolute()) throw new IllegalArgumentException("Absolute " + key + " required");
        return p;
    }

    private static Path real(Path p) throws IOException { return p.toRealPath(); }
    private static String hash(Path p) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(p)));
    }
    private static void write(String name, Object value) throws IOException {
        if (!real(output).equals(output)) throw new IllegalStateException("Output path changed");
        Files.writeString(output.resolve(name), new GsonBuilder().setPrettyPrinting().create().toJson(value) + "\n",
                StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE);
    }
    private static void guard(MinecraftServer server) throws IOException {
        Path expected = real(instance.resolve("saves/legacy-copy"));
        if (!real(server.getWorldPath(LevelResource.ROOT)).equals(expected)) throw new IllegalStateException("Wrong world root");
        if (!expected.startsWith(instance)) throw new IllegalStateException("World symlink escape");
    }
    private static ServerPlayer connected(MinecraftServer s, UUID id) {
        ServerPlayer p = s.getPlayerList().getPlayer(id);
        if (p == null || p instanceof FakePlayer || p.connection == null || p.isRemoved()) throw new IllegalStateException("Live native player required: " + id);
        return p;
    }
    private static Map<String, Object> snapshot(ServerPlayer p) {
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("uuid", p.getUUID().toString()); row.put("entity_id", p.getId());
        row.put("object_identity", System.identityHashCode(p)); row.put("dimension", p.level().dimension().location().toString());
        row.put("native_connection", p.connection != null); row.put("game_time", p.level().getGameTime());
        row.put("persistent", p.getPersistentData().toString());
        row.put("inventory", p.getInventory().save(new ListTag()).toString());
        row.put("full_player", p.saveWithoutId(new CompoundTag()).toString());
        return row;
    }

    @SubscribeEvent public static void commands(RegisterCommandsEvent e) {
        e.getDispatcher().register(Commands.literal("legacyqa").requires(s -> s.hasPermission(2))
                .then(Commands.literal("arm").then(Commands.argument("case", StringArgumentType.word())
                        .then(Commands.argument("peer", StringArgumentType.word()).then(Commands.argument("kind", StringArgumentType.word()).executes(c -> {
                            try {
                                ServerPlayer actor = c.getSource().getPlayerOrException();
                                arm(actor, StringArgumentType.getString(c, "case"), UUID.fromString(StringArgumentType.getString(c, "peer")), StringArgumentType.getString(c, "kind"));
                                c.getSource().sendSuccess(() -> Component.literal("Legacy evidence armed. Native death/C2S respawn or End return must occur independently."), false);
                                return 1;
                            } catch (Exception ex) { throw new IllegalStateException(ex); }
                        }))))));
    }
    private static void arm(ServerPlayer actor, String id, UUID peerId, String kind) throws Exception {
        if (current != null) throw new IllegalStateException("Current case not closed");
        if (!id.matches("[A-Za-z0-9_-]{1,64}") || !(kind.equals("death") || kind.equals("end"))) throw new IllegalArgumentException("Invalid case/kind");
        MinecraftServer s = actor.server; guard(s);
        connected(s, actor.getUUID()); ServerPlayer peer = connected(s, peerId);
        if (actor == peer || actor.getUUID().equals(peerId) || s.getPlayerList().getPlayerCount() != 2) throw new IllegalStateException("Exactly two distinct connected players required");
        if (!actor.isAlive() || !peer.isAlive()) throw new IllegalStateException("Arm only before the native transition");
        if (!s.getGameRules().getBoolean(GameRules.RULE_KEEPINVENTORY)) throw new IllegalStateException("Private keepInventory fixture must already be true; observer will not change it");
        Case next = new Case(id, kind, actor, peer, s.getTickCount());
        Map<String, Object> row = stamp(next); row.put("actor_before", snapshot(actor)); row.put("peer_before", snapshot(peer));
        row.put("present_audited_fields", present(actor.getPersistentData()));
        row.put("missing_audited_fields", missing(actor.getPersistentData()));
        write(id + "-armed.json", row); current = next;
    }
    private static List<String> present(CompoundTag rootTag) {
        return fieldTypes.getAllKeys().stream().sorted().filter(rootTag::contains).toList();
    }
    private static List<String> missing(CompoundTag rootTag) {
        return fieldTypes.getAllKeys().stream().sorted().filter(k -> !rootTag.contains(k)).toList();
    }
    private static Map<String, Object> stamp(Case c) {
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("case", c.id); row.put("nonce", c.nonce); row.put("kind", c.kind); row.put("session", SESSION);
        row.put("pid", ProcessHandle.current().pid()); row.put("qa_sha256", artifact); row.put("candidate_sha256", CANDIDATE);
        row.put("actor_uuid", c.actorId.toString()); row.put("peer_uuid", c.peerId.toString());
        row.put("armed_cycle", c.armed); row.put("native_acceptance", false);
        return row;
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void cloned(PlayerEvent.Clone e) {
        Case c = current;
        if (c == null || !(e.getOriginal() instanceof ServerPlayer oldPlayer) || !(e.getEntity() instanceof ServerPlayer next)) return;
        if (oldPlayer.getUUID().equals(c.peerId)) { fail(c, new IllegalStateException("Unplanned peer Clone during actor case")); return; }
        if (!oldPlayer.getUUID().equals(c.actorId)) return;
        try {
            guard(next.server);
            if (c.cloneCount++ != 0 || oldPlayer != c.original || oldPlayer == next || !next.getUUID().equals(c.actorId)
                    || e.isWasDeath() != c.kind.equals("death")) throw new IllegalStateException("Unexpected native Clone identity/kind/count");
            c.replacement = next; c.cloneCycle = next.server.getTickCount();
            Map<String, Object> row = stamp(c);
            row.put("event", "PlayerEvent.Clone LOWEST observer"); row.put("was_death", e.isWasDeath());
            row.put("old", snapshot(oldPlayer)); row.put("new_at_observer", snapshot(next));
            row.put("audited_observer_comparison", compare(oldPlayer.getPersistentData(), next.getPersistentData()));
            row.put("listener_limit", "LOWEST observes prior listeners, not proof every same-priority/later listener or consumer is finished");
            write(c.id + "-clone.json", row);
        } catch (Exception ex) { fail(c, ex); }
    }
    /** Descriptive comparison, not a production copier or an overall acceptance decision. */
    private static Map<String, Object> compare(CompoundTag before, CompoundTag after) {
        List<String> checked = new ArrayList<>(), absent = new ArrayList<>(), malformed = new ArrayList<>(), differences = new ArrayList<>();
        for (String key : fieldTypes.getAllKeys().stream().sorted().toList()) {
            if (!before.contains(key)) { absent.add(key); continue; }
            boolean pair = key.equals("dynasty_merit_kill_window") || key.equals("dynasty_merit_kill_earned");
            if (!before.contains(key, fieldTypes.get(key).getId()) || key.equals("DynastyXuanniaoBlessing") && !before.hasUUID(key)
                    || pair && !(before.contains("dynasty_merit_kill_window", 4) && before.contains("dynasty_merit_kill_earned", 3))) {
                malformed.add(key); continue;
            }
            checked.add(key);
            boolean aliasTrue = key.startsWith("dynasty_firstkill_") && (before.getBoolean(key)
                    || before.getCompound(Player.PERSISTED_NBT_TAG).contains(key, 1) && before.getCompound(Player.PERSISTED_NBT_TAG).getBoolean(key));
            if (aliasTrue ? !after.contains(key, 1) || !after.getBoolean(key) : !Objects.equals(before.get(key), after.get(key))) differences.add(key);
        }
        // A typed-true nested first kill also repairs absent, false or malformed root aliases.
        List<String> nestedTrue = new ArrayList<>();
        for (String key : fieldTypes.getAllKeys().stream().sorted().filter(k -> k.startsWith("dynasty_firstkill_")).toList()) {
            CompoundTag nested = before.getCompound(Player.PERSISTED_NBT_TAG);
            if (nested.contains(key, 1) && nested.getBoolean(key)) {
                nestedTrue.add(key); if ((!after.contains(key, 1) || !after.getBoolean(key)) && !differences.contains(key)) differences.add(key);
            }
        }
        return Map.of("checked_keys", checked, "absent_root_keys", absent, "malformed_keys_excluded", malformed,
                "nested_true_firstkills", nestedTrue, "differences", differences, "all107_valid_present", checked.size() == 107,
                "overall_acceptance", false);
    }
    @SubscribeEvent public static void loggedIn(PlayerEvent.PlayerLoggedInEvent e) {
        if (current != null && e.getEntity() instanceof ServerPlayer)
            fail(current, new IllegalStateException("Unplanned player login during case: " + e.getEntity().getUUID()));
    }
    @SubscribeEvent public static void loggedOut(PlayerEvent.PlayerLoggedOutEvent e) {
        if (current != null && e.getEntity() instanceof ServerPlayer)
            fail(current, new IllegalStateException("Player logout during case: " + e.getEntity().getUUID()));
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e) {
        if (e.phase != TickEvent.Phase.END || current == null) return;
        Case c = current; MinecraftServer s = ServerLifecycleHooks.getCurrentServer();
        try {
            if (s == null) throw new IllegalStateException("Server disappeared");
            guard(s);
            if (s.getTickCount() - c.armed > 600) throw new IllegalStateException("Native case exceeded600 server ticks");
            if (s.getPlayerList().getPlayerCount() != 2) throw new IllegalStateException("Connected-player count changed");
            if (connected(s, c.peerId) != c.peerOriginal) throw new IllegalStateException("Peer entity binding changed");
            if (c.replacement == null) return;
            ServerPlayer actor = connected(s, c.actorId);
            if (actor != c.replacement) throw new IllegalStateException("Replacement binding changed");
            if (s.getTickCount() - c.cloneCycle < 20) return;
            Map<String, Object> row = stamp(c);
            row.put("status", "CAPTURED_NATIVE_CLONE_PENDING_ANALYSIS"); row.put("clone_count", c.cloneCount);
            row.put("final_cycle", s.getTickCount()); row.put("actor_after20", snapshot(actor)); row.put("peer_after20", snapshot(connected(s, c.peerId)));
            row.put("post_tick_comparison", compare(c.originalRoot, actor.getPersistentData()));
            row.put("peer_root_unchanged", c.peerRoot.equals(connected(s, c.peerId).getPersistentData()));
            row.put("peer_inventory_unchanged", c.peerInventory.equals(connected(s, c.peerId).getInventory().save(new ListTag())));
            row.put("actor_inventory_unchanged", c.actorInventory.equals(actor.getInventory().save(new ListTag())));
            row.put("unproven", List.of("actual C2S origin must be bound independently", "arm-to-event consumer changes require explanation",
                    "snapshot differences are not attributed to this migration handler", "no old-item remap/save/reopen or visual acceptance"));
            write(c.id + "-after20.json", row); current = null;
        } catch (Exception ex) { fail(c, ex); }
    }
    private static void fail(Case c, Exception ex) {
        current = null;
        try { Map<String, Object> row = stamp(c); row.put("status", "CAPTURE_FAILED"); row.put("error", ex.toString()); write(c.id + "-failure-" + UUID.randomUUID() + ".json", row); }
        catch (Exception outputError) { throw new IllegalStateException("Evidence write failure", outputError); }
    }
    private static final class Case {
        final String id, kind, nonce = UUID.randomUUID().toString();
        final UUID actorId, peerId; final ServerPlayer original, peerOriginal;
        final CompoundTag originalRoot, peerRoot;
        final ListTag actorInventory, peerInventory;
        final int armed; int cloneCount, cloneCycle; ServerPlayer replacement;
        Case(String id, String kind, ServerPlayer actor, ServerPlayer peer, int armed) {
            this.id = id; this.kind = kind; this.original = actor; this.peerOriginal = peer; this.actorId = actor.getUUID(); this.peerId = peer.getUUID(); this.armed = armed;
            this.originalRoot = actor.getPersistentData().copy(); this.peerRoot = peer.getPersistentData().copy();
            this.actorInventory = actor.getInventory().save(new ListTag()); this.peerInventory = peer.getInventory().save(new ListTag());
        }
    }
}
