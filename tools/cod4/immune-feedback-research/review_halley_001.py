"""Verify helper evidence without granting or changing research credit."""
from pathlib import Path
import json,hashlib,datetime
from ledger import O,R,B
p=O/'helpers/halley-immune/batch-001.json';data=json.loads(p.read_text());assert data['research_credit']==0 and data['master_credit']==0
checked=0;files=set()
for row in data['records']:
 assert row['research_credit']==row['suggested_credit']==0
 for ref in row['source_refs']:
  f=Path(ref['source_local']).resolve();assert f.is_relative_to(B)
  raw=f.read_bytes();assert hashlib.sha256(raw).hexdigest()==ref['source_sha256']
  lines=raw.decode().splitlines(keepends=True);a,z=ref['line'],ref['end_line'];assert 1<=a<=z<=len(lines)
  assert ''.join(lines[a-1:z])==ref['excerpt'],(f,a,z)
  files.add(str(f));checked+=1
out={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input':str(p.relative_to(R)),'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'evidence_ranges_checked':checked,'distinct_referenced_files':len(files),'research_credit':0,'master_credit_added':0,'master_effective_unchanged':32,'decisions':[
 {'id':data['records'][0]['id'],'use':'支持材料：level对象切换清表、5tick来源关联窗口及HP净差局限。','not_proven':'loader/mixin/provider实际激活及依赖版本未补齐；窗口不是节流，不作为完整新增链。'},
 {'id':data['records'][1]['id'],'use':'语义去重材料：并入现有DNP健康差值家族对照。','not_proven':'参数、平台、总容量变体不能产生新增credit。'},
 {'id':data['records'][2]['id'],'use':'反例材料：目标就近误归属、玩家单槽pending覆盖、全局text_display选择及格式问题。','not_proven':'未审原版advance时序，不把Blocked字符串当完整原生免疫回执。'},
 {'id':data['records'][3]['id'],'use':'身份/原因区分部分候选：主动感染物品对使用者overlay。','not_proven':'Helper及效果链未补，且非Boss拒控；普通阴阳无需追加灰字。'}], 'source_expansion':'Halley原候选缺失链继续归Halley辅研；主岗新扩展Epicfight和Wizardry本地固定源码，主账逐条全文审阅再决定计数。','limits':'只校验所交引用与主岗既有源码观察的一致性；不把80范围当80实现，不运行上游，不声称观感或加载通过。'}
(O/'HALLEY-001-REVIEW.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
