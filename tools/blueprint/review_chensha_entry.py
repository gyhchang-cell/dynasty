#!/usr/bin/env python3
"""Production-coordinate entrance review, without Java or a running world."""
import hashlib
import json
import math
from collections import deque
from pathlib import Path
from review_chensha_architecture import ROOT, PARSER, load_coordinates, validate

OUT=ROOT/'docs/blueprint-cod2/evidence/entry-20261018'


def review():
    java,piece,vault,cells,boxes=load_coordinates()
    checks=validate(piece,vault,cells,boxes)
    def check(value,label):
        assert value,label
        checks.append(label)
    floors=[piece.entranceFloor(z) for z in range(10,35)]
    angle=math.degrees(math.atan2(floors[0]-floors[14],14))
    check(abs(angle-60)<.3,'Voxel descent is within 0.3 degrees of the requested 60 degrees')
    check(floors[0]==72 and floors[-1]==48,'Entry and ambulatory elevations are unchanged')
    check(set(floors[14:])=={48},'Ten-block level approach remains at the bottom of the slope')
    check(all(floors[i]-floors[i+1] in (1,2) for i in range(14)),
          'Every descending riser is one or two blocks; not a single vertical shaft')
    check(piece.entranceFloor(9)==-1 and piece.entranceFloor(35)==-1,'Entrance shaping stays within its bounded connector')
    for z in range(11,25):
        floor=piece.entranceFloor(z)
        check(all(piece.cell(30,y,z)=='LADDER[FACING=EAST]' and piece.cell(29,y,z).startswith('MASONRY_')
                  for y in range(floor+1,floor+5)),f'z={z}: ladder faces into passage and has continuous solid west support')
        check(piece.entranceFloor(z-1)+1<=floor+3,f'z={z}: uphill transfer fits a two-block player below the ceiling')

    def free(x,y,z):
        return piece.cell(x,y,z) in ('AIR','LADDER[FACING=EAST]')
    def body(p):
        x,y,z=p
        return 10<=z<=34 and 30<=x<=34 and free(x,y,z) and free(x,y+1,z)
    def ladder(p):
        return piece.cell(*p)=='LADDER[FACING=EAST]'
    def standing(p):
        x,y,z=p
        return not free(x,y-1,z)
    def route(start,end,allow_ladders):
        # Conservative voxel route only. Standing nodes may jump one block or
        # step/drop two. Wall-ladder nodes can climb vertically. No flight,
        # building blocks, lift teleport or traversing the still-sealed gate.
        queue=deque([start]);parents={start:None}
        while queue:
            p=queue.popleft()
            if p==end:
                path=[]
                while p is not None:path.append(p);p=parents[p]
                return path[::-1]
            x,y,z=p;candidates=[]
            if allow_ladders and ladder(p):candidates.extend([(x,y+1,z),(x,y-1,z)])
            for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
                for dy in (-2,-1,0,1):
                    target=(x+dx,y+dy,z+dz)
                    if not body(target):continue
                    # Both ends of the horizontal crossing must clear the
                    # higher standing height; no diagonal tunnelling through a lip.
                    top=max(y,y+dy)
                    if not body((x,top,z)) or not body((x+dx,top,z+dz)):continue
                    candidates.append(target)
            for q in candidates:
                if q in parents or not body(q):continue
                if not standing(q) and not (allow_ladders and ladder(q)):continue
                parents[q]=p;queue.append(q)
        return None

    start,end=(32,73,10),(32,49,34)
    descent=route(start,end,True);retreat=route(end,start,True)
    check(descent is not None,'Coordinate route exists from open seal to upper ambulatory')
    check(retreat is not None,'Coordinate retreat exists before the lower lift is unlocked')
    check(route(end,start,False) is None,'Negative control: ordinary one-block jumps cannot fake the steep return route')
    check(any(ladder(p) for p in retreat),'Return route actually uses supported ladder cells')
    # At the narrow seal plane, every possible lane still has an entrance gate.
    source=(ROOT/'src/main/java/com/dynasty/dungeon/ChenshaPiece.java').read_text()
    check('gate(result,"entrance","entrance_gate",10,73);' in source,
          'Original five-wide, four-high seal remains at the top of the descent')
    check(all(piece.cell(x,y,10).startswith('MASONRY_') for x in (29,35) for y in range(72,78)),
          'Ladder route cannot go around the gate through either side wall')
    for f in ['src/main/java/com/dynasty/dungeon/ChenshaPiece.java',
              'src/main/java/com/dynasty/dungeon/DungeonFrameworkGameTests.java']:
        check(not PARSER.parse((ROOT/f).read_bytes()).root_node.has_error,'Java syntax: '+f)
    OUT.mkdir(parents=True,exist_ok=True)
    render(piece,angle,retreat)
    report={'date':'2026-10-18','passed':len(checks),'checks':checks,'angle_degrees':angle,
            'floor_profile':floors,'descent_route':descent,'retreat_route':retreat,
            'java_started':False,'native_verified':False,'references':'../architecture-20261018/references.json',
            'limitations':['Voxel reachability is not game movement, falling damage or live player collision validation',
                           'No Java type checking, Forge loading or existing-save migration',
                           '60 degrees is approximated by a 24/14 block slope, not a smooth ramp'],
            'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                       [ROOT/'src/main/java/com/dynasty/dungeon/ChenshaPiece.java',Path(__file__)]}}
    (OUT/'static-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':len(checks),'angle':angle,'retreat_steps':len(retreat),'java_started':False}))


def render(piece,angle,retreat):
    from PIL import Image, ImageDraw, ImageFont
    image=Image.new('RGB',(1200,890),'#161b22');d=ImageDraw.Draw(image)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',20)
    small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',15)
    d.text((35,20),'CHENSHA ENTRANCE | production-coordinate section',font=font,fill='#f0e6d2')
    d.text((35,52),'24 blocks down / 14 blocks forward = %.2f deg | NOT an in-game screenshot'%angle,font=small,fill='#b7c1cd')
    scale=23;ox=100;oy=125
    def rect(z,y):
        a=ox+(z-9)*scale;b=oy+(78-y)*scale
        return (a,b,a+scale,b+scale)
    colors={'MASONRY_0':'#4e555e','MASONRY_3':'#a36d4b','MASONRY_5':'#454550','MASONRY_6':'#656170'}
    for z in range(10,35):
        for y in range(47,79):
            state=piece.cell(30,y,z)
            if state and state.startswith('MASONRY_'):d.rectangle(rect(z,y),fill=colors.get(state,'#565460'),outline='#232830')
            elif state=='LADDER[FACING=EAST]':
                a,b,c,e=rect(z,y);d.line((a+5,b,a+5,e),fill='#ccaa70',width=2);d.line((c-5,b,c-5,e),fill='#ccaa70',width=2)
                for off in (5,13,21):d.line((a+5,b+off,c-5,b+off),fill='#ccaa70',width=2)
    # Native gate markers are placed after cell() and shown separately here.
    for y in range(73,77):d.rectangle(rect(10,y),outline='#db6559',width=3)
    line=[]
    for x,y,z in retreat:
        a,b,c,e=rect(z,y);line.append(((a+c)/2,b+scale*.75))
    d.line(line,fill='#65cbb0',width=2)
    for z in (10,14,18,22,24,28,34):
        d.text((ox+(z-9)*scale,850),str(z),font=small,fill='#bdc9d7')
    d.text((760,160),'RED: original three-seal gate',font=small,fill='#db6559')
    d.text((760,195),'GOLD: supported west-wall ladder',font=small,fill='#ccaa70')
    d.text((760,230),'GREEN: checked voxel retreat route',font=small,fill='#65cbb0')
    d.text((760,280),'Four other lanes remain clear.',font=small,fill='#bdc9d7')
    d.text((760,310),'Bottom level run: z24 -> z34.',font=small,fill='#bdc9d7')
    d.text((760,365),'Requires native movement checks.',font=small,fill='#bdc9d7')
    image.save(OUT/'entry-section.png')


if __name__=='__main__':review()
