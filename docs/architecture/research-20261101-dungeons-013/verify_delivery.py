#!/usr/bin/env python3
"""Check three studies and preserve explicit family holds and empty terminal semantics."""
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
 assert all(len(v)==3 for v in [s['candidates'],r['entries'],d['entries'],a['entries'],de['entries'],st['entries']])
 assert d['historical_unique_local_archive_member_pairs']==178 and not d['within_batch_exact_duplicate_pairs']
 for archive in s['source_archives']:assert sha(Path(archive['path']))==archive['sha256']
 actors={x['member']:x for x in get('actor-component-boundary.json')['entries']};assert len(actors)==4
 counts={};terminals=[]
 for c,v,dup,ai,detail,states in zip(s['candidates'],r['entries'],d['entries'],a['entries'],de['entries'],st['entries']):
  i=c['id'];assert all(x['id']==i for x in [v,dup,ai,detail,states])
  assert c['nbt_sha256']==v['nbt_sha256']==dup['nbt_sha256']==states['nbt_sha256'] and not dup['historical_exact_matches']
  assert set(v['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'} and all(len(x)>20 for x in v['observations'].values())
  assert v['credit_proposal']==int(i=='F01') and not v['formal_credit_added'] and not v['native_acceptance']
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
    if pool['pool']=='minecraft:empty':
     assert i=='F03' and pool['status']=='TERMINAL_EMPTY';terminals.append(dict(id=i,pool=pool['pool'],position=pool['socket_positions']));continue
    assert pool['status']=='FOUND_LOCAL'
    raw=z.read(pool['member']);assert digest(raw)==pool['sha256'] and json.loads(raw)==pool['data']
    for comp in pool['component_identities_only']:
     assert comp['exists_in_archive'] and not comp['studied_or_credited_as_complete_building']
     raw=z.read(comp['member']);cd=read(raw);cp=cd['palette'];actor=actors[comp['member']]
     assert digest(raw)==comp['sha256']==actor['sha256'] and cd['size']==actor['size']==[1,3,1]
     assert [e['nbt']['id'] for e in cd['entities']]==actor['entity_ids'] and len(actor['entity_ids'])==1
     assert actor['entity_ids'][0] in ['minecraft:villager','minecraft:pillager','minecraft:vindicator']
     assert dict(Counter(cp[b['state']]['Name'] for b in cd['blocks']))==actor['materials']
     assert not actor['images_viewed'] and not actor['assembled'] and not actor['building_credit']
 assert [sum(v.values()) for v in counts.values()]==[10,7,8] and len(terminals)==1
 expected=[[(12,16,list(range(18,23)))],[],[(9,12,[19,20,21,22])]]
 for detail,w in zip(de['entries'],expected):assert {(x['x'],x['z'],tuple(x['ys'])) for x in detail['ladder_runs']}=={(x,z,tuple(y)) for x,z,y in w}
 assert all(x['status']=='FAMILY_DISTINCTNESS_UNRESOLVED_NO_PROPOSAL' for x in r['entries'][1:])
 assert len(r['historical_comparison_views'])==2
 for e in r['historical_comparison_views']:check_image(e)
 master=OUT.parent/'continuation-20261022/references/full-buildings.json';outpost=OUT.parent/'research-20261101-scoped-outpost-ledger/outpost-scope-register.json'
 assert sha(master)=='9901cbff65cb11f32b9b6c56e62a727113c8978192f174061ed8491348b4e408'
 assert sha(outpost)=='2426e889e05abf75b9afe50ae0ab50a1a40420e53ae94332c425a43e3606f267'
 urban=OUT.parent/'research-20261101-scoped-urban-lodging-ledger/urban-lodging-scope-register.json';ur=json.loads(urban.read_text())
 assert ur['accepted_references']==2 and ur['remaining']==998 and not ur['construction_allowed']
 v=r['entries'][0]
 dump('reference-proposals.json',dict(entries=[dict(id='013-F01',status='PENDING_SCOPE_AND_FAMILY_ACCEPTANCE',formal_credit_added=0,
  source=s['candidates'][0],observations=v['observations'],proposed_scope=v['proposed_target'],independent_design_basis=v['independent_design_basis'],
  actual_views=v['images_actually_viewed'],original_vertical_states=st['entries'][0],dedup=d['entries'][0],outgoing_pool_evidence=a['entries'][0],
  limitations=['One whole multiroom stone tower, no actor/room/roof or view splitting.','No native route, terrain, art or game acceptance.'])],formal_credit_added=0))
 report=dict(status='PASS_ONE_TOWER_PROPOSAL_TWO_FAMILY_HOLDS',templates_studied=3,new_images_actually_viewed_and_verified=12,historical_images_reviewed_again=2,
  seven_aspect_reviews=3,proposals=1,family_holds=2,formal_credit_added=0,historical_archive_member_pairs_checked=178,actor_components_checked=4,terminal_pools=terminals,
  socket_counts=counts,legacy_count=148,legacy_remaining=852,outpost_each_accepted=1,outpost_each_remaining=999,
  urban_lodging_accepted=2,urban_lodging_remaining=998,urban_register_sha256=sha(urban),cod6=0,
  java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0,
  limits=['No current relevant scope at1000; no production construction.',
   'F02/F03 not proven identical and not proven independent; both withheld from proposals.',
   '178 archive/member pairs include nonbuildings and do not count as178 related complete buildings.',
   'Classified diagram/source state checks are not native route/collision/terrain certification.'])
 dump('verification.json',report)
 lines=['# 第十三批：多室石塔及中心柱单塔家族暂缓','',
  '实际查看3份模板的12张新研究图，重看2张历史对照图，逐例完成七项观察。F01一份限定待验提案，F02/F03两份主体家族独立性暂缓，正式新增0。','',
  '[逐例观察](manual-review.json) · [提案](reference-proposals.json) · [来源](sources.json) · [去重](dedup-evidence.json) · [接口](interface-audit.json) · [补剖](detail-evidence.json) · [门梯台阶](vertical-original-states.json) · [实体边界](actor-component-boundary.json) · [验证](verification.json)','',
  'F02/F03未有精确哈希匹配，但这不能自动证明独立。两者中心柱层架、室板和上室组织需继续审；尖帽、宽檐、木种、短梯或覆苔区别不足以直接给两份信用。本批也未武断宣称它们必然是同一设计。','',
  'F01完整多小室石塔、底部低棚和偏置高帽/露台按整套设计一次。capt​​ive_snow原始组件为1×3×1单村民，其余三个组件为单掠夺者/卫道士，不计建筑。F03的minecraft:empty为终止接口，不是待建空房。','',
  '## 可应用原则','']+['- '+x for x in r['principles']]
 lines+=['','既有DUN05大型公共商住/旅店布局2/1000、缺998不变；三个前哨范围各1/1000、缺999不变；义庄/墓园148/1000、缺852不变；COD6仍0。未运行Java/游戏/网络，未改专业资产、任务/指南针、声音/亮度/窗口/存档或主清单。','']
 (OUT/'HANDOFF.md').write_text('\n'.join(lines))
 for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files]))
 for e in get('RECEIPT.json')['files']:assert (OUT/e['path']).stat().st_size==e['bytes'] and sha(OUT/e['path'])==e['sha256']
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
