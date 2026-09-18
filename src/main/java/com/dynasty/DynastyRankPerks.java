package com.dynasty;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

import java.util.UUID;

/**
 * 官阶福利：官阶越高，基础属性越好。饰品加槽由任务里程碑独立管理。
 *
 * 每阶提供：+2 生命、+0.25 攻击、+0.25 护甲；
 * Rank perks grant attributes; quest milestones grant Curios slots.
 */
@SuppressWarnings("null")
public final class DynastyRankPerks {

    private DynastyRankPerks() {
    }

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

    /** 应用（幂等）：属性按官阶刷新。 */
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
    }
}
