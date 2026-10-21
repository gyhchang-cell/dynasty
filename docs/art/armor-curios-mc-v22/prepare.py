from pathlib import Path
import json,hashlib,zipfile
D=Path(__file__).resolve().parent;R=D.parents[2];A=R/'src/main/resources/assets/dynasty'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=json.loads((D/'selection.json').read_text());base=json.loads((D/'baseline.json').read_text())
with zipfile.ZipFile('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client.jar') as z:generated=json.loads(z.read('assets/minecraft/models/item/generated.json'))['display']
handheld=json.loads((A/'models/item/solid_handheld.json').read_text())['display']
for row in rows:
 p=A/'textures/item'/f"{row['id']}.png";assert sha(p)==base[str(p.relative_to(R))]
 model=A/'models/item'/f"{row['id']}.json";assert model.read_bytes()==(D/'before'/model.relative_to(R)).read_bytes()
 row['display']=handheld if row['group']=='weapons' else generated
(D/'selection.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
