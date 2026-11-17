#!/usr/bin/env python3
"""Offline source, view, secondary-component and ledger boundary checks."""
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
PROPOSE={'F01','F02','F03','F05'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def get(n):return json.loads((OUT/n).read_text())
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def image_check(e):
 p=Path(e['path']);assert sha(p)==e['sha256']
 with Image.open(p) as im:im.verify()
def main():
 s=get('sources.json');r=get('manual-review.json');d=get('dedup-evidence.json');a=get('interface-audit.json')
 de=get('detail-evidence.json');st=get('vertical-original-states.json');sec=get('secondary-component-boundary.json')
 assert all(len(v)==5 for v in [s['candidates'],r['entries'],d['entries'],a['entries'],de['entries'],st['entries']])
 assert d['historical_unique_local_archive_member_pairs']==165 and not d['within_batch_exact_duplicate_pairs']
 for archive in s['source_archives']:assert sha(Path(archive['path']))==archive['sha256']
 secondary={x['member']:x for x in sec['entries']};assert len(secondary)==6
 proposals=[];counts={}
 for c,v,dup,ai,detail,states in zip(s['candidates'],r['entries'],d['entries'],a['entries'],de['entries'],st['entries']):
  i=c['id'];assert all(x['id']==i for x in [v,dup,ai,detail,states])
  assert c['nbt_sha256']==v['nbt_sha256']==dup['nbt_sha256']==states['nbt_sha256'] and not dup['historical_exact_matches']
  assert set(v['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
  assert all(len(x)>20 for x in v['observations'].values())
  assert v['credit_proposal']==int(i in PROPOSE) and not v['formal_credit_added'] and not v['native_acceptance']
  assert len(v['images_actually_viewed'])==4
  assert {x['path'] for x in v['images_actually_viewed']}=={str(OUT/n) for n in c['images']+[i+'-details.png']}
  for e in v['images_actually_viewed']:image_check(e)
  with ZipFile(c['source_archive']) as z:
   raw=z.read(c['member']);original=read(raw);p=original.get('palette') or original['palettes'][0]
   assert digest(raw)==c['nbt_sha256'] and original['size']==c['size']
   chosen=[dict(position=b['pos'],state=p[b['state']]) for b in original['blocks'] if p[b['state']]['Name'].endswith(('_stairs','_door')) or p[b['state']]['Name']=='minecraft:ladder']
   assert states['stairs_doors_ladders']==chosen
   for pool in c['pool_references']:assert json.loads(z.read(pool['member']))==pool['data']
   counter=Counter(x['data']['pool'] for x in c['sockets']);counts[i]=dict(counter)
   assert set(counter)=={x['pool'] for x in ai['outgoing_pools']}
   for pool in ai['outgoing_pools']:
    assert pool['status']=='FOUND_LOCAL' and pool['socket_positions']==[x['position'] for x in c['sockets'] if x['data']['pool']==pool['pool']]
    raw=z.read(pool['member']);assert digest(raw)==pool['sha256'] and json.loads(raw)==pool['data']
    for comp in pool['component_identities_only']:
     assert comp['exists_in_archive'] and not comp['studied_or_credited_as_complete_building']
     raw=z.read(comp['member']);cd=read(raw);cp=cd.get('palette') or cd['palettes'][0];vsec=secondary[comp['member']]
     assert digest(raw)==comp['sha256']==vsec['sha256'] and cd['size']==vsec['size']
     assert [e['nbt']['id'] for e in cd.get('entities',[])]==vsec['entity_ids']
     assert dict(Counter(cp[b['state']]['Name'] for b in cd['blocks']))==vsec['materials']
     assert [dict(position=b['pos'],data=b.get('nbt',{})) for b in cd['blocks'] if cp[b['state']]['Name']=='minecraft:jigsaw']==vsec['sockets']
     assert not vsec['images_viewed'] and not vsec['assembled'] and not vsec['building_credit']
  if i in PROPOSE:
   proposals.append(dict(id='010-'+i,status='PENDING_SCOPE_OWNER_ACCEPTANCE',formal_credit_added=0,
    proposed_scope=v['proposed_target'],source=c,observations=v['observations'],independent_design_basis=v['independent_design_basis'],
    actual_views=v['images_actually_viewed'],original_vertical_states=states,dedup=dup,outgoing_pool_evidence=ai,
    semantic_deduplication=r['semantic_deduplication'],limitations=[
     'One whole authored design; no separate roofs, posts, rooms, actor or screenshot credit.',
     'No automatic credit in existing scopes; purpose, scale and design family await owner review.',
     'No native terrain, collision, whole route, style or gameplay certification.']))
 assert len(proposals)==4 and r['entries'][3]['status']=='WHOLE_RESIDENCE_FORT_PURPOSE_AND_COMPOUND_HOLD'
 actors=[x for x in secondary.values() if x['role']=='actor'];plots=[x for x in secondary.values() if x['role']!='actor']
 assert len(actors)==4 and len(plots)==2
 assert all(x['size']==[1,3,1] and len(x['entity_ids'])==1 for x in actors)
 assert set(e for x in actors for e in x['entity_ids'])=={'minecraft:pillager','minecraft:vindicator','minecraft:villager'}
 assert {tuple(x['size']) for x in plots}=={(14,3,24),(13,5,18)}
 for x in plots:
  assert not x['entity_ids'] and len(x['sockets'])==5
  assert Counter(v['data']['pool'] for v in x['sockets'])=={'kaisyn:outpost/pillagers/grunt':4,'minecraft:empty':1}
  assert not set(x['materials'])&{'minecraft:wheat','minecraft:carrots','minecraft:potatoes','minecraft:farmland','minecraft:beetroots'}
 assert [sum(v.values()) for v in counts.values()]==[8,15,13,10,13]
 wanted=[[(3,3,list(range(2,8))),(16,2,[2,3,4])],[(7,16,[6,7,8,9]),(23,14,[6,7,8,9])],[],
  [(4,6,list(range(2,8))),(6,4,[2,3,4]),(11,5,[2,3,4])],[(13,15,[7,8,9]),(15,11,list(range(7,13))),(17,16,[7,8,9])]]
 for detail,expected in zip(de['entries'],wanted):
  assert {(v['x'],v['z'],tuple(v['ys'])) for v in detail['ladder_runs']}=={(x,z,tuple(y)) for x,z,y in expected}
 assert len(r['historical_comparison_views'])==4
 for e in r['historical_comparison_views']:image_check(e)
 master=OUT.parent/'continuation-20261022/references/full-buildings.json'
 ledger=OUT.parent/'research-20261101-scoped-outpost-ledger/outpost-scope-register.json'
 assert sha(master)=='9901cbff65cb11f32b9b6c56e62a727113c8978192f174061ed8491348b4e408'
 assert sha(ledger)=='2426e889e05abf75b9afe50ae0ab50a1a40420e53ae94332c425a43e3606f267'
 assert len(json.loads(master.read_text())['entries'])==148
 scopes=json.loads(ledger.read_text())['scope_status'];assert len(scopes)==3 and all(x['accepted_references']==1 and x['remaining']==999 for x in scopes)
 assert get('discovery-boundary.json')['network_requests']==0
 dump('reference-proposals.json',dict(entries=proposals,formal_credit_added=0,boundary='Four distinct purpose/scale proposals; no automatically accepted scope references.'))
 report=dict(status='PASS_FIVE_FORT_STUDIES_AND_SECONDARY_BOUNDARIES',templates_studied=5,new_images_actually_viewed_and_verified=20,
  historical_images_reviewed_again=4,seven_aspect_reviews=5,proposals=4,scope_held=1,formal_credit_added=0,
  historical_archive_member_pairs_checked=165,actor_components_checked=4,fenced_plot_components_checked=2,socket_counts=counts,
  legacy_count=148,legacy_remaining=852,cod6=0,existing_scopes=[dict(id=x['id'],accepted=1,remaining=999) for x in scopes],
  legacy_registry_sha256=sha(master),scoped_register_sha256=sha(ledger),java_run=False,game_run=False,network_requests=0,
  production_changes=0,checklist_deletions=0,limits=['No building scope has reached1000; no new production construction.',
   '165 archive/member pairs are dedup units, not165 complete relevant buildings.',
   'Four actor templates and two neighboring plots have zero building credit.',
   'F04 field components contain fenced grass/storage space, not verified planted farms.',
   'Classified full-cell diagrams and original ladder states do not certify native rendering or route clearance.'])
 dump('verification.json',report)
 lines=['# 第十批：遗址、叠层台堡与围栅营厅','',
  '实际查看5份模板的20张新研究图、4张历史对照图，逐例记录七项建筑观察。4份分用途/规模待验提案，1份驻所暂缓完整堡垒/园区提案，正式新增0。','',
  '[逐例观察](manual-review.json) · [完整提案](reference-proposals.json) · [来源](sources.json) · [去重](dedup-evidence.json) · [接口](interface-audit.json) · [补剖](detail-evidence.json) · [原始门梯台阶](vertical-original-states.json) · [外接组件](secondary-component-boundary.json) · [验证](verification.json)','',
  '| 编号 | 研究图 | 限定范围 |','|---|---|---|']
 for c,v in zip(s['candidates'],r['entries']):lines.append(f'| {c["id"]} | [整形及剖切]({c["id"]}-whole.png) | {v["proposed_target"]} |')
 lines+=['','F01按作者完整遗址布局研究，不能补想坍塌前屋顶。F02是叠层台堡，不是四低棚围院；F03高围栅中央低长厅与F05低栅院高长厅连附翼在空间组织上不同。F04本体是小驻所，外接field实际是围栏草地与储料地块，未见作物，未装配成园区。','',
  '外接四种实体模板均为1×3×1单实体；两种field分别14×3×24和13×5×18，内部各4实体接口及1empty。这些原始配置已核对，但没有查看其图像或认证拼装，全部零建筑信用。','',
  '## 可应用原则','']+['- '+v for v in r['principles']]
 lines+=['','筛查165个历史归档/成员组合，保留四旋转几何与原始字节证据，并实际重看最近旧例的整体图；几何相似分数不代替用途、比例、布局的语义去重。','',
  '三个既有前哨范围仍各1/1000、缺999；原义庄/墓园148/1000、缺852；COD6仍0。不混算范围，不提前制作。未运行Java/游戏/网络，不操作声音、亮度、窗口或存档，不改生产资产和主清单。','']
 (OUT/'HANDOFF.md').write_text('\n'.join(lines))
 for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files]))
 for e in get('RECEIPT.json')['files']:assert (OUT/e['path']).stat().st_size==e['bytes'] and sha(OUT/e['path'])==e['sha256']
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
