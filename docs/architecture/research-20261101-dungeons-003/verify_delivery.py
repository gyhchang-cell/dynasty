#!/usr/bin/env python3
"""Validate offline evidence integrity, not native architecture acceptance."""
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile
from PIL import Image

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
MASTER=ROOT/'docs/architecture/continuation-20261022/references/full-buildings.json'
MASTER_SHA='9901cbff65cb11f32b9b6c56e62a727113c8978192f174061ed8491348b4e408'
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def get(name): return json.loads((OUT/name).read_text())
def dump(name,data): (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def main():
 s=get('sources.json'); r=get('manual-review.json'); d=get('dedup-evidence.json')
 detail=get('detail-evidence.json'); a=get('interface-audit.json')
 assert len(s['candidates'])==len(r['entries'])==len(d['entries'])==len(detail['entries'])==len(a['entries'])==12
 assert len({(c['source_archive'],c['member']) for c in s['candidates']})==12
 assert not d['within_batch_exact_duplicate_pairs']
 assert all(not e['historical_exact_matches'] for e in d['entries'])
 assert d['historical_unique_local_archive_member_pairs']==117
 for archive in s['source_archives']: assert sha(Path(archive['path']))==archive['sha256']
 images=0; proposals=[]
 for c,v,dd,ai,de in zip(s['candidates'],r['entries'],detail['entries'],a['entries'],d['entries']):
  assert c['id']==v['id']==dd['id']==ai['id']==de['id']
  assert c['nbt_sha256']==v['nbt_sha256']==de['nbt_sha256']
  assert set(v['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
  assert all(len(t)>20 for t in v['observations'].values())
  assert len(v['images_actually_viewed'])==4
  expected={str(OUT/f) for f in c['images']+[c['id']+'-details.png']}
  assert expected=={e['path'] for e in v['images_actually_viewed']}
  for e in v['images_actually_viewed']:
   p=Path(e['path']); assert sha(p)==e['sha256']
   with Image.open(p) as im: im.verify()
   images+=1
  with ZipFile(c['source_archive']) as z:
   raw=z.read(c['member']); assert hashlib.sha256(raw).hexdigest()==c['nbt_sha256']
   assert read(raw)['size']==c['size']
   for incoming in c['pool_references']: assert json.loads(z.read(incoming['member']))==incoming['data']
   assert {p['pool'] for p in ai['outgoing_pools']}=={p['data']['pool'] for p in c['sockets']}
   for pool in ai['outgoing_pools']:
    if pool['status']=='FOUND_LOCAL':
     raw=z.read(pool['member']); assert hashlib.sha256(raw).hexdigest()==pool['sha256']
     assert json.loads(raw)==pool['data']
     for component in pool['component_identities_only']:
      assert component['exists_in_archive']==(component['member'] in z.namelist())
      if component['exists_in_archive']: assert hashlib.sha256(z.read(component['member'])).hexdigest()==component['sha256']
  assert v['formal_credit_added']==0 and not v['native_acceptance']
  if v['credit_proposal']:
   proposals.append(dict(id=v['id'],target=v['proposed_target'],source_archive=c['source_archive'],
    source_archive_sha256=c['source_archive_sha256'],member=c['member'],nbt_sha256=c['nbt_sha256'],
    publisher_url=c['publisher_url'],url_access='Provenance only; no current network request',
    observations=v['observations'],independent_design_basis=v['independent_design_basis'],
    evidence_actually_viewed=v['images_actually_viewed'],computed_dedup='dedup-evidence.json#'+v['id'],
    status='PROPOSED_SCOPED_REFERENCE_NOT_FORMAL_CREDIT',formal_credit_added=0,native_acceptance=False))
 for e in r['historical_comparison_views']: assert sha(Path(e['path']))==e['sha256']
 assert images==48 and len(r['historical_comparison_views'])==4
 assert {p['id'] for p in proposals}=={'F01','F05','F09'}
 assert sum(v['status']=='SUBSPACE_PRINCIPLES_ONLY' for v in r['entries'])==6
 assert sum(v['status']=='HELD_COMPLETENESS_OR_ROUTE' for v in r['entries'])==3
 quarry=a['entries'][7]; stone=next(p for p in quarry['outgoing_pools'] if p['pool']=='ati_structures:stoneworks')
 assert len(stone['socket_positions'])==4 and len(stone['component_identities_only'])==11
 assert get('discovery-boundary.json')['network_requests']==0
 assert sha(MASTER)==MASTER_SHA
 master=json.loads(MASTER.read_text()); assert len(master['entries'])==148
 assert master['scope_status'][0]['remaining']==852
 dump('reference-proposals.json',dict(proposals=proposals,proposal_count=3,formal_credit_added=0,
  scope_boundary=r['proposal_boundary'],formal_registry_unchanged_sha256=MASTER_SHA))
 report=dict(status='PASS_RESEARCH_EVIDENCE_ONLY',original_templates_studied=12,new_images_viewed_and_verified=48,
  historical_images_reviewed_again=4,seven_aspect_reviews=12,scoped_complete_fortification_proposals=3,
  subspace_only=6,held=3,historical_unique_local_archive_member_pairs_checked=117,exact_duplicate_matches=0,
  formal_credit_added=0,formal_registry_count=148,formal_registry_sha256=MASTER_SHA,
  cod4_original_scope_remaining=852,cod6_credit=0,java_run=False,game_run=False,network_requests=0,
  new_architecture_created=False,production_assets_modified=False,main_checklist_modified=False,prompt_items_deleted=0,
  limitations=['No target has met the 1000-reference requirement.',
   'Three defensive-building proposals are not three implemented buildings or whole battlefields.',
   'No native collision, texture, terrain, complete route or gameplay acceptance.',
   'Quarry external works remain unassembled; eleven components receive zero complete-building credit.',
   'Historical local archive/member units include held components and are not 117 credited buildings.'])
 dump('verification.json',report)
 lines=['# 第三批地下城建筑参考研究（2026-11-01）','',
  '逐例查看12份原始本地NBT的48张新图，另重看4张历史对比图；每例记录布局、比例、立面、屋顶、材质、动线、地形七方面。与117个历史本地归档/成员组合比对，无原文、旋转归一角色几何或纯占用几何完全重复；117包含待核与组件，不是已计数建筑数。','',
  '本批3例DUN03城防建筑参考提案：F01双塔哨站、F05高角塔连低厅、F09四角棚小围院。提案未加入正式台账；另6例仅作局部原则，3例待核。','',
  '正式台账原义庄/墓园范围仍148/1000，缺852；COD6仍0/1000。该148不能分发给每个地下城。本批未达到1000，不开始新建、重做或新增建筑。','',
  '[逐例观察](manual-review.json) · [3例独立提案](reference-proposals.json) · [来源](sources.json) · [去重](dedup-evidence.json) · [补剖面](detail-evidence.json) · [外接池核查](interface-audit.json) · [验证](verification.json)','',
  '| 编号 | 设计 | 研究判断 |','|---|---|---|']
 for c,v in zip(s['candidates'],r['entries']):
  label='完整城防参考提案' if v['credit_proposal'] else '仅局部原则' if v['status']=='SUBSPACE_PRINCIPLES_ONLY' else '完整性/路线待核'
  lines.append(f"| {c['id']} | [{c['member'].rsplit('/',1)[-1]}]({c['id']}-whole.png) | {label}；{v['proposed_target']} |")
 lines+=['','## 可应用的原则','']+['- '+p for p in r['principles']]
 lines+=['','## 保留的缺口','',
  'F03高低房间之间未核实连续路径，F08采石坑四侧外接石作工区未组装，F11长梯有断段。F06水池厅房不能仅凭steam名称算动力工厂；F12多翼府邸不能直接算判官殿或完整阴城。F09/F10/F11的布局确有差异，但差异本身不使三者都成为相关城防参考。','',
  '外接石作池含11种构件，其中六种terrain_matching、五种rigid；其fallback指回同一路径池，JSON内name与路径名不同，仅记录原始事实，不作运行结论。未拼装，不按11栋计数。sources.json中的pool_references是选择主模板的来源池，实际向外接口另见interface-audit.json，二者不混用。','',
  '前两批：[第一批](../research-20261101-dungeons-001/HANDOFF.md)、[第二批](../research-20261101-dungeons-002/HANDOFF.md)。原奖励、层级、捷径等接口缺口继续保留；研究完成不等于程序、任务、指南针和中文同步完成。','',
  '本批只写独立研究目录；未改程序/模型/贴图/任务/指南针/主清单，未删提示词。未运行Java、Gradle、游戏，未访问网络或重试429来源，未动存档、声音、亮度。','']
 (OUT/'HANDOFF.md').write_text('\n'.join(lines))
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 receipt=dict(date='2026-11-01',files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files],
  formal_credit_added=0,prompt_items_deleted=0,validation='Offline evidence integrity only')
 dump('RECEIPT.json',receipt)
 for row in receipt['files']: assert sha(OUT/row['path'])==row['sha256']
 print(json.dumps(dict(**report,delivery_files=len(files)),ensure_ascii=False))

if __name__=='__main__': main()
