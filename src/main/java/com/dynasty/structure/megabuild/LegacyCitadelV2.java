package com.dynasty.structure.megabuild;
import static com.dynasty.structure.megabuild.Blueprint.Kind.*;

/** Inhabited courtyard city. One foundation layer, no solid stacked platforms. */
public final class LegacyCitadelV2 {
    public static final int SIZE=176, HEIGHT=56;
    private final Blueprint bp=new Blueprint(SIZE,HEIGHT,SIZE);
    public final int[] gate={87,1,7},mainHallDoor={87,1,78},vault={87,1,112};
    public LegacyCitadelV2(long seed){build();}
    public Blueprint blueprint(){return bp;}
    private void build(){
        bp.box(4,0,4,171,0,171,PLATFORM);
        for(int i=0;i<3;i++)bp.hollowBox(5+i,1,5+i,170-i,14,170-i,WALL);
        for(int i=0;i<5;i++)bp.hollowBox(4+i,14,4+i,171-i,14,171-i,FLOOR);
        for(int v=4;v<=171;v+=3)for(int j=0;j<2;j++){
            bp.set(v,15,4+j,WALL);bp.set(v,15,170+j,WALL);
            bp.set(4+j,15,v,WALL);bp.set(170+j,15,v,WALL);
        }
        int n=0;
        for(int x:new int[]{13,45,105,137})for(int z:new int[]{20,67,119})
            hall(bp,x,z,x+25,z+32,0,(x==13||x==137)&&(z==20||z==119)?4:3,n++);
        hall(bp,73,78,101,115,0,5,12);
        bp.hollowBox(81,1,107,94,5,114,WALL);
        bp.doorway(86,1,107,89,3,107);
        bp.set(83,1,112,RICH_CHEST);bp.set(92,1,112,RICH_CHEST);
        bp.box(76,6,3,99,6,13,FLOOR);
        bp.hollowBox(76,7,3,99,11,13,WOOD);
        roof(bp,74,1,101,15,12);
        for(int x:new int[]{76,99})bp.box(x,1,4,x,6,12,DARK_WOOD);
        bp.doorway(82,1,3,93,5,14);
        bp.box(82,0,0,93,0,175,FLOOR);
        for(int z:new int[]{17,64,116,156})bp.box(9,0,z,166,0,z+2,FLOOR);
        for(int z=18;z<165;z+=12)for(int x:new int[]{80,95}){
            if(z>=76&&z<=116)continue;
            bp.box(x,1,z,x,3,z,DARK_WOOD);bp.set(x,4,z,LANTERN);
        }
        for(int x:new int[]{9,163}){
            bp.stairs(x,1,145,14,3,STAIR_S);
            bp.box(x,14,159,x+2,14,168,FLOOR);
        }
        bp.box(75,0,127,99,0,150,FLOOR);
        for(int x=76;x<100;x+=4)for(int z=128;z<150;z+=4)
            bp.set(x,1,z,(x+z)%3==0?ORE_IRON:ORE_COPPER);
        bp.set(87,1,152,CHEST);
    }
    /** Continuous internal stairs, open windows, pitched roof, usable rooms. */
    static void hall(Blueprint b,int x0,int z0,int x1,int z1,int y,int floors,int theme){
        int top=y+floors*7;
        b.box(x0,y,z0,x1,top,z1,AIR);
        b.hollowBox(x0,y+1,z0,x1,top-1,z1,WALL);
        for(int f=0;f<floors;f++){
            int fy=y+f*7;
            b.box(x0,fy,z0,x1,fy,z1,FLOOR);
            for(int z=z0+4;z<z1-2;z+=6){
                b.doorway(x0,fy+2,z,x0,fy+4,z+2);
                b.doorway(x1,fy+2,z,x1,fy+4,z+2);
            }
            for(int x=x0+7;x<x1-3;x+=6){
                b.doorway(x,fy+2,z0,x+2,fy+4,z0);
                b.doorway(x,fy+2,z1,x+2,fy+4,z1);
            }
            for(int z=z0+13;z<z1-2;z+=4){
                b.set(x0+2,fy+1,z,theme%3==0?BOOKSHELF:theme%3==1?FURNACE:BARREL);
                b.set(x1-2,fy+1,z,WOOD);
            }
            b.set(x1-3,fy+1,z1-3,f==floors-1?RICH_CHEST:CHEST);
            for(int x:new int[]{x0+6,x1-6})b.set(x,fy+5,z1-5,LANTERN);
            // Intermediate eaves and timber belts break up the tall masonry faces.
            b.hollowBox(x0,fy+6,z0,x1,fy+6,z1,WOOD);
            if(f>0)b.hollowBox(x0-1,fy,z0-1,x1+1,fy,z1+1,ROOF);
        }
        for(int f=0;f<floors-1;f++){
            int fy=y+f*7;
            b.box(x0+3,fy+1,z0+3,x0+5,fy+10,z0+10,AIR);
            b.stairs(x0+3,fy+1,z0+3,7,3,STAIR_S);
        }
        for(int x:new int[]{x0,x1})for(int z:new int[]{z0,z1})b.box(x,y+1,z,x,top-1,z,DARK_WOOD);
        int mid=(x0+x1)/2;
        b.doorway(mid-1,y+1,z0,mid+2,y+4,z0);
        roof(b,x0-2,z0-2,x1+2,z1+2,top);
    }
    static void roof(Blueprint b,int x0,int z0,int x1,int z1,int y){
        int layers=(Math.min(x1-x0,z1-z0))/2;
        for(int i=0;i<layers;i++){
            b.hollowBox(x0+i,y+i,z0+i,x1-i,y+i,z1-i,ROOF);
            if(i==layers-1)b.box(x0+i,y+i,z0+i,x1-i,y+i,z1-i,ROOF);
        }
        for(int x:new int[]{x0,x1})for(int z:new int[]{z0,z1})b.set(x,y+1,z,COPPER);
    }
    public static void main(String[] args){
        var city=new LegacyCitadelV2(0);var b=city.blueprint();
        System.out.println("Citadel: "+b.solidCount()+" "+b.countByCategory());
        if(!b.walkable(city.gate,city.mainHallDoor)||!b.walkable(city.mainHallDoor,city.vault))throw new AssertionError("Main route blocked");
        for(int i=0;i<4;i++)if(b.rotate(i).solidCount()!=b.solidCount())throw new AssertionError("Rotation count");
        for(int x:new int[]{13,45,105,137})for(int z:new int[]{20,67,119})
            if(!b.walkable(city.gate,new int[]{x+12,15,z+16}))throw new AssertionError("Upper floor unreachable: "+x+","+z);
        System.out.println("Entry, vault, twelve third floors and four rotations PASS");
    }
}
