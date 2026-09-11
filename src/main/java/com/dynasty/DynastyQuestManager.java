package com.dynasty;

import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * 任务进度与奖励结算（服务端）。进度保存在玩家数据中。
 * Quest progress and reward claiming (server side), stored in the player's persistent data.
 */
@SuppressWarnings("null")
public final class DynastyQuestManager {

    private DynastyQuestManager() {
    }

    private static final String PROGRESS = "dq_p_";
    private static final String CLAIMED = "dq_c_";
    private static final String FLAG = "dq_e_";

    // ---------------------------------------------------------------- 进度
    public static int progress(ServerPlayer player, DynastyQuests.Quest quest) {
        switch (quest.type) {
            case ITEM -> {
                int have = countItem(player, quest.target);
                return Math.min(quest.need, have);
            }
            case KILL -> {
                return Math.min(quest.need, player.getPersistentData().getInt(PROGRESS + quest.index));
            }
            default -> {
                int stored = player.getPersistentData().getInt(PROGRESS + quest.index);
                return Math.min(quest.need, Math.max(stored, derivedEvent(player, quest.target)));
            }
        }
    }

    private static int derivedEvent(ServerPlayer player, String key) {
        return switch (key) {
            case "rank1" -> DynastyStats.getRank(player) >= 1 ? 1 : 0;
            case "rank9" -> DynastyStats.getRank(player) >= 9 ? 1 : 0;
            case "calm" -> DynastyStats.getRebellion(player) <= 20 ? 1 : 0;
            default -> 0;
        };
    }

    public static boolean claimed(ServerPlayer player, int index) {
        return player.getPersistentData().getBoolean(CLAIMED + index);
    }

    /** 前置任务是否都已领取 / whether all prerequisite quests were claimed. */
    public static boolean unlocked(ServerPlayer player, DynastyQuests.Quest quest) {
        for (int req : quest.requires) {
            if (!claimed(player, req)) {
                return false;
            }
        }
        return true;
    }

    public static boolean ready(ServerPlayer player, DynastyQuests.Quest quest) {
        return progress(player, quest) >= quest.need;
    }

    // ---------------------------------------------------------------- 领奖
    public static boolean claim(ServerPlayer player, int index) {
        DynastyQuests.Quest quest = DynastyQuests.get(index);
        if (quest == null || claimed(player, index) || !unlocked(player, quest) || !ready(player, quest)) {
            return false;
        }
        player.getPersistentData().putBoolean(CLAIMED + index, true);
        for (ItemStack reward : quest.rewards()) {
            if (!player.getInventory().add(reward)) {
                player.drop(reward, false);
            }
        }
        DynastyStats.addMerit(player, 50);
        player.sendSystemMessage(Component.literal("§6[任务] §r已完成：§e" + quest.title + " §7（功名 +50）"));
        return true;
    }

    // ---------------------------------------------------------------- 事件与击杀
    public static void notifyEvent(ServerPlayer player, String key) {
        for (DynastyQuests.Quest quest : DynastyQuests.all()) {
            if (quest.type == DynastyQuests.Type.EVENT && quest.target.equals(key)) {
                int stored = player.getPersistentData().getInt(PROGRESS + quest.index);
                player.getPersistentData().putInt(PROGRESS + quest.index, Math.min(quest.need, stored + 1));
            }
        }
        player.getPersistentData().putBoolean(FLAG + key, true);
    }

    public static void onKill(ServerPlayer player, String entityId) {
        for (DynastyQuests.Quest quest : DynastyQuests.all()) {
            if (quest.type == DynastyQuests.Type.KILL && quest.target.equals(entityId)) {
                int stored = player.getPersistentData().getInt(PROGRESS + quest.index);
                player.getPersistentData().putInt(PROGRESS + quest.index, Math.min(quest.need, stored + 1));
            }
        }
    }

    public static boolean hasFlag(ServerPlayer player, String key) {
        return player.getPersistentData().getBoolean(FLAG + key);
    }

    // ---------------------------------------------------------------- 同步数据
    public static int[] progressArray(ServerPlayer player) {
        int n = DynastyQuests.count();
        int[] out = new int[n];
        for (int i = 0; i < n; i++) {
            out[i] = progress(player, DynastyQuests.get(i));
        }
        return out;
    }

    public static boolean[] claimedArray(ServerPlayer player) {
        int n = DynastyQuests.count();
        boolean[] out = new boolean[n];
        for (int i = 0; i < n; i++) {
            out[i] = claimed(player, i);
        }
        return out;
    }

    private static int countItem(ServerPlayer player, String itemId) {
        Item item = ForgeRegistries.ITEMS.getValue(new ResourceLocation(itemId));
        if (item == null) {
            return 0;
        }
        int count = 0;
        for (int i = 0; i < player.getInventory().getContainerSize(); i++) {
            ItemStack stack = player.getInventory().getItem(i);
            if (!stack.isEmpty() && stack.getItem() == item) {
                count += stack.getCount();
            }
        }
        return count;
    }
}
