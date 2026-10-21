#!/usr/bin/env python3
"""Read-only Python review of production geometry. No Java or game is launched.

The deliberately small translator accepts only the pure coordinate methods used
here. Unknown Java syntax fails closed. This can check occupied cells and produce
cutaways; it cannot certify Forge loading, lighting, collision or game behaviour.
Requires tree-sitter, tree-sitter-java, Pillow; see the evidence report for versions.
"""
import argparse
import hashlib
import json
import math
import re
from collections import Counter, deque
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace

import tree_sitter
import tree_sitter_java

from build_chensha_architecture import ROOT, DOC, outputs

PARSER=tree_sitter.Parser(tree_sitter.Language(tree_sitter_java.language()))


class JavaCoordinates:
    """Translate a whitelist of pure methods, using their actual parsed expressions."""
    def __init__(self):
        self.sources={}
        self.env={'math':math,'int':int,'abs':abs,'min':min,'max':max,'tuple':tuple,
                  'jround':lambda x:math.floor(x+.5), 'masonry':lambda:'MASONRY_0'}

    def expr(self,n):
        t=n.type; text=n.text.decode(); f=n.child_by_field_name
        if t=='identifier': return 'within' if text=='in' else text
        if t in ('decimal_integer_literal','decimal_floating_point_literal'): return text.rstrip('fFdDlL')
        if t in ('true','false','null_literal'): return {'true':'True','false':'False','null':'None'}[text]
        if t=='parenthesized_expression': return '('+self.expr(n.named_children[0])+')'
        if t in ('binary_expression','assignment_expression'):
            left,right=f('left'),f('right')
            op=n.text[left.end_byte-n.start_byte:right.start_byte-n.start_byte].decode().strip()
            op={'&&':'and','||':'or'}.get(op,op)
            assert op in ('+','-','*','/','%','<','>','<=','>=','==','!=','and','or','=','-=','+='),op
            value=f'{self.expr(left)} {op} {self.expr(right)}'
            return value if t=='assignment_expression' else '('+value+')'
        if t=='unary_expression':
            op=n.children[0].text.decode()
            assert op in ('!','-','+')
            return '('+('not ' if op=='!' else op)+self.expr(n.named_children[0])+')'
        if t=='ternary_expression':
            return f'({self.expr(f("consequence"))} if {self.expr(f("condition"))} else {self.expr(f("alternative"))})'
        if t=='cast_expression':
            assert f('type').text==b'int'
            return 'int('+self.expr(f('value'))+')'
        if t=='field_access':
            obj=f('object').text.decode(); field=f('field').text.decode()
            if obj=='Blocks': return repr(field)
            if text=='Math.PI': return 'math.pi'
            if obj in ('Direction','Direction.Axis'): return repr(field)
            if text=='net.minecraft.world.level.block.LadderBlock.FACING': return repr('FACING')
            if text=='Palette.STATES': return 'PALETTE'
            raise ValueError('Unknown field '+text)
        if t=='array_access': return self.expr(f('array'))+'['+self.expr(f('index'))+']'
        if t=='array_creation_expression': return self.expr(f('value'))
        if t=='array_initializer': return '['+','.join(self.expr(c) for c in n.named_children)+']'
        if t=='object_creation_expression':
            typ=f('type').text.decode(); args=[self.expr(c) for c in f('arguments').named_children]
            if typ.startswith('ArrayList'): return '[]'
            if typ=='BlockPos': return '('+','.join(args)+')'
            raise ValueError('Unknown constructor '+text)
        if t=='method_invocation':
            name=f('name').text.decode(); obj=f('object'); raw=obj.text.decode() if obj else ''
            args=[self.expr(c) for c in f('arguments').named_children]
            if name in ('defaultBlockState','get'):
                if raw=='DungeonContent.MERCURY_CHANNEL': return repr('MERCURY_CHANNEL')
                if raw=='DungeonContent.MASONRY': return repr('MASONRY_0')
                return self.expr(obj)
            if name=='setValue': return '('+self.expr(obj)+'+"["+str('+args[0]+')+"="+str('+args[1]+')+"]")'
            if raw=='Math':
                name={'pow':'math.pow','sqrt':'math.sqrt','floor':'math.floor','round':'jround','abs':'abs','cos':'math.cos','sin':'math.sin','max':'max','min':'min'}[name]
            elif raw=='List' and name=='copyOf': name='tuple'
            elif name=='add' and raw=='points': name='points.append'
            elif raw in ('ChenshaVaultLayout','ChenshaArchitecture'): name=raw+'.'+name
            elif raw=='DungeonMasonryBlock' and name=='finish': return '("MASONRY_"+str('+args[0]+'))'
            elif obj: raise ValueError('Unknown call '+text)
            elif name=='in': name='within'
            elif name=='shell': name='masonry'
            return name+'('+','.join(args)+')'
        if t=='update_expression':
            assert text.endswith('++')
            return text[:-2]+' += 1'
        raise ValueError('Unknown expression '+t+': '+text)

    def statements(self,n,depth=1):
        pad='    '*depth; t=n.type; f=n.child_by_field_name
        if t in ('line_comment','block_comment'): return ''
        if t=='block': return ''.join(self.statements(c,depth) for c in n.named_children)
        if t=='local_variable_declaration':
            return ''.join(pad+self.expr(v.child_by_field_name('name'))+' = '+self.expr(v.child_by_field_name('value'))+'\n'
                           for v in n.named_children if v.type=='variable_declarator')
        if t=='expression_statement': return pad+self.expr(n.named_children[0])+'\n'
        if t=='return_statement': return pad+'return '+self.expr(n.named_children[0])+'\n'
        if t=='if_statement':
            s=pad+'if '+self.expr(f('condition'))+':\n'+self.statements(f('consequence'),depth+1)
            if f('alternative'): s+=pad+'else:\n'+self.statements(f('alternative'),depth+1)
            return s
        if t=='enhanced_for_statement':
            return pad+'for '+self.expr(f('name'))+' in '+self.expr(f('value'))+':\n'+self.statements(f('body'),depth+1)
        if t=='for_statement':
            return (self.statements(f('init'),depth)+pad+'while '+self.expr(f('condition'))+':\n'
                    +self.statements(f('body'),depth+1)+'    '*(depth+1)+self.expr(f('update'))+'\n')
        raise ValueError('Unknown statement '+t+': '+n.text.decode())

    def load(self,cls,names):
        path=ROOT/f'src/main/java/com/dynasty/dungeon/{cls}.java'
        source=path.read_bytes(); tree=PARSER.parse(source)
        assert not tree.root_node.has_error, f'Java syntax: {path}'
        body=next(n for n in tree.root_node.named_children if n.type=='class_declaration').child_by_field_name('body')
        methods={m.child_by_field_name('name').text.decode():m for m in body.named_children if m.type=='method_declaration'}
        local=dict(self.env)
        for name in names:
            method=methods[name]
            args=[self.expr(p.child_by_field_name('name')) for p in method.child_by_field_name('parameters').named_children]
            code='def '+('within' if name=='in' else name)+'('+','.join(args)+'):\n'+self.statements(method.child_by_field_name('body'))
            self.sources[cls+'.'+name]=code
            exec(compile(code,str(path),'exec'),local)
        ns=SimpleNamespace(**{name:local['within' if name=='in' else name] for name in names})
        self.env[cls]=ns
        return ns


def load_coordinates():
    java=JavaCoordinates()
    java.env['PALETTE']=[None]+[f'MASONRY_{i}' for i in range(8)]+['CHAIN[AXIS=X]','CHAIN[AXIS=Y]','CHAIN[AXIS=Z]','AIR']
    architecture=java.load('ChenshaArchitecture',['mound'])
    # Read cuboids from the generated Java, independently of the author's manifest.
    source=(ROOT/'src/main/java/com/dynasty/dungeon/ChenshaArchitecture.java').read_text()
    literal=source.split('private static final short[][] BOXES = {',1)[1].split('\n    };',1)[0]
    boxes=[list(map(int,re.findall(r'\d+',row))) for row in literal.splitlines() if row.strip()]
    cells=bytearray(64*96*80)
    for x0,y0,z0,x1,y1,z1,p in boxes:
        for y in range(y0,y1+1):
            for z in range(z0,z1+1):
                for x in range(x0,x1+1): cells[(y*96+z)*64+x]=p
    architecture.decoration=lambda x,y,z: java.env['PALETTE'][cells[(y*96+z)*64+x]] if 0<=x<64 and 0<=y<80 and 0<=z<96 else None
    vault=java.load('ChenshaVaultLayout',['moatRadius','moatCell','daisHeight','roofHeight','constellationOffsets'])
    piece=java.load('ChenshaPiece',['in','rect','vaultRoof','daisHeight','cell','vaultStars'])
    return java,piece,vault,cells,boxes


def validate(piece,vault,cells,boxes):
    checks=[]
    def check(ok,label):
        assert ok,label
        checks.append(label)
    refs=json.loads((DOC/'references.json').read_text())
    check(len(refs)==100 and len({r['url'] for r in refs})==100,'100 distinct author project pages')
    check(all(r['observation_zh'] and r['images'] for r in refs),'Every reference has an observation and image provenance')
    for path,text in outputs().items(): check(path.read_text()==text,'Generated source/resource matches: '+str(path.relative_to(ROOT)))
    check(all(0<=a<=d<64 and 0<=b<=e<80 and 0<=c<=f<96 and 1<=p<=12 for a,b,c,d,e,f,p in boxes),'Cuboids fit the existing 24 clipped pieces')
    # Existing playable clearances, not just validation of the new box data.
    for z0,z1,formula in ((10,34,lambda z:82-z),(59,83,lambda z:107-z),(28,52,lambda z:z-28)):
        for z in range(z0,z1+1):
            floor=formula(z)
            for x in range(30,35):
                assert piece.cell(x,floor,z)!='AIR',('missing stair',x,floor,z)
                for dy in range(1,5): assert piece.cell(x,floor+dy,z)=='AIR',('stair blocked',x,floor+dy,z)
    checks.append('All three stair runs retain five-wide, four-high player clearance')
    for y in range(44,49): check(piece.cell(35,y,41)=='LADDER[FACING=WEST]' and piece.cell(36,y,41) not in (None,'AIR'),'Pit ladder and support y='+str(y))
    check(all(piece.cell(35,y,41)=='AIR' for y in range(49,52)),'Pit exit has three blocks of headroom')
    check(all(piece.cell(52,y,87)=='CRACKED_STONE_BRICKS' and piece.cell(52,y,86)=='AIR' and piece.cell(52,y,88)=='AIR' for y in range(25,28)),'Artisan secret wall remains breakable with clear approaches')
    check(all(piece.cell(x,y,8)=='AIR' for x in range(40,43) for y in range(1,4)),'Return lift bottom access remains open')
    check(all(piece.cell(x,y,8)=='AIR' for x in range(37,43) for y in range(73,76)),'Return lift top access remains open')
    check(all(piece.cell(x,76,z) not in (None,'AIR') for x in range(40,45) for z in range(6,11)),'Lift shaft has a weatherproof cap above its landing')
    for cx in (12,52):
        check(all(piece.cell(cx+dx,28+dy,60+dz)=='AIR' for dx in (-1,0,1) for dy in (0,1) for dz in (-1,0,1)),'Flying skull clearance x='+str(cx))
        check(piece.cell(cx,23,62)=='WATER','Submerged drowner spawn x='+str(cx))
        check(all(piece.cell(cx,y,z) not in (None,'AIR','WATER') for z,y in ((54,23),(55,22),(56,21))),'Water exit steps x='+str(cx))
    check(all(piece.cell(x,y,z)==('LADDER[FACING=EAST]' if x==18 and z==44 else 'AIR') for x in range(18,25) for z in range(41,48) for y in range(29,49)),'Horse burial pit retains its full twenty-block depth')
    check(all(piece.cell(18,y,44)=='LADDER[FACING=EAST]' and (piece.cell(17,y,44) or '').startswith('MASONRY_') for y in range(29,50)),'Burial well has a supported ladder returning only to the upper gallery')
    check(all(piece.cell(x,y,z)=='AIR' for x in range(17,26) for z in range(40,49) for y in range(50,56)),'Horse well has an open sightline above its one-block parapet')
    check(all(piece.cell(x+dx,y+dy,z+dz)=='AIR' for x,y,z in ((10,49,50),(52,49,50),(10,49,78),(52,49,78)) for dx in (-1,0,1) for dy in range(3) for dz in (-1,0,1)), 'Four upper garrison positions retain standing clearance')
    for start in (20,40):
        for edge in (38,58,78):
            check(all(piece.cell(x,y,z)=='AIR' for x in range(start-1,start+5) for z in (edge+1,edge+2) for y in range(25,28)),f'EW bridge clear: {start},{edge}')
    check(all(piece.cell(x,y,z)=='AIR' for x in (31,32) for z in range(68,72) for y in range(25,28)),'NS bridge clear of trial gate')
    # Reachability uses the actual final cell precedence, rather than box intent.
    # This assumes the authored seals are open; it does not emulate Minecraft AI.
    cell=lru_cache(None)(piece.cell)
    def standable(x,y,z):
        floor=cell(x,y-1,z)
        return all(cell(x,y+d,z)=='AIR' for d in (0,1)) and floor not in (None,'AIR','WATER') and not floor.startswith('CHAIN')
    start=(32,25,60); reached={start};queue=deque([start])
    while queue:
        x,y,z=queue.popleft()
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            for dy in (0,):
                p=(x+dx,y+dy,z+dz)
                if p in reached or not(5<=p[0]<=58 and 25<=p[1]<=28 and 33<=p[2]<=86): continue
                if standable(*p): reached.add(p);queue.append(p)
    goals=[(12,25,40),(32,25,40),(52,25,40),(12,25,53),(32,25,60),(52,25,53),(12,25,80),(32,25,84),(52,25,80)]
    check(all(p in reached for p in goals),'All nine middle chambers connect on dry level floors after seals open, without swimming or jumping onto chains')
    # Every chain component must reach solid masonry/deck through adjacent chains.
    chains={(x,y,z) for y in range(18,34) for z in range(32,90) for x in range(4,60)
            if (piece.cell(x,y,z) or '').startswith('CHAIN')}
    remaining=set(chains); components=0
    while remaining:
        queue=deque([remaining.pop()]); anchored=False; components+=1
        while queue:
            x,y,z=queue.popleft()
            for dx,dy,dz in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
                pos=(x+dx,y+dy,z+dz)
                if pos in remaining: remaining.remove(pos);queue.append(pos)
                elif pos not in chains:
                    state=piece.cell(*pos)
                    if state and state.startswith('MASONRY_'): anchored=True
        check(anchored,f'Chain component {components} is anchored to solid masonry')
    stars=piece.vaultStars()
    check(len(stars)==len(set(stars))==28 and stars==vault.constellationOffsets(),'One canonical set of 28 unique pearls')
    check(all(y==vault.roofHeight(x,z) and piece.cell(x,y,z) not in ('AIR',None) for x,y,z in stars),'All pearls attach to the vault roof')
    source=(ROOT/'src/main/java/com/dynasty/dungeon/ChenshaPiece.java').read_text()
    check('SEA_LANTERN' not in source and source.count('Blocks.PEARLESCENT_FROGLIGHT')==1,'No second star placement pass')
    check(all(vault.daisHeight(32,z)==26-z for z in range(17,26)),'Nine accessible main-axis dais risers')
    # Preserve old default, all seven new finishes resolve to actual model JSON.
    variants=json.loads((ROOT/'src/main/resources/assets/dynasty/blockstates/dungeon_masonry.json').read_text())['variants']
    check(set(variants)=={f'finish={i}' for i in range(8)},'All protected masonry finishes resolve')
    for v in variants.values():
        path=ROOT/'src/main/resources/assets/dynasty/models'/f"{v['model'].split(':')[1]}.json"
        json.loads(path.read_text())
    return checks


def render(piece,vault):
    from PIL import Image, ImageDraw, ImageFont
    font_path='/System/Library/Fonts/STHeiti Medium.ttc'
    font=ImageFont.truetype(font_path,21); small=ImageFont.truetype(font_path,15)
    colors={'MASONRY_0':(56,62,67),'MASONRY_1':(57,42,42),'MASONRY_2':(218,211,190),
            'MASONRY_3':(169,104,63),'MASONRY_4':(68,119,103),'MASONRY_5':(67,72,73),
            'MASONRY_6':(45,49,51),'MASONRY_7':(192,163,111),'BONE_BLOCK':(182,180,159),
            'CUT_COPPER':(169,104,63),'WATER':(38,111,155),'LIGHT_BLUE_STAINED_GLASS':(73,130,147),
            'QUARTZ_BLOCK':(218,211,190),'QUARTZ_BRICKS':(205,200,183),'SMOOTH_QUARTZ':(224,218,198),
            'MERCURY_CHANNEL':(87,137,148),'PEARLESCENT_FROGLIGHT':(248,228,180)}
    panels=[('封土入口 / 完整外观', (9,55,0,33,68,79),False),
            ('神道与殉马井 / 去顶剖视', (3,60,32,89,28,56),True),
            ('九玄室 / 去顶剖视', (3,60,31,90,18,30),True),
            ('九级龙台 / 去顶剖视', (7,56,1,30,0,12),True)]
    for idx,(title,bounds,cut) in enumerate(panels):
        x0,x1,z0,z1,y0,y1=bounds
        solids={}
        for y in range(y0,y1+1):
            for z in range(z0,z1+1):
                for x in range(x0,x1+1):
                    s=piece.cell(x,y,z)
                    if s and s!='AIR':
                        # Thin cut walls expose the room; this is clearly a cutaway.
                        if cut and y>y0+1 and (x in (x0+1,x1-1) or z in (z0+1,z1-1)): continue
                        solids[(x,y,z)]=s
        # Static fixtures relevant to this view are explicitly labeled; placement
        # methods remain outside the cell() translator and need native checking.
        if idx==3:
            for pos in vault.constellationOffsets():
                if pos[1]<=y1: solids[pos]='PEARLESCENT_FROGLIGHT'
        scale=6.2 if idx in (1,2) else 8.0
        front=idx==0
        def project(p):
            x,y,z=p
            if front: z=-z
            return ((x-z)*scale,(x+z)*scale*.47-y*scale)
        corners=[project((x,y,z)) for x in (x0,x1+1) for z in (z0,z1+1) for y in (y0,y1+1)]
        minx=min(p[0] for p in corners);miny=min(p[1] for p in corners)
        maxx=max(p[0] for p in corners);maxy=max(p[1] for p in corners)
        width=max(960,int(maxx-minx)+90);height=max(580,int(maxy-miny)+150)
        im=Image.new('RGB',(width,height),(21,26,31));draw=ImageDraw.Draw(im)
        draw.text((28,18),title,fill=(231,226,210),font=font)
        draw.text((28,52),'生产坐标软件剖视 · 纯色材质示意 · 不是游戏截图 / 不含原版光照、碰撞和机关模型',fill=(158,176,184),font=small)
        offset=((width-(maxx-minx))/2-minx,110-miny)
        def p3(p):
            a,b=project(p);return (round(a+offset[0]),round(b+offset[1]))
        faces=[]
        for (x,y,z),state in solids.items():
            if state.startswith('CHAIN'):
                # Draw the actual chain axis as a thin line, avoiding solid-cube rails.
                axis=state[-2];centre=(x+.5,y+.5,z+.5)
                a=list(centre);b=list(centre);d={'X':0,'Y':1,'Z':2}[axis];a[d]-=.5;b[d]+=.5
                faces.append((x+z+y*.02,[],(137,142,137),(p3(a),p3(b))));continue
            color=colors.get(state,(119,108,91))
            specs=[((0,1,0),[(x,y+1,z),(x+1,y+1,z),(x+1,y+1,z+1),(x,y+1,z+1)],1.13),
                   ((1,0,0),[(x+1,y,z),(x+1,y,z+1),(x+1,y+1,z+1),(x+1,y+1,z)],.70),
                   ((0,0,-1 if front else 1),[(x,y,z if front else z+1),(x+1,y,z if front else z+1),
                     (x+1,y+1,z if front else z+1),(x,y+1,z if front else z+1)],.86)]
            for (dx,dy,dz),points,shade in specs:
                if (x+dx,y+dy,z+dz) in solids and not solids[(x+dx,y+dy,z+dz)].startswith('CHAIN'): continue
                rgb=tuple(min(255,int(c*shade)) for c in color)
                faces.append((x+(-z if front else z)+y*.02,[p3(p) for p in points],rgb,None))
        for _,points,color,line in sorted(faces,key=lambda f:f[0]):
            if line: draw.line(line,fill=color,width=2)
            else: draw.polygon(points,fill=color)
        im.save(DOC/f'cutaway-{idx+1}.png')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--render',action='store_true');args=parser.parse_args()
    java,piece,vault,cells,boxes=load_coordinates()
    checks=validate(piece,vault,cells,boxes)
    if args.render: render(piece,vault)
    report={'date':'2026-10-18','mode':'Python source-coordinate checks only; NO JVM/game execution',
            'checks':checks,'passed':len(checks),'cuboids':len(boxes),'references':100,
            'limitations':['No Java type checking or Forge loading','No in-game visual, collision, lighting or playthrough acceptance',
                          'Existing generated chunks are not retroactively rebuilt','Complete Cod2 and Chensha boss/rewards remain unfinished'],
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                             [ROOT/f'src/main/java/com/dynasty/dungeon/{n}.java' for n in
                              ['ChenshaArchitecture','ChenshaPiece','ChenshaVaultLayout','DungeonMasonryBlock','DungeonContent']]}}
    (DOC/'static-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    # Keep the exact translated pure methods inspectable for review of this checker.
    (DOC/'coordinate-methods.py.txt').write_text('\n\n'.join('# '+k+'\n'+v for k,v in java.sources.items()))
    print(json.dumps({'passed':len(checks),'cuboids':len(boxes),'java_started':False},ensure_ascii=False))
