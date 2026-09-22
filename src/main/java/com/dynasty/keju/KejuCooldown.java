package com.dynasty.keju;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * 档位功名奖励冷却（纯逻辑，时钟由调用方注入，方便测试 30 秒边界）。
 *
 * 冷却只限制「档位功名」这一项；龙威 / 疾风 / 天命三个效果与可书写书**不受冷却限制**
 * —— 本轮不改变这个范围。
 *
 * The 30s merit cooldown. The clock is injected so the boundary can be tested
 * without waiting. It only gates the tier merit, not the effects or the book.
 */
public final class KejuCooldown {

    private final long windowMs;
    private final Map<UUID, Long> lastReward = new HashMap<>();

    public KejuCooldown(long windowMs) {
        this.windowMs = Math.max(0L, windowMs);
    }

    public long windowMs() {
        return windowMs;
    }

    /** 冷却是否已结束（恰好等于窗口即视为结束）。/ true when the merit may be granted again. */
    public synchronized boolean ready(UUID player, long now) {
        Long last = lastReward.get(player);
        return last == null || now - last >= windowMs;
    }

    /** 记录一次功名发放。/ record a merit grant. */
    public synchronized void mark(UUID player, long now) {
        lastReward.put(player, now);
    }

    /** 距离可以再拿功名还有多久（毫秒，0 表示可以）。 */
    public synchronized long remaining(UUID player, long now) {
        Long last = lastReward.get(player);
        if (last == null) {
            return 0L;
        }
        long left = windowMs - (now - last);
        return Math.max(0L, left);
    }

    /**
     * 只清理已过期条目（登出时调用）：仍在冷却期内的记录不会被抹掉，
     * 因此断开重连不能绕过冷却，长时间在线也不会无限积累。
     */
    public synchronized void pruneExpired(long now) {
        lastReward.entrySet().removeIf(entry -> now - entry.getValue() >= windowMs);
    }

    public synchronized int size() {
        return lastReward.size();
    }

    /** 清空（服务器关闭时调用）。/ clear everything, e.g. on server shutdown. */
    public synchronized void clear() {
        lastReward.clear();
    }
}
