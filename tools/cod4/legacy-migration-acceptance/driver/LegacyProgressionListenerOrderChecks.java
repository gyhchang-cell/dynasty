package com.dynasty;

import net.minecraft.nbt.CompoundTag;

/** Models the two reviewed whole-container listeners; does not fire Forge events. */
public final class LegacyProgressionListenerOrderChecks {
    private static int checks;
    private static void require(boolean value, String message) {
        checks++;
        if (!value) throw new AssertionError(message);
    }
    private static void state(CompoundTag tag, String key, int state) {
        if (state == 1) tag.putBoolean(key, false);
        if (state == 2) tag.putBoolean(key, true);
        if (state == 3) tag.putString(key, "true");
    }
    public static void main(String[] args) {
        String[] bosses = {"dragon_emperor", "undead_first_emperor", "nine_heaven_general", "dragon_king",
                "rebel_general", "eunuch_mastermind", "phoenix", "qilin", "nian_beast", "nine_tailed_fox"};
        int[][] orders = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
        int cases = 0;
        for (String boss : bosses) for (int root = 0; root < 4; root++)
            for (int nested = 0; nested < 4; nested++) for (int[] order : orders) {
                String key = "dynasty_firstkill_" + boss;
                CompoundTag old = new CompoundTag(), persisted = new CompoundTag(), next = new CompoundTag();
                state(old, key, root); state(persisted, key, nested);
                persisted.putString("other_owner", "preserve");
                old.put("PlayerPersisted", persisted);
                old.putLong("dynasty_merit_kill_window", 1700000000000L);
                old.putInt("dynasty_merit_kill_earned", 120);
                CompoundTag before = old.copy();
                next.put("PlayerPersisted", persisted); // native initial alias
                next.putString("new_owner", "preserve");
                for (int listener : order) {
                    if (listener == 0) LegacyPlayerProgression.copyAuditedRoot(old, next);
                    else next.put("PlayerPersisted", old.getCompound("PlayerPersisted").copy());
                }
                boolean expected = root == 2 || nested == 2;
                require(next.getBoolean(key) == expected, "first-kill result depends on listener order: " + key);
                require(old.equals(before), "old player data mutated: " + key);
                require(next.getCompound("PlayerPersisted").equals(persisted), "nested owner changed");
                require(next.getString("new_owner").equals("preserve"), "unrelated new owner lost");
                require(next.getLong("dynasty_merit_kill_window") == 1700000000000L
                        && next.getInt("dynasty_merit_kill_earned") == 120, "valid budget reset");
                CompoundTag once = next.copy();
                LegacyPlayerProgression.copyAuditedRoot(old, next);
                require(next.equals(once), "repeated migration changed result");
                cases++;
            }
        System.out.println("PASS " + checks + " real-NBT assertions across " + cases
                + " modeled listener-order cases; no actual Forge dispatch/player/world/runtime credit");
    }
}
