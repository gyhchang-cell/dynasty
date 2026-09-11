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

    /** 官阶名称（中文）。/ Rank names (Chinese). */
    public static final String[] RANK_ZH = {
            "布衣", "童生", "秀才", "举人", "贡士", "进士", "翰林", "侍郎", "尚书", "大学士", "丞相", "摄政王"
    };

    /** 官阶名称（英文）。/ Rank names (English). */
    public static final String[] RANK_EN = {
            "Commoner", "Student", "Licentiate", "Provincial Graduate", "Tribute Student", "Metropolitan Graduate",
            "Hanlin Scholar", "Vice Minister", "Minister", "Grand Secretary", "Chancellor", "Prince Regent"
    };

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
        int newRank = Math.min(RANK_ZH.length - 1, merit / 100);
        int oldRank = getRank(player);
        if (newRank != oldRank) {
            player.getPersistentData().putInt(RANK, newRank);
            player.sendSystemMessage(Component.literal("§6[王朝] 官阶晋升：§e"
                    + RANK_ZH[newRank] + "§7 / " + RANK_EN[newRank]));
            player.addEffect(new net.minecraft.world.effect.MobEffectInstance(
                    DynastyEffects.MANDATE_OF_HEAVEN.get(), 20 * 120, 0));
        }
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
        player.getPersistentData().putInt(RANK, Math.max(0, Math.min(RANK_ZH.length - 1, rank)));
    }

    public static void showStats(ServerPlayer player) {
        player.sendSystemMessage(Component.literal("§6===== 王朝档案 =====").withStyle(ChatFormatting.GOLD));
        player.sendSystemMessage(Component.literal("§7官阶：§f" + rankName(player, true)
                + " §8(" + RANK_EN[Math.min(RANK_EN.length - 1, getRank(player))] + ")"));
        player.sendSystemMessage(Component.literal("§7功名：§f" + getMerit(player)));
        player.sendSystemMessage(Component.literal("§7忠诚：§f" + getLoyalty(player) + "§7%"));
        player.sendSystemMessage(Component.literal("§7叛乱：§f" + getRebellion(player) + "§7%"));
    }
}
