package com.dynasty.ritual;

/** Geometry shared by visible warnings and damage. No hidden full-room damage. */
public final class ZhenyuanAttackPattern {
    private ZhenyuanAttackPattern() {}
    public static final int WARNING_TICKS = 36;
    public static int phase(double ratio) { return ratio <= .30 ? 2 : ratio <= .65 ? 1 : 0; }
    public static double ringRadius(int phase) { return 9 + Math.max(0, Math.min(2, phase)) * 3; }
    public static boolean hit(int pattern, int phase, double x, double z) {
        if (!Double.isFinite(x) || !Double.isFinite(z)) return false;
        double r = Math.hypot(x, z);
        return switch (pattern) {
            case 0 -> Math.abs(r - ringRadius(phase)) <= 1.6;
            case 1 -> r <= 4.5;
            case 2 -> r <= 22 && (Math.abs(x) <= 1.35 || Math.abs(z) <= 1.35);
            default -> false;
        };
    }
}
