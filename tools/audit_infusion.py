#!/usr/bin/env python3
"""Audit data-driven infusion coverage and original-content invariants."""
import json,re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];base='86c3d2a422a4413626d10bc6f1728bca5744e2b6'
def read(path):return (root/path).read_text()
def original(path):return subprocess.check_output(['git','show',base+':'+path],cwd=root)
rows=json.loads(read('src/main/resources/data/dynasty/infusion/materials.json'))
ids={r['itemId'] for r in rows};effects={r['enhancementId'].split(':')[1] for r in rows}
assert len(rows)==len(ids)==95 and len(effects)==40
combat=read('src/main/java/com/dynasty/infusion/InfusionCombat.java')
for r in rows:
 assert r['requiredCount']==2 and r['capacityCost'] in (1,2) and r['tier']==1
 assert r['enhancementId'].split(':')[1] in combat
 for source in r['sourceReferences']:
  p=source if source.startswith('src/') else 'src/main/resources/data/dynasty/'+source
  assert r['itemId'] in read(p) or '"'+r['itemId'].split(':')[1]+'"' in read(p),(r['itemId'],p)
 for locale in ['zh_cn','en_us']:
  lang=json.loads(read(f'src/main/resources/assets/dynasty/lang/{locale}.json'))
  assert r['nameKey'] in lang and r['descriptionKey'] in lang
  assert not any(k.startswith('tooltip.dynasty.salvage.') for k in lang)

from PIL import Image
atlas=Image.open(root/'src/main/resources/assets/dynasty/textures/gui/infusion_crests.png')
assert atlas.size==(160,64)
assert len({atlas.crop(((i%10)*16,(i//10)*16,(i%10+1)*16,(i//10+1)*16)).tobytes() for i in range(40)})==40
# Newly generated mappings must include every actual salvage and treasure registry item.
for path in ['src/main/java/com/dynasty/blueprint/BlueprintSalvage.java','src/main/java/com/dynasty/workshop/DynastyTreasures.java']:
 registered=set(re.findall(r'(?:register|part)\("([a-z_]+)"',read(path)))
 # Ammunition is usable ammunition, not an infusion material.
 registered.discard('short_crossbow_bolt')
 missing={'dynasty:'+x for x in registered}-ids
 assert not missing,missing
protected=['src/main/java/com/dynasty/DynastyItems.java','src/main/java/com/dynasty/DynastyTabs.java','src/main/java/com/dynasty/DynastyRelics.java','src/main/java/com/dynasty/DynastyFineItems.java','src/main/java/com/dynasty/block/LivingWorkshopBlock.java','src/main/java/com/dynasty/workshop/WorkshopRecipes.java']
for path in protected:assert (root/path).read_bytes()==original(path),'Changed protected content: '+path
old_book=json.loads(original('docs/quests-remaster/book.json'));new_book=json.loads(read('docs/quests-remaster/book.json'))
for old_ch,new_ch in zip(old_book,new_book):
 assert old_ch['file']==new_ch['file'] and len(old_ch['quests'])==len(new_ch['quests'])
 for old_q,new_q in zip(old_ch['quests'],new_ch['quests']):
  if old_q.get('target')=='dynasty:first_infusion':old_q['description']=new_q['description']
  assert old_q==new_q,'Existing task structure/rewards changed'
for locale in ['zh_cn','en_us']:
 path=f'src/main/resources/assets/dynasty/lang/{locale}.json';old=json.loads(original(path));new=json.loads(read(path))
 assert all(new.get(k)==v for k,v in old.items() if k.startswith(('item.','block.','entity.'))),'Original displayed names changed'
# Loot, recipes and existing item assets are byte-identical, including drop amounts.
changed=subprocess.check_output(['git','diff','--name-only',base],cwd=root).decode().splitlines()
for path in changed:
 assert not any(x in path for x in ['/loot_tables/','/recipes/','/textures/item/','/models/item/']),path
assert 'AnvilUpdateEvent' not in read('src/main/java/com/dynasty/blueprint/BlueprintSalvage.java')
for path in ['src/main/java/com/dynasty/DynastyTiers.java','src/main/java/com/dynasty/DynastyArmorMaterials.java']:
 assert not re.search(r'Ingredient.of\((?:Dynasty|Blueprint)',read(path))
for path in (root/'src/main/java/com/dynasty/infusion').glob('*.java'):
 assert not re.search(r'[\u4e00-\u9fff]',path.read_text()),'Unlocalized infusion Java: '+str(path)
print('PASS: 95 existing materials, 40 effects, bilingual keys, original IDs/names/creative order/assets/loot/recipes/quests, special repair removed.')
