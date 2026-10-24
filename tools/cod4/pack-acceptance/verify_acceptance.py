"""Reconstruct screenshot capture selection and validate actual paired render state."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/cod4/audit-20261022/pack-acceptance'
def read(p):return json.loads(p.read_text())
checks=[];pairs=[]
def check(ok,label,detail=None):checks.append(dict(passed=bool(ok),check=label,detail=detail))
for run in ['run-04','run-05']:
 p=OUT/run
 check((p/'exit-code.txt').read_text().strip()=='0',run+' normal client exit')
 for file in sorted(p.glob('bow-*-frames.json')):
  name=file.name.removesuffix('-frames.json');frames=read(file);negative='negative' in name;noammo='no-ammo' in name or 'noammo' in name
  active=[f for f in frames if f.get('using')]
  check(not active if noammo else bool(active),name+' native use expected state')
  if not noammo:check(any(f.get('server',{}).get('using') for f in frames),name+' integrated server actually using item')
  sampled=set()
  for index,f in enumerate(frames):
   d=f.get('draw');t=d['ticks'] if d else -f['age']-1
   sample=(d and t in [0,1,d['required']-1,d['required'],d['required']+4,28]) or 56<=f['age']<=58
   if not sample or t in sampled:continue
   sampled.add(t);png=p/(name+'-t'+str(t)+'.png')
   if not png.exists():continue
   pairs.append({'screenshot':str(png.relative_to(OUT)),'sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'frame_file':str(file.relative_to(OUT)),'frame_index':index,'hudSerial':f.get('hudSerial'),'state':f,'pairing':'First occurrence of captured t in native render-end sequence; image was copied in this callback, deferred PNG encoding only.'})
  if negative:
   check(all(not f.get('draw') and f['goldPixels']==f['bluePixels']==0 for f in frames),name+' no Dynasty charge HUD');continue
  # The HUD event is absent on GUI/F1 frames; use top-level same-render screen/option state there.
  visible=[f for f in frames if f['screen']=='none' and not f['hideGui'] and f.get('renderedHud',{}).get('draw')]
  required=visible[0]['renderedHud']['draw']['required']
  for t,color in [(required-1,'bluePixels'),(required,'goldPixels')]:
   matched=[f for f in visible if f['renderedHud']['draw']['ticks']==t and f['nativeUseTicks']==t]
   check(any(f[color]>0 and f['goldPixels' if color=='bluePixels' else 'bluePixels']==0 for f in matched),name+' actual rendered boundary '+str(t),{'required':required,'matching_frames':len(matched)})
  hidden=[f for f in frames if f['screen']!='none' or f['hideGui']]
  if hidden:check(all(f['goldPixels']==f['bluePixels']==0 for f in hidden),name+' actual GUI/F1 suppresses HUD',len(hidden))
  ended=[f for f in frames if f['age']>=57]
  # run04 direct setScreen deliberately retains use; it proves coverage, not native inventory cancellation.
  if name!='bow-gui-covered':check(bool(ended) and all(not f.get('draw') and f['goldPixels']==f['bluePixels']==0 for f in ended),name+' release/cancel removes HUD')
p=OUT/'run-05';nav=read(p/'native-navigation.json')
for entry in nav:
 id=entry['item']
 for mode in ['mouse','R']:
  check(any(x.get('recipe')=='dynasty:talisman_paper' for x in entry[mode]['jeiScreen']['layouts']),id+' actual '+mode+' navigates to paper recipe')
 check(any(x.get('recipe')=='dynasty:'+id for x in entry['back']['jeiScreen']['layouts']),id+' Backspace returns to original recipe')
 check(read(p/('native-'+id+'-escape-result.json'))['screen']=='net.minecraft.client.gui.screens.inventory.InventoryScreen',id+' native Escape returns to inventory')
pages=read(p/'paper-all-use-pages.json');recipes={x.get('recipe') for s in pages for x in s['jeiScreen']['layouts']}
check([s['jeiScreen']['page'] for s in pages]==[f'{n}/9' for n in range(1,10)],'actual next-page input traverses all nine paper-use pages')
for entry in nav:check('dynasty:'+entry['item'] in recipes,entry['item']+' reachable in native U paper usages')
report={'checks':checks,'passed':sum(c['passed'] for c in checks),'total':len(checks),'failures':[c for c in checks if not c['passed']], 'screenshot_pair_index':'hud-screenshot-pairs.json','scope':['Actual production full-pack private clients, 86 jar files / 96 native loaded mods, new flat QA worlds.','Survival mode with supplied QA inventory; not acquisition/progression, all-world-generation or human multiplayer acceptance.','run02 has stale-frame boundary/GUI evidence limitations and a real hot-language-cache defect. Preserve it.','run03 missed exact boundaries due PNG timing; run04 and run05 use deferred encoding and paired RenderGuiEvent.Post state.','run04 GUI injection retained use; run05 native E/Escape proves normal inventory opening cancels use.','Tianlang uses actual DragonBowItem 20-tick branch despite old fixture filename rapid. No mechanism changed.','Native keyboard/mouse handler automation is not a human player. Tested HUD coexistence at GUI scale3 only.']}
(OUT/'hud-screenshot-pairs.json').write_text(json.dumps(pairs,ensure_ascii=False,indent=2))
(OUT/'acceptance-before-language-fix.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False,indent=2))
