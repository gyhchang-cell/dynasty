package com.dynasty;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * 饰品的**命中触发**机制（第三十四轮新增）。
 *
 * 在这之前饰品只会「每秒刷属性 + 挂效果」，命中时什么都不做 —— 唯一有触发感的是武器
 * （见 {@link DynastyCombatEvents}）。这里把同样的手感接到饰品上，而且仍然是**表驱动**：
 * 饰品表第 12~14 格写 `命中编码 / 数值 / 概率(%)`，改表就改行为。
 *
 * | 编码 | 名字 | 数值含义 | 概率含义 |
 * |---|---|---|---|
 * | 1 | 吸血 | 造成伤害的几成回血（0.15 = 15%） | 触发概率 |
 * | 2 | 斩杀 | 目标血量低于上限的几成时直接斩（0.20 = 20%） | 触发概率 |
 * | 3 | 会心 | 额外伤害倍率（0.5 = +50%） | 触发概率 |
 * | 4 | 突袭 | 额外伤害倍率，且**只在目标满血时**生效（开局第一刀） | 触发概率 |
 * | 5 | 连击 | 每一层的额外伤害倍率（连打同一目标叠加，最多 6 层，3 秒内有效） | 触发概率 |
 * | 6 | 雷罚 | 附加的固定伤害 | 触发概率 |
 *
 * 数值刻意做小（10%~18% 一档、会心 25%~40% 概率）：饰品是「陪衬」，不该盖过兵器谱。
 * 斩杀有硬限制：**玩家与 Boss / 神兽不吃斩杀**，且目标血量上限 ≤ 80（杂兵）才会触发，
 * 免得变成一键清场。
 *
 * On-hit procs for accessories: lifesteal, execute, crit, ambush, combo, thunder — driven by
 * the last three columns of the accessory table so balance stays in one place.
 */
public final class DynastyTrinketOnHit {

    /** 命中编码 / proc codes */
    public static final int LIFESTEAL = 1;
    public static final int EXECUTE = 2;
    public static final int CRIT = 3;
    public static final int AMBUSH = 4;
    public static final int COMBO = 5;
    public static final int THUNDER = 6;

    /** 斩杀的安全线：血量上限高于这个数的目标不吃斩杀（Boss / 神兽 / 巨兽）。 */
    private static final float EXECUTE_HEALTH_CAP = 80.0F;

    /** 连击窗口与层数上限 / combo window and stack cap */
    private static final long COMBO_WINDOW_MILLIS = 3000L;
    private static final int COMBO_MAX = 6;

    private record Proc(int code, double value, int chance) {}

    private record Combo(UUID target, int stacks, long at) {}

    private static final Map<String, Proc> PROCS = new HashMap<>();
    private static final Map<UUID, Combo> COMBO_STATE = new HashMap<>();

    private DynastyTrinketOnHit() {
    }

    /**
     * 由 {@link DynastyTrinkets} 在建表时调用一次：把每件饰品的命中行抽出来。
     * 之后每次命中只查这张小表，不再遍历整张饰品表。
     */
    public static void index(Object[][] table) {
        PROCS.clear();
        for (Object[] row : table) {
            if (row.length < 14) {
                continue;                       // 老批次的行没有命中列
            }
            int code = (Integer) row[11];
            if (code <= 0) {
                continue;
            }
            PROCS.put((String) row[0], new Proc(code, (Double) row[12], (Integer) row[13]));
        }
    }

    /** 玩家登出时清掉连击状态 / drop combo state on logout */
    public static void forget(Player player) {
        COMBO_STATE.remove(player.getUUID());
    }

    /**
     * 命中前的加伤（会心 / 突袭 / 连击）。
     *
     * @return 加成后的伤害；没有可用饰品时原样返回
     */
    public static float bonus(Player attacker, LivingEntity target, float amount) {
        if (PROCS.isEmpty() || amount <= 0.0F) {
            return amount;
        }
        java.util.Set<String> active = DynastyTrinkets.activeIds(attacker);
        if (active.isEmpty()) {
            return amount;
        }
        long now = System.currentTimeMillis();
        double bonusRatio = 0.0D;
        for (String id : active) {
            Proc proc = PROCS.get(id);
            if (proc == null || proc.code() == LIFESTEAL || proc.code() == EXECUTE
                    || proc.code() == THUNDER) {
                continue;                       // 那三个在结算后用，不在这里加伤
            }
            switch (proc.code()) {
                case CRIT -> {
                    if (roll(attacker, proc.chance())) {
                        bonusRatio += proc.value();
                    }
                }
                case AMBUSH -> {
                    // 突袭：目标还是满血（第一刀）才生效
                    if (target.getHealth() >= target.getMaxHealth() - 0.01F
                            && roll(attacker, proc.chance())) {
                        bonusRatio += proc.value();
                    }
                }
                case COMBO -> {
                    if (roll(attacker, proc.chance())) {
                        bonusRatio += proc.value() * stacks(attacker, target, now);
                    }
                }
                default -> {
                }
            }
        }
        if (bonusRatio <= 0.0D) {
            return amount;
        }
        return amount + (float) (amount * Math.min(2.0D, bonusRatio));
    }

    /**
     * 命中结算后的效果（吸血 / 斩杀 / 雷罚）。
     *
     * @param dealt 本次实际造成的伤害（各段减伤已经算完）
     */
    public static void after(Player attacker, LivingEntity target, float dealt) {
        if (PROCS.isEmpty()) {
            return;
        }
        java.util.Set<String> active = DynastyTrinkets.activeIds(attacker);
        if (active.isEmpty()) {
            return;
        }
        for (String id : active) {
            Proc proc = PROCS.get(id);
            if (proc == null) {
                continue;
            }
            switch (proc.code()) {
                case LIFESTEAL -> {
                    if (dealt > 0.0F && roll(attacker, proc.chance())) {
                        attacker.heal((float) (dealt * proc.value()));
                    }
                }
                case EXECUTE -> {
                    if (target.isAlive() && roll(attacker, proc.chance()) && mayBeExecuted(target)
                            && target.getHealth() <= target.getMaxHealth() * proc.value()) {
                        execute(attacker, target, proc.value());
                    }
                }
                case THUNDER -> {
                    if (target.isAlive() && roll(attacker, proc.chance())) {
                        target.hurt(attacker.damageSources().playerAttack(attacker),
                                (float) proc.value());
                    }
                }
                default -> {
                }
            }
        }
    }

    /**
     * 斩杀：给足伤害（护甲 / 抗性仍会削减，所以给 4 倍血量上限 + 100 保底），并给玩家一句提示。
     * Execute: enough damage to finish a low-health mob, plus a chat hint.
     */
    private static void execute(Player attacker, LivingEntity target, double threshold) {
        target.hurt(attacker.damageSources().playerAttack(attacker),
                (float) (target.getMaxHealth() * 4.0D + 100.0D));
        if (!target.isAlive() && attacker instanceof ServerPlayer server) {
            server.displayClientMessage(Component.literal(
                    "§4[斩杀] §r" + target.getName().getString() + " 在 "
                            + Math.round(threshold * 100) + "% 血线之下被一击了结。"), false);
        }
    }

    /** 斩杀的安全线：玩家、Boss / 神兽、血量上限过高的目标都免斩（免得变成一键清场）。 */
    private static boolean mayBeExecuted(LivingEntity target) {
        if (target instanceof Player) {
            return false;
        }
        if (target.getMaxHealth() > EXECUTE_HEALTH_CAP) {
            return false;
        }
        return !DynastyBalance.isBossOrBeast(target.getType());
    }

    /** 连击层数：3 秒内连续命中同一目标才叠层，换目标或超时都从 1 重新算。 */
    private static int stacks(Player attacker, LivingEntity target, long now) {
        Combo previous = COMBO_STATE.get(attacker.getUUID());
        int next = 1;
        if (previous != null && previous.target().equals(target.getUUID())
                && now - previous.at() <= COMBO_WINDOW_MILLIS) {
            next = Math.min(COMBO_MAX, previous.stacks() + 1);
        }
        COMBO_STATE.put(attacker.getUUID(), new Combo(target.getUUID(), next, now));
        return next;
    }

    /** 概率判定：100 = 必定触发，0 = 永不触发。 */
    private static boolean roll(Player attacker, int chance) {
        if (chance >= 100) {
            return true;
        }
        if (chance <= 0) {
            return false;
        }
        return attacker.getRandom().nextInt(100) < chance;
    }
}
