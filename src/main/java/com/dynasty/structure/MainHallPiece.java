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
 * 太和殿（主殿）：重檐屋顶、金柱、龙椅、匾额、宝箱。
 * Hall of Supreme Harmony: double-eave roof, golden columns, dragon throne, plaque, chests.
 */
public class MainHallPiece extends DynastyStructurePiece {

    public static final int WIDTH = 22;
    public static final int HEIGHT = 26;
    public static final int DEPTH = 20;
    private static final ResourceLocation LOOT = new ResourceLocation("dynasty", "chests/dynasty_palace");

    public MainHallPiece(StructurePieceType type, int genDepth, BlockPos pos) {
        super(type, genDepth,
                makeBoundingBox(pos.getX(), pos.getY(), pos.getZ(), Direction.NORTH, WIDTH, HEIGHT, DEPTH));
        this.setOrientation(Direction.NORTH);
    }

    public MainHallPiece(StructurePieceType type, CompoundTag tag) {
        super(type, tag);
    }

    @Override
    public void postProcess(WorldGenLevel level, StructureManager manager, ChunkGenerator generator,
                            RandomSource random, BoundingBox box, ChunkPos chunkPos, BlockPos pos) {
        BlockState brick = DynastyBlocks.PALACE_BRICKS.get().defaultBlockState();
        BlockState marble = DynastyBlocks.MARBLE_BLOCK.get().defaultBlockState();
        BlockState jade = DynastyBlocks.JADE_BLOCK.get().defaultBlockState();
        BlockState pillar = DynastyBlocks.CRIMSON_PILLAR.get().defaultBlockState();
        BlockState lantern = DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState();
        BlockState screen = DynastyBlocks.SCREEN.get().defaultBlockState();
        BlockState air = Blocks.AIR.defaultBlockState();

        // 1) 殿基（三层须弥座）/ hall podium (three tiers)
        fill(level, box, 1, 0, 1, 20, 0, 18, marble);
        fill(level, box, 2, 1, 2, 19, 1, 17, brick);
        fill(level, box, 3, 2, 3, 18, 2, 16, marble);

        // 2) 殿身墙体与开窗 / hall walls with window openings
        walls(level, box, 4, 3, 4, 17, 12, 16, brick);
        for (int x = 6; x <= 15; x += 3) {
            set(level, box, x, 6, 4, air);
            set(level, box, x, 7, 4, air);
        }
        for (int z = 6; z <= 14; z += 3) {
            set(level, box, 4, 6, z, air);
            set(level, box, 4, 7, z, air);
        }

        // 3) 殿门（南面）/ main doorway (south)
        fill(level, box, 9, 3, 16, 12, 10, 16, air);
        fill(level, box, 8, 11, 16, 13, 11, 16, marble);

        // 4) 金柱 / interior columns
        for (int x = 5; x <= 16; x += 3) {
            for (int z = 5; z <= 15; z += 3) {
                for (int y = 3; y <= 11; y++) {
                    set(level, box, x, y, z, pillar);
                }
                set(level, box, x, 12, z, lantern);
            }
        }

        // 5) 重檐屋顶 / double-eave roof
        for (int layer = 0; layer < 4; layer++) {
            int x1 = 2 + layer;
            int z1 = 2 + layer;
            int x2 = 19 - layer;
            int z2 = 17 - layer;
            walls(level, box, x1, 13 + layer, z1, x2, 13 + layer, z2,
                    layer % 2 == 0 ? brick : jade);
            fill(level, box, x1 + 1, 13 + layer, z1 + 1, x2 - 1, 13 + layer, z2 - 1, air);
        }
        for (int layer = 0; layer < 3; layer++) {
            int x1 = 6 + layer;
            int z1 = 6 + layer;
            int x2 = 15 - layer;
            int z2 = 13 - layer;
            walls(level, box, x1, 17 + layer, z1, x2, 17 + layer, z2,
                    layer % 2 == 0 ? brick : jade);
        }
        fill(level, box, 9, 20, 8, 12, 20, 11, jade);

        // 6) 殿内陈设：龙椅、屏风、匾额、香炉 / throne, screens, plaque, censer
        set(level, box, 10, 3, 6, DynastyBlocks.DRAGON_THRONE.get().defaultBlockState());
        set(level, box, 11, 3, 6, DynastyBlocks.DRAGON_THRONE.get().defaultBlockState());
        set(level, box, 9, 4, 5, screen);
        set(level, box, 12, 4, 5, screen);
        set(level, box, 10, 11, 5, DynastyBlocks.PLAQUE.get().defaultBlockState());
        set(level, box, 11, 11, 5, DynastyBlocks.PLAQUE.get().defaultBlockState());
        set(level, box, 8, 3, 9, DynastyBlocks.ALTAR.get().defaultBlockState());
        set(level, box, 13, 3, 9, DynastyBlocks.ALTAR.get().defaultBlockState());
        set(level, box, 10, 3, 12, DynastyBlocks.INCENSE_BURNER.get().defaultBlockState());
        set(level, box, 11, 3, 12, DynastyBlocks.CHIME_BELL.get().defaultBlockState());
        set(level, box, 5, 3, 15, DynastyBlocks.TAIKO_DRUM.get().defaultBlockState());
        set(level, box, 16, 3, 15, DynastyBlocks.TAIKO_DRUM.get().defaultBlockState());

        // 7) 封顶与宝箱 / ceiling details + treasure
        createChest(level, box, random, 5, 3, 15, LOOT);
        createChest(level, box, random, 16, 3, 15, LOOT);
    }
}
