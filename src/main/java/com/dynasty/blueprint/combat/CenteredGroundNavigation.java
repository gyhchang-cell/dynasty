package com.dynasty.blueprint.combat;

import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.navigation.GroundPathNavigation;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/** Keeps Forge's normal pathfinding, adding only an exact-waypoint arrival fallback. */
public final class CenteredGroundNavigation extends GroundPathNavigation {
    public CenteredGroundNavigation(Mob mob, Level level) {
        super(mob, level);
    }

    @Override protected void followThePath() {
        if (path == null || path.isDone()) return;
        Vec3 next = path.getNextEntityPos(mob);
        // Forge 47's arrival check uses (width + 1) / 2, whereas MoveControl's target
        // uses floor(width + 1) / 2. With width .95F at an exact block centre the
        // former exceeds its own tolerance by 2.98e-8: the mob never leaves node 0.
        // Only consume a node already physically reached; do not loosen clearance,
        // path reachability, corner tests or the entity's real collision dimensions.
        if (mob.position().distanceToSqr(next) <= 1.0e-6) {
            path.advance();
            if (path.isDone()) return;
        }
        super.followThePath();
    }
}
