package com.dynasty.structure.megabuild;
import static com.dynasty.structure.megabuild.Blueprint.Kind.*;

/** Inhabited courtyard city. One foundation layer, no solid stacked platforms. */
public final class TiangongCitadel {
    public static final int SIZE=176, HEIGHT=56;
    private final Blueprint bp=new Blueprint(SIZE,HEIGHT,SIZE);
    static final int[][] HALLS={{15,30,42,57,5},{47,14,73,42,4},{97,12,130,38,4},{137,39,165,69,5},{12,77,41,110,5},{47,58,67,85,3},{110,52,132,81,3},{139,88,167,116,4},{22,125,51,157,4},{59,130,88,166,4},{100,132,129,163,5},{140,128,164,151,3}};
    public final int[] gate={87,1,7},mainHallDoor={87,1,78},vault={87,1,112};
    public TiangongCitadel(long seed){build();PlayerCityEdits.apply(bp);enrich();}
    public Blueprint blueprint(){return bp;}
    final java.util.List<int[]> cages=new java.util.ArrayList<>();
    private void enrich(){
        for(int i=0;i<HALLS.length;i++){
            int[] h=HALLS[i];int x=h[2]-15,z=h[3]-15;
            encounter(x,0,z,i);
            if(i%2==0)encounter(x,7,z,i+1);
            // Distinct upper-floor destinations: library, smithy, apothecary, archive.
            for(int f=2;f<h[4];f++){
                int y=f*7;int cx=h[0]+10,cz=h[1]+12;
                for(int j=0;j<3;j++){
                    bp.box(cx+j*4,y+1,cz+5,cx+j*4+1,y+1,cz+6,WOOD);
                    bp.set(cx+j*4,y+2,cz+5,new Blueprint.Kind[]{BOOKSHELF,ANVIL,BREWING,CRAFTING}[i%4]);
                }
                bp.set(h[2]-5,y+1,h[1]+3,f==h[4]-1?RICH_CHEST:CHEST);
                // Paired red timber pilasters and carved base, not plain repeated grey walls.
                for(int px:new int[]{h[0]+7,h[2]-7}){
                    bp.box(px,y+1,h[1]-1,px,y+4,h[1]-1,RED_WOOD);
                    bp.set(px,y+1,h[1]-2,CHISELED);
                }
            }
        }
        // Central processional hall: colonnade, dais and a readable destination.
        for(int z=84;z<105;z+=5)for(int x:new int[]{79,95}){
            bp.box(x,1,z,x,5,z,RED_WOOD);bp.set(x,1,z,CHISELED);
        }
        bp.box(83,0,99,91,0,104,CHISELED);
        bp.box(84,1,102,90,1,104,WOOD);
        bp.stairs(85,1,101,1,5,STAIR_S);
        // Low curved colonnade follows the garden, leaving the central route open.
        for(int z=87;z<=121;z++){
            int x=134+(int)Math.round(3*Math.sin((z-87)*Math.PI/34));
            bp.box(x,0,z,x+3,0,z,FLOOR);bp.box(x-1,5,z,x+4,5,z,ROOF);
            if(z%5==0){bp.box(x,1,z,x,4,z,RED_WOOD);bp.box(x+3,1,z,x+3,4,z,RED_WOOD);}
        }
        pavilion();
    }
    private void pavilion(){
        // Open octagonal landmark breaks the skyline and the repeated rectilinear halls.
        int cx=87,cz=56;
        for(int dx=-17;dx<=17;dx++)for(int dz=-17;dz<=17;dz++){
            double r=Math.max(Math.max(Math.abs(dx),Math.abs(dz)),(Math.abs(dx)+Math.abs(dz))/1.42);
            if(r>17)continue;
            bp.set(cx+dx,0,cz+dz,r>15?CHISELED:FLOOR);
            if(r>=11)bp.set(cx+dx,7,cz+dz,WOOD);
            if(r>16)bp.set(cx+dx,8,cz+dz,DARK_WOOD);
            int ry=12+(int)((17-r)/3);
            bp.set(cx+dx,ry,cz+dz,ROOF);
        }
        for(int[] p:new int[][]{{-15,0},{15,0},{0,-15},{0,15},{-11,-11},{11,-11},{-11,11},{11,11}}){
            bp.box(cx+p[0],1,cz+p[1],cx+p[0],11,cz+p[1],RED_WOOD);
            bp.set(cx+p[0],1,cz+p[1],CHISELED);
            bp.set(cx+p[0],11,cz+p[1],COPPER);
        }
        // Keep the main north-south axis six blocks wide, columns stay to its side.
        for(int dz:new int[]{-15,15}){
            bp.box(cx,1,cz+dz,cx,5,cz+dz,AIR);
            for(int dx:new int[]{-4,4})bp.box(cx+dx,1,cz+dz,cx+dx,11,cz+dz,RED_WOOD);
        }
        bp.box(cx,18,cz,cx,20,cz,COPPER);
        bp.box(cx-14,1,cz-12,cx-12,10,cz-4,AIR);
        bp.stairs(cx-14,1,cz-12,7,3,STAIR_S);
        bp.set(cx+12,8,cz+2,RICH_CHEST);
        bp.set(cx-9,1,cz+8,BOOKSHELF);bp.set(cx-8,1,cz+8,BOOKSHELF);
        bp.set(cx+9,1,cz+8,CRAFTING);
    }
    private void encounter(int x,int y,int z,int theme){
        // 15x15 closed chamber with a dog-leg corridor. Only this room loses lights.
        bp.box(x,y+1,z,x+14,y+6,z+14,AIR);
        bp.box(x,y,z,x+14,y,z+14,FLOOR);
        bp.hollowBox(x,y+1,z,x+14,y+5,z+14,WALL);
        bp.box(x,y+6,z,x+14,y+6,z+14,FLOOR);
        bp.doorway(x+1,y+1,z,x+2,y+3,z);
        // Entrance light must go around this full-height baffle, not straight to cage.
        bp.box(x+4,y+1,z+1,x+4,y+5,z+9,CHISELED);
        bp.box(x+6,y+2,z,x+11,y+3,z,TINTED_GLASS);
        bp.set(x+10,y+2,z+10,theme%2==0?SPAWNER_ZOMBIE:SPAWNER_SKELETON);
        bp.set(x+12,y+1,z+12,RICH_CHEST);
        bp.set(x+7,y+1,z+12,CHEST);
        cages.add(new int[]{x+10,y+2,z+10});
    }
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
        // Tie the roof to a continuous ceiling, with structural cross-beams.
        b.box(x0,top-1,z0,x1,top-1,z1,WOOD);
        for(int px=x0+3;px<x1;px+=6)b.box(px,top-2,z0,px,top-2,z1,DARK_WOOD);
        if(theme%3==1){
            // Long ridge / gabled workshop roof, distinct from the tower roofs.
            for(int i=0;i<=(x1-x0+4)/2;i++)
                for(int z=z0-2;z<=z1+2;z++){
                    int ry=top+(i+1)/2;
                    b.set(x0-2+i,ry,z,ROOF);b.set(x1+2-i,ry,z,ROOF);
                    // Close triangular gables; no open attic ends.
                    if(z==z0||z==z1)for(int yy=top;yy<ry;yy++){
                        b.set(x0-2+i,yy,z,WOOD);b.set(x1+2-i,yy,z,WOOD);
                    }
                }
        }else if(theme%3==2){
            // Faceted octagonal dome: cuts the corners rather than another square pyramid.
            double cx=(x0+x1)/2.0,cz=(z0+z1)/2.0;
            double rx=(x1-x0)/2.0+2,rz=(z1-z0)/2.0+2;
            b.box(x0-2,top,z0-2,x1+2,top,z1+2,ROOF);
            for(int x=x0-2;x<=x1+2;x++)for(int z=z0-2;z<=z1+2;z++){
                double dx=Math.abs(x-cx)/rx,dz=Math.abs(z-cz)/rz;
                double r=Math.max(Math.max(dx,dz),(dx+dz)/1.45);
                if(r<=1.01)b.set(x,top+(int)(7*Math.sqrt(Math.max(0,1-r*r))),z,ROOF);
            }
            b.set((int)cx,top+8,(int)cz,COPPER);
        }else roof(b,x0-2,z0-2,x1+2,z1+2,top);
    }
    static void roof(Blueprint b,int x0,int z0,int x1,int z1,int y){
        int layers=(Math.min(x1-x0,z1-z0))/2;
        for(int i=0;i<layers;i++){
            int ry=y+(i+1)/2;
            b.hollowBox(x0+i,ry,z0+i,x1-i,ry,z1-i,ROOF);
            if(i==layers-1)b.box(x0+i,ry,z0+i,x1-i,ry,z1-i,ROOF);
        }
        for(int x:new int[]{x0,x1})for(int z:new int[]{z0,z1})b.set(x,y+1,z,COPPER);
    }
    public static void main(String[] args){
        var city=new TiangongCitadel(0);var b=city.blueprint();
        System.out.println("Citadel: "+b.solidCount()+" "+b.countByCategory());
        if(!b.walkable(city.gate,city.mainHallDoor)||!b.walkable(city.mainHallDoor,city.vault))throw new AssertionError("Main route blocked");
        for(int i=0;i<4;i++)if(b.rotate(i).solidCount()!=b.solidCount())throw new AssertionError("Rotation count");
        for(int[] h:HALLS)
            if(!b.walkable(city.gate,new int[]{h[0]+12,15,h[1]+16}))throw new AssertionError("Upper floor unreachable: "+h[0]+","+h[1]);
        System.out.println("Entry, vault, twelve third floors and four rotations PASS");
    }
}
