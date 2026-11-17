"""Preserve source markers; masked image is explanatory, not processor execution."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
from zipfile import ZipFile

OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parents[2]/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR,iso,plans
from PIL import Image,ImageDraw

def sha(b):return hashlib.sha256(b).hexdigest()
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def constants(raw):
    assert raw[:4]==b'\xca\xfe\xba\xbe'
    count=struct.unpack_from('>H',raw,8)[0];pos,index=10,1;values=[]
    sizes={3:4,4:4,5:8,6:8,7:2,8:2,9:4,10:4,11:4,12:4,15:3,16:2,17:4,18:4,19:2,20:2}
    while index<count:
        tag=raw[pos];pos+=1
        if tag==1:
            length=struct.unpack_from('>H',raw,pos)[0];pos+=2
            value=raw[pos:pos+length].decode('utf-8',errors='replace');pos+=length
            if any(w in value.lower() for w in ['platinum_dungeon','tower','ground','geltemplate','stonefill','loot_chest','platinum_chest','boss']):
                values.append(dict(index=index,kind='CONSTANT_Utf8',value=value))
        else:
            pos+=sizes[tag]
            if tag in (5,6):index+=1
        index+=1
    return values

def main():
    src=json.loads((OUT/'sources.json').read_text());archive=src['source_archives'][0]
    resources=[];classes=[];entries=[]
    masked={'structure_gel:blue_gel','structure_gel:yellow_gel','minecraft:structure_block'}
    with ZipFile(archive['path']) as z:
        for n in ['data/lost_aether_content/worldgen/structure/platinum_dungeon.json',
                  'data/lost_aether_content/worldgen/structure_set/platinum_dungeon.json',
                  'data/lost_aether_content/tags/worldgen/biome/has_platinum_dungeon.json']:
            raw=z.read(n);resources.append(dict(member=n,sha256=sha(raw),data=json.loads(raw)))
        for n in [n for n in z.namelist() if n.startswith('com/legacy/lost_aether/world/structure/PlatinumDungeon') and n.endswith('.class')]:
            raw=z.read(n);classes.append(dict(member=n,sha256=sha(raw),relevant_utf8_constants=constants(raw),executed=False,placement_offsets_not_inferred=True))
        manifest=z.read('META-INF/mods.toml')
        for c in src['candidates']:
            d=read(z.read(c['member']));pal=d.get('palette') or d['palettes'][0]
            markers=[dict(position=b['pos'],state=pal[b['state']],data=b['nbt']) for b in d['blocks'] if b.get('nbt') and pal[b['state']]['Name'] in ['minecraft:structure_block','structure_gel:data_handler']]
            entries.append(dict(id=c['id'],nbt_sha256=c['nbt_sha256'],markers=markers,
                structure_data_metadata=dict(Counter(e['data'].get('metadata') for e in markers if e['state']['Name']=='minecraft:structure_block')),
                handler_types=dict(Counter(h['type'] for e in markers for h in e['data'].get('handlers',[]))),
                original_gel_cells=sum(c['materials'].get(n,0) for n in masked if n.startswith('structure_gel:')),
                gel_processing_verified=False,complete_building_identity_confirmed=False))
            if c['id']=='F01':
                cells={tuple(b['pos']):pal[b['state']]['Name'] for b in d['blocks'] if pal[b['state']]['Name'] not in AIR|masked}
                im=Image.new('RGB',(1520,1520),'#edf0f2')
                im.paste(iso(cells,d['size'],False,'040-F01: OMIT gel + structure markers; NOT native output'),(0,0))
                im.paste(iso(cells,d['size'],True,'040-F01: same source, diagnostic mask only',cutoff=18),(760,0))
                im.paste(plans(cells,d['size'],9,'040-F01 MASKED'),(0,680))
                ImageDraw.Draw(im).text((24,1490),'No processor/terrain/route proof. Source templates unchanged. One masked image is NOT another building.',fill='#17252c')
                im.save(OUT/'F01-gel-mask.png')
    dump('boundary-evidence.json',dict(archive=archive,author_resources=resources,
        static_class_string_evidence=classes,manifest_sha256=sha(manifest),manifest_text=manifest.decode(),entries=entries,
        diagnostic_mask=dict(names=sorted(masked),purpose='Expose otherwise obscured source geometry only; does not assert runtime replacement or passability.',image='F01-gel-mask.png'),
        limits='Class constants establish identifiers only; no placement offsets, method semantics, assembly, gel replacement, feature generation or native routes inferred.',
        java_run=False,classes_loaded=False,game_run=False,network_requests=0,building_credit_added=0))
    print('Saved raw markers, author configuration and static class strings; explanatory mask only.')

if __name__=='__main__':main()
