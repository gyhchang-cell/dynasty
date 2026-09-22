package com.dynasty.puzzle;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 一个房间的持久化状态（纯逻辑 + 行格式序列化，可单元测试）。
 *
 * 部件一律用**相对控制器的偏移**做键（`dx,dy,dz`）：可验证的相对坐标，
 * 同一模板多次放置/旋转都不会串状态，也不怕某个部件被拆导致下标错位。
 *
 * 谜面进度（星盘朝向、灯阵亮灭）在**第一次交互时按部件排序下标**取初始值并落盘，
 * 因此重载后不会把转过的星盘重置回初始朝向。
 */
public final class PuzzleRoomState {

    public static final String FORMAT = "puzzle-v1";

    private final PuzzleRules.Kind kind;
    private final int layout;

    private boolean solved;
    private boolean rewardClaimed;
    /** 奖励在**解开时**就抽好并存下来：背包满重试不会重新抽奖 */
    private String rewardRoll = "";
    private String claimedBy = "";

    private final Map<String, Integer> dials = new LinkedHashMap<>();
    private final Map<String, Integer> lamps = new LinkedHashMap<>();
    private final List<Integer> bellInput = new ArrayList<>();

    public PuzzleRoomState(PuzzleRules.Kind kind, int layout) {
        this.kind = kind;
        this.layout = PuzzleRules.wrap(layout);
    }

    public PuzzleRules.Kind kind() {
        return kind;
    }

    public int layout() {
        return layout;
    }

    public boolean solved() {
        return solved;
    }

    public boolean rewardClaimed() {
        return rewardClaimed;
    }

    public boolean rewardAvailable() {
        return solved && !rewardClaimed && !rewardRoll.isEmpty();
    }

    public String rewardRoll() {
        return rewardRoll;
    }

    public String claimedBy() {
        return claimedBy;
    }

    public Map<String, Integer> dials() {
        return dials;
    }

    public Map<String, Integer> lamps() {
        return lamps;
    }

    public List<Integer> bellInput() {
        return bellInput;
    }

    // ------------------------------------------------------------------ 星盘

    public int dialOrientation(String partKey, int sortedIndex) {
        Integer value = dials.get(partKey);
        if (value != null) {
            return value;
        }
        int initial = PuzzleRules.starInitial(layout)[Math.floorMod(sortedIndex, 4)];
        dials.put(partKey, initial);
        return initial;
    }

    /** 右键旋转一次；返回新的朝向 */
    public int rotateDial(String partKey, int sortedIndex) {
        int next = PuzzleRules.rotate(dialOrientation(partKey, sortedIndex));
        dials.put(partKey, next);
        return next;
    }

    /** 四个星盘是否都对上目标（不改状态）*/
    public boolean dialsSatisfied() {
        if (dials.size() < 4) {
            return false;
        }
        int index = 0;
        for (int orientation : dials.values()) {
            if (Math.floorMod(orientation, 4) != PuzzleRules.starTarget(layout, index)) {
                return false;
            }
            index++;
        }
        return index == 4;
    }

    // ------------------------------------------------------------------ 编钟

    public void bellPress(int tone) {
        bellInput.add(Math.floorMod(tone, 5));
    }

    public void clearBellInput() {
        bellInput.clear();
    }

    public boolean bellInputCorrect() {
        return PuzzleRules.bellCorrect(layout, PuzzleRoomState.toArray(bellInput));
    }

    public boolean bellInputWrong() {
        return PuzzleRules.bellPrefixMismatch(layout, PuzzleRoomState.toArray(bellInput));
    }

    // ------------------------------------------------------------------ 四象灯

    public int lampState(String partKey, int sortedIndex) {
        Integer value = lamps.get(partKey);
        if (value != null) {
            return value;
        }
        int initial = PuzzleRules.lampInitial(layout)[Math.floorMod(sortedIndex, 4)];
        lamps.put(partKey, initial);
        return initial;
    }

    /** 点灯：切换自己与顺时针相邻的一盏；返回本灯位新状态 */
    public int toggleLamp(String partKey, int sortedIndex, String neighbourKey, int neighbourIndex) {
        int self = lampState(partKey, sortedIndex);
        int neighbour = lampState(neighbourKey, neighbourIndex);
        lamps.put(partKey, self == 0 ? 1 : 0);
        lamps.put(neighbourKey, neighbour == 0 ? 1 : 0);
        return lamps.get(partKey);
    }

    public boolean lampsSatisfied() {
        if (lamps.size() < 4) {
            return false;
        }
        for (int state : lamps.values()) {
            if (state == 0) {
                return false;
            }
        }
        return true;
    }

    // ------------------------------------------------------------------ 完成 / 重置 / 奖励

    public boolean satisfied() {
        return switch (kind) {
            case STAR -> dialsSatisfied();
            case BELL -> bellInputCorrect();
            case ELEMENTS -> lampsSatisfied();
        };
    }

    /** 标记解开并写入一次奖励结果；重复调用不会改变已存结果。 */
    public void solve(String roll) {
        if (!solved) {
            solved = true;
            rewardRoll = roll;
        }
    }

    public boolean claim(String playerId) {
        if (!rewardAvailable()) {
            return false;
        }
        rewardClaimed = true;
        claimedBy = playerId;
        return true;
    }

    /** 重置进度；**已解开或已领奖的房间拒绝重置**（不能用重置刷奖励）。 */
    public boolean reset() {
        if (solved || rewardClaimed) {
            return false;
        }
        dials.clear();
        lamps.clear();
        bellInput.clear();
        return true;
    }

    // ------------------------------------------------------------------ 序列化（行格式，坏行返回 null）

    public String toLine() {
        return FORMAT + '|' + kind + '|' + layout + '|' + (solved ? 1 : 0) + '|' + (rewardClaimed ? 1 : 0)
                + '|' + encodeMap(dials) + '|' + encodeMap(lamps) + '|' + encodeList(bellInput)
                + '|' + claimedBy + '|' + rewardRoll;
    }

    public static PuzzleRoomState fromLine(String line) {
        String[] parts = line.split("\\|", -1);
        if (parts.length < 10 || !parts[0].startsWith("puzzle-v")) {
            return null;
        }
        try {
            PuzzleRoomState state = new PuzzleRoomState(PuzzleRules.Kind.valueOf(parts[1]),
                    Integer.parseInt(parts[2]));
            state.solved = "1".equals(parts[3]);
            state.rewardClaimed = "1".equals(parts[4]);
            decodeMap(parts[5], state.dials);
            decodeMap(parts[6], state.lamps);
            decodeList(parts[7], state.bellInput);
            state.claimedBy = parts[8];
            state.rewardRoll = parts[9];
            return state;
        } catch (RuntimeException ignored) {
            return null;
        }
    }

    private static String encodeMap(Map<String, Integer> map) {
        StringBuilder builder = new StringBuilder();
        for (Map.Entry<String, Integer> entry : map.entrySet()) {
            if (builder.length() > 0) {
                builder.append(';');          // 部件键里含逗号，所以用分号分隔条目
            }
            builder.append(entry.getKey()).append('=').append(entry.getValue());
        }
        return builder.toString();
    }

    private static void decodeMap(String text, Map<String, Integer> target) {
        if (text == null || text.isEmpty()) {
            return;
        }
        for (String pair : text.split(";")) {
            String[] keyValue = pair.split("=");
            if (keyValue.length == 2) {
                target.put(keyValue[0], Integer.parseInt(keyValue[1]));
            }
        }
    }

    private static String encodeList(List<Integer> list) {
        StringBuilder builder = new StringBuilder();
        for (int value : list) {
            if (builder.length() > 0) {
                builder.append(',');
            }
            builder.append(value);
        }
        return builder.toString();
    }

    private static void decodeList(String text, List<Integer> target) {
        if (text == null || text.isEmpty()) {
            return;
        }
        for (String value : text.split(",")) {
            target.add(Integer.parseInt(value));
        }
    }

    public static int[] toArray(List<Integer> list) {
        int[] array = new int[list.size()];
        for (int i = 0; i < array.length; i++) {
            array[i] = list.get(i);
        }
        return array;
    }
}
