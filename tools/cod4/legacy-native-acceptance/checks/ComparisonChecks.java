package com.dynasty.legacyqa;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.TagParser;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

/** New probe's descriptive comparisons only. Never constructs a player, mod, event or game. */
public final class ComparisonChecks {
    private static int checks;
    private static void check(boolean value, String message) { checks++; if (!value) throw new AssertionError(message); }
    @SuppressWarnings("unchecked")
    private static Map<String, Object> compare(Method method, CompoundTag before, CompoundTag after) throws Exception {
        Map<String, Object> result = (Map<String, Object>) method.invoke(null, before, after);
        check(Boolean.FALSE.equals(result.get("overall_acceptance")), "Probe comparison must never certify runtime acceptance");
        return result;
    }
    public static void main(String[] args) throws Exception {
        CompoundTag fixture = TagParser.parseTag(Files.readString(Path.of(args[0])));
        Class<?> probe = Class.forName("com.dynasty.legacyqa.LegacyNativeQa");
        Field field = probe.getDeclaredField("fieldTypes"); field.setAccessible(true); field.set(null, fixture.copy());
        Method method = probe.getDeclaredMethod("compare", CompoundTag.class, CompoundTag.class); method.setAccessible(true);
        var empty = compare(method, new CompoundTag(), new CompoundTag());
        check(Boolean.FALSE.equals(empty.get("all107_valid_present")), "Empty evidence appears complete");
        check(((List<?>) empty.get("absent_root_keys")).size() == 107, "Missing fields not enumerated");
        var valid = compare(method, fixture, fixture.copy());
        check(Boolean.TRUE.equals(valid.get("all107_valid_present")), "Complete fixture not recognized");
        check(((List<?>) valid.get("differences")).isEmpty(), "Equal valid typed fields differ");
        var missing = fixture.copy(); missing.remove("dq_p_18");
        var reduced = compare(method, missing, fixture.copy());
        check(Boolean.FALSE.equals(reduced.get("all107_valid_present")), "Partial coverage appears complete");
        var lost = fixture.copy(); lost.remove("dq_p_18");
        check(((List<?>) compare(method, fixture, lost).get("differences")).contains("dq_p_18"), "Lost field not visible");
        var wrong = fixture.copy(); wrong.putLong("dynasty_merit", 1);
        var malformed = compare(method, wrong, wrong.copy());
        check(((List<?>) malformed.get("malformed_keys_excluded")).contains("dynasty_merit"), "Wrong numeric type coerced");
        check(Boolean.FALSE.equals(malformed.get("all107_valid_present")), "Malformed fixture counted as107 valid fields");
        var partialPair = fixture.copy(); partialPair.remove("dynasty_merit_kill_window");
        check(((List<?>) compare(method, partialPair, partialPair.copy()).get("malformed_keys_excluded")).contains("dynasty_merit_kill_earned"), "Partial economic pair admitted");
        var invalidUuid = fixture.copy(); invalidUuid.putIntArray("DynastyXuanniaoBlessing", new int[]{1, 2, 3});
        check(((List<?>) compare(method, invalidUuid, invalidUuid.copy()).get("malformed_keys_excluded")).contains("DynastyXuanniaoBlessing"), "Invalid UUID length admitted");
        String key = "dynasty_firstkill_dragon_emperor";
        for (int mode = 0; mode < 3; mode++) {
            var old = new CompoundTag(); var nested = new CompoundTag(); nested.putBoolean(key, true); old.put("PlayerPersisted", nested);
            if (mode == 1) old.putBoolean(key, false);
            if (mode == 2) old.putString(key, "malformed");
            var restored = new CompoundTag(); restored.putBoolean(key, true);
            var repaired = compare(method, old, restored);
            check(((List<?>) repaired.get("nested_true_firstkills")).contains(key), "Nested alias evidence absent");
            check(((List<?>) repaired.get("differences")).isEmpty(), "Correct nested alias repair marked different");
            check(((List<?>) compare(method, old, new CompoundTag()).get("differences")).contains(key), "Missing nested alias repair hidden");
        }
        var rootOnly = new CompoundTag(); rootOnly.putBoolean(key, true);
        check(((List<?>) compare(method, rootOnly, new CompoundTag()).get("differences")).contains(key), "Root true lost without detection");
        System.out.println("PASS " + checks + " QA-comparison-only assertions; 0 Forge events, players, worlds or native acceptance");
    }
}
