package com.dynasty;

/** Dependency-free assertions; compile with the actual production SchoolCombatRules.java. */
public final class SchoolCombatRulesTest {
    private static int checks;
    private static void check(boolean value) { checks++; if (!value) throw new AssertionError("check " + checks); }
    public static void main(String[] args) {
        check(!SchoolCombatRules.fullAttack(Float.NaN));
        check(!SchoolCombatRules.fullAttack(Float.POSITIVE_INFINITY));
        check(!SchoolCombatRules.fullAttack(.899F));
        check(SchoolCombatRules.fullAttack(.9F));
        for (int window : new int[]{60, 100}) {
            for (int elapsed = -5; elapsed <= 180; elapsed++) {
                for (int previous = 0; previous <= 3; previous++) {
                    int result = SchoolCombatRules.combo(previous, true, elapsed, window, 1F);
                    check(result == (elapsed >= 0 && elapsed <= window ? Math.min(3, previous + 1) : 1));
                    check(SchoolCombatRules.combo(previous, false, elapsed, window, 1F) == 1);
                    check(SchoolCombatRules.combo(previous, true, elapsed, window, .5F) == 0);
                }
            }
        }
        check(SchoolCombatRules.combo(0, false, 0, 60, 1) == 1);
        check(SchoolCombatRules.combo(1, true, 60, 60, 1) == 2);
        check(SchoolCombatRules.combo(2, true, 60, 60, 1) == 3);
        check(SchoolCombatRules.within(260, 100, 160));
        check(!SchoolCombatRules.within(261, 100, 160));
        check(!SchoolCombatRules.within(99, 100, 160));
        check(SchoolCombatRules.counterWindow(false) == 60 && SchoolCombatRules.counterWindow(true) == 120);
        check(SchoolCombatRules.comboWindow(false) == 60 && SchoolCombatRules.comboWindow(true) == 100);
        check(SchoolCombatRules.edictDuration(false, false) == 60 && SchoolCombatRules.edictDuration(false, true) == 100);
        check(SchoolCombatRules.edictDuration(true, false) == 20 && SchoolCombatRules.edictDuration(true, true) == 40);
        check(SchoolCombatRules.EDICT_LIMIT == 8 && SchoolCombatRules.EDICT_RADIUS == 5);
        System.out.println("SchoolCombatRules: " + checks + " assertions passed");
    }
}
