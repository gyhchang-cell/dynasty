#!/usr/bin/env python3
"""Validate the local research delivery, never a native architecture acceptance."""
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
MASTER = ROOT / 'docs/architecture/continuation-20261022/references/full-buildings.json'
MASTER_SHA = '9901cbff65cb11f32b9b6c56e62a727113c8978192f174061ed8491348b4e408'
sys.path.insert(0, str(ROOT / 'tools/architecture'))
from nbt_read import read


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
 s = json.loads((OUT / 'sources.json').read_text())
 r = json.loads((OUT / 'manual-review.json').read_text())
 d = json.loads((OUT / 'dedup-evidence.json').read_text())
 detail = json.loads((OUT / 'detail-evidence.json').read_text())
 discovery = json.loads((OUT / 'discovery-boundary.json').read_text())
 assert len(s['candidates']) == len(r['entries']) == len(d['entries']) == len(detail['entries']) == 16
 assert len({c['member'] for c in s['candidates']}) == 16
 assert not d['within_batch_exact_duplicate_pairs']
 assert all(not c['historical_exact_matches'] for c in d['entries'])
 for archive in s['source_archives']: assert sha(Path(archive['path'])) == archive['sha256']
 image_count = 0; proposal_rows = []
 for c, v, dd in zip(s['candidates'], r['entries'], detail['entries']):
  assert c['id'] == v['id'] == dd['id']
  assert c['nbt_sha256'] == v['nbt_sha256']
  assert set(v['observations']) == {'layout', 'proportion', 'facade', 'roof', 'materials', 'circulation', 'terrain'}
  assert len(v['images_actually_viewed']) == 4
  for evidence in v['images_actually_viewed']:
   path = Path(evidence['path']); assert sha(path) == evidence['sha256']
   with Image.open(path) as image: image.verify()
   image_count += 1
  with ZipFile(c['source_archive']) as archive:
   raw = archive.read(c['member']); assert hashlib.sha256(raw).hexdigest() == c['nbt_sha256']
   nbt = read(raw); assert nbt['size'] == c['size']
   for pool in c['pool_references']: assert json.loads(archive.read(pool['member'])) == pool['data']
  assert v['formal_credit_added'] == 0
  if v['credit_proposal']:
   proposal_rows.append(dict(id=v['id'], target='DUN03 defensive-building references only',
    complete_building_identity=c['member'],
    verifiable_source=dict(local_archive=c['source_archive'], archive_sha256=c['source_archive_sha256'],
     member=c['member'], nbt_sha256=c['nbt_sha256'], publisher_url=c['publisher_url'],
     publisher_url_access='Source provenance only; no current network request.'),
    evidence_actually_viewed=v['images_actually_viewed'],
    deduplication_basis=dict(manual=v['independent_design_basis'], computed_evidence='dedup-evidence.json#' + v['id']),
    observations=v['observations'], status='PROPOSED_SCOPED_REFERENCE_NOT_FORMAL_CREDIT',
    native_acceptance=False, formal_credit_added=0))
 for evidence in r['historical_comparison_views']:
  assert sha(Path(evidence['path'])) == evidence['sha256']
 assert image_count == 64 and len(proposal_rows) == 9
 assert len(r['historical_comparison_views']) == 8
 assert discovery['network_requests'] == 0
 assert sha(MASTER) == MASTER_SHA
 master = json.loads(MASTER.read_text()); assert len(master['entries']) == 148
 assert master['scope_status'][0]['remaining'] == 852
 dump(OUT / 'reference-proposals.json', dict(date='2026-11-01', proposals=proposal_rows,
  proposal_count=9, formal_credit_added=0, formal_registry_unchanged_sha256=MASTER_SHA,
  scope_warning='Do not append to COD4 mortuary 148 or COD6 0; no scope has met 1000. No permission to start new architecture.'))
 report = dict(status='PASS_RESEARCH_EVIDENCE_ONLY', original_templates_studied=16,
  new_images_viewed_and_verified=64, historical_images_reviewed_again=8,
  seven_aspect_reviews=16, whole_defensive_building_proposals=9,
  subspace_only=3, entrance_or_relevance_held=4,
  historical_unique_local_archive_member_pairs_checked=d['historical_unique_local_archive_member_pairs'],
  exact_duplicate_matches=0, formal_credit_added=0, formal_registry_count=148,
  formal_registry_sha256=sha(MASTER), cod4_original_scope_remaining=852, cod6_credit=0,
  java_run=False, game_run=False, new_architecture_created=False,
  production_assets_modified=False, main_checklist_modified=False, prompt_items_deleted=0,
  network_requests=0, limitations=[
   'Reference proposals are target-scoped and separate from formal credit.',
   'Stored-block approximations do not certify native texture, collision, generated terrain or playthrough.',
   'F10 lacks close relevance; F12/F13/F14 have entrance/route gaps; F09/F11/F15 are limited subspace studies.',
   'A whole defensive building is one reference, not a finished DUN03 battlefield.'])
 dump(OUT / 'verification.json', report)
 lines = ['# 第二批地下城建筑参考研究（2026-11-01）', '',
  '实际查看16份本地原始NBT的64张新研究图，并重看8张历史图作设计家族比较。逐例记录布局、比例、立面、屋顶、材质、动线、地形7方面观察；对101个历史本地归档/成员组合进行旋转归一、材质无关及纯占用去重。无完全重复；相似度只作辅助，不能代替人工判断。', '',
  '本批可提交9例DUN03城防建筑参考：F01–F08、F16。它们是完整院堡、塔堡或主堡的不同设计，用于城防分区与路径组织研究；不是已建成的9座新建筑，也不是9座完整战场。F09/F11/F15仅限局部空间研究；F10相关性不足，F12/F13/F14的入口或路线仍待核。', '',
  '正式台账保持148/1000（原义庄、墓园范围缺852）；COD6保持0/1000。9例提案未加入148，没有将旧范围信用转给十地下城。未达到1000，不开始制作新建筑。', '',
  '[逐例观察](manual-review.json) · [9例独立参考提案](reference-proposals.json) · [原始来源](sources.json) · [偏轴/高层剖面](detail-evidence.json) · [去重证据](dedup-evidence.json) · [验证](verification.json)', '',
  '| 编号 | 设计 | 用途判断 | 关键空间证据 |', '|---|---|---|---|']
 for c, v in zip(s['candidates'], r['entries']):
  label = 'DUN03城防参考提案' if v['credit_proposal'] else '仅局部研究' if v['completeness_and_relevance'] == 'WHOLE_LAYOUT_SUBSPACE_STUDY_ONLY' else '待核或不相关'
  lines.append(f"| {c['id']} | [{c['member'].rsplit('/', 1)[-1]}]({c['id']}-whole.png) | {label} | {v['observations']['layout']} |")
 lines += ['', '## 已形成的可借鉴原则', ''] + ['- ' + p for p in r['principles']]
 lines += ['', '## 未完成范围', '',
  '1000门槛尚未达到。除正式台账原范围外，十地下城需各自核对相关性及去重；单层水厅、道场小阁或地下房网不能替代完整水宫、三岛与城池。F12需锁定外入场点和迷宫各层回程，F13需锁定金字塔外入口与下腔回路，F14需区分机关通路与熔岩危险。F15细塔没有连续长梯，不宣称已可登顶。', '',
  '前批9处奖励/层级/捷径接口约束仍见[前批接口记录](../research-20261101-dungeons-001/architectural-interface-constraints.json)。枉死城支池排水不等于完整干河底返殿后捷径；没有删除此未验收要求。', '',
  '本批仅写独立研究目录。未改程序、模型、贴图、任务、指南针或主清单；未运行Java/游戏，未重试429来源，未动存档、声音、亮度。没有把研究记录当作游戏内完成验收。', '']
 (OUT / 'HANDOFF.md').write_text('\n'.join(lines))
 files = sorted(p for p in OUT.iterdir() if p.is_file() and p.name != 'RECEIPT.json')
 receipt = dict(date='2026-11-01', files=[dict(path=p.name, bytes=p.stat().st_size, sha256=sha(p)) for p in files],
  formal_credit_added=0, prompt_items_deleted=0, validation='Offline research evidence only')
 dump(OUT / 'RECEIPT.json', receipt)
 for row in receipt['files']: assert sha(OUT / row['path']) == row['sha256']
 print(json.dumps(dict(**report, delivery_files=len(files)), ensure_ascii=False))


if __name__ == '__main__': main()
