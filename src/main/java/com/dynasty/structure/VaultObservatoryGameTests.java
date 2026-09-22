package com.dynasty.structure;

import com.dynasty.Dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

import java.util.ArrayDeque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/** Assertions against the actual production placement stream, not a hand-copied floor plan. */
@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class VaultObservatoryGameTests {
    private static class Layout {
        final Map<BlockPos, BlockState> cells = new HashMap<>();
        int chests;
        int writes;
        void put(int x, int y, int z, BlockState state, int size, int height) {
            if (x < 0 || x >= size || z < 0 || z >= size || y < 0 || y >= height)
                throw new AssertionError("Placement outside bounding box: " + x + "," + y + "," + z);
            cells.put(new BlockPos(x, y, z), state);
            writes++;
        }
        BlockState at(BlockPos pos) { return cells.getOrDefault(pos, Blocks.AIR.defaultBlockState()); }
        boolean walk(BlockPos feet) {
            var floor = at(feet.below());
            return !floor.isAir() && floor.getFluidState().isEmpty()
                    && at(feet).isAir() && at(feet.above()).isAir();
        }
        Set<BlockPos> reachable(BlockPos start, boolean stairs) {
            Set<BlockPos> seen = new HashSet<>();
            ArrayDeque<BlockPos> todo = new ArrayDeque<>();
            seen.add(start); todo.add(start);
            while (!todo.isEmpty()) {
                var here = todo.remove();
                for (int[] d : new int[][]{{1,0},{-1,0},{0,1},{0,-1}}) {
                    var next = here.offset(d[0], 0, d[1]);
                    if (walk(next) && seen.add(next)) todo.add(next);
                    if (!stairs) continue;
                    var up = next.above();
                    // Permit an actual stair step, not a hidden requirement to jump a full cube.
                    if (at(next).getBlock() instanceof StairBlock && at(here.above(2)).isAir()
                            && walk(up) && seen.add(up)) todo.add(up);
                    var down = next.below();
                    if (at(here.below()).getBlock() instanceof StairBlock && at(next.above()).isAir()
                            && walk(down) && seen.add(down)) todo.add(down);
                }
            }
            return seen;
        }
    }

    private static final class TombCapture extends TombPiece {
        final Layout layout = new Layout();
        TombCapture() { super(DynastyStructures.TOMB_PIECE.get(), 0, BlockPos.ZERO); }
        @Override protected void set(WorldGenLevel w, BoundingBox b, int x, int y, int z, BlockState state) {
            layout.put(x, y, z, state, SIZE, HEIGHT);
        }
        @Override void lootChest(WorldGenLevel w, BoundingBox b, RandomSource r, int x, int y, int z, ResourceLocation table) {
            if (!table.equals(new ResourceLocation("dynasty", "chests/imperial_mausoleum")))
                throw new AssertionError("Unexpected tomb loot tier");
            layout.chests++;
            set(w, b, x, y, z, Blocks.CHEST.defaultBlockState());
        }
    }
    private static final class StarCapture extends StarAltarPiece {
        final Layout layout = new Layout();
        StarCapture() { super(DynastyStructures.STAR_ALTAR_PIECE.get(), 0, BlockPos.ZERO); }
        @Override protected void set(WorldGenLevel w, BoundingBox b, int x, int y, int z, BlockState state) {
            layout.put(x, y, z, state, SIZE, HEIGHT);
        }
        @Override void lootChest(WorldGenLevel w, BoundingBox b, RandomSource r, int x, int y, int z, ResourceLocation table) {
            if (!table.equals(new ResourceLocation("dynasty", "chests/ritual_circle")))
                throw new AssertionError("Unexpected observatory loot tier");
            layout.chests++;
            set(w, b, x, y, z, Blocks.CHEST.defaultBlockState());
        }
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 40)
    public static void tombRoomsAreConnectedAndInsideSavedBounds(GameTestHelper h) {
        var p = new TombCapture();
        p.postProcess(null, null, null, RandomSource.create(1), p.getBoundingBox(), null, BlockPos.ZERO);
        var map = p.layout;
        h.assertTrue(map.chests == 4, "Mausoleum must preserve four original-tier chests");
        h.assertTrue(map.writes < 30000, "Tomb placement budget grew unexpectedly");
        var reached = map.reachable(new BlockPos(19, 1, 39), false);
        for (int[] point : new int[][]{{19,20},{19,13},{6,12},{33,12},{6,20},{33,20},{7,30},{32,30},
                {6,9},{33,9},{7,27},{32,27}})
            h.assertTrue(reached.contains(new BlockPos(point[0], 1, point[1])),
                    "Unreachable tomb room/loot approach: " + point[0] + "," + point[1]);
        h.assertTrue(reached.size() >= 600, "Mausoleum no longer provides its broad connected floor area");
        h.assertTrue(map.at(new BlockPos(7,1,7)).is(Blocks.CARTOGRAPHY_TABLE), "Archive map desk missing");
        h.assertTrue(map.at(new BlockPos(36,1,7)).is(Blocks.DECORATED_POT), "Funerary urn niche missing");
        var saved = new CompoundTag();
        p.addAdditionalSaveData(null, saved);
        h.assertTrue(saved.getInt("DynastyTombLayout") == 2, "New starts must persist their layout version");
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 40)
    public static void observatoryHasFourStairsAndConnectedLowerGallery(GameTestHelper h) {
        var p = new StarCapture();
        p.postProcess(null, null, null, RandomSource.create(1), p.getBoundingBox(), null, BlockPos.ZERO);
        var map = p.layout;
        h.assertTrue(map.chests == 2, "Observatory must preserve two original-tier chests");
        h.assertTrue(map.writes < 17000, "Observatory placement budget grew unexpectedly");
        var lower = map.reachable(new BlockPos(4, 1, 5), false);
        for (int[] point : new int[][]{{4,16},{21,9},{5,5},{20,20},{12,4},{12,21},{4,12},{21,12}})
            h.assertTrue(lower.contains(new BlockPos(point[0],1,point[1])),
                    "Blocked lower cloister: " + point[0] + "," + point[1]);
        for (int[] entrance : new int[][]{{12,25},{12,0},{0,12},{25,12}}) {
            var reached = map.reachable(new BlockPos(entrance[0],1,entrance[1]), true);
            h.assertTrue(reached.contains(new BlockPos(12,5,16)), "Stair does not reach upper star court");
        }
        h.assertTrue(map.at(new BlockPos(12,13,12)).is(Blocks.SEA_LANTERN), "Armillary sphere core missing");
        h.assertTrue(map.at(new BlockPos(8,4,18)).is(Blocks.SEA_LANTERN), "Flat star inlay missing");
        var saved = new CompoundTag();
        p.addAdditionalSaveData(null, saved);
        h.assertTrue(saved.getInt("DynastyStarLayout") == 2, "New starts must persist their layout version");
        h.succeed();
    }
}
