package com.dynasty;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingEntityUseItemEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * 伤势系统（第三十四轮新增）：把「代价型饰品 + 内伤」从一次性效果变成**长期账**。
 *
 * 玩法：
 * <ol>
 *   <li><b>怎么来的</b>：单次受到的伤害超过最大生命的 15% 就会累积伤势（按伤害比例，单次最多 +12）；
 *       死亡额外 +25。伤势 0~100。</li>
 *   <li><b>有什么后果</b>：每 10 点伤势扣 3% 生命上限（最多 −30%）；到 34 / 67 点会挂上
 *       **模组自有效果「内伤」I / II**（所以「代价型饰品」会和伤势叠在一起，越打越虚）。</li>
 *   <li><b>怎么好</b>：喝王朝丹药（`dynasty_potion` / 喷溅版）一次 −40；睡一觉 −40；
 *       其余时间每 10 秒自然恢复 1 点（前提是这 10 秒没再挨重击）。</li>
 * </ol>
 *
 * 和饰品一样每秒刷新，属性用固定 UUID 的修饰符（换存档不丢、重复刷新不叠加）。
 * 玩法可见性：跨过 25 / 50 / 75 会提示一次，血量上限与内伤图标本身就是反馈。
 *
 * Long-term injury: heavy hits and deaths add injury points (0-100). Injury lowers max health
 * by 3% per 10 points (capped at -30%) and applies the mod's own Internal Injury effect from
 * 34 points up. Treat with the mod's potions, sleeping, or slow natural recovery.
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class DynastyInjury {

    public static final int MAX = 100;
    private static final String KEY = "dynasty_injury";
    private static final String LAST_HIT = "dynasty_injury_hit";

    /** 单次伤害超过最大生命这个比例才算「重击」 */
    private static final float HEAVY_HIT = 0.15F;
    /** 每 10 点伤势扣 3% 生命上限 */
    private static final double HEALTH_PER_TEN = 0.03D;
    /** 丹药 / 睡觉 / 自然恢复量 */
    private static final int POTION_CURE = 40;
    private static final int SLEEP_CURE = 40;
    private static final long NATURAL_EVERY_TICKS = 200L;

    private static final UUID HEALTH_ID =
            UUID.nameUUIDFromBytes("dynasty_injury_health".getBytes());

    /** 上一帧是否在睡觉（用来判断「睡醒了」）*/
    private static final Map<UUID, Boolean> SLEEPING = new HashMap<>();

    private DynastyInjury() {
    }

    /** 当前伤势 / current injury points */
    public static int of(Player player) {
        return Math.max(0, Math.min(MAX, player.getPersistentData().getInt(KEY)));
    }

    private static void set(Player player, int value) {
        int before = of(player);
        int now = Math.max(0, Math.min(MAX, value));
        player.getPersistentData().putInt(KEY, now);
        hint(player, before, now);
    }

    /** 挨打：重击就累积伤势 / heavy hits add injury */
    public static void onHurt(Player player, float damage) {
        float max = (float) player.getMaxHealth();
        if (max <= 0.0F || damage < max * HEAVY_HIT) {
            return;
        }
        int added = (int) Math.min(12.0F, damage / max * 40.0F);
        if (added > 0) {
            set(player, of(player) + added);
        }
        player.getPersistentData().putLong(LAST_HIT, player.level().getGameTime());
    }

    /** 死亡：重伤一次 / dying adds a big chunk */
    public static void onDeath(Player player) {
        set(player, of(player) + 25);
    }

    /** 治疗（丹药 / 睡觉）/ treat the injury */
    public static void treat(Player player, int amount, String reason) {
        int before = of(player);
        if (before <= 0) {
            return;
        }
        set(player, before - amount);
        if (player instanceof ServerPlayer server) {
            server.displayClientMessage(Component.literal(
                    "§a[伤势] §r" + reason + "，伤势 " + before + " → " + of(player) + "。"), true);
        }
    }

    /** 每秒刷新：属性惩罚 + 内伤效果 + 自然恢复 + 睡觉治疗。 */
    public static void tick(ServerPlayer player) {
        int injury = of(player);

        // 属性：每 10 点扣 3% 生命上限（最多 −30%）
        AttributeInstance health = player.getAttribute(Attributes.MAX_HEALTH);
        if (health != null) {
            health.removeModifier(HEALTH_ID);
            double penalty = Math.min(0.30D, injury / 10.0D * HEALTH_PER_TEN);
            if (penalty > 0.0D) {
                health.addTransientModifier(new AttributeModifier(HEALTH_ID,
                        "dynasty_injury", -penalty, AttributeModifier.Operation.MULTIPLY_TOTAL));
            }
        }

        // 内伤：34 点起 I，67 点起 II（模组自有效果，不是原版 buff）
        int level = injury >= 67 ? 1 : (injury >= 34 ? 0 : -1);
        if (level >= 0) {
            player.addEffect(new net.minecraft.world.effect.MobEffectInstance(
                    DynastyEffects.INTERNAL_INJURY.get(), 60, level, true, false));
        }

        // 睡觉：醒来时按「睡够没」回一次
        boolean sleeping = player.isSleeping();
        Boolean was = SLEEPING.put(player.getUUID(), sleeping);
        if (Boolean.TRUE.equals(was) && !sleeping) {
            treat(player, SLEEP_CURE, "睡了一觉，气血通畅");
        }

        // 自然恢复：每 10 秒 1 点，且这 10 秒内没再挨重击
        if (injury > 0 && player.tickCount % NATURAL_EVERY_TICKS == 0
                && player.level().getGameTime() - player.getPersistentData().getLong(LAST_HIT)
                >= NATURAL_EVERY_TICKS) {
            set(player, injury - 1);
        }
    }

    /** 跨过 25 / 50 / 75 时提醒一次 / warn when crossing a threshold */
    private static void hint(Player player, int before, int now) {
        if (!(player instanceof ServerPlayer server)) {
            return;
        }
        for (int line : new int[]{25, 50, 75}) {
            if (before < line && now >= line) {
                server.displayClientMessage(Component.literal(
                        "§c[伤势] §r已达 " + now + "（生命上限 −" + Math.round(
                                Math.min(30, now / 10 * 3)) + "%）：喝王朝丹药或睡一觉，"
                                + "伤势到 34 / 67 会挂上【内伤】。"), false);
                return;
            }
        }
    }

    // ---------------------------------------------------------------- 事件接线

    /** 每 20 tick 刷新一次（与饰品同频）/ refresh once per second */
    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END
                || !(event.player instanceof ServerPlayer server)
                || server.tickCount % 20 != 0) {
            return;
        }
        tick(server);
    }

    /** 喝下王朝丹药（含喷溅版）就治疗 / the mod's potions cure injury */
    @SubscribeEvent
    public static void onUseFinished(LivingEntityUseItemEvent.Finish event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        String id = DynastyTrinkets.idOf(event.getItem());
        if (id != null && id.contains("potion")) {
            treat(player, POTION_CURE, "服下丹药");
        }
    }

    /** 死亡额外累计 / dying hurts */
    @SubscribeEvent
    public static void onDeath(LivingDeathEvent event) {
        if (event.getEntity() instanceof Player player) {
            onDeath(player);
        }
    }
}
