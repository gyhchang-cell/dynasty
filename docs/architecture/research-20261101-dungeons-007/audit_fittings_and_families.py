#!/usr/bin/env python3
"""Read fittings/feature definitions and document manually observed family exclusion."""
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
KINDS={'minecraft:bookshelf','minecraft:chiseled_bookshelf','minecraft:lectern','minecraft:cartography_table'}

def sha_bytes(raw):return hashlib.sha256(raw).hexdigest()
def evidence(p):return dict(path=str(p),sha256=sha_bytes(p.read_bytes()))
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

def main():
 s=json.loads((OUT/'sources.json').read_text());rows=[]
 for c in s['candidates']:
  with ZipFile(c['source_archive']) as z:
   d=read(z.read(c['member']));pal=d.get('palette') or d['palettes'][0]
   fittings=[dict(position=b['pos'],state=pal[b['state']]) for b in d['blocks'] if pal[b['state']]['Name'] in KINDS]
   dependencies=[]
   for pool in sorted({v['data']['pool'] for v in c['sockets']}):
    ns,name=pool.split(':',1);member=f'data/{ns}/worldgen/template_pool/{name}.json'
    data=json.loads(z.read(member)) if member in z.namelist() else None
    features=[]
    def collect(v):
     if isinstance(v,dict):
      if v.get('element_type')=='minecraft:feature_pool_element':
       feature=v.get('feature');ident=feature.get('feature') if isinstance(feature,dict) else feature
       if isinstance(ident,str):
        nsp,fp=ident.split(':',1);target=f'data/{nsp}/worldgen/configured_feature/{fp}.json'
        features.append(dict(identifier=ident,member=target,exists_in_archive=target in z.namelist(),
         sha256=sha_bytes(z.read(target)) if target in z.namelist() else None,
         data=json.loads(z.read(target)) if target in z.namelist() else None))
      for x in v.values():collect(x)
     elif isinstance(v,list):
      for x in v:collect(x)
    if data:collect(data)
    classification='TERMINAL_IDENTIFIER_LOCAL_JSON_ABSENT' if pool=='minecraft:empty' else 'PILLAR_OR_FEATURE_DEPENDENCY' if ':feature/' in pool else 'EXTERNAL_VILLAGE_STREET' if pool.endswith(('/roads','/streets')) else 'ENTITY_POOL_IDENTIFIER'
    dependencies.append(dict(pool=pool,classification=classification,member=member,exists_in_archive=data is not None,
     sha256=sha_bytes(z.read(member)) if data is not None else None,
     configured_features=features,scope='Identity and configuration only, no generation or assembly'))
  rows.append(dict(id=c['id'],nbt_sha256=c['nbt_sha256'],fittings=fittings,dependencies=dependencies))
 dump('fittings-and-dependencies.json',dict(entries=rows,formal_credit_added=0,
  limits=['Block positions are original source states; count is not guaranteed readable/accessed books or passable room area.',
   'NOT_IN_THIS_ARCHIVE is not proof vanilla entity pools fail at runtime. No game launched.',
   'Feature list recursion reads configuration identities only; no ground columns, streets or generated rooms assembled.']))
 old_index=ROOT/'docs/architecture/continuation-20261022/references/whole-candidates/candidates.json'
 old=next(c for c in json.loads(old_index.read_text())['candidates'] if c['id']=='W018')
 with ZipFile(old['source_jar']) as z:assert sha_bytes(z.read(old['member']))==old['nbt_sha256']
 dump('variant-family-audit.json',dict(date='2026-11-01',excluded_source='F04',
  previous_design=dict(id='W018',source_index=evidence(old_index),archive=old['source_jar'],member=old['member'],nbt_sha256=old['nbt_sha256'],size=old['size']),
  observed_shared_design='相同9×9外轮廓、四外柱、内方室、门(2,2,4)、低基座和分层收进四坡檐；书架内装与少一层屋盖不足以计第二个独立建筑设计。',
  observed_changes='原9×13×9寺庙为三层檐，9×10×9图书馆减一层檐，增加东墙六书架和讲台，局部木框/浅墙变化。',
  decision='SAME_DESIGN_FAMILY_MODIFIED_ROOF_AND_INTERIOR_NO_NEW_INDEPENDENT_REFERENCE',
  heuristic_occupancy_similarity=0.79616,exact_hash_match=False,
  actual_comparison_views=[evidence(old_index.parent/n) for n in ['W018.png','W018-plan.png']],
  current_actual_views=[evidence(OUT/f) for f in ['F04-whole.png','F04-plan.png','F04-vertical.png','F04-details.png']],
  swamp_pair_decision='F02与F03不是同一屋型：13×22×13方底窄高屋加上室与8×8×11低长屋不同。但两者均有未组装/缺证柱基，不提出完整相关参考。',
  formal_credit_added=0))
 print('Original fittings and nested configured-feature identities recorded; F04 historical family excluded.')

if __name__=='__main__':main()
