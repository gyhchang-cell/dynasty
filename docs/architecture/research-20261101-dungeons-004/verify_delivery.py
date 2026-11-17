#!/usr/bin/env python3
"""Check evidence provenance and boundaries; no native or formal acceptance."""
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
 detail=get('detail-evidence.json');a=get('interface-audit.json')
 assert len(s['candidates'])==len(r['entries'])==len(d['entries'])==len(detail['entries'])==len(a['entries'])==8
 assert not d['within_batch_exact_duplicate_pairs']
 assert d['historical_unique_local_archive_member_pairs']==129
 assert all(not e['historical_exact_matches'] for e in d['entries'])
 for archive in s['source_archives']:assert sha(Path(archive['path']))==archive['sha256']
 images=0;proposals=[]
 for c,v,de,dd,ai in zip(s['candidates'],r['entries'],d['entries'],detail['entries'],a['entries']):
  assert c['id']==v['id']==de['id']==dd['id']==ai['id']
  assert c['nbt_sha256']==v['nbt_sha256']==de['nbt_sha256']
  assert set(v['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
  assert all(len(text)>20 for text in v['observations'].values())
  assert len(v['images_actually_viewed'])==4
  assert {e['path'] for e in v['images_actually_viewed']}=={str(OUT/f) for f in c['images']+[c['id']+'-details.png']}
  for e in v['images_actually_viewed']:
   p=Path(e['path']);assert sha(p)==e['sha256']
   with Image.open(p) as im:im.verify()
   images+=1
  with ZipFile(c['source_archive']) as z:
   raw=z.read(c['member']);assert hashlib.sha256(raw).hexdigest()==c['nbt_sha256']
   nbt=read(raw);assert nbt['size']==c['size']
   for incoming in c['pool_references']:assert json.loads(z.read(incoming['member']))==incoming['data']
   assert {p['pool'] for p in ai['outgoing_pools']}=={p['data']['pool'] for p in c['sockets']}
   assert all(':terrain' in p['pool'] for p in ai['outgoing_pools'])
   for pool in ai['outgoing_pools']:
    assert pool['status']=='FOUND_LOCAL'
    raw=z.read(pool['member']);assert hashlib.sha256(raw).hexdigest()==pool['sha256']
    assert json.loads(raw)==pool['data']
    for component in pool['component_identities_only']:
     assert component['exists_in_archive'] and not component['studied_or_credited_as_complete_building']
     assert hashlib.sha256(z.read(component['member'])).hexdigest()==component['sha256']
  assert not v['native_acceptance'] and v['formal_credit_added']==0
  if v['credit_proposal']:
   proposals.append(dict(id=c['id'],target=v['proposed_target'],size=c['size'],
    source_archive=c['source_archive'],source_archive_sha256=c['source_archive_sha256'],
    member=c['member'],nbt_sha256=c['nbt_sha256'],publisher_url=c['publisher_url'],
    url_access='Provenance only; no current network request',
    images_actually_studied=v['images_actually_viewed'],observations=v['observations'],
    independent_design_basis=v['independent_design_basis'],deduplication_evidence=de,
    status='READY_FOR_INDIVIDUAL_SCOPE_REVIEW_NOT_ACCEPTED_CREDIT',
    native_acceptance=False,formal_credit_added=0))
 assert images==32 and {p['id'] for p in proposals}=={'F01','F02','F04','F06','F07'}
 assert len(r['historical_comparison_views'])==2
 for e in r['historical_comparison_views']:assert sha(Path(e['path']))==e['sha256']
 assert sum(e['status']=='SUBSPACE_PRINCIPLES_ONLY' for e in r['entries'])==2
 assert sum(e['status']=='HELD_COMPLETENESS_OR_ROUTE' for e in r['entries'])==1
 assert detail['entries'][1]['occupied_bounds'][1]==[0,30]
 assert get('discovery-boundary.json')['network_requests']==0
 assert sha(MASTER)==MASTER_SHA
 master=json.loads(MASTER.read_text());assert len(master['entries'])==148
 assert master['scope_status'][0]['remaining']==852
 dump('reference-proposals.json',dict(proposals=proposals,proposal_count=5,dun05_urban=4,dun03_fortified_hall=1,
  formal_credit_added=0,scope_boundary=r['scope_boundary'],formal_registry_unchanged_sha256=MASTER_SHA))
 helpers=[OUT.parent/'research-20261101-dungeons-001/inspect_batch.py',
  OUT.parent/'research-20261101-dungeons-002/inspect_details.py',
  OUT.parent/'research-20261101-dungeons-002/check_dedup.py',
  OUT.parent/'research-20261101-dungeons-003/audit_interfaces.py',
  ROOT/'tools/architecture/nbt_read.py',ROOT/'tools/architecture/whole_building_candidates.py',
  ROOT/'tools/architecture/reference_components.py',OUT.parent/'research-20261101-task-map/inspect_expanded_sources.py']
 report=dict(status='PASS_RESEARCH_EVIDENCE_ONLY',original_templates_studied=8,new_images_viewed_and_verified=32,
  historical_images_reviewed_again=2,seven_aspect_reviews=8,scope_specific_proposals=5,
  dun05_urban_proposals=4,dun03_large_fortified_hall_proposals=1,subspace_only=2,held=1,
  historical_local_archive_member_pairs_checked=129,exact_duplicate_matches=0,formal_credit_added=0,
  formal_registry_count=148,formal_registry_sha256=MASTER_SHA,cod4_original_scope_remaining=852,cod6_credit=0,
  java_run=False,game_run=False,network_requests=0,new_architecture_created=False,
  production_assets_modified=False,main_checklist_modified=False,prompt_items_deleted=0,
  helper_provenance=[dict(path=str(p),sha256=sha(p)) for p in helpers],
  limitations=['No scope has met 1000; five proposals must not be summed into one scope.',
   'Stored NBT study images are not author or native-game screenshots.',
   'No native collision, generated terrain, Chinese-style fidelity or complete gameplay acceptance.',
   'Historical local archive/member units include held components and are not credited buildings.'])
 dump('verification.json',report)
 lines=['# 第四批：街区旅店、住宅与城馆研究（2026-11-01）','',
  '实际查看8份本地原始NBT的32张新图，另重看2张历史比较图，逐例记录七方面观察。核对129个历史本地归档/成员组合的原文与旋转归一角色/占用几何，没有完全重复；129包含组件和待核资料，不是有效参考数。','',
  '整理5例范围明确的完整建筑提案：F01/F02为两种旅店组织，F04为多层T形住宅，F07为低厅带窄高室小宅，四例仅对应DUN05相应街区建筑；F06只对应DUN03大型守军城馆。不得将大小、用途不同的5例自动并入一个1000门槛。F05/F08仅局部原则，F03完整可用住房与上楼路线待核。','',
  '[逐例研究](manual-review.json) · [5例提案及原图证据](reference-proposals.json) · [原始来源](sources.json) · [补剖面](detail-evidence.json) · [去重](dedup-evidence.json) · [外接池](interface-audit.json) · [验证](verification.json)','',
  '| 编号 | 原始设计 | 判断和用途限制 |','|---|---|---|']
 for c,v in zip(s['candidates'],r['entries']):
  label='完整建筑参考提案' if v['credit_proposal'] else '仅局部原则' if v['status']=='SUBSPACE_PRINCIPLES_ONLY' else '保留待核'
  lines.append(f'| {c["id"]} | [{c["member"].rsplit("/",1)[-1]}]({c["id"]}-whole.png) | {label}：{v["proposed_target"]} |')
 lines+=['','## 可借鉴原则','']+['- '+p for p in r['principles']]
 lines+=['','## 信用与剩余要求','',
  '正式台账原义庄/墓园范围仍148/1000、缺852，COD6仍0/1000。本批正式新增0，未将148分配给十地下城。每个待制具体建筑的用途/规模仍需独立审查和达到1000，研究提案不是已制作资产，尚不开始新建、重做或新增建筑。','',
  '[前12例城防提案的逐例验收记录](../research-20261101-dungeons-acceptance/HANDOFF.md)已单列，不能将本批5例直接写成同一范围“17/1000”。','',
  '本目录只写独立研究证据，没有改生产程序、模型、贴图、任务、指南针或主清单，没有删提示词。未运行Java、Gradle、游戏或网络请求；未重试429来源，未动声音、亮度或存档。源图为本地NBT结构渲染，原生碰撞、贴图和地形仍未验收。','']
 (OUT/'HANDOFF.md').write_text('\n'.join(lines))
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 receipt=dict(date='2026-11-01',files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files],
  status='PASS_RESEARCH_EVIDENCE_ONLY',formal_credit_added=0,prompt_items_deleted=0)
 dump('RECEIPT.json',receipt)
 for item in receipt['files']:assert sha(OUT/item['path'])==item['sha256']
 print(json.dumps({k:v for k,v in report.items() if k!='helper_provenance'},ensure_ascii=False))

if __name__=='__main__':main()
