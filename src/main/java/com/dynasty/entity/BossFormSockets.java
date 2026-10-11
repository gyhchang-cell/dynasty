package com.dynasty.entity;

import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.Vec3;

/** World-space mount positions for the furnace golem's original right-hand throw. */
public final class BossFormSockets {
    private BossFormSockets() {}
    public static Vec3 throwOrigin(Mob actor) { return hand(actor,actor.position(),-30); }
    public static Vec3 hand(Mob actor,Vec3 position,double yokeAngle) {
        Vec3 forward=Vec3.directionFromRotation(0,actor.yBodyRot);
        Vec3 right=new Vec3(forward.z,0,-forward.x);
        double a=Math.toRadians(yokeAngle);
        // Authored yoke pivot (22,48,2), hammer centre (43,13,-18), 16 units/block.
        double y=(48-35*Math.cos(a)-20*Math.sin(a))/16;
        double z=-(2+35*Math.sin(a)-20*Math.cos(a))/16;
        return position.add(right.scale(43.0/16)).add(forward.scale(z)).add(0,y,0);
    }
}
