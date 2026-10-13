#!/usr/bin/env python3
"""Read the delivered compressed NBT and actual local vanilla textures for cutaway QA."""
import gzip,io,json,struct,sys,zipfile
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'docs/art/cod3-caves-v1'
sys.path.insert(0,str(ROOT/'tools/art/boss-forms'))
import texture_review as review

class Reader:
    def __init__(self,data):self.data=io.BytesIO(data)
    def read(self,fmt):return struct.unpack(fmt,self.data.read(struct.calcsize(fmt)))[0]
    def string(self):return self.data.read(self.read('>H')).decode()
    def value(self,t):
        if t==3:return self.read('>i')
        if t==8:return self.string()
        if t==9:
            subtype=self.read('>B');return [self.value(subtype) for _ in range(self.read('>i'))]
        if t==10:
            d={}
            while (kind:=self.read('>B')):key=self.string();d[key]=self.value(kind)
            return d
        raise ValueError('Unexpected NBT type '+str(t))

client=Path.home()/'.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client.jar'
assert client.exists(),'Use existing local 1.20.1 vanilla client assets; no downloads'
records={}
with zipfile.ZipFile(client) as source:
    for id in ('scenic_crystal_canopy','scenic_ice_bloom'):
        raw=gzip.decompress((ROOT/f'src/main/resources/data/dynasty/structures/{id}.nbt').read_bytes());reader=Reader(raw)
        assert reader.read('>B')==10 and reader.string()==''
        nbt=reader.value(10);assert reader.data.read()==b''
        assert nbt['size']==[31,19,31] and nbt['entities']==[]
        palette=[p['Name'] for p in nbt['palette']];blocks={tuple(b['pos']):palette[b['state']] for b in nbt['blocks']}
        assert len(blocks)==len(nbt['blocks']) and all('nbt' not in b for b in nbt['blocks'])
        for i in range(31):
            for x,z in [(cross,i) for cross in range(13,18)]+[(i,cross) for cross in range(13,18)]:
                assert blocks[x,0,z]!='minecraft:air'
                assert all(blocks[x,y,z]=='minecraft:air' for y in range(1,5))
        shell='minecraft:deepslate' if 'crystal' in id else 'minecraft:packed_ice'
        # Omit the front shell and upper ceiling solely for inspecting actual interior blocks.
        visible={p:b for p,b in blocks.items() if b!='minecraft:air' and not (b==shell and (p[1]>=11 or p[2]<=3 and p[1]>0))}
        textures={}
        def tex(block,face):
            key=block.split(':')[1]+('_top' if block=='minecraft:deepslate' and face in ('up','down') else '')
            if key not in textures:
                with Image.open(io.BytesIO(source.read('assets/minecraft/textures/block/'+key+'.png'))) as im:textures[key]=np.array(im.convert('RGB'))
            return textures[key]
        quads=[]
        neighbours={'north':(0,0,-1),'south':(0,0,1),'east':(-1,0,0),'west':(1,0,0),'up':(0,1,0),'down':(0,-1,0)}
        for p,b in visible.items():
            for face,corners in review.r.FACES.items():
                if tuple(a+d for a,d in zip(p,neighbours[face])) in visible:continue
                texture=tex(b,face)
                quads.append(((np.array(corners)+p)*16,{'uv':[0,0],'uv_size':[16,16],'_tex':texture},'block'))
        out=D/id;out.mkdir(parents=True,exist_ok=True)
        points=np.concatenate([q[0] for q in quads]);fallback=np.zeros((16,16,3),dtype=np.uint8)
        for yaw,label in [(0,'front'),(45,'45'),(90,'right'),(-90,'left'),(180,'back')]:
            review.labelled(review.raster(quads,fallback,yaw=yaw,elevation=14,size=(1000,720),mode='lit',frame_points=points),id+' / '+label+' / NBT cutaway','软件剖视 · 仅读取实际 NBT + 本机原版 PNG · 移去前壁/顶壳便于检查 · 非实机').save(out/(label+'.png'))
        records[id]={'nbt_blocks':len(blocks),'palette':palette,'entities':0,'block_entities':0,'clear_crossing':True,'visible_cutaway_faces':len(quads),'texture_source':'local Minecraft 1.20.1 client.jar; no PNG copied into project','software_cutaway_only':True}
(D/'software-validation.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print('PASS actual delivered NBT: two clear crossings, no entity/NBT payload, real vanilla-texture five-view cutaways')
