"""Audit actual accessory mechanisms and acquisition/task predicates, not icon mentions.

GOOD describes a nontrivial implemented mechanism, never client/MP acceptance.
Flags may coexist. DUPLICATE is a complete table-rule match with no item-specific
combat hook; NO_VISUAL means no identified runtime trigger, not missing icons.
"""
from pathlib import Path
import collections,json,re,sys
ROOT=Path(__file__).resolve().parents[2];JAVA=ROOT/'src/main/java/com/dynasty';DATA=ROOT/'src/main/resources/data/dynasty'
sys.path.insert(0,str(ROOT/'tools/art'))
from quest_snbt import list_compounds,object_id
source=(JAVA/'DynastyTrinkets.java').read_text()
school_source=(JAVA/'DynastyAccessoryData.java').read_text()
school_rules={m[1]:{'school':m[2],'kind':m[3],'amount':float(m[4]),'owner':'DynastySchoolAccessories.bonus/count; DynastyAccessoryRefining.damageBonus/milestones'} for m in re.finditer(r'case "([^"]+)" -> new Bonus\("([^"]+)", "([^"]+)", ([0-9.]+)\)',school_source)}
def location(path,offset):return str(path.relative_to(ROOT))+':'+str(path.read_text()[:offset].count('\n')+1)
rows={}
for m in re.finditer(r'\{"([^"\n]+)",\s*((?:-?\d[^{}\n]*)?)\}',source):
 values=[float(v.strip().removesuffix('D')) for v in m[2].split(',')]
 if len(values) in (7,13,14):rows[m[1]]=values
base=re.search(r'List<String> out = new ArrayList<>\(List.of\((.*?)\)\);',source,re.S)
ids=set(re.findall(r'"([^"\n]+)"',base[1]))|set(rows);assert len(ids)==len(re.findall(r'"([^"\n]+)"',base[1]))+len(rows)
recipes=collections.defaultdict(list);loot=collections.defaultdict(list);rewards=collections.defaultdict(list);tasks=collections.defaultdict(list)
for p in DATA.joinpath('recipes').rglob('*.json'):
 result=json.loads(p.read_text()).get('result');item=result.get('item') if isinstance(result,dict) else result
 if isinstance(item,str) and item.startswith('dynasty:'):recipes[item[8:]].append(str(p.relative_to(ROOT)))
def loot_items(value):
 if isinstance(value,dict):
  if value.get('type')=='minecraft:item' and isinstance(value.get('name'),str):yield value['name']
  for child in value.values():yield from loot_items(child)
 elif isinstance(value,list):
  for child in value:yield from loot_items(child)
for p in DATA.joinpath('loot_tables').rglob('*.json'):
 for item in set(loot_items(json.loads(p.read_text()))):
  if item.startswith('dynasty:'):loot[item[8:]].append(str(p.relative_to(ROOT)))
for p in ROOT.joinpath('modpack/config/ftbquests/quests/chapters').glob('*.snbt'):
 for quest in list_compounds(p.read_text(),'quests'):
  identity=object_id(quest);inner='\n'.join(line[2:] if line.startswith('\t\t') else line for line in quest.splitlines())
  for task in list_compounds(inner,'tasks'):
   kind=re.search(r'\btype:\s*"([^"]+)"',task)
   if not kind:continue
   if kind[1]=='item':
    for item in re.findall(r'\bid:\s*"dynasty:([^"\n]+)"',task):tasks[item].append({'chapter':p.stem,'node':identity,'objective':'OBTAIN','predicate':task.strip()})
   elif kind[1]=='advancement':
    for adv in re.findall(r'\badvancement:\s*"dynasty:([^"\n]+)"',task):
     if adv.startswith('cod4_obtain_'):tasks[adv.removeprefix('cod4_obtain_')].append({'chapter':p.stem,'node':identity,'objective':'OBTAIN','advancement':adv,'hook':'ContentProgress.reconcile: actual inventory/armor/active Curios'})
  for reward in list_compounds(inner,'rewards'):
   if re.search(r'\btype:\s*"item"',reward):
    for item in re.findall(r'\bid:\s*"dynasty:([^"\n]+)"',reward):rewards[item].append({'chapter':p.stem,'node':identity,'reward':reward.strip()})
# Only concrete behavior owners. Registration, tooltip, generators and tests are
# intentionally excluded; references below are evidence to inspect, not tests.
behavior_names=['DynastyAccessoryData.java','DynastySchoolCombat.java','DynastyMerit.java','DynastyCombatEvents.java','DynastyWorldEvents.java','expansion/EquipmentBehaviors.java','expansion/ExpansionEffects.java','cod3/EquipmentFeedback.java']
behavior={name:(JAVA/name).read_text() for name in behavior_names}
external={id:[{'file':location(JAVA/name,m.start()),'line':s.splitlines()[s[:m.start()].count('\n')].strip()} for name,s in behavior.items() for m in re.finditer(r'"'+re.escape(id)+r'"',s)] for id in ids}
signatures=collections.defaultdict(list)
for id,values in rows.items():
 if not external[id]:signatures[tuple(values)].append(id)
# Canonical shared visual owners: actual water transitions, combo release, and
# proc event templates. Inventory models are checked separately, never a cue.
visual={'sea_pearl':'EquipmentFeedback.equipment water transition; EquipmentBehaviors.tick WATER cue','jade_tortoise':'EquipmentFeedback.equipment water transition','sea_conch':'EquipmentFeedback.equipment water transition','dragon_pearl':'EquipmentBehaviors.combo -> releaseComboWave -> qinglong_combo_wave'}
box=(JAVA/'expansion/ContentProgress.java').read_text();assert 'for(String id:DynastyTrinkets.IDS)' in box and 'opened.getBoolean(id)' in box
assert recipes['trinket_box'],'Universal gift source must itself have a real survival recipe'
output=[]
for id in sorted(ids):
 values=rows.get(id);refs=external[id];flags=[]
 simple=values is not None and len(values)==7 and values[4]==0 and values[6]==0 and not refs
 if simple:flags.append('TOO_SIMPLE')
 peers=[x for x in signatures.get(tuple(values or []),[]) if x!=id] if values and not refs else []
 if peers:flags.append('DUPLICATE')
 proc=int(values[10]) if values and len(values)>=13 else 0;link=int(values[13]) if values and len(values)>13 else 0
 cue=visual.get(id)
 if proc:cue='DynastyTrinketOnHit actual proc '+str(proc)+' -> EquipmentFeedback.proc -> existing type-specific native template; item-specific visuals/client inspection pending'
 if not cue:flags.append('NO_VISUAL')
 acquisition=[{'kind':'recipe','path':x} for x in sorted(recipes[id])]+[{'kind':'loot','path':x} for x in sorted(loot[id])]+[{'kind':'quest_reward',**x} for x in rewards[id]]
 acquisition.append({'kind':'trinket_box_unseen_pool','hook':'DynastyUsables.TrinketBoxItem.use -> ContentProgress.gift -> every canonical DynastyTrinkets.IDS until seen; then original weighted pool','source_recipes':recipes['trinket_box']})
 if not acquisition:flags.append('NO_SOURCE')
 if not tasks[id]:flags.append('NO_TASK_LINK')
 mechanism='TOO_SIMPLE' if simple else 'GOOD'
 evidence=[location(JAVA/'DynastyTrinkets.java',m.start()) for m in re.finditer(r'"'+re.escape(id)+r'"',source)]
 slots=[str(p.relative_to(ROOT)) for p in ROOT.joinpath('src/main/resources/data/curios/tags/items').glob('*.json') if 'dynasty:'+id in json.loads(p.read_text()).get('values',[])]
 output.append({'id':id,'mechanism_review':mechanism,'classifications':[mechanism]+flags if mechanism not in flags else flags,'table_rule':values,'school_bonus':school_rules.get(id),'mechanism_evidence':evidence,'item_specific_behavior':refs,'duplicate_full_table_peers':peers,'proc':{'code':proc,'value':values[11],'chance':values[12]} if proc else None,'link_group':link,'sources':acquisition,'task_targets':tasks[id],'reward_mentions_do_not_count_as_objectives':len(rewards[id]),'curios_slots':slots,'mutual_exclusion':{'duplicate_same_id':'activeIds set deduplicates; fixed per-ID UUID','different_ids':'No blanket equip exclusion in DynastyCurioCharm; different IDs can coexist. Highest-wins merit bonus is calculated, not an equip lock.','specific_highest_wins_merit':id in ('gold_seal_charm','imperial_seal_charm','merit_badge'),'synergy':'Highest reached 2/3/4 tier in DynastyTrinketLink, no tier stacking' if link else 'No table synergy group'},'visual_trigger':cue or 'No identified item-specific gameplay cue; inventory icon/held rendering is not proc feedback','client_real_multiplayer_old_world':'PENDING'})
counts=collections.Counter(flag for row in output for flag in row['classifications'])
report={'canonical_accessories':len(output),'classification_definitions':{'GOOD':'Nontrivial concrete mechanism or conditional/proc/link table rule; not complete task/source/visual/gameplay acceptance','TOO_SIMPLE':'Only unconditional table stats with no effect/condition/proc/link or identified item-specific combat owner','DUPLICATE':'Exact full table rule and no identified external combat owner; review peers, do not delete IDs/items','NO_SOURCE':'No actual recipe, loot, quest item reward or verified canonical box pool','NO_TASK_LINK':'No actual FTB item detector or cod4 obtain advancement; icons/descriptions/item rewards excluded','NO_VISUAL':'No identified runtime gameplay cue; models/icons do not qualify'},'classification_counts':{flag:counts.get(flag,0) for flag in ['GOOD','TOO_SIMPLE','DUPLICATE','NO_SOURCE','NO_TASK_LINK','NO_VISUAL']},'universal_gift_survival_recipes':recipes['trinket_box'],'known_mechanism_issue':'Opposite-condition third attributes repaired: main and third predicates are independent; original code-9 max-health UUID is cleared on refresh/unequip; original values/UUIDs/IDs remain; native day/night/unequip verification documented in batch11.','scope':'Source-grounded audit. Real Curios use, visual quality, old-world and network multiplayer acceptance remain pending. All canonical IDs retained; no gameplay deletion.'}
(ROOT/'docs/cod4/accessory-audit.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n');(ROOT/'docs/cod4/accessory-audit-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'accessories':len(output),'counts':dict(counts)},ensure_ascii=False))
