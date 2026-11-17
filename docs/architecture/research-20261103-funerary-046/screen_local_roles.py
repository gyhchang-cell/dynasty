"""Functional candidate prefilter of unread local village houses; never credit."""
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile
from collections import defaultdict
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
ROOT=BASE.parents[1]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
def sha(b):return hashlib.sha256(b).hexdigest()
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def strings(o):
    if isinstance(o,str):yield o
    elif isinstance(o,dict):
        for v in o.values():yield from strings(v)
    elif isinstance(o,list):
        for v in o:yield from strings(v)
def collect(o,seen):
    if isinstance(o,dict):
        for k in ('member','complete_building_identity'):
            if isinstance(o.get(k),str):seen.add(o[k])
        for v in o.values():collect(v,seen)
    elif isinstance(o,list):
        for v in o:collect(v,seen)
def main():
    indices=[];seen=set()
    for p in sorted(BASE.rglob('*.json')):
        if p.parent==OUT:continue
        if p.name in ('sources.json','candidates.json','scope-expansion-sources.json','manual-review.json','full-buildings.json','recipe-source.json'):
            collect(json.loads(p.read_text()),seen);indices.append(evidence(p))
    meta_path=BASE/'research-20261101-dungeons-026/all-structure-metadata.json'
    inv_path=BASE/'research-20261101-dungeons-024/fixed-source-screen.json'
    inventory={e['path']:e['sha256'] for e in json.loads(inv_path.read_text())['archives']}
    rows=[];groups=defaultdict(list)
    for e in json.loads(meta_path.read_text())['entries']:
        if e['member'] in seen or '/houses/' not in e['member'] or len(e.get('size',[]))!=3:continue
        x,y,z=e['size']
        if min(x,z)>=5 and max(x,z)<=32 and 5<=y<=32 and x*y*z<=30000:groups[e['source_archive']].append(e)
    archive_evidence=[]
    for archive,entries in groups.items():
        actual=sha(Path(archive).read_bytes());assert actual==inventory[archive]
        archive_evidence.append(dict(path=archive,sha256=actual))
        with ZipFile(archive) as z:
            for e in entries:
                raw=z.read(e['member']);assert sha(raw)==e['nbt_sha256'];n=read(raw)
                palettes=n.get('palettes') or [n['palette']]
                brewing=[];roles=[]
                for b in n['blocks']:
                    if any(p[b['state']]['Name']=='minecraft:brewing_stand' for p in palettes):brewing.append(b['pos'])
                    if b.get('nbt'):
                        values=set(strings(b['nbt']))
                        if any('cleric' in s.lower() or 'priest' in s.lower() for s in values):roles.append(dict(position=b['pos'],data=b['nbt']))
                entity_roles=[v for v in n.get('entities',[]) if any('cleric' in s.lower() or 'priest' in s.lower() for s in strings(v))]
                rows.append(dict(source_archive=archive,source_archive_sha256=actual,member=e['member'],nbt_sha256=e['nbt_sha256'],size=n['size'],
                    brewing_stand_positions=brewing,cleric_or_priest_block_context=roles,cleric_or_priest_entity_context=entity_roles,
                    candidate_signal=bool(brewing or roles or entity_roles),actual_whole_visual_study=False,semantic_use_confirmed=False,building_credit=0))
    result=dict(date='2026-11-03',fixed_metadata=evidence(meta_path),fixed_archive_inventory=evidence(inv_path),
        prior_indices=indices,archives=archive_evidence,screened_templates=len(rows),
        signal_candidates=sum(e['candidate_signal'] for e in rows),entries=rows,
        counting_limit='机器位置/角色预筛只用于发现线索，不是实际整栋建筑研究、礼仪用途、完整性或语义去重信用。',
        building_credit_added=0,java_run=False,game_run=False,network_requests=0)
    (OUT/'functional-prefilter.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('screened',len(rows),'functional signals',result['signal_candidates'],'credit0')
    for e in rows:
        if e['candidate_signal']:print(e['member'],e['size'],'brew',len(e['brewing_stand_positions']),'role',len(e['cleric_or_priest_block_context'])+len(e['cleric_or_priest_entity_context']))
if __name__=='__main__':main()
