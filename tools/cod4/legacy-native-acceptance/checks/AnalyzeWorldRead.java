package com.dynasty.legacyqa;

import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.nbt.TagParser;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;

/** Headless typed-NBT comparison only; never loads a registry, world or player. */
public final class AnalyzeWorldRead {
    private static ListTag inventory(String snbt) throws Exception {
        return TagParser.parseTag("{Inventory:" + snbt + "}").getList("Inventory", Tag.TAG_COMPOUND);
    }
    private static Map<Byte, CompoundTag> slots(ListTag list) {
        Map<Byte, CompoundTag> result = new LinkedHashMap<>();
        for (Tag t : list) {
            CompoundTag item = (CompoundTag) t;
            if (!item.contains("Slot", Tag.TAG_BYTE) || !item.contains("Count", Tag.TAG_BYTE)
                    || !item.contains("id", Tag.TAG_STRING) || item.getByte("Count") <= 0
                    || result.put(item.getByte("Slot"), item) != null) throw new IllegalArgumentException("Invalid/duplicate inventory slot");
        }
        return result;
    }
    static Map<String, Object> compare(JsonObject input, JsonObject capture) throws Exception {
        JsonObject before = input.getAsJsonObject("disk_player");
        CompoundTag oldData = TagParser.parseTag(before.get("forge_data_snbt").getAsString());
        CompoundTag newData = TagParser.parseTag(capture.get("forge_data_snbt").getAsString());
        if (!oldData.getAllKeys().equals(Set.of("dynasty_merit", "dynasty_rank", "dynasty_loyalty", "dq_p_18"))
                || oldData.getAllKeys().stream().anyMatch(k -> !oldData.contains(k, Tag.TAG_INT)))
            throw new IllegalArgumentException("Exact four-field historical input required; empty/synthetic input is not evidence");
        var fields = new ArrayList<Object>();
        boolean fieldsEqual = true;
        for (String key : oldData.getAllKeys().stream().sorted().toList()) {
            Tag oldValue = oldData.get(key), newValue = newData.get(key);
            boolean equal = oldValue.equals(newValue);
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("key", key); row.put("old_type", oldValue.getId()); row.put("old_snbt", oldValue.toString());
            row.put("new_type", newValue == null ? null : newValue.getId()); row.put("new_snbt", newValue == null ? null : newValue.toString());
            row.put("exact_typed_value_equal", equal); fields.add(row); fieldsEqual &= equal;
        }
        Map<Byte, CompoundTag> oldSlots = slots(inventory(before.get("inventory_snbt").getAsString()));
        Map<Byte, CompoundTag> newSlots = slots(inventory(capture.get("inventory_snbt").getAsString()));
        if (oldSlots.size() != 12 || oldSlots.get((byte) 4) == null
                || !oldSlots.get((byte) 4).getString("id").equals("dynasty:quest_ledger")
                || oldSlots.get((byte) 4).getByte("Count") != 1) throw new IllegalArgumentException("Actual twelve historical stacks required");
        var stackRows = new ArrayList<Object>();
        boolean stacksEqual = true;
        for (var entry : oldSlots.entrySet()) {
            CompoundTag old = entry.getValue(), expected = old.copy(), actual = newSlots.get(entry.getKey());
            if (old.getString("id").equals("dynasty:quest_ledger")) expected.putString("id", "ftbquests:book");
            boolean equal = expected.equals(actual);
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("slot", entry.getKey()); row.put("old_snbt", old.toString()); row.put("expected_snbt", expected.toString());
            row.put("actual_snbt", actual == null ? null : actual.toString()); row.put("exact_expected_stack_equal", equal);
            row.put("historical_tag_present", old.contains("tag")); row.put("historical_forge_caps_present", old.contains("ForgeCaps"));
            stackRows.add(row); stacksEqual &= equal;
        }
        var additions = new ArrayList<Object>();
        boolean onlyFirstManual = true;
        int manualCount = 0;
        for (var entry : newSlots.entrySet()) if (!oldSlots.containsKey(entry.getKey())) {
            CompoundTag stack = entry.getValue();
            additions.add(Map.of("slot", entry.getKey(), "snbt", stack.toString()));
            CompoundTag expectedManual = new CompoundTag();
            expectedManual.putString("id", "dynasty:dynasty_manual"); expectedManual.putByte("Count", (byte) 1);
            expectedManual.putByte("Slot", entry.getKey());
            onlyFirstManual &= stack.equals(expectedManual);
            if (stack.getString("id").equals("dynasty:dynasty_manual")) manualCount += stack.getByte("Count");
        }
        boolean firstManualExplained = !oldData.contains("dynasty_manual_given")
                && newData.contains("dynasty_manual_given", Tag.TAG_BYTE) && newData.getByte("dynasty_manual_given") == 1
                && onlyFirstManual && manualCount == 1;
        Map<String, String> aliases = new LinkedHashMap<>();
        for (var value : capture.getAsJsonArray("active_alias_lookups")) {
            var row = value.getAsJsonObject();
            if (aliases.put(row.get("old_name").getAsString(), row.get("resolved_canonical").getAsString()) != null)
                throw new IllegalArgumentException("Duplicate captured alias");
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("status", "DESCRIPTIVE_LIVE_CAPTURE_COMPARISON_NOT_OVERALL_ACCEPTANCE");
        result.put("historical_fields", fields); result.put("historical_field_count", oldData.getAllKeys().size());
        result.put("all_historical_fields_exact", fieldsEqual); result.put("new_field_keys", newData.getAllKeys().stream().filter(k -> !oldData.contains(k)).sorted().toList());
        Map<String, Object> addedFields = new LinkedHashMap<>();
        for (String key : newData.getAllKeys().stream().filter(k -> !oldData.contains(k)).sorted().toList()) {
            Tag value = newData.get(key);
            addedFields.put(key, Map.of("native_type_id", value.getId(), "snbt", value.toString(), "change_explained", false));
        }
        result.put("new_fields_described_not_automatically_explained", addedFields);
        result.put("historical_inventory", stackRows); result.put("historical_stack_count", oldSlots.size());
        result.put("all_historical_stacks_exact_after_expected_quest_alias", stacksEqual);
        result.put("additional_stacks", additions); result.put("first_manual_addition_explained_by_existing_handler", firstManualExplained);
        result.put("quest_alias_resolves_ftb_book", "ftbquests:book".equals(aliases.get("dynasty:quest_ledger")));
        result.put("healing_alias_resolves_protection_only", "dynasty:vajra_talisman".equals(aliases.get("dynasty:healing_talisman")));
        result.put("historical_healing_stack_present", oldSlots.values().stream().anyMatch(s -> s.getString("id").equals("dynasty:healing_talisman")));
        result.put("native_acceptance", false); result.put("save_reopen_verified", false); result.put("clone_c2s_verified", false);
        return result;
    }
    public static void main(String[] args) throws Exception {
        JsonObject input = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        JsonObject capture = JsonParser.parseString(Files.readString(Path.of(args[1]))).getAsJsonObject();
        if (!capture.get("status").getAsString().equals("NATIVE_WORLD_READ_CAPTURED_COMPARISON_AND_SAVE_REOPEN_PENDING")
                || !capture.get("uuid").getAsString().equals("380df991-f603-344c-a090-369bad2a924a")
                || !capture.get("candidate_sha256").getAsString().equals("e5a78244082214ab5fd76eb35bbb42151e3ec7bd8bc13afee3bc58ea4fe3a669"))
            throw new IllegalArgumentException("Wrong native capture context");
        Files.writeString(Path.of(args[2]), new GsonBuilder().setPrettyPrinting().create().toJson(compare(input, capture)) + "\n",
                StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE);
    }
}
