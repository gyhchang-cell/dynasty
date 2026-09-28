package com.dynasty.puzzle;

import com.dynasty.structure.DynastyStructurePiece;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;

import java.util.ArrayList;
import java.util.List;

/**
 * 自然生成的解谜遗迹部件（三种机关共用一套外壳；朝向与难度档由结构坐标哈希决定）。
 *
 * 与管理员模板 {@link PuzzleTemplates} 的区别：
 * <ul>
 *   <li>写的是 {@link WorldGenLevel}，每一笔都经过 {@code StructurePiece.placeBlock} 的分块裁剪，
 *       不会越界、不会强行加载周围区块；</li>
 *   <li>房间朝向由内容旋转实现（南/西/北/东），世界里能看到四种朝向；</li>
 *   <li>星盘初始朝向 / 灯阵初始亮灭按**世界坐标排序后的运行时编号**赋值，
 *       所以无论房间朝哪边、是否跨区块，玩家看到的「第 i 件」都与状态机算的一致；</li>
 *   <li>难度档写进控制器方块状态，重载后不会改变。</li>
 * </ul>
 *
 * Naturally generated puzzle ruin piece; the shell is shared by all three mechanisms.
 */
public class PuzzleRuinPiece extends DynastyStructurePiece {

    private final PuzzleRules.Kind kind;
    private final int layoutVersion;
    static final net.minecraft.resources.ResourceLocation TREASURE_LOOT =
            new net.minecraft.resources.ResourceLocation("dynasty", "puzzles/treasury_materials");

    public PuzzleRuinPiece(StructurePieceType type, int genDepth, BlockPos corner, PuzzleRules.Kind kind) {
        super(type, genDepth, makeBoundingBox(corner.getX(), corner.getY(), corner.getZ(),
                Direction.NORTH, RuinLayout.TREASURY_SIZE, RuinLayout.TREASURY_HEIGHT, RuinLayout.TREASURY_SIZE));
        this.setOrientation(Direction.NORTH);      // 房间朝向由内容旋转实现，见 RuinLayout.facingFor
        this.kind = kind;
        this.layoutVersion = RuinLayout.TREASURY_VERSION;
    }

    public PuzzleRuinPiece(StructurePieceType type, CompoundTag tag, PuzzleRules.Kind kind) {
        super(type, tag);
        this.kind = kind;
        this.layoutVersion = tag.contains("DynastyRuinLayout")?tag.getInt("DynastyRuinLayout"):2;
    }

    @Override
    protected void addAdditionalSaveData(net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext context, CompoundTag tag) {
        super.addAdditionalSaveData(context,tag);
        tag.putInt("DynastyRuinLayout",layoutVersion);
    }

    protected void treasure(WorldGenLevel level, BoundingBox box, RandomSource random, int x, int y, int z) {
        createChest(level,box,random,x,y,z,TREASURE_LOOT);
    }

    /** 外壳方块（三种机关一致，保持基础框架，方便后续美化）。*/
    static BlockState shellState(RuinLayout.Role role) {
        return switch (role) {
            case AIR -> Blocks.AIR.defaultBlockState();
            case FLOOR -> PuzzleBlocks.RUIN_SHELL.get().defaultBlockState();
            case WALL, CEILING -> PuzzleBlocks.RUIN_SHELL.get().defaultBlockState();
            case LANTERN -> com.dynasty.DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState();
            case ALTAR -> Blocks.ENCHANTING_TABLE.defaultBlockState();
            case GATE -> PuzzleBlocks.RUIN_GATE.get().defaultBlockState();
            case CLUE -> PuzzleBlocks.CLUE_TABLET.get().defaultBlockState();
            case BOOKSHELF -> Blocks.BOOKSHELF.defaultBlockState();
            case WORKBENCH -> Blocks.SMITHING_TABLE.defaultBlockState();
            case TREASURE -> Blocks.CHEST.defaultBlockState();
            case PILLAR -> Blocks.CHISELED_QUARTZ_BLOCK.defaultBlockState();
            case RELIC -> Blocks.BEACON.defaultBlockState();
            case RUG -> Blocks.RED_CARPET.defaultBlockState();
        };
    }

    /** 供 GameTest 用：某个控制器世界坐标对应的（难度档, 朝向）。*/
    public static int[] variantAndFacing(BlockPos controllerWorld) {
        return new int[]{RuinLayout.variantFor(controllerWorld.getX(), controllerWorld.getZ()),
                RuinLayout.facingFor(controllerWorld.getX(), controllerWorld.getZ())};
    }

    /** 本次生成会写下的全部局部偏移（含旋转），用于测试越界与可达性。*/
    public static List<int[]> plannedOffsets(PuzzleRules.Kind kind, int facing) {
        var offsets=new ArrayList<int[]>();
        for(var cell:RuinLayout.shell(RuinLayout.TREASURY_VERSION)){
            int[] r=RuinLayout.rotate(cell.x(),cell.z(),facing);
            offsets.add(new int[]{r[0],cell.y(),r[1]});
        }
        offsets.addAll(java.util.Arrays.asList(RuinLayout.rotatedPartOffsets(kind,facing)));
        offsets.add(new int[]{0,0,0});
        return offsets;
    }

    /** 用世界偏移算灯阵环序（与 PuzzleService.ringOrder 同一套几何）。*/
    static int[] ringOrder(int[][] offsets) {
        int[] dx = new int[offsets.length];
        int[] dz = new int[offsets.length];
        for (int i = 0; i < offsets.length; i++) {
            dx[i] = offsets[i][0];
            dz[i] = offsets[i][2];
        }
        return PuzzleRules.ringOrder(dx, dz);
    }

    static int indexOf(int[] values, int target) {
        for (int i = 0; i < values.length; i++) {
            if (values[i] == target) {
                return i;
            }
        }
        return 0;
    }

    static Direction facingOf(int orientation) {
        return switch (Math.floorMod(orientation, 4)) {
            case 0 -> Direction.NORTH;
            case 1 -> Direction.EAST;
            case 2 -> Direction.SOUTH;
            default -> Direction.WEST;
        };
    }

    @Override
    public void postProcess(WorldGenLevel level, StructureManager manager, ChunkGenerator generator,
                            RandomSource random, BoundingBox box, ChunkPos chunkPos, BlockPos pos) {
        // Saved v1 starts keep their original center instead of shifting unfinished chunks.
        int cx=layoutVersion>=3?RuinLayout.TREASURY_CENTER:getBoundingBox().getXSpan()<RuinLayout.SIZE?6:RuinLayout.CX;
        int cz=layoutVersion>=3?RuinLayout.TREASURY_CENTER:getBoundingBox().getZSpan()<RuinLayout.SIZE?6:RuinLayout.CZ;
        BlockPos controllerWorld = world(cx, RuinLayout.CY, cz);
        int facing = RuinLayout.facingFor(controllerWorld.getX(), controllerWorld.getZ());
        int variant = RuinLayout.variantFor(controllerWorld.getX(), controllerWorld.getZ());

        BlockState marble = com.dynasty.DynastyBlocks.MARBLE_BLOCK.get().defaultBlockState();
        BlockState jade = com.dynasty.DynastyBlocks.JADE_BLOCK.get().defaultBlockState();

        // 1) 外壳：墙 / 地板 / 天花板 / 门楣线索石板 / 封印门 / 宝室祭坛
        for (RuinLayout.Cell cell : RuinLayout.shell(layoutVersion)) {
            if(cx==6 && cell.z() < -6)continue;
            int[] r = RuinLayout.rotate(cell.x(), cell.z(), facing);
            int localX = cx + r[0];
            int localZ = cz + r[1];
            if(cell.role()==RuinLayout.Role.TREASURE){
                treasure(level,box,random,localX,RuinLayout.CY+cell.y(),localZ);
            } else if (cell.role() == RuinLayout.Role.FLOOR) {
                set(level, box, localX, RuinLayout.CY + RuinLayout.FLOOR_Y, localZ, PuzzleBlocks.RUIN_SHELL.get().defaultBlockState());
            } else {
                set(level, box, localX, RuinLayout.CY + cell.y(), localZ,
                        shellState(cx==6 && cell.z()==-6?RuinLayout.Role.WALL:cell.role()));
            }
        }
        // 门框两角压玉边：遗迹在地表看得出来，又不抢后续美术的发挥空间（不占门楣的线索石板位）
        int[] corner = RuinLayout.rotate(3, RuinLayout.FRONT_Z, facing);
        set(level, box, cx + corner[0], RuinLayout.CY + 3, cz + corner[1], jade);
        int[] corner2 = RuinLayout.rotate(-3, RuinLayout.FRONT_Z, facing);
        set(level, box, cx + corner2[0], RuinLayout.CY + 3, cz + corner2[1], jade);

        // 2) 机关部件：先按世界偏移算运行时编号，再写初始状态（任意朝向都对得上）
        int[][] offsets = RuinLayout.rotatedPartOffsets(kind, facing);
        int[] rank = RuinLayout.runtimeOrder(offsets);
        Block part = PuzzleBlocks.partFor(kind);
        int[] starInitial = PuzzleRules.starInitial(variant);
        int[] lampInitial = PuzzleRules.lampInitial(variant);
        int[] ring = kind == PuzzleRules.Kind.ELEMENTS ? ringOrder(offsets) : null;

        for (int i = 0; i < offsets.length; i++) {
            int localX = cx + offsets[i][0];
            int localY = RuinLayout.CY + offsets[i][1];
            int localZ = cz + offsets[i][2];
            int runtimeIndex = rank[i];
            BlockState state = part.defaultBlockState();
            if (kind == PuzzleRules.Kind.STAR) {
                state = state.setValue(PuzzleBlocks.FACING,
                        facingOf(RuinLayout.rotateFacing(starInitial[runtimeIndex], facing)));
            } else if (kind == PuzzleRules.Kind.ELEMENTS) {
                state = state.setValue(PuzzleBlocks.SYMBOL, Math.floorMod(runtimeIndex, 4))
                        .setValue(PuzzleBlocks.LIT, lampInitial[indexOf(ring, runtimeIndex)] == 1);
            }
            set(level, box, localX, localY, localZ, state);
            set(level, box, localX, localY + 1, localZ, PuzzleBlocks.CLUE_TABLET.get().defaultBlockState());
        }

        // 3) 控制器：机关类型 + 难度档写进方块状态（存档 / 重载稳定）
        set(level, box, cx, RuinLayout.CY, cz,
                PuzzleBlocks.RUIN_CONTROLLER.get().defaultBlockState()
                        .setValue(PuzzleBlocks.KIND, kind.ordinal())
                        .setValue(PuzzleBlocks.VARIANT, PuzzleRules.wrap(variant)));
    }

    /** 三个机关各自的部件类（注册时各用一个部件类型，反序列化后类型不会丢）。*/
    public static final class Star extends PuzzleRuinPiece {
        public Star(StructurePieceType type, int genDepth, BlockPos corner) {
            super(type, genDepth, corner, PuzzleRules.Kind.STAR);
        }

        public Star(StructurePieceType type, CompoundTag tag) {
            super(type, tag, PuzzleRules.Kind.STAR);
        }
    }

    public static final class Bell extends PuzzleRuinPiece {
        public Bell(StructurePieceType type, int genDepth, BlockPos corner) {
            super(type, genDepth, corner, PuzzleRules.Kind.BELL);
        }

        public Bell(StructurePieceType type, CompoundTag tag) {
            super(type, tag, PuzzleRules.Kind.BELL);
        }
    }

    public static final class Lamp extends PuzzleRuinPiece {
        public Lamp(StructurePieceType type, int genDepth, BlockPos corner) {
            super(type, genDepth, corner, PuzzleRules.Kind.ELEMENTS);
        }

        public Lamp(StructurePieceType type, CompoundTag tag) {
            super(type, tag, PuzzleRules.Kind.ELEMENTS);
        }
    }
}
