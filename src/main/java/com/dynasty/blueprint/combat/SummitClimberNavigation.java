package com.dynasty.blueprint.combat;

import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.navigation.WallClimberNavigation;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/** Coordinate destinations need the same wall fallback as vanilla's entity destinations.
 * Keep driving to the actual standing centre, not the lower block corner. */
public final class SummitClimberNavigation extends WallClimberNavigation {
    private Vec3 summit;
    private double climbSpeed;
    public SummitClimberNavigation(Mob mob, Level level) { super(mob, level); }
    @Override public boolean moveTo(double x, double y, double z, double speed) {
        boolean routed = super.moveTo(x, y, z, speed);
        summit = new Vec3(x, y, z);
        climbSpeed = speed;
        return routed || summit != null;
    }
    @Override public void stop() { super.stop(); summit = null; }
    @Override public void tick() {
        super.tick();
        if (summit == null) return;
        double horizontal = new Vec3(mob.getX(), summit.y, mob.getZ()).distanceToSqr(summit);
        if (horizontal < .025 && Math.abs(mob.getY() - summit.y) < .15 && mob.onGround()) {
            summit = null;
        } else if (isDone()) {
            mob.getMoveControl().setWantedPosition(summit.x, summit.y, summit.z, climbSpeed);
        }
    }
    @Override protected void followThePath() {
        if (path != null && !path.isDone() && mob.position().distanceToSqr(path.getNextEntityPos(mob)) <= 1.0e-6) {
            path.advance();
            if (path.isDone()) return;
        }
        super.followThePath();
    }
}
