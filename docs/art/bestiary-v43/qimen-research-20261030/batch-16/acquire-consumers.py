from pathlib import Path
import json,subprocess,hashlib,concurrent.futures,datetime
B=Path(__file__).resolve().parent;R=B.parent;tree=json.loads((R/'BluSunrize__ImmersiveEngineering-fixed-tree.json').read_text());commit='e63e4824800945eccf3684200a2c2270e2e1cdf2';names=['PolygonUtils','TextureCoordinateRemapper','MaterialColorGetter','MaterialSpriteGetter','IEOBJCallback'];paths=[next(e['path'] for e in tree['tree'] if e['path'].endswith('/'+name+'.java')) for name in names]
def fetch(p):
 e=next(x for x in tree['tree'] if x['path']==p);out=B/'sources/BluSunrize__ImmersiveEngineering'/p;out.parent.mkdir(parents=True,exist_ok=True);url='https://raw.githubusercontent.com/BluSunrize/ImmersiveEngineering/'+commit+'/'+p;r=subprocess.run(['/usr/bin/curl','--fail','--silent','--show-error','--location','--max-time','30',url,'-o',str(out)],capture_output=True,text=True);row=dict(repo='BluSunrize/ImmersiveEngineering',commit=commit,path=p,url=url,local=str(out.relative_to(B)),exit_code=r.returncode,stderr=r.stderr,expected_blob=e['sha'],new_reference_credit=0,status='FETCH_FAILED_NOT_REVIEWED')
 if r.returncode==0:
  d=out.read_bytes();row.update(sha256=hashlib.sha256(d).hexdigest(),git_blob_sha1=hashlib.sha1(b'blob '+str(len(d)).encode()+b'\0'+d).hexdigest(),lines=len(d.splitlines()));row['git_tree_match']=row['expected_blob']==row['git_blob_sha1'];assert row['git_tree_match'];row['status']='ACQUIRED_NOT_REVIEWED'
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(fetch,paths))
(B/'consumer-acquisition.json').write_text(json.dumps(dict(saved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,new_source_families=0,new_accepted_credit=0),ensure_ascii=False,indent=2)+'\n');print([{k:v for k,v in row.items() if k in ['path','exit_code','lines','stderr','git_tree_match']} for row in rows])
