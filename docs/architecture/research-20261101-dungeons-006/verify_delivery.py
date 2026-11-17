#!/usr/bin/env python3
"""Check four studies, pool provenance and explicit scope rejections."""
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
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def get(n):return json.loads((OUT/n).read_text())
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 s=get('sources.json');r=get('manual-review.json');d=get('dedup-evidence.json');a=get('interface-audit.json');details=get('detail-evidence.json')
 assert len(s['candidates'])==len(r['entries'])==len(d['entries'])==len(a['entries'])==len(details['entries'])==4
 assert d['historical_unique_local_archive_member_pairs']==145
 assert not d['within_batch_exact_duplicate_pairs']
 for archive in s['source_archives']:assert sha(Path(archive['path']))==archive['sha256']
 for c,v,de,ai,dd in zip(s['candidates'],r['entries'],d['entries'],a['entries'],details['entries']):
  assert c['id']==v['id']==de['id']==ai['id']==dd['id']
  assert c['nbt_sha256']==v['nbt_sha256']==de['nbt_sha256'] and not de['historical_exact_matches']
  assert set(v['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
  assert all(len(t)>20 for t in v['observations'].values())
  assert v['credit_proposal']==v['formal_credit_added']==0 and not v['native_acceptance']
  assert len(v['images_actually_viewed'])==4
  assert {e['path'] for e in v['images_actually_viewed']}=={str(OUT/f) for f in c['images']+[c['id']+'-details.png']}
  for e in v['images_actually_viewed']:
   p=Path(e['path']);assert sha(p)==e['sha256']
   with Image.open(p) as im:im.verify()
  with ZipFile(c['source_archive']) as z:
   raw=z.read(c['member']);assert hashlib.sha256(raw).hexdigest()==c['nbt_sha256'] and read(raw)['size']==c['size']
   for pool in c['pool_references']:assert json.loads(z.read(pool['member']))==pool['data']
   assert {p['pool'] for p in ai['outgoing_pools']}=={p['data']['pool'] for p in c['sockets']}
   for pool in ai['outgoing_pools']:
    assert pool['pool'].startswith('trek:mobs/') and pool['status']=='FOUND_LOCAL'
    raw=z.read(pool['member']);assert hashlib.sha256(raw).hexdigest()==pool['sha256'] and json.loads(raw)==pool['data']
    for comp in pool['component_identities_only']:
     assert comp['exists_in_archive'] and not comp['studied_or_credited_as_complete_building']
     assert hashlib.sha256(z.read(comp['member'])).hexdigest()==comp['sha256']
 assert sha(MASTER)==MASTER_SHA and len(json.loads(MASTER.read_text())['entries'])==148
 ledger=OUT.parent/'research-20261101-scoped-outpost-ledger/outpost-scope-register.json'
 scopes=json.loads(ledger.read_text())['scope_status']
 assert len(scopes)==3 and all(x['accepted_references']==1 and x['remaining']==999 for x in scopes)
 assert get('discovery-boundary.json')['network_requests']==0
 report=dict(status='PASS_RESEARCH_AND_SCOPE_REJECTION_EVIDENCE',templates_studied=4,new_images_actually_viewed_and_verified=16,
  seven_aspect_reviews=4,proposals=0,formal_credit_added=0,historical_archive_member_pairs_checked=145,
  existing_scopes=[dict(id=s['id'],accepted=1,remaining=999) for s in scopes],scoped_register_sha256=sha(ledger),
  legacy_registry_unchanged_sha256=MASTER_SHA,legacy_count=148,legacy_remaining=852,cod6=0,
  java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0,
  limitations=['Current three scopes receive no credit from these different designs.',
   'Historical archive/member screen includes components, not 145 accepted designs.',
   'No native collision, terrain, material fidelity or gameplay verification; no scope at1000.'])
 dump('verification.json',report)
 lines=['# 第六批：四份前哨资料及范围排除','',
  '实际查看4份本地NBT的16张新研究图，记录七方面观察，核查145个历史归档/成员组合。没有完全重复，不等于对当前范围有效；本批提案0、正式信用0。','',
  '[逐例观察和四视图哈希](manual-review.json) · [来源](sources.json) · [补剖](detail-evidence.json) · [去重](dedup-evidence.json) · [外接池](interface-audit.json) · [验证](verification.json)','',
  '| 编号 | 设计 | 不计入既有三个范围的理由 |','|---|---|---|']
 for c,v in zip(s['candidates'],r['entries']):lines.append(f'| {c["id"]} | [{c["member"]}]({c["id"]}-whole.png) | {v["scope_rejection"]} |')
 lines+=['','## 学习原则','']+['- '+p for p in r['principles']]
 lines+=['','[三类正式参考范围](../research-20261101-scoped-outpost-ledger/HANDOFF.md)各仍1/1000、缺999；原义庄/墓园148/1000、缺852，COD6仍0。没有为了增加数字将不同用途、规模的资料并入。','',
  '本批没有开始制作、修改生产程序/模型/贴图/任务/指南针/主清单，也没删提示词。未运行Java、Gradle、游戏或网络；未动声音、亮度、用户存档。研究图是本地NBT分类整方块投影，不是原生材质、碰撞或玩法验收。','']
 (OUT/'HANDOFF.md').write_text('\n'.join(lines))
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='RECEIPT.json')
 dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files]))
 for e in get('RECEIPT.json')['files']:assert sha(OUT/e['path'])==e['sha256']
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
