package com.dynasty.entity;

/**
 * Boss 血条「该不该给这个玩家看」的**纯判定**（不引用任何 Minecraft 类，可直接单测）。
 *
 * 需求背景：原版实体跟踪范围（叛将 clientTrackingRange = 14 区块 ≈ 224 格）远大于「看得见」，
 * 于是玩家隔着山体、在地下、甚至刚进维度就会被塞一根血条。这里把判定改成：
 *
 * <ul>
 *   <li><b>可见</b>（同维度 + 视线不被挡 + 合理距离）→ 显示；</li>
 *   <li><b>确实交战</b>（Boss 正锁定该玩家 / 双方刚刚互相攻击过）→ 宽限距离内保持，
 *       短暂被遮挡也不闪烁；</li>
 *   <li><b>从没见过又没交战</b>（初次隔着山体 / 地下）→ 一律不显示；</li>
 *   <li>超出距离、跨维度、死亡 / 移除 / 退出由调用方负责摘掉订阅。</li>
 * </ul>
 *
 * Pure per-player visibility decision for boss bars, so it can be unit tested
 * without a running game.
 */
public final class BossBarVisibility {

    private BossBarVisibility() {
    }

    /** 「看得见就算」的距离（格）/ distance within which sight alone shows the bar */
    public static final double SHOW_DISTANCE = 40.0D;

    /** 交战 / 宽限期的距离上限（格）/ keeping distance while engaged or during grace */
    public static final double KEEP_DISTANCE = 48.0D;

    /** 短暂遮挡的宽限（tick）：约 5 秒，避免血条闪烁 / grace while briefly occluded */
    public static final int GRACE_TICKS = 100;

    /** 检查间隔（tick）：不每 tick 扫玩家 / throttled re-evaluation */
    public static final int CHECK_INTERVAL = 10;

    /** 多久没影就彻底忘掉这个玩家（tick，防止表无限增长）/ drop the entry after this idle time */
    public static final int FORGET_TICKS = 600;

    /** 一次「交手」算作交战的时长（tick）/ how long a blow keeps the fight "active" */
    public static final int ENGAGE_TICKS = 160;

    /**
     * 该玩家现在是否应该看到血条。
     *
     * @param distance    与 Boss 的距离（格）
     * @param canSee      同维度且视线没被挡住
     * @param engaged     确实处于交战中（Boss 锁定该玩家，或双方刚互相攻击过）
     * @param sawBefore   该玩家之前真的看见过它（不是「刚进跟踪范围」）
     * @param lastSeenAgo 距离上一次确认可见过了多少 tick
     */
    public static boolean visible(double distance, boolean canSee, boolean engaged,
                                  boolean sawBefore, int lastSeenAgo) {
        if (engaged) {
            return distance <= KEEP_DISTANCE;
        }
        if (canSee) {
            return distance <= SHOW_DISTANCE;
        }
        // 看不见又没在打：只有「之前见过」且还在宽限窗口内才暂时保留，避免遮挡时闪烁
        if (!sawBefore) {
            return false;
        }
        return lastSeenAgo <= GRACE_TICKS && distance <= KEEP_DISTANCE;
    }

    /** 这次判定之后，是否还需要继续关注这个玩家（否则调用方可以忘掉这条记录）。 */
    public static boolean worthKeeping(boolean visibleNow, boolean sawBefore, int idleTicks) {
        return visibleNow || sawBefore || idleTicks <= FORGET_TICKS;
    }

    /** 是否属于「自然生成」（只有自然生成才做严格的落脚点校验）。*/
    public static boolean strictPlacement(boolean naturalSpawn) {
        return naturalSpawn;
    }
}
