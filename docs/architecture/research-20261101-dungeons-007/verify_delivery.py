#!/usr/bin/env python3
"""Verify offline source, actual-view receipts and bounded research proposals."""
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
PROPOSE={'F01','F05','F06','F07','F08'}
KINDS={'minecraft:bookshelf','minecraft:chiseled_bookshelf','minecraft:lectern','minecraft:cartography_table'}
def digest(raw):return hashlib.sha256(raw).hexdigest()
def sha(p):return digest(p.read_bytes())
def get(n):return json.loads((OUT/n).read_text())
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def check_image(e):
 p=Path(e['path']);assert sha(p)==e['sha256']
 with Image.open(p) as im:im.verify()
def main():
 s=get('sources.json');r=get('manual-review.json');d=get('dedup-evidence.json');a=get('interface-audit.json')
 details=get('detail-evidence.json');f=get('fittings-and-dependencies.json');family=get('variant-family-audit.json')
 assert all(len(x)==8 for x in [s['candidates'],r['entries'],d['entries'],a['entries'],details['entries'],f['entries']])
 assert d['historical_unique_local_archive_member_pairs']==149 and not d['within_batch_exact_duplicate_pairs']
 for archive in s['source_archives']:assert sha(Path(archive['path']))==archive['sha256']
 proposals=[];socket_counts={}
 for c,v,de,ai,dd,ff in zip(s['candidates'],r['entries'],d['entries'],a['entries'],details['entries'],f['entries']):
  ident=c['id'];assert all(x['id']==ident for x in [v,de,ai,dd,ff])
  assert c['nbt_sha256']==v['nbt_sha256']==de['nbt_sha256']==ff['nbt_sha256']
  assert not de['historical_exact_matches']
  assert set(v['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
  assert all(len(t)>20 for t in v['observations'].values())
  assert v['credit_proposal']==int(ident in PROPOSE) and v['formal_credit_added']==0 and not v['native_acceptance']
  assert len(v['images_actually_viewed'])==4
  assert {e['path'] for e in v['images_actually_viewed']}=={str(OUT/n) for n in c['images']+[ident+'-details.png']}
  for e in v['images_actually_viewed']:check_image(e)
  with ZipFile(c['source_archive']) as z:
   raw=z.read(c['member']);original=read(raw);palette=original.get('palette') or original['palettes'][0]
   assert digest(raw)==c['nbt_sha256'] and original['size']==c['size']
   fittings=[dict(position=b['pos'],state=palette[b['state']]) for b in original['blocks'] if palette[b['state']]['Name'] in KINDS]
   assert fittings==ff['fittings']
   for pool in c['pool_references']:assert json.loads(z.read(pool['member']))==pool['data']
   counts=Counter(p['data']['pool'] for p in c['sockets']);socket_counts[ident]=dict(counts)
   assert {p['pool'] for p in ai['outgoing_pools']}==set(counts)=={p['pool'] for p in ff['dependencies']}
   for pool in ai['outgoing_pools']:
    assert len(pool['socket_positions'])==counts[pool['pool']]
    assert pool['socket_positions']==[p['position'] for p in c['sockets'] if p['data']['pool']==pool['pool']]
    exists=pool['member'] in z.namelist()
    assert (pool['status']=='FOUND_LOCAL')==exists
    if exists:
     raw=z.read(pool['member']);assert digest(raw)==pool['sha256'] and json.loads(raw)==pool['data']
     for comp in pool['component_identities_only']:
      present=comp['member'] in z.namelist();assert comp['exists_in_archive']==present
      assert not comp['studied_or_credited_as_complete_building']
      if present:assert digest(z.read(comp['member']))==comp['sha256']
   for dependency in ff['dependencies']:
    exists=dependency['member'] in z.namelist();assert dependency['exists_in_archive']==exists
    if exists:assert digest(z.read(dependency['member']))==dependency['sha256']
    for feature in dependency['configured_features']:
     present=feature['member'] in z.namelist();assert feature['exists_in_archive']==present
     if present:
      raw=z.read(feature['member']);assert digest(raw)==feature['sha256'] and json.loads(raw)==feature['data']
  if ident in PROPOSE:
   proposals.append(dict(id='007-'+ident,status='PENDING_SCOPE_OWNER_ACCEPTANCE',formal_credit_added=0,
    proposed_scope=v['proposed_target'],source=c,observations=v['observations'],
    independent_design_basis=v['independent_design_basis'],actual_views=v['images_actually_viewed'],
    dedup=de,dependencies=ai,fittings_and_feature_configuration=ff,
    limitations=['No native gameplay, terrain, collision or style acceptance.',
     'One complete design, no credit for separate rooms, roofs, furniture, sockets or components.',
     'This proposed use/scale is not the whole monastery, floating-island temple or dungeon.']))
 assert {p['id'] for p in proposals}=={'007-'+x for x in PROPOSE}
 assert details['entries'][6]['occupied_bounds'][1]==[0,14] and s['candidates'][6]['size'][1]==40
 assert socket_counts['F03']=={'minecraft:empty':1,'trek:feature/block_column/dark_oak_fence':9}
 assert socket_counts['F06']=={'minecraft:village/plains/villagers':3,'minecraft:empty':1}
 assert socket_counts['F07']=={'terralith:village/fortified/roads':1,'minecraft:village/plains/villagers':2}
 assert socket_counts['F08']=={'terralith:village/desert/roads':2,'terralith:village/desert/baby_villager':3,'minecraft:village/desert/villagers':2}
 assert r['entries'][3]['status']=='HISTORICAL_DESIGN_FAMILY_VARIANT'
 assert all(r['entries'][i]['status']=='HELD_FOUNDATION_DEPENDENCY' for i in [1,2])
 assert family['excluded_source']=='F04' and family['formal_credit_added']==0
 previous=family['previous_design'];assert sha(Path(previous['source_index']['path']))==previous['source_index']['sha256']
 with ZipFile(previous['archive']) as z:
  raw=z.read(previous['member']);assert digest(raw)==previous['nbt_sha256'] and read(raw)['size']==previous['size']
 assert len(r['historical_comparison_views'])==4
 for e in r['historical_comparison_views']+family['actual_comparison_views']+family['current_actual_views']:check_image(e)
 assert sha(MASTER)==MASTER_SHA and len(json.loads(MASTER.read_text())['entries'])==148
 ledger=OUT.parent/'research-20261101-scoped-outpost-ledger/outpost-scope-register.json'
 scopes=json.loads(ledger.read_text())['scope_status']
 assert len(scopes)==3 and all(x['accepted_references']==1 and x['remaining']==999 for x in scopes)
 assert get('discovery-boundary.json')['network_requests']==0
 dump('reference-proposals.json',dict(entries=proposals,formal_credit_added=0,
  boundary='Five different purpose/scale proposals; not five accepted references in one scope, no transfer between DUN04/DUN07 or old148.'))
 report=dict(status='PASS_BOUNDED_LIBRARY_RESEARCH_EVIDENCE',templates_studied=8,
  new_images_actually_viewed_and_verified=32,historical_images_reviewed_again=4,seven_aspect_reviews=8,
  proposals=5,foundation_held=2,historical_family_exclusions=1,formal_credit_added=0,
  historical_archive_member_pairs_checked=149,socket_counts=socket_counts,
  existing_scopes=[dict(id=x['id'],accepted=1,remaining=999) for x in scopes],scoped_register_sha256=sha(ledger),
  legacy_registry_unchanged_sha256=MASTER_SHA,legacy_count=148,legacy_remaining=852,cod6=0,
  java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0,
  limitations=['No scope has1000 related accepted designs; no construction started.',
   '149 historical member pairs include components and are not149 credited buildings.',
   'Absent vanilla/empty pool JSON in one archive is not proof of runtime failure.',
   'F03 feature height63 is configuration, no pillar/terrain assembly or63 new references.',
   'Categorical whole-block views do not certify native materials, stairs, collision or accessible paths.'])
 dump('verification.json',report)
 lines=['# 第七批：藏书用房参考核查','',
  '实际研究8份本地模板的32张新图，重看4张历史对照图；逐例记录布局、比例、立面、屋顶、材质、动线、地形。筛查149个历史归档/成员组合，不把这些组合数算成参考数。','',
  '**本批5份分用途、分规模提案，正式新增0。** 两份柱基缺证/未组装待核，一份历史设计家族变体排除。五份提案不能直接合成DUN04或DUN07的5/1000。','',
  '[逐例观察与实际看图哈希](manual-review.json) · [完整提案](reference-proposals.json) · [原始来源](sources.json) · [门梯补剖](detail-evidence.json) · [历史去重](dedup-evidence.json) · [外接池](interface-audit.json) · [原始陈设与特征配置](fittings-and-dependencies.json) · [家族排除](variant-family-audit.json) · [验证结果](verification.json)','',
  '| 编号 | 原始设计 | 范围与决定 |','|---|---|---|']
 for c,v in zip(s['candidates'],r['entries']):lines.append(f'| {c["id"]} | [{c["member"]}]({c["id"]}-whole.png) | {v["proposed_target"]} |')
 lines+=['','## 需要保留的区别','',
  '- F04与旧W018同9×9轮廓、同门及柱室组织；减一层屋盖并改书架内装仍不另计。原文/角色几何不完全相同不证明独立设计。',
  '- F02有11处木柱接口，但当前归档未见对应池；F03有9处栅栏柱特征接口和1处空入口，已读嵌套配置，没有组装柱基。',
  '- F07保存盒14×40×21，实际占用最高y14，即15格高；村民接口2、道路接口1。F06村民接口3、空入口1。',
  '- F08七接口分别为道路2、幼年村民3、原版村民2；整组围院算一个设计，不能把房间、屋顶或实体点拆成独立例。',
  '- 书架与讲台坐标用于识别藏书动线；未运行原生碰撞、读书交互、粉末块稳定或完整路径测试。','',
  '## 可借鉴原则','']+['- '+p for p in r['principles']]
 lines+=['','既有三个前哨范围各仍1/1000、缺999；原义庄/墓园148/1000、缺852，COD6仍0。本批未修改这些账本。','',
  '未制作新建筑，未改生产程序、模型、贴图、任务、指南针或主清单，未删除提示词。没有运行Java、Gradle或游戏，没有联网请求；未操作声音、亮度、窗口或存档。研究图为本地NBT分类整方块投影。','']
 (OUT/'HANDOFF.md').write_text('\n'.join(lines))
 for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files]))
 for e in get('RECEIPT.json')['files']:assert (OUT/e['path']).stat().st_size==e['bytes'] and sha(OUT/e['path'])==e['sha256']
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
