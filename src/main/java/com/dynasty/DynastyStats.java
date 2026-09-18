package com.dynasty;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;

/**
 * 王朝玩家数值系统：官阶（功名）、忠诚、叛乱。
 * Dynasty player stats: official rank (merit), loyalty, rebellion. Stored in player persistent data.
 */
@SuppressWarnings("null")
public final class DynastyStats {

    private DynastyStats() {
    }

    private static final String RANK = "dynasty_rank";
    private static final String MERIT = "dynasty_merit";
    private static final String LOYALTY = "dynasty_loyalty";
    private static final String REBELLION = "dynasty_rebellion";

    /** 官阶名称（中文，20 阶，层层递进）。/ Rank names (Chinese, 20 steps). */
    public static final String[] RANK_ZH = {
            "布衣", "童生", "秀才", "举人", "贡士", "进士", "庶吉士", "编修", "侍读", "侍讲",
            "翰林", "侍郎", "尚书", "大学士", "太傅", "少师", "太师", "丞相", "摄政王", "天子"
    };

    /** 官阶名称（英文）。/ Rank names (English). */
    public static final String[] RANK_EN = {
            "Commoner", "Student", "Licentiate", "Provincial Graduate", "Tribute Student",
            "Metropolitan Graduate", "Hanlin Bachelor", "Compiler", "Imperial Reader", "Imperial Lecturer",
            "Hanlin Scholar", "Vice Minister", "Minister", "Grand Secretary", "Grand Tutor",
            "Junior Preceptor", "Grand Preceptor", "Chancellor", "Prince Regent", "Son of Heaven"
    };

    /**
     * 各阶所需功名（递增：每阶比上一阶多要 25 点）。
     * Merit needed for each rank; every step costs 25 more than the previous one.
     */
    public static final int[] RANK_THRESHOLDS = thresholds();

    private static int[] thresholds() {
        int[] out = new int[RANK_ZH.length];
        out[0] = 0;
        for (int i = 1; i < out.length; i++) {
            out[i] = out[i - 1] + 100 + 25 * (i - 1);
        }
        return out;
    }

    /** 功名 → 官阶 / merit to rank */
    public static int rankForMerit(int merit) {
        int rank = 0;
        for (int i = 1; i < RANK_THRESHOLDS.length; i++) {
            if (merit >= RANK_THRESHOLDS[i]) {
                rank = i;
            }
        }
        return rank;
    }

    /** 下一阶还需要多少功名（满阶返回 0）。/ merit still needed for the next rank */
    public static int meritToNext(Player player) {
        int rank = getRank(player);
        if (rank >= RANK_THRESHOLDS.length - 1) {
            return 0;
        }
        return Math.max(0, RANK_THRESHOLDS[rank + 1] - getMerit(player));
    }

    public static int getRank(Player player) {
        return player.getPersistentData().getInt(RANK);
    }

    public static int getMerit(Player player) {
        return player.getPersistentData().getInt(MERIT);
    }

    public static int getLoyalty(Player player) {
        return player.getPersistentData().getInt(LOYALTY);
    }

    public static int getRebellion(Player player) {
        return player.getPersistentData().getInt(REBELLION);
    }

    public static String rankName(Player player, boolean chinese) {
        int r = Math.max(0, Math.min(RANK_ZH.length - 1, getRank(player)));
        return chinese ? RANK_ZH[r] : RANK_EN[r];
    }

    public static void addMerit(ServerPlayer player, int amount) {
        int boosted = Math.round(amount * DynastyTrinkets.meritMultiplier(player));   // 金印饰品
        int merit = Math.max(0, getMerit(player) + boosted);
        player.getPersistentData().putInt(MERIT, merit);
        int newRank = rankForMerit(merit);
        int oldRank = getRank(player);
        if (newRank != oldRank) {
            player.getPersistentData().putInt(RANK, newRank);
            player.sendSystemMessage(Component.literal("§6[王朝] 官阶晋升：§e"
                    + RANK_ZH[newRank] + "§7 / " + RANK_EN[newRank]
                    + "§8（第 " + newRank + " 阶 / 功名 " + merit + "）"));
            player.addEffect(new net.minecraft.world.effect.MobEffectInstance(
                    DynastyEffects.MANDATE_OF_HEAVEN.get(), 20 * 120, 0));
            // 官阶越高，基础属性与饰品槽位越多 / higher rank grants stats and trinket slots
            DynastyRankPerks.apply(player);
            DynastyRankPerks.announce(player, newRank);
            DynastyAdvancements.awardForRank(player, newRank);
        }
        player.getPersistentData().putInt("dynasty_rank_notice", DynastyStats.meritToNext(player));
    }

    public static void addLoyalty(ServerPlayer player, int amount) {
        int v = Math.max(0, Math.min(100, getLoyalty(player) + amount));
        player.getPersistentData().putInt(LOYALTY, v);
    }

    public static void addRebellion(ServerPlayer player, int amount) {
        int v = Math.max(0, Math.min(100, getRebellion(player) + amount));
        player.getPersistentData().putInt(REBELLION, v);
        if (v >= 100) {
            player.sendSystemMessage(Component.literal("§c[王朝] 民怨沸腾！叛军即将出现……"));
        } else if (v >= 60) {
            player.sendSystemMessage(Component.literal("§e[王朝] 民心生变（叛乱 " + v + "%）"));
        }
    }

    public static void setRank(ServerPlayer player, int rank) {
        int r = Math.max(0, Math.min(RANK_ZH.length - 1, rank));
        player.getPersistentData().putInt(RANK, r);
        // 功名也要跟上，否则每秒的「按功名换算官阶」会把它退回去
        player.getPersistentData().putInt(MERIT, Math.max(getMerit(player), RANK_THRESHOLDS[r]));
    }

    public static void showStats(ServerPlayer player) {
        int rank = getRank(player);
        player.sendSystemMessage(Component.literal("§6===== 王朝档案 =====").withStyle(ChatFormatting.GOLD));
        player.sendSystemMessage(Component.literal("§7官阶：§f" + rankName(player, true)
                + " §8(" + RANK_EN[Math.min(RANK_EN.length - 1, rank)] + ")"
                + " §8第 " + rank + "/" + (RANK_ZH.length - 1) + " 阶"));
        player.sendSystemMessage(Component.literal("§7功名：§f" + getMerit(player)
                + (meritToNext(player) > 0
                   ? " §8（升下一阶还需 " + meritToNext(player) + "）" : " §8（已至顶阶）")));
        player.sendSystemMessage(Component.literal("§7忠诚：§f" + getLoyalty(player) + "§7%"));
        player.sendSystemMessage(Component.literal("§7叛乱：§f" + getRebellion(player) + "§7%"));
        player.sendSystemMessage(Component.literal("§7官阶加成：§f+" + DynastyRankPerks.bonusHealth(rank)
                + " 生命、§f+" + String.format("%.2f", DynastyRankPerks.bonusAttack(rank))
                + " 攻击、§f+" + String.format("%.2f", DynastyRankPerks.bonusArmor(rank))
                + " 护甲；§d任务万能槽 +" + DynastySlotProgression.bonusSlots(player)));
    }
}
