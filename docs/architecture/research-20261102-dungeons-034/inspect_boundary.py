"""Read author JSON and class constant strings with Python; never load Java code."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import sys
from zipfile import ZipFile

OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parents[2]/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR

def sha(b):
    return hashlib.sha256(b).hexdigest()

def constants(raw):
    assert raw[:4]==b'\xca\xfe\xba\xbe'
    count=struct.unpack_from('>H',raw,8)[0]
    pos,index=10,1
    values=[]
    sizes={3:4,4:4,5:8,6:8,7:2,8:2,9:4,10:4,11:4,12:4,15:3,16:2,17:4,18:4,19:2,20:2}
    while index<count:
        tag=raw[pos];pos+=1
        if tag==1:
            length=struct.unpack_from('>H',raw,pos)[0];pos+=2
            value=raw[pos:pos+length].decode('utf-8',errors='replace');pos+=length
            if 'guling' in value.lower():
                values.append(dict(index=index,kind='CONSTANT_Utf8',value=value))
        else:
            pos+=sizes[tag]
            if tag in (5,6):index+=1
        index+=1
    return values

def main():
    src=json.loads((OUT/'sources.json').read_text())
    archive=src['source_archives'][0]
    resources=[];classes=[];entries=[]
    with ZipFile(archive['path']) as z:
        for member in ['data/eeeabsmobs/worldgen/structure/guling.json',
            'data/eeeabsmobs/worldgen/structure_set/guling.json',
            'data/eeeabsmobs/tags/worldgen/biome/has_structure/guling.json',
            'data/eeeabsmobs/tags/worldgen/structure/eye_of_guling.json']:
            raw=z.read(member)
            resources.append(dict(member=member,sha256=sha(raw),data=json.loads(raw)))
        for member in ['com/eeeab/eeeabsmobs/sever/world/structure/StructureGuling.class',
            'com/eeeab/eeeabsmobs/sever/world/structure/StructureGuling$Piece.class']:
            raw=z.read(member)
            classes.append(dict(member=member,sha256=sha(raw),relevant_utf8_constants=constants(raw),
                executed=False,placement_offsets_not_inferred=True))
        manifest=z.read('META-INF/mods.toml')
        for c in src['candidates']:
            d=read(z.read(c['member']));pal=d.get('palette') or d['palettes'][0]
            cs={tuple(b['pos']):pal[b['state']] for b in d['blocks'] if pal[b['state']]['Name'] not in AIR}
            edges=[]
            for axis in (0,2):
                for coordinate in (0,d['size'][axis]-1):
                    on={p:v for p,v in cs.items() if p[axis]==coordinate}
                    edges.append(dict(axis=axis,coordinate=coordinate,nonair=len(on),
                        occupied_y_counts={str(y):sum(p[1]==y for p in on) for y in (0,4,10,20,25,30,35,39)}))
            entities=d.get('entities',[])
            entries.append(dict(id=c['id'],nbt_sha256=c['nbt_sha256'],boundary_profiles=edges,
                entity_id_counts=dict(Counter(e.get('nbt',{}).get('id','') for e in entities)),
                native_composition_verified=False,complete_building_credit=0))
    report=dict(archive=archive,author_resources=resources,static_class_string_evidence=classes,
        manifest_sha256=sha(manifest),manifest_text=manifest.decode(),entries=entries,
        limits='Constant-pool strings prove only the strings present in these class files. No method execution, offsets, assembly, native terrain, routes or complete-building identity inferred.',
        java_run=False,classes_loaded=False,game_run=False,network_requests=0,building_credit_added=0)
    (OUT/'boundary-evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    for c in classes:print(c['member'],c['relevant_utf8_constants'])
    for e in entries:print(e['id'],e['entity_id_counts'])

if __name__=='__main__':
    main()
