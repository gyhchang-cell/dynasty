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
 * 长城关隘：一段带垛口的城墙、中央门洞与城楼、东西两座角楼、门前的马道。
 * Great Wall Gate: a crenellated wall segment with a central gate, a gate tower,
 * two flanking turrets and a stepped ramp up to the walkway.
 */
public class WallGatePiece extends DynastyStructurePiece {

    public static final int SIZE = 30;
    public static final int LENGTH = 24;
    public static final int HEIGHT = 16;
    private static final ResourceLocation TURRET_LOOT = new ResourceLocation("dynasty", "chests/barracks");
    private static final ResourceLocation TOWER_LOOT = new ResourceLocation("dynasty", "chests/watchtower");

    public WallGatePiece(StructurePieceType type, int genDepth, BlockPos pos) {
        super(type, genDepth,
                makeBoundingBox(pos.getX(), pos.getY(), pos.getZ(), Direction.NORTH, SIZE, HEIGHT, LENGTH));
        this.setOrientation(Direction.NORTH);
    }

    public WallGatePiece(StructurePieceType type, CompoundTag tag) {
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

        // 1) 墙基与墙体（沿 x 走向，z=9..14）/ footing and the wall band
        fill(level, box, 0, 0, 0, SIZE - 1, 0, LENGTH - 1, marble);
        fill(level, box, 0, 1, 9, SIZE - 1, 6, 14, brick);
        fill(level, box, 0, 7, 10, SIZE - 1, 7, 13, marble);            // 马道 / walkway
        for (int x = 0; x < SIZE; x += 2) {                             // 垛口 / battlements
            set(level, box, x, 7, 9, brick);
            set(level, box, x, 7, 14, brick);
            set(level, box, x, 8, 9, brick);
            set(level, box, x, 8, 14, brick);
        }
        for (int x = 3; x < SIZE; x += 6) {                             // 旗灯 / lantern posts
            set(level, box, x, 8, 10, lantern);
            set(level, box, x, 8, 13, lantern);
        }

        // 2) 门洞 / the gate passage
        fill(level, box, 13, 1, 8, 16, 6, 15, air);
        fill(level, box, 12, 1, 8, 12, 6, 8, brick);
        fill(level, box, 17, 1, 8, 17, 6, 8, brick);
        fill(level, box, 13, 7, 8, 16, 7, 8, brick);                    // 门额 / lintel

        // 3) 城楼 / gate tower above the passage
        walls(level, box, 11, 8, 9, 18, 13, 14, brick);
        fill(level, box, 12, 8, 10, 17, 8, 13, jade);
        fill(level, box, 12, 9, 10, 17, 12, 13, air);
        fill(level, box, 10, 14, 8, 19, 14, 15, brick);
        fill(level, box, 12, 15, 10, 17, 15, 13, brick);
        for (int[] c : new int[][]{{12, 10}, {12, 13}, {17, 10}, {17, 13}}) {
            for (int y = 9; y <= 13; y++) {
                set(level, box, c[0], y, c[1], pillar);
            }
        }

        // 4) 东西角楼 / flanking turrets
        for (int x1 : new int[]{1, 24}) {
            walls(level, box, x1, 8, 9, x1 + 4, 12, 14, brick);
            fill(level, box, x1, 8, 10, x1 + 4, 8, 13, marble);
            fill(level, box, x1 + 1, 9, 10, x1 + 3, 11, 13, air);
            fill(level, box, x1 - 1, 13, 8, x1 + 5, 13, 15, brick);
            set(level, box, x1 + 2, 9, 10, lantern);
        }

        // 5) 马道（门前石阶，往北收、顶端接马道）/ stepped ramp climbing up to the walkway
        for (int i = 0; i <= 6; i++) {
            int y = 1 + i;
            int z = 22 - i;
            fill(level, box, 14, y, z, 15, y, z + 1, marble);           // 阶面 / tread
            fill(level, box, 13, 1, z, 13, y, 23, brick);               // 西挡墙 / west wall
            fill(level, box, 16, 1, z, 16, y, 23, brick);               // 东挡墙 / east wall
        }
        fill(level, box, 14, 7, 14, 15, 8, 14, air);                    // 与马道接口 / opening

        // 6) 陈列 / details
        set(level, box, 12, 8, 12, DynastyBlocks.TAIKO_DRUM.get().defaultBlockState());
        set(level, box, 17, 8, 11, DynastyBlocks.SCREEN.get().defaultBlockState());
        set(level, box, 14, 8, 9, DynastyBlocks.PLAQUE.get().defaultBlockState());
        set(level, box, 15, 8, 9, DynastyBlocks.PLAQUE.get().defaultBlockState());
        set(level, box, 2, 12, 11, bronze);
        set(level, box, 27, 12, 11, bronze);

        // 7) 军械箱 / chests
        createChest(level, box, random, 2, 9, 12, TURRET_LOOT);
        createChest(level, box, random, 27, 9, 12, TURRET_LOOT);
        createChest(level, box, random, 13, 9, 12, TOWER_LOOT);
    }
}
