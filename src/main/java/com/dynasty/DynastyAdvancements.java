package com.dynasty;

import net.minecraft.advancements.Advancement;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

/**
 * 任务/成就联动：把「做过的事」变成成就，FTB 任务书再据此**自动判定完成**
 * （而不是让玩家自己点「完成」）。
 *
 * Achievement bridge: events that happen in the mod are turned into advancements,
 * which the FTB Quests book uses as automatic completion criteria.
 */
public final class DynastyAdvancements {

    private DynastyAdvancements() {
    }

    /** 发放成就 / awards an advancement */
    public static void award(ServerPlayer player, String id) {
        MinecraftServer server = player.getServer();
        if (server == null) {
            return;
        }
        Advancement advancement = server.getAdvancements()
                .getAdvancement(new ResourceLocation(Dynasty.MODID, id));
        if (advancement == null) {
            return;
        }
        player.getAdvancements().award(advancement, "code");
    }

    /** 事件 → 成就 / quest event key to advancement */
    public static void awardForEvent(ServerPlayer player, String key) {
        switch (key) {
            case "keju" -> award(player, "exam_passed");
            case "minister" -> award(player, "met_minister");
            case "army" -> award(player, "army_led");
            case "qilin" -> award(player, "qilin_friend");
            case "dim_celestial" -> award(player, "entered_celestial");
            case "dim_underworld" -> award(player, "entered_underworld");
            default -> {
            }
        }
        // 顺便结算事件功名（每个事件只给一次）/ one-off merit for interactions
        DynastyMerit.onEvent(player, key);
    }

    /** 由数值推导的条件（官阶 / 民心）——每秒检查一次 / derived conditions, checked periodically */
    public static void checkDerived(ServerPlayer player) {
        // 官阶福利（属性 + 饰品槽）随时保持最新 / keep rank perks up to date
        DynastyRankPerks.apply(player);
        int rank = DynastyStats.getRank(player);
        awardForRank(player, rank);
        if (DynastyStats.getRebellion(player) <= 20) {
            award(player, "rebellion_calmed");
        }
    }

    /** 官阶成就：每到一个台阶就点亮 / rank milestones */
    public static void awardForRank(ServerPlayer player, int rank) {
        if (rank >= 1) {
            award(player, "rank_official");
        }
        if (rank >= 3) {
            award(player, "rank_scholar");
        }
        if (rank >= 10) {
            award(player, "rank_hanlin");
        }
        if (rank >= 12) {
            award(player, "rank_minister");
        }
        if (rank >= 13) {
            award(player, "rank_grand_secretary");
        }
        if (rank >= 17) {
            award(player, "rank_chancellor");
        }
        if (rank >= 18) {
            award(player, "rank_prince_regent");
        }
        if (rank >= 19) {
            award(player, "rank_son_of_heaven");
        }
    }
}
