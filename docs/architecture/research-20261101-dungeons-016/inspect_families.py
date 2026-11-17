#!/usr/bin/env python3
"""Measure specified original structural categories; no automatic semantic acceptance."""
from collections import Counter
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
def digest(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def form(s):
 n=s['Name'];r=None
 if n.endswith(('_log','_wood')):r='post'
 elif n.endswith('_planks'):r='planks'
 elif n.endswith('_stairs'):r='stairs'
 elif n.endswith('_slab'):r='slab'
 elif n.endswith('_wall'):r='wall'
 elif n.endswith('_fence'):r='fence'
 elif n in ['minecraft:cobblestone','minecraft:mossy_cobblestone','minecraft:mud_bricks']:r='masonry'
 return None if r is None else dict(form=r,properties=s.get('Properties',{}))
def extract(c):
 with ZipFile(c['source_archive']) as z:raw=z.read(c['member'])
 assert digest(raw)==c['nbt_sha256']
 d=read(raw);p=d.get('palette') or d['palettes'][0]
 rows={tuple(b['pos']):form(p[b['state']]) for b in d['blocks'] if form(p[b['state']]) is not None}
 ladders=[dict(position=b['pos'],state=p[b['state']]) for b in d['blocks'] if p[b['state']]['Name']=='minecraft:ladder']
 return rows,ladders
def pair(a,b,ar,br):
 aa,al=ar;bb,bl=br;common=set(aa)&set(bb);union=set(aa)|set(bb)
 diffs=[dict(position=list(p),left=aa.get(p),right=bb.get(p)) for p in sorted(union) if aa.get(p)!=bb.get(p)]
 return dict(left=a,right=b,left_structural_positions=len(aa),right_structural_positions=len(bb),
  common_positions=len(common),union_positions=len(union),same_form_and_properties=sum(aa[p]==bb[p] for p in common),
  occupancy_jaccard=len(common)/len(union),differences=diffs,ladder_original_states_equal=al==bl)
def main():
 sources=load(OUT/'sources.json')['candidates'];cache={c['id']:extract(c) for c in sources}
 old=next(e for e in load(OUT.parent/'research-20261101-dungeons-013/sources.json')['candidates'] if e['id']=='F03')
 evidence=pair('016-F05','013-F03',cache['F05'],extract(old))
 pairs=[pair(a,b,cache[a],cache[b]) for a,b in [('F02','F03'),('F02','F04'),('F03','F04')]]
 (OUT/'family-structural-evidence.json').write_text(json.dumps(dict(
  normalization='Original coordinates, no scale fitting or spatial alignment. Select logs/wood, planks, stairs, slabs, walls, fences and the three listed masonry blocks; replace material names by forms, retain every state property. All excluded blocks are outside this selected-category measure.',
  selected_masonry=['minecraft:cobblestone','minecraft:mossy_cobblestone','minecraft:mud_bricks'],
  ignored_for_this_measure='Not an all-solid or universal geometry hash; vines, soil, furniture, actors, sockets, glass and other categories are not measured. Exact full-NBT canonical role/occupancy screening is separate.',
  within_batch=pairs,cross_source_reuse=evidence,prior_source_identity={k:old[k] for k in ['source_archive','source_archive_sha256','member','nbt_sha256','size']},
  semantic_decision_automatic=False,formal_credit_added=0),ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(dict(within_batch=[{k:v for k,v in e.items() if k!='differences'} for e in pairs],cross_source={k:v for k,v in evidence.items() if k!='differences'}),ensure_ascii=False))
if __name__=='__main__':main()
