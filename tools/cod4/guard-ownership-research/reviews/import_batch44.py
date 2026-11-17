import hashlib,json,pathlib,shutil
R=pathlib.Path(__file__).resolve().parents[1];D=R.parents[2]/'docs/cod4/audit-20261022/guard-ownership-research';p=D/'helpers/coordinator-guardvillagers/batch-001.json';d=json.loads(p.read_text());dest=R/'.work/sources/mrsterner__GuardVillagers';rows=[]
keep={0,1,2,3,5,6,7,11,12,14}
for i,x in enumerate(d['records']):
 raw=pathlib.Path(x['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==x['sourceSha256'];t=dest/x['path'];t.parent.mkdir(parents=True,exist_ok=True)
 if t.exists():assert t.read_bytes()==raw
 else:shutil.copyfile(x['source'],t)
 if i not in keep:continue
 rows.append(dict(repo=d['repo'],file='/'+pathlib.Path(x['path']).name,method=x['name'],start=x['start'],observation=x['observation'],application=x['application'],limits=x['limits']+' 协调GuardVillagers候选'+str(i)+'，独立完整阅读与语义复核；Yarn概念参考不复制。'))
(dest/'source.json').write_text(json.dumps(dict(repo=d['repo'],sha=d['commit'],provenance=str(p),pinnedSourceBytesCopiedWithoutModification=True),indent=2)+'\n')
(R/'reviews/batch44.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(D/'helper-guardvillagers-review.json').write_text(json.dumps(dict(proposals=15,fullProposedMethodsRead=15,accepted=10,supportOnly={'4':'射箭原版流程与已读模板合并，不独立计','8':'近战Goal攻击转发与tryAttack同链，护盾CD不单计','9':'经典OwnerHurtTarget时间戳模板，已研究同构','10':'Bow AI原版模板，仅巡逻横移差异不计','13':'友军阻挡算法完整阅读并入弩tick的同一保护链'},productionChanged=False),ensure_ascii=False,indent=2)+'\n')
