from pathlib import Path
import re,json,hashlib,zipfile
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[2];H=lambda b:hashlib.sha256(b).hexdigest()
def save(n,d):(B/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=json.loads((B/'provenance.json').read_text());assert H((B/'roots-fixed-source.zip').read_bytes())==p['archive_sha256']
with zipfile.ZipFile(B/'roots-fixed-source.zip') as z:
 root=z.namelist()[0]
 for rel,h in p['entries'].items():assert H((B/'source'/rel).read_bytes())==h==H(z.read(root+rel))
ctx=json.loads((B/'dependency-context/provenance.json').read_text());assert H((B/'dependency-context/ModelArmorBase.java').read_bytes())==ctx['sha256']
for n,v in ctx['additional_sources'].items():assert H((B/'dependency-context'/n).read_bytes())==v['sha256']
def get(n):
 q=list((B/'source').rglob(n));assert len(q)==1;return q[0].read_text()
reg=get('ModItems.java');allparts={};bindings=[];nets=[]
for family,cls,expected in [('wildwood','ModelWildwoodArmor',60),('sylvan','ModelSylvanArmor',53)]:
 s=get(cls+'.java'); matches=list(re.finditer(r'(\w+) = new ModelRenderer\(this, (\d+), (\d+)\);',s));parts=[]
 parents={child:parent for parent,child in re.findall(r'(\w+)\.addChild\((\w+)\)',s)}
 for i,m in enumerate(matches):
  name,u,v=m.groups();u,v=int(u),int(v);end=matches[i+1].start() if i+1<len(matches) else len(s);block=s[m.start():end]
  box=re.search(name+r'\.addBox\(([^)]+)\)',block);assert box
  nums=[float(x.strip().rstrip('fF')) for x in box.group(1).split(',')];assert len(nums)==6
  w,h,d=map(int,nums[3:]);rect=[u,v,u+2*w+2*d,v+d+h];assert rect[2]<=64 and rect[3]<=64
  pivot=re.search(name+r'\.setRotationPoint\(([^)]+)\)',block).group(1)
  rot=re.search(r'setRotation\('+name+r', ([^)]+)\)',block).group(1)
  mirror=re.search(name+r'\.mirror = (true|false);',block);assert mirror
  parts.append({'name':name,'parent':parents[name],'origin':nums[:3],'size':nums[3:],'uv':[u,v],'net_bounds':rect,'pivot_literal':pivot,'rotation_radians_literal':rot,'mirror_assignment':mirror.group(1),'mirror_assignment_after_addBox':mirror.start()>box.start(),'baked_mirror_not_assumed':True,'constructor_block':block.split('setRotation('+name,1)[0]})
 assert len(parts)==expected,(family,len(parts));allparts[family]=parts
 unique={tuple(c['uv']+c['size']):c for c in parts}
 atlas=next(q for q in (B/'source').rglob(family+'_armor.png'));im=Image.open(atlas).convert('RGBA');assert im.size==(64,64)
 page=Image.new('RGB',(1200,((len(unique)+5)//6)*170+45),'#555b60');dr=ImageDraw.Draw(page);dr.text((10,8),family+' raw box-net texture patches; NOT game, face orientations/mirror NOT certified',fill='white')
 for i,(key,c) in enumerate(unique.items()):
  x=10+i%6*200;y=40+i//6*170;rect=c['net_bounds'];t=im.crop(tuple(rect));k=min(180//t.width,120//t.height);t=t.resize((t.width*k,t.height*k),Image.Resampling.NEAREST);page.paste(t,(x,y+25),t);dr.text((x,y),str(key),fill='white')
 page.save(B/(family+'-raw-net-patches.png'));nets.append({'family':family,'source_box_declarations':len(parts),'unique_uv_size_patches':len(unique),'atlas':[64,64]})
 item_cls='ItemWildwoodArmor' if family=='wildwood' else 'ItemSylvanArmor';item=get(item_cls+'.java');assert 'Model'+family.capitalize()+'Armor.getInstance(armorSlot)' in item
 assert ':textures/models/armor/'+family+'_armor.png' in item
 for part,slot in [('helmet','HEAD'),('chestplate','CHEST'),('leggings','LEGS'),('boots','FEET')]:
  name=family+'_'+part;line=next(l.strip() for l in reg.splitlines() if 'event.addItem('+name+' =' in l);assert 'EntityEquipmentSlot.'+slot in line
  model=json.loads(next(q for q in (B/'source').rglob(name+'.json')).read_text());assert model['textures']['layer0']=='roots:items/'+name
  bindings.append({'native_id':'roots:'+name,'slot':slot,'registration':line,'inventory_model':model})
save('box-texture-correspondence.json',{'models':allparts,'totals':nets,'scope':'Raw source constructor/texture net evidence only; NOT current Minecraft1.20.1 UV contract or world-oriented face bake','root_child_corrections':{'wildwood':{'chest_children_Y':-1,'leg_boot_children_Y':-12,'armorScale':1.2},'sylvan':{'head_children_Y':1,'leg_boot_children_Y':-12,'armorScale':1.1}},'mirror_caveat':'ModelRenderer.mirror=true appears AFTER addBox; final baked mirror cannot be inferred from final field. ModelBox construction contract/version remains unverified.'})
save('static-bindings.json',{'native_items':bindings,'paths':['Roots RegistryManager RegisterContentEvent -> ModItems.registerItems -> event.addItem(new item with named slot)','Item constructor sets Roots.MODID native registry name; event.addItem appends shared list','Fixed MysticalLib source context LibRegistry.initAll posts event, registerItems iterates items into actual registry','LibRegistry ModelRegistryEvent -> IModeledObject.initModel -> ModelLoader.setCustomModelResourceLocation(id, handler)','Item getArmorTexture -> dedicated family64x64; getArmorModel -> per-slot singleton model','ModelArmorBase fixed source context: constructor sets64x64 before subclass boxes; render sets slot showModel, pose then root render branches'], 'base_context_slot_roots':{'HEAD':['head'],'CHEST':['chest','armR','armL'],'LEGS':['legR','legL'],'FEET':['bootR','bootL']},'not_plain_L1_L2':True,'bounded_limits':['Roots manifest sets MysticalLib minimum1.13, actual loaded dependency not pinned; fixed upstream context is not proof of exact runtime match','ModelResourceLocation handler consumer mapping not executed','ModelBox mirror/build timing and world-facing seams not attested','old1.12.2 models are reference only, not drop-in1.20.1 assets']})
prior=json.loads((R/'docs/art/armor-silver-whole-20261112/combined-semantic-ledger.json').read_text());seen=set(prior['reviewed_case_keys'])|set(prior.get('reviewed_pending_whole_keys',[]));assert not any(k.startswith('roots:') for k in seen)
groups=[g for g in prior['groups'] if g['semantic_group'] in ['wooden_plate','ironwood_metal_rivets','steeleaf_leaf_plate','jungle_leaf_headgear','forest_troll_hide','complete_skull_feather_harness_armor']]
save('dedup-comparison.json',{'prior_namespace_absent':True,'prior_material_group_records':groups,'decision':'Two related wildwood/sylvan branch-and-panel whole sets treated as ONE pending learning family, not two accepted designs. Wood plate/leaf/bone materials overlap old groups; many little roots are source complexity, not semantic credit. Independent novelty/applicability unaccepted.','new_validated_credit':0,'not_repeated_review':'Prior groups are textual comparison, not claimed new pixel review'})
base=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text());assert all(H((R/f).read_bytes())==h for f,h in base.items())
save('verification.json',{'source_entries_verified':len(p['entries']),'dependency_source_hashes_verified':3,'native_slots':8,'whole_learning_family_candidate':1,'source_cubes_by_family':{k:len(v) for k,v in allparts.items()},'box_net_bounds_within64':True,'original_png':10,'protected_files_unchanged':len(base),'new_validated_credit':0,'reference_gate_met':False,'production_changes':0,'game_starts':0,'checklist_deletions':0})
print('verified D54',nets,'8native IDs 289protected unchanged')
