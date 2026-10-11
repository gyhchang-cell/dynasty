package com.dynasty.dungeon;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/** One finite forward jet. The ray starts outside the solid nozzle mouth. */
public final class DungeonVentGeometry {
    public static Vec3 mouth(BlockPos pos,Direction facing){
        return Vec3.atCenterOf(pos).add(facing.getStepX()*.51,.15,facing.getStepZ()*.51);
    }
    public static AABB jet(BlockPos pos,Direction facing){
        var from=mouth(pos,facing);var to=from.add(facing.getStepX()*3,0,facing.getStepZ()*3);
        double sideX=facing.getAxis()==Direction.Axis.Z?.5:0,sideZ=facing.getAxis()==Direction.Axis.X?.5:0;
        return new AABB(Math.min(from.x,to.x)-sideX,pos.getY()+.2,Math.min(from.z,to.z)-sideZ,
            Math.max(from.x,to.x)+sideX,pos.getY()+1.8,Math.max(from.z,to.z)+sideZ);
    }
    private DungeonVentGeometry(){}
}
