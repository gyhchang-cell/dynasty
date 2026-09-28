package com.dynasty.structure.megabuild;
import static com.dynasty.structure.megabuild.Blueprint.Kind.*;

/** Inhabited courtyard city. One foundation layer, no solid stacked platforms. */
public final class LegacyCitadelV3 {
    public static final int SIZE=176, HEIGHT=56;
    private final Blueprint bp=new Blueprint(SIZE,HEIGHT,SIZE);
    static final int[][] HALLS={{15,30,42,57,5},{47,14,73,42,4},{97,12,130,38,4},{137,39,165,69,5},{12,77,41,110,5},{47,58,67,85,3},{110,52,132,81,3},{139,88,167,116,4},{22,125,51,157,4},{59,130,88,166,4},{100,132,129,163,5},{140,128,164,151,3}};
    public final int[] gate={87,1,7},mainHallDoor={87,1,78},vault={87,1,112};
    public LegacyCitadelV3(long seed){build();}
    public Blueprint blueprint(){return bp;}
    private void build(){
        // Chamfered terraces, staggered districts and open gardens, not a square enclosure.
        for(int x=4;x<172;x++)for(int z=4;z<172;z++){
            if(x+z<36 || (175-x)+z<30 || x+(175-z)<32 || (175-x)+(175-z)<38)continue;
            bp.set(x,0,z,PLATFORM);
        }
        int n=0;
        for(int[] h:HALLS)hall(bp,h[0],h[1],h[2],h[3],0,h[4],n++);
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
        // Sunken lotus pool and crossing bridge in the eastern garden.
        bp.box(108,0,91,133,0,117,WALL);
        bp.box(109,0,92,132,0,116,WATER);
        bp.box(118,1,90,121,1,118,WOOD);
        for(int z=92;z<117;z+=4){bp.set(117,2,z,DARK_WOOD);bp.set(122,2,z,DARK_WOOD);}
        bp.stairs(118,1,89,1,4,STAIR_S);
        bp.stairs(118,1,119,1,4,STAIR_N);
        // Raised connecting gallery between the west towers.
        bp.box(42,7,34,47,7,37,WOOD);
        bp.box(42,8,34,47,8,34,DARK_WOOD);bp.box(42,8,37,47,8,37,DARK_WOOD);
        bp.doorway(42,8,35,42,10,36);bp.doorway(47,8,35,47,10,36);
        for(int[] p:new int[][]{{23,65},{60,105},{149,22},{151,163}}){
            int x=p[0],z=p[1];
            bp.box(x,1,z,x,5,z,LOG);bp.box(x-3,5,z-3,x+3,7,z+3,CROP);
            bp.box(x-2,8,z-2,x+2,8,z+2,CROP);
        }
        // Useful market/workshop stalls rather than empty decorative rooms.
        for(int i=0;i<4;i++){
            int x=47+i*7,z=119;
            bp.box(x,0,z,x+4,0,z+5,FLOOR);
            for(int dx:new int[]{0,4}){bp.box(x+dx,1,z,x+dx,4,z,LOG);bp.box(x+dx,1,z+5,x+dx,4,z+5,LOG);}
            bp.box(x-1,5,z-1,x+5,5,z+6,i%2==0?WOOD:ROOF);
            bp.set(x+1,1,z+3,new Blueprint.Kind[]{ANVIL,CRAFTING,BREWING,FURNACE}[i]);
            bp.set(x+3,1,z+3,BARREL);bp.set(x+2,4,z+2,LANTERN);
        }
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
        if(theme%3==1){
            // Long ridge / gabled workshop roof, distinct from the tower roofs.
            for(int i=0;i<=(x1-x0+4)/2;i++)
                for(int z=z0-2;z<=z1+2;z++){
                    b.set(x0-2+i,top+i,z,ROOF);b.set(x1+2-i,top+i,z,ROOF);
                }
        }else if(theme%3==2){
            // Faceted octagonal dome: cuts the corners rather than another square pyramid.
            double cx=(x0+x1)/2.0,cz=(z0+z1)/2.0;
            double rx=(x1-x0)/2.0+2,rz=(z1-z0)/2.0+2;
            for(int x=x0-2;x<=x1+2;x++)for(int z=z0-2;z<=z1+2;z++){
                double dx=Math.abs(x-cx)/rx,dz=Math.abs(z-cz)/rz;
                double r=Math.max(Math.max(dx,dz),(dx+dz)/1.45);
                if(r<=1.01)b.set(x,top+(int)(10*Math.sqrt(Math.max(0,1-r*r))),z,ROOF);
            }
            b.set((int)cx,top+11,(int)cz,COPPER);
        }else roof(b,x0-2,z0-2,x1+2,z1+2,top);
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
        var city=new LegacyCitadelV3(0);var b=city.blueprint();
        System.out.println("Citadel: "+b.solidCount()+" "+b.countByCategory());
        if(!b.walkable(city.gate,city.mainHallDoor)||!b.walkable(city.mainHallDoor,city.vault))throw new AssertionError("Main route blocked");
        for(int i=0;i<4;i++)if(b.rotate(i).solidCount()!=b.solidCount())throw new AssertionError("Rotation count");
        for(int[] h:HALLS)
            if(!b.walkable(city.gate,new int[]{h[0]+12,15,h[1]+16}))throw new AssertionError("Upper floor unreachable: "+h[0]+","+h[1]);
        System.out.println("Entry, vault, twelve third floors and four rotations PASS");
    }
}
