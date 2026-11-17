# -*- coding: utf-8 -*-
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty');T=ROOT/'tools/cod4/legacy-migration-acceptance/helpers/halley-migration';D=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration'
def sha(b):return hashlib.sha256(b).hexdigest()
for n,title in ((46,'1条：旧单Origin→layer、旧Powers→Apoli state及CHARACTER持久策略。'),(47,'3条：物品死亡筛选/库存复制；实体集合临时成员重载清除；旧PAL source撤销/派生能力刷新。')):
 b='batch-%03d'%n;doc=D/b;manifests=json.loads((T/b/'source-manifest.json').read_text());data=json.loads((doc/(b+'.json')).read_text());audit=json.loads((doc/'document-integrity.json').read_text());support=[]
 for m in manifests:
  for f in m['files']:
   if not f['path'].endswith(('gradle.properties','fabric.mod.json','.mixins.json')):continue
   raw=(ROOT/f['source']).read_bytes();assert sha(raw)==f['sourceSha256'];text=raw.decode()
   support.append(dict(f,repo=m['repo'],commit=m['commit'],git_tree=m['git_tree'],start=1,end=len(text.splitlines()),text=text,excerptSha256=sha(raw),url='https://github.com/'+m['repo']+'/blob/'+m['commit']+'/'+f['path'],credit=0,reason='Fixed native metadata/registration declaration; not independent implementation credit'))
 (doc/'static-wiring-support-not-credit.json').write_text(json.dumps(support,ensure_ascii=False,indent=2)+'\n')
 review={'credit':0,'manual':[{'family':r['family'],'semantic_duplicate_risk':r['semantic_duplicate_risk']} for r in data['records']],'primary_master_matches':audit['master_primary_matches'],'framework_rule':'PowerHolder/NBT/CCA source support reused across046/047: no generic holder suggestion and no per-power-ID/key credit','semantic_acceptance_requires_Kepler':True}
 (doc/'semantic-duplicate-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
 pin='\n'.join('- '+m['repo']+' commit `'+m['commit']+'`, tree `'+m['git_tree']+'`' for m in manifests)
 (doc/'HANDOFF.md').write_text('# Halley '+b+' → Kepler\n\n'+title+' 所有建议credit0、accepted=false，待Kepler最终去重审核。\n\n'+pin+'\n\n完整方法/行范围、源码SHA256/Git blob、摘录与归一哈希见本目录JSON；对应tools source-manifest和provenance保留真实Git commit/tree原始对象。文档核对0解析/哈希错误；'+str(audit['complete_methods_support_not_credit'])+'方法上下文仅为支持证据，不是信用数量。主账机械主方法匹配为空，不能取代语义审查。\n\n注意：默认分支名1.20，实际属性MC1.20.2。Origins声明Apoli2.11.11，与固定Apoli属性相同，但没有执行发布jar重现，不声称精确构建对应。旧Origin坏值不回退新列表，旧power ID未知直接skip；origins→apoli namespace alias只用于配置factory，不自动映射旧玩家TypeID。CCA CHARACTER/ALWAYS_COPY外部复制实现、PAL与原生栈codec未完整展开。\n\n047通用holder/registry全为共享支持不另计；Inventory/EntitySet/PAL为具体不同状态对象，若与046/主账重复由Kepler合并或排除。禁止按ID/字段/平台/下载/方法数凑数。\n\n仅静态参考研究，未执行上游/编译/测试/游戏/GUI，无主账/生产/待办/原存档修改。十小时最低工作量及后续范围继续保留，尚未宣称完成。\n')
cpath=D/'CONTINUATION-20261028.json';c=json.loads(cpath.read_text())
for n,count in ((46,1),(47,3)):
 b='batch-%03d'%n;c['manual_suggestions_not_accepted_credit'][b]=count
 for f in (D/b).iterdir():
  if f.is_file():c['files'][str(f.relative_to(D))]=sha(f.read_bytes())
c['at']=datetime.datetime.now(datetime.timezone.utc).isoformat();c['current']='046(1)/047(3) manual suggestions ready credit0 handoff pending.043-045 delivered. Continue remaining independent scope; ten-hour still incomplete.'
c.setdefault('reservations',{}).update({'batch-046':'apace100/origins-fabric','batch-047':'apace100/apoli'})
cpath.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
print('046/047 handoff ready;4 suggestions credit0')
