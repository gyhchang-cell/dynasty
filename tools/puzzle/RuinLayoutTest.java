import com.dynasty.puzzle.PuzzleRules;
import com.dynasty.puzzle.RuinLayout;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * 自然生成解谜遗迹的**几何与索引一致性**测试（不需要启动游戏）。
 *
 * 直接调用生产类 {@link RuinLayout} 与 {@link PuzzleRules}，断言：
 *   1. 四种朝向 × 三种机关都装在 11×6×11 包围盒里（不会生成半间房）；
 *   2. 生成时写下的初始状态，在「运行时按世界坐标重新编号」之后仍落在正确的部件上；
 *   3. 三个机关 × 三个难度档都可解、且开局都不是完成态；
 *   4. 入口 → 每个部件 → 宝室连通；封印门还在时宝室进不去。
 *
 * 运行：bash tools/puzzle/run_ruin_tests.sh
 */
public final class RuinLayoutTest {

    private static int passed;
    private static final List<String> failures = new ArrayList<>();

    public static void main(String[] args) {
        geometry();
        rotation();
        indexAlignment();
        difficulty();
        reachability();
        System.out.println();
        if (failures.isEmpty()) {
            System.out.println("通过 " + passed + " 项，失败 0 项");
            System.out.println("✅ 遗迹几何 / 朝向 / 索引对齐 / 九档可解性 / 连通性 全部通过");
        } else {
            System.out.println("通过 " + passed + " 项，失败 " + failures.size() + " 项");
            for (String failure : failures) {
                System.out.println("  ❌ " + failure);
            }
            System.exit(1);
        }
    }

    private static void check(String name, boolean ok) {
        check(name, ok, "");
    }

    private static void check(String name, boolean ok, String detail) {
        if (ok) {
            passed++;
        } else {
            failures.add(name + (detail.isEmpty() ? "" : " —— " + detail));
        }
    }

    private static PuzzleRules.Kind[] kinds() {
        return new PuzzleRules.Kind[]{PuzzleRules.Kind.STAR, PuzzleRules.Kind.BELL, PuzzleRules.Kind.ELEMENTS};
    }

    private static int indexOf(int[] values, int target) {
        for (int i = 0; i < values.length; i++) {
            if (values[i] == target) {
                return i;
            }
        }
        return -1;
    }

    private static int[] ringOf(int[][] offsets) {
        int[] dx = new int[offsets.length];
        int[] dz = new int[offsets.length];
        for (int i = 0; i < offsets.length; i++) {
            dx[i] = offsets[i][0];
            dz[i] = offsets[i][2];
        }
        return PuzzleRules.ringOrder(dx, dz);
    }

    /* ---------- 1. 包围盒与发现范围 ---------- */

    private static void geometry() {
        boolean allFit = true;
        boolean inside = true;
        boolean discoverable = true;
        for (PuzzleRules.Kind kind : kinds()) {
            for (int facing = 0; facing < 4; facing++) {
                allFit &= RuinLayout.fits(kind, facing);
                for (int[] offset : RuinLayout.allOffsets(kind, facing)) {
                    inside &= Math.abs(offset[0]) <= RuinLayout.CX && Math.abs(offset[2]) <= RuinLayout.CZ
                            && RuinLayout.CY + offset[1] >= 0 && RuinLayout.CY + offset[1] < RuinLayout.HEIGHT;
                }
                for (int[] offset : RuinLayout.rotatedPartOffsets(kind, facing)) {
                    discoverable &= Math.abs(offset[0]) <= 12 && Math.abs(offset[2]) <= 12
                            && Math.abs(offset[1]) <= 8;
                }
            }
        }
        check("四种朝向 × 三种机关的内容全部落在 11×6×11 包围盒内", allFit);
        check("内容不会写出包围盒（半间房的常见原因）", inside);
        check("机关部件都在控制器 ±12/±8 的发现范围内", discoverable);
        check("部件数量与机关类型一致（星盘 4 / 编钟 5 / 四象灯 4）",
                RuinLayout.partOffsets(PuzzleRules.Kind.STAR).length == 4
                        && RuinLayout.partOffsets(PuzzleRules.Kind.BELL).length == 5
                        && RuinLayout.partOffsets(PuzzleRules.Kind.ELEMENTS).length == 4);
    }

    /* ---------- 2. 旋转与分布 ---------- */

    private static void rotation() {
        boolean roundTrip = true;
        boolean distanceKept = true;
        for (int facing = 0; facing < 4; facing++) {
            int[] once = RuinLayout.rotate(3, -1, facing);
            int[] back = new int[]{once[0], once[1]};
            for (int i = 0; i < 4 - facing; i++) {
                back = RuinLayout.rotate(back[0], back[1], 1);
            }
            roundTrip &= back[0] == 3 && back[1] == -1;
            // 旋转保持距离：两个基向量旋转后，坐标差只是换了个顺序
            int[] a = RuinLayout.rotate(4, 0, facing);
            int[] b = RuinLayout.rotate(0, 6, facing);
            int dx = Math.abs(a[0] - b[0]);
            int dz = Math.abs(a[1] - b[1]);
            distanceKept &= (dx == 4 && dz == 6) || (dx == 6 && dz == 4);
        }
        check("旋转四次回到原位（绕控制器旋转，不平移）", roundTrip);
        check("旋转保持距离（房间尺寸不变）", distanceKept);

        boolean facingRotates = true;
        for (int facing = 0; facing < 4; facing++) {
            for (int orientation = 0; orientation < 4; orientation++) {
                int[] base = RuinLayout.facingVector(orientation);
                int[] want = RuinLayout.rotate(base[0], base[1], facing);
                int[] got = RuinLayout.facingVector(RuinLayout.rotateFacing(orientation, facing));
                facingRotates &= want[0] == got[0] && want[1] == got[1];
            }
        }
        check("星盘朝向随房间旋转（线索方向不错位）", facingRotates);

        int[] facingCount = new int[4];
        int[] variantCount = new int[PuzzleRules.LAYOUTS];
        int samples = 0;
        for (int x = -200; x <= 200; x += 7) {
            for (int z = -200; z <= 200; z += 7) {
                facingCount[RuinLayout.facingFor(x, z)]++;
                variantCount[RuinLayout.variantFor(x, z)]++;
                samples++;
            }
        }
        boolean spread = true;
        for (int count : facingCount) {
            spread &= count > samples / 8;
        }
        for (int count : variantCount) {
            spread &= count > samples / 8;
        }
        check("朝向与难度档在世界上均匀分布（" + samples + " 个采样点）", spread,
                java.util.Arrays.toString(facingCount) + " / " + java.util.Arrays.toString(variantCount));
    }

    /* ---------- 3. 生成时的初始状态 ↔ 运行时编号 ---------- */

    private static void indexAlignment() {
        boolean starAligned = true;
        boolean lampAligned = true;
        for (int variant = 0; variant < PuzzleRules.LAYOUTS; variant++) {
            for (int facing = 0; facing < 4; facing++) {
                // 星盘：生成按 rank 写初始朝向 → 运行时按 (y,x,z) 重排后必须逐一对上
                int[][] offsets = RuinLayout.rotatedPartOffsets(PuzzleRules.Kind.STAR, facing);
                int[] rank = RuinLayout.runtimeOrder(offsets);
                int[] starInitial = PuzzleRules.starInitial(variant);
                int[] written = new int[offsets.length];
                for (int i = 0; i < offsets.length; i++) {
                    written[i] = RuinLayout.rotateFacing(starInitial[rank[i]], facing);
                }
                for (int runtimeIndex = 0; runtimeIndex < offsets.length; runtimeIndex++) {
                    int local = indexOf(rank, runtimeIndex);
                    starAligned &= written[local] == RuinLayout.rotateFacing(starInitial[runtimeIndex], facing);
                }

                // 灯阵：生成按「环序」写初始亮灭 → 运行时重建环序后必须逐位一致
                int[][] lampOffsets = RuinLayout.rotatedPartOffsets(PuzzleRules.Kind.ELEMENTS, facing);
                int[] lampRank = RuinLayout.runtimeOrder(lampOffsets);
                int[] ring = ringOf(lampOffsets);
                int[] lampInitial = PuzzleRules.lampInitial(variant);
                boolean[] lit = new boolean[lampOffsets.length];
                for (int i = 0; i < lampOffsets.length; i++) {
                    lit[i] = lampInitial[indexOf(ring, lampRank[i])] == 1;
                }
                for (int position = 0; position < ring.length; position++) {
                    int local = indexOf(lampRank, ring[position]);
                    lampAligned &= lit[local] == (lampInitial[position] == 1);
                }
            }
        }
        check("星盘初始朝向在四种朝向下都对上「运行时第 i 座」", starAligned);
        check("灯阵初始亮灭在四种朝向下都对上「运行时环序第 i 位」", lampAligned);
    }

    /* ---------- 4. 九种难度配置：可解且开局未完成 ---------- */

    private static void difficulty() {
        check("星盘三套布局自检通过", PuzzleRules.validateStarLayouts() == null,
                String.valueOf(PuzzleRules.validateStarLayouts()));
        check("灯阵三套布局自检通过（含 BFS 可解性）", PuzzleRules.validateLampLayouts() == null,
                String.valueOf(PuzzleRules.validateLampLayouts()));

        boolean starOk = true;
        boolean lampOk = true;
        for (int variant = 0; variant < PuzzleRules.LAYOUTS; variant++) {
            int[] initial = PuzzleRules.starInitial(variant);
            starOk &= !PuzzleRules.starSolved(variant, initial);
            int[] solved = new int[initial.length];
            for (int dial = 0; dial < initial.length; dial++) {
                solved[dial] = PuzzleRules.rotateTimes(initial[dial],
                        PuzzleRules.starTurnsNeeded(variant, dial, initial[dial]));
            }
            starOk &= PuzzleRules.starSolved(variant, solved);

            int[] lamps = PuzzleRules.lampInitial(variant);
            lampOk &= !PuzzleRules.lampSolved(lamps);
            int[] presses = PuzzleRules.lampSolution(lamps);
            lampOk &= presses != null && presses.length > 0;
            if (presses != null) {
                int[] state = lamps.clone();
                for (int press : presses) {
                    state = PuzzleRules.lampToggle(state, press);
                }
                lampOk &= PuzzleRules.lampSolved(state);
            }
        }
        check("星盘三档：开局未完成、按线索可解", starOk);
        check("灯阵三档：开局未完成、按解点得亮", lampOk);

        boolean bellOk = true;
        int previous = 0;
        for (int variant = 0; variant < PuzzleRules.LAYOUTS; variant++) {
            int[] sequence = PuzzleRules.bellSequence(variant);
            bellOk &= sequence.length == PuzzleRules.bellSequenceLength(variant);
            bellOk &= sequence.length > previous && sequence.length >= 3;
            previous = sequence.length;
            bellOk &= PuzzleRules.bellCorrect(variant, sequence);
            bellOk &= !PuzzleRules.bellCorrect(variant, new int[]{sequence[0]});
        }
        check("编钟三档：长度递增（3/4/5）、正确序列通过、长度不足不通过", bellOk);
    }

    /* ---------- 5. 连通性（入口 → 部件 → 宝室，含封印门） ---------- */

    private static void reachability() {
        boolean partsReachable = true;
        boolean treasuryWalkable = true;
        boolean gateSeals = true;
        boolean entranceOpen = true;
        List<String> leaks = new ArrayList<>();
        List<String> sealedParts = new ArrayList<>();
        List<String> unreachableTreasury = new ArrayList<>();
        for (PuzzleRules.Kind kind : kinds()) {
            for (int facing = 0; facing < 4; facing++) {
                String where = kind + "/facing" + facing;
                Set<Long> sealedRoom = walkableFrom(solidCells(kind, facing, true), outside(facing));
                entranceOpen &= sealedRoom.size() > 20;          // 能走进房间内部
                for (int[] offset : RuinLayout.rotatedPartOffsets(kind, facing)) {
                    // 部件本身是实心方块，玩家站的是它旁边那一格
                    if (!standsNextTo(sealedRoom, offset[0], offset[1], offset[2])) {
                        partsReachable = false;
                        sealedParts.add(where + "@" + offset[0] + "," + offset[1] + "," + offset[2]);
                    }
                }
                // 宝室：封印门还在时，宝室里没有任何一格可达（检查点也要跟着房间旋转）
                int[] treasuryA = RuinLayout.rotate(1, -5, facing);
                int[] treasuryB = RuinLayout.rotate(-1, -5, facing);
                int[] treasuryUp = RuinLayout.rotate(0, -5, facing);
                boolean treasurySeen = sealedRoom.contains(key(treasuryA[0], 0, treasuryA[1]))
                        || sealedRoom.contains(key(treasuryB[0], 0, treasuryB[1]))
                        || sealedRoom.contains(key(treasuryUp[0], 1, treasuryUp[1]));
                if (treasurySeen) {
                    gateSeals = false;
                    leaks.add(where);
                }

                Set<Long> openRoom = walkableFrom(solidCells(kind, facing, false), outside(facing));
                // 门开了之后：宝室里能站人（祭坛两侧），且所有部件仍然可达
                if (!openRoom.contains(key(treasuryA[0], 0, treasuryA[1]))
                        && !openRoom.contains(key(treasuryB[0], 0, treasuryB[1]))) {
                    treasuryWalkable = false;
                    unreachableTreasury.add(where);
                }
                for (int[] offset : RuinLayout.rotatedPartOffsets(kind, facing)) {
                    if (!standsNextTo(openRoom, offset[0], offset[1], offset[2])) {
                        treasuryWalkable = false;
                        sealedParts.add(where + "（开门后）");
                    }
                }
            }
        }
        check("入口是通的（玩家能走进房间）", entranceOpen);
        check("入口 → 每个机关部件都走得通（四种朝向）", partsReachable, String.join(" ", sealedParts));
        check("封印门还在时宝室进不去（门真的封住）", gateSeals, String.join(" ", leaks));
        check("封印门移除后宝室可以走到、部件仍然可达（奖励拿得到）", treasuryWalkable,
                String.join(" ", unreachableTreasury));
    }

    /** 玩家能不能站在这件机关旁边（四向 + 上下一格都算）。*/
    private static boolean standsNextTo(Set<Long> walkable, int x, int y, int z) {
        long[] candidates = {
                key(x + 1, y, z), key(x - 1, y, z), key(x, y, z + 1), key(x, y, z - 1),
                key(x, y + 1, z), key(x, y - 1, z)};
        for (long candidate : candidates) {
            if (walkable.contains(candidate)) {
                return true;
            }
        }
        return false;
    }

    /** 玩家站位：门外一级台阶上方（局部坐标，已按朝向旋转）。*/
    private static long[] outside(int facing) {
        int[] step = RuinLayout.rotate(0, RuinLayout.FRONT_Z + 1, facing);
        return new long[]{key(step[0], RuinLayout.FLOOR_Y + 1, step[1])};
    }

    private static long key(int x, int y, int z) {
        return (((long) (x + 32)) << 40) | (((long) (y + 32)) << 20) | (z + 32);
    }

    private static long above(long position) {
        return key(xOf(position), yOf(position) + 1, zOf(position));
    }

    private static long below(long position) {
        return key(xOf(position), yOf(position) - 1, zOf(position));
    }

    private static long shift(long position, int dx, int dz) {
        return key(xOf(position) + dx, yOf(position), zOf(position) + dz);
    }

    private static int xOf(long position) {
        return (int) ((position >> 40) & 0xFFFFF) - 32;
    }

    private static int yOf(long position) {
        return (int) ((position >> 20) & 0xFFFFF) - 32;
    }

    private static int zOf(long position) {
        return (int) (position & 0xFFFFF) - 32;
    }

    /** 生成后的实心集合（局部坐标）；withGate=false 表示封印门已被移除。*/
    private static Set<Long> solidCells(PuzzleRules.Kind kind, int facing, boolean withGate) {
        Set<Long> solid = new HashSet<>();
        for (RuinLayout.Cell cell : RuinLayout.shell()) {
            if (cell.role() == RuinLayout.Role.AIR) {
                continue;
            }
            if (cell.role() == RuinLayout.Role.GATE && !withGate) {
                continue;
            }
            int[] r = RuinLayout.rotate(cell.x(), cell.z(), facing);
            solid.add(key(r[0], cell.y(), r[1]));
        }
        for (int[] offset : RuinLayout.rotatedPartOffsets(kind, facing)) {
            solid.add(key(offset[0], offset[1], offset[2]));                  // 机关本体
            solid.add(key(offset[0], offset[1] + 1, offset[2]));              // 上方线索石板
        }
        solid.add(key(0, 0, 0));                                              // 控制器
        return solid;
    }

    /** 从某点做 4 向 BFS：脚下要实心、身位与头上一格要空（玩家身高 2 格）。*/
    private static Set<Long> walkableFrom(Set<Long> solid, long[] start) {
        Set<Long> seen = new HashSet<>();
        ArrayDeque<Long> queue = new ArrayDeque<>();
        for (long candidate : start) {
            if (walkable(solid, candidate)) {
                seen.add(candidate);
                queue.add(candidate);
            }
        }
        while (!queue.isEmpty()) {
            long here = queue.remove();
            for (int[] d : new int[][]{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}) {
                long next = shift(here, d[0], d[1]);
                if (!seen.contains(next) && walkable(solid, next)) {
                    seen.add(next);
                    queue.add(next);
                }
            }
        }
        return seen;
    }

    private static boolean walkable(Set<Long> solid, long position) {
        return !solid.contains(position) && !solid.contains(above(position))
                && solid.contains(below(position));
    }
}
