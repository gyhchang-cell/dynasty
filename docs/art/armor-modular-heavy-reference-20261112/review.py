"""Bounded source correspondence; never executes the mod or writes game assets."""
from pathlib import Path
import json, hashlib, zipfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
B=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def save(n,v):(B/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
checks={}
for pf,folder in [('provenance.json','source'),('dependency-provenance.json','dependency')]:
 p=load(B/pf); zpath=Path(p['archive']); assert H(zpath.read_bytes())==p['archive_sha256']
 with zipfile.ZipFile(zpath) as z:
  for n,h in p['entries'].items():
   assert H(z.read(n))==h==H((B/folder/n).read_bytes()),n
 for n,h in p['disassemblies'].items():assert H((B/n).read_bytes())==h,n
 checks[pf]={'entries':len(p['entries']),'disassemblies':len(p['disassemblies']),'hashes_pass':True}
prior=ROOT/'docs/art/armor-tyrant-hide-whole-20261112/combined-semantic-ledger.json'
ledger=load(prior)
assert not any('geotetraarmor:' in s for s in ledger['reviewed_case_keys'])
modules=[]
for f in sorted((B/'source/data/tetra/modules/armor').rglob('heavy.json')):
 d=load(f);v=d['variants'][0];e=v['extract'];suffix=e['availableTextures'][0]
 assert len(d['slots'])==1 and len(e['availableTextures'])==1
 assert e['models'][0]['type']=='gecko'
 location=e['models'][0]['location']+suffix
 modules.append({'slot':d['slots'][0],'module_source':str(f.relative_to(B)),
 'variant_key_static_derivation':v['key']+'iron','material':'tetra:metal/iron',
 'available_textures':e['availableTextures'],'resolved_gecko_location':location,
 'icon_module_location':e['models'][1]['location']+suffix,
 'resource_derivation':'source fallback availableTextures[0]; iron textures metal/default do not match'})
assert len(modules)==9
slots={'head':['head/base'],'chest':['chest/base','chest/left','chest/right'],'legs':['legs/belt','legs/left','legs/right'],'feet':['feet/left','feet/right']}
for s,keys in slots.items():assert sorted(m['slot'] for m in modules if m['slot'].startswith(s+'/'))==sorted(keys)
geometry=[];counts={'bones':0,'cubes':0,'box_uv':0,'per_face_uv':0}
for f in sorted((B/'source/assets/geotetraarmor/geo/item/armor/heavy').glob('*.json')):
 g=load(f)['minecraft:geometry'][0];assert (g['description']['texture_width'],g['description']['texture_height'])==(64,64)
 bones=[]
 for b in g['bones']:
  cubes=[];counts['bones']+=1
  for i,c in enumerate(b.get('cubes',[])):
   kind='per_face_uv' if isinstance(c['uv'],dict) else 'box_uv';counts[kind]+=1;counts['cubes']+=1
   cubes.append({'index':i,'origin':c['origin'],'size':c['size'],'rotation':c.get('rotation'), 'uv_kind':kind,'uv':c['uv']})
  bones.append({'name':b['name'],'parent':b.get('parent'),'pivot':b.get('pivot'),'rotation':b.get('rotation'),'cubes':cubes})
 geometry.append({'source':str(f.relative_to(B)),'bones':bones})
assert counts=={'bones':19,'cubes':45,'box_uv':20,'per_face_uv':25},counts
pngs={}
for f in sorted((B/'source').rglob('*.png')):
 with Image.open(f) as im:
  im.load();pngs[str(f.relative_to(B))]={'size':list(im.size),'mode':im.mode,'sha256':H(f.read_bytes())}
assert len(pngs)==12
wear=[v['sha256'] for k,v in pngs.items() if '/textures/item/armor/heavy/' in k]
assert len(wear)==3 and len(set(wear))==1
animations={}
for f in sorted((B/'source/assets/geotetraarmor/animations').rglob('*.json')):
 a=load(f)['animations'];assert all(not v.get('bones') for v in a.values());animations[str(f.relative_to(B))]=a
baseline=load(ROOT/'docs/art/armor-ars-reference-20261111/source-baseline.json')
changed=[p for p,h in baseline.items() if not (ROOT/p).exists() or H((ROOT/p).read_bytes())!=h]
assert not changed,changed
save('whole-configuration.json',{'kind':'RESEARCH_CONFIGURATION_NOT_REGISTERED_ITEM_OR_ACQUIRED_NBT','key':'geotetraarmor/all-nine-heavy-modules/iron','native_item_ids':['geotetraarmor:'+s for s in slots], 'slots':slots,'modules':modules,'iron_texture_tint_static':16777215,'default_replacement_warning':'Native iron replacement JSON uses vanilla modules, not this heavy assembly. No acquired preset or runtime acceptance is claimed.'})
save('declared-geometry-uv.json',{'scope':'Native local pivots/rotations and declared UV, not baked faces or world bounds; signed per-face UV retained','counts':counts,'geometry':geometry,'animations_without_bone_keyframes':animations})
save('png-inventory.json',pngs)
save('verification.json',{'status':'PASS_BOUNDED_SOURCE_HASHES_MODULE_LAYOUT_DECLARED_UV_AND_PROTECTED_BASELINE','sources':checks,'png_entries':12,'unique_wear_atlas':1,'module_slots':9,'native_equipment_slots':4,'geometry_counts':counts,'prior_geotetra_namespace_absent':True,'protected_paths_checked':len(baseline),'protected_changes':changed,'runtime_verified':False,'new_validated_design_credit':0,'gate_met':False})
print(json.dumps(load(B/'verification.json'),ensure_ascii=False))
