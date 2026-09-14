package com.dynasty;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

import java.util.UUID;

/**
 * 官阶福利：官阶越高，基础属性越好、能戴的饰品也越多。
 *
 * 每阶提供：+2 生命、+0.25 攻击、+0.25 护甲；
 * 每 4 阶额外 +1 个「王朝饰品」Curios 槽（最多 +5，加上开局 3 格 = 8 格）。
 *
 * 玩家反馈「开局只有 1 个饰品槽太少」→ 基础槽位从 1 提到 3（见 slots/dynasty_trinket.json）。
 *
 * Rank perks: each rank grants health/attack/armor, and every 4 ranks adds one
 * extra Curios trinket slot (base 3 at start, up to +5).
 */
@SuppressWarnings("null")
public final class DynastyRankPerks {

    private DynastyRankPerks() {
    }

    /** 槽位类型 / the Curios slot that grows with rank */
    public static final String SLOT = "dynasty_trinket";

    /** 开局就有的饰品槽（和 data/curios/curios/slots/dynasty_trinket.json 的 size 保持一致） */
    public static final int BASE_SLOTS = 3;

    private static final UUID HP_ID = UUID.fromString("d1a5c0de-0000-4000-8000-000000000001");
    private static final UUID ATK_ID = UUID.fromString("d1a5c0de-0000-4000-8000-000000000002");
    private static final UUID ARMOR_ID = UUID.fromString("d1a5c0de-0000-4000-8000-000000000003");

    public static int bonusHealth(int rank) {
        return rank * 2;
    }

    public static double bonusAttack(int rank) {
        return rank * 0.25D;
    }

    public static double bonusArmor(int rank) {
        return rank * 0.25D;
    }

    /** 额外饰品槽：开局 3 个，每 4 阶 +1（最多 +5，共 8 格） */
    public static int bonusSlots(int rank) {
        return Math.min(5, rank / 4);
    }

    /** 应用（幂等）：属性按官阶刷新，饰品槽只增不减。/ applies perks, idempotently */
    public static void apply(ServerPlayer player) {
        // 老存档的官阶按新阶梯（20 阶）重新换算
        int expected = DynastyStats.rankForMerit(DynastyStats.getMerit(player));
        int rank = DynastyStats.getRank(player);
        if (expected != rank) {
            DynastyStats.setRank(player, expected);
            rank = expected;
        }
        set(player, Attributes.MAX_HEALTH, HP_ID, "dynasty_rank_health", bonusHealth(rank));
        set(player, Attributes.ATTACK_DAMAGE, ATK_ID, "dynasty_rank_attack", bonusAttack(rank));
        set(player, Attributes.ARMOR, ARMOR_ID, "dynasty_rank_armor", bonusArmor(rank));
        if (player.getHealth() > player.getMaxHealth()) {
            player.setHealth(player.getMaxHealth());
        }
        int want = bonusSlots(rank);
        if (want > 0) {
            DynastyCuriosSetup.growTrinketSlots(player, want);
        }
    }

    private static void set(ServerPlayer player, net.minecraft.world.entity.ai.attributes.Attribute attribute,
                            UUID id, String name, double amount) {
        AttributeInstance instance = player.getAttribute(attribute);
        if (instance == null) {
            return;
        }
        AttributeModifier existing = instance.getModifier(id);
        if (existing != null) {
            if (existing.getAmount() == amount) {
                return;
            }
            instance.removeModifier(id);
        }
        if (amount != 0.0D) {
            instance.addPermanentModifier(new AttributeModifier(id, name, amount,
                    AttributeModifier.Operation.ADDITION));
        }
    }

    /** 官阶晋升时的提示 / message shown on rank up */
    public static void announce(ServerPlayer player, int newRank) {
        player.sendSystemMessage(Component.literal("§6[官阶福利] §r基础属性提升：§f+"
                + bonusHealth(newRank) + " 生命、+" + String.format("%.2f", bonusAttack(newRank))
                + " 攻击、+" + String.format("%.2f", bonusArmor(newRank)) + " 护甲"));
        int slots = bonusSlots(newRank);
        if (slots > 0) {
            player.sendSystemMessage(Component.literal("§d[官阶福利] §r饰品槽 +" + slots
                    + "（共 " + (BASE_SLOTS + slots) + " 格，物品栏里的 Curios 面板可查看）"));
        }
    }
}
