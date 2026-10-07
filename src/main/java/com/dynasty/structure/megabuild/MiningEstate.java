package com.dynasty.structure.megabuild;

import static com.dynasty.structure.megabuild.Blueprint.Kind.*;

/** Mirrored solid quarry benches. Roads and stair headroom are excluded from the ore volume. */
public final class MiningEstate {
    public static final int SIZE=96, HEIGHT=36;
    private final Blueprint bp=new Blueprint(SIZE,HEIGHT,SIZE);
    public MiningEstate(long seed) {
        bp.box(4,0,4,91,0,91,PLATFORM);
        bp.hollowBox(4,1,4,91,7,91,WALL);
        bp.doorway(43,1,4,52,4,4);
        bp.box(43,0,0,52,0,91,FLOOR);
        var random=new java.util.Random(seed);
        for(int tier=0;tier<3;tier++) {
            int height=3+tier*3, z0=14+tier*18;
            for(int x=10;x<=38;x++)for(int z=z0;z<=z0+12;z++)for(int y=1;y<=height;y++) {
                var mineral=mineral(random.nextInt(100));
                bp.set(x,y,z,mineral); bp.set(95-x,y,z,mineral);
            }
            // Side access avoids putting a taller ramp through the previous bench.
            for(int step=0;step<height;step++)for(int x=39;x<=41;x++) {
                int z=z0+step;
                bp.box(x,1,z,x,step+1,z,FLOOR);
                bp.box(95-x,1,z,95-x,step+1,z,FLOOR);
            }
        }
        // The former southern hall becomes two equal stepped mineral mounds.
        for(int y=1;y<=6;y++)for(int x=10+y;x<=38-y;x++)for(int z=70+y;z<=87-y;z++) {
            var mineral=mineral(random.nextInt(100));
            bp.set(x,y,z,mineral); bp.set(95-x,y,z,mineral);
        }
        for(int x:new int[]{39,56})for(int z:new int[]{29,65})bp.set(x,1,z,MINING_CHEST);
        for(int x:new int[]{42,53})for(int z:new int[]{10,64,88}) {
            bp.box(x,1,z,x,3,z,DARK_WOOD); bp.set(x,4,z,LANTERN);
        }
    }
    private static Blueprint.Kind mineral(int n) {
        if(n<38)return RAW_IRON;
        if(n<68)return RAW_COPPER;
        if(n<75)return RAW_GOLD;
        if(n<82)return ORE_COAL;
        if(n<88)return ORE_IRON;
        if(n<93)return ORE_COPPER;
        if(n<96)return ORE_REDSTONE;
        if(n<98)return ORE_LAPIS;
        return n==98?ORE_GOLD:ORE_DIAMOND;
    }
    public Blueprint blueprint(){return bp;}
    public static void main(String[] args) {
        var b=new MiningEstate(0).blueprint();
        for(int[] end:new int[][]{{47,1,90},{40,1,65},{55,1,65},{24,4,16},{71,10,59}})
            if(!b.walkable(new int[]{47,1,4},end))throw new AssertionError("Blocked quarry route "+java.util.Arrays.toString(end));
        System.out.println("Solid mirrored quarry routes PASS");
    }
}
