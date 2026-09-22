package com.dynasty.puzzle;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

/**
 * 遗迹机关的**纯规则**（不引用任何 Minecraft 类，便于 javac 直接跑测试）。
 *
 *   STAR     星盘归位：4 个星盘 × 4 朝向，全部对上目标朝向才开宝室；
 *   BELL     编钟回声：演示一段音序，玩家按顺序重敲（音高区分 + 文字显示音位）；
 *   ELEMENTS 四象点灯：青龙/白虎/朱雀/玄武，点一盏会同时切换自己与顺时针相邻的一盏。
 *
 * 布局（三套）由控制器 VARIANT 决定，所以同一模板多次放置可以用不同谜题。
 */
public final class PuzzleRules {

    private PuzzleRules() {
    }

    public enum Kind {
        STAR(4), BELL(5), ELEMENTS(4);

        public final int parts;

        Kind(int parts) {
            this.parts = parts;
        }

        public static Kind byName(String name) {
            for (Kind kind : values()) {
                if (kind.name().equalsIgnoreCase(name)) {
                    return kind;
                }
            }
            return null;
        }
    }

    /** 每种机关三套布局 / three layouts per kind */
    public static final int LAYOUTS = 3;

    /** 方向名（翻译键后缀）/ four facings */
    public static final String[] FACING_KEYS = {"north", "east", "south", "west"};

    /** 四象（顺时针）/ four symbols clockwise */
    public static final String[] SYMBOL_KEYS = {"dragon", "tiger", "bird", "turtle"};

    /** 五个音位 / five bell tones */
    public static final String[] TONE_KEYS = {"jue", "shang", "gong", "zhi", "yu"};

    /** 五音音高 / vanilla bell pitches */
    public static final float[] TONE_PITCH = {0.6F, 0.8F, 1.0F, 1.25F, 1.5F};

    /** 星盘三套目标（0=北 1=东 2=南 3=西）/ dial targets per layout */
    private static final int[][] STAR_TARGETS = {
            {1, 3, 0, 2},
            {2, 0, 3, 1},
            {3, 2, 1, 0},
    };

    /** 星盘三套初始：都不等于目标 / dial initial states */
    private static final int[][] STAR_INITIAL = {
            {0, 0, 0, 0},
            {1, 1, 1, 1},
            {0, 2, 3, 1},
    };

    /** 编钟三套固定序列（长度 3 / 4 / 5）/ bell sequences */
    private static final int[][] BELL_SEQUENCES = {
            {2, 0, 4},
            {1, 3, 0, 2},
            {4, 2, 1, 3, 0},
    };

    /** 四象灯三套初始（由合法操作从全亮推出，必然可解且非完成态）*/
    private static final int[][] LAMP_INITIAL = {
            {0, 1, 0, 1},
            {1, 0, 1, 0},
            {0, 1, 1, 0},
    };

    // ------------------------------------------------------------------ 星盘

    public static int starTarget(int layout, int dial) {
        return STAR_TARGETS[wrap(layout)][dial];
    }

    public static int[] starTargets(int layout) {
        return STAR_TARGETS[wrap(layout)].clone();
    }

    public static int[] starInitial(int layout) {
        return STAR_INITIAL[wrap(layout)].clone();
    }

    /** 旋转一次：北→东→南→西→北 */
    public static int rotate(int orientation) {
        return Math.floorMod(orientation + 1, 4);
    }

    /** 转 4 次回到原朝向 */
    public static int rotateTimes(int orientation, int times) {
        int result = Math.floorMod(orientation, 4);
        for (int i = 0; i < Math.floorMod(times, 4); i++) {
            result = rotate(result);
        }
        return result;
    }

    public static boolean starSolved(int layout, int[] orientations) {
        int[] target = STAR_TARGETS[wrap(layout)];
        if (orientations == null || orientations.length != target.length) {
            return false;
        }
        for (int i = 0; i < target.length; i++) {
            if (Math.floorMod(orientations[i], 4) != target[i]) {
                return false;
            }
        }
        return true;
    }

    /** 该盘还要转几次才能对上（线索/调试提示用）*/
    public static int starTurnsNeeded(int layout, int dial, int orientation) {
        return Math.floorMod(starTarget(layout, dial) - Math.floorMod(orientation, 4), 4);
    }

    // ------------------------------------------------------------------ 编钟

    public static int[] bellSequence(int layout) {
        return BELL_SEQUENCES[wrap(layout)].clone();
    }

    public static int bellSequenceLength(int layout) {
        return BELL_SEQUENCES[wrap(layout)].length;
    }

    public static boolean bellCorrect(int layout, int[] input) {
        return input != null && Arrays.equals(input, BELL_SEQUENCES[wrap(layout)]);
    }

    /** 前缀已经错了（可以立刻反馈，不必等敲完）*/
    public static boolean bellPrefixMismatch(int layout, int[] input) {
        int[] target = BELL_SEQUENCES[wrap(layout)];
        for (int i = 0; i < input.length && i < target.length; i++) {
            if (input[i] != target[i]) {
                return true;
            }
        }
        return false;
    }

    public static int wrap(int layout) {
        return Math.floorMod(layout, LAYOUTS);
    }

    // ------------------------------------------------------------------ 四象灯

    /** 点一盏灯：切换自己 + 顺时针相邻的一盏 */
    public static int[] lampToggle(int[] lamps, int index) {
        int[] next = lamps.clone();
        int self = Math.floorMod(index, next.length);
        int neighbour = (self + 1) % next.length;
        next[self] = next[self] == 0 ? 1 : 0;
        next[neighbour] = next[neighbour] == 0 ? 1 : 0;
        return next;
    }

    public static int[] lampInitial(int layout) {
        return LAMP_INITIAL[wrap(layout)].clone();
    }

    public static boolean lampSolved(int[] lamps) {
        if (lamps == null || lamps.length == 0) {
            return false;
        }
        for (int lamp : lamps) {
            if (lamp == 0) {
                return false;
            }
        }
        return true;
    }

    /** 广度优先求解，返回要按下的灯位顺序（无解返回 null；四盏灯全部可解）*/
    public static int[] lampSolution(int[] initial) {
        int start = bits(initial);
        int goal = (1 << initial.length) - 1;
        if (start == goal) {
            return new int[0];
        }
        int size = 1 << initial.length;
        int[] previous = new int[size];
        int[] pressed = new int[size];
        Arrays.fill(previous, -1);
        List<Integer> queue = new ArrayList<>();
        queue.add(start);
        previous[start] = start;
        int head = 0;
        while (head < queue.size()) {
            int state = queue.get(head++);
            for (int i = 0; i < initial.length; i++) {
                int next = bits(lampToggle(unbits(state, initial.length), i));
                if (previous[next] != -1) {
                    continue;
                }
                previous[next] = state;
                pressed[next] = i;
                if (next == goal) {
                    List<Integer> steps = new ArrayList<>();
                    int cursor = next;
                    while (cursor != start) {
                        steps.add(0, pressed[cursor]);
                        cursor = previous[cursor];
                    }
                    int[] result = new int[steps.size()];
                    for (int k = 0; k < result.length; k++) {
                        result[k] = steps.get(k);
                    }
                    return result;
                }
                queue.add(next);
            }
        }
        return null;
    }

    private static int bits(int[] lamps) {
        int value = 0;
        for (int i = 0; i < lamps.length; i++) {
            value |= (lamps[i] != 0 ? 1 : 0) << i;
        }
        return value;
    }

    private static int[] unbits(int value, int size) {
        int[] lamps = new int[size];
        for (int i = 0; i < size; i++) {
            lamps[i] = (value >> i) & 1;
        }
        return lamps;
    }

    /** 三套灯阵必须「可解且不是开局即完成」；返回 null 表示全部合格。 */
    public static String validateLampLayouts() {
        for (int layout = 0; layout < LAYOUTS; layout++) {
            int[] initial = LAMP_INITIAL[layout];
            if (lampSolved(initial)) {
                return "布局 " + layout + " 开局即完成";
            }
            int[] solution = lampSolution(initial);
            if (solution == null) {
                return "布局 " + layout + " 无解";
            }
            int[] state = initial.clone();
            for (int press : solution) {
                state = lampToggle(state, press);
            }
            if (!lampSolved(state)) {
                return "布局 " + layout + " 的解不正确";
            }
        }
        return null;
    }

    /** 三套星盘布局必须互不重复、目标合法、且都不是开局即完成。 */
    public static String validateStarLayouts() {
        Set<String> seen = new LinkedHashSet<>();
        for (int layout = 0; layout < LAYOUTS; layout++) {
            int[] target = STAR_TARGETS[layout];
            if (starSolved(layout, STAR_INITIAL[layout])) {
                return "星盘布局 " + layout + " 开局即完成";
            }
            for (int dial = 0; dial < target.length; dial++) {
                if (target[dial] < 0 || target[dial] > 3) {
                    return "星盘布局 " + layout + " 第 " + dial + " 盘朝向非法";
                }
            }
            if (!seen.add(Arrays.toString(target))) {
                return "星盘布局 " + layout + " 与前面的重复";
            }
        }
        return null;
    }

    /** 编钟是否允许输入：演示中或已解开都不接受 */
    public static boolean bellAcceptsInput(boolean demoRunning, boolean solved) {
        return !demoRunning && !solved;
    }

    /** 重复演示请求不得叠加：已有演示在跑时拒绝新的请求 */
    public static boolean demoMayStart(boolean demoRunning, boolean solved) {
        return !demoRunning && !solved;
    }

    /** 房间身份：维度 + 控制器坐标（同一模板多次放置自然不同）*/
    public static String roomKey(String dimension, int x, int y, int z) {
        return dimension + "|" + x + "," + y + "," + z;
    }

    /**
     * 四象灯的**顺时针环序**：按俯视角度 atan2(-dz, dx) 排序（MC 里 +x 东、+z 南，
     * 从上方看下去这个顺序就是顺时针）。返回按下标给出的环序位置列表。
     * 纯计算，便于测试。
     */
    public static int[] ringOrder(int[] dx, int[] dz) {
        Integer[] indices = new Integer[dx.length];
        for (int i = 0; i < indices.length; i++) {
            indices[i] = i;
        }
        java.util.Arrays.sort(indices, (a, b) -> Double.compare(angle(dx[a], dz[a]), angle(dx[b], dz[b])));
        int[] order = new int[indices.length];
        for (int i = 0; i < order.length; i++) {
            order[i] = indices[i];
        }
        return order;
    }

    private static double angle(int dx, int dz) {
        return Math.atan2(dz, dx);
    }

    /** 环序中的下一盏（顺时针相邻）*/
    public static int nextInRing(int[] ring, int position) {
        if (ring == null || ring.length == 0) {
            return -1;
        }
        for (int i = 0; i < ring.length; i++) {
            if (ring[i] == position) {
                return ring[(i + 1) % ring.length];
            }
        }
        return ring[0];
    }
}
