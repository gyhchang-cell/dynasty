"""Five ordinary people: original Minecraft pixels, not four-color portraits.

User's latest requirements 00.10/11/19/20 take precedence for these targets.
The shared generator preserves rigs/held tools; eyes and hair live on the head
UV instead of floating cuboids. Never paints or imports reference asset pixels.
"""
import copy
import hashlib
import io
import json
import math
from PIL import Image, ImageDraw

IDS={'bandit_thug','night_watchman','herb_picker','famished_refugee','swindler'}
STYLE={
    'bandit_thug':('#73594f','#b88c6b','#84614b','#d3aa81'),
    'night_watchman':('#4c6678','#c89d79','#997053','#e4bc97'),
    'herb_picker':('#667b54','#c39d78','#947255','#dfbb91'),
    'famished_refugee':('#85735e','#b8a186','#88745f','#d1b99d'),
    'swindler':('#72637d','#cfac89','#a38163','#e7c7a2'),
}


def palette(id):
    cloth,skin,skin_dark,skin_light=STYLE[id]
    c=tuple(int(cloth[i:i+2],16) for i in (1,3,5))
    shift=lambda d:'#%02x%02x%02x'%tuple(max(0,min(255,v+d)) for v in c)
    return dict(cloth=cloth,cloth_dark=shift(-20),cloth_light=shift(18),
        skin=skin,skin_dark=skin_dark,skin_light=skin_light,
        hair='#3a302b',hair_dark='#272725',hair_light='#60513f',
        eye='#ede7d8',iris='#414e49',
        linen='#d5c8ac',linen_dark='#9d917a',linen_light='#e4d9bf',
        leather='#72543d',leather_dark='#493b30',leather_light='#96754f',
        wood='#a48752',wood_dark='#715a37',wood_light='#c8af76',
        metal='#7a898d',metal_dark='#414e55',metal_light='#b5bdba',
        brass='#a58b53',brass_dark='#715d38',brass_light='#d0bb81',
        leaf='#5e7445',leaf_dark='#3a5135',leaf_light='#87955d',
        lamp='#dec789',lamp_dark='#a18753',lamp_light='#f0e1ad')


def material(id,bone,index):
    if bone=='head':return 'face'
    if bone=='neck' or bone.endswith('_hand'):return 'skin'
    if bone.endswith('_forearm'):
        return 'cloth' if id in ('night_watchman','swindler') else 'skin'
    if bone.endswith(('_foot','_shin')):return 'leather'
    if bone=='waist':return 'leather'
    if bone in ('helmet','armor','left_pauldron','skirt'):
        return 'metal' if bone!='skirt' or index==0 else 'leather'
    if bone=='blade':return 'wood' if index==0 else 'brass' if index==1 else 'metal'
    if bone=='mask':return 'cloth'
    if bone=='lantern':return ('wood','lamp','brass','wood')[index]
    if bone=='clapper':return 'wood'
    if bone=='cap':return 'cloth'
    if bone=='vest':return 'cloth' if index==0 else 'leather'
    if bone=='hat':return 'wood'
    if bone=='basket':return 'leaf' if index>=2 else 'wood'
    if bone=='straps':return 'leather'
    if bone=='sickle':return 'wood' if index==0 else 'metal'
    if bone=='staff':return 'wood'
    if bone in ('rags','bundle'):return 'linen' if index==0 else 'leather'
    if bone=='crown':return 'cloth' if index==0 else 'linen'
    if bone=='abacus':return 'wood' if index<4 else 'brass'
    return 'cloth'


def paint(id,key):
    mat,bone,side,w,h=key;p=palette(id)
    tile=Image.new('RGB',(w,h),p['skin' if mat=='face' else mat]);d=ImageDraw.Draw(tile)
    def rect(x0,y0,x1,y1,col):
        x0=max(0,x0);y0=max(0,y0);x1=min(w-1,x1);y1=min(h-1,y1)
        if x0<=x1 and y0<=y1:d.rectangle((x0,y0,x1,y1),fill=p[col])
    if mat=='face':
        if side=='north':
            rect(0,0,w-1,0,'hair');rect(0,1,0,2,'hair');rect(w-1,1,w-1,2,'hair')
            rect(1,2,2,2,'hair');rect(w-3,2,w-2,2,'hair')
            rect(1,3,2,3,'eye');rect(w-3,3,w-2,3,'eye')
            rect(2,3,2,3,'iris');rect(w-3,3,w-3,3,'iris')
            rect(w//2,4,w//2,4,'skin_dark');rect(w//2-1,5,w//2,5,'skin_dark')
            if id in ('herb_picker','night_watchman'):
                rect(1,6,w-2,6,'hair');rect(w//2,5,w//2,5,'hair')
            if id=='famished_refugee':
                rect(0,4,1,4,'skin_dark');rect(w-2,4,w-1,4,'skin_dark')
            if id=='swindler':rect(2,5,4,5,'hair')
        elif side in ('east','west'):
            # UV wall faces run in opposite local depth directions.
            rear=range(w//2,w) if side=='east' else range(0,w-w//2)
            rect(0,0,w-1,1,'hair')
            for x in rear:rect(x,2,x,h-1,'hair')
            x=w//2-1 if side=='east' else w//2
            rect(x,3,x,4,'skin_dark')
        elif side in ('south','up'):
            rect(0,0,w-1,h-1,'hair');rect(1,0,1,max(0,h-2),'hair_light')
        return tile
    if mat=='skin':
        if w>=3 and h>=3:rect(0,h-1,w-1,h-1,'skin_dark')
    elif mat=='cloth':
        if w>=4 and h>=3:
            rect(0,0,0,h-1,'cloth_dark');rect(w-1,0,w-1,h-1,'cloth_dark')
            rect(1,h-1,w-2,h-1,'cloth_dark')
        if bone=='chest' and side=='north':
            for y in range(min(4,h)):rect(1+y,y,min(w-2,2+y),y,'linen')
        if bone=='robe' and h>=4:rect(1,h-2,w-2,h-2,'linen_dark')
        if bone in ('cap','crown') and side=='north':rect(w//2,0,w//2,1,'linen')
        if id=='famished_refugee' and bone in ('chest','pelvis') and w>=4:
            rect(1,h-3,2,h-2,'linen_dark')
        if bone.endswith('_forearm'):rect(0,h-1,w-1,h-1,'linen_dark')
    elif mat in ('wood','leather','metal','brass','linen','leaf','lamp'):
        if h>=3:rect(0,h-1,w-1,h-1,mat+'_dark')
        if w>=3:rect(1,0,w-2,0,mat+'_light')
        if mat=='wood' and w>=5 and h>=4:
            if bone=='basket':
                for y in range(2,h-1,3):rect(0,y,w-1,y,'wood_dark')
                rect(w//2,1,w//2,h-2,'wood_dark')
            elif bone=='hat':
                rect(1,h//2,w-2,h//2,'wood_dark')
            else:rect(w//2,1,w//2,h-2,'wood_dark')
        if mat=='metal' and bone=='armor' and w>=6 and h>=4:
            rect(1,2,w-2,2,'metal_dark')
            for x in range(1,w-1,3):rect(x,0,x,0,'brass')
        if mat=='lamp' and w>=3 and h>=3:
            rect(0,0,0,h-1,'wood_dark');rect(w-1,0,w-1,h-1,'wood_dark')
        if mat=='leather' and bone=='waist' and side=='north':rect(w//2,0,w//2,1,'brass')
        if mat=='leaf' and w>=2 and h>=2:rect(0,0,0,h-1,'leaf_dark')
    return tile


def render(id,document):
    geo=copy.deepcopy(document);g=geo['minecraft:geometry'][0];tiles={};faces=[]
    for b in g['bones']:
        for i,c in enumerate(b.get('cubes',[])):
            x,y,z=c['size'];dims={'north':(x,y),'south':(x,y),'east':(z,y),'west':(z,y),'up':(x,z),'down':(x,z)}
            mat=material(id,b['name'],i)
            for side in c['uv']:
                w,h=(max(1,math.ceil(v)) for v in dims[side])
                key=(mat,b['name'],side,w,h)
                tiles.setdefault(key,paint(id,key));faces.append((c,side,key))
    size=128;placement={};x=y=2;row=0
    for key,tile in sorted(tiles.items(),key=lambda kv:(-kv[0][4],-kv[0][3],kv[0])):
        w,h=tile.size
        if x+w+2>size:x=2;y+=row;row=0
        if y+h+2>size:raise ValueError('Atlas overflow '+id)
        placement[key]=(x,y);x+=w+4;row=max(row,h+4)
    atlas=Image.new('RGB',(size,size),palette(id)['hair_dark'])
    for key,tile in tiles.items():
        x,y=placement[key];w,h=tile.size
        for yy in range(-2,h+2):
            for xx in range(-2,w+2):
                atlas.putpixel((x+xx,y+yy),tile.getpixel((min(w-1,max(0,xx)),min(h-1,max(0,yy)))))
    for c,side,key in faces:c['uv'][side]={'uv':list(placement[key]),'uv_size':list(tiles[key].size)}
    g['description'].update(texture_width=size,texture_height=size)
    raw=io.BytesIO();atlas.save(raw,format='PNG')
    colors=atlas.getcolors(256);assert colors is not None and len(colors)<=36
    record={'atlas':[size,size],'palette':['#%02x%02x%02x'%rgb for _,rgb in sorted(colors,key=lambda v:v[1])],
        'colors':len(colors),'faces':len(faces),'islands':len(tiles),'gutter':2,
        'geometryChanged':True,'animationsChanged':False,'policy':'2026-10-11 ordinary-human requirements 00.10/11/19/20',
        'islandData':[{'bone':k[1],'material':k[0],'face':k[2],'uv':list(placement[k]),'size':list(tiles[k].size)} for k in placement]}
    return geo,raw.getvalue(),record


def export_one(id,geo,asset):
    geo,png,record=render(id,geo)
    (asset/f'geo/secondary/{id}.geo.json').write_text(json.dumps(geo,indent=2)+'\n')
    (asset/f'textures/entity/secondary/{id}.png').write_bytes(png)
    return record


def generated():
    from build_models import Rig,ASSET
    import build_humans
    original=Rig.save
    try:
        Rig.save=lambda self:self
        rigs=[f() for f in (build_humans.bandit,build_humans.watchman,build_humans.herb,build_humans.refugee,build_humans.swindler)]
    finally:Rig.save=original
    result={}
    for r in rigs:
        desc=json.loads((ASSET/f'geo/secondary/{r.id}.geo.json').read_text())['minecraft:geometry'][0]['description']
        doc={'format_version':'1.12.0','minecraft:geometry':[{'description':desc,'bones':r.bones}]}
        result[r.id]=render(r.id,doc)
    return result


def main():
    from build_models import ASSET,REPO,OUT
    target=REPO/'docs/art/secondary-humans-v3';target.mkdir(parents=True,exist_ok=True)
    before=json.loads((REPO/'build/maintenance/secondary-humans-v3/before-manifest.json').read_text())
    batch=generated();writes={};report={}
    for id,(geo,png,record) in batch.items():
        writes[ASSET/f'geo/secondary/{id}.geo.json']=(json.dumps(geo,indent=2)+'\n').encode()
        writes[ASSET/f'textures/entity/secondary/{id}.png']=png;report[id]=record
    for p in writes:
        if hashlib.sha256(p.read_bytes()).hexdigest()!=before[str(p.relative_to(REPO))]:raise RuntimeError('Concurrent/previous edit: '+str(p))
    for p,data in writes.items():
        if hashlib.sha256(p.read_bytes()).hexdigest()!=before[str(p.relative_to(REPO))]:raise RuntimeError('Concurrent edit: '+str(p))
        temp=p.with_suffix(p.suffix+'.human-tmp');temp.write_bytes(data);temp.replace(p)
    manifest=json.loads((OUT/'model-manifest.json').read_text())
    for id,record in report.items():
        g=batch[id][0]['minecraft:geometry'][0]
        manifest[id].update(atlas=record['atlas'],palette=record['palette'],materialPolicy=record['policy'],
            bones=len(g['bones']),cuboids=sum(len(b.get('cubes',[])) for b in g['bones']))
        for k in ('pixelBlock','whiteMargin'):manifest[id].pop(k,None)
    (OUT/'model-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    p=OUT/'pixel16-export.json';legacy=json.loads(p.read_text())
    for id in IDS:legacy.pop(id,None)
    p.write_text(json.dumps(legacy,indent=2)+'\n')
    (target/'atlases.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Exported five real human rigs and original per-face pixel atlases')


if __name__=='__main__':main()
