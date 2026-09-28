package com.dynasty.entity;

import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Mob;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.UUID;

/**
 * 按**玩家逐个**管理的 Boss 血条订阅（MC 胶水层，判定逻辑在 {@link BossBarVisibility}）。
 *
 * 关键点：
 * <ul>
 *   <li>进入实体跟踪范围（{@code startSeenByPlayer}）只**登记候选**，不立刻加血条 ——
 *       跟踪范围有 14 区块，远大于「看得见」；</li>
 *   <li>真正的订阅 / 退订由 {@link #tick()} 按 {@link BossBarVisibility#CHECK_INTERVAL} 错峰判定，
 *       只看**当前跟踪本实体**的玩家，不扫世界、不扫生物；</li>
 *   <li>不使用 {@code ServerBossEvent#setVisible} 这种全局开关，每个玩家各自独立；</li>
 *   <li>离开跟踪 / 换维度 / 退出 / 死亡 / 移除都会立刻摘掉对应玩家的血条。</li>
 * </ul>
 *
 * Per-player boss bar subscriptions; the boss only ever pays for players that
 * actually track it.
 */
public final class DynastyBossBarSubscriptions {

    /** 每个候选玩家的记忆 / per-candidate memory */
    private static final class Memory {
        int lastSeenTick;
        int lastTouchedTick;
        boolean sawBefore;
        boolean shown;
    }

    private final Mob boss;
    private final ServerBossEvent bar;
    private final Map<UUID, Memory> candidates = new HashMap<>();
    private int cooldown;

    public DynastyBossBarSubscriptions(Mob boss, ServerBossEvent bar) {
        this.boss = boss;
        this.bar = bar;
        // 按实体 id 错峰，避免同 tick 里多个 Boss 一起算
        this.cooldown = 1 + Math.floorMod(boss.getId(), BossBarVisibility.CHECK_INTERVAL);
    }

    /** 进入玩家跟踪范围：只登记候选，先不给血条。/ register a candidate only. */
    public void startSeenByPlayer(ServerPlayer player) {
        Memory memory = this.candidates.computeIfAbsent(player.getUUID(), key -> new Memory());
        memory.lastTouchedTick = this.boss.tickCount;
    }

    /** 离开跟踪范围（含退出 / 换维度 / 超出跟踪距离）：立刻摘掉血条。*/
    public void stopSeenByPlayer(ServerPlayer player) {
        this.candidates.remove(player.getUUID());
        this.bar.removePlayer(player);
    }

    /** 每 tick 调用一次；内部自带间隔与错峰，不会每 tick 扫玩家。*/
    public void tick() {
        if (this.boss.level().isClientSide() || this.candidates.isEmpty()) {
            return;
        }
        if (--this.cooldown > 0) {
            return;
        }
        this.cooldown = BossBarVisibility.CHECK_INTERVAL;
        if (!(this.boss.level() instanceof ServerLevel level) || level.getServer() == null) {
            return;
        }
        int now = this.boss.tickCount;
        Iterator<Map.Entry<UUID, Memory>> iterator = this.candidates.entrySet().iterator();
        while (iterator.hasNext()) {
            Map.Entry<UUID, Memory> entry = iterator.next();
            Memory memory = entry.getValue();
            ServerPlayer player = level.getServer().getPlayerList().getPlayer(entry.getKey());
            if (player == null) {
                memory.shown = false;
                if (now - memory.lastTouchedTick > BossBarVisibility.FORGET_TICKS) {
                    iterator.remove();
                }
                continue;
            }
            if (player.level() != level) {
                hide(player, memory);
                iterator.remove();
                continue;
            }
            double distance = this.boss.distanceTo(player);
            boolean canSee = distance <= BossBarVisibility.SHOW_DISTANCE && player.hasLineOfSight(this.boss);
            if (canSee) {
                memory.lastSeenTick = now;
                memory.sawBefore = true;
            }
            boolean visible = BossBarVisibility.visible(distance, canSee, engaged(player, now),
                    memory.sawBefore, now - memory.lastSeenTick);
            apply(player, memory, visible);
            // 候选集合本身就是「正在跟踪本实体」的玩家。仍在跟踪、暂时看不见时
            // 不能忘记候选，否则玩家在同一跟踪范围内靠近后血条永远不会再出现。
            // 离开跟踪由 stopSeenByPlayer 清理，离线玩家由上面的过期分支清理。
            memory.lastTouchedTick = now;
        }
    }

    /** Boss 死亡 / 移除 / 卸载：清干净（不留下任何幽灵血条）。*/
    public void clear() {
        this.candidates.clear();
        this.bar.removeAllPlayers();
    }

    /** 当前真正订阅了血条的玩家数（调试 / 测试用）。*/
    public int shownCount() {
        int shown = 0;
        for (Memory memory : this.candidates.values()) {
            if (memory.shown) {
                shown++;
            }
        }
        return shown;
    }

    /** 是否正在交战：Boss 锁定该玩家，或双方刚刚互相攻击过。*/
    private boolean engaged(ServerPlayer player, int now) {
        if (this.boss.getTarget() == player) {
            return true;
        }
        if (this.boss.getLastHurtByMob() == player
                && now - this.boss.getLastHurtByMobTimestamp() <= BossBarVisibility.ENGAGE_TICKS) {
            return true;
        }
        return this.boss.getLastHurtMob() == player
                && now - this.boss.getLastHurtMobTimestamp() <= BossBarVisibility.ENGAGE_TICKS;
    }

    private void apply(ServerPlayer player, Memory memory, boolean visible) {
        if (visible == memory.shown) {
            return;
        }
        memory.shown = visible;
        if (visible) {
            memory.lastTouchedTick = this.boss.tickCount;
            this.bar.addPlayer(player);
        } else {
            this.bar.removePlayer(player);
        }
    }

    private void hide(ServerPlayer player, Memory memory) {
        if (memory.shown) {
            memory.shown = false;
            this.bar.removePlayer(player);
        }
        memory.lastTouchedTick = this.boss.tickCount;
    }
}
