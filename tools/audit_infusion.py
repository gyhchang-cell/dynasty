#!/usr/bin/env python3
"""Check original-material invariants against the full-project baseline and refresh audit JSON."""
import json,re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
BASE='7a79adb'
def original(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=root).decode()
def load(path):return json.loads((root/path).read_text())
source=(root/'src/main/java/com/dynasty/infusion/InfusionTraits.java').read_text()
ids=re.findall(r'\bt\("([a-z_]+)",',source)
assert len(ids)==24 and len(set(ids))==24
for locale in ['zh_cn','en_us']:
 path=f'src/main/resources/assets/dynasty/lang/{locale}.json'
 old=json.loads(original(path));new=load(path)
 assert all(new.get(k)==v for k,v in old.items()),'Existing translations changed'
protected=['src/main/java/com/dynasty/DynastyItems.java','src/main/java/com/dynasty/DynastyRelics.java','src/main/java/com/dynasty/DynastyFineItems.java','src/main/java/com/dynasty/blueprint/BlueprintSalvage.java','src/main/java/com/dynasty/block/LivingWorkshopBlock.java','src/main/java/com/dynasty/workshop/WorkshopRecipes.java']
for path in protected:assert (root/path).read_text()==original(path),'Original material/workshop definition changed: '+path
for id in ids:
 for base in ['assets/dynasty/models/item','assets/dynasty/textures/item','data/dynasty/recipes']:
  for suffix in ['.json','.png']:
   path=f'src/main/resources/{base}/{id}{suffix}'
   p=root/path
   if p.exists():assert p.read_bytes()==subprocess.check_output(['git','show',BASE+':'+path],cwd=root),path
book=load('docs/quests-remaster/book.json');old=json.loads(original('docs/quests-remaster/book.json'))
for chapter in old:
 new=next(c for c in book if c['file']==chapter['file'])
 for quest in chapter['quests']:assert next(q for q in new['quests'] if q['id']==quest['id'])==quest,'Existing quest changed'
lang=load('src/main/resources/assets/dynasty/lang/zh_cn.json')
alljson=list((root/'src/main/resources/data/dynasty/recipes').glob('*.json'))+list((root/'src/main/resources/data/dynasty/loot_tables').rglob('*.json'))
tracked=set(subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'src/main/resources/data/dynasty'],cwd=root).decode().splitlines())
alljson=[p for p in alljson if str(p.relative_to(root)) in tracked]
rows=[]
for id in ids:
 refs=[str(p.relative_to(root/'src/main/resources/data/dynasty')) for p in alljson if '"dynasty:'+id+'"' in p.read_text()]
 rows.append({'id':'dynasty:'+id,'name':lang['item.dynasty.'+id],'existing_recipe_and_loot_references':refs})
(root/'docs/infusion/material-audit.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('PASS: 24 existing materials; original definitions, translations, named assets, recipes and all old quests preserved.')
