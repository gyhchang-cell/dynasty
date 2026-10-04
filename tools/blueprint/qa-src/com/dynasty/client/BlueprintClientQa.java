package com.dynasty.client;

import com.dynasty.blueprint.BlueprintEntities;
import com.dynasty.blueprint.TemplateMob;
import com.dynasty.blueprint.TemplateSkills;
import com.dynasty.blueprint.TemplateProjectile;
import com.dynasty.blueprint.combat.AttackState;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.AccessibilityOnboardingScreen;
import net.minecraft.client.gui.screens.ConnectScreen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.LevelSettings;
import net.minecraft.world.level.WorldDataConfiguration;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.Map;
import java.util.LinkedHashMap;
import java.util.concurrent.CompletableFuture;

/** Opt-in disposable QA source set. Output is observed state, never a substitute for a manual visual review. */
@Mod.EventBusSubscriber(modid="dynasty", value=Dist.CLIENT)
public final class BlueprintClientQa {
    private static final String ROLE = System.getProperty("dynasty.blueprintQa", "");
    private static final String RUN = System.getProperty("dynasty.blueprintQa.run", "unset");
    private static final boolean HOST = ROLE.equals("host"), SOLO = Boolean.getBoolean("dynasty.blueprintQa.solo");
    private static final boolean CONNECTION_ONLY = Boolean.getBoolean("dynasty.blueprintQa.connectionOnly");
    private static final boolean DEATH_ONLY = Boolean.getBoolean("dynasty.blueprintQa.deathOnly");
    private static final Path ROOT = Path.of(System.getProperty("dynasty.blueprintQa.output", "build/blueprint-client/results"));
    private static final Path OUT = ROOT.resolve(ROLE), COORD = ROOT.resolve("coord");
    private static final Gson JSON = new GsonBuilder().setPrettyPrinting().create();
    private static final Gson LINE_JSON = new Gson();
    private static final long DEADLINE = System.nanoTime() + 1_200_000_000_000L;
    private static final String[] NAMES = {"overview-front", "overview-side", "overview-45", "zuwu-front", "ludun-front", "fufa-front", "shanxiao-front",
            "sword-combo", "shield-combo", "possession-link", "shanxiao-pounce", "talisman-volley", "shanxiao-rock", "shield-death-cover",
            "sword-death-mid", "sword-death-planted", "priest-death-mid", "priest-death-empty-robe", "shanxiao-death-mid", "shanxiao-death-curled-faded",
            "autonomous-wall-climb", "autonomous-summit-rock"};
    private record Expected(int entityId, String uuid, String id, int skill, long start) { }
    private record Stage(String run, int index, String phase, long published, List<Expected> mobs) { }
    private record WallPlane(String towardWall, double coordinate, int x, int y, int z) { }
    private record Rock(int entityId, String uuid, double[] position) { }
    private record EncounterSample(String run, long tick, int entityId, String uuid, double initialY, double peakY,
            boolean noAi, boolean noGravity, boolean onGround, boolean horizontalCollision, boolean climbing,
            String climbFace, long climbStart, float contactDistance, int skill, long skillStart, String phase,
            double[] position, double[] velocity, WallPlane wall, List<Rock> rocks) { }
    private static final String[] CONTACT_BONES = {"left_claw_contact", "right_claw_contact", "left_foot_contact", "right_foot_contact"};
    private static boolean started, done, captured, readySent;
    private static int settled, observed = -1, hostIndex = -1;
    private static int connectedTicks;
    private static long connectionStarted, nextDiagnostic;
    private static String diagnosticState = "";
    private static Stage local;
    private static CompletableFuture<Stage> pending;
    private static CompletableFuture<Void> setup;
    private static final List<TemplateMob> fixtures = new ArrayList<>(); // Accessed on integrated server thread only.
    private static Cow target;
    private static final List<String> LOG = new ArrayList<>();
    private static boolean encounterActive; // Server thread only, never used to control the subject's AI.
    private static double encounterInitialY, encounterPeakY;
    private static final List<EncounterSample> serverEncounterWindow = new ArrayList<>();
    private static List<EncounterSample> clientEncounterWindow = List.of();
    private static volatile String encounterFailure;
    private static int trackingFrames;
    private static long lastClimbCandidateTick = Long.MIN_VALUE;
    private static String lastClimbCandidate = "No real climb frame observed";
    private static int rejectedClimbFrames;
    private static long lastSecondaryTick = Long.MIN_VALUE;
    private static double secondaryResponse;

    /** Read-only server telemetry. The sole encounter stimulus is setTarget in activate(20). */
    @SubscribeEvent public static void serverTick(TickEvent.ServerTickEvent event) {
        if (!HOST || !encounterActive || event.phase != TickEvent.Phase.END || fixtures.size() != 4) return;
        try {
            TemplateMob beast = fixtures.get(3);
            if (!(beast.level() instanceof net.minecraft.server.level.ServerLevel world) || beast.isRemoved())
                throw new AssertionError("Autonomous encounter subject disappeared");
            if (beast.isNoAi() || beast.isNoGravity()) throw new AssertionError("Autonomous encounter disabled AI/gravity");
            encounterPeakY = Math.max(encounterPeakY, beast.getY());
            Direction face = beast.climbFace();
            List<Rock> rocks = world.getEntitiesOfClass(TemplateProjectile.class, beast.getBoundingBox().inflate(32),
                    p -> p.isRock() && p.getOwner() == beast).stream()
                    .map(p -> new Rock(p.getId(), p.getUUID().toString(), xyz(p.position()))).toList();
            EncounterSample sample = new EncounterSample(RUN, world.getGameTime(), beast.getId(), beast.getUUID().toString(),
                    encounterInitialY, encounterPeakY, beast.isNoAi(), beast.isNoGravity(), beast.onGround(),
                    beast.horizontalCollision, beast.onClimbable(), face == null ? null : face.getName(),
                    beast.climbStartTime(), beast.climbContactDistance(), beast.skillId(), beast.skillStartTime(),
                    beast.skillPhase().name(), xyz(beast.position()), xyz(beast.getDeltaMovement()), wallPlane(beast, face), rocks);
            serverEncounterWindow.add(sample);
            while (serverEncounterWindow.size() > 16) serverEncounterWindow.remove(0);
            Files.writeString(COORD.resolve("encounter-trace.jsonl"), LINE_JSON.toJson(sample) + "\n",
                    java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND);
            Path temporary = COORD.resolve("encounter-window-next.json");
            Files.writeString(temporary, JSON.toJson(serverEncounterWindow));
            Files.move(temporary, COORD.resolve("encounter-window.json"), StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
        } catch (Throwable error) { encounterFailure = "Autonomous server telemetry failed: " + error; }
    }

    private static double[] xyz(Vec3 value) { return new double[] {value.x, value.y, value.z}; }
    private static WallPlane wallPlane(TemplateMob beast, Direction toward) {
        if (toward == null || toward.getAxis() == Direction.Axis.Y) return null;
        double reach = beast.getBbWidth() / 2D + .35;
        for (double dy : new double[] {.5, 1, 0}) {
            BlockPos block = BlockPos.containing(beast.getX() + toward.getStepX() * reach, beast.getY() + dy,
                    beast.getZ() + toward.getStepZ() * reach);
            var shape = beast.level().getBlockState(block).getCollisionShape(beast.level(), block);
            if (shape.isEmpty()) continue;
            AABB box = shape.bounds().move(block);
            if (!box.intersects(beast.getBoundingBox().inflate(.4, .02, .4))) continue;
            double plane = switch (toward) {
                case EAST -> box.minX; case WEST -> box.maxX;
                case SOUTH -> box.minZ; case NORTH -> box.maxZ;
                default -> throw new AssertionError("Vertical climb face");
            };
            return new WallPlane(toward.getName(), plane, block.getX(), block.getY(), block.getZ());
        }
        return null;
    }

    private static void enableContactTracking(Minecraft mc) {
        TemplateMob beast = (TemplateMob) mc.level.getEntity(local.mobs.get(3).entityId);
        if (!(mc.getEntityRenderDispatcher().getRenderer(beast) instanceof com.dynasty.blueprint.client.TemplateMobRenderer renderer))
            throw new AssertionError("Autonomous beast has no real template renderer");
        boolean allPresent = true;
        for (String name : List.of("root", "left_claw_contact", "right_claw_contact", "left_foot_contact", "right_foot_contact")) {
            var bone = renderer.getGeoModel().getBone(name);
            if (bone.isEmpty()) allPresent = false;
            else bone.get().setTrackingMatrices(true);
        }
        if (allPresent) trackingFrames++;
        else if (readySent) throw new AssertionError("Missing climb contact bones after both-client tracking readiness");
    }

    private static boolean observeEncounter(Minecraft mc) throws Exception {
        if (mc.level.getGameTime() - local.published > 600)
            throw new AssertionError("Autonomous encounter timed out without its real event: " + NAMES[observed] + "; " + lastClimbCandidate);
        TemplateMob beast = (TemplateMob) mc.level.getEntity(local.mobs.get(3).entityId);
        if (beast.isNoAi() || beast.isNoGravity()) throw new AssertionError("Client observed disabled autonomous AI/gravity");
        EncounterSample server = null;
        for (EncounterSample sample : clientEncounterWindow) {
            if (!RUN.equals(sample.run) || !sample.uuid.equals(beast.getUUID().toString()))
                throw new AssertionError("Autonomous telemetry belongs to another run/entity");
            if (Math.abs(sample.tick - mc.level.getGameTime()) <= 3 && sample.skill == beast.skillId()
                    && sample.skillStart == beast.skillStartTime()
                    && (server == null || Math.abs(sample.tick - mc.level.getGameTime()) < Math.abs(server.tick - mc.level.getGameTime())))
                server = sample;
        }
        if (server == null || trackingFrames < 2) return false;
        if (server.noAi || server.noGravity) throw new AssertionError("Server trace disabled ordinary subject physics");
        if (beast.position().distanceTo(new Vec3(server.position[0], server.position[1], server.position[2])) > .8) return false;
        Map<String, Object> evidence = new LinkedHashMap<>();
        evidence.put("formatVersion", 1); evidence.put("run", RUN); evidence.put("role", ROLE); evidence.put("stage", observed);
        evidence.put("clientTick", mc.level.getGameTime()); evidence.put("serverTick", server.tick);
        evidence.put("uuid", beast.getUUID().toString()); evidence.put("server", server);
        evidence.put("clientPosition", xyz(beast.position())); evidence.put("clientSkill", beast.skillId());
        evidence.put("clientStart", beast.skillStartTime()); evidence.put("clientClimbStart", beast.climbStartTime());
        evidence.put("clientClimbContactDistance", beast.climbContactDistance());
        var renderer = (com.dynasty.blueprint.client.TemplateMobRenderer) mc.getEntityRenderDispatcher().getRenderer(beast);
        var controller = beast.getAnimatableInstanceCache().getManagerForId(beast.getId()).getAnimationControllers().get("body");
        String clip = controller == null || controller.getCurrentAnimation() == null ? "none" : controller.getCurrentAnimation().animation().name();
        evidence.put("clip", clip);
        if (observed == 20) {
            if (server.peakY >= server.initialY + 2.5 && server.onGround && !server.climbing)
                throw new AssertionError("Subject reached summit before a physically valid climb capture: " + lastClimbCandidate);
            if (!server.climbing || !server.horizontalCollision || server.onGround || server.velocity[1] <= .01
                    || server.position[1] <= server.initialY + .4 || server.skill != 0 || server.wall == null
                    || !beast.onClimbable() || beast.onGround() || beast.climbFace() == null) return false;
            if (!beast.climbFace().getName().equals(server.climbFace) || beast.climbStartTime() != server.climbStart) return false;
            Direction toward = beast.climbFace();
            if (!toward.getName().equals(server.wall.towardWall)) throw new AssertionError("Reported wall plane disagrees with real climb face");
            Map<String, Object> contacts = new LinkedHashMap<>();
            int stance = 0; boolean geometryValid = clip.equals("animation.shanjing_shanxiao.climb");
            for (String name : CONTACT_BONES) {
                var bone = renderer.getGeoModel().getBone(name).orElseThrow(() -> new AssertionError("Missing contact bone " + name));
                var point = bone.getWorldPosition();
                if (!Double.isFinite(point.x) || !Double.isFinite(point.y) || !Double.isFinite(point.z))
                    throw new AssertionError("Nonfinite world-space contact " + name);
                double coordinate = toward.getAxis() == Direction.Axis.X ? point.x : point.z;
                double distance = (server.wall.coordinate - coordinate) * (toward.getAxis() == Direction.Axis.X ? toward.getStepX() : toward.getStepZ());
                Vec3 inside = toward.getAxis() == Direction.Axis.X
                        ? new Vec3(server.wall.coordinate + toward.getStepX() * .01, point.y, point.z)
                        : new Vec3(point.x, point.y, server.wall.coordinate + toward.getStepZ() * .01);
                BlockPos contactBlock = BlockPos.containing(inside);
                boolean onRealWall = !mc.level.getBlockState(contactBlock).getCollisionShape(mc.level, contactBlock).isEmpty();
                contacts.put(name, Map.of("worldPosition", new double[] {point.x, point.y, point.z}, "planeDistance", distance,
                        "projectsOntoSolidWall", onRealWall));
                geometryValid &= distance >= -.04 && distance <= .16 && onRealWall;
                if (distance >= -.04 && distance <= .06 && onRealWall) stance++;
            }
            var root = renderer.getGeoModel().getBone("root").orElseThrow();
            // GeckoLib 4.8 RenderUtils.translateMatrix ADDS a translation matrix twice
            // (local offset, then entity position), also adding 2 to the diagonal.
            // Keep world positions untouched; recover the linear part for direction tests.
            var orientation = new org.joml.Matrix4f(root.getWorldSpaceMatrix());
            orientation.m00(orientation.m00()-2).m11(orientation.m11()-2).m22(orientation.m22()-2);
            var outward = orientation.transformDirection(new org.joml.Vector3f(0, 1, 0)).normalize();
            var upward = orientation.transformDirection(new org.joml.Vector3f(0, 0, -1)).normalize();
            float awayDot = outward.dot(-toward.getStepX(), 0, -toward.getStepZ()), upDot = upward.y;
            geometryValid &= stance >= 2 && awayDot >= .9F && upDot >= .9F;
            evidence.put("clientClimbFace", toward.getName()); evidence.put("contacts", contacts);
            evidence.put("stanceContacts", stance); evidence.put("rootAwayDot", awayDot); evidence.put("rootUpDot", upDot);
            evidence.put("geometryValid", geometryValid);
            lastClimbCandidate = LINE_JSON.toJson(evidence);
            if (lastClimbCandidateTick != mc.level.getGameTime()) {
                lastClimbCandidateTick = mc.level.getGameTime();
                Files.writeString(OUT.resolve("20-climb-candidates.jsonl"), lastClimbCandidate + "\n",
                        java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND);
                if (!geometryValid && rejectedClimbFrames < 3) {
                    Path diagnostic = OUT.resolve("diagnostics"); Files.createDirectories(diagnostic);
                    try (var rejected = Screenshot.takeScreenshot(mc.getMainRenderTarget())) {
                        rejected.writeToFile(diagnostic.resolve("climb-rejected-" + rejectedClimbFrames++ + ".png"));
                    }
                }
            }
            if (!geometryValid) return false;
        } else {
            if (server.peakY < server.initialY + 2 || server.position[1] < server.initialY + 2
                    || server.skill != TemplateSkills.ROCK_THROW || !server.onGround || server.rocks.isEmpty()
                    || !clip.equals("animation.shanjing_shanxiao.rock")) return false;
            List<String> visibleRocks = mc.level.getEntitiesOfClass(TemplateProjectile.class, beast.getBoundingBox().inflate(32),
                    p -> p.isRock() && p.getOwner() != null && p.getOwner().getUUID().equals(beast.getUUID())).stream()
                    .map(p -> p.getUUID().toString()).filter(id -> serverRockMatches(clientEncounterWindow, id)).toList();
            if (visibleRocks.isEmpty()) return false;
            evidence.put("visibleRockUuids", visibleRocks);
            if (Math.abs(beast.actionAge(0) - (mc.level.getGameTime() - server.skillStart) * beast.skillSpeed()) > .01)
                throw new AssertionError("Autonomous rock animation clock differs from real AI start");
        }
        for (Expected expected : local.mobs) {
            TemplateMob mob = (TemplateMob) mc.level.getEntity(expected.entityId);
            LOG.add(NAMES[observed] + " entity=" + expected.id + " uuid=" + expected.uuid + " skill=" + mob.skillId()
                    + " phase=" + mob.skillPhase() + " start=" + mob.skillStartTime() + " clientTime=" + mc.level.getGameTime() + " actionAge=" + mob.actionAge(0));
            observeAnimation(mc, mob, mob == beast);
        }
        Files.writeString(OUT.resolve(String.format("%02d-encounter.json", observed)), JSON.toJson(evidence));
        LOG.add("Encounter " + LINE_JSON.toJson(evidence));
        return true;
    }

    private static boolean serverRockMatches(List<EncounterSample> samples, String uuid) {
        return samples.stream().anyMatch(s -> s.rocks.stream().anyMatch(r -> r.uuid.equals(uuid)));
    }

    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event) {
        if (ROLE.isEmpty() || done || event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        try {
            diagnose(mc);
            if (encounterFailure != null) throw new AssertionError(encounterFailure);
            if (System.nanoTime() > DEADLINE) throw new AssertionError("QA timed out waiting for world, peer or acknowledged stage");
            if (Files.exists(ROOT.resolve(HOST ? "peer/FAIL.txt" : "host/FAIL.txt"))) throw new AssertionError("Other client failed; see its FAIL.txt");
            if (mc.getOverlay() != null) return;
            if (mc.screen instanceof AccessibilityOnboardingScreen) mc.setScreen(new TitleScreen());
            if (!started && mc.screen instanceof TitleScreen) {
                if (!mc.gameDirectory.getCanonicalPath().endsWith("/build/blueprint-client/" + ROLE)) throw new AssertionError("Refusing non-disposable game directory");
                if (Files.exists(OUT.resolve("observations.txt")) || Files.exists(OUT.resolve("PASS.txt"))
                        || Files.exists(OUT.resolve("FAIL.txt")) || Files.exists(COORD.resolve("ready-" + firstStage() + "-" + ROLE + ".txt")))
                    throw new AssertionError("Output run id has already been used by " + ROLE + "; supply a fresh qaRun");
                Files.createDirectories(OUT); Files.createDirectories(COORD);
                mc.options.pauseOnLostFocus = false; mc.options.renderDistance().set(4); mc.options.fov().set(48);
                if (!HOST && !Files.exists(COORD.resolve("listening.txt"))) return;
                started = true;
                if (!HOST) {
                    connectionStarted = System.nanoTime();
                    String address = "127.0.0.1:25587";
                    ConnectScreen.startConnecting(new TitleScreen(), mc, ServerAddress.parseString(address), new ServerData("Disposable blueprint QA", address, false), false);
                } else {
                    GameRules rules = new GameRules(); rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false, null);
                    rules.getRule(GameRules.RULE_DAYLIGHT).set(false, null);
                    mc.createWorldOpenFlows().createFreshLevel("blueprint-" + RUN + "-" + System.currentTimeMillis(),
                            new LevelSettings("Disposable blueprint QA", GameType.CREATIVE, false, net.minecraft.world.Difficulty.NORMAL, true, rules, WorldDataConfiguration.DEFAULT),
                            new WorldOptions(57, false, false), registry -> registry.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());
                }
                return;
            }
            if (mc.level == null || mc.player == null) return;
            if (mc.screen != null) mc.setScreen(null);
            if (HOST && setup == null) {
                MinecraftServer server = mc.getSingleplayerServer();
                setup = server.submit(() -> {
                    server.overworld().setDayTime(6000);
                    if (!SOLO) {
                        server.setUsesAuthentication(false);
                        try { server.getConnection().startTcpServerListener(java.net.InetAddress.getByName("127.0.0.1"), 25587); }
                        catch (Exception ex) { throw new RuntimeException(ex); }
                    }
                }); return;
            }
            if (!HOST && CONNECTION_ONLY) { connectionProbe(mc); return; }
            if (HOST) {
                if (!setup.isDone()) return; setup.join();
                if (!Files.exists(COORD.resolve("listening.txt"))) Files.writeString(COORD.resolve("listening.txt"), RUN + " loopback 127.0.0.1:25587");
                MinecraftServer server = mc.getSingleplayerServer();
                if (CONNECTION_ONLY) { connectionProbe(mc); return; }
                if (!SOLO && Files.exists(COORD.resolve("complete.txt")) && Files.exists(ROOT.resolve("peer/PASS.txt"))) { finish(mc, null); return; }
                if (!SOLO && server.getPlayerList().getPlayerCount() < 2) return;
                if (pending != null) {
                    if (!pending.isDone()) return;
                    Stage produced = pending.join(); publish(produced); local = produced; pending = null;
                }
                if (hostIndex < 0) { hostIndex = firstStage(); pending = server.submit(() -> prepare(server, hostIndex)); return; }
                if (local != null && local.index == hostIndex && local.phase.equals("READY") && hostIndex >= 7 && acknowledged("ready", hostIndex)) {
                    pending = server.submit(() -> activate(server, hostIndex)); return;
                }
                if (acknowledged("captured", hostIndex)) {
                    if (hostIndex >= 20 && !SOLO) verifyEncounterPair(hostIndex);
                    if (hostIndex == lastStage()) {
                        Files.writeString(COORD.resolve("complete.txt"), RUN + " all stages acknowledged by " + (SOLO ? "host only" : "both TCP clients"));
                        if (SOLO || Files.exists(ROOT.resolve("peer/PASS.txt"))) finish(mc, null);
                        return;
                    }
                    hostIndex++; pending = server.submit(() -> prepare(server, hostIndex)); return;
                }
            }
            if (!Files.exists(COORD.resolve("stage.json"))) return;
            Stage state = JSON.fromJson(Files.readString(COORD.resolve("stage.json")), Stage.class);
            if (!RUN.equals(state.run)) throw new AssertionError("Coordination file belongs to another run");
            if (state.index != observed) {
                observed = state.index; settled = 0; captured = false; readySent = false; trackingFrames = 0;
                lastSecondaryTick = Long.MIN_VALUE; secondaryResponse = 0;
            }
            local = state;
            // The final short-lived corpse may expire after its valid capture/ACK. Completion
            // depends on both saved captures, not on keeping an expired fixture alive longer.
            if (!HOST && captured && Files.exists(COORD.resolve("complete.txt"))) { finish(mc, null); return; }
            camera(mc, observed);
            if (!allTracked(mc, state)) { if (++settled > 200) throw new AssertionError("Missing or mismatched prototype entity after 10 seconds, stage=" + observed); return; }
            settled++;
            if (observed >= 20 && Files.exists(COORD.resolve("encounter-window.json"))) {
                clientEncounterWindow = List.of(JSON.fromJson(Files.readString(COORD.resolve("encounter-window.json")), EncounterSample[].class));
            }
            // Stage 21 continues the already tracked, freely moving stage-20 encounter.
            if (settled >= (observed == 21 ? 1 : 25) && !readySent) {
                writeAck("ready", state.index, "All four exact entity UUIDs tracked; players=" + mc.level.players().size()); readySent = true;
            }
            if (!HOST && Files.exists(COORD.resolve("complete.txt"))) finish(mc, null);
        } catch (Throwable error) { finish(mc, error); }
    }

    private static void diagnose(Minecraft mc) throws Exception {
        String screen = mc.screen == null ? "none" : mc.screen.getClass().getSimpleName() + ":" + mc.screen.getTitle().getString();
        String state = "screen=" + screen + " level=" + (mc.level == null ? "none" : mc.level.dimension().location())
                + " localPlayer=" + (mc.player != null) + " players=" + (mc.level == null ? 0 : mc.level.players().size())
                + " activeWindow=" + mc.isWindowActive();
        if (mc.screen instanceof ConnectScreen) {
            for (var field : ConnectScreen.class.getDeclaredFields()) {
                if (net.minecraft.network.Connection.class.isAssignableFrom(field.getType())) {
                    field.setAccessible(true);
                    if (field.get(mc.screen) instanceof net.minecraft.network.Connection connection && connection.channel() != null) {
                        var channel = connection.channel();
                        state += " channel=" + channel.getClass().getSimpleName() + " open=" + channel.isOpen() + " active=" + channel.isActive()
                                + " autoRead=" + channel.config().isAutoRead() + " protocol=" + channel.attr(net.minecraft.network.Connection.ATTRIBUTE_PROTOCOL).get()
                                + " received=" + connection.getAverageReceivedPackets() + " sent=" + connection.getAverageSentPackets()
                                + " listener=" + (connection.getPacketListener() == null ? "none" : connection.getPacketListener().getClass().getSimpleName())
                                + " local=" + channel.localAddress() + " remote=" + channel.remoteAddress();
                    }
                }
            }
        }
        if (HOST && mc.getSingleplayerServer() != null) {
            var connections = mc.getSingleplayerServer().getConnection().getConnections();
            List<net.minecraft.network.Connection> snapshot;
            synchronized (connections) { snapshot = List.copyOf(connections); }
            for (var connection : snapshot) {
                if (connection.isMemoryConnection() || connection.channel() == null) continue;
                var channel = connection.channel();
                var outbound = channel.unsafe().outboundBuffer();
                state += " serverChannel=" + channel.getClass().getSimpleName() + " open=" + channel.isOpen() + " active=" + channel.isActive()
                        + " writable=" + channel.isWritable() + " autoRead=" + channel.config().isAutoRead()
                        + " protocol=" + channel.attr(net.minecraft.network.Connection.ATTRIBUTE_PROTOCOL).get()
                        + " received=" + connection.getAverageReceivedPackets() + " sent=" + connection.getAverageSentPackets()
                        + " pendingBytes=" + (outbound == null ? -1 : outbound.totalPendingWriteBytes())
                        + " remote=" + channel.remoteAddress();
            }
        }
        long now = System.nanoTime();
        if (!state.equals(diagnosticState) || now >= nextDiagnostic) {
            diagnosticState = state; nextDiagnostic = now + 5_000_000_000L;
            String line = java.time.Instant.now() + " " + ROLE + " " + state;
            System.out.println("[Blueprint QA] " + line);
            Files.createDirectories(OUT);
            Files.writeString(OUT.resolve("connection-diagnostics.txt"), line + "\n", java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND);
        }
        if (started && mc.screen instanceof net.minecraft.client.gui.screens.DisconnectedScreen) {
            String reason = screen;
            for (var field : mc.screen.getClass().getDeclaredFields()) {
                if (net.minecraft.network.chat.Component.class.isAssignableFrom(field.getType())) {
                    field.setAccessible(true);
                    if (field.get(mc.screen) instanceof net.minecraft.network.chat.Component component) reason += " | " + component.getString();
                }
            }
            throw new AssertionError("Client disconnected: " + reason);
        }
        if (!HOST && connectionStarted > 0 && mc.level == null && now - connectionStarted > 90_000_000_000L)
            throw new AssertionError("Login has not completed after 90 seconds: " + state);
    }
    private static void connectionProbe(Minecraft mc) throws Exception {
        Path mine = COORD.resolve("connected-" + ROLE + ".txt"), other = COORD.resolve("connected-" + (HOST ? "peer" : "host") + ".txt");
        if (mc.level.players().size() >= 2 && ++connectedTicks >= 40 && !Files.exists(mine))
            Files.writeString(mine, java.time.Instant.now() + " " + ROLE + " observed two real players for 40 ticks; player=" + mc.player.getUUID());
        if (Files.exists(mine) && Files.exists(other)) {
            Files.writeString(OUT.resolve("CONNECTION_PASS.txt"), "PASS: real IPv4 loopback login and two players observed by both clients. No model/animation screenshot or 14-stage acceptance is claimed.\n");
            done = true; mc.stop();
        }
    }

    private static Stage prepare(MinecraftServer server, int index) {
        var world = server.overworld();
        if (index == 21) {
            if (!encounterActive || fixtures.size() != 4) throw new AssertionError("Summit stage lost its original autonomous encounter");
            return snapshot(index, "ACTIVE", world.getGameTime());
        }
        encounterActive = false;
        for (TemplateMob mob : fixtures) mob.discard(); fixtures.clear();
        if (target != null) target.discard();
        world.setBlockAndUpdate(new BlockPos(12, -58, 0), Blocks.AIR.defaultBlockState());
        List<EntityType<TemplateMob>> types = List.of(BlueprintEntities.ZUWU_DAOSHOU.get(), BlueprintEntities.LUDUN_JIASHI.get(), BlueprintEntities.FUFA_JIJIU.get(), BlueprintEntities.SHANJING_SHANXIAO.get());
        float yaw = index == 1 ? 90 : index == 2 ? 45 : 0;
        for (int i = 0; i < 4; i++) {
            TemplateMob mob = types.get(i).create(world);
            mob.moveTo(i * 4, -60, 0, yaw, 0); mob.setYHeadRot(yaw); mob.setYBodyRot(yaw);
            boolean autonomous = index == 20 && i == 3;
            mob.setNoAi(!autonomous); mob.setPersistenceRequired(); mob.setNoGravity(!autonomous); mob.setInvulnerable(true);
            if (index == 20 && i == 3) {
                // Grounded, ordinary autonomous subject. No climb data, velocity, skill or AI goal is injected.
                mob.moveTo(4.5, -60, 3.5, 0, 0);
            }
            world.addFreshEntity(mob); fixtures.add(mob);
        }
        target = EntityType.COW.create(world); target.setNoAi(true); target.setNoGravity(true); target.setInvulnerable(true);
        // The real living target still collides and receives attacks; only its distracting test-fixture model is hidden.
        target.setInvisible(true);
        target.moveTo(index < 7 || index >= 14 ? -30 : index == 8 ? 4 : index >= 10 ? 12 : 0, -60, index == 11 ? 12 : index == 12 ? 10 : 2.3, 180, 0);
        world.addFreshEntity(target);
        if (index == 20) {
            for (int x = 2; x <= 6; x++) for (int z = 5; z <= 7; z++)
                for (int y = -60; y <= -58; y++) world.setBlockAndUpdate(new BlockPos(x, y, z), Blocks.STONE.defaultBlockState());
            target.moveTo(13.5, -60, 13.5, 180, 0);
        }
        if (index == 12) {
            world.setBlockAndUpdate(new BlockPos(12, -58, 0), Blocks.STONE.defaultBlockState());
            fixtures.get(3).setPos(12, -57, 0); fixtures.get(3).setOnGround(true);
        }
        for (var player : server.getPlayerList().getPlayers()) {
            player.setGameMode(GameType.CREATIVE); player.teleportTo(world, 6, -60, 24, 180, 0);
            player.getAbilities().flying = true; player.onUpdateAbilities();
        }
        return snapshot(index, "READY", world.getGameTime());
    }
    private static Stage activate(MinecraftServer server, int index) {
        boolean started = switch (index) {
            case 7 -> fixtures.get(0).startSkill(TemplateSkills.SWORD_COMBO, target);
            case 8 -> fixtures.get(1).startSkill(TemplateSkills.SHIELD_COMBO, target);
            case 9 -> fixtures.get(2).startSkill(TemplateSkills.POSSESSION, fixtures.get(0));
            case 10 -> fixtures.get(3).startSkill(TemplateSkills.POUNCE, target);
            case 11 -> fixtures.get(2).startSkill(TemplateSkills.TALISMAN_VOLLEY, target);
            case 12 -> { fixtures.get(3).setOnGround(true); yield fixtures.get(3).startSkill(TemplateSkills.ROCK_THROW, target); }
            case 13, 14, 15, 16, 17, 18, 19 -> {
                TemplateMob victim = fixtures.get(deathFixture(index));
                victim.setInvulnerable(false); victim.hurt(victim.damageSources().genericKill(), 10000);
                yield victim.isDeadOrDying();
            }
            case 20 -> {
                TemplateMob beast = fixtures.get(3);
                if (beast.isNoAi() || beast.isNoGravity()) throw new AssertionError("Autonomous subject has disabled AI/gravity");
                encounterInitialY = encounterPeakY = beast.getY(); serverEncounterWindow.clear();
                encounterActive = true;
                beast.setTarget(target); // Select a real enemy; navigation and all skill starts remain production AI's job.
                yield true;
            }
            default -> false;
        };
        if (!started) throw new AssertionError("Server refused QA action at stage " + index);
        return snapshot(index, "ACTIVE", server.overworld().getGameTime());
    }
    private static Stage snapshot(int stage, String phase, long now) {
        return new Stage(RUN, stage, phase, now, fixtures.stream().map(m -> new Expected(m.getId(), m.getUUID().toString(), m.blueprintId(), m.skillId(), m.skillStartTime())).toList());
    }
    private static void publish(Stage stage) throws Exception {
        Path temporary = COORD.resolve("stage-next.json"); Files.writeString(temporary, JSON.toJson(stage));
        Files.move(temporary, COORD.resolve("stage.json"), StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
    }
    private static boolean acknowledged(String status, int stage) {
        return Files.exists(COORD.resolve(status + "-" + stage + "-host.txt")) && (SOLO || Files.exists(COORD.resolve(status + "-" + stage + "-peer.txt")));
    }
    private static void verifyEncounterPair(int stage) throws Exception {
        var host = com.google.gson.JsonParser.parseString(Files.readString(ROOT.resolve("host/" + String.format("%02d-encounter.json", stage)))).getAsJsonObject();
        var peer = com.google.gson.JsonParser.parseString(Files.readString(ROOT.resolve("peer/" + String.format("%02d-encounter.json", stage)))).getAsJsonObject();
        if (!host.get("uuid").getAsString().equals(peer.get("uuid").getAsString())
                || Math.abs(host.get("serverTick").getAsLong() - peer.get("serverTick").getAsLong()) > 3)
            throw new AssertionError("Autonomous host/peer captures do not describe the same entity and three-tick event window");
        if (stage == 20) {
            if (host.get("clientClimbStart").getAsLong() != peer.get("clientClimbStart").getAsLong()
                    || !host.get("clientClimbFace").getAsString().equals(peer.get("clientClimbFace").getAsString()))
                throw new AssertionError("Autonomous host/peer climb epoch or wall face differs");
        } else {
            if (host.get("clientStart").getAsLong() != peer.get("clientStart").getAsLong())
                throw new AssertionError("Autonomous host/peer captured different rock throws");
            boolean sameRock = false;
            for (var left : host.getAsJsonArray("visibleRockUuids")) for (var right : peer.getAsJsonArray("visibleRockUuids"))
                sameRock |= left.getAsString().equals(right.getAsString());
            if (!sameRock) throw new AssertionError("Autonomous host/peer did not see the same actual rock projectile");
        }
    }
    private static void writeAck(String status, int stage, String data) throws Exception {
        Files.writeString(COORD.resolve(status + "-" + stage + "-" + ROLE + ".txt"), RUN + "\n" + data);
    }
    private static boolean allTracked(Minecraft mc, Stage state) {
        if (state.mobs.size() != 4) throw new AssertionError("Expected exactly four server prototypes");
        for (Expected expected : state.mobs) {
            if (!(mc.level.getEntity(expected.entityId) instanceof TemplateMob mob) || !mob.getUUID().toString().equals(expected.uuid)
                    || !mob.blueprintId().equals(expected.id)) return false;
        }
        if (!SOLO && mc.level.players().size() < 2) return false;
        return true;
    }
    private static int firstStage() { return DEATH_ONLY ? 14 : 0; }
    private static int lastStage() { return DEATH_ONLY ? 19 : NAMES.length - 1; }
    private static int deathFixture(int stage) { return stage == 13 ? 1 : stage <= 15 ? 0 : stage <= 17 ? 2 : 3; }
    private static int captureAge(int stage) {
        return switch (stage) {
            case 9, 11 -> 26;
            case 13, 15 -> 55;
            case 14, 16, 18 -> 20;
            case 17, 19 -> 40;
            default -> 17;
        };
    }
    private static int lastCaptureAge(int stage) {
        return switch (stage) {
            case 13 -> 180;
            case 15 -> 58;
            case 17, 19 -> 43;
            case 14, 16, 18 -> 28;
            case 10 -> 40;
            case 9, 11 -> 38;
            default -> 30;
        };
    }
    private static void camera(Minecraft mc, int stage) {
        mc.options.hideGui = true; mc.options.setCameraType(CameraType.FIRST_PERSON);
        if (stage >= 20) {
            mc.options.fov().set(48);
            Vec3 eye = new Vec3(10.5, -55.8, -1), look = new Vec3(4.5, -58.3, 5);
            Vec3 delta = look.subtract(eye);
            ArmorStand camera = new ArmorStand(mc.level, eye.x, eye.y, eye.z);
            camera.setPos(eye.x, eye.y - camera.getEyeHeight(), eye.z);
            float yaw = (float) Math.toDegrees(Math.atan2(-delta.x, delta.z));
            camera.setYRot(yaw); camera.setYHeadRot(yaw); camera.yHeadRotO = yaw;
            camera.setXRot((float) -Math.toDegrees(Math.atan2(delta.y, delta.horizontalDistance()))); camera.setOldPosAndRot();
            mc.setCameraEntity(camera); return;
        }
        if (stage >= 14) {
            mc.options.fov().set(42);
            ArmorStand camera = new ArmorStand(mc.level, deathFixture(stage) * 4 + 3, -60.75, 5);
            camera.setYRot(149); camera.setYHeadRot(149); camera.yHeadRotO = 149; camera.setXRot(4); camera.setOldPosAndRot();
            mc.setCameraEntity(camera); return;
        }
        boolean individual = stage >= 3 && stage <= 6;
        mc.options.fov().set(individual ? 42 : 32);
        double x = individual ? (stage - 3) * 4 : 6, z = individual ? 5 : 17;
        ArmorStand camera = new ArmorStand(mc.level, x, individual ? -60.55 : -59.0, z);
        camera.setYRot(180); camera.setYHeadRot(180); camera.yHeadRotO = 180; camera.setXRot(individual ? 0 : 7); camera.setOldPosAndRot();
        mc.setCameraEntity(camera);
    }

    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event) {
        if (ROLE.isEmpty() || done || event.phase != TickEvent.Phase.END || captured || local == null) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || mc.getOverlay() != null || !allTracked(mc, local)) return;
        try {
            if (observed >= 20) {
                enableContactTracking(mc);
                if (!readySent || !local.phase.equals("ACTIVE") || !observeEncounter(mc)) return;
            } else if (!readySent) return;
            else if (observed >= 7) {
                if (!local.phase.equals("ACTIVE")) return;
                if (observed == 8 || observed == 9) sampleSecondaryMotion(mc);
                long age = mc.level.getGameTime() - local.published;
                int wanted = captureAge(observed);
                if (age < wanted) return;
                if (age > lastCaptureAge(observed))
                    throw new AssertionError("Missed active contact capture window, stage=" + observed + " age=" + age);
                if (observed == 8 && secondaryResponse <= .02 || observed == 9 && secondaryResponse <= .005)
                    throw new AssertionError("Actual secondary bones never responded during " + NAMES[observed] + ": maximum=" + secondaryResponse);
                for (Expected expected : local.mobs) {
                    TemplateMob mob = (TemplateMob) mc.level.getEntity(expected.entityId);
                    if (expected.skill != 0 || mob.isDeadOrDying()) {
                        if (mob.skillId() != expected.skill || mob.skillStartTime() != expected.start)
                            throw new AssertionError("SynchedData mismatch " + expected.id + ": actual=" + mob.skillId() + "/" + mob.skillStartTime() + ", server=" + expected.skill + "/" + expected.start);
                        float actionAge = mob.actionAge(0);
                        if (Math.abs(actionAge - (mc.level.getGameTime() - expected.start) * mob.skillSpeed()) > .01)
                            throw new AssertionError("Animation clock mismatch " + expected.id);
                        if (expected.skill != 0) {
                            boolean phaseMatches = false;
                            for (int offset = -3; offset <= 3; offset++)
                                phaseMatches |= TemplateSkills.byId(expected.skill).phaseAt((int) actionAge + offset) == mob.skillPhase();
                            if (!phaseMatches) throw new AssertionError("Phase cannot match synchronized clock " + expected.id);
                        }
                    }
                    LOG.add(NAMES[observed] + " entity=" + expected.id + " uuid=" + expected.uuid + " skill=" + mob.skillId()
                            + " phase=" + mob.skillPhase() + " start=" + mob.skillStartTime() + " clientTime=" + mc.level.getGameTime() + " actionAge=" + mob.actionAge(0));
                    observeAnimation(mc, mob, expected.skill != 0 || mob.isDeadOrDying());
                }
                if (observed == 9) {
                    TemplateMob priest = (TemplateMob) mc.level.getEntity(local.mobs.get(2).entityId);
                    TemplateMob ally = (TemplateMob) mc.level.getEntity(local.mobs.get(0).entityId);
                    if (priest.buffTargetId() != ally.getId() || !ally.isPossessed())
                        throw new AssertionError("Possession target/state failed to synchronize to " + ROLE + "; target="+priest.buffTargetId()+", expected="+ally.getId()+", possessed="+ally.isPossessed());
                }
                if (observed >= 13 && !((TemplateMob) mc.level.getEntity(local.mobs.get(deathFixture(observed)).entityId)).isDeadOrDying())
                    throw new AssertionError("Death state not synchronized for " + NAMES[observed]);
            }
            try (var image = Screenshot.takeScreenshot(mc.getMainRenderTarget())) {
                if (image.getWidth() < 600 || image.getHeight() < 400) throw new AssertionError("Unexpected framebuffer size");
                image.writeToFile(OUT.resolve(String.format("%02d-%s.png", observed, NAMES[observed])));
            }
            captured = true;
            String data = "Captured " + NAMES[observed] + "; four exact UUIDs tracked; players=" + mc.level.players().size() + "; FPS=" + mc.getFps();
            LOG.add(data); Files.write(OUT.resolve("observations.txt"), LOG); writeAck("captured", observed, data);
        } catch (Throwable error) {
            try (var failedFrame = Screenshot.takeScreenshot(mc.getMainRenderTarget())) {
                failedFrame.writeToFile(OUT.resolve(String.format("%02d-%s-FAILED.png", observed, NAMES[observed])));
            } catch (Throwable captureFailure) { error.addSuppressed(captureFailure); }
            finish(mc, error);
        }
    }

    private static void observeAnimation(Minecraft mc, TemplateMob mob, boolean requireAction) {
        var controller = mob.getAnimatableInstanceCache().getManagerForId(mob.getId()).getAnimationControllers().get("body");
        String queued = controller == null || controller.getCurrentAnimation() == null ? "none" : controller.getCurrentAnimation().animation().name();
        String wanted = "animation." + mob.blueprintId() + "." + mob.visualAnimation();
        String state = controller == null ? "none" : controller.getAnimationState().name();
        StringBuilder bones = new StringBuilder();
        if (mc.getEntityRenderDispatcher().getRenderer(mob) instanceof com.dynasty.blueprint.client.TemplateMobRenderer renderer) {
            for (String name : List.of("root", "waist", "right_shoulder", "left_shoulder", "right_elbow", "left_elbow", "right_knee", "left_knee",
                    "right_thigh", "left_thigh", "head", "neck", "tail", "mask_left", "mask_right", "robe_front", "robe_back", "body_head", "body_chest", "dao")) {
                renderer.getGeoModel().getBone(name).ifPresent(bone -> bones.append(" ").append(name).append("=rot(")
                        .append(bone.getRotX()).append(',').append(bone.getRotY()).append(',').append(bone.getRotZ())
                        .append(")pos(").append(bone.getPosX()).append(',').append(bone.getPosY()).append(',').append(bone.getPosZ())
                        .append(")scale(").append(bone.getScaleX()).append(',').append(bone.getScaleY()).append(',').append(bone.getScaleZ()).append(')'));
            }
            LOG.add("Rendered " + mob.blueprintId() + " requested=" + wanted + " queued=" + queued + " controller=" + state + bones);
            if (mob.isDeadOrDying()) {
                if (requireAction && (mob.kind() == TemplateMob.Kind.PRIEST || mob.kind() == TemplateMob.Kind.SHIELD))
                    secondaryPose(renderer, mob, true);
                int overlay = renderer.getPackedOverlay(mob, 0, 0);
                var tint = renderer.getRenderColor(mob, 0, 0xF000F0);
                LOG.add("Death material " + mob.blueprintId() + " hurtTime=" + mob.hurtTime + " overlay=" + overlay
                        + " rgba=" + tint.getRed() + "," + tint.getGreen() + "," + tint.getBlue() + "," + tint.getAlpha());
                if (mob.hurtTime <= 0 && overlay != net.minecraft.client.renderer.texture.OverlayTexture.NO_OVERLAY)
                    throw new AssertionError("Death corpse incorrectly retains damage overlay: " + mob.blueprintId());
                if (observed == 15) {
                    var dao = renderer.getGeoModel().getBone("dao").orElseThrow(() -> new AssertionError("Missing planted dao bone"));
                    // Frozen authored endpoint compensates the fallen parent chain; the model
                    // preview verifies its world-space blade is vertical and tip is at y=-.18px.
                    if (Math.abs(dao.getRotX() - .018052F) > .05F || Math.abs(dao.getRotY() + .402887F) > .05F
                            || Math.abs(dao.getRotZ() - 1.185524F) > .05F || Math.abs(dao.getPosX() - 14.081163F) > .05F
                            || Math.abs(dao.getPosY() - 1.17901F) > .05F || Math.abs(dao.getPosZ() + 11.476758F) > .05F)
                        throw new AssertionError("Dao has not reached the planted endpoint compensated against the collapsed body: actual rot="
                                + dao.getRotX() + "," + dao.getRotY() + "," + dao.getRotZ() + " pos="
                                + dao.getPosX() + "," + dao.getPosY() + "," + dao.getPosZ());
                }
                if (observed == 17) {
                    for (String boneName : List.of("body_head", "body_chest")) {
                        var body = renderer.getGeoModel().getBone(boneName).orElseThrow(() -> new AssertionError("Missing empty-robe body bone " + boneName));
                        if (body.getScaleX() > .02F || body.getScaleY() > .02F || body.getScaleZ() > .02F)
                            throw new AssertionError("Priest anatomical body has not disappeared from empty robe: " + boneName);
                    }
                    var left = renderer.getGeoModel().getBone("mask_left").orElseThrow(() -> new AssertionError("Missing left mask fragment"));
                    var right = renderer.getGeoModel().getBone("mask_right").orElseThrow(() -> new AssertionError("Missing right mask fragment"));
                    if (Math.abs(left.getPosX() - right.getPosX()) < 1F)
                        throw new AssertionError("Priest mask fragments have not separated");
                }
                if (observed == 19) {
                    int bent = 0;
                    for (String boneName : List.of("right_elbow", "left_elbow", "right_knee", "left_knee")) {
                        var limb = renderer.getGeoModel().getBone(boneName).orElseThrow(() -> new AssertionError("Missing curled limb " + boneName));
                        var initial = limb.getInitialSnapshot();
                        if (Math.abs(limb.getRotX() - initial.getRotX()) > .45F || Math.abs(limb.getRotY() - initial.getRotY()) > .45F || Math.abs(limb.getRotZ() - initial.getRotZ()) > .45F) bent++;
                    }
                    if (bent != 4) throw new AssertionError("Shanxiao corpse has not curled all four limbs: bent=" + bent);
                    if (tint.getRed() == 255 && tint.getGreen() == 255 && tint.getBlue() == 255)
                        throw new AssertionError("Shanxiao corpse fur has not faded");
                }
            }
        }
        if (requireAction && (!queued.equals(wanted) || state.equals("STOPPED")))
            throw new AssertionError("Actual Gecko animation did not reach synchronized action: requested=" + wanted + ", queued=" + queued + ", controller=" + state);
    }

    private static void sampleSecondaryMotion(Minecraft mc) throws Exception {
        if (lastSecondaryTick == mc.level.getGameTime()) return;
        lastSecondaryTick = mc.level.getGameTime();
        TemplateMob mob = (TemplateMob) mc.level.getEntity(local.mobs.get(observed == 8 ? 1 : 2).entityId);
        var renderer = (com.dynasty.blueprint.client.TemplateMobRenderer) mc.getEntityRenderDispatcher().getRenderer(mob);
        Map<String, Object> sample = secondaryPose(renderer, mob, false);
        sample.put("run", RUN); sample.put("role", ROLE); sample.put("stage", observed);
        sample.put("clientTick", mc.level.getGameTime()); sample.put("uuid", mob.getUUID().toString());
        sample.put("skill", mob.skillId()); sample.put("start", mob.skillStartTime());
        Files.writeString(OUT.resolve(String.format("%02d-secondary-motion.jsonl", observed)), LINE_JSON.toJson(sample) + "\n",
                java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND);
    }

    private static Map<String, Object> secondaryPose(com.dynasty.blueprint.client.TemplateMobRenderer renderer, TemplateMob mob, boolean death) {
        Map<String, Object> result = new LinkedHashMap<>();
        if (mob.kind() == TemplateMob.Kind.SHIELD) {
            for (String side : List.of("left", "right")) {
                var rail = renderer.getGeoModel().getBone(side + "_shoulder_rail").orElseThrow(() -> new AssertionError("Missing shoulder sliding rail"));
                float y = rail.getPosY();
                if (!Float.isFinite(y) || y < -.001 || y > 1.201 || Math.abs(rail.getPosX()) > .001 || Math.abs(rail.getPosZ()) > .001)
                    throw new AssertionError("Shoulder rail left its authored sliding range");
                if (death && Math.abs(y) > .001) throw new AssertionError("Shoulder procedural rail did not reset for death");
                if (!death) secondaryResponse = Math.max(secondaryResponse, Math.abs(y));
                result.put(side + "_shoulder_rail", new float[] {rail.getPosX(), y, rail.getPosZ()});
                var lower = renderer.getGeoModel().getBone(side + "_hip_plate_lower").orElseThrow(() -> new AssertionError("Missing second hip armour layer"));
                if (Math.abs(lower.getRotX() - lower.getInitialSnapshot().getRotX()) > Math.toRadians(8.1))
                    throw new AssertionError("Lower hip armour exceeds its eight-degree follow range");
                result.put(side + "_hip_plate_lower", new float[] {lower.getRotX(), lower.getRotY(), lower.getRotZ()});
            }
        } else if (mob.kind() == TemplateMob.Kind.PRIEST) {
            Map<String, Double> limits = new LinkedHashMap<>();
            for (String side : List.of("left", "right")) {
                limits.put(side + "_sleeve_inner_spring", 10D); limits.put(side + "_sleeve_outer_spring", 10D);
                limits.put(side + "_sleeve_inner_tip", 18D); limits.put(side + "_sleeve_outer_tip", 18D);
            }
            for (int i = 0; i < 3; i++) { limits.put("talisman_spring_" + i, 25D); limits.put("talisman_tip_" + i, 25D); }
            for (var entry : limits.entrySet()) {
                var bone = renderer.getGeoModel().getBone(entry.getKey()).orElseThrow(() -> new AssertionError("Missing secondary fabric chain " + entry.getKey()));
                var rest = bone.getInitialSnapshot();
                float[] offset = {bone.getRotX() - rest.getRotX(), bone.getRotY() - rest.getRotY(), bone.getRotZ() - rest.getRotZ()};
                for (float angle : offset) {
                    if (!Float.isFinite(angle) || Math.abs(angle) > Math.toRadians(entry.getValue() + .1))
                        throw new AssertionError("Secondary fabric exceeded bounded range: " + entry.getKey());
                    if (death && Math.abs(angle) > .001) throw new AssertionError("Secondary fabric retained spring offset during death: " + entry.getKey());
                    if (!death) secondaryResponse = Math.max(secondaryResponse, Math.abs(angle));
                }
                result.put(entry.getKey(), offset);
            }
        }
        return result;
    }

    private static void finish(Minecraft mc, Throwable error) {
        if (done) return; done = true;
        if (error != null) { error.printStackTrace(); LOG.add("FAIL: " + error); }
        else LOG.add(SOLO ? "PASS: isolated single-client " + (lastStage() - firstStage() + 1) + " stages, actual Gecko action/death clips, and screenshot harness. This is NOT a multiplayer or visual-quality pass."
                : "PASS: real loopback TCP clients acknowledged all " + (lastStage() - firstStage() + 1) + " stages with matching entity identity, action start, phase, actual Gecko action/death clips, possession effect and target. Screenshots still require visual review.");
        try { Files.createDirectories(OUT); Files.write(OUT.resolve(error == null ? "PASS.txt" : "FAIL.txt"), LOG); }
        catch (Exception writeFailure) { writeFailure.printStackTrace(); }
        mc.setCameraEntity(mc.player); mc.stop();
    }
}
