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

        fill(level,box,2,3,2,19,22,17,air);

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
        for (int x : new int[]{5,16}) {
            for (int z = 5; z <= 15; z += 3) {
                for (int y = 3; y <= 11; y++) {
                    set(level, box, x, y, z, pillar);
                }
                set(level, box, x, 12, z, lantern);
            }
        }

        // 5) 重檐屋顶 / double-eave roof
        glazedRoof(level,box,2,2,19,17,13,4);
        glazedRoof(level,box,6,6,15,13,17,3);
        fill(level, box, 9, 20, 8, 12, 20, 11, jade);
        // Symmetrical lattice bays and quiet marble sill bands.
        var lattice=Blocks.DARK_OAK_FENCE.defaultBlockState();
        for(int z=6;z<=14;z+=3) {
            fill(level,box,4,6,z,4,8,z,lattice);
            fill(level,box,17,6,z,17,8,z,lattice);
            set(level,box,4,5,z,marble);set(level,box,17,5,z,marble);
        }
        for(int x:new int[]{6,7,14,15})fill(level,box,x,6,4,x,8,4,lattice);
        // A real three-step approach within this piece's original bounding box.
        for(int k=0;k<3;k++)fill(level,box,9,k,19-k,12,k,19-k,
            com.dynasty.worldgen.DynastyBuildKit.facing(Blocks.QUARTZ_STAIRS.defaultBlockState(),Direction.NORTH));
        // Exterior colonnade breaks up the tall stone wall without narrowing the entrance.
        for(int x:new int[]{4,7,14,17}) {
            set(level,box,x,2,17,marble);
            fill(level,box,x,3,17,x,11,17,pillar);
            set(level,box,x,12,17,DynastyBlocks.BRONZE_BLOCK.get().defaultBlockState());
        }
        for(int x:new int[]{3,18})for(int z:new int[]{4,8,12,16}) {
            fill(level,box,x,3,z,x,11,z,pillar);
            set(level,box,x,12,z,DynastyBlocks.BRONZE_BLOCK.get().defaultBlockState());
        }
        fill(level,box,4,11,17,17,11,17,pillar);
        for(int x:new int[]{6,15})set(level,box,x,12,17,lantern);
        var grille=lattice.setValue(net.minecraft.world.level.block.state.properties.BlockStateProperties.EAST,true)
            .setValue(net.minecraft.world.level.block.state.properties.BlockStateProperties.WEST,true);
        for(int x:new int[]{5,6,15,16})fill(level,box,x,5,16,x,8,16,grille);

        // 6) 殿内陈设：龙椅、屏风、匾额、香炉 / throne, screens, plaque, censer
        set(level, box, 10, 3, 6, DynastyBlocks.DRAGON_THRONE.get().defaultBlockState());
        set(level, box, 11, 3, 6, DynastyBlocks.DRAGON_THRONE.get().defaultBlockState());
        set(level, box, 9, 4, 5, screen);
        set(level, box, 12, 4, 5, screen);
        set(level, box, 10, 11, 5, DynastyBlocks.PLAQUE.get().defaultBlockState());
        set(level, box, 11, 11, 5, DynastyBlocks.PLAQUE.get().defaultBlockState());
        set(level, box, 8, 3, 9, DynastyBlocks.ALTAR.get().defaultBlockState());
        set(level, box, 13, 3, 9, DynastyBlocks.ALTAR.get().defaultBlockState());
        set(level, box, 7, 3, 12, DynastyBlocks.INCENSE_BURNER.get().defaultBlockState());
        set(level, box, 14, 3, 12, DynastyBlocks.CHIME_BELL.get().defaultBlockState());
        // Keep the ceremonial axis free, with a real walkable carpet approach.
        fill(level,box,9,3,8,12,3,15,Blocks.RED_CARPET.defaultBlockState());
        for(int x:new int[]{6,15})for(int z:new int[]{7,10,13}) {
            set(level,box,x,3,z,Blocks.LECTERN.defaultBlockState());
            set(level,box,x,3,z+1,com.dynasty.worldgen.DynastyBuildKit.facing(
                    Blocks.DARK_OAK_STAIRS.defaultBlockState(),Direction.NORTH));
        }
        set(level,box,7,3,5,Blocks.CARTOGRAPHY_TABLE.defaultBlockState());
        set(level,box,14,3,5,Blocks.ENDER_CHEST.defaultBlockState());
        set(level, box, 5, 3, 15, DynastyBlocks.TAIKO_DRUM.get().defaultBlockState());
        set(level, box, 16, 3, 15, DynastyBlocks.TAIKO_DRUM.get().defaultBlockState());

        // 7) 封顶与宝箱 / ceiling details + treasure
        createChest(level, box, random, 7, 3, 15, LOOT);
        createChest(level, box, random, 14, 3, 15, LOOT);
    }
}
