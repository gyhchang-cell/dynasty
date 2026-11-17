# -*- coding: utf-8 -*-
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty');T=ROOT/'tools/cod4/legacy-migration-acceptance/helpers/halley-migration';D=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration'
def sha(x):return hashlib.sha256(x).hexdigest()
for n in (43,44,45):
 b='batch-%03d'%n;base=T/b;doc=D/b
 manifest=json.loads((base/'source-manifest.json').read_text())[0];rawsupport=[]
 for f in manifest['files']:
  if not (f['path'].endswith(('gradle.properties','.mixins.json','mods.toml','fabric.mod.json','/api/IBleeding.java'))):continue
  raw=(ROOT/f['source']).read_bytes();text=raw.decode();assert sha(raw)==f['sourceSha256']
  rawsupport.append(dict(f,repo=manifest['repo'],commit=manifest['commit'],git_tree=manifest['git_tree'],start=1,end=len(text.splitlines()),text=text,excerptSha256=sha(raw),url='https://github.com/'+manifest['repo']+'/blob/'+manifest['commit']+'/'+f['path'],credit=0,reason='Static wiring/version/interface only; never independent implementation credit'))
 (doc/'static-wiring-support-not-credit.json').write_text(json.dumps(rawsupport,ensure_ascii=False,indent=2)+'\n')
 data=json.loads((doc/(b+'.json')).read_text());rows=data['records'];audit=json.loads((doc/'document-integrity.json').read_text())
 risks=[dict(family=r['family'],credit=0,status=r['status'],observation=r['observation'],semantic_duplicate_risk=r['semantic_duplicate_risk']) for r in rows+data.get('excluded_records',[])]
 (doc/'semantic-duplicate-review.json').write_text(json.dumps({'credit':0,'primary_master_matches':audit['master_primary_matches'],'manual_review':risks,'mechanical_match_absence_is_not_semantic_acceptance':True},ensure_ascii=False,indent=2)+'\n')
 titles={43:'3条待审建议：一次领取历史的选择性重生复制；温度与口渴合并持久读取；温控机库存/燃料与空间缓存恢复。',44:'1条待审建议：按维度存放的季节时钟SavedData读取、范围修正与作物玩法消费。',45:'0条建议、1条完整排除链：NBT仅客户端同步，CombatTrackerClone为内存伤害归因快照，未找到持久回读/玩家Clone接线。'}
 (doc/'HANDOFF.md').write_text('# Halley '+b+' → Kepler\n\n'+titles[n]+' 所有条目credit0、accepted=false，仅由Kepler最终核实去重计数。\n\n官方仓库 '+manifest['repo']+'；固定commit `'+manifest['commit']+'`，Git root tree `'+manifest['git_tree']+'`。`source-manifest.json`在同名tools目录，所有取出的源码blob均与真实Git对象核验；完整方法、行范围、源码/摘录/归一哈希和具体语义在本目录JSON。已只读比较主账主方法指纹，未发现机械匹配不代表语义独立。\n\n文档完整性核对：'+str(audit['complete_methods_support_not_credit'])+'个方法上下文仅为支持证据，'+str(audit['evidence_files'])+'个证据文件；解析/哈希错误0。没有把方法或下载文件数当信用。'+(' WaterPurifier已阅读全文但普通炉式计时/库存重复家族风险尚未排除，本批不提交为新增建议。' if n==43 else '')+'\n\n限制：这是静态研究，未执行上游代码、编译、测试、游戏、服务器或图形操作，未动主账/生产/待办/原存档。下一轮仍继续真实研究；十小时最低工作量尚未宣称完成。\n')
p=D/'CONTINUATION-20261028.json';c=json.loads(p.read_text())
for b in ('batch-041','batch-042'):
 if b not in c['delivered_to_Kepler']:c['delivered_to_Kepler'].append(b)
for n,count in ((43,3),(44,1),(45,0)):
 b='batch-%03d'%n;c['manual_suggestions_not_accepted_credit'][b]=count
 for f in (D/b).iterdir():
  if f.is_file():c['files'][str(f.relative_to(D))]=sha(f.read_bytes())
c.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),current='041/042 delivered;043(3 suggestions)/044(1 suggestion)/045(0 suggestions,1 excluded) source-pinned and handoff ready credit0. Bare Git clones read objects only; API limit bypassed without upstream execution. All remaining scope and10h minimum retained; not complete.')
c['reservations']={b:json.loads((T/b/'source-manifest.json').read_text())[0]['repo'] for b in ('batch-043','batch-044','batch-045')}
p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
print('Handoff documents ready; no main ledger edits')
