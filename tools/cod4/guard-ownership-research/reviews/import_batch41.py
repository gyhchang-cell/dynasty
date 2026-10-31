"""Import only individually re-read helper proposals; no automatic research credit."""
import hashlib,json,pathlib,shutil
R=pathlib.Path(__file__).resolve().parents[1];D=R.parents[2]/'docs/cod4/audit-20261022/guard-ownership-research'
p=D/'helpers/coordinator-minecolonies/batch-001.json';d=json.loads(p.read_text());dest=R/'.work/sources/ldtteam__minecolonies'
rows=[];support=[]
# Read all25 full methods and annotation sets. Exclude thin parent reset, shared scan skeleton,
# pure distance arithmetic, and scalar threat mutation; their context remains support only.
reasons={16:'接收侧求援薄转发并入batch002.callForHelp完整链，降支持不计。',1:'导航重置薄扩展，合并到TargetAI.resetTarget支持，不再独立计。',10:'与TargetAI.searchNearbyTarget同一完整扫描骨架，仅支援配额计数，降支持不计。',18:'纯距离平方比较辅助，不以数学封装凑守卫实现。',24:'标量威胁相加/钳制与时间戳更新，作为ThreatTable失效链支持，不独立计。'}
for i,x in enumerate(d['records']):
 src=pathlib.Path(x['source']);raw=src.read_bytes();assert hashlib.sha256(raw).hexdigest()==x['sourceSha256']
 target=dest/x['path'];target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert target.read_bytes()==raw
 else:shutil.copyfile(src,target)
 if i in reasons:support.append(dict(proposal=i,source=x['url'],reason=reasons[i],accepted=False));continue
 rows.append(dict(repo=d['repo'],file='/'+pathlib.Path(x['path']).name,method=x['name'],observation=x['observation'],application=x['application'],limits=x['limits']+' 协调候选batch-001第'+str(i)+'条，接收方已逐条读完整方法及语义；非哈希脚本自动计数。'))
(dest/'source.json').write_text(json.dumps(dict(repo=d['repo'],sha=d['commit'],provenance=str(p),pinnedSourceBytesCopiedWithoutModification=True),indent=2)+'\n')
(R/'reviews/batch41.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(D/'helper-batch001-review.json').write_text(json.dumps(dict(proposals=25,fullMethodsRead=25,acceptedProposals=20,supportOnly=support,excludedOtherRepositoryOverlap=False,helperProposal=str(p),productionChanged=False),ensure_ascii=False,indent=2)+'\n')
