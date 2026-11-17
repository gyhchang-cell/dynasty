#!/usr/bin/env python3
"""Verify bounded tower proposals without accepting them or resolving absent pools."""
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
 s=get('sources.json');r=get('manual-review.json');d=get('dedup-evidence.json');a=get('interface-audit.json')
 de=get('detail-evidence.json');st=get('vertical-original-states.json');ac=get('actor-component-boundary.json')
 assert all(len(v)==4 for v in [s['candidates'],r['entries'],d['entries'],a['entries'],de['entries'],st['entries']])
 assert d['historical_unique_local_archive_member_pairs']==170 and not d['within_batch_exact_duplicate_pairs']
 for archive in s['source_archives']:assert sha(Path(archive['path']))==archive['sha256']
 actors={x['member']:x for x in ac['entries']};assert len(actors)==3
 proposals=[];counts={};unresolved=[]
 for c,v,dup,ai,detail,states in zip(s['candidates'],r['entries'],d['entries'],a['entries'],de['entries'],st['entries']):
  i=c['id'];assert all(x['id']==i for x in [v,dup,ai,detail,states])
  assert c['nbt_sha256']==v['nbt_sha256']==dup['nbt_sha256']==states['nbt_sha256'] and not dup['historical_exact_matches']
  assert set(v['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
  assert all(len(x)>20 for x in v['observations'].values())
  assert v['credit_proposal']==1 and v['formal_credit_added']==0 and not v['native_acceptance']
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
    assert pool['socket_positions']==[x['position'] for x in c['sockets'] if x['data']['pool']==pool['pool']]
    if pool['status']=='NOT_IN_THIS_ARCHIVE':
     assert i=='F02' and pool['pool']=='minecraft:village/common/cats' and pool['member'] not in z.namelist()
     unresolved.append(dict(id=i,pool=pool['pool'],status=pool['status'],certified=False));continue
    assert pool['status']=='FOUND_LOCAL'
    raw=z.read(pool['member']);assert digest(raw)==pool['sha256'] and json.loads(raw)==pool['data']
    for comp in pool['component_identities_only']:
     assert comp['exists_in_archive'] and not comp['studied_or_credited_as_complete_building']
     raw=z.read(comp['member']);cd=read(raw);cp=cd.get('palette') or cd['palettes'][0];actor=actors[comp['member']]
     assert digest(raw)==comp['sha256']==actor['sha256'] and cd['size']==actor['size']==[1,3,1]
     assert [e['nbt']['id'] for e in cd['entities']]==actor['entity_ids'] and len(actor['entity_ids'])==1
     assert actor['entity_ids'][0] in ['minecraft:pillager','minecraft:vindicator']
     assert dict(Counter(cp[b['state']]['Name'] for b in cd['blocks']))==actor['materials']
     assert not actor['images_viewed'] and not actor['assembled'] and not actor['building_credit']
  proposals.append(dict(id='011-'+i,status='PENDING_SCOPE_AND_DESIGN_FAMILY_ACCEPTANCE',formal_credit_added=0,
   proposed_scope=v['proposed_target'],source=c,observations=v['observations'],independent_design_basis=v['independent_design_basis'],
   actual_views=v['images_actually_viewed'],original_vertical_states=states,dedup=dup,outgoing_pool_evidence=ai,
   semantic_deduplication=r['semantic_deduplication'],limitations=[
    'Whole main building study only; no roof-only, material-only, actor, socket or screenshot credit.',
    'F01/F04 require explicit interior/scale family review before counting as separate designs.',
    'F02 vanilla cat pool definition absent from source archive; no complete generation certification.',
    'No native terrain, collision, full route, art style or gameplay acceptance.']))
 assert [sum(v.values()) for v in counts.values()]==[12,10,7,11] and len(unresolved)==1
 expected=[[],[(12,11,list(range(19,24))),(14,11,list(range(19,24)))],[(13,5,list(range(1,8))),(13,9,list(range(1,8)))],[(6,7,list(range(14,21)))]]
 for detail,w in zip(de['entries'],expected):
  assert {(x['x'],x['z'],tuple(x['ys'])) for x in detail['ladder_runs']}=={(x,z,tuple(ys)) for x,z,ys in w}
 assert len(r['historical_comparison_views'])==3
 for e in r['historical_comparison_views']:image_check(e)
 master=OUT.parent/'continuation-20261022/references/full-buildings.json';ledger=OUT.parent/'research-20261101-scoped-outpost-ledger/outpost-scope-register.json'
 assert sha(master)=='9901cbff65cb11f32b9b6c56e62a727113c8978192f174061ed8491348b4e408'
 assert sha(ledger)=='2426e889e05abf75b9afe50ae0ab50a1a40420e53ae94332c425a43e3606f267'
 scopes=json.loads(ledger.read_text())['scope_status'];assert len(scopes)==3 and all(x['accepted_references']==1 and x['remaining']==999 for x in scopes)
 assert get('discovery-boundary.json')['network_requests']==0
 dump('reference-proposals.json',dict(entries=proposals,formal_credit_added=0,boundary='Four provisional source designs with explicit family/purpose/scale review; zero accepted references.'))
 report=dict(status='PASS_TOWER_SOURCE_AND_SCOPE_BOUNDARIES',templates_studied=4,new_images_actually_viewed_and_verified=16,
  historical_images_reviewed_again=3,seven_aspect_reviews=4,proposals=4,formal_credit_added=0,
  historical_archive_member_pairs_checked=170,actor_components_checked=3,unresolved_pools=unresolved,socket_counts=counts,
  legacy_count=148,legacy_remaining=852,cod6=0,existing_scopes=[dict(id=x['id'],accepted=1,remaining=999) for x in scopes],
  legacy_registry_sha256=sha(master),scoped_register_sha256=sha(ledger),java_run=False,game_run=False,network_requests=0,
  production_changes=0,checklist_deletions=0,limits=['170 archive/member pairs are dedup identities, not170 complete building references.',
   'No relevant scope has1000 references and no new production building has started.',
   'Cat pool remains unresolved; record verification does not certify complete native generation.',
   'Whole images are classified full-cell approximations, not native rendering or verified routes.',
   'Four proposals do not guarantee four distinct accepted designs, especially F01/F04 family review.'])
 dump('verification.json',report)
 lines=['# 第十一批：单塔、收分高塔及长厅连望楼','',
  '实际查看4份完整主体模板的16张新研究图，重看3张历史对照图，逐例完成七项观察。4份有边界的待验提案，正式新增0；尤其F01/F04的主体家族独立性不能仅凭屋顶或配色通过。','',
  '[逐例观察](manual-review.json) · [完整提案](reference-proposals.json) · [来源](sources.json) · [去重](dedup-evidence.json) · [接口](interface-audit.json) · [补剖](detail-evidence.json) · [原始门梯台阶](vertical-original-states.json) · [实体边界](actor-component-boundary.json) · [验证](verification.json)','',
  '| 编号 | 研究图 | 限定范围 |','|---|---|---|']
 for c,v in zip(s['candidates'],r['entries']):lines.append(f'| {c["id"]} | [整体及剖切]({c["id"]}-whole.png) | {v["proposed_target"]} |')
 lines+=['','F01普通门全在y19，不能用默认门层代替地面入口；上大下收的宽顶塔与F04方形紧凑分层塔需进一步审主体布局。F02在y19..23才有双短梯，上方多级小帽/细颈不代表一路可登顶。F03主要空间沿横向长厅组织，两个高低尖顶和细旗不拆数。','',
  'F02有1个minecraft:village/common/cats池接口，其定义不在固定本地JAR。命名提示猫相关用途，但没有读到定义，未认证其内容、递归装配或生成行为。其余池的三个实体模板已核对为1×3×1单实体，不计建筑。','',
  '## 可应用原则','']+['- '+x for x in r['principles']]
 lines+=['','历史170个归档/成员组合用于去重，不能记为170个相关完整建筑。三个既有前哨范围各仍1/1000、缺999；原义庄/墓园148/1000、缺852，COD6仍0。','',
  '未运行Java、Gradle、游戏或网络；未操作声音、亮度、窗口或存档。没有新建筑制作、专业资产改动、任务/指南针改动或清单删除。','']
 (OUT/'HANDOFF.md').write_text('\n'.join(lines))
 for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files]))
 for e in get('RECEIPT.json')['files']:assert (OUT/e['path']).stat().st_size==e['bytes'] and sha(OUT/e['path'])==e['sha256']
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
