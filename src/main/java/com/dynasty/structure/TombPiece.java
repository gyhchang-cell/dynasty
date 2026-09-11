package com.dynasty.structure;

import com.dynasty.DynastyBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;

/**
 * 帝陵地宫：墓道、两间耳室、主墓室、棺椁与陪葬品。
 * Imperial mausoleum: corridor, two side chambers, burial chamber, sarcophagus and grave goods.
 */
public class TombPiece extends DynastyStructurePiece {

    public static final int SIZE = 40;
    public static final int HEIGHT = 16;
    private static final ResourceLocation LOOT = new ResourceLocation("dynasty", "chests/imperial_mausoleum");

    public TombPiece(StructurePieceType type, int genDepth, BlockPos pos) {
        super(type, genDepth,
                makeBoundingBox(pos.getX(), pos.getY(), pos.getZ(), Direction.NORTH, SIZE, HEIGHT, SIZE));
        this.setOrientation(Direction.NORTH);
    }

    public TombPiece(StructurePieceType type, CompoundTag tag) {
        super(type, tag);
    }

    @Override
    public void postProcess(WorldGenLevel level, StructureManager manager, ChunkGenerator generator,
                            RandomSource random, BoundingBox box, ChunkPos chunkPos, BlockPos pos) {
        BlockState brick = DynastyBlocks.PALACE_BRICKS.get().defaultBlockState();
        BlockState marble = DynastyBlocks.MARBLE_BLOCK.get().defaultBlockState();
        BlockState jade = DynastyBlocks.JADE_BLOCK.get().defaultBlockState();
        BlockState bronze = DynastyBlocks.BRONZE_BLOCK.get().defaultBlockState();
        BlockState pillar = DynastyBlocks.CRIMSON_PILLAR.get().defaultBlockState();
        BlockState lantern = DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState();
        BlockState air = Blocks.AIR.defaultBlockState();

        // 1) 主墓室外壳（16x16，中空）/ burial chamber shell
        hollowShell(level, box, 12, 0, 12, 27, 9, 27, brick, air);
        fill(level, box, 13, 0, 13, 26, 0, 26, jade);
        fill(level, box, 13, 1, 13, 26, 1, 26, air);

        // 2) 甬道（自南向北）/ corridor from south
        fill(level, box, 18, 0, 28, 21, 6, 39, air);
        fill(level, box, 17, 0, 28, 22, 0, 39, marble);
        walls(level, box, 17, 1, 28, 22, 6, 39, brick);
        fill(level, box, 18, 7, 28, 21, 7, 39, brick);

        // 3) 耳室（东西各一）/ side chambers (east & west)
        hollowShell(level, box, 2, 0, 18, 10, 6, 26, brick, air);
        fill(level, box, 3, 0, 19, 9, 0, 25, marble);
        fill(level, box, 10, 1, 21, 11, 4, 23, air);
        hollowShell(level, box, 29, 0, 18, 37, 6, 26, brick, air);
        fill(level, box, 30, 0, 19, 36, 0, 25, marble);
        fill(level, box, 28, 1, 21, 29, 4, 23, air);

        // 4) 殿柱与长明灯 / pillars and eternal lanterns
        for (int[] c : new int[][]{{14, 14}, {14, 25}, {25, 14}, {25, 25}}) {
            for (int y = 1; y <= 8; y++) {
                set(level, box, c[0], y, c[1], pillar);
            }
            set(level, box, c[0], 9, c[1], lantern);
        }
        set(level, box, 20, 9, 20, lantern);
        set(level, box, 19, 9, 20, lantern);

        // 5) 棺椁与陪葬 / sarcophagus and grave goods
        fill(level, box, 18, 1, 16, 21, 2, 19, brick);
        fill(level, box, 19, 3, 17, 20, 3, 18, jade);
        for (int x = 15; x <= 24; x += 3) {
            set(level, box, x, 1, 22, bronze);
            set(level, box, x, 2, 22, goldish());
        }
        set(level, box, 14, 1, 16, DynastyBlocks.ALTAR.get().defaultBlockState());
        set(level, box, 25, 1, 16, DynastyBlocks.CHIME_BELL.get().defaultBlockState());
        set(level, box, 14, 1, 24, DynastyBlocks.INCENSE_BURNER.get().defaultBlockState());
        set(level, box, 25, 1, 24, DynastyBlocks.DRAGON_THRONE.get().defaultBlockState());

        // 6) 陪葬宝箱 / treasure chests
        createChest(level, box, random, 5, 1, 22, LOOT);
        createChest(level, box, random, 34, 1, 22, LOOT);
        createChest(level, box, random, 16, 1, 24, LOOT);
        createChest(level, box, random, 23, 1, 24, LOOT);
    }

    private BlockState goldish() {
        return DynastyBlocks.CRIMSON_PILLAR.get().defaultBlockState();
    }

    /** 生成带空气内腔的封闭外壳 / build a hollow shell filled with air */
    private void hollowShell(WorldGenLevel level, BoundingBox box, int x1, int y1, int z1,
                             int x2, int y2, int z2, BlockState wall, BlockState inner) {
        walls(level, box, x1, y1, z1, x2, y2, z2, wall);
        fill(level, box, x1, y2 + 1, z1, x2, y2 + 1, z2, wall);
        fill(level, box, x1, y1 - 1, z1, x2, y1 - 1, z2, wall);
        fill(level, box, x1 + 1, y1, z1 + 1, x2 - 1, y2, z2 - 1, inner);
    }
}
