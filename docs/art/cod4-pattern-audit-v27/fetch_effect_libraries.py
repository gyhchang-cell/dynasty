"""Download pinned public VFX source for study, never install dependencies/assets."""
from pathlib import Path
import urllib.request,json,re,concurrent.futures,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2]
def get(url):
 return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Dynasty-pinned-effect-study'}),timeout=35).read()
def one(repo):
 root=R/'build/item-use-references'/repo.replace('/','__');root.mkdir(parents=True,exist_ok=True)
 if (root/'source.json').exists():meta=json.loads((root/'source.json').read_text())
 else:
  info=json.loads(get('https://api.github.com/repos/'+repo));branch=info['default_branch'];commit=json.loads(get(f'https://api.github.com/repos/{repo}/commits/{branch}'))['sha'];meta={'repo':repo,'sha':commit,'branch':branch,'purpose':'PRIMARY_SOURCE_RESEARCH_ONLY'};(root/'source.json').write_text(json.dumps(meta,indent=2)+'\n')
 revision=meta['sha'];tree=json.loads(get(f'https://api.github.com/repos/{repo}/git/trees/{revision}?recursive=1'));assert not tree.get('truncated');(root/'tree.json').write_text(json.dumps(tree))
 paths=[x['path'] for x in tree['tree'] if x['type']=='blob' and x['path'].endswith('.java') and re.search(r'/(client|particle|particles|render|renderer|fx|vfx|visual_effects)/',x['path'],re.I) and not re.search(r'/(gui|screen|configurator|editor|widget|mixin|test|compat)/',x['path'],re.I)]
 def source(path):
  target=root/path
  if target.exists():data=target.read_bytes()
  else:data=get(f'https://raw.githubusercontent.com/{repo}/{revision}/{path}');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  return {'path':path,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:files=list(pool.map(source,paths))
 return {'repo':repo,'revision':revision,'count':len(files),'status':'DOWNLOADED_NOT_REVIEWED','files':files}
if __name__ == '__main__':
 import argparse
 parser=argparse.ArgumentParser()
 parser.add_argument('repos',nargs='*',default=['Low-Drag-MC/Photon','LodestarMC/Lodestone'])
 parser.add_argument('--output',default='effect-library-fetch.json')
 args=parser.parse_args();records=[]
 for repo in args.repos:
  try:row=one(repo);records.append(row);print(repo,row['revision'],row['count'],flush=True)
  except Exception as e:records.append({'repo':repo,'error':str(e)});print(repo,str(e),flush=True)
  (D/args.output).write_text(json.dumps(records,indent=2)+'\n')
