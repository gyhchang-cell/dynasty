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
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.StructurePieceAccessor;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;

/**
 * 宫殿主体：台基、城墙、正门、御道、廊柱、御花园、宝箱。
 * Palace body: terrace, walls, main gate, path, colonnade, garden, treasure chests.
 */
public class PalacePiece extends DynastyStructurePiece {

    public static final int SIZE = 64;
    public static final int HEIGHT = 32;
    private static final ResourceLocation LOOT = new ResourceLocation("dynasty", "chests/dynasty_palace");

    public PalacePiece(StructurePieceType type, int genDepth, BlockPos pos) {
        super(type, genDepth,
                makeBoundingBox(pos.getX(), pos.getY(), pos.getZ(), Direction.NORTH, SIZE, HEIGHT, SIZE));
        this.setOrientation(Direction.NORTH);
    }

    public PalacePiece(StructurePieceType type, CompoundTag tag) {
        super(type, tag);
    }

    @Override
    public void addChildren(StructurePiece piece, StructurePieceAccessor accessor, RandomSource random) {
        if (this.boundingBox.getXSpan() == SIZE) {
            // NORTH reverses local Z: anchor the child's MIN world Z from its far local edge.
            accessor.addPiece(new MainHallPiece(DynastyStructures.MAIN_HALL_PIECE.get(), this.genDepth + 1,
                    world(21, 3, 14 + MainHallPiece.DEPTH - 1)));
            return;
        }
        int x = this.boundingBox.minX();
        int y = this.boundingBox.minY();
        int z = this.boundingBox.minZ();
        accessor.addPiece(new MainHallPiece(DynastyStructures.MAIN_HALL_PIECE.get(), this.genDepth + 1,
                new BlockPos(x + 13, y + 3, z + 12)));
        for (int[] corner : new int[][]{{3, 3}, {37, 3}, {3, 37}, {37, 37}}) {
            accessor.addPiece(new PalaceTowerPiece(DynastyStructures.PALACE_TOWER_PIECE.get(), this.genDepth + 1,
                    new BlockPos(x + corner[0], y + 3, z + corner[1])));
        }
    }

    @Override
    public void postProcess(WorldGenLevel level, StructureManager manager, ChunkGenerator generator,
                            RandomSource random, BoundingBox box, ChunkPos chunkPos, BlockPos pos) {
        // Already-saved 48-block pieces retain their old footprint and layout.
        if (this.boundingBox.getXSpan() == SIZE) {
            PalaceCourtyard.build(this, level, box, random);
            return;
        }
        BlockState brick = DynastyBlocks.PALACE_BRICKS.get().defaultBlockState();
        BlockState marble = DynastyBlocks.MARBLE_BLOCK.get().defaultBlockState();
        BlockState jade = DynastyBlocks.JADE_BLOCK.get().defaultBlockState();
        BlockState pillar = DynastyBlocks.CRIMSON_PILLAR.get().defaultBlockState();
        BlockState lantern = DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState();
        BlockState screen = DynastyBlocks.SCREEN.get().defaultBlockState();
        BlockState air = Blocks.AIR.defaultBlockState();

        // 1) 三层台基 / three-tier terrace
        fill(level, box, 0, 0, 0, 47, 0, 47, brick);
        fill(level, box, 1, 1, 1, 46, 1, 46, brick);
        fill(level, box, 3, 2, 3, 44, 2, 44, marble);
        fill(level, box, 5, 3, 5, 42, 3, 42, marble);

        // 2) 城墙 + 垛口 / walls + crenellations
        walls(level, box, 4, 4, 4, 43, 10, 43, brick);
        for (int i = 4; i <= 43; i += 2) {
            set(level, box, i, 11, 4, brick);
            set(level, box, i, 11, 43, brick);
            set(level, box, 4, 11, i, brick);
            set(level, box, 43, 11, i, brick);
        }

        // 3) 清空院内空间（子部件之后会再填充）/ clear the courtyard volume
        fill(level, box, 5, 4, 5, 42, 20, 42, air);

        // 4) 正门与后门 / main gate and back gate
        fill(level, box, 20, 4, 40, 27, 10, 43, air);
        fill(level, box, 18, 11, 39, 29, 11, 44, marble);
        fill(level, box, 19, 12, 40, 28, 12, 43, brick);
        for (int y = 4; y <= 10; y++) {
            set(level, box, 19, y, 43, pillar);
            set(level, box, 28, y, 43, pillar);
        }
        fill(level, box, 22, 4, 4, 25, 9, 6, air);

        // 5) 御道 / imperial path
        fill(level, box, 22, 3, 32, 25, 3, 39, jade);

        // 6) 廊柱与宫灯 / colonnade + lanterns
        for (int z = 15; z <= 36; z += 3) {
            for (int y = 4; y <= 9; y++) {
                set(level, box, 14, y, z, pillar);
                set(level, box, 33, y, z, pillar);
            }
            set(level, box, 14, 10, z, lantern);
            set(level, box, 33, 10, z, lantern);
        }

        // 7) 御花园 / imperial garden
        fill(level, box, 8, 3, 6, 39, 3, 10, Blocks.GRASS_BLOCK.defaultBlockState());
        for (int x = 10; x <= 38; x += 4) {
            set(level, box, x, 4, 8, DynastyBlocks.ALTAR.get().defaultBlockState());
            set(level, box, x, 5, 8, lantern);
        }

        // 8) 陈设 / furnishings
        set(level, box, 10, 4, 38, DynastyBlocks.TAIKO_DRUM.get().defaultBlockState());
        set(level, box, 37, 4, 38, DynastyBlocks.CHIME_BELL.get().defaultBlockState());
        set(level, box, 10, 4, 34, screen);
        set(level, box, 37, 4, 34, screen);
        set(level, box, 24, 4, 37, DynastyBlocks.INCENSE_BURNER.get().defaultBlockState());

        // 9) 宝箱 / treasure chests（坐标同样是局部坐标）
        createChest(level, box, random, 7, 4, 7, LOOT);
        createChest(level, box, random, 40, 4, 7, LOOT);
        createChest(level, box, random, 7, 4, 40, LOOT);
        createChest(level, box, random, 40, 4, 40, LOOT);

        // Walkable entry stairs instead of a three-block vertical terrace edge.
        for(int step=0;step<3;step++)fill(level,box,20,step+1,44-step,27,step+1,44-step,
                com.dynasty.worldgen.DynastyBuildKit.facing(Blocks.QUARTZ_STAIRS.defaultBlockState(),Direction.NORTH));
        // Shallow paired pools frame the approach without occupying the main hall or corner towers.
        for(int x:new int[]{16,28}) {
            fill(level,box,x,3,34,x+3,3,38,brick);
            fill(level,box,x+1,3,35,x+2,3,37,Blocks.WATER.defaultBlockState());
            for(int z:new int[]{34,38}) {
                set(level,box,x,4,z,Blocks.STONE_BRICK_WALL.defaultBlockState());
                set(level,box,x,5,z,lantern);
            }
        }
        // Timber brackets, balcony sill and tiled lintel articulate the main gate facade.
        for(int x:new int[]{18,29}) {
            fill(level,box,x,4,42,x,10,42,pillar);
            fill(level,box,x-1,10,42,x+1,10,42,Blocks.DARK_OAK_SLAB.defaultBlockState());
            set(level,box,x,9,41,lantern);
        }
        glazedRoof(level,box,18,40,29,45,13,3);
    }

    void lootChest(WorldGenLevel level, BoundingBox box, RandomSource random, int x, int y, int z) {
        createChest(level, box, random, x, y, z, LOOT);
    }
}
