#!/usr/bin/env python3
"""Original Wangsi city geometry. Exports the same cuboids consumed in game; no JVM."""
import json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/blueprint-cod2/evidence/wangsi-20261018'
JAVA=ROOT/'src/main/java/com/dynasty/dungeon/WangsiArchitecture.java'
W,H,D=96,48,128
# Air is explicit: unassigned zero preserves terrain outside the authored envelope.
AIR,STONE,WHITE,WOOD,TILE,RED,LAMP,WATER,CHAIN,IRON=range(1,11)
PALETTE=['null','Blocks.AIR.defaultBlockState()','DungeonMasonryBlock.finish(0)',
 'DungeonMasonryBlock.finish(2)','Blocks.DARK_OAK_PLANKS.defaultBlockState()',
 'DungeonMasonryBlock.finish(1)','Blocks.RED_NETHER_BRICKS.defaultBlockState()',
 'Blocks.PEARLESCENT_FROGLIGHT.defaultBlockState()','Blocks.WATER.defaultBlockState()',
 'Blocks.CHAIN.defaultBlockState()','Blocks.IRON_BARS.defaultBlockState()']

def geometry():
    boxes=[]; group='cavern'
    def box(a,b,c,d,e,f,m):
        assert 0<=a<=d<W and 0<=b<=e<H and 0<=c<=f<D,(a,b,c,d,e,f)
        boxes.append({'group':group,'bounds':[a,b,c,d,e,f],'palette':m})
    def rim(x,y,z,xx,zz,m):
        box(x,y,z,xx,y,z,m);box(x,y,zz,xx,y,zz,m)
        box(x,y,z,x,y,zz,m);box(xx,y,z,xx,y,zz,m)
    # Finite enclosed excavation: 48 independent chunk columns, no fluid oceans.
    box(1,4,1,94,42,126,STONE);box(2,5,2,93,41,125,AIR)
    box(2,5,2,93,12,66,STONE)
    # Entrance at the terrain datum, then a reversible 28-riser stair into the city.
    group='yin_yang_gate'
    box(42,13,1,54,47,8,STONE);box(45,41,0,51,45,8,AIR)
    for z in range(8,37):
        y=40-(z-8)
        box(45,5,z,51,y,z,STONE);box(45,y+1,z,51,min(47,y+5),z,AIR)
        for x in (44,52): box(x,y+1,z,x,y+1,z,WHITE)
    box(43,46,0,53,46,7,TILE);box(45,47,2,51,47,5,TILE)
    for x in (43,53):box(x,41,1,x,45,1,RED)
    box(45,44,1,51,44,1,WOOD)
    for x in (42,54):box(x,41,3,x,41,3,LAMP)
    # Market: eight occupied buildings and a broad cross street, rather than a corridor.
    houses=[]
    for z in (28,48):
        for x in (7,26,57,76):
            group=f'house_{x}_{z}';houses.append([x,z])
            box(x,13,z,x+12,20,z+12,WHITE);box(x+1,13,z+1,x+11,20,z+11,AIR)
            box(x+1,18,z+1,x+11,18,z+11,WOOD)
            # Central south door, upper balcony door and an internal staircase.
            box(x+5,13,z,x+7,16,z,AIR);box(x+5,19,z,x+7,20,z,AIR)
            box(x+4,18,z-2,x+8,18,z-1,WOOD)
            for k in range(6):
                box(x+3,13,z+2+k,x+4,13+k,z+2+k,WOOD)
                box(x+3,14+k,z+2+k,x+4,16+k,z+2+k,AIR)
            for xx in (x,x+12):
                for zz in (z,z+12):box(xx,13,zz,xx,20,zz,WOOD)
            for xx in (x+3,x+9):box(xx,15,z,xx,16,z,IRON)
            # Dark tiled stepped gable; contrasting stepped horse-head walls.
            for dx in range(-1,14):
                ry=21+min(max(dx,0),max(12-dx,0))//2
                box(x+dx,ry,z-1,x+dx,ry,z+13,TILE)
                for zz in (z,z+12):box(x+dx,20,zz,x+dx,ry,zz,WHITE)
            box(x+5,25,z,x+7,25,z+12,TILE)
            for xx in (x-1,x+13):
                for zz in (z-1,z+13):box(xx,22,zz,xx,22,zz,TILE)
            box(x+5,19,z,x+7,20,z,AIR)
            for xx in (x+3,x+9):
                box(xx,19,z-1,xx,20,z-1,CHAIN);box(xx,18,z-1,xx,18,z-1,LAMP)
            # Furnished ground floor; central walking lane remains three blocks wide.
            box(x+8,13,z+7,x+10,13,z+8,WOOD)
            box(x+9,14,z+7,x+9,14,z+7,RED)
            box(x+8,13,z+10,x+11,13,z+11,WHITE)
    group='rooftop_routes'
    # Ridge-height links, with an ascent from each balcony to the accessible roof.
    for x,z in houses:
        for k in range(7):
            box(x+5,18+k,z-3-k,x+7,18+k,z-3-k,WOOD)
        box(x+5,24,z-10,x+11,24,z-9,WOOD)
        # Ridge reaches y25; one final riser, then an open landing on the roof.
        box(x+9,24,z-9,x+11,24,z+1,WOOD)
        box(x+5,25,z+1,x+11,25,z+3,TILE)
    # Roof links across each side street and between the two rows.
    for x in (12,31,62,81):box(x,25,39,x+2,25,48,WOOD)
    for x in (13,63):
        box(x,25,34,x+19,25,36,WOOD)
        box(x,25,54,x+19,25,56,WOOD)
    box(20,13,41,20,13,41,STONE)
    group='forget_river'
    # The red riverbed colours a finite, enclosed vanilla-water basin.
    box(3,5,67,92,7,84,RED);box(3,8,67,92,11,84,WATER)
    for z in (66,85):box(2,5,z,93,12,z,STONE)
    for x in (2,93):box(x,5,66,x,12,85,STONE)
    # Stone arch bridge: seven-wide dry deck, continuous one-block rises.
    for z in range(64,89):
        y=min(16,12+min(z-64,88-z))
        box(45,y-2,z,51,y,z,STONE)
        for x in (44,52):box(x,y,z,x,y+1,z,WHITE)
    # Supported abutments and an actually open arch under the middle span.
    for z in (65,83):box(44,5,z,52,13,z,STONE)
    for z in range(68,83):
        arch=8+round(6*math.sqrt(max(0,1-((z-75)/8)**2)))
        box(44,8,z,52,15,z,STONE)
        box(44,8,z,52,arch-1,z,AIR)
    # Water exits on both banks; no unavoidable swimming trap.
    for x in (8,86):
        for k in range(5):box(x,8,68+k,x+2,8+k,68+k,STONE)
        box(x,12,72,x+2,12,85,STONE)
    box(8,12,65,10,12,76,STONE)
    group='inner_court'
    box(20,5,86,76,16,119,STONE)
    for z in (86,119):box(20,17,z,76,21,z,WHITE)
    for x in (20,76):box(x,17,86,x,21,119,WHITE)
    # Front approach rises from bridge to the court's datum.
    for z in range(85,90):box(45,12,z,51,min(16,12+z-84),z,STONE)
    box(46,17,85,50,21,91,AIR)
    # Narrow enclosed guillotine passage, with side waiting niches.
    box(44,17,90,52,22,99,STONE);box(47,17,90,49,21,99,AIR)
    for z in (90,94,98):box(45,17,z,51,19,z,AIR)
    for z in (90,92,96):box(47,21,z,49,21,z,WOOD)
    # Entrance roof and fixed masonry crossbeam above the blade anchors.
    box(43,23,89,53,23,100,TILE);box(45,24,90,51,24,99,TILE)
    group='yanluo_hall'
    box(29,17,103,67,27,117,WHITE);box(30,17,104,66,26,116,AIR)
    box(44,17,103,52,23,104,AIR)
    for x in (32,64):
        for z in (104,108,112,116):
            box(x-1,17,z-1,x+1,17,z+1,STONE);box(x,18,z,x,26,z,RED)
            box(x-1,26,z-1,x+1,26,z+1,WOOD)
    for dz in range(-2,17):
        y=28+min(max(dz+1,0),max(15-dz,0))//2
        box(27,y,103+dz,69,y,103+dz,TILE)
    box(28,27,103,68,27,117,WOOD)
    for x in (27,69):
        for z in (101,119):box(x,29,z,x,29,z,TILE)
    box(42,17,113,54,18,116,STONE);box(46,19,115,50,20,116,WOOD)
    # Side doors and dry rear access are part of the authored route, not a sealed facade.
    for x in (29,67):box(x,17,109,x,20,111,AIR)
    box(46,17,117,50,20,119,AIR)
    group='pump_house'
    box(5,13,76,17,20,89,WHITE);box(6,13,77,16,19,88,AIR)
    box(4,21,75,18,21,90,TILE);box(6,22,76,16,22,89,TILE)
    box(8,13,76,10,16,77,AIR);box(8,12,73,10,12,89,STONE)
    box(12,13,82,15,16,86,WOOD);box(13,17,83,14,17,85,IRON)
    # Drain maintenance tunnel is dry and sealed from the bulk river. Custom gate
    # opens only its entrance: no hundreds-of-block fluid updates during gameplay.
    group='drain_shortcut'
    box(13,5,90,17,10,123,STONE);box(14,6,90,16,9,122,AIR)
    box(14,5,121,49,10,125,STONE);box(15,6,122,48,9,124,AIR)
    # Return staircase alongside the west court wall, climbs 11 blocks in 11 runs.
    for k in range(12):
        box(16,5,111-k,18,5+k,111-k,STONE)
        box(16,6+k,111-k,18,9+k,111-k,AIR)
    box(17,17,99,22,20,101,AIR);box(17,16,99,22,16,101,STONE)
    # A separate 54-source-cell sump, hydraulically isolated from the main river.
    # Two custom solid grates keep it contained until its controller finishes draining.
    box(13,5,93,17,10,100,STONE);box(14,6,94,16,8,99,WATER)
    for k in range(8):
        box(10,5,88+k,12,12-k,88+k,STONE)
        box(10,13-k,88+k,12,15-k,88+k,AIR)
    box(10,13,88,12,16,89,AIR)
    # Front and rear grates replace these wall cells during structure generation.
    group='river_dock'
    box(23,5,120,75,12,125,RED)
    box(40,13,120,56,16,125,STONE)
    for x in (40,56):box(x,17,121,x,20,121,WOOD);box(x,21,121,x,21,121,LAMP)
    # Roofs, courtyard and halls retain generous headroom beneath the cave ceiling.
    return boxes,houses

def outputs():
    boxes,houses=geometry()
    # A lazy bounded lookup avoids scanning every cuboid for every generated block.
    rows=['        {'+','.join(map(str,b['bounds']+[b['palette']]))+'}' for b in boxes]
    source='''package com.dynasty.dungeon;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
/** Generated by tools/blueprint/build_wangsi.py. Original finite city geometry. */
public final class WangsiArchitecture {
    public static final int WIDTH=96,HEIGHT=48,DEPTH=128;
    private static final int[][] BOXES={
'''+',\n'.join(rows)+'''
    };
    private static final class Cells {
        static final byte[] DATA=build();
        static byte[] build(){
            byte[] data=new byte[WIDTH*HEIGHT*DEPTH];
            for(int[] b:BOXES)for(int y=b[1];y<=b[4];y++)for(int z=b[2];z<=b[5];z++)
                for(int x=b[0];x<=b[3];x++)data[x+z*WIDTH+y*WIDTH*DEPTH]=(byte)b[6];
            return data;
        }
    }
    private static final class Palette {
        static final BlockState[] STATES={'''+','.join(PALETTE)+'''};
    }
    public static BlockState cell(int x,int y,int z){
        if(x<0||x>=WIDTH||y<0||y>=HEIGHT||z<0||z>=DEPTH)return null;
        return Palette.STATES[Byte.toUnsignedInt(Cells.DATA[x+z*WIDTH+y*WIDTH*DEPTH])];
    }
    private WangsiArchitecture(){}
}
'''
    return source,{'dimensions':[W,H,D],'palette':PALETTE,'boxes':boxes,'houses':houses}

if __name__=='__main__':
    source,data=outputs();DOC.mkdir(parents=True,exist_ok=True)
    JAVA.write_text(source);(DOC/'geometry.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(f'Wangsi: {len(data["boxes"])} authored cuboids, {len(data["houses"])} accessible houses')
