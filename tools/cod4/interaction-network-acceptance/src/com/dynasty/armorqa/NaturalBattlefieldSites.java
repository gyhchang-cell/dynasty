package com.dynasty.armorqa;

import com.dynasty.expansion.SmallInteractions;
import com.dynasty.structure.TravelSitePiece;
import com.dynasty.structure.TravelSiteStructure;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderSet;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/**
 * Explicitly invoked QA helper, with no event subscriber or automatic launch.
 * Uses the native locate/start/piece flow in NaturalInteractionPlacementAcceptance.
 * TravelSitePiece.postProcess places battlefield_remnant at (9,1,28); (9,1,27)
 * is its approach. Transform arithmetic follows the cached 1.20.1 StructurePiece
 * getWorldX/Y/Z implementation, without reflective access to protected methods.
 *
 * Runtime chunk requests can generate and populate NATURAL terrain/structures.
 * This helper never places/repairs blocks, moves players, saves, or starts/stops a server.
 * Call on the server thread in the coordinator's private seed-20261023 overworld.
 * Success proves the observed anchors/standing spaces, not interaction completion
 * or an unmodified-world history. No runtime success is implied by this source.
 */
public final class NaturalBattlefieldSites {
    private static final long SEED = 20261023L;
    private static final BlockPos ORIGINAL = new BlockPos(2946, 72, 283);
    private static final ResourceLocation STRUCTURE = new ResourceLocation("dynasty", "desert_caravan");
    private static final ResourceLocation BLOCK = new ResourceLocation("dynasty", "battlefield_remnant");
    private static final int OFFSET = 2048;
    private static final int LOCATE_RADIUS = 4;
    // Square perimeters of radii 1, 2, 3 contain 8 + 16 + 24 = 48 origins.
    private static final int OFFSET_RINGS = 3;
    private static final int MAX_LOCATES = 48;
    private static final int REQUIRED = 2;

    private NaturalBattlefieldSites() {}

    /** Returns exactly two additional distinct anchors, or throws without a partial success. */
    public static List<Map<String, Object>> find(ServerLevel level, BlockPos original) throws Exception {
        Objects.requireNonNull(level, "level");
        Objects.requireNonNull(original, "original");
        require(level.getServer().isSameThread(), "Natural site search requires the server thread");
        require(level.dimension().equals(Level.OVERWORLD) && level.getSeed() == SEED,
                "Expected seed 20261023 overworld");
        require(ORIGINAL.equals(original), "Expected original battlefield anchor 2946, 72, 283");
        var registry = level.registryAccess().registryOrThrow(Registries.STRUCTURE);
        var holder = registry.getHolderOrThrow(ResourceKey.create(Registries.STRUCTURE, STRUCTURE));
        require(holder.value() instanceof TravelSiteStructure, "Unexpected desert_caravan structure type");
        var entry = SmallInteractions.ENTRIES.get("battlefield_remnant");
        require(entry != null && entry.isPresent(), "Battlefield block is not registered");
        var expected = entry.get();
        require(BLOCK.equals(ForgeRegistries.BLOCKS.getKey(expected)), "Unexpected battlefield registry ID");

        List<Map<String, Object>> results = new ArrayList<>();
        List<String> rejected = new ArrayList<>();
        Set<Long> starts = new HashSet<>();
        Set<BlockPos> anchors = new HashSet<>();
        anchors.add(original.immutable());
        int attempts = 0;
        int chunkRequests = 0;
        for (int ring = 1; ring <= OFFSET_RINGS; ring++) {
            for (int dx = -ring; dx <= ring; dx++) {
                for (int dz = -ring; dz <= ring; dz++) {
                    if (Math.max(Math.abs(dx), Math.abs(dz)) != ring) continue;
                    require(attempts < MAX_LOCATES, "Locate budget exhausted");
                    BlockPos searchOrigin = ORIGINAL.offset(dx * OFFSET, 0, dz * OFFSET);
                    attempts++;
                    var located = level.getChunkSource().getGenerator().findNearestMapStructure(
                            level, HolderSet.direct(holder), searchOrigin, LOCATE_RADIUS, false);
                    if (located == null) {
                        rejected.add(attempts + ": no locate result at " + searchOrigin.toShortString());
                        continue;
                    }
                    require(located.getSecond().value() == holder.value(), "Locate returned a different structure");
                    var locatePos = located.getFirst();
                    StructureStart start = null;
                    // Same bounded 3x3 native-start lookup as the existing acceptance tool.
                    // Prefer the reported chunk; the other eight cover a locate/start offset.
                    for (int distance = 0; distance <= 1 && start == null; distance++) {
                        for (int sx = -distance; sx <= distance && start == null; sx++) {
                            for (int sz = -distance; sz <= distance && start == null; sz++) {
                                if (Math.max(Math.abs(sx), Math.abs(sz)) != distance) continue;
                                chunkRequests++;
                                var candidate = level.getChunk((locatePos.getX() >> 4) + sx,
                                        (locatePos.getZ() >> 4) + sz).getStartForStructure(holder.value());
                                if (candidate == null || !candidate.isValid()
                                        || candidate.getStructure() != holder.value()) continue;
                                var bounds = candidate.getBoundingBox();
                                if (locatePos.getX() < bounds.minX() || locatePos.getX() > bounds.maxX()
                                        || locatePos.getZ() < bounds.minZ() || locatePos.getZ() > bounds.maxZ()) continue;
                                start = candidate;
                            }
                        }
                    }
                    if (start == null) {
                        rejected.add(attempts + ": locate without matching native start " + locatePos.toShortString());
                        continue;
                    }
                    if (!starts.add(start.getChunkPos().toLong())) {
                        rejected.add(attempts + ": duplicate start " + start.getChunkPos());
                        continue;
                    }
                    if (start.getPieces().size() != 1 || !(start.getPieces().get(0) instanceof TravelSitePiece)) {
                        rejected.add(attempts + ": expected one complete TravelSitePiece at " + start.getChunkPos());
                        continue;
                    }
                    StructurePiece piece = start.getPieces().get(0);
                    BoundingBox box = piece.getBoundingBox();
                    Direction orientation = piece.getOrientation();
                    if (orientation == null || orientation.getAxis() == Direction.Axis.Y
                            || box.getXSpan() != 31 || box.getYSpan() != 13 || box.getZSpan() != 31) {
                        rejected.add(attempts + ": unexpected orientation/bbox at " + start.getChunkPos());
                        continue;
                    }
                    BlockPos pos = world(box, orientation, 9, 1, 28);
                    BlockPos approach = world(box, orientation, 9, 1, 27);
                    if (anchors.contains(pos)) {
                        rejected.add(attempts + ": original/duplicate anchor " + pos.toShortString());
                        continue;
                    }
                    if (!box.isInside(pos) || !box.isInside(approach)
                            || level.isOutsideBuildHeight(approach.below())
                            || level.isOutsideBuildHeight(approach.above())
                            || !level.getWorldBorder().isWithinBounds(new BlockPos(box.minX(), box.minY(), box.minZ()))
                            || !level.getWorldBorder().isWithinBounds(new BlockPos(box.maxX(), box.maxY(), box.maxZ()))) {
                        rejected.add(attempts + ": out-of-bounds anchor/piece " + pos.toShortString());
                        continue;
                    }
                    // A 31x31 piece intersects at most 3x3 chunks. Fully populate it before observing.
                    int pieceChunks = 0;
                    for (int cx = box.minX() >> 4; cx <= box.maxX() >> 4; cx++) {
                        for (int cz = box.minZ() >> 4; cz <= box.maxZ() >> 4; cz++) {
                            level.getChunk(cx, cz);
                            chunkRequests++;
                            pieceChunks++;
                        }
                    }
                    var state = level.getBlockState(pos);
                    boolean registeredBlock = state.is(expected)
                            && BLOCK.equals(ForgeRegistries.BLOCKS.getKey(state.getBlock()));
                    boolean collision = !state.getCollisionShape(level, pos).isEmpty();
                    boolean outline = !state.getShape(level, pos).isEmpty();
                    boolean support = level.getBlockState(approach.below()).isFaceSturdy(level, approach.below(), Direction.UP);
                    var body = new AABB(approach.getX() + .2, approach.getY(), approach.getZ() + .2,
                            approach.getX() + .8, approach.getY() + 1.8, approach.getZ() + .8);
                    boolean clear = level.noCollision(body);
                    boolean dry = level.getFluidState(approach).isEmpty()
                            && level.getFluidState(approach.above()).isEmpty();
                    if (!(registeredBlock && collision && outline && support && clear && dry)) {
                        rejected.add(attempts + ": invalid anchor " + pos.toShortString() + " state=" + state
                                + " registered=" + registeredBlock + " collision=" + collision + " outline=" + outline
                                + " support=" + support + " clear=" + clear + " dry=" + dry);
                        continue;
                    }
                    anchors.add(pos);
                    var row = new LinkedHashMap<String, Object>();
                    row.put("kind", "natural_interaction");
                    row.put("id", "battlefield_remnant");
                    row.put("pos", pos.toShortString());
                    row.put("approach", approach.toShortString());
                    row.put("structure", STRUCTURE.toString());
                    row.put("startChunk", start.getChunkPos().toString());
                    row.put("start_chunk", start.getChunkPos().toString());
                    row.put("orientation", orientation.getName());
                    row.put("bbox", box.toString());
                    row.put("piece_count", start.getPieces().size());
                    row.put("piece_chunks_loaded", pieceChunks);
                    row.put("local_anchor", "9, 1, 28");
                    row.put("local_approach", "9, 1, 27");
                    row.put("state", state.toString());
                    row.put("expected_registered_block", registeredBlock);
                    row.put("collision_nonempty", collision);
                    row.put("outline_nonempty", outline);
                    row.put("approach_ground_support", support);
                    row.put("approach_body_clear", clear);
                    row.put("approach_fluid_empty", dry);
                    row.put("seed", level.getSeed());
                    row.put("dimension", level.dimension().location().toString());
                    row.put("original", original.toShortString());
                    row.put("search_origin", searchOrigin.toShortString());
                    row.put("locate_pos", locatePos.toShortString());
                    row.put("radius_regions", LOCATE_RADIUS);
                    row.put("locate_attempt", attempts);
                    row.put("observed_tick", level.getGameTime());
                    row.put("scene_blocks_manually_placed", false);
                    results.add(row);
                    if (results.size() == REQUIRED) {
                        for (var accepted : results) {
                            accepted.put("locate_attempts_total", attempts);
                            accepted.put("locate_attempts_limit", MAX_LOCATES);
                            accepted.put("explicit_chunk_requests_total", chunkRequests);
                            accepted.put("distinct_starts_examined", starts.size());
                            accepted.put("search_rejections", List.copyOf(rejected));
                        }
                        return List.copyOf(results);
                    }
                }
            }
        }
        throw new IllegalStateException("Bounded natural battlefield search incomplete: accepted=" + results.size()
                + "/" + REQUIRED + ", attempts=" + attempts + "/" + MAX_LOCATES + ", distinctStarts=" + starts.size()
                + ", explicitChunkRequests=" + chunkRequests + ", partial=" + results + ", rejected=" + rejected);
    }

    private static BlockPos world(BoundingBox box, Direction direction, int x, int y, int z) {
        return switch (direction) {
            case NORTH -> new BlockPos(box.minX() + x, box.minY() + y, box.maxZ() - z);
            case SOUTH -> new BlockPos(box.minX() + x, box.minY() + y, box.minZ() + z);
            case WEST -> new BlockPos(box.maxX() - z, box.minY() + y, box.minZ() + x);
            case EAST -> new BlockPos(box.minX() + z, box.minY() + y, box.minZ() + x);
            default -> throw new IllegalArgumentException("Non-horizontal travel-site orientation: " + direction);
        };
    }

    private static void require(boolean condition, String message) {
        if (!condition) throw new IllegalStateException(message);
    }
}
