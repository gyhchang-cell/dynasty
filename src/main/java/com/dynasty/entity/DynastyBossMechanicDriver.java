package com.dynasty.entity;

import com.dynasty.Dynasty;
import com.dynasty.DynastyBossCombat;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.BossEvent;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Boss 机制的「总调度」：一张表描述每个 Boss 的阶段与招式，实体本身不用改一行 AI。
 *
 * 每个 Boss 表里写清楚：
 *   * phases：血量到某个比例时进入什么阶段 —— 播报标题 + 起护盾（要打满几刀破防、破绽倍率）
 *   * hazardEvery / hazardDelay：每隔多久来一次「预警圈」大招，多少刻后结算（玩家可以躲）
 *   * drainEvery：每隔多久抽干附近小弟给自己回血（逼玩家先清小怪）
 *
 * 状态（当前阶段 / 冷却）都存在实体的 persistentData 上，所以读档后接着打、不会重置。
 * 这样「Boss 机制」就成了可配置内容，而不是散落在每个实体里的硬编码。
 *
 * A single table-driven driver: phases (call-out + breakable shield + burst window),
 * dodgeable telegraphed hazards and minion drain, for every boss/beast of the mod.
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class DynastyBossMechanicDriver {

    private DynastyBossMechanicDriver() {
    }

    private static final String PHASE = "dynasty_boss_phase";
    private static final String HAZARD = "dynasty_boss_hazard_cd";
    private static final String DRAIN = "dynasty_boss_drain_cd";

    /** 一个阶段：血量比例 → 播报 + 护盾（hits = 0 表示不起盾） */
    private record Phase(float ratio, int shieldTicks, int shieldHits, double shieldCut,
                         double weakMultiplier, String title, String hint) {
    }

    /** 一个 Boss 的整套机制 */
    private record Mechanics(List<Phase> phases, int hazardEvery, int hazardDelay, float hazardFactor,
                             MobEffectInstance hazardEffect, ParticleOptions particle,
                             int drainEvery, float drainHeal, int drainMax,
                             BossEvent.BossBarColor color) {
    }

    private static final Mechanics NONE =
            new Mechanics(List.of(), 0, 0, 0.0F, null, null, 0, 0.0F, 0, null);

    private static final Map<String, Mechanics> TABLE = new HashMap<>();
    private static final Map<EntityType<?>, Mechanics> CACHE = new ConcurrentHashMap<>();

    private static Phase phase(float ratio, int ticks, int hits, double cut, double weak,
                               String title, String hint) {
        return new Phase(ratio, ticks, hits, cut, weak, title, hint);
    }

    static {
        // ---------- 天朝·龙庭：龙帝 ----------
        TABLE.put("dragon_emperor", new Mechanics(List.of(
                phase(0.70F, 280, 12, 0.70D, 2.5D, "§c龙帝 · 二阶段　龙鳞护体",
                        "打满 12 下破防 · 破绽期伤害 ×2.5"),
                phase(0.35F, 240, 10, 0.65D, 3.0D, "§4龙帝 · 终阶段　焚天怒火",
                        "预警圈内必闪 · 抽禁军回血")),
                200, 24, 0.55F, new MobEffectInstance(MobEffects.WEAKNESS, 140),
                ParticleTypes.FLAME, 300, 40.0F, 6, BossEvent.BossBarColor.RED));

        // ---------- 地府：不死始皇 ----------
        TABLE.put("undead_first_emperor", new Mechanics(List.of(
                phase(0.66F, 240, 10, 0.65D, 2.5D, "§5始皇 · 俑阵",
                        "俑军护驾：打满 10 下破防"),
                phase(0.33F, 200, 8, 0.60D, 3.0D, "§5始皇 · 暴走",
                        "凋零领域：别站原地 · 吸取俑军回血")),
                220, 26, 0.60F, new MobEffectInstance(MobEffects.WITHER, 160),
                ParticleTypes.SOUL, 260, 50.0F, 8, BossEvent.BossBarColor.PURPLE));

        // ---------- 九霄：天将 ----------
        TABLE.put("nine_heaven_general", new Mechanics(List.of(
                phase(0.60F, 260, 12, 0.70D, 2.5D, "§b天将 · 云盾成形",
                        "打满 12 下破防 · 破绽期伤害 ×2.5"),
                phase(0.30F, 220, 10, 0.65D, 3.0D, "§3天将 · 九天雷狱",
                        "雷狱预警：离开落雷圈")),
                180, 22, 0.70F, new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 1),
                ParticleTypes.ELECTRIC_SPARK, 320, 45.0F, 6, BossEvent.BossBarColor.BLUE));

        // ---------- 东海龙宫：龙王 ----------
        TABLE.put("dragon_king", new Mechanics(List.of(
                phase(0.60F, 280, 12, 0.70D, 2.5D, "§b龙王 · 龙鳞护体",
                        "打满 12 下破防 · 破绽期伤害 ×2.5"),
                phase(0.30F, 220, 10, 0.65D, 3.0D, "§9龙王 · 怒涛",
                        "海啸预警：离开圈子 · 抽虾兵回血")),
                200, 26, 0.65F, new MobEffectInstance(MobEffects.LEVITATION, 60),
                ParticleTypes.BUBBLE_POP, 300, 50.0F, 8, BossEvent.BossBarColor.BLUE));

        // ---------- 叛将 ----------
        TABLE.put("rebel_general", new Mechanics(List.of(
                phase(0.33F, 200, 10, 0.60D, 2.5D, "§c叛将 · 死战",
                        "负隅顽抗：打满 10 下破防 · 破绽期伤害 ×2.5")),
                260, 20, 0.60F, new MobEffectInstance(MobEffects.WEAKNESS, 120),
                ParticleTypes.CRIT, 400, 40.0F, 4, BossEvent.BossBarColor.RED));

        // ---------- 宦官首脑 ----------
        TABLE.put("eunuch_mastermind", new Mechanics(List.of(
                phase(0.25F, 180, 8, 0.55D, 2.5D, "§5宦官 · 阴毒罩体",
                        "打满 8 下破防 · 破绽期伤害 ×2.5")),
                240, 20, 0.55F, new MobEffectInstance(MobEffects.POISON, 140),
                ParticleTypes.WITCH, 360, 35.0F, 4, BossEvent.BossBarColor.PURPLE));

        // ---------- 神兽 ----------
        TABLE.put("phoenix", new Mechanics(List.of(
                phase(0.50F, 160, 8, 0.60D, 2.5D, "§6凤凰 · 涅槃火羽",
                        "打满 8 下破防 · 破绽期伤害 ×2.5")),
                200, 22, 0.50F, new MobEffectInstance(MobEffects.WEAKNESS, 120),
                ParticleTypes.FLAME, 0, 0.0F, 0, BossEvent.BossBarColor.YELLOW));
        TABLE.put("nian_beast", new Mechanics(List.of(
                phase(0.50F, 160, 8, 0.60D, 2.5D, "§c年兽 · 暴怒",
                        "打满 8 下破防 · 破绽期伤害 ×2.5")),
                220, 20, 0.55F, new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100),
                ParticleTypes.LARGE_SMOKE, 0, 0.0F, 0, BossEvent.BossBarColor.RED));
        TABLE.put("nine_tailed_fox", new Mechanics(List.of(
                phase(0.50F, 160, 8, 0.60D, 2.5D, "§d九尾 · 幻影",
                        "打满 8 下破防 · 破绽期伤害 ×2.5")),
                240, 24, 0.50F, new MobEffectInstance(MobEffects.BLINDNESS, 60),
                ParticleTypes.SQUID_INK, 0, 0.0F, 0, BossEvent.BossBarColor.PINK));
    }

    // ---------------------------------------------------------------- 调度
    @SubscribeEvent
    public static void onLivingTick(LivingEvent.LivingTickEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || mob.level().isClientSide()) {
            return;
        }
        Mechanics mechanics = mechanicsOf(mob.getType());
        if (mechanics == NONE) {
            return;
        }
        CompoundTag tag = mob.getPersistentData();
        float ratio = mob.getMaxHealth() <= 0.0F ? 1.0F : mob.getHealth() / mob.getMaxHealth();

        // ① 阶段：血量跌破阈值就播报 + 起盾
        int phase = tag.getInt(PHASE);
        List<Phase> phases = mechanics.phases();
        while (phase < phases.size() && ratio <= phases.get(phase).ratio()) {
            tag.putInt(PHASE, phase + 1);
            enterPhase(mob, mechanics, phases.get(phase));
            phase++;
        }

        // ② 场地大招：先预警后结算，玩家跑出圈子就能躲
        if (mechanics.hazardEvery() > 0 && mob.getTarget() != null) {
            int cooldown = tag.getInt(HAZARD);
            if (cooldown <= 0) {
                tag.putInt(HAZARD, mechanics.hazardEvery());
                DynastyBossMechanics.telegraphedArea(mob, 6.0D, mechanics.hazardDelay(),
                        DynastyBossAI.damage(mob, mechanics.hazardFactor()),
                        mechanics.hazardEffect(), mechanics.particle());
            } else {
                tag.putInt(HAZARD, cooldown - 1);
            }
        }

        // ③ 吸兵回血：身边小弟越多回得越快（所以要先清小怪）
        if (mechanics.drainEvery() > 0) {
            int cooldown = tag.getInt(DRAIN);
            if (cooldown <= 0) {
                tag.putInt(DRAIN, mechanics.drainEvery());
                if (mob.getHealth() < mob.getMaxHealth() * 0.9F) {
                    DynastyBossMechanics.drainMinions(mob, 20.0D,
                            mechanics.drainHeal(), mechanics.drainMax());
                }
            } else {
                tag.putInt(DRAIN, cooldown - 1);
            }
        }

        // ④ Boss 条配色：护盾紫 / 破绽白 / 平时本色
        if (mob instanceof DynastyBossCombat.BarHolder holder) {
            DynastyBossMechanics.syncBar(mob, holder.dynastyBossBar(), mechanics.color());
        }
    }

    /** 进入新阶段：播报 + 起盾 + 冲击波（给「变强了」的手感） */
    private static void enterPhase(Mob mob, Mechanics mechanics, Phase phase) {
        var bar = mob instanceof DynastyBossCombat.BarHolder holder ? holder.dynastyBossBar() : null;
        DynastyBossMechanics.announce(mob, bar, mechanics.color(), phase.title(), phase.hint(),
                SoundEvents.WITHER_SPAWN);
        if (phase.shieldHits() > 0) {
            DynastyBossMechanics.shield(mob, bar, phase.shieldTicks(), phase.shieldHits(),
                    phase.shieldCut());
        }
        DynastyBossMechanics.shockwave(mob, 5.0D, DynastyBossAI.damage(mob, 0.35F));
    }

    /** 按实体类型查表（带缓存：不必每只怪每 tick 查注册表） */
    private static Mechanics mechanicsOf(EntityType<?> type) {
        return CACHE.computeIfAbsent(type, key -> {
            ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(key);
            if (id == null || !id.getNamespace().equals(Dynasty.MODID)) {
                return NONE;
            }
            return TABLE.getOrDefault(id.getPath(), NONE);
        });
    }
}
