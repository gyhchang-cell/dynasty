package com.dynasty.blueprint.combat;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import java.util.List;
import java.util.function.Predicate;

/** Bounded broad phase, then shape filtering. No world-wide entity searches. Units are blocks/degrees. */
public final class CombatGeometry {
    public enum Shape { SECTOR, STRIP, CIRCLE, CONE, RAY }
    private CombatGeometry() {}
    public static List<LivingEntity> query(ServerLevel level, Vec3 origin, Vec3 direction, Shape shape,
            double range, double width, double angle, double height, Predicate<LivingEntity> valid) {
        if (!safe(origin) || !safe(direction) || !Double.isFinite(range) || range < 0 || range > 64
                || !Double.isFinite(width) || width < 0 || width > 64 || !Double.isFinite(height) || height < 0 || height > 64
                || !Double.isFinite(angle) || angle < 0 || angle > 360)
            return List.of();
        double bound = shape == Shape.STRIP || shape == Shape.RAY ? range + width * .5 : range;
        var bounds = new AABB(origin.x-bound, origin.y-height, origin.z-bound, origin.x+bound, origin.y+height, origin.z+bound);
        return level.getEntitiesOfClass(LivingEntity.class, bounds, e -> e.isAlive() && !e.isSpectator() && valid.test(e)
                && contains(origin, direction, shape, range, width, angle, height, e.getBoundingBox()));
    }
    public static boolean contains(Vec3 origin, Vec3 direction, Shape shape, double range, double width,
            double angle, double height, AABB box) {
        if (box.maxY < origin.y - height || box.minY > origin.y + height) return false;
        Vec3 d = new Vec3(direction.x, 0, direction.z).normalize();
        Vec3 centre = box.getCenter();
        double dx = centre.x-origin.x, dz = centre.z-origin.z;
        double padding = Math.min(1.5, Math.max(box.getXsize(), box.getZsize()) * .5);
        double along = dx*d.x + dz*d.z, across = Math.abs(dx*d.z - dz*d.x);
        double radius = Math.sqrt(dx*dx + dz*dz);
        return switch (shape) {
            case CIRCLE -> radius <= range+padding;
            case STRIP, RAY -> along >= -padding && along <= range+padding && across <= width*.5+padding;
            case SECTOR -> radius <= range+padding && (radius <= padding || along / radius >= Math.cos(Math.toRadians(angle*.5)));
            // Range always means radial reach, not an unbounded cone's axial length.
            case CONE -> centre.distanceTo(origin) <= range+padding
                    && (centre.distanceTo(origin) <= padding || centre.subtract(origin).normalize().dot(direction.normalize())
                    >= Math.cos(Math.toRadians(angle*.5)));
        };
    }
    public static boolean inFront(Vec3 position, Vec3 forward, Vec3 source, double degrees) {
        Vec3 offset = source.subtract(position).multiply(1,0,1).normalize();
        return offset.lengthSqr() > 1.0e-8 && forward.multiply(1,0,1).normalize().dot(offset) >= Math.cos(Math.toRadians(degrees*.5));
    }
    private static boolean safe(Vec3 v) { return Double.isFinite(v.lengthSqr()); }
}
