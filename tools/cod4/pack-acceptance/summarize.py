"""Evidence-only checks. Never infer success from process exit or screenshots' existence."""
from pathlib import Path
import json,sys,hashlib
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/pack-acceptance'/sys.argv[1]
def load(p):return json.loads(p.read_text())
report={'run':str(O),'checks':[],'issues':[],'boundaries':['One automated native production client plus its integrated server; not human two-player multiplayer.','QA-provided inventory in a fresh flat survival world, not progression or survival acquisition.','Selected HUD situations at recorded window/GUI scale, not every camera-mod configuration.']}
def check(ok,label,detail=None):
 report['checks'].append({'passed':bool(ok),'check':label,'detail':detail})
 if not ok:report['issues'].append(label)
m=load(O/'manifest.json');mods=load(O/'loaded-mods.json');ids={x['id'] for x in mods}
check((O/'READY.json').exists(),'Actual private client entered a new world with JEI runtime')
for mod in ['dynasty','jei','curios','ftbquests','ftblibrary','ftbteams','noisium','embeddium','armorpointspp','overflowingbars','appleskin','shouldersurfing']:
 check(mod in ids,'Complete pack keeps '+mod+' loaded')
for lang in ['zh_cn','en_us']:
 auditpath=O/(lang+'-talismans-audit.json')
 if not auditpath.exists():continue
 audit=load(auditpath)
 check(len(audit)==7,lang+' has actual JEI lookups for all seven original talismans')
 for id,a in audit.items():
  check(len(a['description'])>=3 and bool(a['recipeIds']),lang+' '+id+' resolves source, use, single-use and craft recipe')
  for mode in ['input','output','info']:
   p=O/(lang+'-'+id+'-'+mode+'-result.json')
   if not p.exists():continue
   s=load(p);screen=s.get('jeiScreen',{});layouts=screen.get('layouts',[])
   check(s['screen']=='mezz.jei.gui.recipes.RecipesGui' and len(layouts)>0,lang+' '+id+' '+mode+' actually rendered native JEI layouts')
   if mode=='info':check(screen.get('category')=='jei:information' and any(x.get('description') for x in layouts),lang+' '+id+' information shown')
   if mode=='output':check(any(x.get('recipe') in a['recipeIds'] for x in layouts),lang+' '+id+' craft navigation selects matching native recipe')
  p=O/(lang+'-'+id+'-escape-result.json')
  if p.exists():check(load(p)['screen']=='net.minecraft.client.gui.screens.inventory.InventoryScreen',lang+' '+id+' Escape returns to original inventory')
for p in sorted(O.glob('bow-*-frames.json')):
 name=p.name.removesuffix('-frames.json');frames=load(p);positive='negative' not in name
 using=[x for x in frames if x.get('using')];active=[x for x in using if x.get('draw')];server=[x for x in frames if x.get('server',{}).get('using')]
 check(bool(using) and bool(server),name+' uses native client and server active item',{'clientFrames':len(using),'serverFrames':len(server)})
 if not positive:
  check(not active and all(x.get('goldPixels',0)==0 and x.get('bluePixels',0)==0 for x in frames),name+' never shows Dynasty charge HUD');continue
 check(bool(active),name+' native bow draw is exposed')
 if not active:continue
 required=active[0]['draw']['required'];before=[x for x in active if x['draw']['ticks']==required-1];at=[x for x in active if x['draw']['ticks']==required]
 check(bool(before) and any(x['bluePixels']>0 and x['goldPixels']==0 for x in before),name+' actual HUD blue at threshold - 1',required-1)
 check(bool(at) and any(x['goldPixels']>0 and x['bluePixels']==0 for x in at),name+' actual HUD gold at threshold',required)
 canceled=[x for x in frames if x['age']>=57]
 check(bool(canceled) and all(not x.get('draw') and x['bluePixels']==0 and x['goldPixels']==0 for x in canceled),name+' HUD disappears after release')
 if 'gui-covered' in name:
  hidden=[x for x in frames if x['screen']!='none'];check(bool(hidden) and all(x['bluePixels']==0 and x['goldPixels']==0 for x in hidden),name+' GUI hides charge HUD')
 if 'hide-gui' in name:
  hidden=[x for x in frames if x['hideGui']];check(bool(hidden) and all(x['bluePixels']==0 and x['goldPixels']==0 for x in hidden),name+' F1-equivalent option hides charge HUD')
 if 'swap' in name:
  empty=[x for x in frames if x['main']=='minecraft:air'];check(bool(empty) and all(not x.get('draw') and x['bluePixels']==0 and x['goldPixels']==0 for x in empty),name+' changing selected hand item cancels charge HUD')
report['native_mod_count']=len(mods);report['snapshot_jar_count']=m['total_mod_jars'];report['checked']=len(report['checks']);report['passed']=sum(x['passed'] for x in report['checks']);report['screenshots']=len(list(O.glob('*.png')))
(O/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['checks']},ensure_ascii=False,indent=2))
