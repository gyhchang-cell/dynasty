"""Read-only import from fixed local cache, verify Git blobs, never grant research credit."""
from pathlib import Path
import json,hashlib,re,sys
from ledger import B,R,O
repo,pattern=sys.argv[1:3];src=R/(sys.argv[3] if len(sys.argv)>3 else 'build/item-use-references')/repo.replace('/','__');src=Path(sys.argv[4]) if len(sys.argv)>4 else src;dst=B/'sources'/repo.replace('/','__');dst.mkdir(exist_ok=True)
prior=json.loads((src/'source.json').read_text());rev=prior['sha'];tree_path=src/'tree.json'
if not tree_path.exists():tree_path=dst/'tree.json'
tree=json.loads(tree_path.read_text());assert tree['sha']==rev and not tree.get('truncated');by={x['path']:x for x in tree['tree']}
if (dst/'source.json').exists():
 meta=json.loads((dst/'source.json').read_text());assert meta['commit']==rev
else:meta={'repo':repo,'commit':rev,'acquisition':'fixed local cached source; verified against pinned Git tree','research_credit':0,'files':[]}
saved={x['path']:x for x in meta['files']};n=0
for p in src.rglob('*'):
 if p.is_file() and p.suffix in ('.java','.json','.gradle','.properties'):
  rel=p.relative_to(src).as_posix()
  if rel not in by or not re.search(pattern,rel):continue
  data=p.read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==by[rel]['sha'];data.decode('utf8')
  out=dst/rel;out.parent.mkdir(parents=True,exist_ok=True)
  if out.exists():assert out.read_bytes()==data
  else:out.write_bytes(data)
  saved[rel]={'path':rel,'sha256':hashlib.sha256(data).hexdigest(),'git_blob_sha1':by[rel]['sha']};n+=1
(dst/'tree.json').write_bytes(tree_path.read_bytes());meta['files']=list(saved.values());(dst/'source.json').write_text(json.dumps(meta,indent=2)+'\n')
p=O/'sources.json';all=json.loads(p.read_text());all=[x for x in all if x['repo']!=repo]+[meta];p.write_text(json.dumps(all,indent=2)+'\n');print(json.dumps({'repo':repo,'commit':rev,'local_verified':n,'credit':0}))
