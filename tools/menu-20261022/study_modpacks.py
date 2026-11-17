"""Review primary project documentation, distinguishing documentation from visual UI evidence."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,urllib.parse,hashlib,re
OUT=Path('docs/menu-20261022/references')
def get(path):
 return json.loads(subprocess.check_output(['curl','-fsSL','--retry','2','--max-time','40','-A','DynastyMenuStudy/1.0','https://api.modrinth.com/v2/'+path],stderr=subprocess.DEVNULL))
hits=get('search?'+urllib.parse.urlencode({'limit':100,'offset':0,'index':'downloads','facets':'[["project_type:modpack"],["categories:adventure","categories:technology","categories:magic","categories:quests"]]'}))['hits']
hits+=get('search?'+urllib.parse.urlencode({'limit':100,'offset':100,'index':'downloads','facets':'[["project_type:modpack"],["categories:adventure","categories:technology","categories:magic","categories:quests"]]'}))['hits']
def fetch(h):
 p=OUT/(h['project_id']+'.json')
 try:
  d=json.loads(p.read_text()) if p.exists() else get('project/'+h['project_id'])
  p.write_text(json.dumps(d,ensure_ascii=False,indent=2));return d
 except Exception:return None
with ThreadPoolExecutor(max_workers=5) as pool:projects=list(pool.map(fetch,hits))
rows=[];seen=set()
for d in projects:
 if not d:continue
 body=d.get('body','');plain=re.sub('<[^>]+>',' ',body);plain=re.sub(r'!\[[^]]*\]\([^)]*\)','',plain)
 # Deduplicate project identity; exclude performance-only and shader-only packs.
 family=re.sub(r'\b(forge|fabric|neoforge|quilt|\d+(?:\.\d+)+)\b','',d['title'].lower());family=re.sub(r'[^a-z0-9]','',family)
 if family in seen:continue
 if not re.search(r'quest|boss|dungeon|magic|technology|rpg|adventure|explor|progression|factory|automation',plain+' '+d.get('description',''),re.I):continue
 lines=[re.sub(r'\s+',' ',s).strip(' #*|>-') for s in plain.splitlines() if re.search(r'menu|interface|quest|progression|custom|boss|rpg|mod[s ]|immers|theme',s,re.I) and 30<len(s)<1000]
 if not lines:continue
 seen.add(family)
 observations=[]
 for pattern,note in [(r'quest','任务与进度作为内容入口依据；基础操作提示不应挤占物品信息。'),(r'custom|hand.?craft','明确强调定制内容；王朝入口沿用自己的标识与色彩。'),(r'rpg|boss|dungeon','冒险主题可用主视觉建立氛围，创建世界仍保持熟悉的选项。'),(r'factory|automation|technology','复杂内容需要清晰层级；主要操作与设置分组。'),(r'immers|theme','主题一致性延伸到二级页面；避免主菜单与泥土背景割裂。')]:
  if re.search(pattern,plain,re.I):observations.append(note)
 rows.append({'project_id':d['id'],'title':d['title'],'url':'https://modrinth.com/modpack/'+d['slug'],'downloads':d['downloads'],'categories':d['categories'],'description':d['description'],'evidence':lines[:4],'observations':observations,'documentation_sha256':hashlib.sha256(body.encode()).hexdigest(),'gallery':d.get('gallery',[]),'scope':'作者项目说明阅读；不等同于启动实测或逐个菜单视觉验收；下载量不是质量保证。'})
 if len(rows)==100:break
(OUT/'study.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print('Reviewed distinct pack documentation:',len(rows))
for i,r in enumerate(rows):print(i+1,r['title'],'|',r['evidence'][0][:180])
