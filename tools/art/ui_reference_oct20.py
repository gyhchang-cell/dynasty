"""Read 100 distinct official mod GUI implementations; keep URLs and layout evidence."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,re,hashlib
OUT=Path(__file__).resolve().parents[2]/'docs/ui-fixes-20261020/references'
OUT.mkdir(parents=True,exist_ok=True)
REPOS=['P3pp3rF1y/SophisticatedBackpacks','P3pp3rF1y/SophisticatedCore',
 'BluSunrize/ImmersiveEngineering','slimeknights/TinkersConstruct',
 'mekanism/Mekanism','AppliedEnergistics/Applied-Energistics-2','Vazkii/Botania',
 'CoFH/ThermalExpansion','Azanor/thaumcraft-beta','Creators-of-Create/Create',
 'Iron431/irons-spells-n-spellbooks','TeamTwilight/twilightforest',
 'Darkhax-Minecraft/EnchDesc','squeek502/AppleSkin','xaero96/XaeroPlus']
def get(url):return subprocess.check_output(['curl','-fsSL','--max-time','40',url],stderr=subprocess.DEVNULL)
def tree(repo):
 try:
  d=json.loads(get('https://api.github.com/repos/'+repo));branch=d['default_branch']
  t=json.loads(get('https://api.github.com/repos/'+repo+'/git/trees/'+branch+'?recursive=1'))
  return [(repo,branch,x['path']) for x in t.get('tree',[]) if re.search(r'(Screen|Gui)\w*\.java$',x['path'].rsplit('/',1)[-1]) and '/client/' in x['path'] and not re.search(r'Util|Init|Loading|Title|Credits|Mixin|Renderer|Accessor',x['path'].rsplit('/',1)[-1])]
 except Exception:return []
with ThreadPoolExecutor(max_workers=5) as e:groups=list(e.map(tree,REPOS))
# Round-robin keeps the sample varied instead of taking one large project's first 100.
selected=[]
for i in range(max(map(len,groups),default=0)):
 for group in groups:
  if i<len(group):selected.append(group[i])
def read(row):
 repo,branch,path=row;url=f'https://raw.githubusercontent.com/{repo}/{branch}/{path}'
 try:s=get(url).decode()
 except Exception:return None
 if len(s)<600 or not re.search(r'extends\s+\w*(Screen|Gui)|void\s+(render|draw|init)',s):return None
 key=hashlib.sha256(url.encode()).hexdigest()[:12];(OUT/(key+'.java')).write_text(s)
 return {'repo':repo,'url':f'https://github.com/{repo}/blob/{branch}/{path}','source':key+'.java',
   'layout_evidence':[line.strip() for line in s.splitlines() if re.search(r'Button|\.bounds\(|\.blit\(|imageWidth|imageHeight|drawString\(|renderTooltip\(|addRenderable|GuiSlot|renderBg|background|addTab|new .*Gui',line)][:12],
   'sha256':hashlib.sha256(s.encode()).hexdigest()}
rows=[]
with ThreadPoolExecutor(max_workers=7) as e:
 for row in e.map(read,selected[:250]):
  if row:rows.append(row)
  if len(rows)>=100:break
(OUT/'manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print('Read',len(rows),'GUI implementations from',len({r['repo'] for r in rows}),'official repositories',flush=True)
