from pathlib import Path
import sys,json,hashlib,subprocess
from PIL import Image
R=Path(__file__).resolve().parents[3];S=Path('/Users/a15356015027/Desktop/dynasty');sys.path.insert(0,str(R/'tools/art/cod2-voxel'))
from creature_surfaces import IDS
from species_materials import finish
from resource_paths import resource_paths
for name in (sys.argv[1:] or IDS):
 d=R/'docs/art/creature-mc-v37'/name;d.mkdir(parents=True,exist_ok=True)
 g,a,t=resource_paths(name)
 for p,key in [(g,'before.geo.json'),(a,'before.animation.json'),(t,'before.png')]:
  if not (d/key).exists():
   assert p.read_bytes()==(S/p.relative_to(R)).read_bytes(),'Shared/worktree differ '+str(p)
   (d/key).write_bytes(p.read_bytes())
 geo=json.loads((d/'before.geo.json').read_text());im=finish(name,geo,Image.open(d/'before.png'));g.write_text(json.dumps(geo,indent=2)+'\n');im.save(t)
 print(name,im.size)
