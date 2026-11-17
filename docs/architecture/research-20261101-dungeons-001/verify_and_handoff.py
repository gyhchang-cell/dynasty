#!/usr/bin/env python3
"""Check delivered evidence, record conservative dedup, and write local handoff."""
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
REF=ROOT/'docs/architecture/continuation-20261022/references'
JAVA=ROOT/'src/main/java/com/dynasty/dungeon'
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from reference_components import geometry_hash,role
from whole_building_candidates import AIR

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def check_anchor(a):
 lines=Path(a['file']).read_text().splitlines()
 assert all(lines[r['line']-1]==r['text'] for r in a['exact_lines']),a['file']
 if 'sha256' in a:assert sha(Path(a['file']))==a['sha256']

def main():
 sources=json.loads((OUT/'sources.json').read_text())
 reviews=json.loads((OUT/'manual-review.json').read_text())
 interface=json.loads((OUT/'architectural-interface-constraints.json').read_text())
 assert len(sources['candidates'])==len(reviews['entries'])==12
 assert len(interface['canonical_dungeons'])==10 and len(interface['conflicts'])==9
 for a in sources['source_archives']:assert sha(Path(a['path']))==a['sha256']
 historical=[]
 for p in sorted(REF.glob('whole-candidates*/candidates.json')):
  d=json.loads(p.read_text())
  historical.extend(dict(index=str(p),id=c['id'],member=c['member'],nbt=c.get('nbt_sha256'),geometry=c.get('material_independent_geometry_sha256')) for c in d['candidates'])
 master=json.loads((REF/'full-buildings.json').read_text())
 for c in master['entries']:
  v=c.get('verifiable_source',{});b=c.get('deduplication_basis',{})
  historical.append(dict(index=str(REF/'full-buildings.json'),id=c['id'],member=c.get('complete_building_identity'),nbt=v.get('nbt_sha256'),geometry=b.get('material_independent_rotation_normalized_geometry_sha256')))
 hashes=[];by_geometry=defaultdict(list)
 for c,r in zip(sources['candidates'],reviews['entries']):
  assert c['id']==r['id'] and c['nbt_sha256']==r['nbt_sha256']
  assert set(r['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
  assert len(r['images_actually_viewed'])==3
  for p in r['images_actually_viewed']:
   image_path=Path(p['path']);assert sha(image_path)==p['sha256']
   with Image.open(image_path) as im:im.verify()
  with ZipFile(c['source_archive']) as z:raw=z.read(c['member'])
  assert hashlib.sha256(raw).hexdigest()==c['nbt_sha256']
  nbt=read(raw);pal=nbt.get('palette') or nbt['palettes'][0]
  cells={tuple(b['pos']):pal[b['state']]['Name'] for b in nbt['blocks'] if pal[b['state']]['Name'] not in AIR}
  g=geometry_hash({p:role(n) for p,n in cells.items()},nbt['size'])
  occupancy=geometry_hash({p:1 for p in cells},nbt['size'])
  matches=[h for h in historical if h['member']==c['member'] or h['nbt']==c['nbt_sha256'] or h['geometry']==g]
  by_geometry[g].append(c['id'])
  hashes.append(dict(id=c['id'],member=c['member'],material_independent_rotation_normalized_geometry_sha256=g,
   pure_occupancy_rotation_normalized_sha256=occupancy,historical_exact_matches=matches,
   caveat='No exact stored hash/name match does not prove a new design family; manual review and target relevance remain required.'))
 dump(OUT/'dedup-evidence.json',dict(entries=hashes,within_batch_exact_duplicates=[v for v in by_geometry.values() if len(v)>1],
  historical_records_checked=len(historical),historical_index_unit='74 historical candidate records plus 148 formal entries; overlap is intentional, not 222 different buildings',
  manual_family_observations=[dict(id=r['id'],basis=r['independent_design_basis']) for r in reviews['entries']],formal_credit_added=0))
 anchors=0
 for d in interface['canonical_dungeons']:
  for a in d['source_anchors']:check_anchor(a);anchors+=1
 for c in interface['conflicts']:
  for a in c['source_anchors']:check_anchor(a);anchors+=1
 for b in interface['existing_source_bindings']:
  for a in b['source_anchors']:check_anchor(a);anchors+=1
 assert all(c['unchanged_from_task_map'] for c in interface['source_prompt_checks'])
 official_sha=sha(REF/'full-buildings.json')
 assert official_sha=='9901cbff65cb11f32b9b6c56e62a727113c8978192f174061ed8491348b4e408'
 assert len(master['entries'])==148
 report=dict(date='2026-11-01',status='PASS_WITH_EXPLICIT_SCOPE_LIMITS',templates_studied=12,images_verified=36,
  seven_aspect_reviews=12,strong_whole_fortification_candidates=4,tower_subspace_only=5,excluded_or_held=3,
  exact_historical_matches=sum(bool(x['historical_exact_matches']) for x in hashes),
  within_batch_exact_duplicate_groups=[v for v in by_geometry.values() if len(v)>1],
  current_source_anchor_ranges_verified=anchors,conflicts_constrained_but_not_implemented=9,dungeon_topology_constraints=10,
  actual_runtime_structure_source_bindings=2,formal_registry_count=148,formal_registry_sha256=official_sha,formal_credit_added=0,
  native_game_validation=False,java_run=False,new_build_created=False,prompt_items_deleted=0,
  unresolved=['1000相关完整建筑门槛未达；本批不能直接加到既有义庄148例。','4城防候选尚需目标登记和设计家族最终核准；5塔仅局部层级参考。','9项矛盾已给建筑约束，程序、任务、唯一奖励和指南针实际绑定仍由协调落实。','枉死城支池除水不等于原文完整干河底永久通路；Boss入口仍UNBOUND_RIVER_DOCK。'])
 dump(OUT/'verification.json',report)
 md=['# 地下城建筑研究与空间接口交接（2026-11-01）','',
 '本批实际研究12份固定本地原始NBT，逐张查看36张整体、平面及纵剖图，逐例写明7方面观察。全部为离线方块占用近似，未启动Java或游戏。',
 '', '完整城防布局强候选4例（F01/F02/F07/F08），完整单塔但仅对应子空间5例（F03/F05/F09/F11/F12），排除或待核3例（F04/F06/F10）。F02是完整遗址布局候选，不是完整有顶住宅；F10内部建筑与连通性仍不充分。',
 '', '正式台账仍148/1000，原范围缺852；COD6仍0/1000。十地下城不得继承义庄148例。本批正式新增0；强候选未自动分摊到10个目标。原先15份聚落模板也没有变成15个信用。',
 '', '## 实际研究证据','',
 '[逐例7方面观察](manual-review.json) · [原始来源与NBT校验](sources.json) · [去重依据](dedup-evidence.json) · [验证结果](verification.json)',
 '', '| 编号 | 原始设计 | 判断 | 可借鉴内容 |','|---|---|---|---|']
 for c,r in zip(sources['candidates'],reviews['entries']):
  md.append(f"| {c['id']} | [{c['member'].rsplit('/',1)[-1]}]({c['id']}-whole.png) | {r['completeness_and_relevance']} | {r['observations']['layout']} |")
 md+=['','## 9处矛盾的建筑约束','', '以下均是既有来源约束；未新增蓝图、实际ID、奖励代码或任务数据。每条精确原文与生产源码片段见[接口约束](architectural-interface-constraints.json)。','',
  '| 矛盾 | 精确原文位置 | 唯一入口、层级、永久捷径约束 |','|---|---|---|']
 for c in interface['conflicts']:
  links='；'.join(f"[{Path(a['file']).name}:{a['start_line']}](<{a['file']}:{a['start_line']}>)" for a in c['source_anchors'])
  md.append('| '+c['id']+' '+c['topic']+' | '+links+' | '+' '.join(c['architectural_constraints'])+' |')
 md+=['','## 已有源码可复用的两处空间锚点','',
 '沉沙玄宫：`dynasty:chensha_xuangong`，主世界；GenerationStub为origin+(32,72,4)，origin地面基准=采样最高地形−72。72/48/24/0为入口/神道/九玄室/底层地板标高。底层return_lift在+(41,1,8)，目标+(41,73,8)。GenerationStub是结构锚点，不能未经净空核查当传送落脚点。',
 '', '枉死城：`dynasty:yinsi_wangsi_cheng`，`dynasty:underworld`；GenerationStub为origin+(48,41,3)，origin=采样最高地形−40。已有坡道下降至街巷，内衙/屋顶另有标高。`wangsi_sump_drained`只清理x14..16/y6..8/z94..99封闭支池，不能冒称排干主河并贯通殿后；Boss仍为`UNBOUND_RIVER_DOCK`，secret与onceLoot定义为空。',
 '', '准确生产路径（只读核对）：']
 for name in ['DungeonDefinition.java','ChenshaStructure.java','ChenshaPiece.java','WangsiStructure.java','WangsiPiece.java','WangsiArchitecture.java','WangsiSluice.java']:
  md.append(f'- [{name}](<{JAVA/name}>)')
 md+=['','## 协调接入约束','',
 '十座的规范入口地点、层级、秘密支路、永久捷径及准确原文路径均列于architectural-interface-constraints.json。除上述两座，其他8座本批未核实真实ID和落地坐标，明确留空。',
 '', '任务和指南针显示原文中文建筑名，以实际维度、结构ID、实例键关联规范入场点。屋顶出入口、秘密房和返程捷径仍属于同一实例。发现建筑、到层、开捷径、完成战区、领取奖励分别记录；入口抵达不等于通关。',
 '', '未满1000不做新建筑。程序、掉落、任务、中文指南针由协调接入，本批不宣称已实现或已验收。只改本独立研究目录，未删任何主清单项、未改正式参考台账、未重试429来源、未操作存档或声音亮度。','']
 (OUT/'HANDOFF.md').write_text('\n'.join(md))
 # A delivery manifest includes every file except itself; verify hashes on handoff.
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 dump(OUT/'RECEIPT.json',dict(date='2026-11-01',files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files],
  formal_credit_added=0,prompt_items_deleted=0,validation='offline source and evidence verification only'))
 print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
