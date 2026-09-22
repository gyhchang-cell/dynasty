package com.dynasty.keju;

/**
 * 按「哪个服务器实例」持有科举的临时状态（会话与奖励冷却）。
 *
 * 用身份比较（{@code ==}）而不是数值相等：同进程换了一个服务器实例就等于换了一个
 * 全新的槽位，旧实例的待答会话与冷却不会串到新实例；服务器关闭时把槽位清空。
 * 泛型键不引用任何 Minecraft 类，因此可以脱离游戏单测。
 *
 * Per-server (identity-keyed) holder for the temp state: sessions and cooldown.
 * Keyed by identity so a new server instance never inherits the previous one's
 * sessions, and the slot is reset on shutdown.
 */
public final class KejuServerState<K> {

    private final long cooldownMs;
    private K owner;
    private KejuSessionRegistry sessions;
    private KejuCooldown cooldown;

    public KejuServerState(long cooldownMs) {
        this.cooldownMs = cooldownMs;
        this.sessions = new KejuSessionRegistry();
        this.cooldown = new KejuCooldown(cooldownMs);
    }

    /** 取该服务器的会话表（换了实例就换新表）。/ sessions for this server instance. */
    public synchronized KejuSessionRegistry sessions(K key) {
        bind(key);
        return sessions;
    }

    /** 取该服务器的冷却表。/ cooldown for this server instance. */
    public synchronized KejuCooldown cooldown(K key) {
        bind(key);
        return cooldown;
    }

    /** 当前绑定的服务器实例。/ currently bound server instance. */
    public synchronized K owner() {
        return owner;
    }

    /** 服务器关闭：清空该实例的会话与冷却。/ drop sessions and cooldown of that instance. */
    public synchronized void shutdown(K key) {
        if (key != null && key != owner) {
            return;
        }
        owner = null;
        sessions = new KejuSessionRegistry();
        cooldown = new KejuCooldown(cooldownMs);
    }

    private void bind(K key) {
        if (key == null || key == owner) {
            return;
        }
        owner = key;
        sessions = new KejuSessionRegistry();
        cooldown = new KejuCooldown(cooldownMs);
    }
}
