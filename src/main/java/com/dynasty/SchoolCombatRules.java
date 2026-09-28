package com.dynasty;

/** Pure, tick-based rules shared by the server and the bounded regression tests. */
final class SchoolCombatRules {
    static final int GUARD_TICKS = 40, GUARD_COOLDOWN = 120, EDICT_COOLDOWN = 160;
    static final int EDICT_CHARGE = 40, EDICT_WINDOW = 80, MARK_WINDOW = 160, EDICT_LIMIT = 8;
    static final double EDICT_RADIUS = 5, STATIONARY_DISTANCE_SQUARED = 0.0144;

    private SchoolCombatRules() { }

    static boolean fullAttack(float strength) { return Float.isFinite(strength) && strength >= 0.9F; }
    static boolean within(long now, long then, int window) { return now >= then && now - then <= window; }
    static int combo(int previous, boolean sameTarget, long elapsed, int window, float strength) {
        if (!fullAttack(strength)) return 0;
        return sameTarget && elapsed >= 0 && elapsed <= window ? Math.min(3, previous + 1) : 1;
    }
    static int counterWindow(boolean mirror) { return mirror ? 120 : 60; }
    static int comboWindow(boolean tassel) { return tassel ? 100 : 60; }
    static int edictDuration(boolean boss, boolean seal) { return boss ? (seal ? 40 : 20) : (seal ? 100 : 60); }
}
