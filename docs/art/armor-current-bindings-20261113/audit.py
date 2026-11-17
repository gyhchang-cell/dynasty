"""Read-only project audit. Writes evidence only inside this new batch directory."""
from pathlib import Path
import hashlib, json, re, zipfile, subprocess, sys
from PIL import Image

D = Path(__file__).resolve().parent
R = D.parents[2]
sha = lambda b: hashlib.sha256(b).hexdigest()
def load(p): return json.loads(p.read_text())
def save(n, d): (D/n).write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n')
def digest(p): return sha(p.read_bytes())
assert not (D/'verification.json').exists(), 'Frozen batch; do not overwrite'
targets = load(R/'docs/art/armor-space-whole-20261112/current-dynasty-targets.json')['targets']
priority = {p:h for t in targets for p,h in t['files'].items()}
protected = load(R/'docs/art/armor-ars-reference-20261111/source-baseline.json')
baseline = {p:digest(R/p) for p in protected | priority}
assert all(baseline[p]==h for p,h in (protected | priority).items())
ids = [i for t in targets for i in t['native_ids']]
subprocess.run([sys.executable,str(R/'tools/art/snapshot_texture_requirements.py'),
 '--batch-dir',str(D),'--targets',*ids,'--application',
 'D73：只读核实28件图标/14张穿戴图的当前绑定、原稿RGBA、历史版本、项目覆盖源；修正静态UV面的命名误判。不制作、不改变美术、不启动Java、不删待办。'], check=True)
sources = ['src/main/java/com/dynasty/'+p for p in ['Dynasty.java','DynastyContent.java','DynastyGear.java','DynastyArmorMaterials.java',
 'client/OriginalItemGeometry.java','client/DynastyClientEvents.java','client/DivineArmorLightLayer.java']]
sources += ['build.gradle','gradle.properties','src/main/resources/assets/minecraft/atlases/blocks.json']
source_hashes = {}
for p in sources:
 b=(R/p).read_bytes(); out=D/'inputs'/p; out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b);source_hashes[p]=sha(b)
save('source-inputs.json',source_hashes)
jar=Path.home()/'.gradle/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar'
entries=['net/minecraft/client/'+p+'.java' for p in ['model/HumanoidModel','model/HumanoidArmorModel','model/geom/ModelPart','model/geom/LayerDefinitions',
 'renderer/entity/LivingEntityRenderer','renderer/entity/layers/HumanoidArmorLayer','renderer/entity/player/PlayerRenderer']]
entries+=['net/minecraftforge/client/ForgeHooksClient.java','net/minecraftforge/client/extensions/common/IClientItemExtensions.java','net/minecraft/world/item/ArmorItem.java']
consumer={}
with zipfile.ZipFile(jar) as z:
 for p in entries:
  b=z.read(p);o=D/'consumer'/p;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(b);consumer[p]=sha(b)
save('consumer-provenance.json',{'source_jar':str(jar),'sha256':digest(jar),'version':'1.20.1-47.4.10_mapped_official_1.20.1','entries':consumer,'scope':'Local source dependency context, not compiled game or live mod-stack acceptance'})
v15=R/'docs/art/remaining-textures-v15'
manifest={r['source_path']:r for r in load(v15/'delivery-manifest.json')['files']}
selection={}
for folder in ['armor-foundations-v29','armor-sacred-v25']:
 base=R/'docs/art'/folder
 for row in load(base/'selection.json'):
  selection[row['id']] = (base,row)
atlas=load(R/'src/main/resources/assets/minecraft/atlases/blocks.json')
filters=[s['pattern'] for s in atlas['sources'] if s['type']=='minecraft:filter']
items=[]; worn=[]; historical_inputs={}
for t in targets:
 family=t['family']
 for native in t['native_ids']:
  ident=native.split(':')[1];mp=f'src/main/resources/assets/dynasty/models/item/{ident}.json'; model=load(R/mp)
  custom=model.get('loader')=='dynasty:original_item'
  texture=model['original_texture'] if custom else model['textures']['layer0']
  ns,rel=texture.split(':'); resource=f'assets/{ns}/'+(rel if custom else f'textures/{rel}.png')
  ip='src/main/resources/'+resource; im=Image.open(R/ip).convert('RGBA')
  assert ip in priority and (R/ip).exists()
  excluded=any(re.fullmatch(f['namespace'],ns) and re.fullmatch(f['path'],f'item/{ident}') for f in filters)
  assert excluded==custom
  row={'id':native,'model':mp,'model_sha256':digest(R/mp),'icon':ip,'icon_sha256':digest(R/ip), 'size':im.size,
    'consumer':'original_item direct full-resolution PNG' if custom else 'item/generated layer0 atlas',
    'excluded_from_shared_block_atlas':excluded,'material':f'dynasty:{family}',
    'slot':ident[len(family)+1:],'expected_worn_resource':f'assets/dynasty/textures/models/armor/{family}_layer_{2 if ident.endswith("_leggings") else 1}.png',
    'runtime_acceptance':False}
  if custom:
   base,sel=selection[ident];p=base/'sources'/f'{ident}.png';origin=Image.open(p).convert('RGBA');crop=origin.crop(sel['crop_bounds'])
   expected=Image.new('RGBA',(crop.width+4,crop.height+4));expected.paste(crop,(2,2))
   equal=expected.size==im.size and expected.tobytes()==im.tobytes();assert equal
   row['selected_original']={'batch':base.name,'original':str(p.relative_to(R)),'original_sha256':digest(p),'crop_bounds':sel['crop_bounds'],'original_size':origin.size,'exact_rgba_plus_2px_padding':equal}
   for h in [p,base/'selection.json']:historical_inputs[str(h.relative_to(R))]=digest(h)
  else:
   m=manifest[ip];p=v15/m['candidate_path'];assert digest(R/ip)==digest(p)==m['sha256']
   row['historical_v15_match']=True;row['qualification']='Already historically redrawn; not confirmed never-made/crude redraw permission'
   historical_inputs[str(p.relative_to(R))]=digest(p)
  items.append(row)
 for layer in [1,2]:
  rel=f'src/main/resources/assets/dynasty/textures/models/armor/{family}_layer_{layer}.png';m=manifest[rel];p=v15/m['candidate_path']
  assert digest(R/rel)==digest(p)==m['sha256'];im=Image.open(R/rel).convert('RGBA');assert im.size==(64,32)
  worn.append({'family':family,'layer':layer,'path':rel,'sha256':digest(R/rel),'v15_candidate':str(p.relative_to(R)), 'candidate_matches_current_bytes':True,
   'historical_manifest_status':m['status'],'current_source_contains_candidate':True,'size':im.size,'runtime_acceptance':False})
  historical_inputs[str(p.relative_to(R))]=digest(p)
historical_inputs[str((v15/'delivery-manifest.json').relative_to(R))]=digest(v15/'delivery-manifest.json')
save('historical-inputs.json',historical_inputs);save('item-bindings.json',items);save('worn-versions.json',worn)
keys={p.removeprefix('src/main/resources/'):h for p,h in priority.items()}
overrides={}
for folder in ['src/generated/resources','build/resources/main']:
 rows=[]
 for key,expected in keys.items():
  p=R/folder/key
  if p.exists(): rows.append({'resource':key,'sha256':digest(p),'matches_current_source':digest(p)==expected})
 overrides[folder]=rows
packs=[]
for p in sorted((R/'modpack/resourcepacks').glob('*.zip')):
 with zipfile.ZipFile(p) as z:
  matches=sorted(set(z.namelist()) & set(keys))
  packs.append({'path':str(p.relative_to(R)),'sha256':digest(p),'entries':len(z.namelist()),'target_resource_matches':matches})
save('override-scope.json',{'folders':overrides,'modpack_zip_packs':packs,'limits':['Only project generated/main build resources and modpack resource-pack ZIPs checked.','User instance resource-pack priority, other mods and loaded Jar not inspected.','Existing build output equality is not a new build or runtime test.']})
assert len(overrides['src/generated/resources'])==0
assert len(overrides['build/resources/main'])==70 and all(r['matches_current_source'] for r in overrides['build/resources/main'])
assert not any(p['target_resource_matches'] for p in packs)
faces=[('head_model_y_min_crown', [8,0,16,8]),('head_model_y_max_chin',[16,0,24,8]),('hat_model_y_min',[40,0,48,8]),('hat_model_y_max',[48,0,56,8])]
coverage=[]
for t in targets:
 p=R/f'src/main/resources/assets/dynasty/textures/models/armor/{t["family"]}_layer_1.png';a=Image.open(p).convert('RGBA').getchannel('A')
 coverage.append({'family':t['family'],'faces':[{'name':name,'bounds':b,'nonzero_alpha_pixels':sum(v>0 for v in a.crop(b).getdata()),'pixels':64} for name,b in faces]})
save('head-horizontal-face-correction.json',{'source_chain':['ModelPart.Cube vertex/UV construction','HumanoidModel.createMesh head(-4,-8,-4), size(8,8,8)','LivingEntityRenderer.render scale(-1,-1,1)'],
 'correction':'In neutral ordinary humanoid pose, model-space y_min (Direction.DOWN) is anatomical crown, rectangle [8,0,16,8]. y_max (Direction.UP) is chin/lower plane, rectangle [16,0,24,8]. Empty latter rectangle alone cannot establish missing crown.',
 'supersedes_only':'Prior static_cap_risk naming as evidence of missing head top; does not rewrite frozen historic records or authorize texture edits.',
 'limit':'Nonzero alpha coverage alone is not proof of intended cutouts, face winding, seams or live appearance; Main independent review and live acceptance remain.', 'coverage':coverage})
scan=subprocess.run(['rg','-n','getArmorTexture|getHumanoidArmorModel|initializeClient|RegisterGeometryLoaders|DivineArmorLightLayer|ItemColors',str(R/'src/main/java/com/dynasty')],capture_output=True,text=True)
(D/'scoped-hook-search.txt').write_text(scan.stdout)
unclosed=[]
for item in items:
 unclosed.append({'id':item['id'],'remaining':['Worn material/UV seams and actual client appearance acceptance','User live resource-pack/mod overrides unknown']+(['Icon versus earlier worn-atlas design coherence not accepted'] if 'selected_original' in item else ['Historical v15 icon; age alone does not qualify as crude/unmade']), 'confirmed_wrong_layer':False,'confirmed_missing_icon_reference':False,'redraw_authorized_by_audit':False})
save('unclosed-targets.json',unclosed)
prior=R/'docs/art/armor-valonite-whole-20261112/combined-semantic-ledger.json'
(D/'combined-semantic-ledger.json').write_bytes(prior.read_bytes())
save('reference-carry.json',{'path':str(prior.relative_to(R)),'sha256':digest(prior),'new_credit':0,'validated_total':None,'exact_gap':None,'gate_met':False})
end={p:digest(R/p) for p in baseline}
source_unchanged=all(digest(R/p)==h for p,h in source_hashes.items())
history_unchanged=all(digest(R/p)==h for p,h in historical_inputs.items())
assert end==baseline and source_unchanged and history_unchanged
save('protected-before-after.json',{'before':baseline,'after':end})
save('verification.json',{'batch':'D73','protected_count':len(protected),'priority_count':len(priority),'item_count':len(items),'selected_original_exact_rgba':sum('selected_original'in r for r in items),'v15_icon_matches':sum(r.get('historical_v15_match',False) for r in items),'v15_worn_matches':len(worn),'protected_unchanged':end==baseline,'source_inputs_unchanged':source_unchanged,'historical_inputs_unchanged':history_unchanged,'production_changes':0,'java_starts':0,'checklist_deletions':0,'new_reference_credit':0,'gate_met':False,'runtime_acceptance':False})
save('progress.json',{'batch':'D73','status':'CURRENT_PROJECT_BINDINGS_AND_ORIGINAL_PIXELS_AUDITED_RUNTIME_PENDING','prior':'docs/art/armor-valonite-whole-20261112/progress.json','target_status':str((D/'unclosed-targets.json').relative_to(R)),'new_credit':0,'gate_met':False,'production_changes':0,'next_scope':'Independent review of UV face correction; continue unstudied applicable whole references before production. Protect selected originals; do not automatically redraw older v15 icons.'})
print('PASS: 28 bindings, 16 original RGBA, 12 v15 icons, 14 worn atlases; protected/source/history unchanged')
