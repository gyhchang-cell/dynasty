import com.dynasty.puzzle.PuzzleRoomState;
import com.dynasty.puzzle.PuzzleRules;

import java.util.ArrayList;
import java.util.List;

/**
 * 遗迹机关核心逻辑的可运行测试（不需要 JUnit、不需要 Minecraft 运行时）。
 *
 * 运行：
 *   ./gradlew compileJava --offline
 *   javac -cp build/classes/java/main -d /tmp/puzzle_test tools/puzzle/PuzzleRulesTest.java
 *   java  -cp build/classes/java/main:/tmp/puzzle_test PuzzleRulesTest
 *
 * 只测纯逻辑（PuzzleRules / PuzzleRoomState）；界面、音效、多人真机行为不在本测试范围。
 */
public final class PuzzleRulesTest {

    private static int passed;
    private static final List<String> failures = new ArrayList<>();

    public static void main(String[] args) {
        dialRotation();
        dialCluesMatchTargets();
        bellSequences();
        bellGatingWhileDemoing();
        lampToggleRule();
        lampLayoutsSolvable();
        resetDoesNotRefreshClaimed();
        roomsAreIsolated();
        sameTemplateDifferentIdentity();
        saveAndLoad();
        missingPartsBlockSolve();
        twoPlayersOneReward();
        rewardRetryAfterNoSpace();
        duplicateClaimIgnored();
        serverSideHasNoClientImports();

        System.out.println();
        System.out.println("通过 " + passed + " 项，失败 " + failures.size() + " 项");
        for (String failure : failures) {
            System.out.println("  ❌ " + failure);
        }
        if (!failures.isEmpty()) {
            System.exit(1);
        }
        System.out.println("✅ 遗迹机关核心逻辑测试全部通过");
    }

    // ------------------------------------------------------------------ 用例

    private static void dialRotation() {
        check("星盘：一转一步（北→东→南→西→北）",
                PuzzleRules.rotate(0) == 1 && PuzzleRules.rotate(1) == 2
                        && PuzzleRules.rotate(2) == 3 && PuzzleRules.rotate(3) == 0);
        check("星盘：转四次回到原朝向",
                PuzzleRules.rotateTimes(2, 4) == 2 && PuzzleRules.rotateTimes(3, 8) == 3);
        PuzzleRoomState room = new PuzzleRoomState(PuzzleRules.Kind.STAR, 0);
        int first = room.rotateDial("0,0,0", 0);
        int initial = PuzzleRules.starInitial(0)[0];
        check("星盘：状态机每次旋转都往前走一步", first == PuzzleRules.rotate(initial));
        for (int i = 0; i < 3; i++) {
            room.rotateDial("0,0,0", 0);
        }
        check("星盘：状态机转四次回到初始朝向",
                room.dialOrientation("0,0,0", 0) == initial);
    }

    private static void bellSequences() {
        check("编钟：三套序列长度分别是 3 / 4 / 5",
                PuzzleRules.bellSequence(0).length == 3 && PuzzleRules.bellSequence(1).length == 4
                        && PuzzleRules.bellSequence(2).length == 5);
        check("编钟：正确序列被接受",
                PuzzleRules.bellCorrect(0, PuzzleRules.bellSequence(0))
                        && PuzzleRules.bellCorrect(1, PuzzleRules.bellSequence(1))
                        && PuzzleRules.bellCorrect(2, PuzzleRules.bellSequence(2)));
        int[] wrong = PuzzleRules.bellSequence(1).clone();
        wrong[0] = (wrong[0] + 1) % 5;
        check("编钟：错误序列被拒绝且能立刻报前缀错",
                !PuzzleRules.bellCorrect(1, wrong) && PuzzleRules.bellPrefixMismatch(1, wrong));
        check("编钟：长度不足时不算完成",
                !PuzzleRules.bellCorrect(2, new int[]{PuzzleRules.bellSequence(2)[0]}));

        PuzzleRoomState room = new PuzzleRoomState(PuzzleRules.Kind.BELL, 0);
        for (int tone : PuzzleRules.bellSequence(0)) {
            room.bellPress(tone);
        }
        check("编钟：按对顺序后状态机判定完成", room.bellInputCorrect() && room.satisfied());
        room.clearBellInput();
        room.bellPress((PuzzleRules.bellSequence(0)[0] + 1) % 5);
        boolean wrongDetected = room.bellInputWrong();
        room.clearBellInput();
        check("编钟：敲错能被识别，清空后回到等待输入", wrongDetected && room.bellInput().isEmpty());
    }

    private static void bellGatingWhileDemoing() {
        check("编钟：演示中不接受输入", !PuzzleRules.bellAcceptsInput(true, false));
        check("编钟：演示中重复请求不会叠加（拒绝新演示）", !PuzzleRules.demoMayStart(true, false));
        check("编钟：演示结束后可以输入", PuzzleRules.bellAcceptsInput(false, false)
                && PuzzleRules.demoMayStart(false, false));
        check("编钟：已解开后不再接受输入/演示", !PuzzleRules.bellAcceptsInput(false, true)
                && !PuzzleRules.demoMayStart(false, true));
    }

    private static void lampToggleRule() {
        int[] lamps = {1, 0, 1, 1};
        int[] after = PuzzleRules.lampToggle(lamps, 1);
        check("灯阵：点第 2 盏会切换自己与顺时针相邻（第 3 盏）",
                after[1] == 1 && after[2] == 0 && after[0] == lamps[0] && after[3] == lamps[3]);
        int[] ring = PuzzleRules.ringOrder(new int[]{0, 3, 0, -3}, new int[]{-3, 0, 3, 0});
        check("灯阵：环序为俯视顺时针（北→东→南→西）",
                ring[0] == 0 && ring[1] == 1 && ring[2] == 2 && ring[3] == 3);
        check("灯阵：环序取下一盏正确", PuzzleRules.nextInRing(ring, 0) == 1
                && PuzzleRules.nextInRing(ring, 3) == 0);
        check("灯阵：全亮判定", PuzzleRules.lampSolved(new int[]{1, 1, 1, 1})
                && !PuzzleRules.lampSolved(new int[]{1, 0, 1, 1}));
    }

    private static void lampLayoutsSolvable() {
        check("灯阵：三套初始状态都可解且非开局即完成", PuzzleRules.validateLampLayouts() == null);
        for (int layout = 0; layout < PuzzleRules.LAYOUTS; layout++) {
            int[] state = PuzzleRules.lampInitial(layout);
            int[] solution = PuzzleRules.lampSolution(state);
            boolean ok = solution != null && solution.length > 0;
            if (ok) {
                for (int press : solution) {
                    state = PuzzleRules.lampToggle(state, press);
                }
                ok = PuzzleRules.lampSolved(state);
            }
            check("灯阵：布局 " + layout + " 按解操作后全亮", ok);
        }
    }

    private static void resetDoesNotRefreshClaimed() {
        PuzzleRoomState claimed = new PuzzleRoomState(PuzzleRules.Kind.STAR, 0);
        claimed.solve("minecraft:emerald=3");
        claimed.claim("player-a");
        check("重置：已领奖的房间拒绝重置", !claimed.reset() && claimed.rewardClaimed()
                && !claimed.rewardAvailable());
        PuzzleRoomState solvedOnly = new PuzzleRoomState(PuzzleRules.Kind.STAR, 0);
        solvedOnly.solve("minecraft:emerald=2");
        check("重置：已解开未领奖也拒绝重置（不能重刷）", !solvedOnly.reset() && solvedOnly.solved());
        PuzzleRoomState fresh = new PuzzleRoomState(PuzzleRules.Kind.STAR, 0);
        fresh.rotateDial("1,0,1", 0);
        check("重置：未解开的房间可以重置并清空进度", fresh.reset() && fresh.dials().isEmpty());
    }

    private static void dialCluesMatchTargets() {
        boolean unique = true;
        for (int layout = 0; layout < PuzzleRules.LAYOUTS; layout++) {
            int[] fromClues = new int[4];
            for (int dial = 0; dial < 4; dial++) {
                fromClues[dial] = PuzzleRules.starTarget(layout, dial);
            }
            if (!PuzzleRules.starSolved(layout, fromClues)) {
                unique = false;
            }
            int[] wrong = fromClues.clone();
            wrong[2] = PuzzleRules.rotate(wrong[2]);
            if (PuzzleRules.starSolved(layout, wrong)) {
                unique = false;
            }
        }
        check("星盘：三套线索都能唯一推出目标（错一盘就不算完成）", unique);
        check("星盘：布局校验通过（无重复、非完成态）", PuzzleRules.validateStarLayouts() == null);

        PuzzleRoomState room = new PuzzleRoomState(PuzzleRules.Kind.STAR, 1);
        for (int dial = 0; dial < 4; dial++) {
            String key = "0,0," + dial;
            int guard = 0;
            while (room.dialOrientation(key, dial) != PuzzleRules.starTarget(1, dial) && guard++ < 8) {
                room.rotateDial(key, dial);
            }
        }
        check("星盘：四盘都转到目标后状态机判定完成", room.satisfied() && room.dialsSatisfied());
    }

    private static void roomsAreIsolated() {
        PuzzleRoomState first = new PuzzleRoomState(PuzzleRules.Kind.STAR, 0);
        PuzzleRoomState second = new PuzzleRoomState(PuzzleRules.Kind.STAR, 0);
        first.rotateDial("0,0,0", 0);
        check("房间隔离：A 的进度不影响 B", !first.dials().isEmpty() && second.dials().isEmpty());
        first.solve("minecraft:emerald=1");
        first.claim("player-a");
        check("房间隔离：A 领奖不影响 B 的可领状态",
                !second.solved() && !second.rewardClaimed() && first.rewardClaimed());
    }

    private static void sameTemplateDifferentIdentity() {
        String one = PuzzleRules.roomKey("minecraft:overworld", 10, 64, 20);
        String two = PuzzleRules.roomKey("minecraft:overworld", 10, 64, 21);
        String other = PuzzleRules.roomKey("dynasty:celestial_dynasty", 10, 64, 20);
        check("房间身份：同模板两次放置身份不同", !one.equals(two));
        check("房间身份：不同维度不串状态", !one.equals(other));
    }

    private static void saveAndLoad() {
        PuzzleRoomState room = new PuzzleRoomState(PuzzleRules.Kind.ELEMENTS, 2);
        room.toggleLamp("0,0,-3", 0, "3,0,0", 1);
        room.solve("minecraft:emerald=4,minecraft:iron_ingot=2");
        PuzzleRoomState loaded = PuzzleRoomState.fromLine(room.toLine());
        check("存档：行格式往返保留灯阵状态", loaded != null && loaded.lamps().size() == 2
                && loaded.lampState("0,0,-3", 0) == room.lampState("0,0,-3", 0));
        check("存档：已解开与奖励结果一起保留", loaded != null && loaded.solved()
                && !loaded.rewardClaimed() && loaded.rewardRoll().equals(room.rewardRoll()));
        loaded.claim("player-b");
        PuzzleRoomState again = PuzzleRoomState.fromLine(loaded.toLine());
        check("存档：已领奖状态保留（重载后不会重新可领）",
                again != null && again.rewardClaimed() && !again.rewardAvailable());
        check("存档：坏行返回 null（不影响其它房间）", PuzzleRoomState.fromLine("garbage") == null);
    }

    private static void missingPartsBlockSolve() {
        PuzzleRoomState room = new PuzzleRoomState(PuzzleRules.Kind.STAR, 0);
        for (int dial = 0; dial < 3; dial++) {
            String key = "0,0," + dial;
            int guard = 0;
            while (room.dialOrientation(key, dial) != PuzzleRules.starTarget(0, dial) && guard++ < 8) {
                room.rotateDial(key, dial);
            }
        }
        check("部件缺失：只到 3 个星盘时不算完成", !room.satisfied());
        check("部件缺失：不满足时不给奖励", !room.rewardAvailable());
    }

    private static void twoPlayersOneReward() {
        PuzzleRoomState room = new PuzzleRoomState(PuzzleRules.Kind.BELL, 0);
        for (int tone : PuzzleRules.bellSequence(0)) {
            room.bellPress(tone);
        }
        room.solve("minecraft:emerald=3");
        check("奖励：第一个玩家领取成功", room.claim("player-a"));
        check("奖励：第二个玩家（同时点击）领不到", !room.claim("player-b")
                && room.claimedBy().equals("player-a"));
    }

    private static void rewardRetryAfterNoSpace() {
        PuzzleRoomState room = new PuzzleRoomState(PuzzleRules.Kind.STAR, 0);
        room.solve("minecraft:emerald=5,minecraft:bread=2");
        String rollBefore = room.rewardRoll();
        check("奖励：未领取时一直可领（背包满时由调用方拒绝，状态不变）",
                room.rewardAvailable() && room.rewardRoll().equals(rollBefore));
        check("奖励：重试领取后结果不变（不会重新抽奖）",
                room.claim("player-a") && room.rewardRoll().equals(rollBefore));
    }

    private static void duplicateClaimIgnored() {
        PuzzleRoomState room = new PuzzleRoomState(PuzzleRules.Kind.STAR, 0);
        room.solve("minecraft:emerald=1");
        room.claim("player-a");
        check("重复数据包：重复领取被拒绝且不改状态", !room.claim("player-a") && !room.claim("player-b")
                && room.claimedBy().equals("player-a"));
    }

    /** 专用服务器不得加载客户端类：机关包与命令不得引用 net.minecraft.client.* */
    private static void serverSideHasNoClientImports() {
        String[] files = {"PuzzleService.java", "PuzzleBlocks.java", "PuzzleRules.java",
                "PuzzleRoomState.java", "PuzzleSavedData.java", "PuzzleTemplates.java", "PuzzleCommand.java"};
        StringBuilder problems = new StringBuilder();
        for (String name : files) {
            java.nio.file.Path path = java.nio.file.Paths.get("src/main/java/com/dynasty/puzzle/" + name);
            try {
                String text = java.nio.file.Files.readString(path);
                if (text.contains("net.minecraft.client") || text.contains("Dist.CLIENT")) {
                    problems.append(name).append(' ');
                }
            } catch (java.io.IOException error) {
                problems.append(name).append("(读不到) ");
            }
        }
        check("专用服务器：机关包与命令未引用客户端类", problems.length() == 0);
    }

    private static void check(String name, boolean condition) {
        if (condition) {
            passed++;
            System.out.println("  ✓ " + name);
        } else {
            failures.add(name);
            System.out.println("  ✗ " + name);
        }
    }
}
