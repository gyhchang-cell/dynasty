from pathlib import Path
import re,json,hashlib,zipfile,shutil
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[2];H=lambda b:hashlib.sha256(b).hexdigest()
def save(n,d):(B/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=json.loads((B/'provenance.json').read_text());a=B/'eidolon-fixed-source.zip';assert H(a.read_bytes())==p['archive_sha256']
with zipfile.ZipFile(a) as z:
 prefix=z.namelist()[0]
 for f,h in p['entries'].items():assert H((B/'source'/f).read_bytes())==h==H(z.read(prefix+f))
def get(n):
 ps=list((B/'source').rglob(n));assert len(ps)==1;return ps[0].read_text()
s=get('SilverArmorModel.java');parts=[]
for m in re.finditer(r'PartDefinition (\w+) = (\w+)\.addOrReplaceChild\("([^"]+)", (.*?);',s,re.S):
 var,parent,name,body=m.groups();u,v=map(int,re.search(r'texOffs\((\d+), (\d+)\)',body).groups());c=re.search(r'addBox\((.*?)new CubeDeformation\(([-\d.]+)[fF]\)',body,re.S);nums=[float(n.strip().rstrip('fF')) for n in c.group(1).strip().rstrip(',').split(',')];assert len(nums)==6
 w,h,d=map(int,nums[3:]);f5=u+d;f6=f5+w;f7=f6+w;f8=f6+d;f9=f8+w;t=v+d;b=t+h
 faces={'down':[f5,v,f6,t],'up':[f6,t,f7,v],'west':[u,t,f5,b],'north':[f5,t,f6,b],'east':[f6,t,f8,b],'south':[f8,t,f9,b]}
 assert all(0<=n<=64 for rect in faces.values() for n in rect)
 parts.append({'name':name,'parent':parent,'origin':nums[:3],'size':nums[3:],'inflate':float(c.group(2)),'mirror':'.mirror()' in body,'pose_literal':body.split(', PartPose.',1)[1],'raw_modelpart_uv':faces,'source_statement':m.group(0)})
assert len(parts)==10
atlas=next(q for q in (B/'source').rglob('silver_armor.png'));im=Image.open(atlas).convert('RGBA');assert im.size==(64,64)
can=Image.new('RGB',(1200,850),'#555b60');dr=ImageDraw.Draw(can);dr.text((10,10),'Silver armor raw source UV crops; NOT game, mirrored/transformed faces not simulated',fill='white')
for i,part in enumerate(parts):
 y=42+i*80;dr.text((10,y),part['name']+' mirror='+str(part['mirror']),fill='white')
 for j,(face,q) in enumerate(part['raw_modelpart_uv'].items()):
  x=275+j*150;u1,v1,u2,v2=q;t=im.crop((min(u1,u2),min(v1,v2),max(u1,u2),max(v1,v2)));k=min(125//t.width,48//t.height);t=t.resize((t.width*k,t.height*k),Image.Resampling.NEAREST);can.paste(t,(x,y+20),t);dr.text((x,y),face+' '+str(q),fill='white')
can.save(B/'raw-uv-crops.png')
save('geometry-and-raw-uv.json',{'atlas_size':[64,64],'explicit_cubes':10,'raw_source_uv_rectangles':60,'parts':parts,'alias_roots':['body','pelvis','head','left_legging','left_foot','right_legging','right_foot','left_arm','right_arm'],'base_mesh_note':'HumanoidModel.createMesh before alias root replacement; inherited leg roots remain pose sources, excluded from custom bodyParts render lists. No final mesh/runtime claim.','limits':'source rectangles only; signed UP V kept, rotations/inflate/mirror are separate. guard has Y0.7854 rotation; final seam orientation unverified.'})
reg=get('Registry.java');bindings=[]
for name,typ in [('silver_helmet','HELMET'),('silver_chestplate','CHESTPLATE'),('silver_leggings','LEGGINGS'),('silver_boots','BOOTS')]:
 line=next(l.strip() for l in reg.splitlines() if 'addItem("'+name+'"' in l);assert 'new SilverArmorItem(Type.'+typ in line
 model=json.loads(next(q for q in (B/'source').rglob(name+'.json')).read_text());assert model['textures']['layer0']=='eidolon:item/'+name
 bindings.append({'native_id':'eidolon:'+name,'type':typ,'registration':line,'item_model':model})
cl=get('ClientRegistry.java');it=get('SilverArmorItem.java');assert 'event.registerLayerDefinition(SILVER_ARMOR_LAYER, SilverArmorModel::createBodyLayer)' in cl;assert 'new SilverArmorModel(event.getEntityModels().bakeLayer(SILVER_ARMOR_LAYER))' in cl
assert 'SILVER_ARMOR_MODEL.slot = getEquipmentSlot()' in it;assert ':textures/entity/silver_armor.png' in it
save('static-bindings.json',{'native_items':bindings,'native_namespace':'Eidolon.MODID = eidolon; gradle mod_id eidolon_repraised is not item namespace','actual_source_chain':['ITEMS DeferredRegister ForgeRegistries.ITEMS + Eidolon.MODID -> addItem supplier -> SilverArmorItem ArmorItem.Type','CLIENT MOD RegisterLayerDefinitions -> SilverArmorModel.createBodyLayer','CLIENT MOD AddLayers -> bakeLayer(SILVER_ARMOR_LAYER) -> shared SILVER_ARMOR_MODEL','IClientItemExtensions.getHumanoidArmorModel -> set slot from actual item getEquipmentSlot -> copyFromDefault -> setupAnim -> return singleton','getArmorTexture overrides material path -> eidolon:textures/entity/silver_armor.png'],'slot_render_lists':{'HEAD':['head'],'CHEST':['body','leftArm','rightArm'],'LEGS':['leftLegging','rightLegging','pelvis'],'FEET':['leftFoot','rightFoot']},'source_pose_limit':'copyFromDefault copies leggings/feet from inherited leg parts before setupAnim; actual visual update order and singleton reuse need runtime validation, not certified by reading source.','excluded_warlock_full_four_slot_claim':'Only hat/cloak/boots registered; no fourth leggings ID invented; dyed colors same design.'})
# Fixed-source screening evidence for another robe source; no whole-family credit.
archive=Path('/tmp/dynasty-hexerei-d54.zip');target=B/'screening';target.mkdir(exist_ok=True);shutil.copyfile(archive,target/'hexerei-fixed-source.zip')
with zipfile.ZipFile(archive) as z:
 n=next(n for n in z.namelist() if n.endswith('/item/ModItems.java'));data=z.read(n);(target/'ModItems.java').write_bytes(data)
 lines=data.decode().splitlines();excerpt='\n'.join(f'{i+1}: {l}' for i,l in enumerate(lines) if 953<=i<=1012);(target/'registration-excerpt.txt').write_text(excerpt+'\n')
save('screening.json',{'repository':'https://github.com/JoeFoxe/Hexerei-1.19','commit':'d46fa9004eade34991b844f1e1e8d8771ed9fcf7','archive_sha256':H(archive.read_bytes()),'entry':n,'entry_sha256':H(data),'conclusion':'Basic witch registers head/chest/boots; leggings commented. Orc/druid four-slot registrations commented. Existing PNGs not proof of native registered full sets. No full-armor credit.','native_armor_art_not_viewed':True})
prior=json.loads((R/'docs/art/armor-space-whole-20261112/combined-semantic-ledger.json').read_text());groups=prior['groups'];selected=[g for g in groups if g['semantic_group'] in ['silver_metal_plume','deepsilver_compact_center_plate','crest_plate_variants','souls_silver_enclosed_plate_family','sterling_padded_metal','complete_skull_feather_harness_armor','creature_hide_shell_vests']]
save('dedup-comparison.json',{'reviewed_prior_namespace_absent':'eidolon' not in {k.split(':')[0] for k in prior['reviewed_case_keys']},'prior_namespace_screen_not_semantic_credit':True,'selected_prior_textual_groups':selected,'judgment':'Silver compact pale metal plate belongs near already reviewed metal/closed-face plate families. Guard rotated45deg/shortshoulders are bounded model distinctions, not independently accepted design novelty. No new group/credit assigned. Warlock fabric is incomplete three-slot context; not four-slot credit.','all_other_prior_plate_crest_feather_hide_groups':'remain in inherited ledger; not claimed to be visually re-reviewed this batch'})
base=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text());assert all(H((R/f).read_bytes())==h for f,h in base.items())
save('verification.json',{'archive_and_28_source_entries_match':True,'source_entries':len(p['entries']),'silver_native_slots':4,'explicit_silver_cubes':10,'in_bounds_raw_uv_rectangles':60,'protected_files_unchanged':len(base),'whole_source_candidate':1,'new_validated_credit':0,'production_changes':0,'game_starts':0,'checklist_deletions':0,'not_runtime_acceptance':True})
print('verified D53: 4slots 10cubes 60rawUV; warlock/hexerei not fullfour; 289protected')
