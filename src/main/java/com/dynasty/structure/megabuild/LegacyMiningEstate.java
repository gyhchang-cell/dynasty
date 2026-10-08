package com.dynasty.structure.megabuild;
import static com.dynasty.structure.megabuild.Blueprint.Kind.*;
/** Surface mine with ramped benches, working rooms and a public entrance. */
public final class LegacyMiningEstate {
    public static final int SIZE=96,HEIGHT=36;
    private final Blueprint bp=new Blueprint(SIZE,HEIGHT,SIZE);
    public LegacyMiningEstate(long seed){ this(seed, false); }
    public LegacyMiningEstate(long seed, boolean openQuarry){
        bp.box(4,0,4,91,0,91,PLATFORM);
        bp.hollowBox(4,1,4,91,7,91,WALL);
        bp.doorway(43,1,4,51,4,4);
        bp.box(43,0,0,51,0,91,FLOOR);
        LegacyCitadelV2.hall(bp,57,12,85,32,0,2,1);
        LegacyCitadelV2.hall(bp,59,42,85,61,0,2,2);
        LegacyCitadelV2.hall(bp,56,70,86,86,0,2,0);
        // Raised quarry benches are hollow underneath and reachable by stairs.
        for(int tier=0;tier<3;tier++){
            int y=tier*3;
            int z=14+tier*13;
            bp.box(10,y,z,38,y,z+10,FLOOR);
            if(tier>0){
                bp.hollowBox(10,1,z,38,y-1,z+10,WALL);
                bp.stairs(24,y-2,z-3,3,4,STAIR_S);
            }
            for(int x=12;x<=36;x+=4)for(int zz=z+3;zz<=z+8;zz+=4)
                bp.set(x,y+1,zz,tier==0?ORE_COPPER:tier==1?ORE_IRON:ORE_COAL);
        }
        // Layout 4 in main opened this route; older saves keep their original wall.
        if(openQuarry)bp.doorway(38,1,43,38,3,46);
        bp.set(12,1,65,CHEST);
        bp.set(36,1,65,RICH_CHEST);
        for(int x:new int[]{11,37})for(int z:new int[]{58,80}){
            bp.box(x,1,z,x,4,z,DARK_WOOD);bp.set(x,5,z,LANTERN);
        }
    }
    public Blueprint blueprint(){return bp;}
    public static void main(String[] args){
        var b=new LegacyMiningEstate(0).blueprint();
        System.out.println("Estate: "+b.solidCount()+" "+b.countByCategory());
        for(int[] end:new int[][]{{70,1,20},{72,8,50},{70,8,78},{25,7,47}})
            if(!b.walkable(new int[]{47,1,4},end))throw new AssertionError("Blocked estate route "+java.util.Arrays.toString(end));
        System.out.println("Estate entrance, upper rooms and quarry PASS");
    }
}
