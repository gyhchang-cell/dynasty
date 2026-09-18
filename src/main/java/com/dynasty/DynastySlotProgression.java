package com.dynasty;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.LinkedHashMap;
import java.util.Map;

/** 每个里程碑永久 +1 万能槽；按玩家保存，重领、死亡、重进与任务队伍变动不会重复加槽。 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class DynastySlotProgression {
    private static final String KEY = "dynasty_slot_milestones";
    private static final Map<String, Milestone> MILESTONES = loadMilestones();
    private static Field questFile;
    private static Method teamData;
    private static Method questById;
    private static Method completed;
    private static boolean bridgeInitialized;
    private static boolean warned;

    private record Milestone(String title, long questId) { }

    private DynastySlotProgression() { }

    private static Map<String, Milestone> loadMilestones() {
        var stream = DynastySlotProgression.class.getResourceAsStream("/data/dynasty/curios_progression.json");
        if (stream == null) {
            throw new IllegalStateException("Missing generated Curios progression data");
        }
        try (var reader = new InputStreamReader(stream, StandardCharsets.UTF_8)) {
            JsonObject json = new Gson().fromJson(reader, JsonObject.class);
            Map<String, Milestone> entries = new LinkedHashMap<>();
            json.entrySet().forEach(entry -> {
                JsonObject value = entry.getValue().getAsJsonObject();
                entries.put(entry.getKey(), new Milestone(value.get("title").getAsString(),
                        Long.parseLong(value.get("quest_id").getAsString(), 16)));
            });
            return Map.copyOf(entries);
        } catch (java.io.IOException exception) {
            throw new IllegalStateException("Cannot load Curios progression", exception);
        }
    }

    public static java.util.Set<String> milestoneIds() {
        return MILESTONES.keySet();
    }

    private static CompoundTag progress(Player player) {
        return player.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).getCompound(KEY);
    }

    public static int bonusSlots(Player player) {
        CompoundTag progress = progress(player);
        return (int) MILESTONES.keySet().stream().filter(progress::getBoolean).count();
    }

    /** FTB command reward calls this as the reward recipient, with elevated permission. */
    public static int unlock(ServerPlayer player, String id) {
        Milestone milestone = MILESTONES.get(id);
        if (milestone == null) {
            return 0;
        }
        CompoundTag saved = player.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
        CompoundTag flags = saved.getCompound(KEY);
        if (flags.getBoolean(id)) {
            sync(player);
            return 1;
        }
        flags.putBoolean(id, true);
        saved.put(KEY, flags);
        player.getPersistentData().put(Player.PERSISTED_NBT_TAG, saved);
        sync(player);
        player.sendSystemMessage(Component.literal("§6[里程碑] §f" + milestone.title()
                + "§r：永久获得 §d+1 万能饰品槽§r（任务已解锁 " + bonusSlots(player)
                + "/" + MILESTONES.size() + "）。打开 Curios 面板即可佩戴。"));
        return 1;
    }

    private static void sync(ServerPlayer player) {
        DynastyCuriosSetup.syncQuestSlots(player, bonusSlots(player));
    }

    /** 旧档已完成的任务、离线队友完成的任务，也能补发；不需要重置任务或输入命令。 */
    private static void reconcileQuests(ServerPlayer player) {
        if (!ModList.get().isLoaded("ftbquests") || bonusSlots(player) == MILESTONES.size()) {
            return;
        }
        try {
            if (!bridgeInitialized) {
                Class<?> fileType = Class.forName("dev.ftb.mods.ftbquests.quest.ServerQuestFile");
                Class<?> teamType = Class.forName("dev.ftb.mods.ftbquests.quest.TeamData");
                Class<?> objectType = Class.forName("dev.ftb.mods.ftbquests.quest.QuestObject");
                questFile = fileType.getField("INSTANCE");
                teamData = fileType.getMethod("getOrCreateTeamData", Entity.class);
                questById = fileType.getMethod("getQuest", long.class);
                completed = teamType.getMethod("isCompleted", objectType);
                bridgeInitialized = true;
            }
            Object file = questFile.get(null);
            if (file == null) {
                return;
            }
            Object team = teamData.invoke(file, player);
            if (team == null) {
                return;
            }
            CompoundTag flags = progress(player);
            for (var entry : MILESTONES.entrySet()) {
                if (flags.getBoolean(entry.getKey())) {
                    continue;
                }
                Object quest = questById.invoke(file, entry.getValue().questId());
                if (quest != null && Boolean.TRUE.equals(completed.invoke(team, quest))) {
                    unlock(player, entry.getKey());
                }
            }
        } catch (ReflectiveOperationException | LinkageError exception) {
            if (!warned) {
                Dynasty.LOGGER.warn("[Dynasty] FTB slot reconciliation unavailable; command rewards still work", exception);
                warned = true;
            }
        }
    }

    @SubscribeEvent
    public static void onTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player)
                || player.tickCount % 20 != 0) {
            return;
        }
        if (player.tickCount % 100 == 0) {
            reconcileQuests(player);
        }
        sync(player);
    }

    @SubscribeEvent
    public static void onClone(PlayerEvent.Clone event) {
        CompoundTag old = progress(event.getOriginal());
        CompoundTag saved = event.getEntity().getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
        saved.put(KEY, old.copy());
        event.getEntity().getPersistentData().put(Player.PERSISTED_NBT_TAG, saved);
        DynastyTrinkets.forget(event.getEntity());
    }
}
