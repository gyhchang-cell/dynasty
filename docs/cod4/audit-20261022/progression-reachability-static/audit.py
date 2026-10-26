"""Read-only production analysis. All writes are confined beside this script."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
import json,re,hashlib,collections,datetime,math
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
sys.path.insert(0,str(ROOT/'tools/art'))
from quest_snbt import list_compounds,object_id
assert ROOT.name=='dynasty'
inputs={}
def text(p):
 p=Path(p);inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest();return p.read_text()
def read(p):return json.loads(text(p))
def save(n,d):
 p=OUT/n;assert p.parent==OUT;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def ref(p,line=None):return {'path':str(p.relative_to(ROOT)),'line':line,'sha256':inputs.get(str(p.relative_to(ROOT)))}
def scc(graph):
 serial=0;indices={};low={};stack=[];on=set();result=[]
 def visit(v):
  nonlocal serial
  indices[v]=low[v]=serial;serial+=1;stack.append(v);on.add(v)
  for w in graph.get(v,[]):
   if w not in indices:visit(w);low[v]=min(low[v],low[w])
   elif w in on:low[v]=min(low[v],indices[w])
  if low[v]==indices[v]:
   part=[]
   while True:
    w=stack.pop();on.remove(w);part.append(w)
    if w==v:break
   if len(part)>1 or v in graph.get(v,[]):result.append(sorted(part))
 for v in list(graph):
  if v not in indices:visit(v)
 return sorted(result,key=lambda a:(-len(a),a))
# Current FTB dependency graph, tasks and rewards remain separate.
quests={};duplicate=[]
for p in sorted((ROOT/'modpack/config/ftbquests/quests/chapters').glob('*.snbt')):
 raw=text(p)
 for b in list_compounds(raw,'quests'):
  inner='\n'.join(x[2:] if x.startswith('\t\t') else x for x in b.splitlines());qid=object_id(b).lower();dep=re.search(r'^\tdependencies:\s*\[([^\]]*)\]',inner,re.M);title=re.search(r'^\ttitle:\s*"([^"]*)"',inner,re.M)
  tasks=[];rewards=[]
  for field,dest in [('tasks',tasks),('rewards',rewards)]:
   for x in list_compounds(inner,field):
    kind=re.search(r'\btype:\s*"([^"]+)"',x);item=re.search(r'\bitem:\s*(?:\{\s*id:\s*)?"([a-z_]+:[a-z0-9_./-]+)"',x);count=re.search(r'\bcount:\s*(\d+)',x);adv=re.search(r'\badvancement:\s*"([^"]+)"',x)
    dest.append({'id':object_id(x),'type':kind[1] if kind else None,'item':item[1] if item else None,'count':int(count[1]) if count else 1,'advancement':adv[1] if adv else None,'consume_items_explicit':bool(re.search(r'consume_items:\s*true',x)),'raw':x})
  if qid in quests:duplicate.append(qid)
  quests[qid]={'id':qid,'title':title[1] if title else '', 'chapter':p.stem,'dependencies':[i.lower() for i in re.findall(r'"([0-9a-fA-F]{16})"',dep[1])] if dep else [],'tasks':tasks,'rewards':rewards,'source':ref(p,raw.count('\n',0,raw.index(b))+1)}
def ancestors(q):
 seen=set();todo=list(quests[q]['dependencies'])
 while todo:
  x=todo.pop()
  if x not in seen:seen.add(x);todo.extend(quests.get(x,{}).get('dependencies',[]))
 return seen
def chain(q):return [{'id':x,'title':quests[x]['title'],'source':quests[x]['source']} for x in sorted(ancestors(q)) if x in quests]
qcycles=scc({q:v['dependencies'] for q,v in quests.items()})
missing=[{'quest':q,'missing':x} for q,v in quests.items() for x in v['dependencies'] if x not in quests]
# Ingredient groups preserve alternatives/tags; pattern counts repeated symbols.
def ingredient(v):
 if isinstance(v,list):return sorted(set(x for a in v for x in ingredient(a)))
 if isinstance(v,dict):
  if 'item' in v:return [v['item']]
  if 'tag' in v:return ['#'+v['tag']]
 return []
recipes={};produced=collections.defaultdict(list);uses=collections.defaultdict(list)
for p in sorted((ROOT/'src/main/resources/data/dynasty/recipes').rglob('*.json')):
 d=read(p);rid='dynasty:'+str(p.relative_to(ROOT/'src/main/resources/data/dynasty/recipes').with_suffix(''));r=d['result'];item=r['item'] if isinstance(r,dict) else r
 if d['type']=='minecraft:crafting_shaped':groups=[ingredient(d['key'][c]) for row in d['pattern'] for c in row if c!=' ']
 elif d['type']=='minecraft:crafting_shapeless':groups=[ingredient(v) for v in d['ingredients']]
 elif d['type']=='minecraft:smithing_transform':groups=[ingredient(d[k]) for k in ['template','base','addition'] if ingredient(d.get(k))]
 else:groups=[ingredient(d.get('ingredient',{}))]
 counts=collections.Counter(g[0] for g in groups if len(g)==1)
 recipes[rid]={'id':rid,'type':d['type'],'result':item,'count':r.get('count',1) if isinstance(r,dict) else 1,'ingredient_groups':groups,'exact_singleton_cost':dict(counts),'source':ref(p),'definition':d};produced[item].append(rid)
 for g in groups:
  for i in g:uses[i].append(rid)
# Structured loot including conditions/functions, then require a separate provider binding.
java={p:text(p) for p in sorted((ROOT/'src/main/java/com/dynasty').rglob('*.java')) if 'GameTest' not in p.name and '/client/' not in str(p)}
loot={};loot_by_item=collections.defaultdict(list)
def walk(v,trail=()):
 if isinstance(v,dict):
  yield trail,v
  for k,x in v.items():yield from walk(x,trail+(k,))
 elif isinstance(v,list):
  for i,x in enumerate(v):yield from walk(x,trail+(i,))
mods={p:read(p) for p in sorted((ROOT/'src/main/resources/data/dynasty/forge/biome_modifier').glob('*.json'))}
configs={p:read(p) for p in sorted((ROOT/'src/main/resources/data/dynasty/worldgen/configured_feature').glob('*.json'))}
placed={p:read(p) for p in sorted((ROOT/'src/main/resources/data/dynasty/worldgen/placed_feature').glob('*.json'))}
structures={p:read(p) for p in sorted((ROOT/'src/main/resources/data/dynasty/worldgen/structure').glob('*.json'))}
structure_sets={p:read(p) for p in sorted((ROOT/'src/main/resources/data/dynasty/worldgen/structure_set').glob('*.json'))}
biomes={p:read(p) for p in sorted((ROOT/'src/main/resources/data/dynasty/worldgen/biome').glob('*.json'))}
dimensions={p:read(p) for p in sorted((ROOT/'src/main/resources/data/dynasty/dimension').glob('*.json'))}
def bindings(kind,name):
 out=[]
 if kind=='entities':
  for p,d in mods.items():
   if any(v.get('type')=='dynasty:'+name for _,v in walk(d)):out.append({'kind':'BIOME_SPAWN_ENTRY_CONDITIONAL','source':ref(p),'definition':d})
  for p,d in biomes.items():
   if any(v.get('type')=='dynasty:'+name for _,v in walk(d)):
    ds=[{'source':ref(dp),'definition':dd} for dp,dd in dimensions.items() if any(v.get('biome')=='dynasty:'+p.stem for _,v in walk(dd))]
    out.append({'kind':'DIMENSION_BIOME_SPAWN_ENTRY_CONDITIONAL','biome':ref(p),'spawn_definition':d.get('spawners'),'dimension_bindings':ds,'requires':'real dimension access, vanilla spawn placement/caps, not a spawn guarantee'})
 if kind=='blocks':
  for p,d in configs.items():
   if any(v.get('Name')=='dynasty:'+name for _,v in walk(d)):
    feature='dynasty:'+p.stem
    for pp,pd in placed.items():
     if pd.get('feature')!=feature:continue
     for mp,md in mods.items():
      fs=md.get('features',[]);fs=[fs] if isinstance(fs,str) else fs
      if 'dynasty:'+pp.stem in fs:out.append({'kind':'CONFIGURED_PLACED_BIOME_CHAIN','configured':ref(p),'configured_definition':d,'placed':ref(pp),'placement':pd,'biome_modifier':ref(mp),'biome_definition':md})
 if kind=='chests':
  for p,raw in java.items():
   for no,line in enumerate(raw.splitlines(),1):
    if ('"chests/'+name+'"' in line or '"dynasty:chests/'+name+'"' in line or (re.search(r'\b(?:chest|loot)\(',line) and '"'+name+'"' in line)):
     out.append({'kind':'JAVA_CHEST_BINDING_REQUIRES_CALLER_WORLDGEN','source':ref(p,no),'line':line.strip()})
 return out
for p in sorted((ROOT/'src/main/resources/data/dynasty/loot_tables').rglob('*.json')):
 d=read(p);rid='dynasty:'+str(p.relative_to(ROOT/'src/main/resources/data/dynasty/loot_tables').with_suffix(''));parts=rid.split(':',1)[1].split('/');entries=[]
 for trail,v in walk(d):
  if v.get('type')=='minecraft:item':entries.append({'item':v['name'],'json_pointer':'/'+ '/'.join(map(str,trail)),'definition':v});loot_by_item[v['name']].append(rid)
 loot[rid]={'id':rid,'source':ref(p),'entries':entries,'definition':d,'provider_bindings':bindings(parts[0],'/'.join(parts[1:]))}
# Known production Java grants: parse actual registry field registrations, then explicit drop calls.
constants={}
for p,raw in java.items():
 for m in re.finditer(r'\b([A-Z][A-Z0-9_]*)\s*=\s*(?:[A-Za-z0-9_]+\.)?(?:basic|armor|sword|bow|crossbow|weapon|simple|item|register)\(\s*"([a-z0-9_]+)"',raw):constants[p.stem+'.'+m[1]]='dynasty:'+m[2]
java_sources=collections.defaultdict(list)
p=ROOT/'src/main/java/com/dynasty/DynastyBossDrops.java';raw=java[p]
case=None
for no,line in enumerate(raw.splitlines(),1):
 m=re.search(r'case "([a-z_]+)"',line)
 if m:case=m[1]
 for m in re.finditer(r'drop\(event,\s*([A-Za-z0-9_.]+),\s*(\d+),\s*rand,\s*([0-9.]+)F',line):
  item=constants.get(m[1]);
  if item:java_sources[item].append({'kind':'JAVA_ENTITY_DROP','entity':'dynasty:'+case,'count_range':[1,int(m[2])],'chance':float(m[3]),'source':ref(p,no),'spawn_entry_bindings':bindings('entities',case)})
p=ROOT/'src/main/java/com/dynasty/DynastyWeaponGifts.java'
for no,line in enumerate(java[p].splitlines(),1):
 for m in re.finditer(r'grant\(player,\s*"([a-z_]+)"',line):java_sources['dynasty:'+m[1]].append({'kind':'CONDITIONAL_WEAPON_GIFT','source':ref(p,no),'condition_source':ref(p),'note':'rank12/17, five distinct counted bosses, or daytime phoenix; not a free seed'})
# Exact shops and their actual conditions, intentionally not a global free-item seed.
shopfile=ROOT/'src/main/java/com/dynasty/cod3/DynastyNpcEntity.java'
shops=[]
for role,goods in {'lao_chen':['blueprint','refined_steel'],'han_chong':['mu_mao','bamboo_slip'],'baibao_jin':['tea','silk','jade'],'hei_po':['healing_salve','tea'],'xiaoyuanzi':['healing_salve','tea']}.items():
 for i,item in enumerate(goods):shops.append({'role':role,'output':'dynasty:'+item,'count':1,'input':{'dynasty:copper_coin':8+i*4},'max_uses':8,'conditions':['find living existing NPC within6blocks','available stock and actual native payment'],'source':ref(shopfile,134)})
for role,item,flag in [('lao_chen','blueprint','world_02'),('mo_jizi','blueprint','world_02'),('han_chong','refined_steel','world_01'),('baibao_jin','silver_ingot','world_09')]:shops.append({'role':role,'output':'dynasty:'+item,'count':1,'input':{'dynasty:copper_coin':12},'max_uses':8,'conditions':['worldChanged '+flag,'NPC alive/reachable/stock'],'source':ref(shopfile,77)})
for role,material,amount,coins in [('baibao_jin','fox_pelt',2,6),('ba_tu','wolf_fang',2,5),('huang_laohan','crab_shell',2,6),('huang_laohan','kappa_scale',2,8)]:shops.append({'role':role,'output':'dynasty:copper_coin','count':coins,'input':{'dynasty:'+material:amount},'max_uses':16,'conditions':['natural material','existing NPC reachable/stock'],'source':ref(shopfile,109)})
shops.append({'role':'huang_laohan','output':'dynasty:sea_pearl','count':1,'input':{'dynasty:copper_coin':48},'max_uses':8,'conditions':['dragon_palace dimension','NPC alive/reachable/stock'],'source':ref(shopfile,123)})
shop_index=collections.defaultdict(list)
for s in shops:shop_index[s['output']].append(s)
quest_items=collections.defaultdict(list);quest_rewards=collections.defaultdict(list)
for q,v in quests.items():
 for t in v['tasks']:
  if t['item']:quest_items[t['item']].append(q)
  elif t['advancement'] and t['advancement'].startswith('dynasty:cod4_obtain_'):quest_items['dynasty:'+t['advancement'].split('cod4_obtain_',1)[1]].append(q)
 for r in v['rewards']:
  if r['item']:quest_rewards[r['item']].append({'quest':q,'reward':r,'dependencies':v['dependencies']})
# Native-classified 181 equipment snapshot is re-bound to current registrations/recipes, no new client.
oldpath=ROOT/'tools/cod4/journey-acceptance/old-equipment-utility.json';old=read(oldpath);equipment={r['item']:r for r in old['items']}
registration=[]
for item,row in equipment.items():
 reg=row.get('registration') or {};p=ROOT/reg.get('path','')
 if p.is_file():text(p)
 registration.append({'item':item,'source':reg.get('path'),'previous_sha256':reg.get('sha256'),'current_sha256':inputs.get(reg.get('path')),'matches_prior_classification_source':inputs.get(reg.get('path'))==reg.get('sha256')})
allitems=set(equipment)|set(produced)
for r in recipes.values():
 for g in r['ingredient_groups']:allitems.update(g)
sources={}
for item in sorted(allitems):
 sources[item]={'recipes':produced.get(item,[]),'loot_tables':[{'id':l,'provider_binding_count':len(loot[l]['provider_bindings'])} for l in loot_by_item.get(item,[])],'java_grants':java_sources.get(item,[]),'shops':shop_index.get(item,[]),'quest_reward_sources':quest_rewards.get(item,[]),'quest_objectives':quest_items.get(item,[])}
# SCC membership does not prove deadlock: all conversion alternatives stay visible.
ig={i:{j for rid in produced.get(i,[]) for g in recipes[rid]['ingredient_groups'] for j in g if not j.startswith('#')} for i in produced}
icycles=scc(ig)
cycle_reports=[]
for c in icycles:
 cs=set(c);escapes=[]
 for i in c:
  for rid in produced.get(i,[]):
   if all(any(v not in cs for v in g) for g in recipes[rid]['ingredient_groups']):escapes.append({'item':i,'recipe':rid,'kind':'RECIPE_WITH_NO_MANDATORY_INTERNAL_INGREDIENT'})
  for l in loot_by_item.get(i,[]):escapes.append({'item':i,'loot':l,'kind':'LOOT_POTENTIAL_EXTERNAL_SEED','provider_binding_count':len(loot[l]['provider_bindings'])})
  for s in shop_index.get(i,[]):escapes.append({'item':i,'shop':s,'kind':'CONDITIONAL_SHOP_EXTERNAL_CANDIDATE'})
  for s in java_sources.get(i,[]):escapes.append({'item':i,'java':s,'kind':'CONDITIONAL_JAVA_EXTERNAL_CANDIDATE'})
 cycle_reports.append({'items':c,'external_candidates':escapes,'status':'HAS_EXTERNAL_OR_ALTERNATIVE_CANDIDATES_NOT_PROVEN_DEADLOCK' if escapes else 'NO_INDEXED_EXIT_REQUIRES_MANUAL_REVIEW_NOT_YET_UNOBTAINABLE'})
# Per-item expanded recipe-only cost is a declared witness, not least-time/global least-cost proof.
def expand(item,n=1,path=()):
 if item.startswith('#') or item not in produced:return collections.Counter({item:n}),[],[]
 if item in path:return None,[],['cycle:'+item]
 options=sorted(produced[item],key=lambda rid:(rid!='dynasty:'+item.split(':')[1],len(recipes[rid]['ingredient_groups']),rid))
 for rid in options:
  r=recipes[rid];batches=math.ceil(n/r['count']);total=collections.Counter();steps=[];warnings=[];valid=True
  for g in r['ingredient_groups']:
   resolved=False
   for v in g:
    cost,st,w=expand(v,batches,path+(item,))
    if cost is not None:total.update(cost);steps+=st;warnings+=w;resolved=True;break
   if not resolved:valid=False;break
  if valid:return total,steps+[{'item':item,'recipe':rid,'requested':n,'batches':batches,'produced':batches*r['count'],'actual_recipe_groups':r['ingredient_groups']}],warnings
 return None,[],['NO_ACYCLIC_RECIPE_ONLY_WITNESS:'+item]
item_rows=[]
for item,row in equipment.items():
 cost,steps,w=expand(item)
 qr=[];inversions=[]
 for q in quest_items.get(item,[]):
  ancestor_equipment=sorted({t['item'] for a in ancestors(q) if a in quests for t in quests[a]['tasks'] if t['item'] in equipment})
  qr.append({'quest':q,'chapter':quests[q]['chapter'],'title':quests[q]['title'],'ancestors':sorted(ancestors(q)),'earlier_equipment_objectives':ancestor_equipment,'source':quests[q]['source']})
  downstream={recipes[rid]['result'] for rid in uses.get(item,[])}
  for x in sorted(downstream&set(ancestor_equipment)):inversions.append({'quest':q,'successor_required_in_ancestor':x,'interpretation':'Objective ordering inversion only; crafting/use are not automatically gated by this quest.'})
 item_rows.append({'item':item,'category':row['category'],'acquisition_source_index':sources[item],'quests':qr,'direct_recipe_costs':[recipes[rid] for rid in produced.get(item,[])],'recipe_only_leaf_cost_witness':dict(cost) if cost is not None else None,'recipe_only_steps':steps,'cost_limits':'Chosen acyclic recipe-only witness, batches rounded per subtree; no global leftovers optimisation, no fuel/workstation/tool/time estimate, alternatives/sources may be cheaper. Leaf source conditions must be checked separately.','unresolved_cost':w,'successor_recipe_uses':[{'recipe':rid,'output':recipes[rid]['result'],'cost':recipes[rid]['exact_singleton_cost']} for rid in uses.get(item,[])],'objective_order_inversions':inversions,'prior_utility_classification':row['classification'],'survival_or_replacement_time_proven':False})
# Strongly linked selected six-stage route, retaining all four armor slots through full inventory.
stage_items={'开局':['mu_mao','shi_ge','cloth_chestplate','bamboo_chestplate'],'早期':['tong_dao','tie_jian','sword_bronze','bronze_chestplate','qimen_gear','qimen_cable','repeating_crossbow'],'中期':['sword_silver','sword_jade','jade_chestplate','silver_chestplate','silk_pouch'],'中后期':['liuyun_sword','zhenyue_blade','siege_crossbow','rope_dart','meteor_hammer','mandarin_duck_axe','flying_claw'],'后期':['juque_sword','qinglong_dao','xuanwu_blade','dragon_scale_chestplate','draco_king_chestplate'],'终盘':['xuantian_chestplate','hunyuan_chestplate','hongmeng_chestplate','beidou_chestplate','xuantian_axe','supreme_sword']}
stages=[]
for stage,ids in stage_items.items():
 rr=[]
 for short in ids:
  item='dynasty:'+short
  if item not in sources:rr.append({'item':item,'status':'NAME_NOT_IN_INDEX_DO_NOT_INVENT_EQUIVALENCE'});continue
  leaves,steps,w=expand(item);rr.append({'item':item,'source':sources[item],'cost':dict(leaves) if leaves is not None else None,'recipe_steps':steps,'leaf_source_records':{leaf:sources.get(leaf,{'external_namespace_or_tag':leaf}) for leaf in (leaves or {})},'quest_paths':[{'node':quests[q],'ancestor_chain':chain(q)} for q in quest_items.get(item,[])],'unresolved':w,'status':'STATIC_CONDITIONAL_PATHS_ONLY'})
 stages.append({'stage':stage,'items':rr,'natural_play_verified':False})
# Track every recursive dependency for equipment; no unknown root may be silently free.
closure=set(equipment);todo=list(closure)
while todo:
 item=todo.pop()
 for rid in produced.get(item,[]):
  for g in recipes[rid]['ingredient_groups']:
   for dep in g:
    if dep not in closure:closure.add(dep);todo.append(dep)
leaves=sorted(x for x in closure if x.startswith('dynasty:') and not produced.get(x))
leaf_rows=[]
for i in leaves:
 src=sources[i];positive=bool(src['java_grants'] or src['shops'] or any(l['provider_binding_count'] for l in src['loot_tables']))
 leaf_rows.append({'item':i,'source':src,'status':'CONDITIONAL_SOURCE_ADAPTER_FOUND' if positive else 'MISSING_INDEXED_NATURAL_PROVIDER_REVIEW_REQUIRED','not_a_proven_unobtainable_item':True})
refpath=ROOT/'docs/cod4/audit-20261022/quest-reference-1000.json';reference=read(refpath)
summary={'status':'STATIC_ONLY_NO_SURVIVAL_OR_2_3H_CERTIFICATION','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'write_scope':str(OUT.relative_to(ROOT))+'/**','production_changes':[],'game_clients_started':0,'existing_survival_clients':{'run01_exit':0,'run02_exit':0,'source':'Read pre-existing exit-code files only; no further UI or launch'},'quest_nodes':len(quests),'quest_duplicate_ids':duplicate,'quest_missing_dependencies':missing,'quest_cycles':qcycles,'recipes':len(recipes),'equipment_denominator':len(equipment),'equipment_categories':dict(collections.Counter(r['category'] for r in equipment.values())),'equipment_registration_source_drift':[r for r in registration if not r['matches_prior_classification_source']],'recipe_scc_count':len(cycle_reports),'recipe_cycles_without_indexed_external_candidate':[r['items'] for r in cycle_reports if not r['external_candidates']],'recursive_dependency_item_count':len(closure),'nonrecipe_dynasty_leaf_count':len(leaves),'source_provider_review_candidates':[r['item'] for r in leaf_rows if r['status'].startswith('MISSING')],'objective_order_inversions':[{'item':r['item'],**x} for r in item_rows for x in r['objective_order_inversions']],'research':{'path':str(refpath.relative_to(ROOT)),'sha256':inputs[str(refpath.relative_to(ROOT))],'count':len(reference['sites']),'semantic_unique':len({s['semantic_sha256'] for s in reference['sites']}),'scope':'Existing same acquisition/predecessor/reward audit research, read-only reuse; no new implementation or1000 playthroughs claimed.'},'limitations':['Loot presence is not physical encounter; entity/provider paths remain conditional.','External Minecraft ingredients/tags are named, not assumed freely available or stage appropriate.','Java static index is targeted, not a complete abstract interpreter; missing indexed provider is a review gap, never automatic impossibility.','FTB dependencies normally gate objective submission/rewards, not equipment crafting/use; no inferred global recipe gates.','No real2-3h timing or newly completed TODO claim.']}
save('quest-graph.json',quests);save('recipes.json',recipes);save('loot-provider-index.json',loot);save('java-and-shop-sources.json',{'java_grants':dict(java_sources),'shops':shops});save('item-source-index.json',sources);save('equipment-coverage.json',{'denominator':len(equipment),'registration_source_binding':registration,'items':item_rows});save('recipe-cycles.json',cycle_reports);save('six-stage-paths.json',stages);save('nonrecipe-material-sources.json',leaf_rows);save('summary.json',summary);save('input-sha256.json',inputs)
print(json.dumps({k:summary[k] for k in ['quest_nodes','quest_missing_dependencies','quest_cycles','recipes','equipment_denominator','equipment_registration_source_drift','recipe_scc_count','recipe_cycles_without_indexed_external_candidate','nonrecipe_dynasty_leaf_count','source_provider_review_candidates','objective_order_inversions']},ensure_ascii=False,indent=2))
