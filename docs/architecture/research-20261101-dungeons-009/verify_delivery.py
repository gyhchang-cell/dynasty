#!/usr/bin/env python3
"""Verify fort studies, actual entity components and unchanged reference ledgers."""
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
MASTER=ROOT/'docs/architecture/continuation-20261022/references/full-buildings.json'
MASTER_SHA='9901cbff65cb11f32b9b6c56e62a727113c8978192f174061ed8491348b4e408'
PROPOSE={'F01','F02','F04'}
def digest(raw):return hashlib.sha256(raw).hexdigest()
def sha(p):return digest(p.read_bytes())
def get(n):return json.loads((OUT/n).read_text())
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def image_check(e):
 p=Path(e['path']);assert sha(p)==e['sha256']
 with Image.open(p) as im:im.verify()
def main():
 s=get('sources.json');r=get('manual-review.json');d=get('dedup-evidence.json');a=get('interface-audit.json')
 details=get('detail-evidence.json');states=get('vertical-original-states.json')
 assert all(len(x)==4 for x in [s['candidates'],r['entries'],d['entries'],a['entries'],details['entries'],states['entries']])
 assert d['historical_unique_local_archive_member_pairs']==161 and not d['within_batch_exact_duplicate_pairs']
 for archive in s['source_archives']:assert sha(Path(archive['path']))==archive['sha256']
 entities={};proposals=[];counts={}
 for c,v,de,ai,dd,st in zip(s['candidates'],r['entries'],d['entries'],a['entries'],details['entries'],states['entries']):
  ident=c['id'];assert all(x['id']==ident for x in [v,de,ai,dd,st])
  assert c['nbt_sha256']==v['nbt_sha256']==de['nbt_sha256']==st['nbt_sha256'] and not de['historical_exact_matches']
  assert set(v['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
  assert all(len(t)>20 for t in v['observations'].values())
  assert v['credit_proposal']==int(ident in PROPOSE) and v['formal_credit_added']==0 and not v['native_acceptance']
  assert len(v['images_actually_viewed'])==4
  assert {e['path'] for e in v['images_actually_viewed']}=={str(OUT/n) for n in c['images']+[ident+'-details.png']}
  for e in v['images_actually_viewed']:image_check(e)
  with ZipFile(c['source_archive']) as z:
   raw=z.read(c['member']);original=read(raw);pal=original.get('palette') or original['palettes'][0]
   assert digest(raw)==c['nbt_sha256'] and original['size']==c['size']
   selected=[dict(position=b['pos'],state=pal[b['state']]) for b in original['blocks'] if pal[b['state']]['Name'].endswith(('_stairs','_door')) or pal[b['state']]['Name']=='minecraft:ladder']
   assert selected==st['stairs_doors_ladders']
   for pool in c['pool_references']:assert json.loads(z.read(pool['member']))==pool['data']
   counter=Counter(p['data']['pool'] for p in c['sockets']);counts[ident]=dict(counter)
   assert {p['pool'] for p in ai['outgoing_pools']}==set(counter)
   for pool in ai['outgoing_pools']:
    assert pool['pool'].startswith('kaisyn:outpost/pillagers/') and pool['status']=='FOUND_LOCAL'
    assert pool['socket_positions']==[p['position'] for p in c['sockets'] if p['data']['pool']==pool['pool']]
    raw=z.read(pool['member']);assert digest(raw)==pool['sha256'] and json.loads(raw)==pool['data']
    for comp in pool['component_identities_only']:
     assert comp['exists_in_archive'] and not comp['studied_or_credited_as_complete_building']
     raw=z.read(comp['member']);assert digest(raw)==comp['sha256']
     component=read(raw);assert component['size']==[1,3,1]
     identifiers=[e['nbt']['id'] for e in component['entities']]
     assert len(identifiers)==1 and identifiers[0] in ['minecraft:pillager','minecraft:vindicator']
     entities[comp['member']]=dict(sha256=comp['sha256'],size=component['size'],entity_ids=identifiers,building_credit=0)
  if ident in PROPOSE:
   proposals.append(dict(id='009-'+ident,status='PENDING_SCOPE_OWNER_ACCEPTANCE',formal_credit_added=0,
    proposed_scope=v['proposed_target'],source=c,observations=v['observations'],
    independent_design_basis=v['independent_design_basis'],actual_views=v['images_actually_viewed'],
    original_vertical_states=st,dedup=de,outgoing_pool_evidence=ai,
    semantic_deduplication=r['semantic_deduplication'],
    limitations=['One entire joined design, no separate credit for towers, roofs, rooms, actors or sockets.',
     'No automatic credit in existing three scopes; owner must accept purpose and scale.',
     'No native terrain, collision, full-route, style or gameplay acceptance; no new construction.']))
 assert {p['id'] for p in proposals}=={'009-'+i for i in PROPOSE}
 assert len(entities)==3
 assert [sum(c.values()) for c in counts.values()]==[14,7,6,8]
 expected_ladders=[[(10,11,[6,7,8,9,10])],[(20,4,list(range(7,19)))],[(11,10,[1,3,5])],
  [(24,14,list(range(1,11))),(20,17,[5,6])]]
 for detail,wanted in zip(details['entries'],expected_ladders):
  assert {(x['x'],x['z'],tuple(x['ys'])) for x in detail['ladder_runs']}=={(x,z,tuple(ys)) for x,z,ys in wanted}
 assert r['entries'][2]['status']=='PYRAMID_BARRACK_SCOPE_MISMATCH'
 assert len(r['historical_comparison_views'])==5
 for e in r['historical_comparison_views']:image_check(e)
 assert sha(MASTER)==MASTER_SHA and len(json.loads(MASTER.read_text())['entries'])==148
 ledger=OUT.parent/'research-20261101-scoped-outpost-ledger/outpost-scope-register.json'
 scopes=json.loads(ledger.read_text())['scope_status']
 assert len(scopes)==3 and all(x['accepted_references']==1 and x['remaining']==999 for x in scopes)
 assert get('discovery-boundary.json')['network_requests']==0
 dump('entity-component-boundary.json',dict(entries=entities,formal_credit_added=0,
  limits='Three1×3×1 original actor templates confirmed; identities not images, buildings or accepted references.'))
 dump('reference-proposals.json',dict(entries=proposals,formal_credit_added=0,
  boundary='Three purpose/scale-specific proposals, not three newly accepted references in one old scope.'))
 report=dict(status='PASS_FORT_RESEARCH_AND_ENTITY_SCOPE_BOUNDARIES',templates_studied=4,
  new_images_actually_viewed_and_verified=16,historical_images_reviewed_again=5,seven_aspect_reviews=4,
  proposals=3,scope_held=1,formal_credit_added=0,historical_archive_member_pairs_checked=161,
  original_actor_templates_checked=3,socket_counts=counts,
  existing_scopes=[dict(id=x['id'],accepted=1,remaining=999) for x in scopes],scoped_register_sha256=sha(ledger),
  legacy_registry_unchanged_sha256=MASTER_SHA,legacy_count=148,legacy_remaining=852,cod6=0,
  java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0,
  limitations=['No current scope at1000, no production building started.',
   '161 historical archive/member pairs include components and are not161 accepted buildings.',
   'Actor pool weights and socket positions do not represent room or building counts.',
   'F03 ladder states are y1/3/5 only; native climbability not tested.',
   'Whole-cell views and original states do not certify native material fidelity, terrain or route clearance.'])
 dump('verification.json',report)
 lines=['# 第九批：完整堡垒本体与实体池边界','',
  '实际查看4份本地堡垒模板的16张新研究图，并重看5张历史对照图。逐例记录布局、比例、立面、屋顶、材质、动线、地形，筛查161个历史归档/成员组合。','',
  '**3份分用途/规模提案，正式新增0；1份金字塔营房因布局范围不合保留研究。** 没有将塔、棚、房间、实体、截图或池权重拆成独立建筑计数。','',
  '[逐例观察](manual-review.json) · [完整提案](reference-proposals.json) · [来源](sources.json) · [补剖与梯段](detail-evidence.json) · [原始门梯台阶](vertical-original-states.json) · [去重](dedup-evidence.json) · [接口](interface-audit.json) · [实体模板边界](entity-component-boundary.json) · [验证](verification.json)','',
  '| 编号 | 来源 | 提案或保留范围 |','|---|---|---|']
 for c,v in zip(s['candidates'],r['entries']):lines.append(f'| {c["id"]} | [{c["member"]}]({c["id"]}-whole.png) | {v["proposed_target"]} |')
 lines+=['','## 防止误计的核查','',
  '- 四份base_plate实际包含建筑本体；名称不表示只有一块地板。向外接口分别14、7、6、8处，全是实体池，没有待接侧房池。',
  '- 原始卫道士、掠夺者、队长模板各为1×3×1且只含一个实体，已核对源字节与实体ID；不计成建筑。',
  '- F01为低双棚残墙围院；F02为26×23×10狭长高低双塔连桥；F04为三角塔连低侧楼，不靠沙色/红色/覆绿差异判新设计。',
  '- F03外壳虽像实心金字塔，底层有十字通道及四区；中心梯仅y1/3/5，未把缺格补画成连续梯，也未作原生不可攀登断言。',
  '- 重看既有三份正式前哨及最近maya、swamp_church实际图，记录空间组织差异；几何邻近分数只筛查，不是独立性证明。',
  '- 提案不直接并入旧双高塔、单角高塔L厅、四低棚三个范围；尤其F02需独立确认尺度与桥式组织是否可用于同一目标。','',
  '## 可应用原则','']+['- '+p for p in r['principles']]
 lines+=['','既有三个前哨范围各仍1/1000、缺999；原义庄/墓园148/1000、缺852；COD6仍0。未改账本或开展新建筑制作。','',
  '本轮前两批：[第七批书屋](../research-20261101-dungeons-007/HANDOFF.md)、[第八批矿业](../research-20261101-dungeons-008/HANDOFF.md)。这三批合计16份原始模板、64张实际新研究图、11张历史重看图、9份分范围待验提案；这是研究工作量，不能当成某一范围新增16或9例。','',
  '未运行Java、Gradle、游戏或网络；未操作声音、亮度、窗口或用户存档。未修改生产程序、模型、贴图、任务、指南针或主清单，未删除提示词。所有图为离线分类整方块研究图。','']
 (OUT/'HANDOFF.md').write_text('\n'.join(lines))
 for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files]))
 for e in get('RECEIPT.json')['files']:assert (OUT/e['path']).stat().st_size==e['bytes'] and sha(OUT/e['path'])==e['sha256']
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
