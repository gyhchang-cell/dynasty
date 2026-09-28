"""Full 111x101 interior estate, including boundary, overhangs and player's landscape."""
import copy,json,math,hashlib,shutil,sys
from pathlib import Path
from collections import Counter,deque
import build_courtyard_world as w
from PIL import Image,ImageDraw
ROOT=w.ROOT
w.REF=ROOT/'build/courtyard-full-reference'
w.OUT=ROOT/'build/courtyard-full-completion'
w.DEST=Path('/Users/a15356015027/Public/.minecraft/versions/Dynasty 王朝/saves/徽院全境-111x101独立版')
w.WORLD_NAME='徽院全境 · 111×101 完整试建'
w.CHUNK_BOUNDS=(15,27,-13,-4)
B=w.B;put=w.put;fill=w.fill;stairs=w.stairs;slab=w.slab;lamp=w.lamp
ORIGINAL={};COPIES=[]

def tree(x,z,kind='oak',height=6):
    fill(x,-59,z,x,-60+height,z,kind+'_log',axis='y')
    for yy in range(height-3,height+1):
        r=3 if yy<height else 2
        for dx in range(-r,r+1):
            for dz in range(-r,r+1):
                if dx*dx+dz*dz<=r*r+2 and (dx or dz or yy==height):
                    put(x+dx,-59+yy,z+dz,kind+'_leaves',distance=1,persistent=True,waterlogged=False)
def lightpost(x,z):
    put(x,-59,z,'chiseled_stone_bricks');put(x,-58,z,'stone_brick_wall',up=True,north='none',south='none',east='none',west='none',waterlogged=False)
    put(x,-57,z,'lantern',hanging=False,waterlogged=False)
def path(points,width=1):
    for (xa,za),(xb,zb) in zip(points,points[1:]):
        n=max(abs(xb-xa),abs(zb-za),1)
        for i in range(n+1):
            x=round(xa+(xb-xa)*i/n);z=round(za+(zb-za)*i/n)
            for dx in range(-width,width+1):
                for dz in range(-width,width+1):put(x+dx,-60,z+dz,'stone_bricks' if (x+z+dx)%6 else 'mossy_stone_bricks')

def facade_copy(dx,label):
    # Three-dimensional region, not one x slice. Includes brackets, lifted eaves and front/back relief.
    source={p:s for p,s in ORIGINAL.items() if 372<=p[0]<=387 and -153<=p[2]<=-111 and -59<=p[1]<=-30
            and not any(v in s['Name'] for v in ['leaves','bamboo','grass','flower','lilac','peony','rose_bush','dirt','water','vine'])}
    for (x,y,z),s in source.items():B[x+dx,y,z]=copy.deepcopy(s)
    COPIES.append((label,dx,source))

def great_hall():
    fill(268,-60,-152,294,-60,-112,'stone_bricks')
    fill(269,-59,-150,293,-59,-114,'spruce_planks')
    for z in (-151,-113):
        fill(269,-58,z,294,-49,z,'smooth_quartz')
        for x in range(271,294,5):
            fill(x,-58,z,x,-48,z,'stripped_spruce_wood',axis='y')
            fill(x+1,-55,z,x+3,-51,z,'spruce_fence',east=True,west=True,north=False,south=False,waterlogged=False)
    # Roof follows the measured horse-head profile, sunk beneath the copied coping.
    tops={z:max([y for (x,y,zz),s in ORIGINAL.items() if x==379 and zz==z and 'air' not in s['Name']]+[-49]) for z in range(-153,-110)}
    for z in range(-151,-112):
        roof_y=max(-49,tops[z]-2)
        for x in range(268,296):
            put(x,roof_y,z,'deepslate_bricks');slab(x,roof_y+1,z)
    for x in range(271,294,5):
        fill(x,-48,-150,x,-48,-114,'stripped_spruce_wood',axis='y')
        for z in (-148,-116):fill(x,-58,z,x,-49,z,'stripped_spruce_wood',axis='y')
        for z in (-141,-132,-123):lamp(x,-49,z)
    # Screens, seating bays and a raised rear reception dais; circulation stays central.
    fill(270,-58,-139,274,-58,-125,'polished_andesite')
    fill(270,-57,-139,270,-52,-125,'spruce_planks')
    for z in range(-138,-124,3):put(271,-56,z,'chiseled_stone_bricks')
    for z in (-144,-120):
        for x in (279,285,290):
            put(x,-58,z,'spruce_fence',waterlogged=False);slab(x,-57,z,'spruce','top');stairs(x+1,-58,z,'west','spruce')
    # Whole entrance assemblies on both gable ends, all original properties retained.
    facade_copy(-84,'main-hall-east')
    facade_copy(-110,'main-hall-west')
    for x in range(293,297):fill(x,-58,-133,x,-55,-131,'air')
    # Copy after openings so the actual original door state remains authoritative.
    facade_copy(-84,'main-hall-east-final')

def veranda(x0,z0,x1,z1):
    fill(x0,-59,z0,x1,-59,z1,'stone_bricks')
    for x in range(x0,x1+1):
        for z in range(z0,z1+1):
            edge=x in (x0,x1) or z in (z0,z1)
            y=-51+(1 if not edge else 0)
            slab(x,y,z)
    if x1-x0>z1-z0:
        posts=[(x,z) for x in range(x0,x1+1,5) for z in (z0,z1)]
    else:posts=[(x,z) for z in range(z0,z1+1,5) for x in (x0,x1)]
    for x,z in posts:
        fill(x,-58,z,x,-52,z,'stripped_spruce_wood',axis='y');lamp(x,-53,z+1 if z==z0 else z-1)
    # Continuous top timber fascia under tile eaves.
    for z in (z0,z1):fill(x0,-52,z,x1,-52,z,'spruce_planks')
    for x in (x0,x1):fill(x,-52,z0,x,-52,z1,'spruce_planks')

def pavilion(cx,cz,r=5,base=-59):
    for dx in range(-r,r+1):
        for dz in range(-r,r+1):
            if abs(dx)+abs(dz)<=r*2-2:put(cx+dx,base,cz+dz,'stone_bricks')
    for dx,dz in [(-r+1,-r+1),(r-1,-r+1),(-r+1,r-1),(r-1,r-1)]:
        fill(cx+dx,base+1,cz+dz,cx+dx,base+7,cz+dz,'stripped_spruce_wood',axis='y')
        lamp(cx+dx,base+5,cz+dz+1)
    for ring in range(r+2,-1,-1):
        y=base+7+(r+2-ring)//2
        for dx in range(-ring,ring+1):
            for dz in range(-ring,ring+1):
                if max(abs(dx),abs(dz))==ring:
                    slab(cx+dx,y+(1 if abs(dx)==ring and abs(dz)==ring else 0),cz+dz)
    put(cx,base+12,cz,'chiseled_deepslate');slab(cx,base+13,cz,'stone_brick')
    for dx in (-2,2):stairs(cx+dx,base+1,cz,'east' if dx<0 else 'west','spruce')

def make():
    raw=json.loads((w.REF/'blocks.json').read_text())
    for k,s in raw.items():
        x,y,z=map(int,k.split(','))
        if 260<=x<=390 and -189<=z<=-74:
            # Keep excavation, water and terrain details as well as all built frames.
            if y>=-60 or s['Name'] not in ('minecraft:dirt','minecraft:bedrock'):
                ORIGINAL[x,y,z]=s
    B.update(copy.deepcopy(ORIGINAL))
    great_hall()
    # Central ring exactly follows the user's broad U-shaped platform.
    veranda(320,-153,351,-148);veranda(320,-117,351,-111)
    veranda(320,-148,325,-117);veranda(346,-148,351,-117)
    # Inner court: open pavilion, lotus pools, narrow paths; keep a clear approach from the original gate.
    pavilion(335,-132,5)
    for za,zb in [(-145,-140),(-124,-119)]:
        for x in range(328,344):
            for z in range(za,zb+1):
                put(x,-61,z,'clay');put(x,-60,z,'water',level=0)
        for x in range(328,344,3):put(x,-59,za+2,'lily_pad')
    path([(353,-132),(342,-132)],1);path([(328,-132),(303,-132),(295,-132)],2)
    # Four different secondary buildings on the four measured rectangular platforms.
    w.room(354,-181,377,-164,'south','study')
    w.room(297,-168,313,-155,'south','study')
    w.room(322,-104,344,-83,'north','tea')
    # Northeast annex second-floor reading balcony, access by a real stair flight.
    fill(357,-51,-178,374,-51,-168,'spruce_planks')
    for x in range(357,375):put(x,-50,-168,'spruce_fence',east=True,west=True,north=False,south=False,waterlogged=False)
    for i in range(8):
        for x in (355,356):
            fill(x,-58+i,-166-i,x,-55+i,-166-i,'air');stairs(x,-59+i,-166-i,'north','spruce')
    fill(355,-51,-175,357,-51,-173,'spruce_planks')
    # Continuous garden routes joining every platform, not just isolated buildings.
    path([(365,-162),(365,-158),(305,-158),(305,-154)],1)
    path([(335,-111),(335,-106),(335,-104)],1)
    path([(305,-158),(305,-132),(305,-108),(315,-99),(321,-94)],1)
    path([(279,-155),(279,-176),(340,-176),(351,-170)],1)
    path([(279,-110),(279,-103),(291,-96),(316,-96)],1)
    # Southwest lake garden: irregular basin, curving stepping-stone route and waterside pavilion.
    for x in range(273,313):
        for z in range(-105,-84):
            if ((x-292)/18)**2+((z+96)/9)**2<1+.13*math.sin(x):
                put(x,-61,z,'clay');put(x,-60,z,'water',level=0)
    path([(278,-103),(285,-99),(291,-96),(300,-94),(310,-90),(315,-85)],1)
    pavilion(302,-85,4)
    # Long grass and texture variation are subordinate to designed paths and rocks.
    for x,z,k in [(276,-176,'cherry'),(287,-180,'oak'),(329,-174,'cherry'),(341,-162,'oak'),(273,-92,'oak'),(315,-87,'cherry'),(311,-113,'oak')]:tree(x,z,k)
    for x,z in [(285,-165),(335,-166),(277,-87),(311,-104)]:
        for dx,dz,h in [(0,0,3),(1,0,2),(0,1,1),(-1,1,2)]:fill(x+dx,-59,z+dz,x+dx,-60+h,z+dz,'andesite')
    for x,z in [(271,-173),(273,-173),(275,-172),(338,-180),(340,-179),(342,-180)]:
        for y in range(-59,-52):put(x,y,z,'bamboo',age=1,leaves='large' if y>-56 else 'small',stage=0)
    for x,z in [(305,-149),(305,-140),(305,-124),(305,-115),(315,-98),(340,-108),(351,-158),(319,-159),(284,-174),(279,-108),(314,-86)]:lightpost(x,z)
    # Enclosing wall sections have stepped dark coping and repeating timber/stone detail.
    for z in (-183,-81):
        for x in range(267,380):
            fill(x,-59,z,x,-55,z,'smooth_quartz');put(x,-59,z,'stone_bricks');slab(x,-54,z)
            if x%8==0:put(x,-54,z,'chiseled_deepslate');slab(x,-53,z,'stone_brick')
    for x in (267,379):
        for z in list(range(-182,-154))+list(range(-110,-81)):
            fill(x,-59,z,x,-55,z,'smooth_quartz');put(x,-59,z,'stone_bricks');slab(x,-54,z)
    # Entire completed east court and its projecting eaves stay as supplied, including empty door spaces.
    for p,s in ORIGINAL.items():B[p]=copy.deepcopy(s)
    # Keep the sample forecourt itself open: no new room inserted into its original garden.
    for p in list(B):
        x,y,z=p
        if 352<=x<=388 and -154<=z<=-110 and p not in ORIGINAL and y>-60:
            B.pop(p)

def plan():
    im=Image.new('RGB',(1160,1050),'#53644b');d=ImageDraw.Draw(im)
    top={}
    for (x,y,z),s in B.items():
        if s['Name']=='minecraft:air':continue
        if (x,z) not in top or top[x,z][0]<y:top[x,z]=(y,s)
    for (x,z),(y,s) in top.items():
        name=s['Name'];c='#aeb0a5'
        if 'deepslate' in name:c='#39444b'
        elif 'leaves' in name:c='#d7a0b1' if 'cherry' in name else '#62804d'
        elif 'water' in name:c='#4f91a6'
        elif any(k in name for k in ['wood','planks','spruce','oak']):c='#92724b'
        elif any(k in name for k in ['quartz','calcite','diorite']):c='#ebe7d9'
        elif 'bamboo' in name:c='#8ba65e'
        px=(x-253)*8;py=(z+194)*8;d.rectangle((px,py,px+7,py+7),fill=c)
    d.rectangle(((267-253)*8,(-183+194)*8,(379-253)*8,(-81+194)*8),outline='#e1b970',width=2)
    for x in range(260,391,10):d.text(((x-253)*8,5),str(x),fill='white')
    for z in range(-190,-73,10):d.text((4,(z+194)*8),str(z),fill='white')
    im.save(w.OUT/'plan.png')

def verify():
    assert all(B[p]==s for p,s in ORIGINAL.items()),'Player original changed'
    # Complete copied facade keeps all 3D offsets; intersecting older ground-frame markers may supersede bottom stones only.
    for label,dx,source in COPIES:
        lost=[p for p,s in source.items() if p[1]>-59 and B.get((p[0]+dx,p[1],p[2]))!=s]
        assert not lost,(label,'copied volume lost',lost[:5])
    report={'frame_outer':{'x':[267,379],'z':[-183,-81],'size':[113,103]},'interior_size':[111,101],
            'original_preserved':len(ORIGINAL),'explicit_states':len(B),'facade_copies':[(label,len(s)) for label,dx,s in COPIES],
            'full_bounds':[[min(p[i] for p in B),max(p[i] for p in B)] for i in range(3)],'destination':str(w.DEST)}
    (w.OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(report,flush=True)

if __name__=='__main__':
    w.OUT.mkdir(exist_ok=True);make();verify();plan()
    (w.OUT/'blocks.json').write_text(json.dumps({','.join(map(str,p)):s for p,s in B.items()}))
    print(w.write_world(),flush=True)
