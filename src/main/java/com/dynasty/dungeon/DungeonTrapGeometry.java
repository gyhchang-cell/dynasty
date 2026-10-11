package com.dynasty.dungeon;

import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.AABB;

/** Shared visible hammer dimensions and authoritative contact volume, in block units. */
public final class DungeonTrapGeometry {
    public static final double HAMMER_INSET=.05,HAMMER_WIDTH=.9,HAMMER_HEIGHT=.65;
    public static final double HAMMER_RAISED=2.6,HAMMER_CONTACT=1.02;
    public static double hammerY(int phase,float progress){
        double p=Mth.clamp(progress,0,1);
        return switch(phase){
            case 1 -> HAMMER_RAISED+Math.sin(p*Math.PI*6)*.03;
            case 2 -> HAMMER_CONTACT;
            case 3 -> HAMMER_CONTACT+(HAMMER_RAISED-HAMMER_CONTACT)*p;
            default -> HAMMER_RAISED;
        };
    }
    public static AABB hammerContact(BlockPos pos){
        return new AABB(pos.getX()+HAMMER_INSET,pos.getY()+HAMMER_CONTACT,pos.getZ()+HAMMER_INSET,
            pos.getX()+HAMMER_INSET+HAMMER_WIDTH,pos.getY()+HAMMER_CONTACT+HAMMER_HEIGHT,pos.getZ()+HAMMER_INSET+HAMMER_WIDTH);
    }
    public static AABB updraft(BlockPos pos){return new AABB(pos.above()).expandTowards(0,3,0);}
    private DungeonTrapGeometry(){}
}
