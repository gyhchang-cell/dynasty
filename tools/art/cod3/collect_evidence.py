"""Collect final in-game evidence only when both native clients actually passed."""
import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw
from rebuild_npcs import ROOT, ASSETS, DOC, ROLES, STATES

p=argparse.ArgumentParser();p.add_argument('--native',required=True);p.add_argument('--views',required=True);p.add_argument('--frozen',required=True);p.add_argument('--jar',type=Path,required=True);p.add_argument('--refined');p.add_argument('--baseline-frozen');p.add_argument('--work');p.add_argument('--refined-frozen');a=p.parse_args()
native=ROOT/'build/cod3-client'/a.native/'results';views=ROOT/a.views/'results';frozen=ROOT/'build/blueprint-client/frozen'/a.frozen
assert (views/'PASS.txt').exists() and not (views/'FAIL.txt').exists()
resource=json.loads((DOC/'resource-validation.json').read_text());model_hashes={}
with zipfile.ZipFile(a.jar) as z:
 for r in resource['roles']:
  for rel,sha in r['sha256'].items():
   assert hashlib.sha256((ASSETS/rel).read_bytes()).hexdigest()==sha
   assert hashlib.sha256(z.read('assets/dynasty/'+rel)).hexdigest()==sha
   ps=[p for p in frozen.rglob(Path(rel).name) if str(p).endswith('/assets/dynasty/'+rel)]
   assert ps and all(hashlib.sha256(p.read_bytes()).hexdigest()==sha for p in ps),(rel,'runtime differs')
   model_hashes[rel]=sha
 assert not any('Cod3NpcNativeQa' in name or 'Cod3NpcArtQa' in name for name in z.namelist())
refined_roles={'hei_po','chu_nongyu'} if a.refined else set()
if a.refined:
 baseline=ROOT/'build/blueprint-client/frozen'/a.baseline_frozen
 for r in resource['roles']:
  if r['id'] in refined_roles:continue
  for rel,sha in r['sha256'].items():
   ps=[p for p in baseline.rglob(Path(rel).name) if str(p).endswith('/assets/dynasty/'+rel)]
   assert ps and all(hashlib.sha256(p.read_bytes()).hexdigest()==sha for p in ps),(rel,'baseline differs')
clients={};dest=DOC/'native';dest.mkdir(exist_ok=True)
if a.work:
 prior=ROOT/'build/blueprint-client/frozen'/a.refined_frozen
 for role in refined_roles:
  for rel in (f'geo/npc/{role}.geo.json',f'textures/entity/npc/{role}.png'):
   file=next(p for p in prior.rglob(Path(rel).name) if str(p).endswith('/assets/dynasty/'+rel));assert file.read_bytes()==(ASSETS/rel).read_bytes()
  rel=f'animations/npc/{role}.animation.json';file=next(p for p in prior.rglob(Path(rel).name) if str(p).endswith('/assets/dynasty/'+rel))
  old=json.loads(file.read_text())['animations'];new=json.loads((ASSETS/rel).read_text())['animations']
  for clip in old:
   if role!='hei_po' or clip!='animation.npc.work':assert old[clip]==new[clip]
for client in ('host','peer'):
 source=native/client;assert (source/'PASS.txt').exists() and not (source/'FAIL.txt').exists()
 rows=json.loads((source/'evidence.json').read_text());assert len(rows)==300 and len({r['stage'] for r in rows})==210
 extra=[]
 if a.refined:
  refined_source=ROOT/'build/cod3-client'/a.refined/'results'/client
  assert (refined_source/'PASS.txt').exists() and not (refined_source/'FAIL.txt').exists()
  extra=json.loads((refined_source/'evidence.json').read_text());assert len(extra)==40 and len({r['stage'] for r in extra})==28
  assert {(r['spec']['role'],r['spec']['state']) for r in extra}=={(r,s) for r in refined_roles for s in STATES}
  rows=[r for r in rows if r['spec']['role'] not in refined_roles]+extra
 work=[]
 if a.work:
  work_source=ROOT/'build/cod3-client'/a.work/'results'/client
  assert (work_source/'PASS.txt').exists() and not (work_source/'FAIL.txt').exists()
  work=json.loads((work_source/'evidence.json').read_text());assert len(work)==2 and all(r['spec']==dict(role='hei_po',state='work',angle=0) for r in work)
  rows=[r for r in rows if not (r['spec']['role']=='hei_po' and r['spec']['state']=='work')]+work
 assert {(r['spec']['role'],r['spec']['state']) for r in rows}=={(r,s) for r in ROLES for s in STATES}
 assert all(r['animation']=='animation.npc.'+r['spec']['state'] for r in rows)
 assert any(r['resourceReload'] for r in rows)
 motions=[r['poseDelta'] for r in rows if 'poseDelta' in r];assert len(motions)==90 and min(motions)>.0001
 grips=[v for r in rows for v in r['gripDistancesMetres'].values()];assert grips and max(grips)<.2
 def shot_source(row):
  if a.work and row['spec']['role']=='hei_po' and row['spec']['state']=='work':return work_source
  return refined_source if row['spec']['role'] in refined_roles else source
 for r in rows:assert (shot_source(r)/r['screenshot']).exists()
 target=dest/client;target.mkdir(exist_ok=True)
 for name in ('evidence.json','PASS.txt'):shutil.copyfile(source/name,target/name)
 if (source/'completion-recovery.txt').exists():shutil.copyfile(source/'completion-recovery.txt',target/'completion-recovery.txt')
 if a.refined:
  for name in ('evidence.json','PASS.txt'):shutil.copyfile(refined_source/name,target/('refined-'+name))
  (target/'final-evidence.json').write_text(json.dumps(rows,indent=2)+'\n')
 if a.work:
  for name in ('evidence.json','PASS.txt'):shutil.copyfile(work_source/name,target/('work-'+name))
 for role in ROLES:
  for state,angle in [('idle',0),('idle',45),('idle',90),('idle',180),('work',0),('walk',0),('react',0)]:
   chosen=[r for r in rows if r['spec']==dict(role=role,state=state,angle=angle)][-1]
   shutil.copyfile(shot_source(chosen)/chosen['screenshot'],target/chosen['screenshot'])
 clients[client]={'passed':True,'stages':210,'screenshots':300,'refinedStages':28 if extra else 0,'refinedScreenshots':len(extra),'workRefinementStages':1 if work else 0,'workRefinementScreenshots':len(work),'motionSamples':len(motions),'minimumPoseDelta':min(motions),'maximumGripDistanceMetres':max(grips),'completionExportRecovered':(source/'completion-recovery.txt').exists(),'fullRun':str(source.relative_to(ROOT))}
checks=[];roles=list(ROLES);angles=['180','135','90','0','silhouette']
for part in range(3):
 sheet=Image.new('RGB',(1000,1100),'#b8c2cc');draw=ImageDraw.Draw(sheet)
 for row,role in enumerate(roles[part*5:part*5+5]):
  for column,angle in enumerate(angles):
   im=Image.open(views/f'{role}-{angle}.png').convert('RGB');bg=im.getpixel((0,0))
   points=[(x,y) for y in range(im.height) for x in range(im.width) if im.getpixel((x,y))!=bg]
   assert points;xs=[x for x,y in points];ys=[y for x,y in points];bounds=[min(xs),min(ys),max(xs),max(ys)]
   assert bounds[0]>0 and bounds[1]>0 and bounds[2]<599 and bounds[3]<599
   if angle=='silhouette':assert all(im.getpixel(pos)==(0,0,0) for pos in points)
   checks.append({'role':role,'view':angle,'foreground':len(points),'bounds':bounds})
   sheet.paste(im.resize((200,200),Image.Resampling.NEAREST),(column*200,row*220));draw.text((column*200+4,row*220+203),role+' '+angle,fill='black')
 sheet.save(DOC/f'review-{part+1}.png')
(DOC/'views-validation.json').write_text(json.dumps({'passed':True,'renders':75,'frames':checks},indent=2)+'\n')
shutil.copyfile(views/'PASS.txt',DOC/'render-pass.txt')
sheet=Image.new('RGB',(1000,660),'white');draw=ImageDraw.Draw(sheet)
for i,role in enumerate(ROLES):
 im=Image.open(ASSETS/f'textures/entity/npc/{role}.png');sheet.paste(im.resize((192,192),Image.Resampling.NEAREST),((i%5)*200,(i//5)*220));draw.text(((i%5)*200+4,(i//5)*220+196),role,fill='black')
sheet.save(DOC/'textures-review.png')
delivery=ROOT/'build/cod3-art-20261010/dynasty-1.4.0-cod3-npc-art.jar';shutil.copyfile(a.jar,delivery)
verification={'passed':True,'date':'2026-10-11','scope':'15 existing cod3 NPCs; resource art and opt-in QA only','runtimeFiles':45,'editableFiles':30,'geckoVersion':'4.8.4','minecraftVersion':'1.20.1','forgeVersion':'47.4.10','renderedViews':75,'clients':clients,'nativeRun':a.native,'refinedNativeRun':a.refined,'workNativeRun':a.work,'frozenRun':a.frozen,'jar':str(delivery.relative_to(ROOT)),'jarSha256':hashlib.sha256(delivery.read_bytes()).hexdigest(),'resourceSha256':model_hashes,'productionJavaChanged':False}
(DOC/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
print('PASS: 15 NPCs, 75 five-view renders, 2x210 in-world stages, 2x300 captures, moving wrists and attached hand props; final Jar SHA '+verification['jarSha256'])
