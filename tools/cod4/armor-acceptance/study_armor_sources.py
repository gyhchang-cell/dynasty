"""Conservative candidate extraction. Candidates are NOT accepted references or a fulfilled quota."""
from pathlib import Path
import collections,hashlib,json,re
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
MASK=re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
METHOD=re.compile(r'(?m)^[ \t]*(?:(?:public|protected|private|static|final|synchronized|default)\s+)+(?:[\w<>?,.\[\]@]+\s+)+(?P<name>\w+)\s*\([^;{}]*?\)\s*(?:throws[^{;]+)?\{')
EFFECT=re.compile(r'\b(?:addEffect|removeEffect|removeAllEffects|addPotionEffect|removePotionEffect|addStatusEffect|removeStatusEffect|addTemporaryAttributeModifiers|removeAttributeModifiers|addTransientModifier|addPermanentModifier|removeModifier|applyAttributeModifiersToEntity|removeAttributeModifiersFromEntity|setSprinting|setInvulnerable|startUsingItem|stopUsingItem|resetActiveHand|setActiveHand)\s*\(')
COOL=re.compile(r'\b(?:addCooldown|setCooldown|setCooldownUntil|setRemainingCooldown|resetCooldown|setCooldownTime|setCooldownTicks|applyCooldown)\s*\(')
STATE=re.compile(r'\b(?:putInt|putLong|setInteger|setLong|putBoolean|setBoolean|setTag|removeTag|remove|set)\s*\([^\n;]*(?:[Cc]ooldown|[Cc]harg|[Aa]ctiv|[Dd]uration|[Ll]ast|[Tt]ick|[Tt]ime|[Uu]se|[Ee]quip|[Bb]uff|[Ss]tate|[Mm]ode|[Ff]light|[Ff]lying)')
EQUIP=re.compile(r'\b(?:getItemBySlot|getEquippedStack|getArmorSlots|getArmorInventoryList|getMainHandItem|getOffhandItem|getMainHandStack|getOffHandStack|getHeldItemMainhand|getHeldItemOffhand|isEquipped|hasCurio|isWearing|hasArmorSet|hasSetBonus|isCorrectArmor|onEquipped|onUnequipped|onUnequip|onEquip|curioTick|onArmorTick|wornTick|inventoryTick|hasWindyRobes|hasCurios|findCurios|findFirstCurio)\b')
rows=[];seen=set();source_count=0
for corpus in [ROOT/'build/item-use-references',ROOT/'build/creature-reference-1000']:
 for meta in sorted(corpus.glob('*/source.json')):
  data=json.loads(meta.read_text());repo=data.get('repo');revision=data.get('sha')
  if not repo or not revision:continue
  for p in sorted(meta.parent.rglob('*.java')):
   if any(x.lower() in {'client','render','renderer','renderers','model','models','datagen','generated','test','tests'} for x in p.parts):continue
   raw=p.read_text(errors='replace');code=MASK.sub(lambda m: ''.join('\n' if c=='\n' else ' ' for c in m[0]),raw)
   item_file=any(x.lower() in {'item','items','curios','armor','armour','equipment','weapon','weapons'} for x in p.parts) or bool(re.search(r'(?:Item|Armor|Armour|Curio|Bauble|Trinket|Cooldown)(?:Handler|Events|Impl|Capability)?\.java$',p.name))
   stack=[];end_at={}
   for i,c in enumerate(code):
    if c=='{':stack.append(i)
    elif c=='}' and stack:end_at[stack.pop()]=i+1
   source_count+=1
   for m in METHOD.finditer(code):
    end=end_at.get(m.end()-1)
    if end is None:continue
    body=raw[m.start():end];masked=code[m.start():end];name=m['name']
    if name.startswith(('register','getDefaultAttribute','getAttributeModifiers','append','addInformation','getTooltip')):continue
    if not item_file and not EQUIP.search(masked):continue
    actions=EFFECT.findall(masked)+COOL.findall(masked)+STATE.findall(body)
    if not actions:continue
    # Predicate/lifecycle or concrete item input is required. Registration fields do not pass this gate.
    if not re.search(r'\b(?:if|switch)\s*\(|\b(?:onUnequip|onUnequipped|curioTick|onArmorTick|use|useOn|onItemRightClick|finishUsingItem|inventoryTick|onUseTick|onPlayerStoppedUsing|releaseUsing)\b',masked):continue
    norm=re.sub(r'\s+','',MASK.sub('',body))
    digest=hashlib.sha256(norm.encode()).hexdigest()
    if digest in seen:continue
    seen.add(digest)
    line=raw.count('\n',0,m.start())+1;last=raw.count('\n',0,end)+1;rel=p.relative_to(meta.parent).as_posix()
    rows.append({'repo':repo,'revision':revision,'path':rel,'line':line,'end_line':last,'method':name,
      'source_local':str(p.relative_to(ROOT)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
      'snippet_sha256':digest,'url':f'https://github.com/{repo}/blob/{revision}/{rel}#L{line}-L{last}',
      'item_scoped':item_file,'actions':actions,'excerpt':body})
out=BASE/'.work/armor-reference-candidates.json';out.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('Source files scanned:',source_count,'distinct candidate methods:',len(rows),'(not accepted)')
print(json.dumps(dict(collections.Counter(x['repo'] for x in rows)),indent=2))
for i,r in enumerate(rows[:15]):print(i,r['repo'],r['path'],r['method'],r['actions'])
