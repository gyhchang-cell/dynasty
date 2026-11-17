#!/usr/bin/env python3
"""Source/view verification for authored ruins, towers and a purpose hold."""
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
def image_check(e):
 p=Path(e['path']);assert sha(p)==e['sha256']
 with Image.open(p) as im:im.verify()
def main():
 s=get('sources.json');r=get('manual-review.json');d=get('dedup-evidence.json');a=get('interface-audit.json');de=get('detail-evidence.json');st=get('vertical-original-states.json')
 assert all(len(v)==4 for v in [s['candidates'],r['entries'],d['entries'],a['entries'],de['entries'],st['entries']])
 assert d['historical_unique_local_archive_member_pairs']==174 and not d['within_batch_exact_duplicate_pairs']
 for archive in s['source_archives']:assert sha(Path(archive['path']))==archive['sha256']
 actors={x['member']:x for x in get('actor-component-boundary.json')['entries']};assert len(actors)==3
 proposals=[];counts={}
 for c,v,dup,ai,detail,states in zip(s['candidates'],r['entries'],d['entries'],a['entries'],de['entries'],st['entries']):
  i=c['id'];assert all(x['id']==i for x in [v,dup,ai,detail,states])
  assert c['nbt_sha256']==v['nbt_sha256']==dup['nbt_sha256']==states['nbt_sha256'] and not dup['historical_exact_matches']
  assert set(v['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'} and all(len(x)>20 for x in v['observations'].values())
  assert v['credit_proposal']==int(i!='F04') and not v['formal_credit_added'] and not v['native_acceptance']
  assert len(v['images_actually_viewed'])==4 and {x['path'] for x in v['images_actually_viewed']}=={str(OUT/n) for n in c['images']+[i+'-details.png']}
  for e in v['images_actually_viewed']:image_check(e)
  with ZipFile(c['source_archive']) as z:
   raw=z.read(c['member']);original=read(raw);p=original.get('palette') or original['palettes'][0]
   assert digest(raw)==c['nbt_sha256'] and original['size']==c['size']
   selected=[dict(position=b['pos'],state=p[b['state']]) for b in original['blocks'] if p[b['state']]['Name'].endswith(('_stairs','_door')) or p[b['state']]['Name']=='minecraft:ladder']
   assert selected==states['stairs_doors_ladders']
   for pool in c['pool_references']:assert json.loads(z.read(pool['member']))==pool['data']
   count=Counter(x['data']['pool'] for x in c['sockets']);counts[i]=dict(count)
   assert set(count)=={v['pool'] for v in ai['outgoing_pools']}
   for pool in ai['outgoing_pools']:
    assert pool['status']=='FOUND_LOCAL' and pool['pool'].startswith('kaisyn:outpost/pillagers/')
    assert pool['socket_positions']==[x['position'] for x in c['sockets'] if x['data']['pool']==pool['pool']]
    raw=z.read(pool['member']);assert digest(raw)==pool['sha256'] and json.loads(raw)==pool['data']
    for comp in pool['component_identities_only']:
     assert comp['exists_in_archive'] and not comp['studied_or_credited_as_complete_building']
     raw=z.read(comp['member']);cd=read(raw);cp=cd.get('palette') or cd['palettes'][0];actor=actors[comp['member']]
     assert digest(raw)==comp['sha256']==actor['sha256'] and cd['size']==actor['size']==[1,3,1]
     assert [e['nbt']['id'] for e in cd['entities']]==actor['entity_ids'] and len(actor['entity_ids'])==1
     assert actor['entity_ids'][0] in ['minecraft:pillager','minecraft:vindicator']
     assert dict(Counter(cp[b['state']]['Name'] for b in cd['blocks']))==actor['materials']
     assert not actor['images_viewed'] and not actor['assembled'] and not actor['building_credit']
  if i!='F04':proposals.append(dict(id='012-'+i,status='PENDING_SCOPE_AND_DESIGN_FAMILY_ACCEPTANCE',formal_credit_added=0,
   proposed_scope=v['proposed_target'],source=c,observations=v['observations'],independent_design_basis=v['independent_design_basis'],
   actual_views=v['images_actually_viewed'],original_vertical_states=states,dedup=dup,outgoing_pool_evidence=ai,
   semantic_deduplication=r['semantic_deduplication'],limitations=['One entire authored design, no tower/room/balcony/flag/actor/view splitting.',
    'Purpose/scale and family require independent acceptance; F03 long-hall variants require scrutiny beyond roof form.',
    'No native collision, terrain, route or gameplay certification; no new construction.']))
 assert len(proposals)==3 and r['entries'][3]['status']=='WINDMILL_PURPOSE_AND_FUNCTION_HOLD'
 assert [sum(v.values()) for v in counts.values()]==[11,12,8,7]
 expected=[[],[(7,12,[26,27,28,29])],[(4,6,list(range(1,12))),(4,10,list(range(1,12))),(25,6,[1,2,3]),(25,10,[1,2,3]),(6,8,list(range(11,30)))],[(12,15,[10,11,12]),(13,14,list(range(14,20)))]]
 for detail,w in zip(de['entries'],expected):assert {(x['x'],x['z'],tuple(x['ys'])) for x in detail['ladder_runs']}=={(x,z,tuple(y)) for x,z,y in w}
 assert len(r['historical_comparison_views'])==6
 for e in r['historical_comparison_views']:image_check(e)
 master=OUT.parent/'continuation-20261022/references/full-buildings.json';ledger=OUT.parent/'research-20261101-scoped-outpost-ledger/outpost-scope-register.json'
 assert sha(master)=='9901cbff65cb11f32b9b6c56e62a727113c8978192f174061ed8491348b4e408'
 assert sha(ledger)=='2426e889e05abf75b9afe50ae0ab50a1a40420e53ae94332c425a43e3606f267'
 scopes=json.loads(ledger.read_text())['scope_status'];assert len(scopes)==3 and all(x['accepted_references']==1 and x['remaining']==999 for x in scopes)
 assert get('discovery-boundary.json')['network_requests']==0
 dump('reference-proposals.json',dict(entries=proposals,formal_credit_added=0,boundary='Three unaccepted whole-design proposals, one windmill purpose hold.'))
 report=dict(status='PASS_THREE_TOWER_PROPOSALS_AND_WINDMILL_HOLD',templates_studied=4,new_images_actually_viewed_and_verified=16,
  historical_images_reviewed_again=6,seven_aspect_reviews=4,proposals=3,scope_held=1,formal_credit_added=0,historical_archive_member_pairs_checked=174,
  actor_components_checked=3,socket_counts=counts,legacy_count=148,legacy_remaining=852,cod6=0,
  existing_scopes=[dict(id=x['id'],accepted=1,remaining=999) for x in scopes],legacy_registry_sha256=sha(master),scoped_register_sha256=sha(ledger),
  java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0,
  limits=['174 archive/member pairs are dedup identities, not174 complete relevant buildings.',
   'No current relevant scope at1000, no production design started.',
   'F04 windmill form does not prove guard-tower or machine-workshop purpose.',
   'Diagram/source checks do not certify native materials, collision, assembly or full access.'])
 dump('verification.json',report)
 lines=['# 第十二批：错层废塔、窄高塔与端塔长厅','',
  '实际查看4份作者完整布局模板的16张新研究图，重看6张历史比较图；七项观察逐例保存。3份限定用途/规模待验提案，1份风车状塔屋因用途/功能缺证保留研究，正式新增0。','',
  '[逐例观察](manual-review.json) · [提案](reference-proposals.json) · [来源](sources.json) · [去重](dedup-evidence.json) · [接口](interface-audit.json) · [补剖](detail-evidence.json) · [门梯台阶](vertical-original-states.json) · [实体边界](actor-component-boundary.json) · [验证](verification.json)','',
  '| 编号 | 研究图 | 限定范围 |','|---|---|---|']
 for c,v in zip(s['candidates'],r['entries']):lines.append(f'| {c["id"]} | [整体及剖切]({c["id"]}-whole.png) | {v["proposed_target"]} |')
 lines+=['','F01按作者整座废塔布局研究，残台、外柱与小砖帽不拆数。F02主墙是蘑菇柄方块，布局为多层错移塔室和阳台，不将灰色投影误作全石塔。F03比较旧W008及011-F03的整栋厅塔关系，端塔平顶/长扶壁厅的主体差异需独立复核，屋顶变化本身不提供新增信用。','',
  'F04完整围院和风车状轮面仅说明形态，没有认证机械驱动/研磨设备、当前任务用途或原生路线。两段梯y10..12与y14..19的转接不能补想成已验连续梯。所有外接池在固定本地源内，三个实体模板均1×3×1，不计建筑。','',
  '## 可应用原则','']+['- '+x for x in r['principles']]
 lines+=['','原三个前哨范围仍各1/1000、缺999；义庄/墓园原账148/1000、缺852；COD6仍0。174个历史归档/成员组合只是去重筛查量，不是合格建筑数。','',
  '未运行Java/Gradle/游戏/网络，未操作声音、亮度、窗口或存档。未改专业资产、任务/指南针和主清单，未删除未完成提示词。','']
 (OUT/'HANDOFF.md').write_text('\n'.join(lines))
 for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files]))
 for e in get('RECEIPT.json')['files']:assert (OUT/e['path']).stat().st_size==e['bytes'] and sha(OUT/e['path'])==e['sha256']
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
