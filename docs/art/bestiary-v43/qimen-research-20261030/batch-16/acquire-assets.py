from pathlib import Path
import json,subprocess,hashlib,datetime,concurrent.futures
B=Path(__file__).resolve().parent;R=B.parent;tree=json.loads((R/'BluSunrize__ImmersiveEngineering-fixed-tree.json').read_text());commit='e63e4824800945eccf3684200a2c2270e2e1cdf2'
paths=['src/main/resources/assets/immersiveengineering/models/item/chemthrower.obj.ie','src/main/resources/assets/immersiveengineering/models/item/chemthrower.mtl','src/main/resources/assets/immersiveengineering/textures/item/chemthrower.png']
def fetch(p):
 e=next(x for x in tree['tree'] if x['path']==p);out=B/'reference-assets'/p;out.parent.mkdir(parents=True,exist_ok=True);url='https://raw.githubusercontent.com/BluSunrize/ImmersiveEngineering/'+commit+'/'+p;r=subprocess.run(['/usr/bin/curl','--fail','--silent','--show-error','--location','--max-time','30',url,'-o',str(out)],capture_output=True,text=True);row=dict(repo='BluSunrize/ImmersiveEngineering',commit=commit,path=p,url=url,local=str(out.relative_to(B)),exit_code=r.returncode,stderr=r.stderr,expected_blob=e['sha'],status='FETCH_FAILED_NOT_REVIEWED',new_reference_credit=0)
 if r.returncode==0:
  d=out.read_bytes();row.update(sha256=hashlib.sha256(d).hexdigest(),git_blob_sha1=hashlib.sha1(b'blob '+str(len(d)).encode()+b'\0'+d).hexdigest(),bytes=len(d));row['git_tree_match']=row['expected_blob']==row['git_blob_sha1'];assert row['git_tree_match'];row['status']='ACQUIRED_NOT_YET_REVIEWED'
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(fetch,paths))
(B/'asset-acquisition.json').write_text(json.dumps(dict(saved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,production_copy=False,new_source_families=0,new_accepted_credit=0),ensure_ascii=False,indent=2)+'\n');print([{k:v for k,v in r.items() if k in ['path','status','exit_code','bytes','stderr','git_tree_match']} for r in rows])
