package com.dynasty.puzzle;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

import java.util.List;

/**
 * 三个可玩宝室的模板生成（管理员命令调用；**不接入自然生成**）。
 *
 * 布局（控制器在原点，房间朝 +Z 开门）：
 *   主室 x,z ∈ [-3,3]、y ∈ [0,2]，地板 y=-1、天花板 y=3，外墙 |x|=4 / |z|=4；
 *   入口：z=4 墙上 x ∈ [-1,0]、y ∈ [0,1] 挖空；
 *   宝室：z ∈ [-6,-4] 的凹室，z=-4 用封印石堵门（解开后由控制器移除）；
 *   线索石板放在每个机关部件**正上方**（对应关系看得见，不用猜）；
 *   宝室里的祭坛只是奖励台视觉，实际奖励由控制器发放（不放箱子，避免二次来源）。
 *
 * 全部使用已有方块（宫廷砖 / 汉白玉 / 玉块 / 宫灯 / 祭坛），不新增贴图。
 */
public final class PuzzleTemplates {

    private PuzzleTemplates() {
    }

    public enum Room {
        STAR("star_room", PuzzleRules.Kind.STAR, 0),
        BELL("bell_room", PuzzleRules.Kind.BELL, 1),
        LAMP("lamp_room", PuzzleRules.Kind.ELEMENTS, 2);

        public final String id;
        public final PuzzleRules.Kind kind;
        public final int defaultVariant;

        Room(String id, PuzzleRules.Kind kind, int defaultVariant) {
            this.id = id;
            this.kind = kind;
            this.defaultVariant = defaultVariant;
        }

        public static Room byId(String id) {
            for (Room room : values()) {
                if (room.id.equalsIgnoreCase(id)) {
                    return room;
                }
            }
            return null;
        }
    }

    public static void build(ServerLevel level, BlockPos origin, Room room, int variant) {
        Block shell = com.dynasty.DynastyBlocks.PALACE_BRICKS.get();
        Block marble = com.dynasty.DynastyBlocks.MARBLE_BLOCK.get();
        Block trim = com.dynasty.DynastyBlocks.JADE_BLOCK.get();
        Block lantern = com.dynasty.DynastyBlocks.IMPERIAL_LANTERN.get();

        for (int x = -4; x <= 4; x++) {
            for (int z = -6; z <= 4; z++) {
                boolean outer = Math.abs(x) == 4 || z == -6 || z == 4;
                boolean inside = x >= -3 && x <= 3 && ((z >= -3 && z <= 3) || (z >= -6 && z <= -5));
                if (inside) {
                    level.setBlock(origin.offset(x, -1, z), marble.defaultBlockState(), 2);
                }
                for (int y = 0; y <= 3; y++) {
                    BlockPos pos = origin.offset(x, y, z);
                    if (y == 3 && inside) {
                        level.setBlock(pos, shell.defaultBlockState(), 2);
                    } else if (outer) {
                        level.setBlock(pos, (Math.abs(x) == 4 && y == 2 && Math.abs(z) % 2 == 0)
                                ? trim.defaultBlockState() : shell.defaultBlockState(), 2);
                    } else {
                        level.setBlock(pos, Blocks.AIR.defaultBlockState(), 2);
                    }
                }
            }
        }
        for (int x = -1; x <= 0; x++) {
            for (int y = 0; y <= 1; y++) {
                level.setBlock(origin.offset(x, y, 4), Blocks.AIR.defaultBlockState(), 2);
            }
        }
        for (int x = -3; x <= 3; x++) {
            for (int y = 0; y <= 2; y++) {
                level.setBlock(origin.offset(x, y, -4), (x >= -1 && x <= 0 && y <= 1)
                        ? PuzzleBlocks.RUIN_GATE.get().defaultBlockState()
                        : shell.defaultBlockState(), 2);
            }
        }
        level.setBlock(origin.offset(-3, 2, 3), lantern.defaultBlockState(), 2);
        level.setBlock(origin.offset(3, 2, 3), lantern.defaultBlockState(), 2);
        level.setBlock(origin.offset(0, 0, -5), com.dynasty.DynastyBlocks.ALTAR.get().defaultBlockState(), 2);
        level.setBlock(origin.offset(-2, 0, -5), lantern.defaultBlockState(), 2);
        level.setBlock(origin.offset(2, 0, -5), lantern.defaultBlockState(), 2);

        level.setBlock(origin, PuzzleBlocks.RUIN_CONTROLLER.get().defaultBlockState()
                .setValue(PuzzleBlocks.KIND, room.kind.ordinal())
                .setValue(PuzzleBlocks.VARIANT, PuzzleRules.wrap(variant)), 3);

        if (room == Room.STAR) {
            int[][] corners = {{-2, -2}, {-2, 2}, {2, -2}, {2, 2}};
            int[] initial = PuzzleRules.starInitial(variant);
            for (int i = 0; i < corners.length; i++) {
                BlockPos pos = origin.offset(corners[i][0], 0, corners[i][1]);
                level.setBlock(pos, PuzzleBlocks.STAR_DIAL.get().defaultBlockState()
                        .setValue(PuzzleBlocks.FACING, facing(PuzzleRules.wrap(initial[i]))), 3);
                level.setBlock(pos.above(), PuzzleBlocks.CLUE_TABLET.get().defaultBlockState(), 3);
            }
        } else if (room == Room.BELL) {
            for (int i = 0; i < 5; i++) {
                BlockPos pos = origin.offset(-2 + i, 0, -2);
                level.setBlock(pos, PuzzleBlocks.ECHO_BELL.get().defaultBlockState(), 3);
                level.setBlock(pos.above(), PuzzleBlocks.CLUE_TABLET.get().defaultBlockState(), 3);
            }
        } else {
            int[][] ring = {{0, -3}, {3, 0}, {0, 3}, {-3, 0}};
            int[] initial = PuzzleRules.lampInitial(variant);
            for (int i = 0; i < ring.length; i++) {
                BlockPos pos = origin.offset(ring[i][0], 0, ring[i][1]);
                level.setBlock(pos, PuzzleBlocks.ELEMENT_LAMP.get().defaultBlockState()
                        .setValue(PuzzleBlocks.LIT, initial[i] == 1)
                        .setValue(PuzzleBlocks.SYMBOL, i), 3);
                level.setBlock(pos.above(), PuzzleBlocks.CLUE_TABLET.get().defaultBlockState(), 3);
            }
        }
    }

    private static Direction facing(int orientation) {
        return switch (orientation) {
            case 0 -> Direction.NORTH;
            case 1 -> Direction.EAST;
            case 2 -> Direction.SOUTH;
            default -> Direction.WEST;
        };
    }

    public static List<String> ids() {
        return List.of(Room.STAR.id, Room.BELL.id, Room.LAMP.id);
    }
}
