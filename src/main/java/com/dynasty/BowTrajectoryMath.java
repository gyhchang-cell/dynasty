package com.dynasty;

import net.minecraft.world.phys.Vec3;

/** Shared, side-effect-free flight constraints and the vanilla arrow renderer's orientation. */
public final class BowTrajectoryMath {
    public static final double SEEK_RADIUS = 6.0D;
    public static final double SEEK_CORRIDOR_RADIUS = 2.25D;
    public static final double SEEK_CONE_COS = Math.cos(Math.toRadians(30.0D));
    public static final double TURN_RADIANS_PER_TICK = Math.toRadians(4.0D);

    private BowTrajectoryMath() {}

    /** Assistance stays near the fired ray, never attracts an arrow to a target behind it. */
    public static boolean insideAssistCorridor(Vec3 delta, Vec3 velocity, Vec3 launchDirection) {
        double distanceSq = delta.lengthSqr();
        if (distanceSq < 1.0E-8D || distanceSq > SEEK_RADIUS * SEEK_RADIUS
                || velocity.lengthSqr() < 0.04D || launchDirection.lengthSqr() < 1.0E-8D) return false;
        Vec3 launch = launchDirection.normalize();
        double along = delta.dot(launch);
        double lateralSq = Math.max(0, distanceSq - along * along);
        return delta.dot(velocity) > 0 && along / Math.sqrt(distanceSq) >= SEEK_CONE_COS
                && lateralSq <= SEEK_CORRIDOR_RADIUS * SEEK_CORRIDOR_RADIUS;
    }

    /** A bounded turn without changing speed, gravity or the vanilla ballistic integration. */
    public static Vec3 steer(Vec3 velocity, Vec3 targetDelta) {
        double speed = velocity.length();
        if (speed < 0.2D || targetDelta.lengthSqr() < 1.0E-8D) return velocity;
        Vec3 forward = velocity.scale(1.0D / speed);
        Vec3 desired = targetDelta.normalize();
        double dot = Math.max(-1, Math.min(1, forward.dot(desired)));
        if (dot <= 0) return velocity;
        double angle = Math.acos(dot);
        if (angle <= TURN_RADIANS_PER_TICK) return desired.scale(speed);
        Vec3 sideways = desired.subtract(forward.scale(dot)).normalize();
        return forward.scale(Math.cos(TURN_RADIANS_PER_TICK))
                .add(sideways.scale(Math.sin(TURN_RADIANS_PER_TICK))).scale(speed);
    }

    /** ArrowRenderer uses interpolated yaw/pitch, not the already gravity-adjusted velocity. */
    public static Vec3 renderedDirection(float oldYaw, float yaw, float oldPitch, float pitch, float partial) {
        double y = Math.toRadians(oldYaw + (yaw - oldYaw) * partial);
        double p = Math.toRadians(oldPitch + (pitch - oldPitch) * partial);
        // Unlike the player's camera pitch, positive arrow pitch points upward.
        return new Vec3(Math.sin(y) * Math.cos(p), Math.sin(p), Math.cos(y) * Math.cos(p));
    }
}
