#!/usr/bin/env python3
"""Permanent vanilla-block cave scenery; standard one-piece jigsaw assets, no entity or tick logic."""
import gzip,hashlib,json,struct
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/'src/main/resources/data/dynasty'
DOC=ROOT/'docs/art/cod3-caves-v1'
SIZE=(31,19,31)

def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def utf(s):
    b=s.encode();return struct.pack('>H',len(b))+b
def kind(value):return 10 if isinstance(value,dict) else 9 if isinstance(value,list) else 8 if isinstance(value,str) else 3
def payload(value):
    t=kind(value)
    if t==3:return struct.pack('>i',value)
    if t==8:return utf(value)
    if t==10:return b''.join(bytes([kind(v)])+utf(k)+payload(v) for k,v in value.items())+b'\0'
    subtype=kind(value[0]) if value else 10
    assert all(kind(v)==subtype for v in value)
    return bytes([subtype])+struct.pack('>i',len(value))+b''.join(payload(v) for v in value)

class Cave:
    def __init__(self,id,shell):self.id=id;self.blocks={};self.shell=shell
    def put(self,x,y,z,block):
        assert 0<=x<31 and 0<=y<19 and 0<=z<31
        self.blocks[x,y,z]='minecraft:'+block
    def box(self,x,y,z,w,h,d,block):
        for xx in range(x,x+w):
            for yy in range(y,y+h):
                for zz in range(z,z+d):self.put(xx,yy,zz,block)
    def chamber(self):
        # An actual stepped hollow room, with four 5x4 portals and a clear central crossing.
        radii=[12]*5+[11]*3+[10]*3+[9,9,7,7,6,6,0,0]
        def inside(x,z,r,margin=0):
            a,b=abs(x-15),abs(z-15)
            return max(a,b)<=r+margin and a+b<=int(r*1.65)+margin*2
        for y in range(18):
            radius=radii[y];previous=radii[max(0,y-1)]
            for x in range(31):
                for z in range(31):
                    if y==0 and inside(x,z,12,1):self.put(x,y,z,self.shell)
                    elif 1<=y<=16 and inside(x,z,radius):self.put(x,y,z,'air')
                    elif inside(x,z,max(radius,previous),1):self.put(x,y,z,self.shell)
        for side in (0,26):
            self.box(13,0,side,5,1,5,self.shell);self.box(13,1,side,5,4,5,'air')
            self.box(side,0,13,5,1,5,self.shell);self.box(side,1,13,5,4,5,'air')
    def export(self,biomes,salt):
        # Only declared blocks are written; corners outside the cave retain natural terrain.
        palette=sorted(set(self.blocks.values()));lookup={v:i for i,v in enumerate(palette)}
        nbt={'DataVersion':3465,'size':list(SIZE),'palette':[{'Name':b} for b in palette],
             'blocks':[{'state':lookup[b],'pos':list(pos)} for pos,b in sorted(self.blocks.items())],'entities':[]}
        path=DATA/f'structures/{self.id}.nbt';path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(gzip.compress(b'\x0a\0\0'+payload(nbt),mtime=0))
        dump(DATA/f'tags/worldgen/biome/has_structure/{self.id}.json',{'replace':False,'values':biomes})
        dump(DATA/f'worldgen/template_pool/{self.id}.json',{'name':'dynasty:'+self.id,'fallback':'minecraft:empty','elements':[{'weight':1,'element':{'element_type':'minecraft:single_pool_element','location':'dynasty:'+self.id,'processors':'minecraft:empty','projection':'rigid'}}]})
        # 1.20.1 adds the root piece only when max depth >0. With no jigsaw blocks this stays one piece.
        dump(DATA/f'worldgen/structure/{self.id}.json',{'type':'minecraft:jigsaw','biomes':'#dynasty:has_structure/'+self.id,'step':'underground_structures','spawn_overrides':{},'terrain_adaptation':'none','start_pool':'dynasty:'+self.id,'size':1,'start_height':{'type':'minecraft:uniform','min_inclusive':{'absolute':-40},'max_inclusive':{'absolute':-24}},'use_expansion_hack':False,'max_distance_from_center':32})
        dump(DATA/f'worldgen/structure_set/{self.id}.json',{'structures':[{'structure':'dynasty:'+self.id,'weight':1}],'placement':{'type':'minecraft:random_spread','salt':salt,'spacing':80 if 'crystal' in self.id else 96,'separation':28 if 'crystal' in self.id else 32}})
        return {'id':self.id,'size':SIZE,'blocks':len(self.blocks),'block_palette':dict(Counter(self.blocks.values())),'entities':0,'block_entities':0,'clear_crossing':{'center':[15,1,15],'north':[15,1,0],'south':[15,1,30],'west':[0,1,15],'east':[30,1,15]},'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def crystal():
    c=Cave('scenic_crystal_canopy','deepslate');c.chamber()
    # Five geometric star knots and a sparse constellation trace on the inner roof.
    stars=[(10,12),(14,10),(20,13),(19,19),(11,20)]
    for (x,z),(nx,nz) in zip(stars,stars[1:]):
        steps=max(abs(nx-x),abs(nz-z))
        for step in range(steps+1):
            c.put(round(x+(nx-x)*step/steps),17,round(z+(nz-z)*step/steps),'calcite')
    for i,(x,z) in enumerate(stars):
        c.box(x-1,16,z-1,3,1,3,'amethyst_block');c.put(x,15,z,'sea_lantern')
        if i%2==0:c.put(x,14,z,'amethyst_block')
    for x,z,h in [(6,7,5),(24,8,4),(7,24,3),(24,23,6)]:
        c.box(x-1,1,z-1,3,1,3,'calcite');c.box(x-1,2,z-1,3,h-2,3,'amethyst_block')
        c.put(x,h,z,'sea_lantern');c.put(x,h+1,z,'amethyst_block');c.put(x,h+2,z,'calcite')
    return c

def ice():
    c=Cave('scenic_ice_bloom','packed_ice');c.chamber()
    # Two different scales of stepped ice flowers. Broad petals attach to one central crystal.
    for x,z,h in [(7,7,5),(23,8,7),(7,24,4),(23,23,6)]:
        c.box(x-1,1,z-1,3,2,3,'blue_ice');c.box(x,3,z,1,h-2,1,'packed_ice')
        for dx,dz in [(-2,0),(2,0),(0,-2),(0,2)]:
            c.box(x+dx-1,h-1,z+dz-1,2,2,2,'blue_ice')
        c.put(x,h,z,'sea_lantern');c.put(x,h+1,z,'calcite')
    for x,z in [(5,15),(25,15),(15,5),(15,25)]:
        for dx,dz in [(-2,0),(2,0),(0,-2),(0,2)]:
            c.box(x+dx,8,z+dz,1,3,1,'blue_ice')
        c.box(x,7,z,1,5,1,'calcite');c.put(x,9,z,'sea_lantern')
    # Non-slippery central mineral path lets visitors cross the display safely.
    c.box(13,0,0,5,1,31,'calcite');c.box(0,0,13,31,1,5,'calcite')
    return c

def main():
    first=crystal();second=ice()
    records=[first.export(['#minecraft:is_overworld'],460090901),second.export(['minecraft:snowy_plains','minecraft:ice_spikes','minecraft:frozen_peaks','minecraft:jagged_peaks','minecraft:snowy_slopes','minecraft:grove','minecraft:snowy_taiga'],460092401)]
    for c in (first,second):
        # Stable editable source / test manifest; no preview replaces actual NBT data.
        dump(DOC/f'{c.id}.blocks.json',{'size':SIZE,'blocks':[{'pos':pos,'block':b} for pos,b in sorted(c.blocks.items())]})
        for x,z in [(x,z) for x in range(13,18) for z in range(31)]+[(x,z) for x in range(31) for z in range(13,18)]:
            assert c.blocks[x,0,z]!='minecraft:air'
            assert all(c.blocks[x,y,z]=='minecraft:air' for y in range(1,5))
    dump(DOC/'manifest.json',{'source':'tools/art/cod3/scenic_caves.py','scenes':{'scenic_09':first.id,'scenic_24':second.id},'records':records,'permanence':'ordinary placed blocks in generated chunks; no timer','generation':'standard data-driven JigsawStructure, one piece, only newly generated chunks','audio':'no added sound','lighting':'vanilla sea lantern blocks, no server particle or mob creation'})
    print('Generated two permanent one-piece cave landmarks; four clear portals, no entity or block-entity data.')
if __name__=='__main__':main()
