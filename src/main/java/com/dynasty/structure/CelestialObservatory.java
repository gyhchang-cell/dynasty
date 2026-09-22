package com.dynasty.structure;

import com.dynasty.DynastyBlocks;
import com.dynasty.worldgen.DynastyBuildKit;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.structure.BoundingBox;

/** Two walkable levels: a shaded scholar's ambulatory below an open armillary court. */
final class CelestialObservatory {
    private static final ResourceLocation LOOT = new ResourceLocation("dynasty", "chests/ritual_circle");

    static void build(StarAltarPiece p, WorldGenLevel w, BoundingBox b, RandomSource random) {
        var marble = DynastyBlocks.MARBLE_BLOCK.get().defaultBlockState();
        var jade = DynastyBlocks.JADE_BLOCK.get().defaultBlockState();
        var bronze = DynastyBlocks.BRONZE_BLOCK.get().defaultBlockState();
        var lamp = DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState();
        var air = Blocks.AIR.defaultBlockState();
        p.fill(w, b, 0, 0, 0, 25, 0, 25, marble);
        p.fill(w, b, 0, 1, 0, 25, 19, 25, air);
        p.walls(w, b, 1, 0, 1, 24, 0, 24, jade);
        p.fill(w, b, 7, 1, 7, 18, 3, 18, DynastyBlocks.PALACE_BRICKS.get().defaultBlockState());
        p.fill(w, b, 3, 4, 3, 22, 4, 22, marble);
        p.walls(w, b, 3, 4, 3, 22, 4, 22, jade);
        p.walls(w, b, 7, 4, 7, 18, 4, 18, bronze);

        // Lower-level piers are spaced to leave a two-block-wide walkable covered loop.
        for (int x : new int[]{3, 22}) for (int z : new int[]{3, 8, 17, 22}) {
            p.fill(w, b, x, 1, z, x, 3, z, Blocks.QUARTZ_PILLAR.defaultBlockState());
            p.set(w, b, x, 3, z + (z < 12 ? 1 : -1), lamp);
        }
        for (int z : new int[]{3, 22}) for (int x : new int[]{8, 17})
            p.fill(w, b, x, 1, z, x, 3, z, Blocks.QUARTZ_PILLAR.defaultBlockState());
        // Four grand flights rise from ground to the top court. No jumping full-block tiers.
        for (int i = 0; i < 4; i++) {
            int near = 1 + i, far = 24 - i;
            p.fill(w, b, 11, 0, far, 14, i, far, marble);
            p.fill(w, b, 11, i + 1, far, 14, i + 1, far,
                    DynastyBuildKit.facing(Blocks.QUARTZ_STAIRS.defaultBlockState(), Direction.NORTH));
            p.fill(w, b, 11, 0, near, 14, i, near, marble);
            p.fill(w, b, 11, i + 1, near, 14, i + 1, near,
                    DynastyBuildKit.facing(Blocks.QUARTZ_STAIRS.defaultBlockState(), Direction.SOUTH));
            p.fill(w, b, near, 0, 11, near, i, 14, marble);
            p.fill(w, b, near, i + 1, 11, near, i + 1, 14,
                    DynastyBuildKit.facing(Blocks.QUARTZ_STAIRS.defaultBlockState(), Direction.EAST));
            p.fill(w, b, far, 0, 11, far, i, 14, marble);
            p.fill(w, b, far, i + 1, 11, far, i + 1, 14,
                    DynastyBuildKit.facing(Blocks.QUARTZ_STAIRS.defaultBlockState(), Direction.WEST));
            // Cut the terrace deck away above lower steps: no forehead-height ledges.
            p.fill(w, b, 11, i + 2, near, 14, 8, near, air);
            p.fill(w, b, 11, i + 2, far, 14, 8, far, air);
            p.fill(w, b, near, i + 2, 11, near, 8, 14, air);
            p.fill(w, b, far, i + 2, 11, far, 8, 14, air);
            // Open arches preserve the lower circuit underneath the four upper flights.
            if (i >= 2) {
                p.fill(w, b, 11, 1, near, 14, 2, near, air);
                p.fill(w, b, 11, 1, far, 14, 2, far, air);
                p.fill(w, b, near, 1, 11, near, 2, 14, air);
                p.fill(w, b, far, 1, 11, far, 2, 14, air);
            }
        }
        // Corner chambers have distinct usable furnishings, with the central aisles left open.
        for (int x : new int[]{5, 20}) for (int z : new int[]{6, 19}) {
            p.set(w, b, x, 1, z, Blocks.LECTERN.defaultBlockState());
            p.set(w, b, x, 3, z, lamp);
        }
        p.set(w, b, 5, 1, 8, Blocks.CARTOGRAPHY_TABLE.defaultBlockState());
        p.fill(w, b, 7, 1, 4, 9, 2, 4, Blocks.BOOKSHELF.defaultBlockState());
        p.set(w, b, 20, 1, 17, Blocks.BREWING_STAND.defaultBlockState());
        p.set(w, b, 18, 1, 21, Blocks.CRAFTING_TABLE.defaultBlockState());
        p.lootChest(w, b, random, 5, 1, 16, LOOT);
        p.lootChest(w, b, random, 20, 1, 9, LOOT);

        // Balustrades are intentionally interrupted at all four stair arrivals.
        for (int i = 3; i <= 22; i++) {
            if (i >= 10 && i <= 15) continue;
            for (int edge : new int[]{3, 22}) {
                p.set(w, b, i, 5, edge, Blocks.SANDSTONE_WALL.defaultBlockState());
                p.set(w, b, edge, 5, i, Blocks.SANDSTONE_WALL.defaultBlockState());
            }
        }
        for (int x : new int[]{6, 19}) for (int z : new int[]{6, 19}) {
            p.set(w, b, x, 5, z, bronze);
            p.fill(w, b, x, 6, z, x, 10, z, Blocks.QUARTZ_PILLAR.defaultBlockState());
            p.set(w, b, x, 11, z, jade);
            p.set(w, b, x, 12, z, lamp);
            p.set(w, b, x, 13, z, Blocks.LIGHTNING_ROD.defaultBlockState());
        }
        // Eave fragments and raised corner finials frame the silhouette without hiding the sky.
        for (int z : new int[]{5, 20}) {
            p.fill(w, b, 5, 10, z, 9, 10, z, Blocks.DARK_PRISMARINE_SLAB.defaultBlockState());
            p.fill(w, b, 16, 10, z, 20, 10, z, Blocks.DARK_PRISMARINE_SLAB.defaultBlockState());
        }
        for (int x : new int[]{5, 20}) {
            p.fill(w, b, x, 10, 5, x, 10, 9, Blocks.DARK_PRISMARINE_SLAB.defaultBlockState());
            p.fill(w, b, x, 10, 16, x, 10, 20, Blocks.DARK_PRISMARINE_SLAB.defaultBlockState());
        }
        // A block-built, three-dimensional armillary sphere; all geometry is static and bounded.
        for (int a = -4; a <= 4; a++) for (int c = -4; c <= 4; c++) {
            int rr = a * a + c * c;
            if (rr < 13 || rr > 19) continue;
            p.set(w, b, 12 + a, 13 + c, 12, bronze);
            p.set(w, b, 12, 13 + c, 12 + a, jade);
            p.set(w, b, 12 + a, 13, 12 + c, bronze);
        }
        p.set(w, b, 12, 13, 12, Blocks.SEA_LANTERN.defaultBlockState());
        for (int x : new int[]{8, 16}) p.fill(w, b, x, 5, 12, x, 9, 12, Blocks.QUARTZ_PILLAR.defaultBlockState());
        p.set(w, b, 12, 5, 12, DynastyBlocks.RITUAL_ALTAR.get().defaultBlockState());
        p.set(w, b, 10, 5, 10, DynastyBlocks.TAIKO_DRUM.get().defaultBlockState());
        p.set(w, b, 14, 5, 10, DynastyBlocks.CHIME_BELL.get().defaultBlockState());
        // Flat inlay, not cubes blocking the path; seven illuminated stars cross the court.
        for (int[] s : new int[][]{{8,18},{9,17},{10,16},{12,16},{14,17},{16,17},{17,15}})
            p.set(w, b, s[0], 4, s[1], Blocks.SEA_LANTERN.defaultBlockState());
    }
}
