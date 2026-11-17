#!/usr/bin/env python3
"""Owner acceptance of three studies into three isolated purpose/scale scopes."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from zipfile import ZipFile

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
BASE=OUT.parent
SRC=BASE/'research-20261101-dungeons-003'
INDEX=BASE/'research-20261101-dungeons-acceptance'
MASTER=BASE/'continuation-20261022/references/full-buildings.json'
MASTER_SHA='9901cbff65cb11f32b9b6c56e62a727113c8978192f174061ed8491348b4e408'
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from reference_components import geometry_hash,role
from whole_building_candidates import AIR

SCOPES={
 'F01':dict(id='DUN03-OUTPOST-TWIN-TALL-TOWERS',name='双高塔与低连接体防御前哨',
  scale='48×48×48保存盒；实际占用高度39格。参考多层高塔与低连体的前哨，非16格单层角棚。',
  use='DUN03外围/入口局部防御节点：双核心塔、下部分室与中间连接咽喉的组织。',
  exclusion='不覆盖长城、瓮城、主城堡、完整战场或四角小棚；双塔合为一项设计。'),
 'F05':dict(id='DUN03-OUTPOST-CORNER-TOWER-L-HALL',name='高角塔连L形低厅防御前哨',
  scale='27×45×35保存盒；实际占用27×45×34。参考角部细高塔与低厅，不替代低四棚围院。',
  use='DUN03局部哨站：长低厅、偏角制高点与入口支线的层次。',
  exclusion='不覆盖多塔围城、大型城馆或整战场；完整L厅与角塔组合最多一例。'),
 'F09':dict(id='DUN03-OUTPOST-LOW-FOUR-CANOPY',name='近地四角哨棚与低墙开院',
  scale='16×8×16保存及占用盒，单层近地；不接受高塔堡通过缩放直接替代本范围。',
  use='DUN03外围小型警戒节点：低墙、四角棚、主要开口和院心视线。',
  exclusion='不覆盖双高塔、角塔连厅、瓮城或完整战场；四棚及四实体点合为一个哨点。'),
}
REREAD=[BASE/'research-20261101-dungeons-001/F02-whole.png',
 BASE/'research-20261101-dungeons-001/F07-whole.png',
 BASE/'continuation-20261022/references/whole-candidates/W026.png',
 *[SRC/f'{ident}-whole.png' for ident in SCOPES]]
SEMANTIC={
 'F01':'本次重看旧ruined_castle全景，其集中破损多角塔、前伸桥与残墙围合，异于本例双主塔夹低连接体；结合原117单位去重及第二批长院堡、低双塔堡、双高厅堡的既有布局记录，不属于旋转或换材质。',
 'F05':'本次重看Trek castle全景，其厚石多角围合、宽塔帽及内院与本例细高角塔连L形低厅不同；第二批small_keep为紧凑尖塔与两低厅、woodland_keep为环院对角高楼。本例不是这些布局的旋转覆绿。',
 'F09':'原研究已对照stray_ruins全景/平面，雪覆残墙开院并非本例四角有顶棚。本次重看Terralith graveyard，墓列及一侧矮墙开院无四角棚；与四棚哨点用途、空间和屋盖不同。',
}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def get(p):return json.loads(p.read_text())
def ev(p):return dict(path=str(p),sha256=sha(p))
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

def main():
 assert sha(MASTER)==MASTER_SHA and len(get(MASTER)['entries'])==148
 support_path=SRC/'coordinator-independent-three-outpost-review-20261101.json'
 support=get(support_path)
 assert support['formal_credit_added']==0
 assert {e['id'] for e in support['entries']}==set(SCOPES)
 for e in support['report_inputs']:assert sha(ROOT/e['path'])==e['sha256']
 # Preserve completed batches; validate their covered files without modifying them.
 for folder in [SRC,BASE/'research-20261101-dungeons-002']:
  for e in get(folder/'RECEIPT.json')['files']:assert sha(folder/e['path'])==e['sha256']
 s=get(SRC/'sources.json');r=get(SRC/'manual-review.json');d=get(SRC/'dedup-evidence.json')
 detail=get(SRC/'detail-evidence.json');interfaces=get(SRC/'interface-audit.json')
 assert d['historical_unique_local_archive_member_pairs']==117 and not d['within_batch_exact_duplicate_pairs']
 assert len(get(INDEX/'acceptance-index.json')['entries'])==12
 by=lambda rows:{e['id']:e for e in rows}
 sources=by(s['candidates']);reviews=by(r['entries']);dedup=by(d['entries'])
 cuts=by(detail['entries']);pools=by(interfaces['entries']);independent=by(support['entries'])
 accepted=[];scopes=[];hashes=[]
 for ident,scope in SCOPES.items():
  c=sources[ident];v=reviews[ident];de=dedup[ident];co=independent[ident]
  assert v['credit_proposal']==1 and len(v['observations'])==7
  assert not de['historical_exact_matches']
  assert c['nbt_sha256']==v['nbt_sha256']==de['nbt_sha256']==co['nbt_sha256_verified']
  assert sha(Path(c['source_archive']))==c['source_archive_sha256']==co['archive_sha256_verified']
  with ZipFile(c['source_archive']) as z:
   raw=z.read(c['member']);assert hashlib.sha256(raw).hexdigest()==c['nbt_sha256']
   nbt=read(raw);assert nbt['size']==c['size']
   pal=nbt.get('palette') or nbt['palettes'][0]
   cells={tuple(b['pos']):pal[b['state']]['Name'] for b in nbt['blocks'] if pal[b['state']]['Name'] not in AIR}
   assert geometry_hash({p:role(n) for p,n in cells.items()},nbt['size'])==de['role_sha256']
   assert geometry_hash({p:1 for p in cells},nbt['size'])==de['occupancy_sha256']
   hashes.append(de['occupancy_sha256'])
   assert {p['pool'] for p in pools[ident]['outgoing_pools']}=={p['data']['pool'] for p in c['sockets']}
   for pool in pools[ident]['outgoing_pools']:
    assert ':terrain' in pool['pool'] or ':mobs/' in pool['pool']
    assert pool['status']=='FOUND_LOCAL'
    poolraw=z.read(pool['member']);assert hashlib.sha256(poolraw).hexdigest()==pool['sha256']
    assert json.loads(poolraw)==pool['data']
    for comp in pool['component_identities_only']:
     assert comp['exists_in_archive'] and not comp['studied_or_credited_as_complete_building']
     assert hashlib.sha256(z.read(comp['member'])).hexdigest()==comp['sha256']
  assert len(v['images_actually_viewed'])==len(co['pngs_actually_viewed'])==4
  own={e['sha256'] for e in v['images_actually_viewed']}
  for e in v['images_actually_viewed']:assert sha(Path(e['path']))==e['sha256']
  for e in co['pngs_actually_viewed']:assert sha(ROOT/e['path'])==e['sha256'] and e['sha256'] in own
  accepted.append(dict(reference_id='003-'+ident,scope_id=scope['id'],decision='ACCEPTED_SCOPED_COMPLETE_BUILDING_REFERENCE',
   accepted_reference_units=1,counting_unit='Entire joined outpost / courtyard design once, not towers, shelters, components or screenshots',
   source_archive=c['source_archive'],source_archive_sha256=c['source_archive_sha256'],member=c['member'],nbt_sha256=c['nbt_sha256'],
   publisher_url=c['publisher_url'],publisher_url_access='Recorded provenance only; zero current network requests',
   stored_size=c['size'],occupied_bounds=cuts[ident]['occupied_bounds'],images_actually_studied=v['images_actually_viewed'],
   observations=v['observations'],original_dedup=de,semantic_deduplication=SEMANTIC[ident],outgoing_pool_evidence=pools[ident],
   independent_review_receipt=ev(support_path),owner_acceptance_basis='Owner actual prior whole/plan/vertical/detail and source study plus independent coordinator review; raw bytes and role/occupancy geometry rechecked here.',
   native_asset_acceptance=False,production_complete=False,whole_dungeon_credit=0,mortuary_credit=0,cod6_credit=0))
  scopes.append(dict(**scope,target_references=1000,accepted_references=1,remaining=999,
   accepted_reference_ids=['003-'+ident],production_gate='NOT_MET',construction_authorized_by_reference_gate=False,
   style_boundary='空间与比例参考；不是中式风格、原生碰撞、地形生成或战斗玩法验收。'))
 assert len(set(hashes))==3
 inputs=[SRC/n for n in ['sources.json','manual-review.json','dedup-evidence.json','detail-evidence.json','interface-audit.json','RECEIPT.json']]
 inputs += [support_path,INDEX/'acceptance-index.json',BASE/'research-20261101-dungeons-002/manual-review.json',BASE/'research-20261101-dungeons-002/RECEIPT.json']
 ledger=dict(date='2026-11-01',register='Isolated dungeon outpost purpose/scale reference scopes',version=1,
  entries=accepted,scope_status=scopes,accepted_unique_references=3,
  accounting='Three separately bounded scopes each hold 1/1000. No common 3/1000 production threshold is asserted; no credit transfer to any other building or dungeon.',
  supersedes_proposal_only_status_for=['003-F01','003-F05','003-F09'],source_reports_remain_historical=True,
  source_evidence=[ev(p) for p in inputs],historical_images_actually_reviewed_again=[ev(p) for p in REREAD],
  dedup_boundary='Original 117 local archive/member exact and rotated-geometry screen retained; owner geometry rechecked for three accepted sources, visual family reasoning documented. No claim that every one of 117 historical units received a new semantic review.',
  legacy_registry=dict(path=str(MASTER),sha256=MASTER_SHA,entries=148,original_scope='义庄/墓园',remaining=852,cod6=0,modified=False),
  new_buildings_created=0,main_checklist_modified=False,prompt_items_deleted=0,java_run=False,game_run=False,network_requests=0)
 dump('outpost-scope-register.json',ledger)
 # Validate written cross-links and nontransferable counters.
 written=get(OUT/'outpost-scope-register.json')
 assert len(written['entries'])==3 and len(written['scope_status'])==3
 for scope in written['scope_status']:
  assert scope['accepted_references']==1 and scope['remaining']==999 and scope['production_gate']=='NOT_MET'
  assert {e['reference_id'] for e in written['entries'] if e['scope_id']==scope['id']}==set(scope['accepted_reference_ids'])
 assert sha(MASTER)==MASTER_SHA
 report=dict(status='PASS_SCOPED_REFERENCE_ACCEPTANCE_ONLY',accepted_unique_designs=3,scope_counts={s['id']:'1/1000; remaining999' for s in scopes},
  legacy_registry_unchanged_sha256=MASTER_SHA,master_count=148,legacy_scope_remaining=852,cod6=0,
  owner_raw_geometry_rechecks=3,coordinator_actual_views_from_receipt=12,owner_historical_views_revisited_this_acceptance=6,
  original_historical_archive_member_screen=117,new_universal_credit=0,production_gate_met=False,checklist_deletions=0,java_run=False,game_run=False,network_requests=0)
 dump('verification.json',report)
 lines=['# 三例防御前哨的限定范围正式接纳','',
  '结合专岗此前实际原始来源与四图研究、历史去重，以及主协调独立查看12张图的收据，正式接纳三项完整建筑参考。这里只接纳参考研究，未制作或验收游戏建筑。','',
  '**按用途与规模分成三个范围，各1/1000、各缺999，不建立通用3/1000门槛。** 原义庄/墓园148/1000与COD6的0不变；三个范围不能互借，也不代表任何地下城整体增加三座完整参考。','',
  '| 参考 | 限定范围 | 尺度 | 本范围 |','|---|---|---|---|']
 for ident,scope in SCOPES.items():
  lines.append(f'| [003-{ident}](../research-20261101-dungeons-acceptance/003-{ident}.md) | {scope["name"]} | {scope["scale"]} | 1/1000，缺999 |')
 lines+=['','[正式独立范围台账](outpost-scope-register.json) · [核查结果](verification.json) · [主协调独立复核](../research-20261101-dungeons-003/coordinator-independent-three-outpost-review-20261101.json)','',
  '本次重新核对三份原始NBT及角色/占用几何，核对来源归档、四视图哈希、门梯与外接地形/实体池。重看三张旧比较图及三张前哨全景，排除可见布局家族误并。保留既有117个归档/成员的筛查，不声称本次重新逐一研究117例。双塔不拆两例，四棚不拆四例。','',
  '第二、三批原报告与12例入口是当时的提案状态，未改写历史；本台账只更新003-F01/F05/F09的限定范围参考接纳状态，其他9例仍待独立验收。','',
  '空间比例借鉴不等于中式风格合格，结构渲染不等于原生贴图、碰撞、地形或整条游戏动线验收。未达任一范围1000，不开始新建/重做/新增建筑；未运行Java/游戏/网络、未修改生产资产、主清单或提示词。','']
 (OUT/'HANDOFF.md').write_text('\n'.join(lines))
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files]))
 for e in get(OUT/'RECEIPT.json')['files']:assert sha(OUT/e['path'])==e['sha256']
 print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
