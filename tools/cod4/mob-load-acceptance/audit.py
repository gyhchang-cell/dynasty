"""Read actual runtime resources; count declared cuboids/quads and retain provenance.
Native baked counts (when present) are checked against declarations. No asset writes.
"""
from pathlib import Path
import hashlib,json,zipfile,csv
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/mob-load-acceptance';O.mkdir(parents=True,exist_ok=True)
A=R/'src/main/resources/assets/dynasty';OLD=R/'docs/art/secondary-cuboid-v1/source'
# Shape comparators are explicit QA proposals: SecondaryMob inherits PathfinderMob,
# NOT any vanilla mob/model. Non-equivalent forms must not become an invented base.
COMPARE={
'famished_refugee':('VILLAGER','human biped'), 'bandit_thug':('ZOMBIE','hostile human biped'),
'night_watchman':('VILLAGER','human biped'),'swindler':('VILLAGER','human biped'),'herb_picker':('VILLAGER','human biped'),
'paper_cut_child':('ZOMBIE','biped; flat paper anatomy not equivalent'),
'red_fox':('FOX','same animal'),'gray_wolf':('WOLF','same animal'),'wild_boar':('PIG','same porcine body plan'),
'golden_leopard':('OCELOT','feline body plan'),'clockwork_rat':('FOX','quadruped proxy only; no vanilla rat'),
'giant_python':('SILVERFISH','elongated ground proxy only; no vanilla snake'),
'stone_worm':('SILVERFISH','segmented ground proxy only; no vanilla worm'),
'corpse_beetle':('SPIDER','arthropod proxy only; six vs eight legs'),
'venom_scorpion':('SPIDER','arthropod proxy only; no vanilla scorpion'),
'crab_soldier':('SPIDER','arthropod proxy only; no vanilla crab'),
'locust_swarm':('BAT','flying small-creature proxy only; one swarm entity vs one bat'),
'bat_demon':('BAT','same animal'),'gray_falcon':('PARROT','bird proxy; no vanilla falcon'),
'jingwei_bird':('PARROT','bird body plan'),'wooden_magpie':('PARROT','bird body plan; mechanical proxy'),
'river_imp':('DROWNED','aquatic humanoid proxy'), 'drowning_ghost':('DROWNED','aquatic undead humanoid'),
'carp_spirit':('COD','fish body plan'),'snail_maiden':('TURTLE','shelled aquatic proxy only; no vanilla snail'),
'lantern_ghost':('VEX','flying ghost proxy; no vanilla lantern ghost'),
'paper_money_ghost':('VEX','flying ghost proxy'),'wandering_spirit':('VEX','flying ghost proxy'),
'tree_spirit':('IRON_GOLEM','large upright guardian proxy; no vanilla tree spirit'),
'stone_sprite':('RAVAGER','heavy quadruped proxy; no vanilla stone sprite')}
roster=json.loads((R/'docs/cod4/secondary-roster.json').read_text());assert len(roster)==30
nativepath=O/'run-02/native-geometry.json';native=json.loads(nativepath.read_text()) if nativepath.exists() else None
rows=[]
for spec in roster:
 id=spec['id'];p=A/f'geo/secondary/{id}.geo.json';g=json.loads(p.read_text())['minecraft:geometry'][0];cs=[c for b in g['bones'] for c in b.get('cubes',[])];q=sum(len(c['uv']) if isinstance(c['uv'],dict) else 6 for c in cs)
 oldg=json.loads((OLD/f'{id}.geo.json').read_text())['minecraft:geometry'][0];oldc=[c for b in oldg['bones'] for c in b.get('cubes',[])];oldq=sum(len(c['uv']) if isinstance(c['uv'],dict) else 6 for c in oldc)
 unused_geo=None
 if id in ['bandit_thug','night_watchman']:
  unused_geo={'path':str(p.relative_to(R)),'cuboids':len(cs),'quads':q}
  p=A/f'models/entity/steve_fighters/{id}.json';definition=json.loads(p.read_text());cs=definition['parts'];q=6*len(cs)
 base,why=COMPARE[id];v=native['vanilla'][base] if native else None
 frozen=R/'tools/cod4/mob-load-acceptance/.work/frozen'/p.relative_to(R)
 assert frozen.read_bytes()==p.read_bytes(),f'Current runtime model changed during QA: {id}'
 row={'id':id,'name':spec['name'],'cuboids':len(cs),'declared_quads':q,'original_cuboids':len(oldc),'original_quads':oldq,'original_delta_quads':q-oldq,'proposed_vanilla_comparator':base,'comparison_reason':why,'base_status':'QA morphological comparator, NOT inherited or project-declared corresponding base','vanilla_cuboids':v['cuboids'] if v else None,'vanilla_quads':v['quads'] if v else None,'delta_to_comparator':q-v['quads'] if v else None,'unused_geo':unused_geo,'source':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 if native:
  n=native['secondary'][id];assert n['cuboids']==len(cs) and n['quads']==q,(id,n,q);row['native']=n
 rows.append(row)
sourcejar=next((Path.home()/'.gradle/caches/forge_gradle/minecraft_user_repo').rglob('forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar'))
sourceout=O/'vanilla-source';sourceout.mkdir(exist_ok=True)
with zipfile.ZipFile(sourcejar) as z:
 for name in ['HumanoidModel','VillagerModel','ZombieModel','FoxModel','WolfModel','PigModel','OcelotModel','IronGolemModel','SilverfishModel','VexModel','DrownedModel','CodModel','TurtleModel','SpiderModel','BatModel','ParrotModel','RavagerModel']:
  n='net/minecraft/client/model/'+name+'.java';(sourceout/(name+'.java')).write_bytes(z.read(n))
 for n in ['net/minecraft/client/model/geom/ModelPart.java','net/minecraft/client/model/geom/LayerDefinitions.java']:(sourceout/Path(n).name).write_bytes(z.read(n))
report={'status':'NOT COMPLETE','method':'Active final-bound model only: JSON geo face entries or Steve parts*6, reconciled to native GeckoLib GeoCube non-null quads when runtime available. Vanilla native ModelPart.visit cuboids and Cube.polygons; body layers only, all baked cubes, not texture size/file size. Quad != triangle; two triangles per quad. Hidden/internal declared quads still cost unless actually omitted; no automatic opacity assumptions.','renderer_source':'src/main/java/com/dynasty/expansion/ExpansionClient.java','runtime_renderer':'Final live entity dispatcher: bandit_thug/night_watchman use SteveFighterRenderer registered LOWEST by SteveFighterBindings; remaining28 use ExpansionClient.Renderer/GeoEntityRenderer. Steve body resource parts bake one six-face Cube each; empty native hat; held-item layer variable with equipment. Ghosts translucent. Native dispatcher and baked geometry are the authority.','baseline_uncertainty':'No project-declared vanilla base mapping exists. Proposed morphological comparators disclosed per row; retained original own rigs also counted. Cannot certify corresponding-base requirement by silently choosing a larger vanilla model.','sourcejar':str(sourcejar),'sourcejar_sha256':hashlib.sha256(sourcejar.read_bytes()).hexdigest(),'native_available':bool(native),'entities':rows}
(O/'geometry-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
with (O/'geometry-counts.csv').open('w') as f:
 keys=[k for k in rows[0] if k!='native'];w=csv.DictWriter(f,keys,extrasaction='ignore');w.writeheader();w.writerows(rows)
print('Audited',len(rows),'entities; native baked count verification:',bool(native),'largest',max(rows,key=lambda r:r['declared_quads'])['id'])
