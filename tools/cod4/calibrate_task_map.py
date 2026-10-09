"""Calibrate the existing table from actual FTB tasks, recipe results and discovery rewards.

This does not create quests or certify client/old-world/multiplayer acceptance.
Run after task/source edits; retain authored mechanism and pending notes.
"""
from pathlib import Path
import csv,io,json,re,sys,collections
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/art'))
from quest_snbt import list_compounds,object_id
DATA=ROOT/'src/main/resources/data/dynasty'
MAP=ROOT/'docs/cod4/content-task-map.tsv'
rows=list(csv.DictReader(MAP.open(),delimiter='\t'));fields=list(rows[0]);assert len(fields)==13
links=collections.defaultdict(list);quest_count=0
for file in sorted((ROOT/'modpack/config/ftbquests/quests/chapters').glob('*.snbt')):
    for quest in list_compounds(file.read_text(),'quests'):
        quest_count+=1;identity=object_id(quest);assert identity
        inner='\n'.join(line[2:] if line.startswith('\t\t') else line for line in quest.splitlines())
        dependencies=re.search(r'^\tdependencies:\s*\[([^\]]*)\]',inner,re.M)
        deps=re.findall(r'"([0-9a-fA-F]{16})"',dependencies[1]) if dependencies else []
        rewards=list_compounds(inner,'rewards')
        reward=[]
        for block in rewards:
            kind=re.search(r'\btype:\s*"([^"]+)"',block)
            if kind and kind[1]=='xp':
                amount=re.search(r'\bxp:\s*(\d+)',block);reward.append('xp='+amount[1] if amount else 'PENDING: legacy value is not read by installed XPReward.readData')
            elif kind and kind[1]=='item':
                count=re.search(r'\bcount:\s*(\d+)',block)
                reward+=[item+' x'+(count[1] if count else '1') for item in re.findall(r'\bid:\s*"((?:dynasty|minecraft):[^"]+)"',block)]
            elif kind and kind[1]=='command':
                command=re.search(r'\bcommand:\s*("(?:\\.|[^"\\])*")',block)
                reward.append('command='+json.loads(command[1]) if command else 'command (see node)')
            elif kind:reward.append(kind[1]+' (see node)')
        for task in list_compounds(inner,'tasks'):
            kind=re.search(r'\btype:\s*"([^"]+)"',task)
            if not kind:continue
            keys=set(re.findall(r'\b(?:id|entity):\s*"dynasty:([^"]+)"',task))
            adv=re.search(r'\badvancement:\s*"dynasty:([^"]+)"',task)
            if adv and adv[1].startswith('cod4_'):keys.add(adv[1].removeprefix('cod4_obtain_').removeprefix('cod4_'))
            for key in keys:links[key].append(dict(chapter=file.stem,node=identity,type=kind[1],target=adv[1] if adv else key,deps=deps,rewards=reward))
recipes=collections.defaultdict(list);uses=collections.defaultdict(list)
def input_items(value):
    if isinstance(value,dict):
        for key,child in value.items():
            if key=='item' and isinstance(child,str):yield child
            elif key!='result':yield from input_items(child)
    elif isinstance(value,list):
        for child in value:yield from input_items(child)
for path in sorted((DATA/'recipes').rglob('*.json')):
    value=json.loads(path.read_text());result=value.get('result');item=result.get('item','') if isinstance(result,dict) else result if isinstance(result,str) else ''
    if item.startswith('dynasty:'):recipes[item.split(':',1)[1]].append(str(path.relative_to(DATA/'recipes')).removesuffix('.json'))
    for ingredient in set(input_items(value)):
        if ingredient.startswith('dynasty:'):uses[ingredient.split(':',1)[1]].append(str(path.relative_to(DATA/'recipes')).removesuffix('.json'))
discoveries=collections.defaultdict(list)
for path in sorted((DATA/'advancements/recipes').rglob('*.json')):
    value=json.loads(path.read_text());conditions=[]
    for criterion in value.get('criteria',{}).values():
        for item in criterion.get('conditions',{}).get('items',[]):conditions+=item.get('items',[])
    for recipe in value.get('rewards',{}).get('recipes',[]):discoveries[recipe.removeprefix('dynasty:')].append(str(path.relative_to(DATA/'advancements')).removesuffix('.json')+' via inventory('+','.join(conditions)+')')
supply_source=(ROOT/'src/main/java/com/dynasty/expansion/ExpansionContent.java').read_text()
supplies=set(re.findall(r'"([^"]+)"',re.search(r'List.of\(([^)]*)\)\)\s*SUPPLIES\.put',supply_source)[1]))
assert len(supplies)==8
school={'zhenyue_blade':'guard','beichen_spear':'guard','liuyun_sword':'sword','chengying_sword':'sword','zhuxing_bow':'archer','fengling_bow':'archer','chiling_brush':'talisman','leifu_staff':'talisman'}
advanced={'beichen_spear','chengying_sword','fengling_bow','leifu_staff'}
mechanisms={'entity':'SecondarySpawnHooks placement; SecondaryMob AI/contactAttack/dropCustomDeathLoot; no quest hook unless listed','effect':'ExpansionEffects.apply and effect tick; EffectPresentation.added/removed/expired; no independent quest','armor':'EquipmentBehaviors.equipment/refresh/hurt/block/tick; DynastySetBonus; actual set-count EQUIP is intrinsic','accessory':'DynastyTrinkets.activeIds/tick/apply and EquipmentBehaviors.refresh/hurt; actual Curios EQUIP is intrinsic','interaction':'SmallInteractions.Site.use -> persisted site_<ID>_start/next/count/done -> DynastyAdvancements.award(cod4_<ID>)','weapon':'FTB native item-task detection; original weapon combat; no invented use restriction'}
gaps={'sword_scar_wall':'Moonlight sword dance and existing secret 28 still pending','battlefield_remnant':'Three unique coordinates only advance existing optional cod4 node; broader original main/side objective link remains pending','ghost_market_boat':'Original incense reward retained; TALK/DELIVER/merchant and existing secret 17 remain pending','wayside_tea_stall':'Original milk cleanse retained; poison-tea choice/clue/result and existing secret 19 still pending'}
for row in rows:
    ident,kind=row['CONTENT_ID'],row['TYPE'];found=list(links.get(ident,[]))
    if kind=='armor':
        for suffix in ['helmet','chestplate','leggings','boots']:found+=links.get(ident+'_'+suffix,[])
    stages=sorted({entry['chapter']+':'+entry['node'] for entry in found})
    row['CURRENT_TASK']=';'.join(sorted({entry['chapter'] for entry in found})) or 'NO_CURRENT_TASK_LINK'
    row['TASK_STAGE']=';'.join(stages) if stages else ('建议接 dynasty_story_03 环境调查；未创建节点' if kind=='entity' else '内在装备/效果行为，无独立节点')
    objectives=sorted({('CRAFT' if ident in supplies and entry['target'].startswith('cod4_obtain_') else 'INTERACT' if kind=='interaction' else 'OBTAIN' if entry['type']=='item' or entry['target'].startswith('cod4_obtain_') else entry['type'].upper())+':'+entry['target'] for entry in found})
    row['OBJECTIVE']=';'.join(objectives) or ('EQUIP (intrinsic; no quest)' if kind in ('accessory','armor') else 'APPLY/REMOVE (intrinsic; no quest)' if kind=='effect' else 'SPAWN/KILL (ecology/loot; no quest)' if kind=='entity' else 'NO_CURRENT_TASK_LINK')
    hooks=[]
    if any(entry['type']=='item' for entry in found):hooks.append('FTB native item detector (exact nodes above; real FTB acceptance pending)')
    if any(entry['target'].startswith('cod4_obtain_') for entry in found):hooks.append('ContentProgress.crafted(ItemCraftedEvent)' if ident in supplies else 'ContentProgress.login/tick/reconcile (inventory+armor+active Curios)')
    if kind in mechanisms:hooks.append(mechanisms[kind])
    if ident in school:hooks.append('DynastySchoolProgression.onKill -> canonical path rank; reconcile -> original attained milestones and recipe book; DynastyWeaponProgression.reward -> per-stack investment')
    row['PROGRESS_HOOK']='; '.join(hooks) or 'Vanilla registered recipe/crafting and item pickup; no custom task hook'
    if ident=='mortuary_room':row['PROGRESS_HOOK']='Site.use preserves original milk path; useMortuary -> original persisted Site timer/completion; native existing a_ji patient UUID/owner/site saved in entity NBT -> actual healing-potion effect -> SecretTracker original 29 payment/bottle/longyuan_sword/player-dimension claim; original cod4_mortuary_room advancement; no new NPC/task/claim engine'
    if ident=='puzzle_box':row['PROGRESS_HOOK']='Site.use -> usePuzzle -> original persisted Site start/next/count/done; SecretTracker.pressPuzzle -> original cod3_progress_30 north/east/south/west sequence with retained stand/sneak alternation -> original dimension/player secret_30 claim; cod4_puzzle_box advancement; discrete native progress deep-copied on death; no new quest engine'
    if ident=='ancient_well':row['PROGRESS_HOOK']='Site.use -> useWell -> original persisted Site start/next/completion; SecretTracker.deliverWellWater -> original cod3_progress_8 seven real water deliveries -> original dimension/player secret_8 claim; cod4_ancient_well advancement bridges existing node; no separate quest/claim engine'

    rewards=sorted({reward for entry in found for reward in entry['rewards']});mode=['FTB node rewards: '+(','.join(rewards) if rewards else 'none')]
    outputs=recipes.get(ident,[])
    if kind=='armor':outputs=sorted({recipe for suffix in ['helmet','chestplate','leggings','boots'] for recipe in recipes.get(ident+'_'+suffix,[])})
    if outputs:mode.append('registered recipe '+','.join(outputs)+'; craft/use not rank gated; JEI display client pending')
    discovery=sorted({record for recipe in outputs for record in discoveries.get(recipe,[])})
    if discovery:mode.append('recipe-book discovery: '+';'.join(discovery))
    if ident in school:
        path=school[ident];mode.append('SchoolProgression.reconcile: '+('rank>=3 OR owned branch discovers branch_'+ident+' and its _advance' if ident in advanced else 'rank>=1 OR owned base/branch discovers '+ident+' and original two school ornaments')+'; original rank 1/3/6/10 attained milestones backfilled; no FTB/rank craft or use prohibition')
    if ident in supplies:mode.append('ContentProgress.reconcile discovers cod4/'+ident+'; crafting advances legacy cod4_obtain ID; USE effects do not award craft records')
    if ident in uses:mode.append('actual recipe ingredient uses: '+','.join(sorted(uses[ident])))
    if kind=='interaction':
        gain={'wayside_shrine':'LUCK 2400 ticks','nameless_tomb':'LUCK 2400 ticks','old_weapon_rack':'tie_jian with 25% remaining durability','herb_spot':'2 tea','abandoned_armory':'1 qimen_gear','ancient_well':'clear YIN and SOUL','mortuary_room':'clear YIN and SOUL','wayside_tea_stall':'clear POISON','old_bellows':'3 iron nuggets + actual furnace assistance','broken_waterwheel':'2 copper coins + shared world_02 flag'}.get(ident,'2 copper coins')
        mode.append('actual one-time Site.use completion: '+gain+'; personal cod4_'+ident+' advancement; incomplete secret steps noted explicitly')
        if ident=='mortuary_room':mode.append('Original milk cleanse retained; loaded/proximity/alive/owner-bound existing living patient, actual native healing 4 HP and released original AI; >=2400 original deadline, one actual healing potion -> one bottle and original native secret 29 heirloom sword; old completion/cleanse not replayed, native claim preserved through clone; finite actor UUID/dimension-bound breathing/rescue cue, actual scene display pending')
        if ident=='puzzle_box':mode.append('N/E/S/W plus original stand/sneak/stand sequence; original 800-tick stages and >=2400 total deadline, fourth latch >=10 ticks; original secret 30 -> one blueprint; original three-count kept, two Site coins only on new completion; legacy done/claim never repay; finite interlocking-pin feedback and localized clue, actual display pending')
        if ident=='ancient_well':mode.append('7 actual water buckets -> 7 retained empty buckets; interval 515 ticks and total >=3600 ticks; original native secret 8 -> 1 jade once per player/dimension; legacy Site completion/counters retained, only missing native reward earned; no old cleanse/payment/reward replay')
    trade={'fox_pelt':'baibao_jin: 2 -> 6 copper','wolf_fang':'ba_tu: 2 -> 5 copper','python_gall':'hei_po: 1 -> 2 healing_salve','locust_dust':'hei_po: 2 -> 1 healing_salve','crab_shell':'huang_laohan: 2 -> 6 copper','kappa_scale':'huang_laohan: 2 -> 8 copper'}
    if ident in trade:
        remaining={'fox_pelt':'none; client/survival acceptance still pending','wolf_fang':'gray wolf fang ornament','crab_shell':'crab general ornament','kappa_scale':'none; actual client/survival acceptance pending','python_gall':'Hei Po gu brewing and cold-resistance wine','locust_dust':'poison smoke bomb, gu brewing and crop insect control'}
        mode.append('actual native material trade '+trade[ident]+'; remaining specific function: '+remaining[ident])
    infusions={'fox_pelt':'cold_ward, vanilla/Dynasty leather only: 20% freeze reduction + 8 fewer frozen ticks per second', 'wolf_fang':'existing shanxiao_claw third-hit pursuit on melee weapons; original family/cooldown', 'crab_shell':'existing retaliation on defensive equipment including sea_silk Dragon Palace light armor', 'kappa_scale':'existing water_ward on defensive equipment including original sea_pearl; native water combat trigger'}
    if ident=='kappa_scale':
        mode.append('Native VillagerProfession.FISHERMAN level>=2: actual 2 scales -> 1 emerald, 12 native stock, 5 villager XP, original restock/prices; native level-two trade pool and loaded/interacted old villager missing-offer append, all saved offers/uses/demand preserved; existing boatman trade retained')
        row['PROGRESS_HOOK']+='; ProgressionMerchant.fishermanTrades/ensureFishermanTrade -> native Villager/MerchantMenu transaction'
    if ident in infusions:
        mode.append('existing InfusionMenu paid transaction: 2 materials + 3 XP levels, one capacity; '+infusions[ident]+'; get_jade only existing gate; original 95 traits and foreign/growth/durability NBT retained')
        row['PROGRESS_HOOK']+='; InfusionMenu.request -> existing first_infusion; InfusionCombat equipped effect; native JEI category reads same traits (client display pending)'

    extra={'repeating_crossbow':'ContentProgress archer rank>=6 discovers cod4/repeating_crossbow','siege_crossbow':'ContentProgress archer rank>=10 discovers cod4/siege_crossbow','meteor_hammer':'official OR guard rank>=3 discovers; minister 64 copper, 8/day','mandarin_duck_axe':'official OR guard rank>=3 discovers; minister 64 copper, 8/day','rope_dart':'official OR guard rank>=3 discovery; minister same existing gating','flying_claw':'official OR guard rank>=3 discovery; minister same existing gating','sea_pearl':'entered_dragon_palace -> legacy Minister 48 copper, 8/day; native huang_laohan in Dragon Palace 48 copper, 8/NPC persisted stock'}
    if ident in extra:mode.append(extra[ident])
    if not outputs and not found:mode.append('intrinsic effects/loot only; no claimed recipe, shop or FTB unlock')
    row['REWARD_MODE']='; '.join(mode)
    row['MULTIPLAYER_CREDIT']='personal vanilla advancement; native FTB TeamData task progress; reward ownership follows original node team_reward/default_reward_team; real multiplayer pending' if found else 'wearer/target entity only; no quest credit'
    row['REPEATABLE']='false (existing one-time nodes)' if found else 'n/a (intrinsic behavior)'
    compat='Registry IDs and existing node IDs retained; completed advancement/FTB rewards not manually replayed; real old-world restart pending'
    if ident in supplies:compat+='; old completed legacy cod4_obtain kept; new progress only from actual crafting'
    elif kind=='interaction':compat+='; Player.PERSISTED_NBT_TAG/dynastyCod4 site records retained; no reset of timers or completed rewards'
    elif ident in school:compat+='; player dynastySchoolProgression cloned and rank milestones/recipe discoveries reconciled without rank/XP changes; smithing preserves dynastyWeaponGrowth NBT'
    elif kind=='accessory':compat+='; Curios state and original attribute UUIDs retained; owned school ornament recipes reconciled'
    elif any(entry['target'].startswith('cod4_obtain_') for entry in found):compat+='; inventory/armor/active Curios regrant missing impossible advancement only'
    row['OLD_SAVE_COMPAT']=compat
    notes=row['NOTES']
    if ident in ('fox_pelt','kappa_scale'):notes=re.sub(r'; Remaining material functions belong to existing Stage [^;]*; native workshop/NPC integration pending, not an invented new mainline','',notes)
    if ident=='mortuary_room':
        notes=re.sub(r'; Original milk cleanse retained; living victim/healing-potion delivery and existing secret 29 still pending','',notes)
        notes=re.sub(r'; Remaining Site/secret closure must reuse existing Stage [^;]*; no separate exported secret task node is present','',notes)
        if 'Native SecretTracker 29 verified' not in notes:notes+='; Native SecretTracker 29 verified: actual native living patient healing/payment/bottle/one-time heirloom, original milk/legacy completion and native entity reload; client scene/real old-world/network multiplayer pending'
    if ident=='puzzle_box':
        notes=re.sub(r'; Original stand/sneak sequence retained; expressed puzzle and existing secret 30 still pending','',notes)
        notes=re.sub(r'; Remaining Site/secret closure must reuse existing Stage [^;]*; no separate exported secret task node is present','',notes)
        if 'Native SecretTracker 30 verified' not in notes:notes+='; Native SecretTracker 30 verified: actual cardinal and posture predicates, original two-minute deadline, blueprint scope and legacy reward non-replay, discrete partial death clone; client/old-world/network multiplayer pending'
    if ident=='ancient_well':
        notes=re.sub(r'; Original seven counters retained; actual water delivery and existing secret 8 remain pending','',notes)
        notes=re.sub(r'; Remaining Site/secret closure must reuse existing Stage [^;]*; no separate exported secret task node is present','',notes)
        if 'Native SecretTracker 8 verified' not in notes:notes+='; Native SecretTracker 8 verified: loaded/proximity and real payment, original one-time persisted claim and clone, original three-minute deadline; actual visual/old-world/network multiplayer acceptance pending'
    if ident in gaps and gaps[ident] not in notes:notes+='; '+gaps[ident]
    if ident in gaps and stages:
        hint='Remaining Site/secret closure must reuse existing Stage '+','.join(stages)+'; no separate exported secret task node is present'
        if hint not in notes:notes+='; '+hint
    if ident in trade and ident not in ('fox_pelt','kappa_scale') and stages:
        hint='Remaining material functions belong to existing Stage '+','.join(stages)+'; native workshop/NPC integration pending, not an invented new mainline'
        if hint not in notes:notes+='; '+hint
    deps=';'.join(sorted({entry['node']+'<-'+(','.join(entry['deps']) or 'none') for entry in found}))
    if deps:notes=re.sub(r';? ?FTB dependencies:.*','',notes)+'; FTB dependencies:'+deps
    row['NOTES']=notes
out=io.StringIO();writer=csv.DictWriter(out,fieldnames=fields,delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(rows);MAP.write_text(out.getvalue())
assert len(list(csv.DictReader(io.StringIO(out.getvalue()),delimiter='\t')))==len(rows)
print(json.dumps({'rows':len(rows),'real_ftb_nodes':quest_count,'rows_with_actual_task_targets':sum(r['CURRENT_TASK']!='NO_CURRENT_TASK_LINK' for r in rows),'no_new_quests':True,'client_and_real_old_world_acceptance':'PENDING'},ensure_ascii=False))
