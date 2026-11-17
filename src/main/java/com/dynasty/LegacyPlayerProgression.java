package com.dynasty;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Copies audited player facts only; it never dispatches rewards or copies active control state. */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class LegacyPlayerProgression {
    private static final String WINDOW = "dynasty_merit_kill_window";
    private static final String EARNED = "dynasty_merit_kill_earned";
    private static final String BLESSING = "DynastyXuanniaoBlessing";
    private static final List<String> FIRST_KILLS = List.of(
            "dragon_emperor", "undead_first_emperor", "nine_heaven_general", "dragon_king",
            "rebel_general", "eunuch_mastermind", "phoenix", "qilin", "nian_beast", "nine_tailed_fox");
    private static final Map<String, Integer> ROOT_TYPES = rootTypes();

    private LegacyPlayerProgression() {}

    @SubscribeEvent
    public static void clonePlayer(PlayerEvent.Clone event) {
        if (!(event.getOriginal() instanceof ServerPlayer oldPlayer)
                || !(event.getEntity() instanceof ServerPlayer newPlayer)
                || oldPlayer == newPlayer || !oldPlayer.getUUID().equals(newPlayer.getUUID())) return;
        List<String> invalid = copyAuditedRoot(oldPlayer.getPersistentData(), newPlayer.getPersistentData());
        if (!invalid.isEmpty()) {
            Dynasty.LOGGER.warn("[Dynasty] Skipped malformed legacy progression fields for {}: {}",
                    newPlayer.getUUID(), invalid);
        }
    }

    // Package access permits offline tests using real NBT, without constructing a player or world.
    static List<String> copyAuditedRoot(CompoundTag source, CompoundTag target) {
        List<String> invalid = new ArrayList<>();
        for (var entry : ROOT_TYPES.entrySet()) {
            copyTyped(source, target, entry.getKey(), entry.getValue(), invalid);
        }
        if (source.contains(BLESSING)) {
            if (source.hasUUID(BLESSING)) target.put(BLESSING, source.get(BLESSING).copy());
            else invalid.add(BLESSING);
        }
        // Preserve the economic budget's original timestamp and spent amount together.
        // Malformed/partial pairs are diagnosed, not silently converted into a new budget.
        // Anti-reset preservation is guaranteed here only for a well-typed pair.
        if (source.contains(WINDOW) || source.contains(EARNED)) {
            if (source.contains(WINDOW, Tag.TAG_LONG) && source.contains(EARNED, Tag.TAG_INT)) {
                target.put(WINDOW, source.get(WINDOW).copy());
                target.put(EARNED, source.get(EARNED).copy());
            } else {
                invalid.add(WINDOW + "/" + EARNED);
            }
        }
        CompoundTag persisted = source.getCompound(Player.PERSISTED_NBT_TAG);
        for (String boss : FIRST_KILLS) {
            String key = "dynasty_firstkill_" + boss;
            if (source.contains(key, Tag.TAG_BYTE) && source.getBoolean(key)
                    || persisted.contains(key, Tag.TAG_BYTE) && persisted.getBoolean(key)) {
                target.putBoolean(key, true);
            }
        }
        // Do not mutate inherited PlayerPersisted: Forge initially aliases the old Tag,
        // and existing whole-container Clone handlers may subsequently replace it.
        return List.copyOf(invalid);
    }

    private static void copyTyped(CompoundTag source, CompoundTag target, String key, int type,
                                  List<String> invalid) {
        if (!source.contains(key)) return;
        if (source.contains(key, type)) target.put(key, source.get(key).copy());
        else invalid.add(key);
    }

    private static Map<String, Integer> rootTypes() {
        Map<String, Integer> types = new LinkedHashMap<>();
        add(types, Tag.TAG_INT, "dynasty_merit", "dynasty_rank", "dynasty_loyalty", "dynasty_rebellion",
                "dynasty_boss_kinds", "DynastyEventMonsterKills");
        add(types, Tag.TAG_STRING, "dynasty_boss_kinds_list", "dynasty_festival_day");
        add(types, Tag.TAG_BYTE, "dynasty_manual_given");
        for (String key : List.of("keju", "minister", "army", "qilin", "dim_celestial", "dim_underworld")) {
            types.put("dynasty_merit_evt_" + key, (int) Tag.TAG_BYTE);
        }
        for (String key : List.of("dragon_crystal", "xuantian_jade", "dragon_emperor_seal", "emperor_bone",
                "jade", "phoenix_feather", "rebel_head", "eunuch_token", "sky_token", "jade_seal",
                "official_seal", "edict", "tiger_tally", "blueprint", "bronze_ingot", "silver_ingot",
                "refined_steel", "cinnabar")) {
            types.put("dynasty_merit_seen_" + key, (int) Tag.TAG_BYTE);
        }
        for (String key : List.of("gilded_mace", "supreme_sword", "seven_star_saber", "sunbow")) {
            types.put("dynasty_gift_" + key, (int) Tag.TAG_BYTE);
        }
        for (String boss : FIRST_KILLS) types.put("dynasty_firstkill_" + boss, (int) Tag.TAG_BYTE);
        for (int index = 0; index < 24; index++) {
            types.put("dq_p_" + index, (int) Tag.TAG_INT);
            types.put("dq_c_" + index, (int) Tag.TAG_BYTE);
        }
        for (String key : List.of("keju", "rank1", "minister", "army", "calm", "dim_celestial",
                "dim_underworld", "qilin", "rank9")) {
            types.put("dq_e_" + key, (int) Tag.TAG_BYTE);
        }
        return Map.copyOf(types);
    }

    private static void add(Map<String, Integer> types, int type, String... keys) {
        for (String key : keys) types.put(key, type);
    }
}
