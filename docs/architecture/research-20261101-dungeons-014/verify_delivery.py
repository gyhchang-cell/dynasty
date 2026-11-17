#!/usr/bin/env python3
"""Check traceable evidence and ensure unresolved tower families receive no credit."""
import ast
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def get(n):return json.loads((OUT/n).read_text())
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def check_image(e):
 p=Path(e['path']);assert sha(p)==e['sha256']
 with Image.open(p) as im:im.verify()
def main():
 s=get('sources.json');r=get('manual-review.json');d=get('dedup-evidence.json');a=get('interface-audit.json');de=get('detail-evidence.json');st=get('vertical-original-states.json')
 assert all(len(v)==4 for v in [s['candidates'],r['entries'],d['entries'],a['entries'],de['entries'],st['entries']])
 assert d['historical_unique_local_archive_member_pairs']==181 and not d['within_batch_exact_duplicate_pairs']
 for archive in s['source_archives']:assert sha(Path(archive['path']))==archive['sha256']
 actors={x['member']:x for x in get('actor-component-boundary.json')['entries']};assert len(actors)==3
 counts={}
 for c,v,dup,ai,detail,states in zip(s['candidates'],r['entries'],d['entries'],a['entries'],de['entries'],st['entries']):
  i=c['id'];assert all(x['id']==i for x in [v,dup,ai,detail,states])
  assert c['nbt_sha256']==v['nbt_sha256']==dup['nbt_sha256']==states['nbt_sha256'] and not dup['historical_exact_matches']
  assert set(v['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'} and all(len(x)>20 for x in v['observations'].values())
  assert v['status']=='FAMILY_DISTINCTNESS_UNRESOLVED_NO_PROPOSAL' and not any(v[k] for k in ['credit_proposal','formal_credit_added','native_acceptance'])
  assert len(v['images_actually_viewed'])==4 and {x['path'] for x in v['images_actually_viewed']}=={str(OUT/n) for n in c['images']+[i+'-details.png']}
  for e in v['images_actually_viewed']:check_image(e)
  with ZipFile(c['source_archive']) as z:
   raw=z.read(c['member']);original=read(raw);p=original['palette'];assert digest(raw)==c['nbt_sha256'] and original['size']==c['size']
   chosen=[dict(position=b['pos'],state=p[b['state']]) for b in original['blocks'] if p[b['state']]['Name'].endswith(('_stairs','_door')) or p[b['state']]['Name']=='minecraft:ladder']
   assert chosen==states['stairs_doors_ladders']
   for pool in c['pool_references']:assert json.loads(z.read(pool['member']))==pool['data']
   count=Counter(x['data']['pool'] for x in c['sockets']);counts[i]=dict(count);assert set(count)=={v['pool'] for v in ai['outgoing_pools']}
   for pool in ai['outgoing_pools']:
    assert pool['socket_positions']==[x['position'] for x in c['sockets'] if x['data']['pool']==pool['pool']]
    assert pool['status']=='FOUND_LOCAL'
    raw=z.read(pool['member']);assert digest(raw)==pool['sha256'] and json.loads(raw)==pool['data']
    for comp in pool['component_identities_only']:
     assert comp['exists_in_archive'] and not comp['studied_or_credited_as_complete_building']
     raw=z.read(comp['member']);cd=read(raw);cp=cd['palette'];actor=actors[comp['member']]
     assert digest(raw)==comp['sha256']==actor['sha256'] and cd['size']==actor['size']==[1,3,1]
     assert [e['nbt']['id'] for e in cd['entities']]==actor['entity_ids'] and len(actor['entity_ids'])==1
     assert actor['entity_ids'][0] in ['minecraft:pillager','minecraft:vindicator']
     assert dict(Counter(cp[b['state']]['Name'] for b in cd['blocks']))==actor['materials']
     assert not actor['images_viewed'] and not actor['assembled'] and not actor['building_credit']
 assert [sum(v.values()) for v in counts.values()]==[9,9,10,8]
 expected=[[(6,3,list(range(2,8))),(6,8,list(range(6,13))),(6,5,list(range(13,20)))],
  [(8,8,[1,2,3,4]),(8,9,[14,15,16,17]),(9,8,[14,15,16,17])],
  [(3,6,[2,3,4]),(6,3,[2,3,4])],[(6,3,[1,2,3]),(9,6,[1,2,3])]]
 for detail,w in zip(de['entries'],expected):assert {(x['x'],x['z'],tuple(x['ys'])) for x in detail['ladder_runs']}=={(x,z,tuple(y)) for x,z,y in w}
 assert len(r['historical_comparison_views'])==4
 for e in r['historical_comparison_views']:check_image(e)
 registers={
  'legacy':(OUT.parent/'continuation-20261022/references/full-buildings.json','9901cbff65cb11f32b9b6c56e62a727113c8978192f174061ed8491348b4e408'),
  'outpost':(OUT.parent/'research-20261101-scoped-outpost-ledger/outpost-scope-register.json','2426e889e05abf75b9afe50ae0ab50a1a40420e53ae94332c425a43e3606f267'),
  'urban':(OUT.parent/'research-20261101-scoped-urban-lodging-ledger/urban-lodging-scope-register.json','38a1bcaf7c032e024a18dcf5f66c00467b34771e1974299e4dad4da98b64a330')}
 for p,h in registers.values():assert sha(p)==h
 dump('reference-proposals.json',dict(entries=[],formal_credit_added=0,reason='All four complete tower templates held for unresolved family distinctness; no scoped reference proposal.'))
 report=dict(status='PASS_FOUR_NARROW_TOWER_STUDIES_FOUR_FAMILY_HOLDS',templates_studied=4,new_images_actually_viewed_and_verified=16,historical_images_reviewed_again=4,
  seven_aspect_reviews=4,proposals=0,family_holds=4,formal_credit_added=0,historical_archive_member_pairs_checked=181,actor_components_checked=3,
  socket_counts=counts,unchanged_register_sha256={n:h for n,(p,h) in registers.items()},legacy_count=148,legacy_remaining=852,
  outpost_each_accepted=1,outpost_each_remaining=999,urban_lodging_accepted=2,urban_lodging_remaining=998,cod6=0,
  java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0,
  limits=['No current relevant scope at1000; no production construction.',
   'Four templates not proven identical or independently designed; all withheld from proposals.',
   '181 archive/member pairs are geometric comparison units, not181 relevant complete buildings.',
   'Classified diagrams and original states do not certify native collision, routes or terrain.'])
 dump('verification.json',report)
 lines=['# 第十四批：四座窄塔研究，家族独立性全部暂缓','',
  '实际查看4份模板的16张新研究图，重看4张历史对照图，逐例完成布局、比例、立面、屋顶、材料、动线和地形观察。全部为完整单塔形态研究；独立设计未通过，待验提案0，正式新增0。','',
  '[逐例观察](manual-review.json) · [来源](sources.json) · [去重](dedup-evidence.json) · [接口](interface-audit.json) · [补剖](detail-evidence.json) · [原始门梯台阶](vertical-original-states.json) · [实体边界](actor-component-boundary.json) · [验证](verification.json)','',
  '四座均有中央柱、外围室板和上室。可见室板高度、宽窄、出檐和屋顶差异，但本批不把木种、覆苔、窗、帽顶或不同哈希当独立建筑依据，也未武断认定四座完全相同。保留完整研究记录供进一步复核。','',
  '181个历史archive/member对已做精确几何比较，不代表181个合格参考；几何最近D008海庙另有用途和层次，与塔不同，但这不能证明塔彼此独立。三个外接实体模板均为1×3×1单掠夺者/卫道士，未作建筑、图像或组件拼装验收。','',
  '## 可应用原则','']+['- '+x for x in r['principles']]
 lines+=['','DUN05大型公共商住/旅店布局仍2/1000、缺998；三个前哨范围各1/1000、缺999；义庄/墓园148/1000、缺852；COD6仍0。未运行Java、游戏或网络，未改程序、美术、任务/指南针、主清单、声音、亮度、窗口或存档。','']
 (OUT/'HANDOFF.md').write_text('\n'.join(lines))
 for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files]))
 for e in get('RECEIPT.json')['files']:assert (OUT/e['path']).stat().st_size==e['bytes'] and sha(OUT/e['path'])==e['sha256']
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
