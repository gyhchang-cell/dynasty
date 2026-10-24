"""Read frozen production sources; write an explicit 30-species / 10-material provenance matrix."""
from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
F=BASE/'.work/frozen'
OUT=ROOT/'docs/cod4/audit-20261022/ecology-acceptance'
R=F/'src/main/resources/data/dynasty'
def read(p):return json.loads(p.read_text())
roster=read(ROOT/'docs/cod4/secondary-roster.json')
hooks=(F/'src/main/java/com/dynasty/expansion/SecondarySpawnHooks.java').read_text()
constraints={}
for line in hooks.splitlines():
 if 'case ' in line and '->' in line:
  ids,expr=line.split('->',1)
  for name in re.findall(r'"([a-z_]+)"',ids):constraints[name]=expr.strip()
structure_sets={}
for p in (R/'worldgen/structure_set').glob('*.json'):
 data=read(p)
 for e in data.get('structures',[]):structure_sets.setdefault(e['structure'],[]).append({'set':p.stem,'placement':data['placement']})
rows=[]
for mob in roster:
 ident=mob['id'];modifier=R/f'forge/biome_modifier/secondary_{ident}.json';biomes=R/f'tags/worldgen/biome/secondary/{ident}.json';loot=R/f'loot_tables/entities/{ident}.json'
 rows.append({**mob,'biome_modifier':read(modifier) if modifier.exists() else None,'biome_tag':read(biomes) if biomes.exists() else None,'extra_habitat_gate':constraints.get(ident,'See SecondarySpawnHooks global / species predicates'),'loot_table':read(loot) if loot.exists() else None,'native_natural_world_status':'SEE_RUNTIME_POSITION_MATRIX; natural spawn and drop not inferred from registration'})
materials=[]
request=(ROOT/'docs/cod4/request.txt').read_text().split('COD4-11 材料体系',1)[1].split('COD4-12',1)[0]
for line in request.splitlines():
 cells=[v.strip() for v in line.strip('|').split('|')]
 if len(cells)!=6 or not re.fullmatch('[a-z_]+',cells[1]):continue
 ident=cells[1];sources=[]
 for mob in rows:
  loot=mob['loot_table']
  if loot and 'dynasty:'+ident in json.dumps(loot):sources.append({'species':mob['id'],'conditions_and_entries':loot})
 materials.append({'id':ident,'name':cells[0],'requested_source':cells[5],'existing_entity_loot_sources':sources,'natural_kill_drop_verified':False})
tags=[]
for name in ['ecology/ruined_villages','blueprint/ghost_sites','ecology/tombs','secondary/ruins','ecology/roads','blueprint/clockwork_dog_sites','blueprint/mining_spider_sites']:
 data=read(R/f'tags/worldgen/structure/{name}.json')
 tags.append({'tag':name,'values':data['values'],'natural_structure_sets':{sid:structure_sets.get(sid,[]) for sid in data['values']}})
for t in tags:
 t['structure_biome_constraints']={}
 for name in t['values']:
  key=name.split(':',1)[1];p=R/'worldgen/structure'/f'{key}.json'
  if not p.exists():continue
  st=read(p);v={k:st.get(k) for k in ['type','biomes','step']};tag=st.get('biomes')
  if isinstance(tag,str) and tag.startswith('#dynasty:'):
   q=R/'tags/worldgen/biome'/f"{tag.split(':',1)[1]}.json"
   if q.exists():v['biome_tag_values']=read(q)['values']
  t['structure_biome_constraints'][name]=v
result={'frozen_manifest_sha256':hashlib.sha256((OUT/'frozen-source-sha256.json').read_bytes()).hexdigest(),'denominators':{'species':len(rows),'materials':len(materials),'structure_tags':len(tags)},'species':rows,'materials':materials,'structure_tags':tags,'known_gap':'ruined_villages empty; ghost_sites is ruined_battlefield; no dedicated abandoned-village/mortuary/graveyard/ghost-market proof inferred from these aliases'}
assert len(rows)==30 and len(materials)==10
(OUT/'source-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(OUT/'species-source-matrix.tsv').write_text('id\trequested_habitat\tadditional_gate\tnatural_spawn_drop\n'+''.join(f"{m['id']}\t{m['spawn']}\t{m['extra_habitat_gate']}\tPENDING_RUNTIME_AND_NATURAL_DROP\n" for m in rows))
print(json.dumps(result['denominators']))
