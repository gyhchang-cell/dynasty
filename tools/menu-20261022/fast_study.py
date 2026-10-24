exec(open('tools/menu-20261022/verify_large_packs.py').read().split('qualified=[]')[0])
from concurrent.futures import as_completed
# Cache aligned ranges: a ZIP index normally needs only its tail and first block.
def cached_read(self,n=-1):
 n=min(self.size-self.pos,n if n>=0 else self.size-self.pos)
 if n<=0:return b''
 if not hasattr(self,'cache'):self.cache={}
 parts=[]
 while n:
  block=self.pos//65536*65536
  if block not in self.cache:
   end=min(block+65535,self.size-1)
   data=subprocess.check_output(['curl','-fsSL','--retry','1','--connect-timeout','8','--max-time','25','--max-filesize','2000000','--range',f'{block}-{end}',self.url+f'?studyBlock={block}'],stderr=subprocess.DEVNULL)
   if len(data)!=end-block+1:raise RuntimeError('Range length mismatch')
   self.cache[block]=data
  b=self.cache[block];a=self.pos-block;count=min(n,len(b)-a)
  if count<=0:raise RuntimeError('Empty range')
  parts.append(b[a:a+count]);self.pos+=count;n-=count
 return b''.join(parts)
RemoteZip.read=cached_read
base_get=get
version_cache={}
def get(path):
 if path.startswith('version/') and path[8:] in version_cache:return version_cache[path[8:]]
 return base_get(path)
queries=[{'limit':100,'offset':i,'index':'downloads','facets':'[["project_type:modpack"],["categories:quests","categories:technology"]]'} for i in range(0,400,100)]
with ThreadPoolExecutor(max_workers=4) as pool:groups=list(pool.map(lambda q:base_get('search?'+urllib.parse.urlencode(q))['hits'],queries))
ids=list(dict.fromkeys(h['project_id'] for g in groups for h in g))
projects=[]
for i in range(0,len(ids),50):
 ds=base_get('projects?ids='+urllib.parse.quote(json.dumps(ids[i:i+50])))
 for d in ds:(OUT/(d['id']+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2))
 projects.extend(ds)
# Include already collected popular content packs, but never count project variants twice.
for p in OUT.glob('*.json'):
 d=json.loads(p.read_text())
 if isinstance(d,dict) and 'project_type' in d and d['id'] not in ids:projects.append(d);ids.append(d['id'])
projects.sort(key=lambda d:-d['downloads'])
vids=[d['versions'][-1] for d in projects if d.get('versions')]
for i in range(0,len(vids),80):
 for v in base_get('versions?ids='+urllib.parse.quote(json.dumps(vids[i:i+80]))):version_cache[v['id']]=v
print('Primary project documents',len(projects),'version metadata',len(version_cache),flush=True)
qualified=[];seen=set()
def qualify(result):
 if not result:return
 d,v=result
 if v['mod_count']<100 or re.search(r'optim|shader|fps|lunar|hypixel',d['title'],re.I):return
 family=re.sub(r'\b(forge|fabric|neoforge|quilt|bmc\d|mmc\d|\d+(?:\.\d+)+)\b','',d['title'].lower());family=re.sub(r'[^a-z0-9]','',family)
 if family in seen:return
 lines=[re.sub(r'\s+',' ',x).strip(' #*|>-') for x in d['body'].splitlines() if re.search(r'menu|interface|quest|progression|custom|boss|rpg|adventure|explor|immers|theme|factory',x,re.I) and 35<len(x)<800 and not x.startswith('![')]
 if not lines:return
 seen.add(family);qualified.append({'project_id':d['id'],'title':d['title'],'url':'https://modrinth.com/modpack/'+d['slug'],'downloads':d['downloads'],'mod_count':v['mod_count'],'version_id':v['version_id'],'evidence':lines[:4],'gallery':d['gallery'],'source_sha256':hashlib.sha256(d['body'].encode()).hexdigest(),'scope':'Author documentation and real modpack index reviewed; not a claim of 100 in-game menu visual inspections.'})
 print('LARGE',len(qualified),d['title'],v['mod_count'],flush=True)
 (OUT/'large-pack-study.json').write_text(json.dumps(qualified,ensure_ascii=False,indent=2))
# Reuse completed reads first, then fetch remaining manifests concurrently.
remaining=[]
for d in projects:
 if (OUT/(d['id']+'-manifest.json')).exists():qualify(verify(d))
 else:remaining.append(d)
with ThreadPoolExecutor(max_workers=12) as pool:
 fs=[pool.submit(verify,d) for d in remaining]
 for f in as_completed(fs):
  qualify(f.result())
  if len(qualified)>=100:
   for future in fs:future.cancel()
   break
(OUT/'large-pack-study.json').write_text(json.dumps(qualified[:100],ensure_ascii=False,indent=2))
print('COMPLETE',len(qualified[:100]),flush=True)
