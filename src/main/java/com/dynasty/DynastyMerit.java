package com.dynasty;

import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EntityType;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * 功名来源（任务只给一点点，主要靠打怪 / 与 NPC 交互 / 第一次获得新物品）。
 *
 * Merit sources: fights, NPC interaction and first-time item pickups. Quest rewards
 * only give a small amount, so ranks are earned by actually playing.
 */
@SuppressWarnings("null")
public final class DynastyMerit {

    private DynastyMerit() {
    }

    // ---- 与 NPC / 事件交互：每个事件只给一次 / one-off rewards
    private static final String FLAG = "dynasty_merit_evt_";

    public static void onEvent(ServerPlayer player, String key) {
        int amount = switch (key) {
            case "keju" -> 30;              // 科举答对
            case "minister" -> 15;          // 与大臣交谈
            case "army" -> 12;              // 虎符列阵
            case "qilin" -> 10;             // 喂麒麟
            case "dim_celestial" -> 40;     // 第一次到天朝
            case "dim_underworld" -> 40;    // 第一次到地府
            default -> 0;
        };
        if (amount <= 0 || player.getPersistentData().getBoolean(FLAG + key)) {
            return;
        }
        player.getPersistentData().putBoolean(FLAG + key, true);
        DynastyStats.addMerit(player, amount);
        player.displayClientMessage(Component.literal("§6[功名] §r+" + amount + "（" + reason(key) + "）"), true);
    }

    private static String reason(String key) {
        return switch (key) {
            case "keju" -> "科举中第";
            case "minister" -> "拜见大臣";
            case "army" -> "列阵点兵";
            case "qilin" -> "祥瑞麒麟";
            case "dim_celestial" -> "登临天朝";
            case "dim_underworld" -> "初入地府";
            default -> "功勋";
        };
    }

    // ---- 击杀：滚怪也有功名，但每 10 分钟封顶，避免刷分 / kill merit, capped per 10 minutes
    private static final String KILL_WINDOW = "dynasty_merit_kill_window";
    private static final String KILL_EARNED = "dynasty_merit_kill_earned";
    private static final int KILL_CAP = 120;

    public static void onMobKill(ServerPlayer player, EntityType<?> type) {
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(type);
        if (id == null || !id.getNamespace().equals(Dynasty.MODID)) {
            return;
        }
        int amount = switch (id.getPath()) {
            case "dragon_emperor" -> 300;
            case "nine_heaven_general" -> 260;
            case "rebel_general", "eunuch_mastermind" -> 220;
            case "undead_first_emperor" -> 240;
            case "phoenix", "qilin" -> 60;
            case "nian_beast", "nine_tailed_fox" -> 40;
            case "assassin", "royal_guard" -> 12;
            case "archer", "imperial_soldier", "rebel_soldier", "terracotta_warrior" -> 5;
            default -> 0;
        };
        if (amount <= 0) {
            return;
        }
        // 小怪部分有 10 分钟上限（Boss 不受限）/ trash merit is capped
        if (amount < 100) {
            long now = System.currentTimeMillis();
            long window = player.getPersistentData().getLong(KILL_WINDOW);
            int earned = player.getPersistentData().getInt(KILL_EARNED);
            if (now - window > 10 * 60 * 1000L) {
                player.getPersistentData().putLong(KILL_WINDOW, now);
                earned = 0;
            }
            if (earned >= KILL_CAP) {
                return;
            }
            amount = Math.min(amount, KILL_CAP - earned);
            player.getPersistentData().putInt(KILL_EARNED, earned + amount);
        }
        DynastyStats.addMerit(player, amount);
    }

    // ---- 第一次获得某件王朝物品：每种一次 / first-time pickup merit
    private static final String SEEN = "dynasty_merit_seen_";

    public static void onFirstObtain(ServerPlayer player, String itemPath) {
        int amount = switch (itemPath) {
            case "dragon_crystal", "xuantian_jade", "dragon_emperor_seal", "emperor_bone" -> 25;
            case "jade", "phoenix_feather", "rebel_head", "eunuch_token", "sky_token" -> 12;
            case "jade_seal", "official_seal", "edict", "tiger_tally", "blueprint" -> 8;
            case "bronze_ingot", "silver_ingot", "refined_steel", "cinnabar" -> 5;
            default -> 0;
        };
        if (amount <= 0 || player.getPersistentData().getBoolean(SEEN + itemPath)) {
            return;
        }
        player.getPersistentData().putBoolean(SEEN + itemPath, true);
        DynastyStats.addMerit(player, amount);
        player.displayClientMessage(Component.literal(
                "§6[功名] §r+" + amount + "（初次获得 " + itemPath + "）"), true);
    }
}
