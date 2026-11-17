import hashlib,json,pathlib,shutil
R=pathlib.Path(__file__).resolve().parents[1];D=R.parents[2]/'docs/cod4/audit-20261022/guard-ownership-research';p=D/'helpers/halley-recruits/batch-001.json';rs=json.loads(p.read_text());dest=R/'.work/sources/talhanation__recruits';rows=[];drop={22:'守位距离平方模板并入23资格完整链，几何常量不计',24:'追击距离与CD模板，实际伤害坐骑重选并入26/事件链',28:'弓弹道/损耗原版模板且坐骑替换已见26，不单计',29:'与GuardVillagers村民信誉选玩家完整模板同构，仅阈值不同不计'}
for i,x in enumerate(rs):
 raw=pathlib.Path(x['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==x['sourceSha256'];t=dest/x['path'];t.parent.mkdir(parents=True,exist_ok=True)
 if t.exists():assert t.read_bytes()==raw
 else:shutil.copyfile(x['source'],t)
 if i in drop:continue
 rows.append(dict(repo=x['repo'],file='/'+pathlib.Path(x['path']).name,method=x['name'],start=x['start'],observation=x['observation'],application=x['application'],limits=x['limits']+' Halley候选'+str(i)+'完整方法已独立阅读，按语义边界去重。'))
(dest/'source.json').write_text(json.dumps(dict(repo=rs[0]['repo'],sha=rs[0]['commit'],provenance=str(p),pinnedSourceBytesCopiedWithoutModification=True),indent=2)+'\n')
(R/'reviews/batch47.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(D/'helper-recruits-review.json').write_text(json.dumps(dict(proposals=30,fullProposedMethodsRead=30,accepted=26,supportOnly=drop,productionChanged=False,sourceCRLF='原始文件保留CRLF，摘录比较时规范换行'),ensure_ascii=False,indent=2)+'\n')
