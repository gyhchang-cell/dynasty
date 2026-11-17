package com.dynasty.blueprint.combat;

import com.dynasty.blueprint.TemplateMob;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.ai.control.MoveControl;
import net.minecraft.world.phys.Vec3;

/** Follow ordinary reachable paths while presenting the actual frontal shield toward its enemy. */
public final class ShieldCoverMoveControl extends MoveControl {
    private final TemplateMob shield;
    private boolean remappedLastTick;
    private float pathYaw;

    public ShieldCoverMoveControl(TemplateMob shield) {
        super(shield);
        this.shield = shield;
    }

    @Override public void tick() {
        boolean covering = shield.isCoveringBackline() || shield.kind()==TemplateMob.Kind.CHILD && shield.skillId()==0
                && shield.isAlive() && shield.getTarget()!=null && shield.getTarget().isAlive();
        if (remappedLastTick) {
            // MOVE_TO/WAIT do not clear xxa in vanilla. Never leave our previous lateral input
            // behind when the path ends, the target dies, or another goal takes over.
            shield.setXxa(0);
            // Keep vanilla's own turn progression independent of the guard-facing presentation.
            // Otherwise a path directly behind the enemy resets the 90-degree turn every tick.
            if (covering) shield.setYRot(pathYaw);
        }
        remappedLastTick = false;
        super.tick(); // Retains path speed, waypoint handling, terrain collision and jump control.
        var enemy = shield.getTarget();
        if (!covering || enemy == null || !enemy.isAlive()) return;
        Vec3 towardEnemy = enemy.position().subtract(shield.position()).multiply(1, 0, 1);
        if (towardEnemy.lengthSqr() < 1.0e-8) return;

        pathYaw = shield.getYRot();
        float pathRadians = pathYaw * Mth.DEG_TO_RAD;
        float pathSin = Mth.sin(pathRadians), pathCos = Mth.cos(pathRadians);
        // This is Entity.getInputVector's horizontal transform, without changing its magnitude.
        double worldX = shield.xxa * pathCos - shield.zza * pathSin;
        double worldZ = shield.zza * pathCos + shield.xxa * pathSin;
        float guardYaw = (float)(Mth.atan2(towardEnemy.z, towardEnemy.x) * Mth.RAD_TO_DEG) - 90F;
        float guardRadians = guardYaw * Mth.DEG_TO_RAD;
        float guardSin = Mth.sin(guardRadians), guardCos = Mth.cos(guardRadians);
        shield.setXxa((float)(worldX * guardCos + worldZ * guardSin));
        shield.setZza((float)(worldZ * guardCos - worldX * guardSin));
        // hurt() tests getLookAngle (entity yaw), so a visual-only body/head turn is insufficient.
        shield.setYRot(guardYaw);
        shield.setYBodyRot(guardYaw);
        shield.setYHeadRot(guardYaw);
        remappedLastTick = true;
    }
}
