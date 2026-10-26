package local.mcmacro;

/** Tick-based movement phases; timing follows actual takeoff/landing, not wall time. */
public final class TellyPlan {
    private int airborne;
    private int grounded;
    public Frame tick(boolean onGround) {
        if (onGround) { airborne = 0; grounded++; }
        else { airborne++; grounded = 0; }
        boolean outbound = onGround || airborne <= 3;
        return new Frame(outbound, onGround, !outbound, airborne > 25 || grounded > 8);
    }
    public static float degreesPerCount(float sensitivity) {
        float f = Math.max(0, Math.min(1, sensitivity)) * 0.6F + 0.2F;
        return f * f * f * 8F * 0.15F;
    }
    public static float quantize(float angle, float origin, float sensitivity) {
        float step = degreesPerCount(sensitivity);
        return origin + Math.round((angle - origin) / step) * step;
    }
    public static float cardinal(float yaw) { return Math.round(yaw / 90F) * 90F; }
    public static final class Frame {
        public final boolean forward, jump, place, stalled;
        Frame(boolean forward, boolean jump, boolean place, boolean stalled) {
            this.forward = forward; this.jump = jump; this.place = place; this.stalled = stalled;
        }
    }
}
