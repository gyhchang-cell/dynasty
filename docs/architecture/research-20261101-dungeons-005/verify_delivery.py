#!/usr/bin/env python3
"""Verify local research provenance, family exclusion and scoped proposal limits."""
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

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def get(n):return json.loads((OUT/n).read_text())
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

def main():
 s=get('sources.json');r=get('manual-review.json');d=get('dedup-evidence.json')
 detail=get('detail-evidence.json');a=get('interface-audit.json');family=get('variant-family-audit.json')
 assert len(s['candidates'])==len(r['entries'])==len(d['entries'])==len(detail['entries'])==len(a['entries'])==8
 assert d['historical_unique_local_archive_member_pairs']==137
 assert not d['within_batch_exact_duplicate_pairs'] and all(not e['historical_exact_matches'] for e in d['entries'])
 for archive in s['source_archives']:assert sha(Path(archive['path']))==archive['sha256']
 images=0;proposals=[]
 for c,v,de,dd,ai in zip(s['candidates'],r['entries'],d['entries'],detail['entries'],a['entries']):
  assert c['id']==v['id']==de['id']==dd['id']==ai['id']
  assert c['nbt_sha256']==v['nbt_sha256']==de['nbt_sha256']
  assert set(v['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
  assert all(len(t)>20 for t in v['observations'].values())
  assert len(v['images_actually_viewed'])==4
  assert {e['path'] for e in v['images_actually_viewed']}=={str(OUT/f) for f in c['images']+[c['id']+'-details.png']}
  for e in v['images_actually_viewed']:
   p=Path(e['path']);assert sha(p)==e['sha256']
   with Image.open(p) as im:im.verify()
   images+=1
  with ZipFile(c['source_archive']) as z:
   raw=z.read(c['member']);assert hashlib.sha256(raw).hexdigest()==c['nbt_sha256']
   nbt=read(raw);assert nbt['size']==c['size']
   for p in c['pool_references']:assert json.loads(z.read(p['member']))==p['data']
   assert {p['pool'] for p in ai['outgoing_pools']}=={p['data']['pool'] for p in c['sockets']}
   for pool in ai['outgoing_pools']:
    assert pool['pool'].startswith('trek:mobs/') and pool['status']=='FOUND_LOCAL'
    raw=z.read(pool['member']);assert hashlib.sha256(raw).hexdigest()==pool['sha256']
    assert json.loads(raw)==pool['data']
    for component in pool['component_identities_only']:
     assert component['exists_in_archive'] and not component['studied_or_credited_as_complete_building']
     assert hashlib.sha256(z.read(component['member'])).hexdigest()==component['sha256']
  assert not v['native_acceptance'] and v['formal_credit_added']==0
  if v['credit_proposal']:
   proposals.append(dict(id=c['id'],target=v['proposed_target'],size=c['size'],occupied_bounds=dd['occupied_bounds'],
    source_archive=c['source_archive'],source_archive_sha256=c['source_archive_sha256'],member=c['member'],nbt_sha256=c['nbt_sha256'],
    publisher_url=c['publisher_url'],url_access='Provenance only; no network access this batch',
    images_actually_studied=v['images_actually_viewed'],observations=v['observations'],independent_design_basis=v['independent_design_basis'],
    deduplication_evidence=de,family_exclusion_record='variant-family-audit.json' if c['id']=='F02' else None,
    status='READY_FOR_INDIVIDUAL_SCOPE_REVIEW_NOT_ACCEPTED_CREDIT',native_acceptance=False,formal_credit_added=0))
 assert images==32 and {p['id'] for p in proposals}=={'F01','F02','F04','F06','F07'}
 assert family['representative']=='F02' and family['excluded_independent_designs']==['F03']
 assert family['max_independent_family_references']==1
 assert not r['entries'][2]['credit_proposal'] and r['entries'][2]['status']=='SAME_DESIGN_FAMILY_VARIANT'
 for e in family['actual_visual_evidence']:assert sha(Path(e['path']))==e['sha256']
 assert get('discovery-boundary.json')['network_requests']==0
 assert sha(MASTER)==MASTER_SHA and len(json.loads(MASTER.read_text())['entries'])==148
 dump('reference-proposals.json',dict(proposals=proposals,proposal_count=5,dun05_urban=5,formal_credit_added=0,
  scope_boundary=r['scope_boundary'],formal_registry_unchanged_sha256=MASTER_SHA))
 helpers=[OUT.parent/'research-20261101-dungeons-001/inspect_batch.py',OUT.parent/'research-20261101-dungeons-002/inspect_details.py',
  OUT.parent/'research-20261101-dungeons-002/check_dedup.py',OUT.parent/'research-20261101-dungeons-003/audit_interfaces.py',
  ROOT/'tools/architecture/nbt_read.py',ROOT/'tools/architecture/whole_building_candidates.py',ROOT/'tools/architecture/reference_components.py',
  OUT.parent/'research-20261101-task-map/inspect_expanded_sources.py']
 report=dict(status='PASS_RESEARCH_EVIDENCE_ONLY',templates_studied=8,new_images_actually_viewed_and_verified=32,
  historical_images_reviewed_again=0,seven_aspect_reviews=8,scope_specific_proposals=5,same_family_variant_exclusions=1,
  held=1,subspace_only=1,historical_local_archive_member_pairs_checked=137,exact_geometry_matches=0,
  formal_credit_added=0,formal_registry_count=148,formal_registry_sha256=MASTER_SHA,cod4_original_scope_remaining=852,cod6_credit=0,
  network_requests=0,java_run=False,game_run=False,new_architecture_created=False,production_assets_modified=False,
  main_checklist_modified=False,prompt_items_deleted=0,helper_provenance=[dict(path=str(p),sha256=sha(p)) for p in helpers],
  limitations=['Five proposals have separate purpose/scale boundaries and are not one accepted count.',
   'Exact hash novelty is not semantic novelty; F03 excluded despite distinct hashes.',
   'NBT full-cell renderings are not author screenshots, native collision tests or Chinese-style fidelity acceptance.',
   'No current target has met 1000; historical archive/member counts include components and held units.'])
 dump('verification.json',report)
 lines=['# 第五批：住宅与同设计家族研究（2026-11-01）','',
  '实际研究8份本地NBT的32张新图，逐例记录布局、比例、立面、屋顶、材质、动线和地形。核对137个历史本地归档/成员组合，未见原文或旋转归一角色/占用完全相同；137不是有效建筑信用数。','',
  'F02云杉小屋与F03雪地小屋虽然哈希不同，仍是同一旋转/覆雪家族，只以F02提出一例。五个提案分属不同小住宅用途、规模，不合并成某范围5/1000。F05入口连接待核，F08仅厅廊附翼原则。','',
  '[逐例七方面研究](manual-review.json) · [提案及四视图证据](reference-proposals.json) · [家族排除](variant-family-audit.json) · [原始来源](sources.json) · [补剖面](detail-evidence.json) · [去重](dedup-evidence.json) · [实体池](interface-audit.json) · [验证](verification.json)','',
  '| 编号 | 原始设计 | 范围及决定 |','|---|---|---|']
 for c,v in zip(s['candidates'],r['entries']):
  lines.append(f'| {c["id"]} | [{c["member"].rsplit("/",1)[-1]}]({c["id"]}-whole.png) | {v["status"]}：{v["proposed_target"]} |')
 lines+=['','## 应用原则','']+['- '+p for p in r['principles']]
 lines+=['','正式义庄/墓园旧范围仍148/1000、缺852；COD6仍0。本批正式新增0，不开始新建筑制作，没有制作资产、任务或指南针同步完成的主张。不同范围不转借信用。',
  '', '未运行Java、Gradle、游戏或网络；未重试429来源，未修改声音、亮度、用户存档、生产代码、模型、贴图、主清单或提示词。研究图是原始NBT的本地结构渲染，不代替原生材质、碰撞、地形或玩法验收。','']
 (OUT/'HANDOFF.md').write_text('\n'.join(lines))
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 receipt=dict(date='2026-11-01',status='PASS_RESEARCH_EVIDENCE_ONLY',formal_credit_added=0,prompt_items_deleted=0,
  files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files])
 dump('RECEIPT.json',receipt)
 for e in receipt['files']:assert sha(OUT/e['path'])==e['sha256']
 print(json.dumps({k:v for k,v in report.items() if k!='helper_provenance'},ensure_ascii=False))

if __name__=='__main__':main()
