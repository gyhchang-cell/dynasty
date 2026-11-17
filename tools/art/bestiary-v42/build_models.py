"""Authoritative, original realm-mob native layers and material-aware pixel UVs.

Five anatomical humanoids keep the six canonical Steve blocks. The soul is a
hollow hood, shell and hanging strips, not another dressed player. No reference
pixels are read by this exporter. Old shared-skin generators cannot overwrite
these independent runtime atlases.
"""
from pathlib import Path
import json, math, hashlib, shutil
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/art/bestiary-v42'
ASSETS=ROOT/'src/main/resources/assets/dynasty'
JAVA=ROOT/'src/main/java/com/dynasty/client/RealmCreatureLayers.java'
IDS=['jade_guard','soul_soldier','thunder_envoy','merfolk','terracotta_warrior','minister']
TITLES=['玉甲卫','冥卒','雷使','鲛人','兵马俑战士','大臣（友方NPC）']
SCALES=[1.08,1.05,1,1,1,1]

class Model:
    def __init__(self,id):self.name=id;self.bones=[];self.cubes=[]
    def bone(self,n,parent='root',p=(0,0,0),r=(0,0,0)):
        self.bones.append(dict(name=n,parent=None if n=='root' else parent,pivot=list(p),rotation=list(r),cubes=[]));return n
    def cube(self,n,o,s,mat,role):
        c=dict(origin=list(o),size=list(s),material=mat,role=role)
        next(b for b in self.bones if b['name']==n)['cubes'].append(c);self.cubes.append(c)

def humanoid(id):
    m=Model(id);m.bone('root');m.bone('body');m.cube('body',(-4,0,-2),(8,12,4),'cloth','torso')
    m.bone('head');m.cube('head',(-4,-8,-4),(8,8,8),'skin','face')
    for side,s in [('right',-1),('left',1)]:
        arm=m.bone(side+'_arm',p=(s*5,2,0));m.cube(arm,(-3 if s<0 else -1,-2,-2),(4,12,4),'cloth','arm_'+side)
        leg=m.bone(side+'_leg',p=(s*1.9,12,0));m.cube(leg,(-2,0,-2),(4,12,4),'cloth','leg')
    if id=='jade_guard':
        m.bone('helmet','head',(0,-6.7,0));m.cube('helmet',(-4.2,-1.5,-4.2),(8,2,8),'metal','helmet')
        m.bone('brow','head',(0,-4.8,-4.2));m.cube('brow',(-4,-.6,-.4),(8,1,1),'bronze','brow')
        # Mask only covers the lower face; a real open eye band remains visible.
        m.bone('mask','head',(0,-1.4,-4.22));m.cube('mask',(-3,-1.1,-.4),(6,3,1),'metal','mask')
        for side,s in [('right',-1),('left',1)]:
            m.bone('shoulder_'+side,side+'_arm',(s,-1.8,0));m.cube('shoulder_'+side,(-2.2,-.4,-2.4),(4,2,5),'metal','shoulder')
        m.bone('collar','body',(0,.8,-2.1));m.cube('collar',(-3,-.4,-.3),(6,2,1),'bronze','collar')
    elif id=='thunder_envoy':
        m.bone('headband','head',(0,-6.7,0));m.cube('headband',(-4.15,-.6,-4.15),(8,1,8),'cloth','headband')
        m.bone('knot','head',(3,-5.8,3.9));m.cube('knot',(-.5,0,0),(1,5,1),'cloth','knot')
        m.bone('collar','body',(0,0,-2.1));m.cube('collar',(-3,-.3,-.3),(6,2,1),'bronze','collar')
        for side,s in [('right',-1),('left',1)]:
            m.bone('cuff_'+side,side+'_arm',(s,6.3,0));m.cube('cuff_'+side,(-2.15,0,-2.15),(4,2,4),'bronze','cuff')
    elif id=='terracotta_warrior':
        # Human-made clay guardian: recognizable Steve base, restrained molded details.
        m.bone('topknot','head',(1,-8,1));m.cube('topknot',(-1.5,-2,-1.5),(3,2,3),'clay','topknot')
        m.bone('collar','body',(0,.3,-2));m.cube('collar',(-3,-.3,-.6),(6,2,1),'clay','collar')
        for side,s in [('right',-1),('left',1)]:
            m.bone('shoulder_'+side,side+'_arm',(s,-1.7,0));m.cube('shoulder_'+side,(-2,-.3,-2.3),(4,2,5),'clay','shoulder')
    elif id=='minister':
        m.bone('hat','head',(0,-7.8,0));m.cube('hat',(-4,-1.2,-4),(8,2,8),'cloth','hat')
        # Keep integer Steve-sized UVs; slight shell inflation avoids coplanar hat/head faces.
        m.cubes[-1]['inflate']=.15
        for side,s in [('right',-1),('left',1)]:
            m.bone('hat_fold_'+side,'hat',(s*3.8,-.3,1),r=(0,0,s*.10));m.cube('hat_fold_'+side,(-1 if s<0 else 0,0,0),(1,1,3),'cloth','hat_fold')
        m.bone('collar','body',(0,.7,-2.1));m.cube('collar',(-3,-.5,-.3),(6,2,1),'cloth','collar')
    else:
        # A walking gilled sea-person: keep the actual ground-navigation legs.
        for side,s in [('right',-1),('left',1)]:
            m.bone('gill_'+side,'head',(s*3.9,-3,.7),(0,s*.22,s*.14));m.cube('gill_'+side,(-.4,-2,0),(1,4,3),'fin','gill')
        m.bone('dorsal','body',(0,2,1.9));m.cube('dorsal',(-.4,0,0),(1,7,3),'fin','dorsal')
        m.bone('tail','body',(0,10,1.9),(-.42,0,0));m.cube('tail',(-1,0,0),(2,3,5),'skin','tail')
        m.bone('tail_fin','tail',(0,0,4),(.12,0,0));m.cube('tail_fin',(-3,0,0),(6,1,3),'fin','tail_fin')
    return m

def soul():
    m=Model('soul_soldier');m.bone('root');m.bone('body',p=(0,1,0))
    # The front opening and the gap below the hood are real space, not black paint.
    for s in [-1,1]:m.cube('body',(s*3-.75,0,-2),(2,10,4),'iron','shell')
    m.cube('body',(-3.5,0,-2),(7,2,4),'iron','collar')
    m.cube('body',(-3.5,8,-2),(7,2,4),'iron','belt')
    m.bone('head',p=(0,-.5,0));m.cube('head',(-3.5,-7,0),(7,7,2),'cloth','hood_back')
    m.cube('head',(-3.5,-7,-3),(7,1,4),'cloth','hood_top')
    for s in [-1,1]:m.cube('head',(s*3-.5,-6,-3),(1,6,4),'cloth','hood_side')
    m.bone('mask','head',(0,-3,-2.2));m.cube('mask',(-2.5,-2.5,-.5),(5,5,1),'bone','mask')
    for side,s in [('right',-1),('left',1)]:
        m.bone(side+'_arm',p=(s*4.5,3,0),r=(-.18,0,-s*.08));m.cube(side+'_arm',(-1.5,0,-1.5),(3,7,3),'iron','sleeve')
        m.bone('hand_'+side,side+'_arm',(0,6,-.1));m.cube('hand_'+side,(-1,0,-1),(2,3,2),'bone','hand')
        # Staggered lengths and a rear third panel read as torn cloth, never a pair of trousers.
        m.bone('strip_'+side,'body',(s*2.2,9,.6),(.10 if s<0 else -.06,s*.12,-s*.16));m.cube('strip_'+side,(-1.5,0,-1),(3,7 if s<0 else 9,1),'cloth','strip')
        m.bone('strip_'+side+'_tip','strip_'+side,(0,6 if s<0 else 8,0),(.11,0,0));m.cube('strip_'+side+'_tip',(-1,0,-.4),(2,3,1),'cloth','strip_tip')
    m.bone('backcloth','body',(0,2,2));m.cube('backcloth',(-3,0,0),(6,13,1),'cloth','backcloth')
    m.bone('rear_strip','backcloth',(-.7,12,.1),(.24,.05,.08));m.cube('rear_strip',(-1.5,0,0),(3,6,1),'cloth','strip')
    return m

PALETTES={
 'jade_guard':{'cloth':['202f2e','30423b','485849','61715b'],'skin':['8e6650','af8465','d0aa82','e2c6a0'],'metal':['263c36','3c5b4a','5f8061','91a484'],'bronze':['514536','796340','a38a55','c5af79']},
 'thunder_envoy':{'cloth':['202738','303d57','4b607b','7989a0'],'skin':['725241','a47b58','c6a17a','d9bf97'],'bronze':['483d36','786044','b09160','d1ba84']},
 'merfolk':{'cloth':['1e353a','2b5056','46757a','78a09d'],'skin':['2c555b','497b7c','78a69b','b1c9b4'],'fin':['243f50','3b6170','5d8991','8bb2af']},
 'soul_soldier':{'cloth':['202c37','304453','4a6370','6e8490'],'bone':['707e7d','a5b7b0','d3ded0','e9e9cf'],'iron':['202e35','354750','516873','788c92']},
 'terracotta_warrior':{'cloth':['46362d','71513d','956b4b','bd916a'],'skin':['624833','8b6749','b38a60','ceaa7b'],'clay':['513d30','79573e','a07951','c59b6e']},
 'minister':{'cloth':['20293d','303f5b','4e6484','7c90a5'],'skin':['846249','ad8761','cfaf83','e2ca9e']},
}

def paint_clay(c,f,w,h):
    """Molded clay rows share one body; no metal edging, rivet template or noise."""
    role=c['role'];front=f=='north';side=f in ('east','west');back=f=='south'
    im=Image.new('RGBA',(w,h),'#a07951' if f not in ('down','south') else '#8b6749');d=ImageDraw.Draw(im)
    if role=='face':
        if front:
            d.rectangle((0,0,7,1),fill='#513d30');d.line((1,2,3,2),fill='#624833');d.line((5,2,6,2),fill='#624833')
            d.line((1,3,2,3),fill='#46362d');d.point((5,3),fill='#46362d')
            d.rectangle((3,3,4,5),fill='#c59b6e');d.line((2,6,5,6),fill='#624833');d.line((3,7,4,7),fill='#79573e')
            d.point((0,5),fill='#bd916a');d.point((7,4),fill='#bd916a')
        elif side:d.rectangle((0,0,w-1,1),fill='#513d30');d.line((1,5,2,6),fill='#8b6749')
        else:im.paste('#79573e' if f=='down' else '#513d30',(0,0,w,h))
    elif role=='torso':
        if front or back:
            d.rectangle((0,0,w-1,1),fill='#79573e')
            for y in (4,7):
                d.line((0,y,w-1,y),fill='#79573e')
                for x in range(1 if y==4 else 0,w,3):d.line((x,y-2,x,y-1),fill='#bd916a')
            d.rectangle((0,9,w-1,10),fill='#624833');d.rectangle((3,9,4,10),fill='#bd916a')
            if front:d.line((5,1,4,3),fill='#624833');d.line((4,3,5,4),fill='#79573e')
        elif side:
            d.line((0,4,w-1,4),fill='#79573e');d.line((0,7,w-1,7),fill='#79573e');d.rectangle((0,9,w-1,10),fill='#624833')
    elif role.startswith('arm_'):
        d.rectangle((0,4,w-1,5),fill='#79573e');d.rectangle((0,9,w-1,11),fill='#b38a60')
        if front:d.line((1,1,2,1),fill='#c59b6e');d.line((1,6,1,8),fill='#bd916a')
    elif role=='leg':
        d.rectangle((0,0,w-1,3),fill='#71513d');d.rectangle((0,4,w-1,8),fill='#956b4b');d.rectangle((0,10,w-1,11),fill='#624833')
        if front:d.line((1,5,1,8),fill='#bd916a');d.line((2,9,3,9),fill='#79573e')
    elif role=='topknot':
        im.paste('#513d30',(0,0,w,h));d=ImageDraw.Draw(im)
        if front:d.line((0,1,w-1,1),fill='#956b4b')
    elif role=='collar':
        if front:d.line((0,0,w-1,0),fill='#c59b6e');d.rectangle((2,0,3,1),fill='#79573e')
    elif role=='shoulder':
        if front:d.line((0,h-1,w-1,h-1),fill='#79573e');d.line((1,0,w-2,0),fill='#bd916a')
    return im

def paint_minister(c,f,w,h):
    """An older civilian face and quiet layered cloth, not a recolored soldier."""
    role=c['role'];front=f=='north';back=f=='south';side=f in ('east','west')
    im=Image.new('RGBA',(w,h),'#4e6484' if f!='down' else '#303f5b');d=ImageDraw.Draw(im)
    if role=='face':
        im.paste('#cfaf83',(0,0,w,h));d=ImageDraw.Draw(im)
        if front:
            d.rectangle((0,0,w-1,1),fill='#30323b');d.line((1,2,2,2),fill='#8f9a9a');d.line((5,2,6,2),fill='#8f9a9a')
            d.point((2,3),fill='#383736');d.point((5,3),fill='#383736');d.line((3,3,3,5),fill='#ad8761')
            d.line((1,4,1,5),fill='#b99a76');d.line((6,4,6,5),fill='#b99a76')
            d.rectangle((2,6,5,6),fill='#909b98');d.rectangle((3,7,4,7),fill='#b6c0b1')
        elif side:d.rectangle((0,0,w-1,1),fill='#30323b');d.line((0,2,0,5),fill='#8f9a9a')
        elif back or f=='up':im.paste('#30323b',(0,0,w,h))
    elif role=='torso':
        if front:
            d.polygon([(0,0),(2,0),(5,6),(4,7)],fill='#a7b9bc');d.line((2,0,5,6),fill='#303f5b')
            d.rectangle((0,9,w-1,10),fill='#30323b');d.rectangle((3,9,4,10),fill='#8f9e86')
            d.line((1,4,1,8),fill='#303f5b');d.line((6,2,6,8),fill='#7c90a5')
        elif back:d.line((2,1,2,8),fill='#303f5b');d.line((5,3,5,8),fill='#7c90a5');d.rectangle((0,9,w-1,10),fill='#30323b')
        elif side:d.rectangle((0,9,w-1,10),fill='#30323b');d.line((1,3,1,7),fill='#303f5b')
    elif role.startswith('arm_'):
        if front or back:d.line((1,1,1,6),fill='#303f5b');d.line((2,4,2,7),fill='#7c90a5')
        d.rectangle((0,8,w-1,9),fill='#303f5b');d.rectangle((0,10,w-1,11),fill='#cfaf83')
    elif role=='leg':
        d.rectangle((0,0,w-1,8),fill='#303f5b');d.rectangle((0,10,w-1,11),fill='#30323b')
        if front or back:d.line((1,1,1,7),fill='#4e6484');d.line((0,8,w-1,8),fill='#7c90a5')
    elif role.startswith('hat'):
        im.paste('#30323b',(0,0,w,h));d=ImageDraw.Draw(im)
        if front:d.line((0,h-1,w-1,h-1),fill='#4a4d56')
    elif role=='collar':
        im.paste('#a7b9bc',(0,0,w,h));d=ImageDraw.Draw(im)
        if front:d.line((2,0,3,h-1),fill='#303f5b')
    return im

def faces(c):
    u,v=c['uv'];w,h,d=c['size']
    return {'west':(u,v+d,d,h),'north':(u+d,v+d,w,h),'east':(u+d+w,v+d,d,h),'south':(u+2*d+w,v+d,w,h),'up':(u+d,v,w,d),'down':(u+d+w,v,w,d)}

def paint(id,c,f,w,h):
    if id=='terracotta_warrior':return paint_clay(c,f,w,h)
    if id=='minister':return paint_minister(c,f,w,h)
    role=c['role'];p=['#'+x for x in PALETTES[id][c['material']]]
    im=Image.new('RGBA',(w,h),p[1 if f=='down' else 2]);d=ImageDraw.Draw(im)
    front=f=='north';side=f in ('east','west');back=f=='south';up=f=='up'
    def rect(x,y,x1,y1,col):
        if x1>=x and y1>=y:d.rectangle((x,y,x1,y1),fill=col)
    if role=='face':
        # One deliberate face, three very different masks/physiognomies, no shared template.
        if id=='jade_guard':
            if front:
                rect(0,0,7,2,'#263c36');rect(0,5,7,7,'#3c5b4a')
                rect(1,3,3,3,'#433c32');rect(5,3,6,3,'#433c32')
                d.point((2,4),fill='#232b28');d.point((5,4),fill='#232b28');rect(3,4,4,5,'#af8465')
            elif back or up:im.paste('#3c5b4a',(0,0,w,h))
            elif side:rect(0,0,w-1,2,'#263c36');rect(0,5,w-1,7,'#3c5b4a')
        elif id=='thunder_envoy':
            if front:
                rect(0,0,7,1,'#242830');rect(0,2,7,2,'#4b607b')
                d.line((1,3,3,4),fill='#4b382d');d.line((5,4,6,3),fill='#4b382d')
                d.point((2,4),fill='#222b33');d.point((5,4),fill='#222b33')
                rect(3,4,4,5,'#a47b58');rect(2,6,5,6,'#514235');rect(3,7,4,7,'#514235')
                d.point((6,5),fill='#896550')
            elif back or up:im.paste('#242830',(0,0,w,h))
            elif side:rect(0,0,7,2,'#242830');rect(0,3,1,6,'#4a3930')
        else:
            if front:
                rect(0,0,7,1,'#2c555b');rect(1,2,3,2,'#31535a');rect(5,2,6,2,'#31535a')
                rect(1,3,2,3,'#c6d7bb');rect(5,3,6,3,'#c6d7bb');d.point((2,3),fill='#213841');d.point((5,3),fill='#213841')
                rect(3,4,4,5,'#78a69b');rect(2,6,5,6,'#31535a');rect(3,7,4,7,'#b1c9b4')
            elif up:im.paste('#2c555b',(0,0,w,h))
            elif side:
                for y in (3,5):d.line((1,y,3,y+1),fill='#2c555b')
    elif role=='torso':
        if id=='jade_guard':
            im.paste('#3c5b4a',(0,0,w,h));d=ImageDraw.Draw(im)
            if front or back:
                rect(0,0,w-1,1,'#263c36');rect(0,9,w-1,10,'#514536');rect(3,9,4,10,'#b3a46c')
                # Broad lamellar courses; staggered joining, never a boxed border per part.
                for y in (3,6):
                    d.line((0,y,w-1,y),fill='#263c36')
                    for x in range((y//3)%2, w,3):d.line((x,y-2,x,y-1),fill='#5f8061')
                if front:rect(3,2,4,4,'#91a484');d.point((3,2),fill='#c5af79')
            elif side:
                for y in (3,6,9):d.line((0,y,w-1,y),fill='#263c36')
        elif id=='thunder_envoy':
            if front:
                d.polygon([(0,0),(2,0),(5,7),(4,8)],fill='#7989a0');d.line((1,0,5,7),fill='#b09160')
                rect(0,9,7,10,'#483d36');rect(3,9,4,10,'#d1ba84');rect(6,4,7,8,'#303d57')
            elif back:rect(1,1,2,8,'#303d57');rect(5,2,6,8,'#303d57');rect(0,9,w-1,10,'#483d36')
            elif side:rect(0,9,w-1,10,'#483d36');rect(0,3,0,7,'#303d57')
        else:
            im.paste('#497b7c',(0,0,w,h));d=ImageDraw.Draw(im)
            if front:rect(2,1,5,8,'#78a69b');rect(3,2,4,7,'#b1c9b4')
            if side or back:
                for y in (2,5,8):
                    for x in range((y//3)%2,w,3):d.line((x,y,x+1,y+1),fill='#2c555b')
            rect(0,10,w-1,11,'#243f50')
    elif role.startswith('arm_'):
        jade=id=='jade_guard';sea=id=='merfolk'
        if sea:
            im.paste('#497b7c',(0,0,w,h));d=ImageDraw.Draw(im)
            if front:rect(1,2,2,7,'#78a69b')
            rect(0,9,w-1,11,'#78a69b')
        elif jade:
            im.paste('#3c5b4a',(0,0,w,h));d=ImageDraw.Draw(im)
            rect(0,4,w-1,5,'#263c36');rect(0,8,w-1,9,'#796340');rect(0,10,w-1,11,'#af8465')
            if front:rect(1,1,2,3,'#5f8061');rect(1,6,2,7,'#5f8061')
        else:
            if front or back:d.line((1,1,1,6),fill='#303d57');d.line((2,4,2,7),fill='#7989a0')
            rect(0,8,w-1,8,'#786044');rect(0,9,w-1,11,'#c6a17a')
    elif role=='leg':
        if id=='jade_guard':
            rect(0,0,w-1,4,'#30423b');rect(0,5,w-1,9,'#3c5b4a');rect(0,10,w-1,11,'#26302d')
            if front:rect(1,6,2,8,'#5f8061');d.line((0,4,w-1,4),fill='#796340')
        elif id=='thunder_envoy':
            rect(0,0,w-1,2,'#303d57');rect(0,8,w-1,11,'#343532')
            if front:d.line((1,3,1,7),fill='#7989a0');d.line((0,9,w-1,9),fill='#786044')
        else:
            im.paste('#497b7c',(0,0,w,h));d=ImageDraw.Draw(im)
            if front:rect(1,1,2,6,'#78a69b');rect(1,10,2,10,'#243f50')
            if side:d.line((1,3,2,4),fill='#2c555b');d.line((1,7,2,8),fill='#2c555b')
    elif id=='soul_soldier':
        if role=='mask' and front:
            im.paste('#d3ded0',(0,0,w,h));d=ImageDraw.Draw(im)
            d.line((0,1,1,2),fill='#304453');d.line((3,2,4,1),fill='#304453')
            rect(1,2,1,2,'#202c37');rect(3,2,3,2,'#202c37');rect(2,3,2,4,'#707e7d');d.point((2,4),fill='#304453')
        elif role in ('strip','strip_tip','backcloth'):
            if role=='backcloth' and front:im.paste(p[0],(0,0,w,h));d=ImageDraw.Draw(im)
            if front or back:rect(0,0,0,h-2,p[1]);rect(w//2,1,w//2,h-3,p[2]);rect(0,h-2,w//2,h-1,p[0])
            if role=='backcloth' and back:d.line((2,2,2,7),fill=p[3]);d.line((2,7,4,9),fill=p[1])
        elif role=='shell':
            if front:d.line((0,1,0,h-2),fill=p[3]);rect(0,6,w-1,6,p[1])
        elif role=='sleeve':
            if front:rect(0,1,1,2,p[3]);rect(0,5,w-1,6,p[0])
        elif role=='hand' and front:d.line((1,0,1,h-1),fill=p[0])
    elif role in ('gill','dorsal','tail_fin'):
        if side or up:
            for x in range(1,w,2):d.line((x,0,x,h-1),fill=p[1])
        elif front:rect(0,h-1,w-1,h-1,p[3])
    elif role=='tail':
        if up:d.line((0,0,0,h-1),fill=p[0])
    else:
        # Restricted role-based accents, no random rectangular weathering or full white outlines.
        if role in ('brow','collar','cuff') and front:rect(0,0,w-1,0,p[3])
        if role=='shoulder' and front:d.line((0,h-1,w-1,h-1),fill=p[0]);d.line((1,0,w-2,0),fill=p[3])
        if role=='mask' and front:
            rect(1,1,w-2,1,p[1]);d.point((w//2,0),fill='#c5af79')
        if role=='helmet' and (front or side):rect(0,h-1,w-1,h-1,p[1])
        if role=='headband' and front:rect(3,0,4,0,'#d1ba84')
    return im

def export(m):
    folder=OUT/m.name;folder.mkdir(parents=True,exist_ok=True)
    im=Image.new('RGBA',(128,128));x=y=1;row=0
    for c in m.cubes:
        w,h,d=c['size'];bw=2*(w+d);bh=h+d
        if x+bw+1>128:x=1;y+=row+1;row=0
        if y+bh+1>128:raise ValueError('UV overflow')
        c['uv']=[x,y];row=max(row,bh)
        for f,(u,v,fw,fh) in faces(c).items():im.paste(paint(m.name,c,f,int(fw),int(fh)),(int(u),int(v)))
        x+=bw+1
    tex=ASSETS/'textures/entity/bestiary'/f'{m.name}.png';tex.parent.mkdir(exist_ok=True);im.save(tex);im.save(folder/'texture.png')
    im.resize((512,512),Image.Resampling.NEAREST).save(folder/'texture-4x.png')
    uv=im.copy();dr=ImageDraw.Draw(uv)
    for c in m.cubes:
        for f,(u,v,w,h) in faces(c).items():dr.rectangle((u,v,u+w-1,v+h-1),outline='#de58b3')
    uv.resize((512,512),Image.Resampling.NEAREST).save(folder/'uv-4x.png')
    data=dict(id=m.name,texture_size=[128,128],texture=str(tex.relative_to(ROOT)),scale=SCALES[IDS.index(m.name)],bones=m.bones)
    (folder/'model.json').write_text(json.dumps(data,indent=2)+'\n')
    jf=lambda x:f'{float(x):.5f}F'
    lines=['        MeshDefinition mesh = new MeshDefinition();','        PartDefinition root = mesh.getRoot();']
    for b in m.bones:
        if b['name']=='root':continue
        cubes='CubeListBuilder.create()'
        for c in b['cubes']:
            args=', '.join(map(jf,c['origin']+c['size']))
            if c.get('inflate'):args+=', new CubeDeformation('+jf(c['inflate'])+')'
            cubes+=f'.texOffs({c["uv"][0]}, {c["uv"][1]}).addBox('+args+')'
        lines.append(f'        PartDefinition {b["name"]} = {b["parent"]}.addOrReplaceChild("{b["name"]}", {cubes}, PartPose.offsetAndRotation('+', '.join(map(jf,b['pivot']+b['rotation']))+'));')
    lines.append('        return LayerDefinition.create(mesh, 128, 128);')
    return '\n'.join(lines)

def main():
    study=json.loads((OUT/'reference-study.json').read_text())
    assert study['count']==100 and all(v['viewed'] for v in study['items']), 'Inspect 100 actual similar mobs before new modeling'
    methods=[]
    for id in IDS:
        folder=OUT/id;folder.mkdir(parents=True,exist_ok=True)
        old=ASSETS/'textures/entity'/f'{id}.png'
        if not (folder/'before.texture.png').exists():shutil.copy2(old,folder/'before.texture.png')
        m=soul() if id=='soul_soldier' else humanoid(id)
        methods.append('    public static LayerDefinition '+id+'() {\n'+export(m)+'\n    }')
    JAVA.write_text('package com.dynasty.client;\n\nimport net.minecraft.client.model.geom.PartPose;\nimport net.minecraft.client.model.geom.builders.*;\n\n/** Generated original native models / UVs: tools/art/bestiary-v42/build_models.py. */\npublic final class RealmCreatureLayers {\n    private RealmCreatureLayers() {}\n'+'\n\n'.join(methods)+'\n}\n')
    print('Exported six independent native models and original 128px UV atlases; 100-reference gate satisfied for the additional humanoid batch')

if __name__=='__main__':main()
