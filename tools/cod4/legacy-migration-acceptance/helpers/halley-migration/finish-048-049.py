# -*- coding: utf-8 -*-
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty');T=Path(__file__).resolve().parent;D=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration'
sha=lambda x:hashlib.sha256(x).hexdigest()
for n,parent in ((48,'046/047'),(49,'047')):
 b='batch-%03d'%n;doc=D/b;data=json.loads((doc/(b+'.json')).read_text());audit=json.loads((doc/'document-integrity.json').read_text());m=json.loads((T/b/'source-manifest.json').read_text())[0];r=data['support_records'][0]
 (doc/'reviewed-suggestions.jsonl').write_text('')
 (doc/'semantic-duplicate-review.json').write_text(json.dumps({'credit':0,'new_suggestions':0,'support_only':True,'supports_batches':parent,'semantic_duplicate_risk':r['semantic_duplicate_risk'],'master_mechanical_matches_not_semantic_acceptance':audit['master_primary_matches'],'prohibition':'Do not turn dependency methods, keys, strategy names or API wrappers into new implementation credits.'},ensure_ascii=False,indent=2)+'\n')
 (doc/'HANDOFF.md').write_text('# Halley '+b+' → Kepler（依赖补证，新增建议0）\n\n补充'+parent+'，records为空，support_records含一条完整支持链。credit0、accepted=false，不进入主账新信用。\n\n'+m['repo']+' commit `'+m['commit']+'`，tree `'+m['git_tree']+'`。真实commit/tree/blob对象及源码SHA256见tools对应目录；完整方法及字段lambda行范围、全文和摘录/归一hash见'+b+'.json。文档核对0解析/哈希错误。方法数只描述证据规模。\n\n'+r['observation']+'\n\n适用：'+r['application']+'\n\n限制：'+r['limits']+'\n\n重复风险：'+r['semantic_duplicate_risk']+'\n\n仅静态源码/证据文档；未执行上游、编译、测试、游戏、GUI；不碰主账、生产、待办、原存档。十小时实际工作量尚未宣称完成，继续独立来源研究。\n')
p=D/'CONTINUATION-20261028.json';c=json.loads(p.read_text());c['at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
for n in (48,49):
 b='batch-%03d'%n;c['manual_suggestions_not_accepted_credit'][b]=0
 for f in (D/b).iterdir():
  if f.is_file():c['files'][str(f.relative_to(D))]=sha(f.read_bytes())
 c.setdefault('reservations',{})[b]=json.loads((T/b/'source-manifest.json').read_text())[0]['repo']+' dependency support only'
c['current']='048 CCA5.3/049 PAL1.9 dependency support complete, 0 new suggestions, credit0; handoff pending. Continue new LevelZ reservation/source evaluation; ten-hour minimum not yet complete.'
p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
print('048/049 handoff documents ready;0 new suggestions')
