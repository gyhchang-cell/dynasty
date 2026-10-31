from pathlib import Path
import json,subprocess,hashlib,datetime
B=Path(__file__).resolve().parent;R=B.parent;tree={x['path']:x for x in json.loads((R/'batch-03/grapplemod-fixed-tree.json').read_text())['tree']};repo='yyon/grapplemod';commit='40080155cf1160b3ef4c6db9d47d01746925f9f1'
paths=['src/main/resources/assets/grapplemod/models/item/'+n+'.json' for n in ['grapplinghook','hook','rope']]+['src/main/resources/assets/grapplemod/textures/'+n for n in ['item/grapplinghook.png','item/hook.png','item/entity_hook.png','item/rope.png','entity/entity_hook.png','entity/rope.png']]
rows=[]
for p in paths:
 if p not in tree: print('not in fixed tree',p);continue
 out=B/'reference-assets'/p;out.parent.mkdir(parents=True,exist_ok=True);url=f'https://raw.githubusercontent.com/{repo}/{commit}/{p}'
 z=subprocess.run(['/usr/bin/curl','--fail','--silent','--show-error','--location','--max-time','30',url,'-o',str(out)],capture_output=True,text=True);x=dict(repo=repo,commit=commit,path=p,url=url,local=str(out.relative_to(B)),exit_code=z.returncode,stderr=z.stderr,status='ACQUIRED_NOT_REVIEWED',expected_blob=tree[p]['sha'],new_reference_credit=0)
 if z.returncode==0:
  data=out.read_bytes();x.update(sha256=hashlib.sha256(data).hexdigest(),git_blob_sha1=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest(),bytes=len(data));x['git_tree_match']=x['git_blob_sha1']==x['expected_blob'];assert x['git_tree_match']
 rows.append(x);print(p,x['status'],z.returncode)
 if z.returncode:break
(B/'asset-acquisition.json').write_text(json.dumps(dict(saved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,new_source_families=0,new_accepted_credit=0),ensure_ascii=False,indent=2)+'\n')
