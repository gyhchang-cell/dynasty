#!/usr/bin/env python3
"""Validate source bytes, terrain/actor boundaries and one-proposal scope limit."""
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
 assert d['historical_unique_local_archive_member_pairs']==185 and not d['within_batch_exact_duplicate_pairs']
 for archive in s['source_archives']:assert sha(Path(archive['path']))==archive['sha256']
 components={x['member']:x for x in get('secondary-component-boundary.json')['entries']};assert len(components)==2
 counts={}
 for c,v,dup,ai,detail,states in zip(s['candidates'],r['entries'],d['entries'],a['entries'],de['entries'],st['entries']):
  i=c['id'];assert all(x['id']==i for x in [v,dup,ai,detail,states])
  assert c['nbt_sha256']==v['nbt_sha256']==dup['nbt_sha256']==states['nbt_sha256'] and not dup['historical_exact_matches']
  assert set(v['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'} and all(len(x)>20 for x in v['observations'].values())
  assert v['credit_proposal']==int(i=='F01') and not v['formal_credit_added'] and not v['native_acceptance']
  assert v['status']==('SCOPED_WHOLE_TOWER_PROPOSAL' if i=='F01' else 'FAMILY_DISTINCTNESS_UNRESOLVED_NO_PROPOSAL')
  assert len(v['images_actually_viewed'])==4 and {x['path'] for x in v['images_actually_viewed']}=={str(OUT/n) for n in c['images']+[i+'-details.png']}
  for e in v['images_actually_viewed']:check_image(e)
  with ZipFile(c['source_archive']) as z:
   raw=z.read(c['member']);original=read(raw);p=original['palette'];assert digest(raw)==c['nbt_sha256'] and original['size']==c['size']
   chosen=[dict(position=b['pos'],state=p[b['state']]) for b in original['blocks'] if p[b['state']]['Name'].endswith(('_stairs','_door')) or p[b['state']]['Name']=='minecraft:ladder']
   assert chosen==states['stairs_doors_ladders']
   for pool in c['pool_references']:assert json.loads(z.read(pool['member']))==pool['data']
   count=Counter(x['data']['pool'] for x in c['sockets']);counts[i]=dict(count);assert set(count)=={v['pool'] for v in ai['outgoing_pools']}
   for pool in ai['outgoing_pools']:
    assert pool['socket_positions']==[x['position'] for x in c['sockets'] if x['data']['pool']==pool['pool']] and pool['status']=='FOUND_LOCAL'
    raw=z.read(pool['member']);assert digest(raw)==pool['sha256'] and json.loads(raw)==pool['data']
    for comp in pool['component_identities_only']:
     assert comp['exists_in_archive'] and not comp['studied_or_credited_as_complete_building']
     raw=z.read(comp['member']);cd=read(raw);cp=cd['palette'];component=components[comp['member']]
     assert digest(raw)==comp['sha256']==component['sha256'] and cd['size']==component['size']
     assert [e['nbt']['id'] for e in cd['entities']]==component['entity_ids']
     assert dict(Counter(cp[b['state']]['Name'] for b in cd['blocks']))==component['materials']
     sockets=[dict(position=b['pos'],state=cp[b['state']],data=b.get('nbt',{})) for b in cd['blocks'] if cp[b['state']]['Name']=='minecraft:jigsaw']
     assert sockets==component['sockets'] and len(sockets)==1
     assert not component['images_viewed'] and not component['assembled'] and not component['building_credit']
     if i=='F01':
      assert cd['size']==[25,24,25] and not cd['entities'] and component['kind']=='STONE_SOIL_TERRAIN_NOT_BUILDING'
      assert set(component['materials'])=={'minecraft:andesite','minecraft:stone','minecraft:rooted_dirt','minecraft:dirt','minecraft:coarse_dirt','minecraft:grass_block','minecraft:air','minecraft:jigsaw'}
      assert sockets[0]['data']['pool']=='ati_structures:terrain_small' and sockets[0]['position']==[12,23,12]
     else:
      assert i=='F02' and cd['size']==[1,3,1] and component['entity_ids']==['minecraft:zombie_villager'] and sockets[0]['data']['pool']=='minecraft:empty'
 assert [sum(v.values()) for v in counts.values()]==[1,1,0]
 expected=[[(9,5,list(range(5,11))),(5,9,list(range(11,21)))],
  [(8,7,list(range(1,7))+[21,22,23]),(7,6,list(range(7,12))),(6,7,list(range(12,17))),(7,8,list(range(17,21)))],
  [(5,5,list(range(1,10))),(4,4,list(range(7,16)))]]
 for detail,w in zip(de['entries'],expected):assert {(x['x'],x['z'],tuple(x['ys'])) for x in detail['ladder_runs']}=={(x,z,tuple(y)) for x,z,y in w}
 assert de['entries'][0]['occupied_bounds']==[[0,14],[0,22],[0,14]]
 assert len(r['historical_comparison_views'])==4
 for e in r['historical_comparison_views']:check_image(e)
 registers={
  'legacy':(OUT.parent/'continuation-20261022/references/full-buildings.json','9901cbff65cb11f32b9b6c56e62a727113c8978192f174061ed8491348b4e408'),
  'outpost':(OUT.parent/'research-20261101-scoped-outpost-ledger/outpost-scope-register.json','2426e889e05abf75b9afe50ae0ab50a1a40420e53ae94332c425a43e3606f267'),
  'urban':(OUT.parent/'research-20261101-scoped-urban-lodging-ledger/urban-lodging-scope-register.json','38a1bcaf7c032e024a18dcf5f66c00467b34771e1974299e4dad4da98b64a330')}
 for p,h in registers.values():assert sha(p)==h
 v=r['entries'][0]
 dump('reference-proposals.json',dict(entries=[dict(id='015-F01',status='PENDING_SCOPE_AND_FAMILY_ACCEPTANCE',formal_credit_added=0,
  source=s['candidates'][0],observations=v['observations'],proposed_scope=v['proposed_target'],independent_design_basis=v['independence_question'],
  actual_views=v['images_actually_viewed'],original_vertical_states=st['entries'][0],dedup=d['entries'][0],outgoing_pool_evidence=a['entries'][0],
  limitations=['One complete mud-walled open-top watchtower layout only; terrain not credited as building.',
   'Ground y0 socket and terrain_small repeated names/fallback do not certify recursive assembly termination or world placement.',
   'No native route, art, gameplay, quest or compass acceptance.'])],formal_credit_added=0))
 report=dict(status='PASS_ONE_MUD_TOWER_LAYOUT_PROPOSAL_TWO_FAMILY_HOLDS',templates_studied=3,new_images_actually_viewed_and_verified=12,historical_images_reviewed_again=4,
  seven_aspect_reviews=3,proposals=1,family_holds=2,formal_credit_added=0,historical_archive_member_pairs_checked=185,secondary_components_checked=2,
  socket_counts=counts,unchanged_register_sha256={n:h for n,(p,h) in registers.items()},legacy_count=148,legacy_remaining=852,
  outpost_each_accepted=1,outpost_each_remaining=999,urban_lodging_accepted=2,urban_lodging_remaining=998,cod6=0,
  java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0,
  limits=['No relevant scope at1000; no production construction.',
   'F02/F03 family distinctness unresolved, neither proposed.',
   'Raw terrain component is not an assembled foundation, complete building or terrain-placement acceptance.',
   'Stored diagrams and states do not certify native routes, textures or collision.'])
 dump('verification.json',report)
 lines=['# 第十五批：泥墙敞天塔提案与两项家族暂缓','',
  '实际查看3份源模板的12张新研究图，重看4张历史对照图，逐例七项观察。015-F01泥墙方筒敞天守望塔仅整塔布局待验提案1份；F02/F03两份家族独立性暂缓，正式新增0。','',
  '[逐例观察](manual-review.json) · [提案](reference-proposals.json) · [来源](sources.json) · [去重](dedup-evidence.json) · [接口](interface-audit.json) · [补剖](detail-evidence.json) · [原始门梯台阶](vertical-original-states.json) · [组件边界](secondary-component-boundary.json) · [验证](verification.json)','',
  'F01保存高25但非空最高y22，y20大板为敞天平台，不是坡顶。terrain_small原组件25×24×25只含石土草与一个同名接口，没有实体。未渲染或拼装地基，未验证处理器、接口匹配、递归终止或落位，不增加参考实例。','',
  'F02细杆长梯托宽上室，与旧窄颈宽顶塔家族仍有疑问；F03小型中心柱叠室加砖帽，与旧同类塔待辨，缩小和烟管不自动增加实例。F02外接1×3×1单僵尸村民也不是房屋。','',
  'F02同一xz梯在y1..6及21..23两个不连续高度段，原证据逐y保存，不用min/max掩盖缺段。','',
  '## 可应用原则','']+['- '+x for x in r['principles']]
 lines+=['','既有公共商住/旅店布局2/1000、缺998，三个前哨范围各1/1000、缺999，义庄/墓园148/1000、缺852，COD6仍0。未运行Java、游戏或网络，未修改程序、美术资产、任务/指南针、主清单、声音、亮度、窗口或存档。','']
 (OUT/'HANDOFF.md').write_text('\n'.join(lines))
 for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files]))
 for e in get('RECEIPT.json')['files']:assert (OUT/e['path']).stat().st_size==e['bytes'] and sha(OUT/e['path'])==e['sha256']
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
