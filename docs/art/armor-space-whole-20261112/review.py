from pathlib import Path
import re,json,hashlib,zipfile
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent; R=B.parents[2]
H=lambda b:hashlib.sha256(b).hexdigest()
def save(n,d): (B/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=json.loads((B/'provenance.json').read_text()); a=B/'ad-astra-fixed-source.zip';assert H(a.read_bytes())==p['archive_sha256']
with zipfile.ZipFile(a) as z:
 root=z.namelist()[0]
 for rel,h in p['entries'].items():assert H((B/'source'/rel).read_bytes())==h==H(z.read(root+rel)),rel
def get(name):
 paths=list((B/'source').rglob(name));assert len(paths)==1,(name,paths)
 return paths[0].read_text()
s=get('SpaceSuitModel.java'); block=s.split('public static LayerDefinition createSpaceSuitLayer() {',1)[1].split('public static LayerDefinition createNetheriteSpaceSuitLayer()',1)[0]
parts=[]; cubes=[]
pat=r'PartDefinition (\w+) = (\w+)\.addOrReplaceChild\(("[^"]+"|PartNames.HAT), (.*?);'
for m in re.finditer(pat,block,re.S):
 var,parent,name,body=m.groups();name='hat' if name=='PartNames.HAT' else json.loads(name)
 pose=body.split(', PartPose.',1)[1]; ps=[float(x.rstrip('f')) for x in re.findall(r'-?\d+(?:\.\d+)?f?',pose)]
 entry={'name':name,'parent':'root' if parent=='modelPartData' else parent,'pose_literal':pose,'pose_numbers':ps,'statement':m.group(0),'cubes':[]}
 mirror=False
 for c in re.finditer(r'\.texOffs\((\d+), (\d+)\)(\.mirror\(\))?\.addBox\(([^;]+?)new CubeDeformation\(([-\d.]+)f\)\)',body,re.S):
  u,v,mir,nums,inf=c.groups();mirror=mirror or bool(mir);n=[float(x.rstrip('f')) for x in nums.strip().rstrip(',').split(',')];assert len(n)==6
  u,v=int(u),int(v);w,h,d=map(int,n[3:]);f4=u;f5=u+d;f6=u+d+w;f7=u+d+2*w;f8=u+d+w+d;f9=u+d+w+d+w;t=v+d;b=t+h
  faces={'down':[f5,v,f6,t],'up':[f6,t,f7,v],'west':[f4,t,f5,b],'north':[f5,t,f6,b],'east':[f6,t,f8,b],'south':[f8,t,f9,b]}
  for q in faces.values():assert all(0<=v<=64 for v in q),(name,q)
  cube={'part':name,'index':len(entry['cubes']),'origin':n[:3],'size':n[3:],'uv':[u,v],'inflate':float(inf),'mirror':mirror,'raw_modelpart_uv':faces}
  entry['cubes'].append(cube);cubes.append(cube)
 parts.append(entry)
assert len(parts)==14 and len(cubes)==13,(len(parts),len(cubes))
assert [c['mirror'] for c in cubes if c['part']=='left_boot']==[True,True]
items=get('ModItems.java'); regs=[]
for item,typ,cls in [('space_helmet','HELMET','CustomDyeableArmorItem'),('space_suit','CHESTPLATE','SpaceSuitItem'),('space_pants','LEGGINGS','CustomDyeableArmorItem'),('space_boots','BOOTS','CustomDyeableArmorItem')]:
 line=next(l.strip() for l in items.splitlines() if 'register("'+item+'"' in l);assert 'new '+cls+'(SpaceSuitMaterial.MATERIAL, ArmorItem.Type.'+typ in line
 f=B/'source/common/src/main/generated/resources/assets/ad_astra/models/item'/f'{item}.json'
 # item models reside in main/resources in this fixed source when not generated
 if not f.exists(): f=next(q for q in (B/'source').rglob(item+'.json') if '/models/item/' in str(q))
 model=json.loads(f.read_text()); assert model['textures']['layer0']=='ad_astra:item/'+item
 regs.append({'id':'ad_astra:'+item,'slot_type':typ,'class':cls,'source_statement':line,'item_model':str(f.relative_to(B)),'model':model})
assert 'extends CustomDyeableArmorItem' in get('SpaceSuitItem.java')
assert 'extends DyeableArmorItem' in get('CustomDyeableArmorItem.java')
client=get('AdAstraClient.java');forge=get('AdAstraClientForge.java');mix=get('CustomDyeableArmorItemMixin.java')
impl=next(q.read_text() for q in (B/'source/forge').rglob('ClientPlatformUtilsImpl.java'))
assert 'event.enqueueWork(AdAstraClient::init)' in forge and 'registerArmor();' in client
assert 'SpaceSuitModel::new' in client and 'ARMOR_RENDERERS.put' in impl
assert 'bakeLayer(renderer.layer())' in mix and 'renderer.factory().create(root, slot, stack' in mix
assert 'common.CustomDyeableArmorItemMixin' in (B/'source/forge/src/main/resources/adastra.mixins.json').read_text()
assert 'this.rightBoot = root.getChild("left_boot")' in s and 'this.leftBoot = root.getChild("right_boot")' in s
atlas=next(q for q in (B/'source').rglob('space_suit.png') if '/entity/armor/' in str(q));im=Image.open(atlas).convert('RGBA');assert im.size==(64,64)
canvas=Image.new('RGB',(1200,1100),'#555b60');draw=ImageDraw.Draw(canvas)
draw.text((10,10),'Fixed-source raw UV crops (not game / not transformed faces); U/D signed rect retained in JSON',fill='white')
for i,cube in enumerate(cubes):
 y=42+i*80;draw.text((8,y),f"{cube['part']} #{cube['index']} mirror={cube['mirror']} inflate={cube['inflate']}",fill='white')
 for j,(face,q) in enumerate(cube['raw_modelpart_uv'].items()):
  x=285+j*148;u1,v1,u2,v2=q; crop=im.crop((min(u1,u2),min(v1,v2),max(u1,u2),max(v1,v2)))
  k=min(110//crop.width,48//crop.height);crop=crop.resize((crop.width*k,crop.height*k),Image.Resampling.NEAREST)
  canvas.paste(crop,(x,y+20),crop);draw.text((x,y),face+' '+str(q),fill='white')
canvas.save(B/'raw-uv-crops.png')
geometry={'atlas':str(atlas.relative_to(B)),'atlas_size':[64,64],'parts':parts,'part_count':14,'cube_count':13,'raw_face_rectangles':78,'contract_context':'Minecraft ModelPart box UV; signed UP V retained; mirror and inflate separate. Crops normalize bounds only; no world transform/orientation/worn claim.','not_runtime':True}
save('geometry-and-raw-uv.json',geometry)
save('static-bindings.json',{'native_registrations':regs,'whole_design_key':'ad_astra:basic_space_suit','forge_source_chain':['CLIENT MOD event onClientSetup -> enqueue AdAstraClient.init -> registerArmor','ClientPlatformUtils.registerArmor -> forge ARMOR_RENDERERS item map -> SpaceSuitModel::new','RegisterLayerDefinitions -> onRegisterEntityLayers -> SpaceSuitModel.register -> createSpaceSuitLayer','CustomDyeableArmorItemMixin listed in forge config -> IClientItemExtensions -> bakeLayer(renderer.layer) -> factory(root,slot,stack,original)','SPACE_SUITS tag space_suit_items contains all basic four -> SPACE_SUIT_TEXTURE; material getName iron is not texture filename'],'visible_roots':{'HEAD':['head','visor'],'CHEST':['body','right_arm','left_arm'],'LEGS':['belt','right_leg','left_leg'],'FEET':['left_boot','right_boot']},'nonroot_children':{'body':['backpack'],'right_arm':['cube_r1'],'left_arm':['cube_r2']},'source_boot_name_inversion':'rightBoot field reads left_boot and copies parent rightLeg; leftBoot reads right_boot and copies parent leftLeg. Retain as source fact; actual visual side result unverified.','limits':['Mixin application/remap/Forge execution unverified','Architectury platform bridge inferred from fixed platform implementation; not runtime verified','no wearing/five views/seams validation','no variants counted independently']})
baseline=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text());changed=[f for f,h in baseline.items() if not (R/f).exists() or H((R/f).read_bytes())!=h];assert not changed,changed
gear=R/'src/main/java/com/dynasty/DynastyGear.java'; gs=gear.read_text(); target=[]
for family in ['bamboo','brocade','cloth','leather','sea_silk','hongmeng','cinnabar']:
 if family not in ['cloth','sea_silk']: assert '{"'+family+'", DynastyArmorMaterials.' in gs
 else: assert 'armor("'+family+'_helmet"' in gs
 ids=['dynasty:'+family+'_'+part for part in ['helmet','chestplate','leggings','boots']]
 files={}
 for part in ['helmet','chestplate','leggings','boots']:
  for rel in [f'src/main/resources/assets/dynasty/textures/item/{family}_{part}.png',f'src/main/resources/assets/dynasty/models/item/{family}_{part}.json']:
   assert (R/rel).exists();files[rel]=H((R/rel).read_bytes())
 for layer in [1,2]:
  rel=f'src/main/resources/assets/dynasty/textures/models/armor/{family}_layer_{layer}.png';assert (R/rel).exists();files[rel]=H((R/rel).read_bytes())
 target.append({'family':family,'native_ids':ids,'static_cap_risk':family in ['bamboo','brocade','cloth','leather','sea_silk'],'material_priority':family in ['hongmeng','cinnabar','brocade'],'status':'historic static finding, not confirmed redraw authorization; worn acceptance pending','files':files})
save('current-dynasty-targets.json',{'gear_source':str(gear.relative_to(R)),'gear_sha256':H(gear.read_bytes()),'confirmed_never_redrawn_sets':0,'static_cap_risk_families':5,'static_material_priority_families':3,'unique_static_finding_families':7,'targets':target,'protected_legacy_whole_torso_families':['bronze','general','jade','sky','xuantian'],'validated_applicable_independent_design_total':None,'exact_remaining_gap_to_1000':None,'count_note':'654 names / 640 armor name families / 215 conservative learning groups are historic discovery/review counts, not independently validated applicable totals. No accepted-history reset.'})
receipt=R/'docs/cod4/audit-20261022/coordinator-textureD49-D50-static-consumer-geometry-review-20261112.json';assert H(receipt.read_bytes())=='3c958b261af7f9b989e931f528e6e477d4391e282b62ade0bc4d581a45d6d298'
save('verification.json',{'source_archive_hash_and_entries_match':True,'source_entries':len(p['entries']),'native_slots_checked':4,'basic_parts':len(parts),'basic_cubes':len(cubes),'raw_uv_rectangles_in_bounds':78,'left_boot_persistent_mirror_checked':True,'protected_source_files_unchanged':len(baseline),'production_mutations':0,'game_starts':0,'checklist_deletions':0,'new_validated_design_credit':0,'validated_total':None,'exact_gap':None,'coordinator_D49_D50_receipt_sha256':H(receipt.read_bytes()),'coordinator_receipt_claim':'hash verified only here, independent review delivered by Main; no duplicate credit'})
print('verified',len(parts),'parts',len(cubes),'cubes',len(p['entries']),'source entries',len(baseline),'protected')
