from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request,urllib.parse,json,re,hashlib,subprocess
O=Path('docs/ui-fixes-20261020/references/mod-projects');O.mkdir(exist_ok=True)
def get(path):
 return json.loads(subprocess.check_output(['curl','-fsSL','--max-time','35','-A','DynastyUIReference/1.0','https://api.modrinth.com/v2/'+path],stderr=subprocess.DEVNULL))
def search(q):
 try:return get('search?'+urllib.parse.urlencode({'query':q,'limit':100,'index':'downloads','facets':'[["project_type:mod"]]'}))['hits']
 except Exception as e:print(q,str(e),flush=True);return []
queries=['backpack','storage','crafting','terminal','bag','machine','furnace','workbench','magic']
with ThreadPoolExecutor(max_workers=3) as e:groups=list(e.map(search,queries))
ids=list(dict.fromkeys(x['project_id'] for g in groups for x in g));print('Candidates',len(ids),flush=True)
projects=[]
for i in range(0,len(ids),75):
 try:projects.extend(get('projects?ids='+urllib.parse.quote(json.dumps(ids[i:i+75]))))
 except Exception as e:print(str(e),flush=True)
rows=[]
for d in projects:
 text=d.get('body','');title=d['title'];slug=d['slug'];desc=d.get('description','')
 # Only actual container, crafting, bag or handheld equipment interfaces; exclude cosmetics/HUD-only tools.
 if not re.search(r'backpack|storage|crafting|satchel|pouch|container|terminal|spellbook|machine|furnace|workbench|magic',desc+' '+title,re.I):continue
 lines=[re.sub(r'\s+',' ',s).strip(' #*_-') for s in text.splitlines() if re.search(r'\bGUI\b|user interface|inventory screen|crafting screen|storage screen|container screen|open.{0,35}(?:inventory|menu|screen|backpack)|right.click.{0,45}(?:inventory|menu|screen|backpack)|search bar|slot.{0,30}(?:inventory|GUI)|(?:\bGUI\b|界面|インベントリ)',s,re.I) and len(s)<2000]
 if not lines:continue
 row={'project_id':d['id'],'title':title,'url':'https://modrinth.com/mod/'+slug,'source_url':d.get('source_url'),'description':desc,'evidence':[x[:220] for x in lines[:3]],'gallery':d.get('gallery',[]),'documentation_sha256':hashlib.sha256(text.encode()).hexdigest()}
 (O/(d['id']+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2))
 rows.append(row)
rows.sort(key=lambda r: next((i for i,x in enumerate(ids) if x==r['project_id']),9999))
(O/'candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print('Qualified',len(rows),flush=True)
for i,r in enumerate(rows[:125]):print(i+1,r['title'],'|',r['evidence'][0][:170],flush=True)
