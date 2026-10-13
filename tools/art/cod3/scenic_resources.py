#!/usr/bin/env python3
"""Original non-entity scenic rigs. Geometry/UV/animation source, not render mockups."""
from pathlib import Path
import base64, copy, json, math, uuid
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
A = ROOT / 'src/main/resources/assets/dynasty'
D = ROOT / 'docs/art/cod3-scenic-v1'
FACES = ('north', 'south', 'east', 'west', 'up', 'down')
PALETTES = {
    'azure_dragon': ['#193d42','#326b64','#579184','#9fc2a2','#d7d8ab','#736c42'],
    'mountain_xuanwu': ['#202c30','#3d5051','#687467','#9caa88','#c0bda2','#697742'],
    'sun_crow': ['#392b24','#71512b','#af7b35','#d4a24c','#efd18a','#7a3c29'],
}

def dump(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

class Rig:
    def __init__(self, name):
        self.name=name; self.bones=[]; self.by_name={}; self.tracks={}
    def bone(self, name, parent, pivot):
        b={'name':name,'pivot':list(pivot),'cubes':[]}
        if parent: b['parent']=parent
        self.bones.append(b); self.by_name[name]=b
        return name
    def box(self, bone, origin, size, mat=2):
        self.by_name[bone]['cubes'].append({'origin':list(origin),'size':list(size),'_material':mat})
    def motion(self, bone, channel, values):
        self.tracks.setdefault(bone,{})[channel]={str(i):v for i,v in enumerate(values)}
    def export(self):
        texture=A/f'textures/entity/scenic/{self.name}.png'
        colors=PALETTES[self.name]
        # Allocate individual face rectangles at a consistent 0.5 pixel per model unit.
        # UV area follows actual aspect/area; skinny appendages no longer stretch square swatches.
        tiles=[]
        for b in self.bones:
            for c in b['cubes']:
                w,h,d=c['size']; c['uv']={}
                for face,(fw,fh) in zip(FACES,[(w,h),(w,h),(d,h),(d,h),(w,d),(w,d)]):
                    tw,th=max(2,math.ceil(fw*.5)),max(2,math.ceil(fh*.5))
                    tiles.append((c,face,tw,th,c['_material']))
        for side in (128,256):
            x=y=1;row=0; placements=[]
            for c,f,w,h,m in sorted(tiles,key=lambda t:-t[3]):
                if x+w+1>side:x=1;y+=row+2;row=0
                if y+h+1>side:break
                placements.append((c,f,x,y,w,h,m));x+=w+2;row=max(row,h)
            else:break
        assert len(placements)==len(tiles),'Atlas allocation failed'
        im=Image.new('RGB',(side,side),colors[0]); draw=ImageDraw.Draw(im)
        for c,f,x,y,w,h,m in placements:
            c['uv'][f]={'uv':[x,y],'uv_size':[w,h]}
            base=tuple(bytes.fromhex(colors[m][1:])); factor=1.10 if f=='up' else .78 if f=='down' else 1
            col=tuple(min(255,round(v*factor)) for v in base)
            draw.rectangle((x-1,y-1,x+w,y+h),fill=col)
            if w>=7 and h>=6 and m not in (0,4):
                high=tuple(min(255,round(v*1.12)) for v in col)
                low=tuple(round(v*.84) for v in col)
                draw.rectangle((x+1,y+1,x+w-2,y+2),fill=high)
                if f not in ('up','down'):
                    # Ordered scale/feather clusters, confined to broad surfaces.
                    for yy in range(y+5,y+h-2,6):
                        for xx in range(x+2+(3 if (yy-y)//6%2 else 0),x+w-3,8):
                            draw.rectangle((xx,yy,xx+2,yy+1),fill=low)
        for b in self.bones:
            for c in b['cubes']:c.pop('_material')
        texture.parent.mkdir(parents=True,exist_ok=True); im.save(texture)
        geo={'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.'+self.name,'texture_width':side,'texture_height':side,'visible_bounds_width':32,'visible_bounds_height':24,'visible_bounds_offset':[0,8,0]},'bones':self.bones}]}
        animation={'format_version':'1.8.0','animations':{'animation.scenic.idle':{'loop':True,'animation_length':4,'bones':self.tracks}}}
        dump(A/f'geo/scenic/{self.name}.geo.json',geo)
        lod_counts={}
        for lod in ('medium','far'):
            reduced=copy.deepcopy(geo)
            for b in reduced['minecraft:geometry'][0]['bones']:
                name=b['name'];cubes=b['cubes']
                if lod=='medium':
                    b['cubes']=[c for c in cubes if min(c['size'])>=2 and not (name=='shell' and min(c['size'])==3)]
                    if self.name=='azure_dragon':
                        if name.startswith('trunk_'):b['cubes']=cubes[:2] if int(name.split('_')[1])%2 else cubes
                        elif 'limb' in name:b['cubes']=cubes[:2]
                elif self.name=='azure_dragon':
                    limit=1 if name.startswith('trunk_') else 2 if 'antler' in name or 'limb' in name else 0 if 'whisker' in name else 3 if name=='head' else 1
                    b['cubes']=cubes[:limit]
                elif self.name=='mountain_xuanwu':
                    b['cubes']=(cubes[:4]+cubes[10::3]) if name=='shell' else cubes[:2] if name in ('head','snake_head') else cubes[:1]
                else:
                    b['cubes']=cubes[:1]+cubes[1::4] if name.endswith('_outer') else cubes[:2]
            lod_counts[lod]=sum(len(b['cubes']) for b in reduced['minecraft:geometry'][0]['bones'])
            reduced['minecraft:geometry'][0]['description']['identifier']+='_'+lod
            dump(A/f'geo/scenic/{self.name}_{lod}.geo.json',reduced)
        dump(A/f'animations/scenic/{self.name}.animation.json',animation)
        # Bedrock codec X/rotation conversion to editable Blockbench coordinates.
        def uid(s): return str(uuid.uuid5(uuid.NAMESPACE_URL,'dynasty/scenic-v1/'+self.name+'/'+s))
        groups={}; elements=[]
        for b in self.bones:
            rot=b.get('rotation',[0,0,0]);group={'name':b['name'],'uuid':uid(b['name']),'origin':[-b['pivot'][0],*b['pivot'][1:]],'rotation':[-rot[0],-rot[1],rot[2]],'children':[]}; groups[b['name']]=group
            for i,c in enumerate(b['cubes']):
                x,y,z=c['origin'];w,h,d=c['size']; ident=uid(b['name']+'/'+str(i)); faces={}
                for f,v in c['uv'].items():
                    u,vv=v['uv'];du,dv=v['uv_size']; faces[f]={'texture':0,'uv':[u+du,vv+dv,u,vv] if f in ('up','down') else [u,vv,u+du,vv+dv]}
                elements.append({'name':b['name']+'_'+str(i),'uuid':ident,'type':'cube','from':[-x-w,y,z],'to':[-x,y+h,z+d],'origin':group['origin'],'box_uv':False,'faces':faces})
                group['children'].append(ident)
        out=[]
        for b in self.bones:
            if b.get('parent'): groups[b['parent']]['children'].append(groups[b['name']])
            else: out.append(groups[b['name']])
        dump(D/f'blockbench/{self.name}.bbmodel',{'meta':{'format_version':'4.10','model_format':'geckolib_model','box_uv':False},'name':self.name,'model_identifier':self.name,'geckolib_modid':'dynasty','resolution':{'width':side,'height':side},'elements':elements,'outliner':out,'textures':[{'name':self.name+'.png','id':'0','uuid':uid('texture'),'width':side,'height':side,'uv_width':side,'uv_height':side,'source':'data:image/png;base64,'+base64.b64encode(texture.read_bytes()).decode()}]})
        dump(D/f'blockbench/{self.name}.animation.json',animation)
        return {'name':self.name,'bones':len(self.bones),'cubes':sum(len(b['cubes']) for b in self.bones),'lod_cubes':lod_counts,'palette':colors,'texture':[side,side],'uv_density':'0.5 logical pixels / source unit, minimum two pixels for narrow faces'}

def dragon():
    r=Rig('azure_dragon');r.bone('root',None,[0,0,0])
    # Tapered linked trunk. The head leads; waves travel down progressively thinner tail segments.
    previous='root'
    for i in range(9):
        z=64-i*20; width=18-i*1.45; name=r.bone('trunk_'+str(i),previous,[0,14,z+10])
        r.by_name[name]['rotation']=[0,round(math.sin(i*.8)*8,3),0]
        r.box(name,[-width/2,14-width*.35,z-11],[width,width*.7,22],2 if i<5 else 1)
        r.box(name,[-width*.35,13.5-width*.35,z-8],[width*.7,2,16],4)
        r.box(name,[-2,14+width*.35,z-6],[4,5 if i<5 else 3,7],3)
        values=[math.sin(j*math.pi/2-i*.7)*5 for j in range(5)]
        r.motion(name,'rotation',[[0,round(v,3),0] for v in values]); previous=name
    r.bone('neck','trunk_0',[0,14,72]);r.box('neck',[-8,9,71],[16,12,14],2)
    r.bone('head','neck',[0,16,81]);r.box('head',[-11,10,81],[22,16,22],2)
    r.box('head',[-9,10,103],[18,9,16],3);r.box('head',[-8,15.5,118],[16,4,2],0)
    r.bone('jaw','head',[0,10,90]);r.box('jaw',[-8,7,94],[16,3,24],4)
    for s in (-1,1):
        r.box('head',[s*11-(2 if s<0 else 0),20,95],[2,3,5],4)
        r.box('head',[s*10-(2 if s<0 else 0),23,94],[3,3,7],0)
        n=r.bone(('left' if s>0 else 'right')+'_antler','head',[s*7,25,88])
        r.box(n,[s*7-2,25,85],[4,12,4],4);r.box(n,[s*7-2,35,78],[4,4,10],4)
        r.box(n,[s*7-2,36,78],[4,5,3],4)
        n=r.bone(('left' if s>0 else 'right')+'_whisker','head',[s*8,12,111])
        r.box(n,[min(s*8,s*22),11,110],[14,2,2],4);r.box(n,[s*22-1,7,107],[2,6,3],4)
        r.motion(n,'rotation',[[0,0,v*s] for v in [-5,0,5,0,-5]])
        for i,z in enumerate((50,-12)):
            n=r.bone(f'{"left" if s>0 else "right"}_limb_{i}', 'trunk_'+str(0 if i==0 else 3),[s*7,12,z])
            r.box(n,[min(s*7,s*16),5,z-3],[9,8,6],2)
            r.box(n,[s*16-3,2,z-3.5],[6,5,12.5],3)
            for toe in (-1,1): r.box(n,[s*16-2+toe*2,1,z+6],[2,3,5],4)
    return r

def turtle():
    r=Rig('mountain_xuanwu');r.bone('root',None,[0,0,0]);r.bone('shell','root',[0,20,0])
    r.box('shell',[-38,10,-46],[76,18,92],1);r.box('shell',[-32,28,-38],[64,12,76],2)
    r.box('shell',[-24,40,-26],[48,8,52],3);r.box('shell',[-34,6,-40],[68,6,80],0)
    # Raised scute boundaries and original small mountain ridge are structural, not a particle cloud.
    for x in (-21,0,21):r.box('shell',[x-1.5,47.5,-30],[3,3,60],0)
    for z in (-23,0,23):r.box('shell',[-27,47.5,z-1.5],[54,3,3],0)
    for x,z,w,h in [(-15,-10,22,27),(8,9,19,18),(0,-23,15,16)]:
        r.box('shell',[x-w/2,47.5,z-w/2],[w,h*.5+.5,w],2)
        r.box('shell',[x-w*.35,48+h*.5,z-w*.35],[w*.7,h*.35,w*.7],3)
        r.box('shell',[x-w*.18,48+h*.85,z-w*.18],[w*.36,h*.15,w*.36],4)
    r.bone('neck','root',[0,19,40]);r.box('neck',[-10,12,38],[20,15,20],2)
    r.bone('head','neck',[0,21,55]);r.box('head',[-14,11,55],[28,19,25],2)
    r.box('head',[-11,12,80],[22,10,13],3);r.box('head',[-10,11.5,91],[20,6,3],0)
    for s in (-1,1):
        r.box('head',[s*14-(2 if s<0 else 0),24,75],[2,3,6],4)
        for front,z in [('fore',27),('hind',-28)]:
            n=r.bone(front+('_left' if s>0 else '_right'),'root',[s*28,15,z])
            r.box(n,[min(s*28,s*48),5,z-8],[20,12,16],2)
            r.box(n,[s*48-5,0,z-10],[10,7,23],0)
            for k in (-1,0,1):r.box(n,[s*48-3+k*3,0,z+11],[2,4,6],4)
            phase=1 if (front=='fore')==(s>0) else -1
            r.motion(n,'rotation',[[v*phase,0,s*v*.5*phase] for v in [-5,0,5,0,-5]])
    previous=r.bone('snake_base','shell',[25,34,-24])
    # Shell-bound serpent, thick root and narrowing neck; an independent second head, no humanoid torso.
    for i,(x,y,z,w) in enumerate([(29,35,-26,12),(38,44,-14,11),(41,55,1,10),(37,64,17,9)]):
        n=r.bone('snake_'+str(i),previous,[x,y,z]);r.box(n,[x-w/2,y-3,z-7],[w,13,16],1)
        r.motion(n,'rotation',[[0,v,0] for v in [-3,2,3,-2,-3]]);previous=n
    r.bone('snake_head',previous,[37,75,26]);r.box('snake_head',[30,70,24],[14,12,20],2)
    r.box('snake_head',[31,69,42],[12,5,8],3);r.box('snake_head',[31.5,68.5,49.5],[11,3,1],0)
    for x in (30,43):r.box('snake_head',[x,78,38],[1,2,4],4)
    r.bone('tail','root',[0,14,-44]);r.box('tail',[-7,9,-65],[14,10,23],2);r.box('tail',[-4,10,-79],[8,6,15],1)
    r.motion('head','rotation',[[0,v,0] for v in [-3,0,3,0,-3]])
    return r

def crow():
    r=Rig('sun_crow');r.bone('root',None,[0,0,0]);r.bone('breast','root',[0,25,0])
    r.box('breast',[-10,16,-18],[20,20,32],0);r.box('breast',[-8,20,14],[16,15,10],0)
    r.box('breast',[-7,29,23.5],[14,3,1],3)
    r.bone('neck','breast',[0,34,15]);r.box('neck',[-6,30,12],[12,13,17],0)
    r.bone('head','neck',[0,40,23]);r.box('head',[-8,38,21],[16,12,22],0)
    r.box('head',[-5,39,42],[10,6,9],3);r.box('head',[-3,38,50],[6,4,5],2)
    for s in (-1,1):
        r.box('head',[s*8-(1 if s<0 else 0),45,34],[1,2,4],4)
        wing=r.bone(('left' if s>0 else 'right')+'_wing','breast',[s*8,31,0])
        r.box(wing,[min(s*8,s*31),27,-9],[23,8,21],1)
        outer=r.bone(('left' if s>0 else 'right')+'_outer',wing,[s*29,30,-2])
        r.box(outer,[min(s*29,s*54),27,-10],[25,5,20],1)
        # Separated overlapping cuboid primary feathers; stepped span and trailing edge.
        for i in range(5):
            x=s*(40+i*5);z=-8-i*7
            r.box(outer,[x-3,26,z-12],[6,3,26-i*2],1 if i%2 else 0)
            r.box(outer,[x-2,25.5,z-13],[4,2,3],4)
        r.motion(wing,'rotation',[[0,0,s*v] for v in [-8,4,8,4,-8]])
        r.motion(outer,'rotation',[[0,0,s*v] for v in [-3,0,3,0,-3]])
    r.bone('tail','breast',[0,24,-17])
    for i in (-1,0,1):r.box('tail',[i*7-4,19,-52+abs(i)*5],[8,4,34-abs(i)*4],1 if i==0 else 0)
    r.motion('tail','rotation',[[v,0,0] for v in [-2,0,2,0,-2]])
    # Three distinct leg chains, all attached to the ventral breast. Third foot readable in side/underside view.
    for i,(x,z) in enumerate([(-6,2),(6,2),(0,-11)]):
        n=r.bone('leg_'+str(i),'breast',[x,18,z]);r.box(n,[x-2,6,z-2],[4,12,4],0)
        r.box(n,[x-3,3,z-2],[6,4,10],1)
        for toe in (-1,1):r.box(n,[x+toe*3-1,2,z+6],[2,3,7],0)
        r.motion(n,'rotation',[[v,0,0] for v in [-3,0,3,0,-3]])
    return r

def main():
    records=[r.export() for r in (dragon(),turtle(),crow())]
    dump(D/'authoring.json',{'source':'tools/art/cod3/scenic_resources.py','scenes':{'scenic_01':'azure_dragon','scenic_10':'mountain_xuanwu','scenic_25':'sun_crow'},'records':records,'world_scale':4,'server_entities':0,'collision':'none: visual-only','animation_clock':'elapsed authoritative packet ticks, 80-tick loops'})
    print('Generated three independent scenic rigs, pixel textures, loops and editable Blockbench sources.')
if __name__=='__main__':main()
