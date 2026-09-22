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
 * 国子监：四面围墙的院落、明伦堂（藏书）、东西厢房、神道石碑与泮池。
 * Imperial Academy: a walled courtyard with the lecture hall (books), side rooms,
 * a stele-lined approach and the semicircular pond.
 */
public class AcademyPiece extends DynastyStructurePiece {

    public static final int SIZE = 46;
    public static final int HEIGHT = 18;
    private static final ResourceLocation LOOT = new ResourceLocation("dynasty", "chests/temple");

    public AcademyPiece(StructurePieceType type, int genDepth, BlockPos pos) {
        super(type, genDepth,
                makeBoundingBox(pos.getX(), pos.getY(), pos.getZ(), Direction.NORTH, SIZE, HEIGHT, SIZE));
        this.setOrientation(Direction.NORTH);
    }

    public AcademyPiece(StructurePieceType type, CompoundTag tag) {
        super(type, tag);
    }

    void lootChest(WorldGenLevel level, BoundingBox box, RandomSource random, int x,int y,int z,ResourceLocation table) {
        createChest(level,box,random,x,y,z,table);
    }

    @Override
    public void postProcess(WorldGenLevel level, StructureManager manager, ChunkGenerator generator,
                            RandomSource random, BoundingBox box, ChunkPos chunkPos, BlockPos pos) {
        // Persisted old starts retain their 34-block layout, including not-yet-generated chunks.
        if (getBoundingBox().getXSpan() >= SIZE) {
            AcademyCourtyard.build(this, level, box, random);
            return;
        }
        BlockState brick = DynastyBlocks.PALACE_BRICKS.get().defaultBlockState();
        BlockState marble = DynastyBlocks.MARBLE_BLOCK.get().defaultBlockState();
        BlockState jade = DynastyBlocks.JADE_BLOCK.get().defaultBlockState();
        BlockState bronze = DynastyBlocks.BRONZE_BLOCK.get().defaultBlockState();
        BlockState pillar = DynastyBlocks.CRIMSON_PILLAR.get().defaultBlockState();
        BlockState lantern = DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState();
        BlockState shelf = Blocks.BOOKSHELF.defaultBlockState();
        BlockState lectern = Blocks.LECTERN.defaultBlockState();
        BlockState air = Blocks.AIR.defaultBlockState();

        // 1) 台基与院墙 / platform and enclosure wall
        fill(level, box, 0, 0, 0, SIZE - 1, 0, SIZE - 1, marble);
        walls(level, box, 0, 1, 0, SIZE - 1, 3, SIZE - 1, brick);
        walls(level, box, 0, 4, 0, SIZE - 1, 4, SIZE - 1,Blocks.DARK_PRISMARINE_SLAB.defaultBlockState());
        fill(level, box, 15, 1, 32, 18, 3, 33, air);
        for(int x:new int[]{14,19}) {
            fill(level,box,x,1,33,x,4,33,pillar);
            set(level,box,x,5,33,lantern);
        }

        // 2) 明伦堂（讲堂）/ lecture hall
        walls(level, box, 10, 1, 6, 23, 8, 19, brick);
        fill(level, box, 11, 1, 7, 22, 1, 18, jade);                    // 地面 / floor
        fill(level, box, 11, 2, 7, 22, 7, 18, air);
        glazedRoof(level,box,9,5,24,20,8,4);
        fill(level,box,13,12,12,20,12,13,jade);

        for (int[] c : new int[][]{{12, 8}, {12, 17}, {21, 8}, {21, 17}}) {   // 讲堂立枨
            for (int y = 2; y <= 8; y++) {
                set(level, box, c[0], y, c[1], pillar);
            }
            set(level, box, c[0], 9, c[1], lantern);
        }
        fill(level, box, 12, 2, 7, 21, 2, 7, shelf);                    // 藏书墙 / shelves
        fill(level, box, 12, 2, 18, 21, 2, 18, shelf);
        set(level, box, 16, 2, 12, lectern);                            // 讲案 / lectern
        set(level, box, 17, 2, 12, lectern);
        set(level, box, 16, 3, 10, bronze);

        // 3) 东西厢房 / side rooms
        walls(level, box, 2, 1, 6, 8, 5, 19, brick);
        fill(level, box, 3, 1, 7, 7, 1, 18, marble);
        fill(level, box, 3, 2, 7, 7, 4, 18, air);
        glazedRoof(level,box,1,5,9,20,6,3);
        walls(level, box, 25, 1, 6, 31, 5, 19, brick);
        fill(level, box, 26, 1, 7, 30, 1, 18, marble);
        fill(level, box, 26, 2, 7, 30, 4, 18, air);
        glazedRoof(level,box,24,5,32,20,6,3);

        // Open usable doors and fit symmetrical recessed lattice windows.
        fill(level,box,16,2,19,17,4,19,air);
        fill(level,box,8,2,12,8,3,13,air);
        fill(level,box,25,2,12,25,3,13,air);
        var window=Blocks.DARK_OAK_FENCE.defaultBlockState();
        for(int x:new int[]{12,13,20,21})fill(level,box,x,4,19,x,5,19,window);
        for(int z:new int[]{8,9,16,17}) {
            fill(level,box,10,4,z,10,5,z,window);
            fill(level,box,23,4,z,23,5,z,window);
        }

        // 4) 神道：石刻与灯笼 / stone-lined approach
        fill(level, box, 15, 1, 20, 18, 1, 31, marble);
        for (int z = 21; z <= 30; z += 3) {
            for (int y = 1; y <= 4; y++) {
                set(level, box, 14, y, z, marble);
                set(level, box, 19, y, z, marble);
            }
            set(level, box, 14, 3, z, DynastyBlocks.PLAQUE.get().defaultBlockState());
            set(level, box, 19, 3, z, DynastyBlocks.PLAQUE.get().defaultBlockState());
            set(level, box, 14, 5, z, lantern);
            set(level, box, 19, 5, z, lantern);
        }

        // 5) 东西泮池（对称两池）/ twin ponds with a stone railing
        for (int x1 : new int[]{5, 21}) {
            fill(level, box, x1, 1, 23, x1 + 5, 1, 28, Blocks.WATER.defaultBlockState());
            fill(level, box, x1 - 1, 2, 22, x1 + 6, 2, 29, marble);      // 石栏 / railing
            fill(level, box, x1, 2, 23, x1 + 5, 2, 28, air);
            fill(level, box, x1, 3, 23, x1 + 5, 3, 28, air);
            for (int[] c : new int[][]{{x1 - 1, 22}, {x1 + 6, 22}, {x1 - 1, 29}, {x1 + 6, 29}}) {
                set(level, box, c[0], 3, c[1], bronze);                  // 柱头 / posts
            }
        }

        // 6) 供品与藏书箱 / offerings and chests
        set(level, box, 16, 1, 20, DynastyBlocks.CHIME_BELL.get().defaultBlockState());
        set(level, box, 17, 1, 20, DynastyBlocks.INCENSE_BURNER.get().defaultBlockState());
        set(level, box, 4, 4, 10, pillar);
        set(level, box, 29, 4, 10, pillar);
        createChest(level, box, random, 4, 2, 12, LOOT);
        createChest(level, box, random, 29, 2, 12, LOOT);
        createChest(level, box, random, 12, 2, 16, LOOT);
    }
}
