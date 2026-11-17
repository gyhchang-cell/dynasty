package com.dynasty.legacyqa;

import com.google.gson.GsonBuilder;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtIo;
import net.minecraft.nbt.Tag;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Reads native NBT only. It neither loads a world/registry nor writes any input file. */
public final class ReadLegacyInput {
    private static CompoundTag read(Path p) throws Exception {
        try (var input = Files.newInputStream(p)) { return NbtIo.readCompressed(input); }
    }
    private static String sha(Path p) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(p)));
    }
    private static Map<String, Object> player(CompoundTag p) {
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("has_valid_uuid", p.hasUUID("UUID"));
        if (p.hasUUID("UUID")) row.put("uuid", p.getUUID("UUID").toString());
        CompoundTag facts = p.getCompound("ForgeData");
        Map<String, Object> fields = new LinkedHashMap<>();
        for (String key : facts.getAllKeys().stream().sorted().toList()) {
            Tag value = facts.get(key);
            fields.put(key, Map.of("native_type_id", value.getId(), "snbt", value.toString()));
        }
        row.put("forge_data", fields); row.put("forge_data_snbt", facts.toString());
        List<Object> inventory = new ArrayList<>();
        for (Tag value : p.getList("Inventory", 10)) {
            CompoundTag stack = (CompoundTag) value;
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("id", stack.getString("id")); item.put("count", stack.getByte("Count"));
            item.put("slot", stack.getByte("Slot")); item.put("full_stack_snbt", stack.toString());
            item.put("count_type", stack.getTagType("Count")); item.put("slot_type", stack.getTagType("Slot"));
            item.put("tag_present", stack.contains("tag")); item.put("forge_caps_present", stack.contains("ForgeCaps"));
            inventory.add(item);
        }
        row.put("inventory", inventory); row.put("inventory_snbt", p.get("Inventory").toString());
        return row;
    }
    public static void main(String[] args) throws Exception {
        Path levelPath = Path.of(args[0]), playerPath = Path.of(args[1]), out = Path.of(args[2]);
        CompoundTag level = read(levelPath), diskPlayer = read(playerPath), integratedPlayer = level.getCompound("Data").getCompound("Player");
        List<Object> legacyIds = new ArrayList<>();
        CompoundTag registry = level.getCompound("fml").getCompound("Registries").getCompound("minecraft:item");
        for (Tag tag : registry.getList("ids", 10)) {
            CompoundTag entry = (CompoundTag) tag;
            if (List.of("dynasty:quest_ledger", "dynasty:healing_talisman", "dynasty:dynasty_guide", "dynasty:vajra_talisman", "ftbquests:book").contains(entry.getString("K")))
                legacyIds.add(Map.of("name", entry.getString("K"), "old_numeric_id", entry.getInt("V"), "snbt", entry.toString()));
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("status", "NATIVE_NBT_INPUT_READ_ONLY_NOT_WORLD_LOAD");
        result.put("level_path", levelPath.toString()); result.put("level_sha256", sha(levelPath));
        result.put("player_path", playerPath.toString()); result.put("player_sha256", sha(playerPath));
        result.put("disk_player", player(diskPlayer)); result.put("integrated_player", player(integratedPlayer));
        result.put("both_inventory_tags_equal", diskPlayer.get("Inventory").equals(integratedPlayer.get("Inventory")));
        result.put("both_forge_data_equal", diskPlayer.getCompound("ForgeData").equals(integratedPlayer.getCompound("ForgeData")));
        result.put("legacy_item_snapshot", legacyIds); result.put("old_aliases_snbt", registry.getList("aliases", 10).toString());
        result.put("numeric_ids_not_future_preservation_assertion", true);
        result.put("native_world_or_event_executed", false); result.put("original_inputs_written", false);
        result.put("native_acceptance", false);
        Files.writeString(out, new GsonBuilder().setPrettyPrinting().create().toJson(result) + "\n", StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE);
        System.out.println("Read native NBT input; no world/player construction or input writes");
    }
}
