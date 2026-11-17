"""Study two previously unread fixed-source small ritual/temple candidates."""
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile
import hashlib
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT;return m
def main():
    m=load('renderer017',BASE/'research-20261101-dungeons-017/inspect_batch.py')
    m.SELECTION=[('trek','*远足*jar','https://modrinth.com/datapack/trek',['overworld/medium/ritual']),
        ('radiation_zone_reborn','*radiation_zone_reborn*jar','https://mcreator.net',['totem_temple'])]
    m.main()
    src=json.loads((OUT/'sources.json').read_text());context=[]
    for c in src['candidates']:
        ident=c['member'].split('/structures/',1)[0].split('/')[-1]+':'+c['member'].split('/structures/',1)[1][:-4]
        # A name/processor mention alone is not a direct placement selector.
        c['pool_references']=[r for r in c['pool_references'] if any(e['element'].get('location')==ident for e in r['data'].get('elements',[]))]
        c['publisher_url_role']='author-project displayURL from manifest' if c['id']=='F01' else 'generic tool homepage from manifest, NOT a verified project homepage'
        with ZipFile(c['source_archive']) as z:
            # Renderer imported its own read helper; no NBT/game file is extracted.
            renderer=load('reader001',BASE/'research-20261101-dungeons-001/inspect_batch.py')
            d=renderer.read(z.read(c['member']));p=d['palette']
            resources=[]
            for member in z.namelist():
                if not member.endswith('.json'):continue
                if '/worldgen/' in member and (('ritual' in member and c['id']=='F01') or ('totem_temple' in member and c['id']=='F02')):
                    raw=z.read(member);resources.append(dict(member=member,sha256=sha(raw),data=json.loads(raw)))
                if c['id']=='F02' and member in ['assets/radiation_zone_reborn/lang/zh_cn.json','assets/radiation_zone_reborn/lang/en_us.json']:
                    raw=z.read(member);lang=json.loads(raw);resources.append(dict(member=member,sha256=sha(raw),selected_entries={k:v for k,v in lang.items() if 'decayed_totem' in k}))
            raw=z.read('META-INF/mods.toml')
            context.append(dict(id=c['id'],manifest_sha256=sha(raw),manifest_text=raw.decode(),
                resources=resources,block_entities=[b for b in d['blocks'] if b.get('nbt')],entities=d.get('entities',[]),
                jigsaw_count=sum(p[b['state']]['Name']=='minecraft:jigsaw' for b in d['blocks'])))
    (OUT/'sources.json').write_text(json.dumps(src,ensure_ascii=False,indent=2)+'\n')
    (OUT/'author-context.json').write_text(json.dumps(dict(entries=context,network_requests=0),ensure_ascii=False,indent=2)+'\n')
    load('audit017',BASE/'research-20261101-dungeons-017/audit_sources.py').main()
    load('dedup002',BASE/'research-20261101-dungeons-002/check_dedup.py').main()
    d=json.loads((OUT/'dedup-evidence.json').read_text())
    d['formal_identity_records_checked']=len(json.loads((BASE/'continuation-20261022/references/full-buildings.json').read_text())['entries'])
    d['formal_count_annotation_corrected_from_legacy_helper']=True
    (OUT/'dedup-evidence.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
