package com.dynasty.structure;

import com.dynasty.DynastyBlocks;
import com.dynasty.worldgen.DynastyBuildKit;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;

/** A processional tomb, four themed chambers and two routes around the central vault. */
final class MausoleumVault {
    private static final ResourceLocation LOOT = new ResourceLocation("dynasty", "chests/imperial_mausoleum");

    static void build(TombPiece p, WorldGenLevel w, BoundingBox b, RandomSource random) {
        var dark = Blocks.DEEPSLATE_BRICKS.defaultBlockState();
        var tile = Blocks.POLISHED_DEEPSLATE.defaultBlockState();
        var jade = DynastyBlocks.JADE_BLOCK.get().defaultBlockState();
        var bronze = DynastyBlocks.BRONZE_BLOCK.get().defaultBlockState();
        var marble = DynastyBlocks.MARBLE_BLOCK.get().defaultBlockState();
        var lamp = DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState();
        var air = Blocks.AIR.defaultBlockState();

        // Independent sealed volumes, never excavation of the entire bounding-box cube.
        chamber(p, w, b, 10, 3, 29, 23, 11);
        chamber(p, w, b, 14, 24, 25, 38, 7);
        chamber(p, w, b, 2, 5, 9, 16, 7);
        chamber(p, w, b, 30, 5, 37, 16, 7);
        chamber(p, w, b, 2, 25, 11, 35, 7);
        chamber(p, w, b, 28, 25, 37, 35, 7);
        // Side loops link the southern galleries to the northern archive/ossuary.
        chamber(p, w, b, 4, 16, 8, 25, 5);
        chamber(p, w, b, 31, 16, 35, 25, 5);
        passage(p, w, b, 5, 15, 7, 26);
        passage(p, w, b, 32, 15, 34, 26);
        passage(p, w, b, 8, 11, 11, 13);
        passage(p, w, b, 28, 11, 31, 13);
        passage(p, w, b, 10, 29, 15, 31);
        passage(p, w, b, 24, 29, 29, 31);
        passage(p, w, b, 17, 22, 22, 39);
        // The long main aisle inherits the hall's high roof; only side tunnels stay low.
        p.fill(w, b, 17, 5, 24, 22, 6, 38, air);
        p.fill(w, b, 17, 5, 22, 22, 7, 23, air);
        p.fill(w, b, 17, 8, 23, 22, 8, 24, dark);

        // Inlaid main axis guides the player; the open arena stays sixteen blocks wide.
        p.fill(w, b, 18, 0, 12, 21, 0, 39, jade);
        for (int z = 14; z <= 36; z += 4) {
            p.set(w, b, 18, 0, z, bronze);
            p.set(w, b, 21, 0, z, bronze);
        }
        p.walls(w, b, 12, 0, 5, 27, 0, 21, marble);
        // Six tall side piers carry alternating ribs and a tiered coffer, not a flat lid.
        for (int x : new int[]{11, 28}) for (int z : new int[]{6, 13, 20}) {
            p.fill(w, b, x, 1, z, x, 9, z, tile);
            p.set(w, b, x, 2, z, bronze);
            p.set(w, b, x, 8, z, jade);
            p.set(w, b, x, 9, z, lamp);
        }
        for (int z : new int[]{6, 13, 20}) {
            p.fill(w, b, 12, 9, z, 14, 9, z, dark);
            p.fill(w, b, 25, 9, z, 27, 9, z, dark);
            p.fill(w, b, 15, 10, z, 24, 10, z, tile);
            p.set(w, b, 19, 10, z, lamp);
            p.set(w, b, 20, 10, z, lamp);
        }
        p.fill(w, b, 15, 11, 7, 24, 11, 18, jade);
        p.fill(w, b, 16, 12, 8, 23, 12, 17, dark);
        p.fill(w, b, 17, 13, 9, 22, 13, 16, tile);

        // Processional entrance: repeated stone arches, recessed guardian niches and lamps.
        for (int z : new int[]{27, 33, 37}) {
            for (int x : new int[]{15, 24}) {
                p.fill(w, b, x, 1, z, x, 5, z, tile);
                p.set(w, b, x, 4, z, lamp);
            }
            p.fill(w, b, 16, 5, z, 17, 5, z, dark);
            p.fill(w, b, 22, 5, z, 23, 5, z, dark);
            p.fill(w, b, 18, 6, z, 21, 6, z, bronze);
        }
        for (int x : new int[]{16, 23}) for (int z : new int[]{25, 30, 35}) {
            p.set(w, b, x, 1, z, Blocks.CHISELED_DEEPSLATE.defaultBlockState());
            p.set(w, b, x, 2, z, DynastyBlocks.INCENSE_BURNER.get().defaultBlockState());
        }
        for (int x : new int[]{16, 23}) {
            p.fill(w, b, x, 0, 39, x, 5, 39, marble);
            p.set(w, b, x, 6, 39, jade);
        }
        p.fill(w, b, 17, 5, 39, 22, 5, 39, dark);
        p.fill(w, b, 18, 6, 39, 21, 6, 39, bronze);

        // Northern stepped dais and a visibly separate sarcophagus, with space all around.
        p.fill(w, b, 16, 1, 6, 23, 1, 10, marble);
        p.fill(w, b, 17, 1, 11, 22, 1, 11,
                DynastyBuildKit.facing(Blocks.QUARTZ_STAIRS.defaultBlockState(), Direction.NORTH));
        p.fill(w, b, 18, 2, 7, 21, 2, 9, dark);
        p.fill(w, b, 18, 3, 7, 21, 3, 9, Blocks.DEEPSLATE_TILE_SLAB.defaultBlockState());
        p.fill(w, b, 19, 3, 7, 20, 3, 9, jade);
        for (int x : new int[]{15, 24}) {
            p.set(w, b, x, 1, 7, DynastyBlocks.ALTAR.get().defaultBlockState());
            p.set(w, b, x, 1, 10, DynastyBlocks.INCENSE_BURNER.get().defaultBlockState());
        }
        // Archive: book niches and a map desk. Opposite chamber: funerary urns and chimes.
        for (int z : new int[]{7, 10, 14}) {
            p.fill(w, b, 3, 1, z, 3, 3, z, Blocks.BOOKSHELF.defaultBlockState());
            p.set(w, b, 4, 1, z, Blocks.LECTERN.defaultBlockState());
            p.set(w, b, 36, 1, z, Blocks.DECORATED_POT.defaultBlockState());
            p.set(w, b, 36, 3, z, lamp);
        }
        p.set(w, b, 7, 1, 7, Blocks.CARTOGRAPHY_TABLE.defaultBlockState());
        p.set(w, b, 32, 1, 7, DynastyBlocks.CHIME_BELL.get().defaultBlockState());
        // South galleries give distinct silhouettes instead of four empty boxes.
        for (int z : new int[]{27, 31, 33}) {
            p.set(w, b, 3, 1, z, Blocks.CHISELED_DEEPSLATE.defaultBlockState());
            p.set(w, b, 3, 2, z, DynastyBlocks.SCREEN.get().defaultBlockState());
            p.set(w, b, 36, 1, z, Blocks.SMITHING_TABLE.defaultBlockState());
        }
        p.set(w, b, 8, 1, 33, DynastyBlocks.TAIKO_DRUM.get().defaultBlockState());
        p.set(w, b, 31, 1, 33, Blocks.GRINDSTONE.defaultBlockState());
        // Same four original-tier chests: richer exploration, no multiplication of loot.
        p.lootChest(w, b, random, 7, 1, 9, LOOT);
        p.lootChest(w, b, random, 32, 1, 9, LOOT);
        p.lootChest(w, b, random, 8, 1, 27, LOOT);
        p.lootChest(w, b, random, 31, 1, 27, LOOT);
    }

    private static void chamber(TombPiece p, WorldGenLevel w, BoundingBox b,
                                int x0, int z0, int x1, int z1, int top) {
        var wall = Blocks.DEEPSLATE_BRICKS.defaultBlockState();
        p.fill(w, b, x0, 0, z0, x1, 0, z1, Blocks.POLISHED_DEEPSLATE.defaultBlockState());
        p.fill(w, b, x0 + 1, 1, z0 + 1, x1 - 1, top - 1, z1 - 1, Blocks.AIR.defaultBlockState());
        p.walls(w, b, x0, 1, z0, x1, top, z1, wall);
        p.fill(w, b, x0, top, z0, x1, top, z1, wall);
        // Relief panels, continuous trim and corner quoins break up broad wall surfaces.
        p.walls(w, b, x0, 1, z0, x1, 1, z1, DynastyBlocks.PALACE_BRICKS.get().defaultBlockState());
        p.walls(w, b, x0, top - 1, z0, x1, top - 1, z1, DynastyBlocks.BRONZE_BLOCK.get().defaultBlockState());
        for (int x : new int[]{x0, x1}) for (int z : new int[]{z0, z1})
            p.fill(w, b, x, 1, z, x, top, z, Blocks.CHISELED_DEEPSLATE.defaultBlockState());
        p.set(w, b, (x0 + x1) / 2, top - 1, (z0 + z1) / 2,
                DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState());
    }

    private static void passage(TombPiece p, WorldGenLevel w, BoundingBox b,
                                int x0, int z0, int x1, int z1) {
        p.fill(w, b, x0, 0, z0, x1, 0, z1, DynastyBlocks.MARBLE_BLOCK.get().defaultBlockState());
        p.fill(w, b, x0, 1, z0, x1, 4, z1, Blocks.AIR.defaultBlockState());
        p.fill(w, b, x0, 5, z0, x1, 5, z1, Blocks.DEEPSLATE_TILES.defaultBlockState());
    }
}
