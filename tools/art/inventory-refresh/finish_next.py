"""Incorporate only the twenty visually reviewed, authorized replacements."""
from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parents[3];D=R/'docs/art/inventory-refresh-v1';selected=json.loads((D/'accessory-next-selection.json').read_text());m=json.loads((D/'generated-manifest.json').read_text());new=[]
for row in selected:
 p=D/'next-generation'/f"{row['id']}.json"
 if not p.exists():raise SystemExit('Still generating '+row['id'])
 info=json.loads(p.read_text());target=D/'sources/accessories'/f"{row['id']}.png";shutil.copy2(info['path'],target);new.append({'id':row['id'],'prompt':info['prompt'],'source':str(target.relative_to(R))})
existing={x['id'] for x in m['accessories']};m['accessories'] += [x for x in new if x['id'] not in existing];(D/'generated-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print('Accessory manifest contains',len(m['accessories']))
