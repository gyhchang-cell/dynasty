"""Apply the art branch's exact owned patch to the shared tree without discarding concurrent edits.
No build, JVM, client, or gameplay test is invoked. Back up every overwritten byte.
"""
import subprocess,sys,json,hashlib,shutil,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[3];dest=Path(sys.argv[1]).resolve();D=R/'docs/art/boss-forms-v2';backup=R/'build/boss-forms-delivery/before-sync';backup.mkdir(parents=True,exist_ok=True)
tracked=['src/main/java/com/dynasty/blueprint/client/Cod2EliteVoxelRenderer.java','src/main/java/com/dynasty/blueprint/elite/EliteContent.java','src/main/java/com/dynasty/blueprint/elite/FoxMatron.java','src/main/java/com/dynasty/blueprint/elite/HammerChain.java','src/main/java/com/dynasty/client/BossEightArtBindings.java','src/main/java/com/dynasty/entity/DynastyEntities.java']
patch=subprocess.check_output(['git','diff','main','--',*tracked],cwd=R);(backup.parent/'source-adaptations.patch').write_bytes(patch)
subprocess.run(['git','apply','--check','--whitespace=nowarn','-'],cwd=dest,input=patch,check=True)
new=[R/'src/main/java/com/dynasty/client/BossFormsRenderer.java',R/'src/main/java/com/dynasty/entity/BossFormSockets.java']
for folder in ['src/main/resources/assets/dynasty/geo/boss_forms','src/main/resources/assets/dynasty/animations/boss_forms','src/main/resources/assets/dynasty/textures/entity/boss_forms','tools/art/boss-forms','docs/art/boss-forms-v2']:
 new.extend(p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='delivery.json')
for f in new:
 rel=f.relative_to(R);target=dest/rel
 if target.exists():assert target.read_bytes()==f.read_bytes(),'Concurrent destination edit: '+str(rel)
pre={p:hashlib.sha256((dest/p).read_bytes()).hexdigest() for p in tracked}
for rel in tracked:
 p=dest/rel;saved=backup/rel;saved.parent.mkdir(parents=True,exist_ok=True)
 if not saved.exists():shutil.copy2(p,saved)
# Repeat the full check immediately before writing and refuse if a concurrent edit arrived.
assert pre=={p:hashlib.sha256((dest/p).read_bytes()).hexdigest() for p in tracked}
subprocess.run(['git','apply','--whitespace=nowarn','-'],cwd=dest,input=patch,check=True)
for f in new:
 target=dest/f.relative_to(R);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target)
post={str(p.relative_to(R)):hashlib.sha256((dest/p.relative_to(R)).read_bytes()).hexdigest() for p in new}
post.update({p:hashlib.sha256((dest/p).read_bytes()).hexdigest() for p in tracked})
record={'destination':str(dest),'sourceBase':subprocess.check_output(['git','rev-parse','main'],cwd=R,text=True).strip(),'nativeStatus':'NOT_RUN_USER_EXAM_HOLD','copiedFiles':len(new),'patchedJavaFiles':tracked,'sha256':post,'sourcePatchSha256':hashlib.sha256(patch).hexdigest()}
(D/'delivery.json').write_text(json.dumps(record,indent=2)+'\n');shutil.copy2(D/'delivery.json',dest/'docs/art/boss-forms-v2/delivery.json');print('Synced',len(new),'new files and',len(tracked),'narrow Java source patches. No Java launched.')
