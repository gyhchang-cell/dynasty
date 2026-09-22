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
 * 观星台：五层台基、八卦立柱、中央祭坛与地面上的星图（北斗七星）。
 * Star Altar: five stepped tiers, eight trigram pillars, a central altar and
 * a star chart (the Big Dipper) laid into the platform.
 */
public class StarAltarPiece extends DynastyStructurePiece {

    public static final int SIZE = 26;
    public static final int HEIGHT = 20;
    private static final ResourceLocation LOOT = new ResourceLocation("dynasty", "chests/ritual_circle");
    private final boolean remastered;

    /** 北斗七星：平台面上的星位 / the Big Dipper laid into the platform */
    private static final int[][] DIPPER = {
            {8, 20}, {9, 19}, {10, 18}, {11, 16}, {13, 15}, {15, 14}, {17, 13},
    };

    /** 八卦方位上的八根立柱 / eight trigram pillars */
    private static final int[][] PILLARS = {
            {7, 8}, {8, 7}, {17, 7}, {18, 8}, {7, 17}, {8, 18}, {17, 18}, {18, 17},
    };

    public StarAltarPiece(StructurePieceType type, int genDepth, BlockPos pos) {
        super(type, genDepth,
                makeBoundingBox(pos.getX(), pos.getY(), pos.getZ(), Direction.NORTH, SIZE, HEIGHT, SIZE));
        this.setOrientation(Direction.NORTH);
        this.remastered = true;
    }

    public StarAltarPiece(StructurePieceType type, CompoundTag tag) {
        super(type, tag);
        this.remastered = tag.getInt("DynastyStarLayout") >= 2;
    }

    @Override
    protected void addAdditionalSaveData(net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext ctx,
                                         CompoundTag tag) {
        super.addAdditionalSaveData(ctx, tag);
        tag.putInt("DynastyStarLayout", remastered ? 2 : 1);
    }

    void lootChest(WorldGenLevel level, BoundingBox box, RandomSource random, int x, int y, int z, ResourceLocation table) {
        createChest(level, box, random, x, y, z, table);
    }

    @Override
    public void postProcess(WorldGenLevel level, StructureManager manager, ChunkGenerator generator,
                            RandomSource random, BoundingBox box, ChunkPos chunkPos, BlockPos pos) {
        if (remastered) {
            CelestialObservatory.build(this, level, box, random);
            return;
        }
        BlockState marble = DynastyBlocks.MARBLE_BLOCK.get().defaultBlockState();
        BlockState jade = DynastyBlocks.JADE_BLOCK.get().defaultBlockState();
        BlockState bronze = DynastyBlocks.BRONZE_BLOCK.get().defaultBlockState();
        BlockState pillar = DynastyBlocks.CRIMSON_PILLAR.get().defaultBlockState();
        BlockState lantern = DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState();

        // 1) 五层台基 / five stepped tiers
        fill(level, box, 0, 0, 0, 25, 0, 25, marble);
        fill(level, box, 1, 1, 1, 24, 1, 24, marble);
        fill(level, box, 3, 2, 3, 22, 2, 22, marble);
        fill(level, box, 5, 3, 5, 20, 3, 20, marble);
        fill(level, box, 7, 4, 7, 18, 4, 18, jade);

        // 2) 南面石阶 / southern stairway
        for (int i = 0; i <= 3; i++) {
            fill(level, box, 12, 1 + i, 25 - i, 13, 1 + i, 26 - i, marble);
        }

        // 3) 八卦立柱与灯 / eight trigram pillars with lanterns
        for (int[] c : PILLARS) {
            for (int y = 5; y <= 12; y++) {
                set(level, box, c[0], y, c[1], pillar);
            }
            set(level, box, c[0], 13, c[1], jade);
            set(level, box, c[0], 14, c[1], lantern);
        }

        // 4) 中央祭坛 / central altar
        for (int x = 12; x <= 13; x++) {
            for (int z = 12; z <= 13; z++) {
                set(level, box, x, 5, z, DynastyBlocks.RITUAL_ALTAR.get().defaultBlockState());
            }
        }
        set(level, box, 11, 5, 12, DynastyBlocks.TAIKO_DRUM.get().defaultBlockState());
        set(level, box, 14, 5, 13, DynastyBlocks.CHIME_BELL.get().defaultBlockState());
        set(level, box, 12, 5, 11, bronze);
        set(level, box, 13, 5, 14, bronze);

        // 5) 平台上的星图 / the star chart
        for (int[] p : DIPPER) {
            set(level, box, p[0], 5, p[1], jade);
        }
        set(level, box, 8, 5, 8, bronze);
        set(level, box, 17, 5, 8, bronze);
        set(level, box, 8, 5, 17, bronze);
        set(level, box, 17, 5, 17, bronze);

        // 6) 供箱 / offering chests
        createChest(level, box, random, 9, 5, 9, LOOT);
        createChest(level, box, random, 16, 5, 16, LOOT);
    }
}
