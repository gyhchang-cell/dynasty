"""Bind authored whole-body selection and compare all three mausoleum states."""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
sys.path.insert(0,str(OUT.parents[2]/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR,plans
from PIL import Image,ImageDraw
def sha(b):return hashlib.sha256(b).hexdigest()
def get(p):return json.loads(p.read_text())
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def main():
    src=get(OUT/'sources.json');resources=[];states={};bodies=[]
    names=['the_mausoleum','the_mausoleum1','the_mausoleum2']
    core={'goety:crypt_bricks','goety:crypt_plinth','goety:crypt_pillar','goety:crypt_tiles','goety:crypt_tiles_stairs','goety:crypt_tiles_slab','goety:shade_bricks_wall'}
    with ZipFile(src['source_archives'][0]['path']) as z:
        for name in names:
            n='data/goetyawaken/structures/'+name+'.nbt';raw=z.read(n);d=read(raw);pal=d.get('palette') or d['palettes'][0]
            ss={tuple(b['pos']):pal[b['state']] for b in d['blocks']};states[name]=ss
            cs={p:s for p,s in ss.items() if s['Name'] not in AIR}
            bodies.append(dict(member=n,nbt_sha256=sha(raw),size=d['size'],occupied_bounds=[[min(p[i] for p in cs),max(p[i] for p in cs)] for i in range(3)],
                jigsaw_count=sum(s['Name']=='minecraft:jigsaw' for s in ss.values()),
                lower_door_count=sum(s['Name'].endswith('_door') and s.get('Properties',{}).get('half')=='lower' for s in ss.values()),
                black_wool_cells=sum(s['Name']=='minecraft:black_wool' for s in cs.values()),
                block_entity_counts=dict(Counter(b['nbt'].get('id') for b in d['blocks'] if b.get('nbt'))),
                top_centre_states=[dict(pos=[18,y,18],state=ss.get((18,y,18))) for y in range(40,48)]))
        for n in ['data/goetyawaken/worldgen/structure/the_mausoleum.json',
                  'data/goetyawaken/worldgen/template_pool/the_mausoleum/start_pool.json',
                  'data/goetyawaken/worldgen/template_pool/the_mausoleum.json',
                  'data/goetyawaken/worldgen/processor_list/the_mausoleum_loot.json',
                  'assets/goety/patchouli_books/black_book/zh_cn/entries/world/strctures/the_mausoleum.json',
                  'assets/goety/patchouli_books/black_book/en_us/entries/world/strctures/the_mausoleum.json']:
            raw=z.read(n);resources.append(dict(member=n,sha256=sha(raw),data=json.loads(raw)))
        manifest=z.read('META-INF/mods.toml')
    pairs=[]
    for left,right in itertools.combinations(names,2):
        a,b=states[left],states[right]
        changes=[dict(position=list(p),left=a.get(p),right=b.get(p)) for p in sorted(a.keys()|b.keys()) if a.get(p)!=b.get(p)]
        ca={p:s for p,s in a.items() if s['Name'] in core};cb={p:s for p,s in b.items() if s['Name'] in core}
        counts=Counter((e['left']['Name'] if e['left'] else 'OMITTED',e['right']['Name'] if e['right'] else 'OMITTED') for e in changes)
        pairs.append(dict(left=left,right=right,changed_raw_states=len(changes),changes=changes,
            changed_state_pairs=[dict(left=a,right=b,count=n) for (a,b),n in sorted(counts.items())],
            original_core_names=sorted(core),original_core_cells=len(ca),original_core_states_identical=ca==cb))
    oldfolder=BASE/'continuation-20261022/references/whole-candidates'
    old=next(e for e in get(oldfolder/'candidates.json')['candidates'] if e['id']=='W028')
    assert old['nbt_sha256']==bodies[0]['nbt_sha256']
    dump('author-and-family-evidence.json',dict(author_resources=resources,bodies=bodies,pairs=pairs,
        manifest_sha256=sha(manifest),manifest_text=manifest.decode(),
        provenance_url_role='Archive manifest issueTrackerURL; no publisher homepage invented.',
        old_candidate_id='W028',old_candidate_index=evidence(oldfolder/'candidates.json'),old_review=evidence(oldfolder/'review-batch-001.json'),
        old_hold_reason=get(oldfolder/'review-batch-001.json')['not_credited']['W028'],
        old_family_not_newly_discovered=True,complete_building_family_count_at_most=1,
        direct_author_start_alternatives=['goetyawaken:the_mausoleum1','goetyawaken:the_mausoleum2'],
        no_external_building_jigsaw=True,native_entry_digging_route_verified=False,
        wool_not_hidden_or_replaced=True,custom_waterlogging_processor_executed=False,
        limits='Direct start selection and zero connectors establish complete authored template-body boundary, not world terrain/entry or continuous navigation. Exact shell equality does not equate block entities or gameplay.'))
    ss=states['the_mausoleum1'];cells={p:s['Name'] for p,s in ss.items() if s['Name'] not in AIR}
    im=Image.new('RGB',(1520,1640),'#edf0f2')
    im.paste(plans(cells,[37,48,37],32,'042-F01'),(0,0));im.paste(plans(cells,[37,48,37],35,'042-F01'),(0,800))
    ImageDraw.Draw(im).text((24,1610),'Original upper planes only. Sealed external entry and continuous digging/navigation NOT certified.',fill='#17252c')
    im.save(OUT/'F01-upper-levels.png')
    print([(p['left'],p['right'],p['changed_raw_states'],p['original_core_cells'],p['original_core_states_identical']) for p in pairs])
if __name__=='__main__':main()
