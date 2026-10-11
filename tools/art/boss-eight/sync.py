"""Synchronize only verified owned resources, refusing concurrent edits; retain restore bytes."""
import json,hashlib,shutil,sys,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[3];dest=Path(sys.argv[1]);M=json.loads((Path(__file__).parent/'targets.json').read_text());proof=json.loads((R/'docs/art/boss-eight-v1/native-validation.json').read_text());assert proof['status']=='PASS' and proof['nativeStages']==74
owned={}
for id,m in M.items():
 old={b['path']:b['sha256'] for b in m['baseline']+m.get('dependencies',[])}
 for kind,ext in [('geo','.geo.json'),('animations','.animation.json'),('textures/entity','.png')]:
  p=str(Path('src/main/resources/assets/dynasty')/kind/m['folder']/(id+ext));owned[p]=old.get(p)
 for dep in m.get('dependencies',[]):owned[dep['path']]=dep['sha256']
owned['src/main/java/com/dynasty/client/BossEightArtBindings.java']=None
sha=lambda b:hashlib.sha256(b).hexdigest()
# Validate the entire write set before the first mutation.
for p,old in owned.items():
 if (dest/p).exists():assert sha((dest/p).read_bytes()) in [old,sha((R/p).read_bytes())], 'Concurrent target edit: '+p
 else:assert old is None,'Missing target: '+p
for path,h in proof['resourceSha256'].items():assert sha((R/'src/main/resources'/path).read_bytes())==h,'Art changed after native verification'
backup=R/'build/boss-eight-delivery/before-sync';backup.mkdir(parents=True,exist_ok=True);result={}
for p,old in owned.items():
 if (dest/p).exists() and not (backup/p).exists():(backup/p).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest/p,backup/p)
 (dest/p).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/p,dest/p);result[p]=sha((dest/p).read_bytes())
(R/'docs/art/boss-eight-v1/delivery.json').write_text(json.dumps({'destination':str(dest),'ownedFiles':result,'nativeProof':'native-validation.json','buildJarSha256':proof['productionJarSha256'],'excluded':'Combat, registration, quests, drops, other developers working files'},indent=2)+'\n')
print('Synchronized verified owned files:',len(result))
