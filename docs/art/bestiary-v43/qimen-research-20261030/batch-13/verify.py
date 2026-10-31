from pathlib import Path
import json,hashlib,re,zipfile
B=Path(__file__).resolve().parent;R=B.parent;m=json.loads((B/'native-consumers.json').read_text());v=json.loads((B/'post-hurt-pose-review.json').read_text());checks=[]
def ck(name,value):checks.append(dict(check=name,passed=bool(value)));assert value,name
sources={s['id']:s for s in v['sources']}
for s in sources.values():
 p=B/s['local'];ck(s['id']+' hash',hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256']);n=len(p.read_bytes().splitlines())
 for a,b in s['reviewed_ranges']:ck(s['id']+f' read range {a}-{b}',1<=a<=b<=n)
for e in v['evidence']:
 ck(e['id']+' zero credit',e['credit_added']==0)
 for ref in e['sources']:
  ck(e['id']+' source '+ref['source'],ref['source'] in sources)
  for a,b in ref['ranges']:ck(e['id']+f' inside actual read {ref["source"]} {a}-{b}',any(c<=a<=b<=d for c,d in sources[ref['source']]['reviewed_ranges']))
ck('mapping hash',hashlib.sha256(Path(m['mapping_cache']).read_bytes()).hexdigest()==m['mapping_sha256'])
with zipfile.ZipFile(m['base_source_cache']) as z:
 for f in m['files']:
  raw=z.read(f['path']);data='\n'.join(raw.decode().splitlines())+'\n';ck(f['id']+' exact entry',hashlib.sha256(raw).hexdigest()==f['base_entry_sha256']);ck(f['id']+' SRG reconstruction',data==(B/f['srg']).read_text());ck(f['id']+' mapped view',re.sub(r'\b[mf]_\d+_\b',lambda x:f['symbols'].get(x[0],x[0]),data)==(B/f['reading_view']).read_text());ck(f['id']+' not Fabric merged',f['variant']=='VANILLA_MCP_BEFORE_FORGE_NOT_FABRIC_MERGED')
a=json.loads((R/'batch-02/dual-swords-acquisition.json').read_text());prior={str((Path.cwd()/x['local']).resolve()):x for x in a if 'local' in x}
for s in v['sources']:
 if s.get('repo'):
  row=prior[str((B/s['local']).resolve())];ck(s['id']+' original fixed source',row['sha256']==s['sha256'] and row['git_tree_match'] and row['commit']==s['version'])
fp=(B/sources['ItemInHandRenderer']['local']).read_text().splitlines();calls=[n for n in range(357,500) if 'this.applyItemArmTransform(' in fp[n-1]];ck('source call locations',calls==[377,403,418,423,426,429,453,479,490]);ck('source slice ordinal 2/4', [n for n in calls if n>416][2]==426 and [n for n in calls if n>416][4]==453)
ck('no claims of production/running',v['production_changed'] is False and v['java_game_started'] is False);ck('same family zero new accepted',v['new_source_families']==0 and v['new_accepted_gate_credit']==0)
(B/'local-verification.json').write_text(json.dumps(dict(status='PASS',checks=len(checks),scope='固定来源、基线重建、阅读范围包含关系及源代码调用点；不认证Fabric Mixin字节码应用或运行行为',results=checks),ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks))
