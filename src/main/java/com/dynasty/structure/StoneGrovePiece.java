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
 * 皇陵石刻：享殿、神道两侧的石像生与石碑林、南端的石阙。
 * Imperial Stone Grove: an offering hall, spirit-path statues, two rows of stelae
 * and a stone gate tower at the southern end.
 */
public class StoneGrovePiece extends DynastyStructurePiece {

    public static final int SIZE = 32;
    public static final int HEIGHT = 14;
    private static final ResourceLocation LOOT = new ResourceLocation("dynasty", "chests/imperial_tomb");

    public StoneGrovePiece(StructurePieceType type, int genDepth, BlockPos pos) {
        super(type, genDepth,
                makeBoundingBox(pos.getX(), pos.getY(), pos.getZ(), Direction.NORTH, SIZE, HEIGHT, SIZE));
        this.setOrientation(Direction.NORTH);
    }

    public StoneGrovePiece(StructurePieceType type, CompoundTag tag) {
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
        BlockState plaque = DynastyBlocks.PLAQUE.get().defaultBlockState();
        BlockState air = Blocks.AIR.defaultBlockState();

        // 1) 地面与神道 / pavement and the spirit path
        fill(level, box, 0, 0, 0, SIZE - 1, 0, SIZE - 1, marble);
        fill(level, box, 15, 0, 0, 16, 0, SIZE - 1, jade);
        for (int z = 2; z <= 30; z += 5) {
            set(level, box, 14, 3, z, lantern);
            set(level, box, 17, 3, z, lantern);
        }

        // 2) 享殿 / offering hall
        walls(level, box, 11, 1, 2, 20, 8, 9, brick);
        fill(level, box, 12, 1, 3, 19, 1, 8, marble);
        fill(level, box, 12, 2, 3, 19, 7, 8, air);
        fill(level, box, 10, 8, 1, 21, 8, 10, brick);
        fill(level, box, 12, 9, 3, 19, 9, 8, brick);
        for (int[] c : new int[][]{{12, 3}, {12, 8}, {19, 3}, {19, 8}}) {
            for (int y = 2; y <= 8; y++) {
                set(level, box, c[0], y, c[1], pillar);
            }
            set(level, box, c[0], 9, c[1], lantern);
        }
        fill(level, box, 15, 2, 4, 16, 2, 5, DynastyBlocks.ALTAR.get().defaultBlockState());
        set(level, box, 15, 2, 7, DynastyBlocks.INCENSE_BURNER.get().defaultBlockState());
        set(level, box, 16, 2, 7, DynastyBlocks.CHIME_BELL.get().defaultBlockState());
        createChest(level, box, random, 12, 2, 3, LOOT);
        createChest(level, box, random, 19, 2, 3, LOOT);

        // 3) 石像生：神道两侧的四对造像 / four pairs of statues along the path
        for (int z = 12; z <= 27; z += 5) {
            for (int x1 : new int[]{10, 19}) {
                fill(level, box, x1, 1, z, x1 + 2, 1, z + 2, marble);
                set(level, box, x1 + 1, 2, z + 1, bronze);
                set(level, box, x1 + 1, 3, z + 1, marble);
                set(level, box, x1 + 1, 4, z + 1, jade);
                set(level, box, x1 + 1, 5, z + 1, plaque);
            }
        }

        // 4) 石碑林：东西各两列 / two rows of stelae on either side
        for (int z = 11; z <= 29; z += 3) {
            for (int x1 : new int[]{2, 5, 25, 28}) {
                for (int y = 1; y <= 4; y++) {
                    set(level, box, x1, y, z, marble);
                }
                set(level, box, x1, 5, z, plaque);
            }
        }

        // 5) 南端石阙 / stone gate tower at the south end
        for (int x1 : new int[]{13, 18}) {
            for (int y = 1; y <= 7; y++) {
                set(level, box, x1, y, 30, pillar);
            }
            set(level, box, x1, 8, 30, bronze);
            set(level, box, x1, 9, 30, lantern);
        }
        fill(level, box, 13, 7, 30, 18, 7, 30, brick);
        set(level, box, 15, 6, 30, DynastyBlocks.PLAQUE.get().defaultBlockState());
        set(level, box, 16, 6, 30, DynastyBlocks.PLAQUE.get().defaultBlockState());
    }
}
