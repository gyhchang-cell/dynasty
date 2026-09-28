import com.dynasty.DynastyTooltipBudget;
import com.dynasty.client.DynastyTooltipText;
import com.dynasty.entity.BossBarVisibility;
import com.dynasty.entity.DynastySpawnPlacement;
import net.minecraft.world.entity.MobSpawnType;

import java.util.ArrayList;
import java.util.List;

/**
 * 本轮两项改造的**可执行逻辑测试**（不需要启动游戏）。
 *
 * 直接调用生产类：
 *   * {@link BossBarVisibility} —— 叛将血条「该不该给这个玩家看」的纯判定；
 *   * {@link DynastySpawnPlacement} —— 自然生成落点校验的「严格 / 放行」分档；
 *   * {@link DynastyTooltipText} —— 悬停说明的数值折叠（运算类型）与预算。
 *
 * 运行：bash tools/eqdev/run_eqdev_tests.sh
 */
public final class EqDevLogicTest {

    private static int passed;
    private static final List<String> failures = new ArrayList<>();

    public static void main(String[] args) {
        bossBarVisibility();
        twoPlayers();
        spawnPlacement();
        tooltipMath();
        System.out.println();
        if (failures.isEmpty()) {
            System.out.println("通过 " + passed + " 项，失败 0 项");
            System.out.println("✅ 叛将血条判定 / 生成落点 / 悬停数值折叠 逻辑测试全部通过");
        } else {
            System.out.println("通过 " + passed + " 项，失败 " + failures.size() + " 项");
            for (String failure : failures) {
                System.out.println("  ❌ " + failure);
            }
            System.exit(1);
        }
    }

    private static void check(String name, boolean ok) {
        if (ok) {
            passed++;
        } else {
            failures.add(name);
        }
    }

    private static void check(String name, boolean ok, String detail) {
        if (ok) {
            passed++;
        } else {
            failures.add(name + " —— " + detail);
        }
    }

    /* ---------- 血条：单玩家各种情形 ---------- */

    private static void bossBarVisibility() {
        check("血条：常量合理（0 < 宽限 < 遗忘；间隔不每 tick；保持距离 ≥ 显示距离）",
                BossBarVisibility.GRACE_TICKS > 0
                        && BossBarVisibility.FORGET_TICKS > BossBarVisibility.GRACE_TICKS
                        && BossBarVisibility.CHECK_INTERVAL >= 5
                        && BossBarVisibility.KEEP_DISTANCE >= BossBarVisibility.SHOW_DISTANCE
                        && BossBarVisibility.ENGAGE_TICKS > 0);

        check("血条：初次隔着山体 / 在地下（没看见、没交战、也没见过）→ 不显示",
                !BossBarVisibility.visible(30.0D, false, false, false, 9_999));

        check("血条：同维度、视线通畅、距离合适 → 显示",
                BossBarVisibility.visible(20.0D, true, false, false, 0));

        check("血条：看得见但太远 → 不显示",
                !BossBarVisibility.visible(BossBarVisibility.SHOW_DISTANCE + 1.0D, true, false, false, 0));

        check("血条：交战中在保持距离内 → 显示；超出 → 不显示",
                BossBarVisibility.visible(45.0D, false, true, true, 5_000)
                        && !BossBarVisibility.visible(BossBarVisibility.KEEP_DISTANCE + 1.0D, false, true, true, 0));

        check("血条：战斗中短暂遮挡（曾见过 + 宽限内）→ 保持显示，不闪烁",
                BossBarVisibility.visible(30.0D, false, false, true, BossBarVisibility.GRACE_TICKS - 1));

        check("血条：宽限刚过又没交战 → 收起",
                !BossBarVisibility.visible(30.0D, false, false, true, BossBarVisibility.GRACE_TICKS + 1));

        check("血条：交战中即使长时间被遮挡也不收起（对方还在打你）",
                BossBarVisibility.visible(25.0D, false, true, true, BossBarVisibility.FORGET_TICKS * 2));

        check("血条：走远且未交战 → 收起（离开范围）",
                !BossBarVisibility.visible(30.0D, false, false, true, 201));

        check("血条：看清过又贴脸 → 显示（不因为「没见过」被误伤）",
                BossBarVisibility.visible(10.0D, true, false, true, 3));

        check("血条：维护成本收敛（不可见且没见过且长时间没有交互 → 可以忘记该玩家）",
                !BossBarVisibility.worthKeeping(false, false, BossBarVisibility.FORGET_TICKS + 1)
                        && BossBarVisibility.worthKeeping(false, true, BossBarVisibility.FORGET_TICKS + 1)
                        && BossBarVisibility.worthKeeping(false, false, 5));
    }

    /* ---------- 血条：两位玩家差异（同一次判定里各自独立） ---------- */

    private static void twoPlayers() {
        boolean a = BossBarVisibility.visible(28.0D, true, false, false, 9_999);
        boolean b = BossBarVisibility.visible(28.0D, false, false, false, 9_999);
        check("血条：同距离下，看得见的玩家有血条，隔墙的玩家没有", a && !b);

        boolean c = BossBarVisibility.visible(60.0D, false, true, true, 0);
        check("血条：交战中但超出保持距离 → 不显示", !c);

        boolean d = BossBarVisibility.visible(45.0D, false, true, true, 1_000);
        boolean e = BossBarVisibility.visible(45.0D, false, false, false, 1_000);
        check("血条：两名玩家同距离时按「是否交战 / 是否见过」分别判定", d && !e);
    }

    /* ---------- 生成落点：自然生成严格，其它入口放行 ---------- */

    private static void spawnPlacement() {
        check("生成：自然生成 / 区块生成要做落点校验",
                DynastySpawnPlacement.strict(MobSpawnType.NATURAL)
                        && DynastySpawnPlacement.strict(MobSpawnType.CHUNK_GENERATION));
        check("生成：刷怪蛋 / 命令 / 召唤 / 结构 / 刷怪笼一律放行（不一刀切）",
                !DynastySpawnPlacement.strict(MobSpawnType.SPAWN_EGG)
                        && !DynastySpawnPlacement.strict(MobSpawnType.COMMAND)
                        && !DynastySpawnPlacement.strict(MobSpawnType.MOB_SUMMONED)
                        && !DynastySpawnPlacement.strict(MobSpawnType.STRUCTURE)
                        && !DynastySpawnPlacement.strict(MobSpawnType.SPAWNER)
                        && !DynastySpawnPlacement.strict(MobSpawnType.DISPENSER));
        check("生成：没有任何输入时安全返回 false（不抛异常）",
                !DynastySpawnPlacement.hasStandingSpace(null, null, null));
    }

    /* ---------- 悬停：属性运算类型与预算 ---------- */

    private static void tooltipMath() {
        check("悬停：默认预算与文档一致（3 行）", DynastyTooltipBudget.BRIEF_LIMIT == 3
                && DynastyTooltipText.BRIEF_LIMIT == DynastyTooltipBudget.BRIEF_LIMIT);

        double additionOnly = DynastyTooltipText.fold(0.0D, List.of(
                new DynastyTooltipText.Mod(DynastyTooltipText.OP_ADDITION, 4.0D),
                new DynastyTooltipText.Mod(DynastyTooltipText.OP_ADDITION, 6.0D)));
        check("悬停：多个加法修饰符相加", additionOnly == 10.0D, "得到 " + additionOnly);

        // 加法 + 基础乘 + 总乘：(0+5) * (1+0.2) * (1+0.5) = 9
        double folded = DynastyTooltipText.fold(0.0D, List.of(
                new DynastyTooltipText.Mod(DynastyTooltipText.OP_ADDITION, 5.0D),
                new DynastyTooltipText.Mod(DynastyTooltipText.OP_MULTIPLY_BASE, 0.2D),
                new DynastyTooltipText.Mod(DynastyTooltipText.OP_MULTIPLY_TOTAL, 0.5D)));
        check("悬停：按原版顺序折叠（加法 → 基础乘 → 总乘）", Math.abs(folded - 9.0D) < 1.0E-9D,
                "得到 " + folded + "，期望 9");
        check("悬停：确实不是「把修饰符数值直接相加」", Math.abs(folded - 5.7D) > 1.0E-9D);

        double chained = DynastyTooltipText.fold(1.0D, List.of(
                new DynastyTooltipText.Mod(DynastyTooltipText.OP_MULTIPLY_TOTAL, 0.5D),
                new DynastyTooltipText.Mod(DynastyTooltipText.OP_MULTIPLY_TOTAL, 0.5D)));
        check("悬停：多个总乘要连乘（2.25 而不是 2.0）", Math.abs(chained - 2.25D) < 1.0E-9D,
                "得到 " + chained);

        double baseMult = DynastyTooltipText.fold(10.0D, List.of(
                new DynastyTooltipText.Mod(DynastyTooltipText.OP_MULTIPLY_BASE, 0.1D),
                new DynastyTooltipText.Mod(DynastyTooltipText.OP_MULTIPLY_BASE, 0.2D)));
        check("悬停：多个基础乘先相加再乘（13.0）", Math.abs(baseMult - 13.0D) < 1.0E-9D,
                "得到 " + baseMult);

        double unknown = DynastyTooltipText.fold(0.0D, List.of(new DynastyTooltipText.Mod(42, 7.0D)));
        check("悬停：未知运算类型保守按加法处理（不丢数值）", unknown == 7.0D, "得到 " + unknown);

        check("悬停：套装减伤按真实上限截断（将军铠 16% × 4 = 64%；鲛绡甲 28% × 4 → 90%）",
                Math.abs(DynastyTooltipText.fullSetReduction(0.16D) - 0.64D) < 1.0E-9D
                        && Math.abs(DynastyTooltipText.fullSetReduction(0.28D) - 0.90D) < 1.0E-9D);
        check("悬停：实穿件数减伤按件数与上限计算，件数夹在 0..4",
                Math.abs(DynastyTooltipText.wornReduction(0.25D, 2) - 0.50D) < 1.0E-9D
                        && Math.abs(DynastyTooltipText.wornReduction(0.33D, 4) - 0.90D) < 1.0E-9D
                        && DynastyTooltipText.wornReduction(0.21D, 0) == 0.0D
                        && Math.abs(DynastyTooltipText.wornReduction(0.21D, 9) - 0.84D) < 1.0E-9D);

        check("悬停：百分比与数字格式（16% / 5.5% / 90% / 16 / 16.5）",
                "16%".equals(DynastyTooltipText.percent(0.16D))
                        && "5.5%".equals(DynastyTooltipText.percent(0.055D))
                        && "90%".equals(DynastyTooltipText.percent(0.9D))
                        && "16".equals(DynastyTooltipText.number(16.0D))
                        && "16.5".equals(DynastyTooltipText.number(16.5D)));
    }
}
