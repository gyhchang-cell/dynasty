"""Complete a measured player courtyard in a NEW flat save. Never write the reference save."""
import copy,gzip,io,json,math,struct,time,zlib,hashlib
from collections import Counter,defaultdict
from pathlib import Path
import nbtlib as n
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
REF=ROOT/'build/courtyard-reference'
OUT=ROOT/'build/courtyard-completion'
DEST=Path('/Users/a15356015027/Public/.minecraft/versions/Dynasty 王朝/saves/徽院试建-独立存档')
B={}; ORIGINAL={}
CHUNK_BOUNDS=(19,28,-13,-3)
WORLD_NAME='徽院试建 · 独立完成版'
def state(name,**props):
    v={'Name':name if ':' in name else 'minecraft:'+name}
    if props:v['Properties']={k:str(v).lower() for k,v in props.items()}
    return v
def put(x,y,z,name,**props): B[x,y,z]=state(name,**props)
def fill(x0,y0,z0,x1,y1,z1,name,**props):
    for x in range(x0,x1+1):
        for y in range(y0,y1+1):
            for z in range(z0,z1+1):put(x,y,z,name,**props)
def stairs(x,y,z,facing,material='deepslate_brick',half='bottom'):
    put(x,y,z,material+'_stairs',facing=facing,half=half,shape='straight',waterlogged=False)
def slab(x,y,z,material='deepslate_brick',typ='bottom'):
    put(x,y,z,material+'_slab',type=typ,waterlogged=False)
def beam(x0,y,z0,x1,z1):fill(x0,y,z0,x1,y,z1,'stripped_spruce_wood',axis='y')
def lamp(x,y,z):put(x,y,z,'lantern',hanging=True,waterlogged=False)
def lattice(x,y,z):put(x,y,z,'spruce_fence',north=True,south=True,east=False,west=False,waterlogged=False)

def roof(x0,z0,x1,z1,eave):
    # Ridge parallel to Z; a curved, shallow two-sided tiled roof with lifted corners.
    mid=(x0+x1)//2;half=max(mid-x0,x1-mid)
    for x in range(x0,x1+1):
        dist=abs(x-mid);y=eave+int((half-dist)*0.65)
        for z in range(z0,z1+1):
            lift=1 if dist>=half-1 and z in (z0,z1) else 0
            if x==mid:put(x,y+lift,z,'deepslate_bricks')
            else:stairs(x,y+lift,z,'east' if x<mid else 'west')
            if dist==half:slab(x,y-1+lift,z)
    ridge=eave+int(half*.65)
    for z in range(z0,z1+1):slab(mid,ridge+1,z,'stone_brick')
    for z in (z0,z1):
        put(mid,ridge+1,z,'chiseled_deepslate');slab(mid,ridge+2,z,'stone_brick')
    # Visible underside rafters at regular bays, not an empty roof shell.
    for z in range(z0+1,z1,3):beam(x0+1,eave-1,z,x1-1,z)

def room(x0,z0,x1,z1,door_side,kind):
    fill(x0,-59,z0,x1,-59,z1,'spruce_planks')
    fill(x0,-58,z0,x1,-53,z1,'air')
    for x in range(x0,x1+1):
        for z in range(z0,z1+1):
            if x in (x0,x1) or z in (z0,z1):
                fill(x,-58,z,x,-53,z,'smooth_quartz')
                put(x,-58,z,'stone_bricks')
    for x in (x0,x1):
        for z in (z0,(z0+z1)//2,z1):fill(x,-58,z,x,-52,z,'stripped_spruce_wood',axis='y')
    midz=(z0+z1)//2;midx=(x0+x1)//2
    if door_side=='east':
        fill(x1,-58,midz-1,x1,-55,midz+1,'air')
        for z in (midz-4,midz+4):
            fill(x1,-56,z,x1,-54,z,'air')
            for y in range(-56,-53):lattice(x1,y,z)
        stairs(x1+1,-59,midz,'west','stone_brick')
    else:
        z=z1 if door_side=='south' else z0
        fill(midx-1,-58,z,midx+1,-55,z,'air')
        for x in (x0+2,x1-2):
            fill(x,-56,z,x,-54,z,'spruce_fence',east=True,west=True,north=False,south=False,waterlogged=False)
    # White gable infill and timber headers.
    for z in (z0,z1):
        for x in range(x0,x1+1):
            h=int((min(x-x0,x1-x))*.65)
            fill(x,-52,z,x,-51+h,z,'smooth_quartz')
    roof(x0-1,z0-1,x1+1,z1+1,-51)
    lamp(midx,-53,midz)
    if kind=='hall':
        fill(x0+1,-58,z0+2,x0+1,-55,z1-2,'bookshelf')
        for z in range(z0+3,z1-1,3):
            put(x0+3,-58,z,'spruce_fence',waterlogged=False)
            slab(x0+3,-57,z,'spruce','top')
            stairs(x0+4,-58,z,'west','spruce')
        fill(x0+1,-58,midz-1,x0+2,-57,midz+1,'chiseled_stone_bricks')
        put(x0+2,-56,midz,'flower_pot')
    elif kind=='study':
        fill(x0+1,-58,z0+1,x1-1,-56,z0+1,'bookshelf')
        put(midx,-58,midz,'lectern',facing='south',has_book=False,powered=False)
        put(x0+1,-58,z1-1,'crafting_table')
        put(x1-1,-58,z1-1,'barrel',facing='up',open=False)
    else:
        for x in (x0+2,x1-2):
            put(x,-58,midz,'spruce_fence',waterlogged=False);slab(x,-57,midz,'spruce','top')
            stairs(x,-58,midz+1,'north','spruce')
        put(x1-1,-58,z1-1,'cauldron')

def build():
    src=json.loads((REF/'blocks.json').read_text())
    for k,s in src.items():
        p=tuple(map(int,k.split(',')));x,y,z=p
        if 351<=x<=387 and -154<=z<=-110 and y>=-60 and s['Name']!='minecraft:structure_block':
            B[p]=s;ORIGINAL[p]=s
    # Three deliberately different volumes around a planted open courtyard.
    room(355,-138,362,-126,'east','hall')
    room(366,-151,376,-143,'south','study')
    room(366,-121,376,-113,'north','tea')
    # Stone paths, alternating inset slabs and inset green pockets.
    for x in range(354,379):
        for z in range(-152,-111):
            if 363<=x<=365 or -134<=z<=-130 or (364<=x<=376 and z in (-142,-141,-123,-122)):
                put(x,-60,z,'stone_bricks' if (x+z)%5 else 'mossy_stone_bricks')
    # East-side sheltered gallery, with clear central gate passage.
    for za,zb in [(-143,-136),(-128,-121)]:
        fill(374,-59,za,376,-59,zb,'stone_bricks')
        for z in range(za,zb+1,3):
            fill(374,-58,z,374,-53,z,'stripped_spruce_wood',axis='y');lamp(375,-54,z)
        roof(373,za,377,zb,-52)
    # Stepped coping follows the sample's material palette on the two plain enclosure walls.
    for z in (-153,-111):
        for x in range(353,379):
            slab(x,-48,z)
            if (x-353)%5==0:put(x,-49,z,'chiseled_deepslate')
    # Reuse the player's upper horse-head wall, translated to the opposite boundary.
    # The original small west gate is preserved below the copied crown.
    for (x,y,z),s in ORIGINAL.items():
        if x==379 and y>=-49:
            B[353,y,z]=copy.deepcopy(s)
    # Courtyard pond with stepped edges, lilies, stone island and a small crossing.
    for x in range(366,373):
        for z in range(-140,-135):
            edge=x in (366,372) or z in (-140,-136)
            put(x,-61,z,'clay');put(x,-60,z,'stone_bricks' if edge else 'water',**({} if edge else {'level':0}))
    for x,z in [(368,-138),(371,-137)]:put(x,-59,z,'lily_pad')
    for z in range(-140,-135):slab(370,-59,z,'spruce')
    # Rock and bamboo garden south of the principal axis; keep player's corner vegetation.
    for x,z,h in [(368,-126,2),(371,-125,3),(367,-124,1)]:
        fill(x,-59,z,x,-60+h,z,'andesite');slab(x,-59+h,z,'stone_brick')
    for x,z in [(369,-127),(372,-126),(367,-125)]:
        for y in range(-59,-54):put(x,y,z,'bamboo',age=1,leaves='large' if y>=-56 else 'small',stage=0)
    # Benches, flower pots and soft nighttime lighting under the eaves.
    for z in (-141,-123):
        for x in (359,361):stairs(x,-59,z,'south' if z==-141 else 'north','spruce')
    for x,z in [(363,-139),(363,-125),(365,-142),(365,-122)]:
        put(x,-59,z,'stone_brick_wall',up=True,north='none',south='none',east='none',west='none',waterlogged=False)
        put(x,-58,z,'lantern',hanging=False,waterlogged=False)
    # Preserve every completed reference block; additions occupy only previously empty spaces.
    # Source greenery is part of the composition, not scaffolding to be erased.
    B.update(copy.deepcopy(ORIGINAL))

def palette_section(sy,cx,cz):
    palette=[];lookup={};values=[]
    for y in range(sy*16,sy*16+16):
        for z in range(cz*16,cz*16+16):
            for x in range(cx*16,cx*16+16):
                default='bedrock' if y==-64 else 'dirt' if -63<=y<=-61 else 'grass_block' if y==-60 else 'air'
                s=B.get((x,y,z),state(default));key=json.dumps(s,sort_keys=True)
                if key not in lookup:lookup[key]=len(palette);palette.append(n.Compound(s))
                values.append(lookup[key])
    # Compound constructor does not recursively tag Python values.
    tagged=[]
    for p in palette:
        v=n.Compound({'Name':n.String(p['Name'])})
        if 'Properties' in p:v['Properties']=n.Compound({k:n.String(vv) for k,vv in p['Properties'].items()})
        tagged.append(v)
    bs=n.Compound({'palette':n.List[n.Compound](tagged)})
    if len(tagged)>1:bs['data']=pack(values,max(4,(len(tagged)-1).bit_length()))
    return n.Compound({'Y':n.Byte(sy),'block_states':bs,'biomes':n.Compound({'palette':n.List[n.String]([n.String('minecraft:plains')])})})

def pack(values,bits):
    per=64//bits;words=[]
    for start in range(0,len(values),per):
        v=sum(int(q)<<(i*bits) for i,q in enumerate(values[start:start+per]))
        words.append(v if v<2**63 else v-2**64)
    return n.LongArray(words)
def write_world():
    if DEST.exists():raise RuntimeError('Refusing to overwrite existing world: '+str(DEST))
    stage=OUT/'world';stage.mkdir(parents=True,exist_ok=False)
    level=n.load(REF/'snapshot/level.dat');d=level['Data']
    for key in ['Player','DragonFight','CustomBossEvents','WanderingTraderId']:d.pop(key,None)
    d['LevelName']=n.String(WORLD_NAME);d['GameType']=n.Int(1);d['allowCommands']=n.Byte(1)
    d['SpawnX']=n.Int(394);d['SpawnY']=n.Int(-59);d['SpawnZ']=n.Int(-132);d['SpawnAngle']=n.Float(90)
    d['Time']=n.Long(6000);d['DayTime']=n.Long(6000);d['LastPlayed']=n.Long(int(time.time()*1000))
    d['raining']=n.Byte(0);d['thundering']=n.Byte(0);d['Difficulty']=n.Byte(0)
    for k in ['doMobSpawning','doWeatherCycle','doDaylightCycle','doFireTick']:d['GameRules'][k]=n.String('false')
    d['GameRules']['spawnRadius']=n.String('0')
    gen=d['WorldGenSettings']['dimensions']['minecraft:overworld']['generator']
    assert str(gen['type'])=='minecraft:flat'
    gen['settings']['structure_overrides']=n.List[n.String]([])
    gen['settings']['layers'][1]['height']=n.Int(3)
    level.save(stage/'level.dat',gzipped=True)
    regions=defaultdict(dict)
    column_tops={}
    for (x,y,z),s in B.items():
        if s['Name']!='minecraft:air':column_tops[x,z]=max(column_tops.get((x,z),-60),y)
    for cx in range(CHUNK_BOUNDS[0],CHUNK_BOUNDS[1]):
        for cz in range(CHUNK_BOUNDS[2],CHUNK_BOUNDS[3]):
            heights=[]
            for z in range(cz*16,cz*16+16):
                for x in range(cx*16,cx*16+16):
                    h=column_tops.get((x,z),-60)
                    heights.append(h+65)
            entities=[]
            for (bx,by,bz),s in B.items():
                if bx//16==cx and bz//16==cz and s['Name'] in ('minecraft:barrel','minecraft:lectern'):
                    entities.append(n.Compound({'id':n.String(s['Name']),'x':n.Int(bx),'y':n.Int(by),'z':n.Int(bz)}))
            chunk=n.Compound({'DataVersion':n.Int(3465),'xPos':n.Int(cx),'yPos':n.Int(-4),'zPos':n.Int(cz),
                'Status':n.String('minecraft:full'),'isLightOn':n.Byte(0),'LastUpdate':n.Long(0),'InhabitedTime':n.Long(0),
                'sections':n.List[n.Compound]([palette_section(sy,cx,cz) for sy in range(-4,20)]),
                'block_entities':n.List[n.Compound](entities),'block_ticks':n.List[n.Compound]([]),'fluid_ticks':n.List[n.Compound]([]),
                'PostProcessing':n.List[n.List[n.Short]]([n.List[n.Short]([]) for _ in range(24)]),
                'Heightmaps':n.Compound({k:pack(heights,9) for k in ['WORLD_SURFACE','MOTION_BLOCKING','MOTION_BLOCKING_NO_LEAVES','OCEAN_FLOOR']}),
                'structures':n.Compound({'starts':n.Compound({}),'References':n.Compound({})})})
            stream=io.BytesIO();n.File(chunk).write(stream);payload=zlib.compress(stream.getvalue())
            regions[cx//32,cz//32][(cx%32)+(cz%32)*32]=payload
    (stage/'region').mkdir()
    for (rx,rz),cs in regions.items():
        header=bytearray(8192);body=bytearray();sector=2
        for slot,payload in sorted(cs.items()):
            raw=struct.pack('>I',len(payload)+1)+b'\x02'+payload;size=(len(raw)+4095)//4096
            header[slot*4:slot*4+4]=struct.pack('>I',(sector<<8)|size)
            header[4096+slot*4:4100+slot*4]=struct.pack('>I',int(time.time()))
            body.extend(raw+b'\0'*(size*4096-len(raw)));sector+=size
        (stage/'region'/f'r.{rx}.{rz}.mca').write_bytes(header+body)
    return stage

def render(full=False):
    # Software voxel preview from actual output states, not an AI concept image.
    im=Image.new('RGB',(1600,1200),'#c5d2d7');draw=ImageDraw.Draw(im)
    def color(s):
        name=s['Name'];c=(132,108,76)
        if any(k in name for k in ['quartz','calcite','diorite','powder']):c=(223,219,203)
        elif 'deepslate' in name:c=(56,67,75)
        elif 'stone' in name or 'andesite' in name:c=(126,132,129)
        elif 'leaves' in name:c=(200,139,153) if 'cherry' in name else (74,115,64)
        elif 'bamboo' in name:c=(101,132,67)
        elif 'water' in name:c=(67,145,163)
        elif 'lantern' in name:c=(240,183,80)
        elif 'spruce' in name:c=(94,71,47)
        return c
    def proj(x,y,z):
        if full:return (800+(x-325-z-132)*6,650-(y+60)*9+(z+132+x-325)*3)
        return (800+(x-369-z-132)*16,860-(y+60)*19+(z+132+x-369)*8)
    # View from east/south, so the player's original gate remains the foreground landmark.
    for (x,y,z),s in sorted(B.items(),key=lambda q:(q[0][0]+q[0][2],q[0][1])):
        if s['Name']=='minecraft:air':continue
        x0,x1=x,x+1;y0,y1=y,y+1;z0,z1=z,z+1
        name=s['Name'];props=s.get('Properties',{})
        if 'slab' in name:
            if props.get('type')=='top':y0=y+.5
            elif props.get('type')!='double':y1=y+.5
        if any(k in name for k in ['fence','bamboo','lantern','flower_pot']):x0+=.3;x1-=.3;z0+=.3;z1-=.3
        c=color(s)
        faces=[([(x1,y0,z0),(x1,y0,z1),(x1,y1,z1),(x1,y1,z0)],.77,(x+1,y,z)), ([(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],.88,(x,y,z+1)), ([(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)],1.08,(x,y+1,z))]
        for poly,factor,neighbor in faces:
            other=B.get(neighbor,{}).get('Name','air')
            if other not in ('air','minecraft:air') and not any(k in other for k in ['slab','stairs','fence','bamboo','lantern','trapdoor','leaves','wall','door']):continue
            draw.polygon([proj(*p) for p in poly],fill=tuple(min(255,int(v*factor)) for v in c))
    im.save(OUT/'preview.png')

def main():
    OUT.mkdir(exist_ok=True);build();render()
    (OUT/'blocks.json').write_text(json.dumps({','.join(map(str,p)):s for p,s in B.items()}))
    print('Original',len(ORIGINAL),'Output',len(B),'preserved',sum(B[p]==s for p,s in ORIGINAL.items()),flush=True)
    stage=write_world()
    print('Staged world:',stage,flush=True)
if __name__=='__main__':main()
