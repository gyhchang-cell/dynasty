#!/usr/bin/env python3
"""Verify source identities, observed mining fittings, covers and scope limits."""
import ast
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
MASTER=ROOT/'docs/architecture/continuation-20261022/references/full-buildings.json'
MASTER_SHA='9901cbff65cb11f32b9b6c56e62a727113c8978192f174061ed8491348b4e408'
KINDS={'furnace','blast_furnace','barrel','chest','grindstone','damaged_anvil','water_cauldron','lava_cauldron','ladder','campfire','cyan_carpet'}
def digest(raw):return hashlib.sha256(raw).hexdigest()
def sha(p):return digest(p.read_bytes())
def get(n):return json.loads((OUT/n).read_text())
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def image_check(e):
 p=Path(e['path']);assert sha(p)==e['sha256']
 with Image.open(p) as im:im.verify()
def main():
 s=get('sources.json');r=get('manual-review.json');d=get('dedup-evidence.json');a=get('interface-audit.json')
 details=get('detail-evidence.json');f=get('fittings-and-cover.json')
 assert all(len(x)==4 for x in [s['candidates'],r['entries'],d['entries'],a['entries'],details['entries'],f['entries']])
 assert d['historical_unique_local_archive_member_pairs']==157 and not d['within_batch_exact_duplicate_pairs']
 for archive in s['source_archives']:assert sha(Path(archive['path']))==archive['sha256']
 for c,v,de,ai,dd,ff in zip(s['candidates'],r['entries'],d['entries'],a['entries'],details['entries'],f['entries']):
  ident=c['id'];assert all(x['id']==ident for x in [v,de,ai,dd,ff])
  assert c['nbt_sha256']==v['nbt_sha256']==de['nbt_sha256']==ff['nbt_sha256'] and not de['historical_exact_matches']
  assert set(v['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
  assert all(len(t)>20 for t in v['observations'].values())
  assert v['credit_proposal']==int(ident=='F01') and v['formal_credit_added']==0 and not v['native_acceptance']
  assert len(v['images_actually_viewed'])==4
  assert {e['path'] for e in v['images_actually_viewed']}=={str(OUT/n) for n in c['images']+[ident+'-details.png']}
  for e in v['images_actually_viewed']:image_check(e)
  with ZipFile(c['source_archive']) as z:
   raw=z.read(c['member']);original=read(raw);palette=original.get('palette') or original['palettes'][0]
   assert digest(raw)==c['nbt_sha256'] and original['size']==c['size']
   fittings=[dict(position=b['pos'],state=palette[b['state']]) for b in original['blocks'] if palette[b['state']]['Name'].split(':')[-1] in KINDS]
   top=[dict(position=b['pos'],state=palette[b['state']]) for b in original['blocks'] if b['pos'][1]==5 and palette[b['state']]['Name'] not in {'minecraft:air','minecraft:structure_void'}]
   assert fittings==ff['original_fittings'] and top==ff['y5_nonair_states']
   for pool in c['pool_references']:assert json.loads(z.read(pool['member']))==pool['data']
   assert {p['pool'] for p in ai['outgoing_pools']}=={p['data']['pool'] for p in c['sockets']}
   for pool in ai['outgoing_pools']:
    assert pool['pool']=='minecraft:empty' and pool['status']=='NOT_IN_THIS_ARCHIVE'
    assert pool['member'] not in z.namelist()
   if ident=='F01':
    assert len(top)==92 and sum(t['state']['Name']=='minecraft:cyan_carpet' for t in fittings)==20
   if ident=='F02':
    assert len(top)==24 and all(t['state']['Name']=='minecraft:stripped_spruce_log' for t in top)
    assert {tuple(t['position']) for t in top}=={(x,5,zp) for x in range(7) for zp in range(7) if x in [0,6] or zp in [0,6]}
 assert details['entries'][3]['occupied_bounds'][1]==[0,16] and s['candidates'][3]['size'][1]==18
 assert details['entries'][3]['ladder_runs']==[dict(x=12,z=4,ys=[1,2,3,4,5])]
 assert len(r['historical_comparison_views'])==2
 for e in r['historical_comparison_views']:image_check(e)
 assert sha(MASTER)==MASTER_SHA and len(json.loads(MASTER.read_text())['entries'])==148
 ledger=OUT.parent/'research-20261101-scoped-outpost-ledger/outpost-scope-register.json'
 scopes=json.loads(ledger.read_text())['scope_status']
 assert len(scopes)==3 and all(x['accepted_references']==1 and x['remaining']==999 for x in scopes)
 assert get('discovery-boundary.json')['network_requests']==0
 proposal=dict(id='008-F01',status='PENDING_SCOPE_OWNER_ACCEPTANCE',formal_credit_added=0,
  proposed_scope=r['entries'][0]['purpose_and_scale_boundary'],source=s['candidates'][0],
  observations=r['entries'][0]['observations'],actual_views=r['entries'][0]['images_actually_viewed'],
  dedup=d['entries'][0],original_fittings_and_cover=f['entries'][0],
  independent_design_basis='Two unequal working bays under a notched flat cover, perimeter furnace/water/tool stations and full side storage row; manually compared to historical C004 enclosed shrine/front-court design.',
  limits=['One small covered support workshop only, not a giant factory or complete mining estate.',
   'F02 uncovered frame, F03 excavation and F04 geode receive no additional whole-building proposal.',
   'No native terrain, collision, transport or machine gameplay acceptance; no construction before1000 scope-valid designs.'])
 dump('reference-proposals.json',dict(entries=[proposal],formal_credit_added=0))
 report=dict(status='PASS_MINING_RESEARCH_AND_WHOLE_BUILDING_BOUNDARIES',templates_studied=4,
  new_images_actually_viewed_and_verified=16,historical_images_reviewed_again=2,seven_aspect_reviews=4,
  proposals=1,uncovered_support_space=1,excavation_or_geode_only=2,formal_credit_added=0,
  historical_archive_member_pairs_checked=157,
  existing_scopes=[dict(id=x['id'],accepted=1,remaining=999) for x in scopes],scoped_register_sha256=sha(ledger),
  legacy_registry_unchanged_sha256=MASTER_SHA,legacy_count=148,legacy_remaining=852,cod6=0,
  java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0,
  limitations=['One pending DUN02 small-support-workshop proposal, not one accepted COD6 mining complex.',
   '157 historical archive/member pairs include components; they are not157 accepted whole buildings.',
   'Local absence of minecraft:empty JSON is not runtime-failure proof.',
   'Categorical views merge absent and air positions; full-cell drawings do not certify native materials or collision.'])
 dump('verification.json',report)
 lines=['# 第八批：矿业空间与完整建筑边界','',
  '实际查看4份本地模板的16张新研究图和2张历史对照图，逐例记录七方面观察，筛查157个历史归档/成员组合。没有将组合数、图片数、炉桶数或矿石数转成建筑计数。','',
  '**1份DUN02小型覆顶维修/储料工作棚提案，正式新增0。** 裸梁操作跨、露天矿坑和晶洞附属设施各留研究记录，不作为三份完整建筑提案。','',
  '[逐例观察](manual-review.json) · [完整提案](reference-proposals.json) · [原始来源](sources.json) · [补剖和梯段](detail-evidence.json) · [历史去重](dedup-evidence.json) · [接口](interface-audit.json) · [陈设与顶层原始状态](fittings-and-cover.json) · [验证](verification.json)','',
  '| 编号 | 来源 | 用途/规模与决定 |','|---|---|---|']
 for c,v in zip(s['candidates'],r['entries']):lines.append(f'| {c["id"]} | [{c["member"]}]({c["id"]}-whole.png) | {v["purpose_and_scale_boundary"]} |')
 lines+=['','## 核实的区别','',
  '- F01仅12×6×9，尽管文件名为large；中央20格灰色投影是青色地毯，不能当大型矿石工作台。炉3、桶7及工具沿边布置。',
  '- F02顶部y5仅外周24格梁，中央5×5空白；没有F01的连续覆盖，不凭同池large/small两个NBT分别累计完整覆顶工坊。',
  '- F03主要是露天凹坑及矿石岩边；F04主要是高晶洞壳及入口器具。岩石高点、矿体、天然壳与炉具不自动构成完整房屋。',
  '- F04保存高18格、占用最高y16，侧梯只在y1..5；不宣称18格可用楼层、洞顶环廊或运输线已经连通。',
  '- F01与旧C004实际图对照：前者双工作跨敞口平覆棚，后者封闭方祭室加前院；最邻近几何分数仅筛查用途。','',
  '## 可应用原则','']+['- '+p for p in r['principles']]
 lines+=['','既有三类前哨各仍1/1000、缺999；原义庄/墓园148/1000、缺852；COD6正式参考仍0。当前没有任何范围达到1000，不开始建筑制作。','',
  '未运行Java、Gradle或游戏；没有联网请求，未操作声音、亮度或存档。未改生产程序、模型、贴图、任务、指南针或主清单，未删除提示词。所有图片是离线NBT分类整方块研究图。','']
 (OUT/'HANDOFF.md').write_text('\n'.join(lines))
 for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files]))
 for e in get('RECEIPT.json')['files']:assert (OUT/e['path']).stat().st_size==e['bytes'] and sha(OUT/e['path'])==e['sha256']
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
