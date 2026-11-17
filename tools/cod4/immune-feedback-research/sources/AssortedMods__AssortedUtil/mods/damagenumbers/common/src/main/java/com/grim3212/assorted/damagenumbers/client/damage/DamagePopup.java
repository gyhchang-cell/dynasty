package com.grim3212.assorted.damagenumbers.client.damage;

import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;

import java.util.Locale;

/** A number thrown up off a creature that falls, bounces once or twice and fades, the way RPG Damage's did. */
public class DamagePopup {

    private static final double GRAVITY = 0.03D;
    private static final double DRAG = 0.98D;
    private static final double BOUNCE = -0.6D;

    final FormattedCharSequence text;
    final float offset;
    final int color;
    final int lifetime;
    private final double floor;

    double x;
    double y;
    double z;
    double lastX;
    double lastY;
    double lastZ;
    private double motionX;
    private double motionY;
    private double motionZ;
    int age;

    public DamagePopup(FormattedCharSequence text, float offset, int color, int lifetime, double x, double y, double z, double floor, RandomSource random) {
        this.text = text;
        this.offset = offset;
        this.color = color;
        this.lifetime = lifetime;
        this.floor = floor;
        this.x = this.lastX = x;
        this.y = this.lastY = y;
        this.z = this.lastZ = z;
        this.motionX = (random.nextDouble() - 0.5D) * 0.2D;
        this.motionY = 0.15D + random.nextDouble() * 0.15D;
        this.motionZ = (random.nextDouble() - 0.5D) * 0.2D;
    }

    public int color() {
        return this.color;
    }

    /** False once it has faded out. */
    public boolean tick() {
        this.lastX = this.x;
        this.lastY = this.y;
        this.lastZ = this.z;
        this.x += this.motionX;
        this.y += this.motionY;
        this.z += this.motionZ;
        this.motionY -= GRAVITY;
        this.motionX *= DRAG;
        this.motionY *= DRAG;
        this.motionZ *= DRAG;
        if (this.y < this.floor) {
            this.y = this.floor;
            this.motionY *= BOUNCE;
            this.motionX *= 0.6D;
            this.motionZ *= 0.6D;
        }

        return ++this.age < this.lifetime;
    }

    /** Solid for the first half of its life, then fading out. */
    public int alpha(float partialTick) {
        float left = 1.0F - (this.age + partialTick) / this.lifetime;
        return (int) (Mth.clamp(left * 2.0F, 0.0F, 1.0F) * 255.0F);
    }

    /** Whole numbers stay whole; half hearts and the like get one decimal. */
    public static String amount(float value) {
        return Math.abs(value - Math.round(value)) < 0.05F ? Integer.toString(Math.round(value)) : String.format(Locale.ROOT, "%.1f", value);
    }
}
