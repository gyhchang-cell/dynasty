package com.dynasty;

import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 按「世界推进顺序」加强怪物：越晚去的维度，怪越强。
 *
 * 档位（主线顺序）：主世界 1.0 → 天朝·龙庭 1.8 → 地府 2.4 → 九霄天界 3.0 → 东海龙宫 3.6
 *   * 最大生命 × 档位
 *   * 攻击力 ×(1 + 0.45 × (档位 - 1))
 *   * 再乘一个「官阶系数」：(1 + 0.04 × 官阶)，玩家越强怪也跟着涨（最多 +80%）
 *
 * 只加一次（用固定 UUID，重复进区块不会叠加）。
 * 玩家的受伤上限由 DynastyBalance.playerDamageCapFactor 继续兜底，不会一击秒杀。
 *
 * ⚠ 属性必须走 {@link DynastyAttributes}（安全访问）：原版对没有该属性的实体读值会抛异常。
 *   「进天朝 / 地府崩服」的老 bug 就是这里踩到的：区块里只要有一个**盔甲架**
 *   （`LivingEntity.createLivingAttributes()` 里没有攻击力），读攻击力就会
 *   IllegalArgumentException → 服务端主线程直接崩。现在读不到就跳过这件装备。
 *
 * Mobs get stronger the later the dimension appears in the progression order.
 * Attribute reads always go through {@link DynastyAttributes} so a mob without
 * ATTACK_DAMAGE (e.g. an armour stand) can never crash the server thread again.
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class DynastyDimensionDifficulty {

    private DynastyDimensionDifficulty() {
    }

    /** 已经提示过的实体类型（避免刷屏）/ entity ids we already logged about */
    private static final Set<String> SKIPPED = ConcurrentHashMap.newKeySet();

    private static final UUID HEALTH_ID = UUID.fromString("d1a5c0de-0000-4000-8000-00000000d101");
    private static final UUID ATTACK_ID = UUID.fromString("d1a5c0de-0000-4000-8000-00000000d102");
    private static final String HEALTH_NAME = "dynasty_dimension_health";
    private static final String ATTACK_NAME = "dynasty_dimension_attack";

    /** 维度档位 / dimension tier（越晚去的世界越高） */
    public static double tier(ResourceKey<Level> dimension) {
        if (dimension == Level.OVERWORLD) {
            return 1.0D;
        }
        if (dimension == com.dynasty.block.DynastyPortalBlock.CELESTIAL_DYNASTY) {
            return 1.8D;
        }
        if (dimension == com.dynasty.block.DynastyPortalBlock.UNDERWORLD) {
            return 2.4D;
        }
        if (dimension == com.dynasty.block.DynastyPortalBlock.JIUXIAO) {
            return 3.0D;
        }
        if (dimension == com.dynasty.block.DynastyPortalBlock.DRAGON_PALACE) {
            return 3.6D;
        }
        return 1.0D;
    }

    @SubscribeEvent
    public static void onJoin(EntityJoinLevelEvent event) {
        if (event.getLevel().isClientSide() || !(event.getEntity() instanceof Mob mob)) {
            return;
        }
        // 双保险：任何怪（包括别的模组的怪 / 盔甲架这种特殊实体）属性表再怪，
        // 也只跳过这一只，绝不让服务端主线程崩掉。
        // Never let one weird mob crash the whole server thread.
        try {
            applyDifficulty(mob);
        } catch (Throwable throwable) {
            reportOnce(mob, throwable);
        }
    }

    private static void applyDifficulty(Mob mob) {
        double tier = tier(mob.level().dimension());
        double rank = rankFactor(mob);
        if (tier <= 1.0D && rank <= 1.0D) {
            return;
        }
        double healthFactor = tier * rank;
        double attackFactor = (1.0D + 0.45D * (tier - 1.0D)) * rank;
        boolean changed = false;

        // 最大生命 ×档位×官阶（取不到生命属性的实体直接跳过）
        AttributeInstance health = DynastyAttributes.instance(mob, Attributes.MAX_HEALTH);
        if (health == null) {
            reportOnce(mob, null);
            return;
        }
        changed |= add(health, HEALTH_ID, HEALTH_NAME, health.getValue() * (healthFactor - 1.0D));

        // 攻击力：没有攻击力属性的怪（盔甲架 / 纯展示实体）就只加血，不报错
        AttributeInstance attack = DynastyAttributes.instance(mob, Attributes.ATTACK_DAMAGE);
        if (attack != null && attack.getBaseValue() > 0.0D) {
            changed |= add(attack, ATTACK_ID, ATTACK_NAME,
                    attack.getBaseValue() * (attackFactor - 1.0D));
        }
        if (changed && health.getValue() > 0.0D && mob.getHealth() < mob.getMaxHealth()) {
            mob.setHealth(mob.getMaxHealth());          // 血量上限涨了就补满
        }
    }

    /** 同一种实体只提示一次，免得刷屏 / log once per entity type */
    private static void reportOnce(Mob mob, Throwable throwable) {
        var id = ForgeRegistries.ENTITY_TYPES.getKey(mob.getType());
        String key = id == null ? mob.getType().toString() : id.toString();
        if (!SKIPPED.add(key)) {
            return;
        }
        if (throwable == null) {
            Dynasty.LOGGER.info("[Dynasty] 维度难度：{} 没有攻击力属性，只按生命加成处理", key);
        } else {
            Dynasty.LOGGER.warn("[Dynasty] 维度难度：{} 属性异常，已跳过（{}）", key, throwable.toString());
        }
    }

    /** 官阶系数：附近玩家的官阶越高，怪越强 / nearby player's rank makes mobs tougher */
    private static double rankFactor(Mob mob) {
        Player player = mob.level().getNearestPlayer(mob, 128.0D);
        if (player == null) {
            return 1.0D;
        }
        int rank = DynastyStats.getRank(player);
        return 1.0D + Math.min(0.8D, 0.04D * rank);
    }

    private static boolean add(AttributeInstance instance, UUID id, String name, double amount) {
        if (instance == null || amount <= 0.0D) {
            return false;
        }
        if (instance.getModifier(id) != null) {
            return false;                                // 已经加过就跳过（幂等）
        }
        instance.addPermanentModifier(new AttributeModifier(id, name, amount,
                AttributeModifier.Operation.ADDITION));
        return true;
    }
}
