#!/usr/bin/env python3
"""Author Chensha masonry, supported chain bridges and the corresponding resources.

No Minecraft/Java process is launched. Cuboids below are the production geometry;
the review manifest is exported from these same cuboids, not a concept rendering.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JAVA = ROOT / 'src/main/java/com/dynasty/dungeon/ChenshaArchitecture.java'
ASSETS = ROOT / 'src/main/resources/assets/dynasty'
DOC = ROOT / 'docs/blueprint-cod2/evidence/architecture-20261018'
# Palette 1..8 are protected masonry finishes 0..7. Zero leaves the base untouched.
STONE, EARTH, JADE, BRONZE, PATINA, BASALT, CARVED, SAND = range(1, 9)
CHAIN_X, CHAIN_Y, CHAIN_Z = 9, 10, 11
AIR = 12
FINISHES = ['deepslate_bricks', 'black_terracotta', 'quartz_bricks', 'cut_copper',
            'oxidized_cut_copper', 'polished_basalt', 'chiseled_polished_blackstone', 'sandstone']
ROOMS = [
    ('兵器耳室', '左右铜架与端墙兵器台', 4, 32),
    ('封石前殿', '对称断龙石基座', 24, 32),
    ('礼器耳室', '三座高低错落的礼器台', 44, 32),
    ('西渠玄室', '水渠两侧干廊、抱柱铜箍', 4, 52),
    ('水银封喉殿', '兽眼背墙铜框与封门立柱', 24, 52),
    ('东渠玄室', '排水壁龛与低矮水口', 44, 52),
    ('简牍藏室', '层叠贴墙书架形石龛', 4, 72),
    ('九棺前廊', '台阶两侧礼制柱列', 24, 72),
    ('殉葬后室', '棺床、残壁与暗室前的回折通路', 44, 72),
]


def geometry():
    boxes = []
    group = 'entrance'

    def box(x0, y0, z0, x1, y1, z1, material):
        assert 0 <= x0 <= x1 < 64 and 0 <= z0 <= z1 < 96 and 0 <= y0 <= y1 < 80
        boxes.append({'group': group, 'bounds': [x0, y0, z0, x1, y1, z1], 'palette': material})

    def rim(x0, y, z0, x1, z1, material):
        box(x0,y,z0,x1,y,z0,material); box(x0,y,z1,x1,y,z1,material)
        box(x0,y,z0,x0,y,z1,material); box(x1,y,z0,x1,y,z1,material)

    # The lower parts remain buried: two unequal surviving que tower fragments.
    for x, top in [(18,79),(45,77)]:
        box(x-2,65,1,x+2,72,5,JADE)
        box(x-1,73,2,x+1,top-1,4,JADE)
        box(x-2,top,1,x+1,top,5,JADE)
        box(x,74,1,x,top-1,1,CARVED)
    # A bronze jamb and lintel are continuous, their rivets are attached inlays.
    for x in (29,35):
        box(x,72,0,x,77,1,BRONZE)
        for y in (73,75,77): box(x,y,0,x,y,0,PATINA)
    box(29,77,0,35,77,1,BRONZE)
    box(28,78,0,36,78,2,CARVED)
    # Sand-capped roof is a low remnant of the mound, with its torn front lip.
    box(25,79,0,39,79,11,SAND)
    box(25,79,0,28,79,1,EARTH)
    box(36,79,0,39,79,2,EARTH)
    for x in (25,39): box(x,73,2,x,78,10,EARTH)
    for z in (2,5,8): box(26,78,z,38,78,z,BASALT)

    group = 'shendao'
    # 6-block tall, two-block wide piers and grounded feet; capitals join beams.
    for x in (8,14,45,55):
        for z in (37,55,70,85):
            box(x-1,49,z-1,x+1,49,z+1,STONE)
            box(x,50,z,x,54,z,BASALT)
            box(x-1,55,z-1,x+1,55,z+1,CARVED)
            box(x-1,56,z-1,x+1,56,z+1,STONE)
        box(x,56,37,x,56,85,BASALT)
    for z in (37,55,70,85):
        box(8,56,z,14,56,z,BASALT); box(45,56,z,55,56,z,BASALT)
    for y, mat in ((49,EARTH),(55,CARVED),(56,BASALT)):
        rim(4,y,33,59,88,mat)
    # Paired burial bays with recessed fronts, rather than isolated cuboids.
    for z in (58,66,74,82):
        for x in (5,56):
            box(x,49,z,x+2,49,z+3,STONE)
            box(x,50,z+1,x+1,50,z+2,EARTH)
            box(x,51,z+1,x+1,51,z+2,CARVED)
    # Coping follows the rim but never fills the 20-block horse well.
    rim(17,48,40,25,48,CARVED)
    for z in range(35,88,4):
        box(27,48,z,28,48,z,JADE); box(37,48,z,38,48,z,JADE)

    for index, (name, motif, cx, cz) in enumerate(ROOMS):
        group = f'chamber_{index+1}'
        rim(cx,32,cz,cx+15,cz+15,CARVED)
        # Continuous perimeter wall skirting; preserve authored bridge openings.
        for x in (cx+1,cx+14):
            for z in (cz+1,cz+14):
                box(x,25,z,x,30,z,BASALT)
                box(x,31,z,x,32,z,BRONZE if index==4 else CARVED)
        # Ceiling coffers are above all bridge portals and player head space.
        for dx in (4,11): box(cx+dx,32,cz+1,cx+dx,32,cz+14,BASALT)
        box(cx+1,32,cz+7,cx+14,32,cz+7,BASALT)
        if index == 0:  # Weapon racks placed against side walls, open axial aisle.
            for x in (cx+1,cx+13):
                box(x,25,cz+3,x+1,25,cz+11,BRONZE)
                for z in (cz+3,cz+7,cz+11): box(x,26,z,x,28,z,PATINA)
                box(x,29,cz+3,x,29,cz+11,BRONZE)
        elif index == 1:
            for x in (cx+2,cx+11):
                box(x,25,cz+3,x+2,25,cz+5,JADE)
                box(x+1,26,cz+4,x+1,28,cz+4,CARVED)
        elif index == 2:
            for n in range(3):
                x=cx+3+n*4
                box(x,25,cz+2,x+1,25+n,cz+3,STONE)
                box(x,26+n,cz+2,x+1,26+n,cz+3,BRONZE)
        elif index == 3:
            for z in (cz+3,cz+11):
                for x in (cx+1,cx+14): box(x,28,z,x,29,z,PATINA)
                box(cx+1,31,z,cx+14,31,z,BASALT)
        elif index == 4:
            # Relief frame lies on the north wall, clear of all three eye targets.
            box(cx+2,29,cz,cx+13,29,cz,BRONZE)
            for x in (cx+2,cx+13): box(x,25,cz,x,29,cz,BRONZE)
        elif index == 5:
            for z in (cz+3,cz+7,cz+11):
                box(cx+14,25,z,cx+14,26,z+1,PATINA)
                box(cx+15,27,z,cx+15,28,z+1,CARVED)
        elif index == 6:
            for y in (25,27,29):
                box(cx+1,y,cz+2,cx+1,y,cz+12,EARTH)
                box(cx+2,y,cz+2,cx+2,y,cz+12,CARVED)
            for z in (cz+2,cz+7,cz+12): box(cx+1,25,z,cx+1,29,z,BASALT)
        elif index == 7:
            for x in (cx+2,cx+12):
                for z in (cz+3,cz+11):
                    box(x,25,z,x,29,z,CARVED)
                    box(x,30,z,x,31,z,JADE)
        else:
            for x,z in ((cx+3,cz+3),(cx+10,cz+3),(cx+3,cz+10)):
                box(x,25,z,x+2,25,z+3,STONE)
                box(x,26,z+1,x+2,26,z+2,EARTH)

    group='bridges'
    # Four-block deck, two-block unobstructed centre. Side chains touch anchors,
    # vertical droppers touch the deck; no chain sheet floating above the room.
    for start in (20,40):
        for z in (38,58,78):
            box(start,24,z,start+3,24,z+3,BRONZE)
            for edge in (z,z+3):
                for x in (start-1,start+4): box(x,24,edge,x,28,edge,PATINA)
                box(start,27,edge,start+3,27,edge,CHAIN_X)
                for x in (start,start+3): box(x,25,edge,x,26,edge,CHAIN_Y)
    # The first north/south gap is occupied by the descent; do not dress it as a flat bridge.
    for start in (68,):
        box(30,24,start,33,24,start+3,BRONZE)
        # The x=29..35 stair connector has final precedence where it crosses.
        for edge in (30,33):
            # Anchors are on the bridge, clear of the timed gate at z=67.
            for z in (start,start+3): box(edge,24,z,edge,28,z,PATINA)
            box(edge,27,start+1,edge,27,start+2,CHAIN_Z)
            for z in (start+1,start+2): box(edge,25,z,edge,26,z,CHAIN_Y)
    # The centre of the northern gap is the stair to the imperial vault. Put
    # traversable bridges at its flanks; a flat centre deck would plug that stair.
    for x0 in (8,50):
        box(x0,24,48,x0+3,24,51,BRONZE)
        for z in (47,52): box(x0,25,z,x0+3,28,z,AIR)
        for x in (x0,x0+3):
            for z in (48,51): box(x,24,z,x,28,z,PATINA)
            box(x,27,49,x,27,50,CHAIN_Z)
            for z in (49,50): box(x,25,z,x,26,z,CHAIN_Y)
    return boxes


def outputs():
    boxes = geometry()
    rows='\n'.join('        {'+','.join(map(str,b['bounds']+[b['palette']]))+'},' for b in boxes)
    java='''package com.dynasty.dungeon;

import net.minecraft.core.Direction;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.ChainBlock;
import net.minecraft.world.level.block.state.BlockState;

/** Generated by tools/blueprint/build_chensha_architecture.py; edit its cuboids. */
public final class ChenshaArchitecture {
    private ChenshaArchitecture() {}
    // Fixed 64x96x80 piece space; lookup is O(1), with no per-cell allocation.
    private static final short[][] BOXES = {
ROWS
    };
    private static final byte[] CELLS = rasterize();
    private static byte[] rasterize() {
        byte[] cells = new byte[64*96*80];
        for (short[] b : BOXES)
            for (int y=b[1]; y<=b[4]; y++) for (int z=b[2]; z<=b[5]; z++) for (int x=b[0]; x<=b[3]; x++)
                cells[(y*96+z)*64+x]=(byte)b[6];
        return cells;
    }
    // Lazy until world generation, after Forge registry initialization.
    private static final class Palette {
        static final BlockState[] STATES = make();
        private static BlockState[] make() {
            BlockState[] states = new BlockState[13];
            for (int i=1;i<=8;i++) states[i]=DungeonMasonryBlock.finish(i-1);
            states[9]=Blocks.CHAIN.defaultBlockState().setValue(ChainBlock.AXIS,Direction.Axis.X);
            states[10]=Blocks.CHAIN.defaultBlockState();
            states[11]=Blocks.CHAIN.defaultBlockState().setValue(ChainBlock.AXIS,Direction.Axis.Z);
            states[12]=Blocks.AIR.defaultBlockState();
            return states;
        }
    }
    public static BlockState decoration(int x, int y, int z) {
        if(x<0||x>=64||y<0||y>=80||z<0||z>=96)return null;
        return Palette.STATES[CELLS[(y*96+z)*64+x]];
    }
    /** Low fractured mound; subsequent room and connector carving takes precedence. */
    public static BlockState mound(int x, int y, int z) {
        if(x<11||x>53||z<0||z>31||y<52||y>79)return null;
        double radius=Math.max(Math.abs(x-32.0-(z-13)*.18)/21,Math.abs(z-13.0)/18);
        if(radius>1)return null;
        int top=79-(int)Math.floor(Math.max(0,radius-.12)*10);
        // Two stepped erosion cuts join the outside edge, never blind holes.
        if(x<25&&z<8&&x+z<27)top-=3;
        if(x>42&&z>19&&x+z>66)top-=2;
        if(y>top)return null;
        return Palette.STATES[y>=top-1?8:2];
    }
}
'''.replace('ROWS',rows)
    result={JAVA:java}
    variants={f'finish={i}':{'model': 'dynasty:block/dungeon_masonry'+(f'_{i}' if i else '')} for i in range(8)}
    result[ASSETS/'blockstates/dungeon_masonry.json']=json.dumps({'variants':variants},indent=2)+'\n'
    for i,texture in enumerate(FINISHES):
        if not i: continue  # Preserve the existing default model byte-for-byte.
        result[ASSETS/f'models/block/dungeon_masonry_{i}.json']=json.dumps({
            'parent':'minecraft:block/cube_all','textures':{'all':'minecraft:block/'+texture}},indent=2)+'\n'
    result[DOC/'geometry.json']=json.dumps({'coordinate_system':'x east, y up, z south; local 64×80×96',
        'scope':'production decorative cuboids; base rooms, mound, mechanisms and connectors are in Java',
        'rooms':[dict(name=n,motif=m,x=x,z=z) for n,m,x,z in ROOMS],
        'palette': ['base']+FINISHES+['chain_x','chain_y','chain_z','air'], 'boxes':boxes},ensure_ascii=False,indent=2)+'\n'
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
    for path,content in outputs().items():
        if args.check:
            assert path.exists() and path.read_text()==content, f'Generated output differs: {path}'
        else:
            path.parent.mkdir(parents=True,exist_ok=True); path.write_text(content)
    print(f'{len(geometry())} production cuboids; resources '+('verified' if args.check else 'written'))
