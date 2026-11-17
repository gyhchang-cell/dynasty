from pathlib import Path
import json,hashlib,zipfile,re
B=Path(__file__).resolve().parent; R=B.parents[2]; D=R/'docs/art/armor-modular-heavy-reference-20261112'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(B/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
prov=json.loads((B/'provenance.json').read_text());entries=0;classes=0
for row in prov:
 assert H(Path(row['archive']))==row['sha256']
 with zipfile.ZipFile(row['archive']) as z:
  for n,h in row['entries'].items():
   assert H(B/n)==h
   prefix='source/'+Path(row['archive']).name+'/'
   assert hashlib.sha256(z.read(n.removeprefix(prefix))).hexdigest()==h
   entries+=1
 for n,h in row['disassemblies'].items():assert H(B/n)==h;classes+=1
# Freeze method bodies with source hash and line for an independent reviewer.
requests=[(B/'bytecode','GeoArmorRenderer.class.txt',[' getHeadBone(',' getBodyBone(',' getRightArmBone(',' getLeftArmBone(',' getRightLegBone(',' getLeftLegBone(',' getRightBootBone(',' getLeftBootBone(',' applyBoneVisibilityBySlot(',' setAllBonesVisible(',' setBoneVisible(']),(B/'bytecode','GeoArmorRenderer$2.class.txt',['static {};']),(B/'bytecode','ClientSetup.class.txt',[' modelRegistryReady(']),(B/'bytecode','ModularModelLoader.class.txt',[' read(']),(B/'bytecode','UnresolvedItemModel.class.txt',[' bake(']),(B/'bytecode','ModularOverrideList.class.txt',[' getOverrideModel(',' createLayerModel(',' filterModels(',' lambda$filterModels',' lambda$createLayerModel']), (B/'bytecode','ItemLayerModel.class.txt',[' bake(']),(D/'bytecode','ModularArmorItem.class.txt',[' getModels(',' modelNotGecko(']),(D/'bytecode','ModularGeoArmorRenderer.class.txt',[' applyBaseTransformations(',' applyBoneVisibilityBySlot(',' setAllBonesVisible('])]
excerpts=[]
for root,name,terms in requests:
 f=next(root.rglob(name));lines=f.read_text().splitlines()
 for i,l in enumerate(lines):
  if l.startswith(('  public ','  protected ','  private ','  static ')) and any(t in l for t in terms):
   end=i+1
   while end<len(lines) and 'LineNumberTable:' not in lines[end]:end+=1
   excerpts.append({'source':str(f.relative_to(R)),'sha256':H(f),'line':i+1,'method_body':'\n'.join(lines[i:end])})
save('consumer-method-excerpts.json',excerpts)
configuration=json.loads((D/'whole-configuration.json').read_text());geo=json.loads((D/'declared-geometry-uv.json').read_text());bone_names={}
for g in geo['geometry']:bone_names[Path(g['source']).name.split('.')[0]]={b['name'] for b in g['bones']}
slot_bones={'head':{'base':['armorHead']},'chest':{'base':['armorBody'],'left':['armorLeftArm'],'right':['armorRightArm']},'legs':{'base':['armorBelt'],'left':['armorLeftLeg'],'right':['armorRightLeg']},'feet':{'left':['armorLeftBoot'],'right':['armorRightBoot']}}
for slot,models in slot_bones.items():
 for model,names in models.items():assert set(names)<=bone_names[model]
icons={slot:[m['icon_module_location'] for m in configuration['modules'] if m['slot'].startswith(slot+'/')] for slot in slot_bones}
assert list(map(len,icons.values()))==[1,3,3,2]
base=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text());changes=[p for p,h in base.items() if H(R/p)!=h];assert not changes
save('static-consumers.json',{'scope':'Exact local archive static consumers; no runtime classloader claim','local_gecko_version':'4.8.3','equipment_root_visibility':slot_bones,'visibility_contract':'Superclass switches HEAD/CHEST/LEGS/FEET 1/2/3/4, first hides all managed roots; conditional native ModelPart.visible enables slot roots. Subclass extends reset to armorBelt and enables belt on LEGS. Missing roots are null-safe. This is not a guarantee of rendered descendant faces.','pose_contract':'Subclass overrides applyBaseTransformations: own head/body/arm/leg/boot transforms; belt follows body if both exist; no superclass transformation call. Source method body saved.','native_inventory_layers_unordered':icons,'layer_order_limit':'Both module and model render priority sorting exists; equal-priority original collection order not asserted. No invented final flattened inventory PNG.','inventory_chain':['ClientSetup.modelRegistryReady registers modular_loader','ModularModelLoader.read parses display and optional variants','UnresolvedItemModel.bake installs ModularOverrideList','getOverrideModel calls IModularItem.getModels','GeoTetraArmor.getModels filters nonNull and modelNotGecko, sorts renderLayer','createLayerModel maps ModuleModel.location to atlas material and assigns per-layer tint/emission/transform','ItemLayerModel.bake creates unbaked item elements from SpriteContents, bakes quads, applies layer transformers, adds CompositeModel quads and builds'], 'configuration_identity':'Same D49 all-nine-heavy iron configuration, not a new candidate or registered ID','static_consumer_correspondence_complete':True,'final_raster_or_game_wearing_verified':False})
save('verification.json',{'status':'PASS_FIXED_ARCHIVES_HASHES_FOUR_SLOT_ROOTS_AND_INVENTORY_CONSUMER_CORRESPONDENCE','source_entries':entries,'readonly_disassemblies':classes,'method_excerpts':len(excerpts),'four_slots':4,'inventory_modules':9,'protected_paths':len(base),'production_changes':changes,'runtime_starts':0,'new_candidate_credit':0,'new_validated_design_credit':0,'gate_met':False})
print((B/'verification.json').read_text())
