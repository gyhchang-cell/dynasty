"""Count actual mods in remote mrpack indices using bounded HTTP zip ranges."""
exec(open('tools/menu-20261022/study_modpacks.py').read().split('hits=get(')[0])
import io,struct,zipfile,urllib.request
class RemoteZip(io.RawIOBase):
 def __init__(self,url,size):self.url=url;self.size=size;self.pos=0
 def seekable(self):return True
 def seek(self,off,whence=0):
  self.pos=off if whence==0 else self.pos+off if whence==1 else self.size+off
  return self.pos
 def tell(self):return self.pos
 def read(self,n=-1):
  n=min(self.size-self.pos,n if n>=0 else self.size-self.pos)
  if n<=0:return b''
  b=subprocess.check_output(['curl','-fsSL','--max-time','35','--max-filesize','2000000','--range',f'{self.pos}-{self.pos+n-1}',self.url+f'?dynastyRange={self.pos}-{n}'],stderr=subprocess.DEVNULL)
  if len(b)>n:raise RuntimeError('Oversized range')
  self.pos+=len(b);return b

def verify(d):
 if not d:return None
 p=OUT/(d['id']+'-manifest.json')
 try:
  if p.exists():v=json.loads(p.read_text())
  else:
   ver=get('version/'+d['versions'][-1])
   f=next(f for f in ver['files'] if f['filename'].endswith('.mrpack'))
   with zipfile.ZipFile(RemoteZip(f['url'],f['size'])) as z:idx=json.loads(z.read('modrinth.index.json'))
   mods=[e['path'] for e in idx['files'] if e['path'].startswith('mods/') and e['path'].endswith('.jar')]
   v={'version_id':ver['id'],'download_url':f['url'],'mod_count':len(mods),'mods':mods,'index_sha256':hashlib.sha256(json.dumps(idx,sort_keys=True).encode()).hexdigest()}
   p.write_text(json.dumps(v,ensure_ascii=False,indent=2))
  return d,v
 except Exception as e:
  print('Skip',d['title'],str(e)[:100],flush=True);return None

qualified=[];seen=set()
for offset in range(0,800,100):
 hits=get('search?'+urllib.parse.urlencode({'limit':100,'offset':offset,'index':'downloads','facets':'[["project_type:modpack"],["categories:adventure","categories:technology","categories:magic","categories:quests"]]'}))['hits']
 def project(h):
  p=OUT/(h['project_id']+'.json')
  try:
   d=json.loads(p.read_text()) if p.exists() else get('project/'+h['project_id']);p.write_text(json.dumps(d,ensure_ascii=False,indent=2));return d
  except Exception:return None
 with ThreadPoolExecutor(max_workers=8) as pool:ds=list(pool.map(project,hits))
 with ThreadPoolExecutor(max_workers=8) as pool:
  for result in pool.map(verify,ds):
   if not result:continue
   d,v=result
   if v['mod_count']<100:continue
   if re.search(r'optim|shader|fps|lunar|hypixel',d['title'],re.I):continue
   family=re.sub(r'\b(forge|fabric|neoforge|quilt|bmc\d|mmc\d|\d+(?:\.\d+)+)\b','',d['title'].lower());family=re.sub(r'[^a-z0-9]','',family)
   if family in seen:continue
   seen.add(family)
   body=d['body'];lines=[re.sub(r'\s+',' ',x).strip(' #*|>-') for x in body.splitlines() if re.search(r'menu|interface|quest|progression|custom|boss|rpg|adventure|explor|immers|theme|factory',x,re.I) and 35<len(x)<800 and not x.startswith('![')]
   if not lines:continue
   qualified.append({'project_id':d['id'],'title':d['title'],'url':'https://modrinth.com/modpack/'+d['slug'],'downloads':d['downloads'],'mod_count':v['mod_count'],'version_id':v['version_id'],'evidence':lines[:4],'gallery':d['gallery'],'source_sha256':hashlib.sha256(body.encode()).hexdigest(),'scope':'Primary author documentation and real modpack index inspected. Menu images or in-game behavior not assumed from this evidence.'})
   print('LARGE',len(qualified),d['title'],v['mod_count'],flush=True)
   if len(qualified)>=100:break
 (OUT/'large-pack-study.json').write_text(json.dumps(qualified,ensure_ascii=False,indent=2))
 if len(qualified)>=100:break
print('VERIFIED LARGE PACKS',len(qualified),flush=True)
