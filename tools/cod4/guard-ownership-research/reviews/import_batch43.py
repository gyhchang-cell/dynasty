import hashlib,json,pathlib,shutil
R=pathlib.Path(__file__).resolve().parents[1];D=R.parents[2]/'docs/cod4/audit-20261022/guard-ownership-research';p=D/'helpers/coordinator-minecolonies/batch-002.json';d=json.loads(p.read_text());dest=R/'.work/sources/ldtteam__minecolonies';rows=[]
for i,x in enumerate(d['records']):
 raw=pathlib.Path(x['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==x['sourceSha256'];t=dest/x['path'];t.parent.mkdir(parents=True,exist_ok=True)
 if t.exists():assert t.read_bytes()==raw
 else:shutil.copyfile(x['source'],t)
 if i==4:continue
 rows.append(dict(repo=d['repo'],file='/'+pathlib.Path(x['path']).name,method=x['name'],observation=x['observation'],application=x['application'],limits=x['limits']+' 协调候选batch-002第'+str(i)+'条，已独立全文复核及主账去重。'))
(R/'reviews/batch43.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
q=R/'reviews/batch41.json';old=json.loads(q.read_text());old=[x for x in old if not(x['file']=='/AbstractEntityAIGuard.java' and x['method']=='startHelpCitizen')];q.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
(D/'helper-batch002-review.json').write_text(json.dumps(dict(proposals=8,fullMethodsRead=8,acceptedProposals=7,supportOnly=[dict(proposal=4,reason='performMoveAway求援转发并入callForHelp完整路径，避免多节点膨胀')],reclassifiedBatch001=[dict(proposal=16,reason='startHelpCitizen接收侧薄转发并入callForHelp完整路径，移除此前1信用')],combinedAcceptedFrom33=27,productionChanged=False),ensure_ascii=False,indent=2)+'\n')
