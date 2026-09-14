package com.dynasty.entity;

import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitlesAnimationPacket;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.TickTask;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.BossEvent;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.List;

/**
 * Boss 机制工具箱（第二轮：把「站着互砍」变成「看懂机制再打」）。
 *
 * 提供四套通用机制，任何 Boss / 神兽只要在 {@code customServerAiStep} 里调一行就能用：
 *
 *   ① 阶段播报 announce —— 换 Boss 条颜色 + 全屏标题 + 低吼粒子，让玩家知道「进二阶段了」。
 *   ② 破防护盾 shield / hitShield / breakShield / syncBar ——
 *      Boss 举起护盾（减伤 70%）并叠抗性，玩家必须**打满 N 下**才能破盾；
 *      破盾后进入**破绽**窗口（受伤 ×2.5），这就是「集火」的时机。
 *   ③ 可躲的场地大招 telegraphedArea —— 先画预警圈 + 低吼，1 秒后才结算伤害，
 *      玩家跑出圈就能躲掉（延迟任务走服务端主线程 TickTask，不用自己写计时器）。
 *   ④ 吸兵回血 drainMinions / 落地冲击波 shockwave —— 让「清小怪」「别站正面」有意义。
 *
 * ⚠ NBT 状态放在 persistentData 上，存档读档后依旧生效；
 *   所有取属性都走 {@link com.dynasty.DynastyAttributes}，属性缺了也不会崩服。
 *
 * Shared boss mechanics: phase call-outs, breakable shields with a burst window,
 * dodgeable telegraphed ground attacks, minion drain and shockwaves.
 */
@SuppressWarnings("null")
public final class DynastyBossMechanics {

    private DynastyBossMechanics() {
    }

    // ---- 状态键（存在 persistentData 上，读档不丢）/ NBT state keys ----
    private static final String SHIELD_END = "dynasty_shield_end";
    private static final String SHIELD_HITS = "dynasty_shield_hits";
    private static final String SHIELD_NEED = "dynasty_shield_need";
    private static final String SHIELD_CUT = "dynasty_shield_cut";
    private static final String WEAK_END = "dynasty_weak_end";
    private static final String WEAK_MUL = "dynasty_weak_mul";

    private static long clock(LivingEntity entity) {
        return entity.level().getGameTime();
    }

    // ---------------------------------------------------------------- ① 阶段播报
    /** 全屏标题 + 换 Boss 条颜色 + 低吼 / phase call-out with title and boss-bar colour */
    public static void announce(Mob boss, ServerBossEvent bar, BossEvent.BossBarColor color,
                                String title, String subtitle, SoundEvent sound) {
        if (bar != null && color != null) {
            bar.setColor(color);
        }
        for (ServerPlayer player : nearbyPlayers(boss, 64.0D)) {
            player.connection.send(new ClientboundSetTitlesAnimationPacket(5, 35, 10));
            player.connection.send(new ClientboundSetSubtitleTextPacket(
                    Component.literal("§7" + subtitle)));
            player.connection.send(new ClientboundSetTitleTextPacket(Component.literal(title)));
        }
        boss.playSound(sound == null ? SoundEvents.WITHER_SPAWN : sound, 2.2F, 0.7F);
        particles(boss.level(), boss, ParticleTypes.SOUL_FIRE_FLAME, 30, 1.4D);
    }

    // ---------------------------------------------------------------- ② 破防护盾
    /**
     * 起盾：减伤 cut（0~1），需要被打满 hits 下才破。
     * 破盾判定在 {@link com.dynasty.DynastyBossCombat} 的 LivingHurtEvent 里做。
     */
    public static void shield(Mob boss, ServerBossEvent bar, int ticks, int hits, double cut) {
        CompoundTag tag = boss.getPersistentData();
        tag.putLong(SHIELD_END, clock(boss) + Math.max(20, ticks));
        tag.putInt(SHIELD_HITS, 0);
        tag.putInt(SHIELD_NEED, Math.max(1, hits));
        tag.putDouble(SHIELD_CUT, Math.min(0.95D, Math.max(0.0D, cut)));
        boss.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, ticks, 2, false, false));
        if (bar != null) {
            bar.setColor(BossEvent.BossBarColor.PURPLE);
        }
        particles(boss.level(), boss, ParticleTypes.ENCHANT, 60, 1.8D);
        boss.playSound(SoundEvents.SHIELD_BLOCK, 2.0F, 0.6F);
    }

    /** 现在是否处于护盾状态 / shield currently up */
    public static boolean shielded(LivingEntity boss) {
        CompoundTag tag = boss.getPersistentData();
        return tag.getInt(SHIELD_NEED) > 0 && clock(boss) < tag.getLong(SHIELD_END);
    }

    /** 护盾减伤比例 / shield damage cut */
    public static double shieldCut(LivingEntity boss) {
        return Math.min(0.95D, Math.max(0.0D, boss.getPersistentData().getDouble(SHIELD_CUT)));
    }

    /** 护盾还差几下破 / remaining hits to break the shield */
    public static int shieldLeft(LivingEntity boss) {
        CompoundTag tag = boss.getPersistentData();
        return Math.max(0, tag.getInt(SHIELD_NEED) - tag.getInt(SHIELD_HITS));
    }

    /** 命中护盾记一次数；返回 true 表示这次打破了 / count a hit, true when it breaks */
    public static boolean hitShield(LivingEntity boss) {
        CompoundTag tag = boss.getPersistentData();
        int hit = tag.getInt(SHIELD_HITS) + 1;
        tag.putInt(SHIELD_HITS, hit);
        return hit >= tag.getInt(SHIELD_NEED);
    }

    /** 破盾：清状态 + 开破绽 + 播报 / shield breaks into a burst window */
    public static void breakShield(Mob boss, ServerBossEvent bar, int weakTicks, double multiplier) {
        CompoundTag tag = boss.getPersistentData();
        tag.putInt(SHIELD_NEED, 0);
        tag.putLong(SHIELD_END, 0L);
        boss.removeEffect(MobEffects.DAMAGE_RESISTANCE);
        weakPoint(boss, bar, weakTicks, multiplier);
        announce(boss, bar, BossEvent.BossBarColor.WHITE, "§f破　防",
                "护盾碎裂：破绽期间伤害 ×" + trim(multiplier), SoundEvents.WITHER_BREAK_BLOCK);
    }

    /** 破绽窗口：这段时间里受到的伤害 ×multiplier / vulnerability window */
    public static void weakPoint(Mob boss, ServerBossEvent bar, int ticks, double multiplier) {
        CompoundTag tag = boss.getPersistentData();
        tag.putLong(WEAK_END, clock(boss) + Math.max(20, ticks));
        tag.putDouble(WEAK_MUL, Math.max(1.0D, multiplier));
        boss.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, ticks, 1, false, false));
        if (bar != null) {
            bar.setColor(BossEvent.BossBarColor.WHITE);
        }
        particles(boss.level(), boss, ParticleTypes.CRIT, 50, 1.6D);
    }

    public static boolean weak(LivingEntity boss) {
        return clock(boss) < boss.getPersistentData().getLong(WEAK_END);
    }

    public static double weakMultiplier(LivingEntity boss) {
        return Math.max(1.0D, boss.getPersistentData().getDouble(WEAK_MUL));
    }

    /** Boss 条配色跟着机制走（护盾紫 / 破绽白 / 平时本色）/ keep the bar colour in sync */
    public static void syncBar(LivingEntity boss, ServerBossEvent bar, BossEvent.BossBarColor normal) {
        if (bar == null) {
            return;
        }
        if (shielded(boss)) {
            bar.setColor(BossEvent.BossBarColor.PURPLE);
        } else if (weak(boss)) {
            bar.setColor(BossEvent.BossBarColor.WHITE);
        } else if (normal != null && bar.getColor() != normal) {
            bar.setColor(normal);
        }
    }

    // ---------------------------------------------------------------- ③ 可躲的场地大招
    /**
     * 预警 + 延迟结算的圆形攻击：玩家在 delay 刻内跑出半径就躲掉了。
     * A telegraphed circle: leave the radius within {@code delay} ticks to dodge it.
     */
    public static void telegraphedArea(Mob boss, double radius, int delay, float damage,
                                       MobEffectInstance effect, ParticleOptions particle) {
        if (!(boss.level() instanceof ServerLevel level)) {
            return;
        }
        Vec3 center = boss.position();
        level.sendParticles(particle == null ? ParticleTypes.CRIT : particle,
                center.x, center.y + 0.3D, center.z, 140, radius * 0.5D, 0.35D, radius * 0.5D, 0.02D);
        boss.playSound(SoundEvents.RAVAGER_ROAR, 2.4F, 0.6F);
        delay(level, delay, () -> {
            if (!boss.isAlive()) {
                return;
            }
            AABB box = new AABB(center, center).inflate(radius, 3.5D, radius);
            List<Player> hit = level.getEntitiesOfClass(Player.class, box);
            for (Player player : hit) {
                player.hurt(boss.damageSources().mobAttack(boss), damage);
                if (effect != null) {
                    player.addEffect(new MobEffectInstance(effect));
                }
            }
            level.sendParticles(ParticleTypes.EXPLOSION_EMITTER,
                    center.x, center.y + 0.4D, center.z, 1, 0.0D, 0.0D, 0.0D, 0.0D);
            if (!hit.isEmpty()) {
                level.sendParticles(ParticleTypes.LAVA, center.x, center.y + 0.6D, center.z,
                        40, radius * 0.4D, 0.4D, radius * 0.4D, 0.0D);
            }
        });
    }

    /** 在服务端主线程排队一个延迟动作（不用自己写计时器）/ schedule on the server thread */
    public static void delay(ServerLevel level, int ticks, Runnable action) {
        MinecraftServer server = level.getServer();
        if (server == null) {
            return;
        }
        server.tell(new TickTask(server.getTickCount() + Math.max(0, ticks), action));
    }

    // ---------------------------------------------------------------- ④ 吸兵回血 / 冲击波
    /** 抽干附近小弟给自己回血：每只回 healPer，最多 max 只 / drain minions to heal */
    public static void drainMinions(Mob boss, double radius, float healPer, int max) {
        List<Mob> minions = boss.level().getEntitiesOfClass(Mob.class,
                boss.getBoundingBox().inflate(radius),
                mob -> mob != boss && mob.isAlive() && isAlly(mob));
        int drained = 0;
        for (Mob minion : minions) {
            if (drained >= max) {
                break;
            }
            minion.hurt(boss.damageSources().magic(), minion.getMaxHealth());
            drained++;
        }
        if (drained > 0) {
            boss.heal(healPer * drained);
            particles(boss.level(), boss, ParticleTypes.HEART, 8 * drained, 1.0D);
            boss.playSound(SoundEvents.WITHER_AMBIENT, 1.6F, 1.2F);
        }
    }

    /** 落地冲击波：把半径内的玩家击退 + 伤害 / shockwave on landing */
    public static void shockwave(Mob boss, double radius, float damage) {
        for (Player player : boss.level().getEntitiesOfClass(Player.class,
                boss.getBoundingBox().inflate(radius))) {
            player.hurt(boss.damageSources().mobAttack(boss), damage);
            Vec3 push = new Vec3(player.getX() - boss.getX(), 0.0D, player.getZ() - boss.getZ());
            if (push.lengthSqr() > 1.0E-3D) {
                push = push.normalize().scale(0.9D);
                player.push(push.x, 0.45D, push.z);
                player.hurtMarked = true;
            }
        }
        particles(boss.level(), boss, ParticleTypes.EXPLOSION, 12, radius * 0.5D);
        boss.playSound(SoundEvents.GENERIC_EXPLODE, 2.0F, 0.8F);
    }

    // ---------------------------------------------------------------- 小工具
    public static List<ServerPlayer> nearbyPlayers(Mob boss, double radius) {
        return boss.level().getEntitiesOfClass(ServerPlayer.class,
                boss.getBoundingBox().inflate(radius));
    }

    private static void particles(Level level, LivingEntity entity, ParticleOptions particle,
                                  int count, double spread) {
        if (level instanceof ServerLevel server) {
            server.sendParticles(particle, entity.getX(), entity.getY() + 1.0D, entity.getZ(),
                    count, spread, spread * 0.6D, spread, 0.02D);
        }
    }

    private static boolean isAlly(Mob mob) {
        var id = net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getKey(mob.getType());
        return id != null && id.getNamespace().equals(com.dynasty.Dynasty.MODID);
    }

    private static String trim(double value) {
        return value == Math.floor(value) ? String.valueOf((int) value) : String.valueOf(value);
    }
}
