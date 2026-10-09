package com.dynasty.dungeon;

import net.minecraft.core.BlockPos;
import java.util.ArrayList;
import java.util.List;

/** Authored vault geometry, shared by placement and the bounded room hazard. */
public final class ChenshaVaultLayout {
    private ChenshaVaultLayout() {}

    public static double moatRadius(int x, int z) {
        double dx=(x-31.5)/23.5, dz=(z-15.5)/13.5;
        return dx*dx+dz*dz;
    }

    public static boolean moatCell(int x, int z) {
        double radius=moatRadius(x,z);
        // The southern crossing is part of the main route, not a damage tile.
        return radius>.55&&radius<.8&&!(x>=30&&x<=34&&z>=22);
    }

    public static int daisHeight(int x, int z) {
        if(x<24||x>39||z<6||z>25||moatRadius(x,z)>=.55)return 0;
        return Math.max(0,Math.min(9,10-(int)Math.floor(Math.max(Math.abs(x-31.5)/1.5,Math.abs(z-15.5)))));
    }

    public static int roofHeight(int x, int z) {
        return 8+(int)(9*Math.sqrt(Math.max(0,1-moatRadius(x,z))));
    }

    public static List<BlockPos> constellationOffsets() {
        var points=new ArrayList<BlockPos>(28);
        for(int ring=0;ring<2;ring++) {
            int count=ring==0?16:12;
            double rx=ring==0?17:10, rz=ring==0?9:6;
            for(int index=0;index<count;index++) {
                double angle=2*Math.PI*(index+.25)/count;
                int x=(int)Math.round(31.5+rx*Math.cos(angle));
                int z=(int)Math.round(15.5+rz*Math.sin(angle));
                points.add(new BlockPos(x,roofHeight(x,z),z));
            }
        }
        return List.copyOf(points);
    }
}
