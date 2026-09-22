package com.dynasty.structure;

import com.dynasty.Dynasty;
import com.dynasty.DynastyBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePiecesBuilder;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** Tests production placement calls, including the separately generated main hall. */
@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class PalaceLayoutGameTests {
    private static final ResourceLocation PALACE_LOOT = new ResourceLocation("dynasty", "chests/dynasty_palace");
    private static final BlockPos ORIGIN = new BlockPos(101, 72, -205);

    private static final class Capture extends PalacePiece {
        final Map<BlockPos, BlockState> cells = new HashMap<>();
        final Set<BlockPos> chests = new HashSet<>();

        Capture() { super(DynastyStructures.PALACE_PIECE.get(), 0, ORIGIN); }
        Capture(CompoundTag tag) { super(DynastyStructures.PALACE_PIECE.get(), tag); }

        @Override protected void set(WorldGenLevel w, BoundingBox b, int x, int y, int z, BlockState state) {
            BoundingBox own = getBoundingBox();
            if (x < 0 || x >= own.getXSpan() || y < 0 || y >= own.getYSpan()
                    || z < 0 || z >= own.getZSpan())
                throw new AssertionError("Palace placement escapes saved bounds: " + x + "," + y + "," + z);
            cells.put(new BlockPos(x, y, z), state);
        }

        @Override protected boolean createChest(WorldGenLevel w, BoundingBox b, RandomSource r,
                                                 int x, int y, int z, ResourceLocation table) {
            if (!PALACE_LOOT.equals(table)) throw new AssertionError("Unexpected palace loot table: " + table);
            if (!chests.add(new BlockPos(x, y, z))) throw new AssertionError("Duplicate palace chest");
            set(w, b, x, y, z, Blocks.CHEST.defaultBlockState());
            return true;
        }

        void build() {
            postProcess(null, null, null, RandomSource.create(7), getBoundingBox(),
                    new ChunkPos(ORIGIN), ORIGIN);
        }

        BlockState at(int x, int y, int z) {
            return cells.getOrDefault(new BlockPos(x, y, z), Blocks.AIR.defaultBlockState());
        }

        BlockPos local(BlockPos world) {
            // Both production pieces deliberately face NORTH: local Z is reversed.
            return new BlockPos(world.getX() - getBoundingBox().minX(),
                    world.getY() - getBoundingBox().minY(), getBoundingBox().maxZ() - world.getZ());
        }

        boolean walk(int x, int z) {
            return x >= 0 && x < SIZE && z >= 0 && z < SIZE
                    && !at(x, 3, z).isAir() && at(x, 3, z).getFluidState().isEmpty()
                    && at(x, 4, z).isAir() && at(x, 5, z).isAir();
        }
    }

    private static final class MainHallCapture extends MainHallPiece {
        final Capture palace;
        int chests;

        MainHallCapture(MainHallPiece piece, Capture palace) {
            super(DynastyStructures.MAIN_HALL_PIECE.get(), piece.createTag(null));
            this.palace = palace;
        }

        @Override protected void set(WorldGenLevel w, BoundingBox b, int x, int y, int z, BlockState state) {
            if (x < 0 || x >= WIDTH || y < 0 || y >= HEIGHT || z < 0 || z >= DEPTH)
                throw new AssertionError("Main hall placement escapes own bounds: " + x + "," + y + "," + z);
            BlockPos target = palace.local(world(x, y, z));
            palace.set(w, palace.getBoundingBox(), target.getX(), target.getY(), target.getZ(), state);
        }

        @Override protected boolean createChest(WorldGenLevel w, BoundingBox b, RandomSource r,
                                                 int x, int y, int z, ResourceLocation table) {
            if (!PALACE_LOOT.equals(table)) throw new AssertionError("Unexpected main hall loot table: " + table);
            chests++;
            set(w, b, x, y, z, Blocks.CHEST.defaultBlockState());
            return true;
        }
    }

    private static List<StructurePiece> children(PalacePiece piece) {
        StructurePiecesBuilder builder = new StructurePiecesBuilder();
        piece.addChildren(piece, builder, RandomSource.create(7));
        return builder.build().pieces();
    }

    private static void assertRoutes(GameTestHelper h, Capture palace) {
        BlockPos entry = new BlockPos(31, 4, 59);
        h.assertTrue(palace.walk(entry.getX(), entry.getZ()), "Front gate lacks two blocks of headroom");
        Set<BlockPos> seen = new HashSet<>();
        ArrayDeque<BlockPos> queue = new ArrayDeque<>();
        seen.add(entry);
        queue.add(entry);
        while (!queue.isEmpty()) {
            BlockPos current = queue.remove();
            for (int[] d : new int[][]{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}) {
                BlockPos next = current.offset(d[0], 0, d[1]);
                if (palace.walk(next.getX(), next.getZ()) && seen.add(next)) queue.add(next);
            }
        }
        // Both side halls, both side bridges, both rear gardens/pavilions, garden bridge, hall approach.
        for (int[] target : new int[][]{{13, 43}, {50, 43}, {23, 43}, {39, 43},
                {21, 8}, {40, 8}, {10, 10}, {52, 10}, {31, 8}, {31, 33}})
            h.assertTrue(seen.contains(new BlockPos(target[0], 4, target[1])),
                    "Unreachable palace room/bridge: " + Arrays.toString(target));
        // Chests cannot be sealed in an inaccessible decorative alcove.
        for (BlockPos chest : palace.chests) {
            boolean reachable = false;
            for (Direction side : Direction.Plane.HORIZONTAL)
                reachable |= seen.contains(chest.relative(side));
            h.assertTrue(reachable, "No standing space next to palace chest: " + chest);
        }
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 40)
    public static void palaceBoundsRoutesAndAmenities(GameTestHelper h) {
        Capture palace = new Capture();
        h.assertTrue(palace.getBoundingBox().getXSpan() == 64
                && palace.getBoundingBox().getYSpan() == 32
                && palace.getBoundingBox().getZSpan() == 64, "New palace must declare a 64 x 32 x 64 footprint");
        palace.build();
        h.assertTrue(palace.chests.size() == 4, "Parent palace must retain exactly four loot chests");
        h.assertTrue(palace.at(9, 4, 33).is(Blocks.BOOKSHELF), "West archive shelves missing");
        h.assertTrue(palace.at(16, 4, 33).is(Blocks.LECTERN), "West archive reading station missing");
        h.assertTrue(palace.at(54, 4, 33).is(Blocks.SMITHING_TABLE), "East smithing station missing");
        h.assertTrue(palace.at(54, 4, 34).is(Blocks.BLAST_FURNACE), "East smelting station missing");
        h.assertTrue(palace.at(47, 4, 46).is(Blocks.ANVIL), "East repair anvil missing");
        h.assertTrue(palace.at(31, 3, 8).is(Blocks.DARK_OAK_PLANKS), "Rear pond bridge missing");
        assertRoutes(h, palace);
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 40)
    public static void palaceMainHallTransformAndMergedRoutes(GameTestHelper h) {
        Capture palace = new Capture();
        palace.build();
        List<StructurePiece> children = children(palace);
        h.assertTrue(children.size() == 1 && children.get(0) instanceof MainHallPiece,
                "New courtyard must have one main hall, without legacy towers over its pavilions");
        MainHallPiece hall = (MainHallPiece) children.get(0);
        BoundingBox box = hall.getBoundingBox();
        h.assertTrue(new BlockPos(box.minX(), box.minY(), box.minZ()).equals(palace.world(21, 3, 33)),
                "Main hall minimum world corner has wrong NORTH orientation transform");
        h.assertTrue(new BlockPos(box.maxX(), box.maxY(), box.maxZ()).equals(palace.world(42, 28, 14)),
                "Main hall maximum corner must stay within the declared palace");
        MainHallCapture capture = new MainHallCapture(hall, palace);
        capture.postProcess(null, null, null, RandomSource.create(7), box, new ChunkPos(ORIGIN), ORIGIN);
        h.assertTrue(capture.chests == 2 && palace.chests.size() == 4, "Keep two hall + four courtyard loot rolls");
        h.assertTrue(palace.at(31, 3, 33).is(Blocks.QUARTZ_STAIRS), "Hall steps must face the ceremonial avenue");
        h.assertTrue(palace.at(31, 6, 20).is(DynastyBlocks.DRAGON_THRONE.get()), "Throne transformed to wrong location");
        assertRoutes(h, palace);
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 40)
    public static void savedFortyEightBlockPalaceRetainsLegacyLayout(GameTestHelper h) {
        CompoundTag oldTag = new Capture().createTag(null);
        oldTag.putIntArray("BB", new int[]{ORIGIN.getX(), ORIGIN.getY(), ORIGIN.getZ(),
                ORIGIN.getX() + 47, ORIGIN.getY() + 27, ORIGIN.getZ() + 47});
        Capture restored = new Capture(oldTag);
        restored.build();
        h.assertTrue(restored.getBoundingBox().getXSpan() == 48 && restored.getBoundingBox().getYSpan() == 28
                        && restored.getBoundingBox().getZSpan() == 48,
                "Saved palace must not silently expand into neighbouring chunks");
        h.assertTrue(restored.chests.equals(Set.of(new BlockPos(7, 4, 7), new BlockPos(40, 4, 7),
                new BlockPos(7, 4, 40), new BlockPos(40, 4, 40))), "Saved palace chest locations changed");
        List<StructurePiece> children = children(restored);
        h.assertTrue(children.size() == 5 && children.stream().filter(p -> p instanceof PalaceTowerPiece).count() == 4,
                "Saved 48-block layout must retain its four tower children");
        BoundingBox hall = children.get(0).getBoundingBox();
        h.assertTrue(new BlockPos(hall.minX(), hall.minY(), hall.minZ()).equals(ORIGIN.offset(13, 3, 12)),
                "Legacy main hall anchor changed");
        Capture roundTrip = new Capture(restored.createTag(null));
        h.assertTrue(roundTrip.getBoundingBox().getXSpan() == 48 && roundTrip.getOrientation() == Direction.NORTH,
                "Legacy NBT round-trip changed footprint or orientation");
        h.succeed();
    }
}
