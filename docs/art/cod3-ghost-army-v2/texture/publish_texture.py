"""Publish reviewed native atlas and replace BB embedded image only, with hash guards."""
from pathlib import Path
import json,hashlib,base64,os
D=Path(__file__).resolve().parent;R=D.parents[3];M=D.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((D/'source-before.json').read_text())
for p,h in before.items():assert sha(R/p)==h,'Concurrent edit: '+p
bb=M/'blockbench/ghost_army_soldier.bbmodel';obj=json.loads(bb.read_text());assert len(obj['textures'])==1
png=D/'texture.png';data=png.read_bytes();obj['textures'][0]['source']='data:image/png;base64,'+base64.b64encode(data).decode();obj['textures'][0]['name']='ghost_army_soldier.png'
prod=R/'src/main/resources/assets/dynasty/textures/entity/scenic/ghost_army_soldier.png';prod.parent.mkdir(parents=True,exist_ok=True)
with prod.open('xb') as f:f.write(data)
tmp=bb.with_name(bb.name+'.texture-pending');tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');assert sha(bb)==before[str(bb.relative_to(R))];os.replace(tmp,bb)
print('Published original atlas',sha(prod),'and BB embedded image only')
