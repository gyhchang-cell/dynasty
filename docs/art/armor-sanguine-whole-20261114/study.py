from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2];P=D.parent/'armor-dark-steel-whole-20261114'
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
T=D/'source/src/main/resources/assets/caverns_and_chasms';G=D/'source/src/generated/resources';C=D/'source/src/main/java/com/teamabnormals/caverns_and_chasms'
# nominal dimensions determine UV, deformations affect geometry only; parent offsets retained.
base=[('head',[0,0],[-4,-8,-4],[8,8,8],False,[0,0,0]),('hat',[32,0],[-4,-8,-4],[8,8,8],False,[0,0,0]),('body',[16,16],[-4,0,-2],[8,12,4],False,[0,0,0]),('right_arm',[40,16],[-3,-2,-2],[4,12,4],False,[-5,2,0]),('left_arm',[40,16],[-1,-2,-2],[4,12,4],True,[5,2,0]),('right_leg',[0,16],[-2,0,-2],[4,12,4],False,[-1.9,12,0]),('left_leg',[0,16],[-2,0,-2],[4,12,4],True,[1.9,12,0])]
extra=[('head/left_horn',[0,0],[-7.25,-12.125,-1],[2,5,2],False,[0,0,0]),('head/right_horn',[24,0],[5.25,-12.125,-1],[2,5,2],False,[0,0,0]),('right_arm/right_shoulder_horn',[32,0],[-3.5,-6.25,-1],[2,3,2],False,[-5,2,0]),('left_arm/left_shoulder_horn',[56,0],[1.5,-6.25,-1],[2,3,2],False,[5,2,0])]
# Same Minecraft1.20.1 source-context ModelPart.Cube UV arithmetic; keep signed UP V.
def faces(uv,sz):
 u,v=uv;x,y,z=sz;return {'DOWN_y_min':[u+z,v,u+z+x,v+z],'UP_y_max':[u+z+x,v+z,u+z+2*x,v],'WEST_x_min':[u,v+z,u+z,v+z+y],'NORTH_z_min':[u+z,v+z,u+z+x,v+z+y],'EAST_x_max':[u+z+x,v+z,u+2*z+x,v+z+y],'SOUTH_z_max':[u+2*z+x,v+z,u+2*z+2*x,v+z+y]}
slots={'HEAD':['head','hat','head/left_horn','head/right_horn'],'CHEST':['body','right_arm','left_arm','right_arm/right_shoulder_horn','left_arm/left_shoulder_horn'],'LEGS':['body','right_leg','left_leg'],'FEET':['right_leg','left_leg']};rows=[]
for slot,names in slots.items():
 layer=2 if slot=='LEGS' else 1;im=Image.open(T/f'textures/models/armor/sanguine_layer_{layer}.png').convert('RGBA')
 for name,uv,origin,sz,mirror,offset in base+extra:
  if name not in names:continue
  deform=[.5,.5,.5] if slot=='LEGS' else [1,1,1]
  if name in ['right_leg','left_leg']:deform=[v-.1 for v in deform]
  if name=='hat':deform=[v+.5 for v in deform]
  if '/left_horn' in name or '/right_horn' in name:deform=[.25,.625,.25]
  if 'shoulder_horn' in name:deform=[.5,.25,.5]
  fs=[]
  for direction,rect in faces(uv,sz).items():
   u0,v0,u1,v1=rect;box=[min(u0,u1),min(v0,v1),max(u0,u1),max(v0,v1)];assert 0<=box[0]<box[2]<=64 and 0<=box[1]<box[3]<=32
   crop=im.crop(box);fs.append({'source_direction':direction,'signed_uv':rect,'raw_crop_rect':box,'nontransparent_pixels':sum(v>0 for v in crop.getchannel('A').getdata()),'pixels':crop.width*crop.height})
  rows.append({'slot':slot,'layer':layer,'part':name,'uv':uv,'nominal_origin':origin,'nominal_size':sz,'deformation':deform,'parent_offset':offset,'mirror':mirror,'faces':fs})
assert len(rows)==14 and sum(len(x['faces']) for x in rows)==84
save('slot-face-uv.json',{'scope':'4 native slots /14 visible-root cube instances (including transparent hat) /84 raw UV face rectangles; NOT84 designs','source_deformation_context':'source OUTER_ARMOR1.0; inner .5 from sameMC1.20.1 Forge47.4.10 mapped source, exact declared Forge47.1.3 binary not loaded','orientation':'Source normal labels; y_min/y_max not renamed world top/bottom. Signed UP V and mirror flags preserved; crop page not final vertex/mirror/pose rasterization.','rows':rows})
out=Image.new('RGB',(1200,60+len(rows)*100),(84,89,94));dr=ImageDraw.Draw(out);dr.text((12,8),'RAW SOURCE UV RECTANGLES / SIGNED UV IN JSON / NOT GAME / MIRRORS NOT BAKED',fill='white')
for i,row in enumerate(rows):
 y=45+i*100;dr.text((10,y),f'{row["slot"]} L{row["layer"]} {row["part"]}',fill='white');im=Image.open(T/f'textures/models/armor/sanguine_layer_{row["layer"]}.png').convert('RGBA')
 for j,f in enumerate(row['faces']):
  crop=im.crop(f['raw_crop_rect']);up=crop.resize((crop.width*4,crop.height*4),Image.Resampling.NEAREST);x=300+j*145;out.paste(up,(x,y+25),up);dr.text((x,y+3),f['source_direction'],fill='white')
out.save(D/'raw-slot-face-crops.png')
assert all(f['nontransparent_pixels']==0 for row in rows if row['part']=='hat' for f in row['faces'])
sourcebindings=[]
for part,slot in [('helmet','HEAD'),('chestplate','CHEST'),('leggings','LEGS'),('boots','FEET')]:
 model=G/f'assets/caverns_and_chasms/models/item/sanguine_{part}.json';a=json.loads(model.read_text());assert a['textures']['layer0']==f'caverns_and_chasms:item/sanguine_{part}';assert len(a['overrides'])==10
 rec=G/f'data/caverns_and_chasms/recipes/sanguine_{part}.json';b=json.loads(rec.read_text());assert b['result']['item']==f'caverns_and_chasms:sanguine_{part}' and b['key']['X']['item']=='caverns_and_chasms:living_flesh'
 sourcebindings.append({'id':b['result']['item'],'slot':slot,'layer':2 if slot=='LEGS' else 1,'custom_model':slot in ['HEAD','CHEST'],'model':str(model),'model_sha256':h(model),'trim_override_count':10,'recipe':b,'recipe_sha256':h(rec)})
save('four-slot-source-binding.json',{'material':'BlueprintArmorMaterial ResourceLocation caverns_and_chasms:sanguine -> getName.toString -> Forge default texture resource path','bindings':sourcebindings,'extra_geometry':'4 child cuboids, no model replacement on LEGS/FEET; singleton baked by INSTANCE with outer deformation','render_property_copy':'Exact declared Forge extension getGenericArmorModel calls copyModelProperties when replacement differs; root pose and visibility forwarded. This is source tracing, not runtime proof.','unverified':['loaded exact Blueprint binary and checksum403','mixin activation and trimmed stack visuals','living_flesh material origin and native crafting','runtime/mirror/seam/pose']})
oldtarget=Path('docs/art/armor-valonite-whole-20261112/current-target-status.json');old=json.loads(oldtarget.read_text());assert old['confirmed_old_crude_redraw_IDs']==[]
save('target-qualification.json',{'prior_status':{'path':str(oldtarget.resolve()),'sha256':h(oldtarget)},'target_count':28,'priority_files':70,'confirmed_old_crude_redraw_IDs':[],'redraw_authorized':False,'reason':'No newer evidence proves a priority target both never-redrawn and crude; all priority hashes checked. Do not infer crude from age or untested worn coherence.','research_applicability':{'primary':'cinnabar current icon/worn material-coherence questions: learn discrete red material/compact four-slot identity, not copying or horn redesign','secondary':'hongmeng premium armor boundary: small features attached to vanilla cube versus excessive shoulder/head extension','cloth_leather_sea_silk':'Does not supply fabric-specific texture credit; continue material-specific research later.'}})
L=json.loads((P/'combined-semantic-ledger.json').read_text());key='caverns_and_chasms:sanguine/default_untrimmed';assert key not in L['reviewed_pending_whole_keys'];matches=[g for g in L['groups'] if g['semantic_group'] in ['organic_flesh_rib_armor_family','dark_rib_chest_variants','giant_monster_visor_horn_variants','dragon_scale_family_conservative','mixed_dark_red_slit_plate','meror_red_kit_variants']]
save('historical-group-comparison.json',{'all_group_names_screened':len(L['groups']),'all_case_keys_screened':len(L['case_to_group']),'closest_stored_observations':matches,'source':str(P/'combined-semantic-ledger.json'),'source_sha256':h(P/'combined-semantic-ledger.json'),'decision':'No new validated credit or learning group. Horn/rib/red-organic overlap remains; namespace/model differences not novelty proof.','scope':'stored observations/keys, not reopening all historic PNG'})
comparisons=[]
for k in L['reviewed_pending_whole_keys']:
 if k in ['thebetweenlands:bone','thebetweenlands:ancient','forbidden_arcanus:mortem','forbidden_arcanus:draco_arcanus','forbidden_arcanus:tyr']:reason='骨/有机/角饰高级甲的结构及材质观察存在交集，不能由红色、角数或模型块数断言独立。'
 elif k.startswith('tconstruct:plate') or k in ['eidolon:silver','thebetweenlands:syrmorite','thebetweenlands:valonite','oreganized:electrum/winged_gold_custom_uv','enderio:dark_steel/default_unpainted_no_faceplate']:reason='同为原版基础短胸直腿分离靴；独立附角与翼饰/面甲/护颊不同，仍需和全部旧有机肋甲/角饰族联合去重。'
 else:reason='旧整套材质/用途记录继续保留；本套的暗红有机材质与局部角饰不代表已独立于全部旧族，图标/图层/组件/状态不单列信用。'
 comparisons.append({'prior_whole_key':k,'comparison':reason})
for x in L.get('pending_whole_configurations',[]):comparisons.append({'prior_whole_key':x['configuration_key'],'comparison':'模块重甲整体与默认四槽甲均只按整体；不由模块数/角块数增加语义设计。'})
save('complete-old-whole-dedup.json',{'prior_pending_whole_keys':len(L['reviewed_pending_whole_keys']),'comparisons':comparisons,'D54_accepted_carry':L['local_independently_accepted_whole_families'],'conclusion':'At most1 new pending source configuration,0 accepted designs; no group split or historical total reset','scope':'All old whole keys compared with stored observations; not claiming old images all re-viewed'})
print({'slot_cube_instances':len(rows),'raw_uv_faces':84,'hat_faces_all_transparent':True,'old_whole_keys_plus_modular':len(comparisons)})
