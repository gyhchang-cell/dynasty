package com.dynasty.legacyqa;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.TagParser;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;

/** Synthetic checks of the analysis tool, not live remap/save/Clone acceptance. */
public final class AnalysisChecks {
    private static int checks;
    private static void check(boolean value, String label) {
        if (!value) throw new AssertionError(label);
        checks++;
    }
    private static ListTag inventory(JsonObject value) throws Exception {
        return TagParser.parseTag("{Inventory:" + value.get("inventory_snbt").getAsString() + "}").getList("Inventory", 10);
    }
    private static JsonObject fixture(JsonObject input) throws Exception {
        var before = input.getAsJsonObject("disk_player");
        CompoundTag root = TagParser.parseTag(before.get("forge_data_snbt").getAsString());
        root.putBoolean("dynasty_manual_given", true);
        ListTag list = inventory(before);
        for (var t : list) {
            var stack = (CompoundTag) t;
            if (stack.getString("id").equals("dynasty:quest_ledger")) stack.putString("id", "ftbquests:book");
        }
        list.add(TagParser.parseTag("{id:\"dynasty:dynasty_manual\",Count:1b,Slot:12b}"));
        JsonObject capture = new JsonObject();
        capture.addProperty("inventory_snbt", list.toString()); capture.addProperty("forge_data_snbt", root.toString());
        capture.add("active_alias_lookups", JsonParser.parseString("[{\"old_name\":\"dynasty:quest_ledger\",\"resolved_canonical\":\"ftbquests:book\"},{\"old_name\":\"dynasty:healing_talisman\",\"resolved_canonical\":\"dynasty:vajra_talisman\"}]"));
        return capture;
    }
    private static Map<String, Object> analyze(JsonObject input, JsonObject capture) throws Exception {
        return AnalyzeWorldRead.compare(input, capture);
    }
    public static void main(String[] args) throws Exception {
        JsonObject input = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        var capture = fixture(input);
        var good = analyze(input, capture);
        check(Boolean.TRUE.equals(good.get("all_historical_fields_exact")), "four original facts retained");
        check(Boolean.TRUE.equals(good.get("all_historical_stacks_exact_after_expected_quest_alias")), "slot/count/item identity preserved");
        check(Boolean.TRUE.equals(good.get("first_manual_addition_explained_by_existing_handler")), "one legitimate first manual");
        check(Boolean.FALSE.equals(good.get("native_acceptance")) && Boolean.FALSE.equals(good.get("save_reopen_verified")), "fixture cannot pass native/save");
        check(good.get("historical_field_count").equals(4) && good.get("historical_stack_count").equals(12), "no107-field coverage inflation");
        check(Boolean.FALSE.equals(good.get("historical_healing_stack_present")), "registry alias is not an owned healing stack");
        for (byte bad : new byte[]{2, -1}) {
            var malformed = fixture(input);
            CompoundTag malformedData = TagParser.parseTag(malformed.get("forge_data_snbt").getAsString());
            malformedData.putByte("dynasty_manual_given", bad);
            malformed.addProperty("forge_data_snbt", malformedData.toString());
            check(Boolean.FALSE.equals(analyze(input, malformed).get("first_manual_addition_explained_by_existing_handler")), "noncanonical true byte cannot be explained by putBoolean(true)");
        }
        var changed = fixture(input);
        CompoundTag data = TagParser.parseTag(changed.get("forge_data_snbt").getAsString());
        data.remove("dynasty_merit"); changed.addProperty("forge_data_snbt", data.toString());
        check(Boolean.FALSE.equals(analyze(input, changed).get("all_historical_fields_exact")), "missing merit detected");
        data.putInt("dynasty_merit", 280); data.putShort("dynasty_rank", (short) 2); changed.addProperty("forge_data_snbt", data.toString());
        check(Boolean.FALSE.equals(analyze(input, changed).get("all_historical_fields_exact")), "equal numeric value wrong type detected");
        changed = fixture(input); ListTag list = inventory(changed);
        for (var t : list) if (((CompoundTag) t).getByte("Slot") == 4) ((CompoundTag) t).putByte("Count", (byte) 2);
        changed.addProperty("inventory_snbt", list.toString());
        check(Boolean.FALSE.equals(analyze(input, changed).get("all_historical_stacks_exact_after_expected_quest_alias")), "book count duplication detected");
        changed = fixture(input); list = inventory(changed);
        for (var t : list) if (((CompoundTag) t).getByte("Slot") == 4) ((CompoundTag) t).putString("id", "dynasty:dynasty_guide");
        changed.addProperty("inventory_snbt", list.toString());
        check(Boolean.FALSE.equals(analyze(input, changed).get("all_historical_stacks_exact_after_expected_quest_alias")), "guide cannot impersonate installed FTB book");
        changed = fixture(input); list = inventory(changed); var first = list.remove(0); list.add(first);
        changed.addProperty("inventory_snbt", list.toString());
        check(Boolean.TRUE.equals(analyze(input, changed).get("all_historical_stacks_exact_after_expected_quest_alias")), "list order does not change native Slot identity");
        changed = fixture(input); list = inventory(changed); list.add(TagParser.parseTag("{id:\"dynasty:dynasty_manual\",Count:1b,Slot:13b}"));
        changed.addProperty("inventory_snbt", list.toString());
        check(Boolean.FALSE.equals(analyze(input, changed).get("first_manual_addition_explained_by_existing_handler")), "repeated manual not excused");
        changed = fixture(input); list = inventory(changed); list.add(TagParser.parseTag("{id:\"minecraft:stone\",Count:1b,Slot:13b}"));
        changed.addProperty("inventory_snbt", list.toString());
        check(Boolean.FALSE.equals(analyze(input, changed).get("first_manual_addition_explained_by_existing_handler")), "unrelated grant not excused");
        for (String extra : new String[]{"tag", "ForgeCaps"}) {
            changed = fixture(input); list = inventory(changed);
            for (var t : list) if (((CompoundTag) t).getByte("Slot") == 12) ((CompoundTag) t).put(extra, TagParser.parseTag("{unexpected:1b}"));
            changed.addProperty("inventory_snbt", list.toString());
            check(Boolean.FALSE.equals(analyze(input, changed).get("first_manual_addition_explained_by_existing_handler")), "unexplained new manual data not excused: " + extra);
            var artificialInput = input.deepCopy();
            var sourcePlayer = artificialInput.getAsJsonObject("disk_player");
            var historicalStacks = inventory(sourcePlayer);
            for (var t : historicalStacks) if (((CompoundTag) t).getByte("Slot") == 4) ((CompoundTag) t).put(extra, TagParser.parseTag("{fixture_only:1b}"));
            sourcePlayer.addProperty("inventory_snbt", historicalStacks.toString());
            changed = fixture(artificialInput);
            check(Boolean.TRUE.equals(analyze(artificialInput, changed).get("all_historical_stacks_exact_after_expected_quest_alias")), "synthetic custom book data retained: " + extra);
            list = inventory(changed);
            for (var t : list) if (((CompoundTag) t).getByte("Slot") == 4) ((CompoundTag) t).remove(extra);
            changed.addProperty("inventory_snbt", list.toString());
            check(Boolean.FALSE.equals(analyze(artificialInput, changed).get("all_historical_stacks_exact_after_expected_quest_alias")), "synthetic lost book data detected: " + extra);
        }
        for (String key : new String[]{"forge_data_snbt", "inventory_snbt"}) {
            var invalid = input.deepCopy(); invalid.getAsJsonObject("disk_player").addProperty(key, key.startsWith("forge") ? "{}" : "[]");
            try { analyze(invalid, fixture(input)); throw new AssertionError("Empty historical basis accepted: " + key); }
            catch (IllegalArgumentException expected) { checks++; }
        }
        changed = fixture(input); list = inventory(changed); list.add(list.get(0).copy()); changed.addProperty("inventory_snbt", list.toString());
        try { analyze(input, changed); throw new AssertionError("Duplicate native slot accepted"); }
        catch (IllegalArgumentException expected) { checks++; }
        System.out.println("PASS " + checks + " analysis-tool assertions; all captures synthetic; no world, registry, player or event");
    }
}
