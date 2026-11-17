from pathlib import Path
from PIL import Image,ImageDraw
import zipfile,json,hashlib,re
B=Path(__file__).resolve().parent; R=B.parents[2];S=B/'source/src/main';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(B/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
p=json.loads((B/'provenance.json').read_text());assert H(Path(p['archive']))==p['archive_sha256']
with zipfile.ZipFile(p['archive']) as z:
 prefix=z.namelist()[0]
 for n,h in p['entries'].items():assert hashlib.sha256(z.read(prefix+n)).hexdigest()==h==H(B/'source'/n)
 source_scan={};hits={}
 for n in z.namelist():
  if n.endswith('.java'):
   data=z.read(n);source_scan[n.removeprefix(prefix)]=hashlib.sha256(data).hexdigest();s=data.decode()
   words=[t for t in ['ArmorRenderer','ArmorFeatureRenderer','BipedEntityModel.getModelData','getArmorTexture'] if t in s]
   if words:hits[n.removeprefix(prefix)]=words
save('bounded-renderer-token-screen.json',{'scope':'Mechanical token screen, not semantic reading credit or proof against reflection/external mixins','tokens':['ArmorRenderer','ArmorFeatureRenderer','BipedEntityModel.getModelData','getArmorTexture'],'java_hashes':source_scan,'hits':hits})
reg=(S/'java/com/github/thedeathlycow/frostiful/registry/FItems.java').read_text();material=(S/'java/com/github/thedeathlycow/frostiful/item/FrostResistantArmorMaterials.java').read_text()
assert 'return "frostiful_" + this.name;' in material
prior=json.loads((R/'docs/art/armor-modular-consumers-20261112/combined-semantic-ledger.json').read_text());assert not any(k.startswith('frostiful:') for k in prior['reviewed_case_keys'])
bindings=[]
for prefix,enum,mat in [('fur','FUR_ARMOR','fur'),('fur_padded_chainmail','FUR_LINED_CHAIN','fur_lined_chainmail')]:
 for part,slot,layer in [('helmet','HELMET',1),('chestplate','CHESTPLATE',1),('leggings','LEGGINGS',2),('boots','BOOTS',1)]:
  item=prefix+'_'+part;const=item.upper();assert re.search(r'Item '+const+r' = new ArmorItem\(\s*FrostResistantArmorMaterials\.'+enum+r',\s*ArmorItem.Type\.'+slot,reg)
  assert f'register("{item}", {const});' in reg
  model=S/f'resources/assets/frostiful/models/item/{item}.json';m=json.loads(model.read_text());assert m['parent']=='minecraft:item/generated' and m['textures']['layer0']==f'frostiful:item/{item}'
  tex=S/f'resources/assets/minecraft/textures/models/armor/frostiful_{mat}_layer_{layer}.png';assert tex.exists()
  with Image.open(tex) as im:assert im.size==(64,32)
  bindings.append({'id':'frostiful:'+item,'native_type':slot,'native_material':enum,'base_icon':m['textures']['layer0'],'native_item_model':str(model.relative_to(B)),'declared_standard_texture_context':'minecraft:textures/models/armor/frostiful_'+mat+f'_layer_{layer}.png','layer':layer,'scope':'Ordinary ArmorItem and material-name source declaration; standard MC1.20.1 context, Fabric renderer actual invocation not runtime-tested','trim_override_count':len(m.get('overrides',[]))})
# Reuse previously fixed local MC1.20.1 generated Forge UV context, without calling it Fabric source.
ctx=json.loads((R/'docs/art/armor-iridium-whole-20261112/context-provenance.json').read_text());assert H(Path(ctx['archive']))==ctx['archive_sha256']
with zipfile.ZipFile(ctx['archive']) as z:
 for n,h in ctx['entries'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 src=z.read('net/minecraft/client/model/HumanoidModel.java').decode()
parts={}
for line in src.splitlines():
 m=re.search(r'addOrReplaceChild\("(\w+)", CubeListBuilder.create\(\).texOffs\((\d+), (\d+)\)(\.mirror\(\))?\.addBox\((.+)',line)
 if m:
  name,u,v,mirror,args=m.groups();args=args.split(', ');parts[name]={'uv':[int(u),int(v)],'dimensions':[float(a.rstrip('F')) for a in args[3:6]],'mirror':bool(mirror)}
assert len(parts)==7
save('uv-context.json',{'prior_fixed_context':ctx,'context_only':'Generated Forge MC1.20.1 geometry/box UV; not exact Fabric source, runtime wear or world face orientation','parts':parts})
slotparts={'HEAD':['head','hat'],'CHEST':['body','right_arm','left_arm'],'LEGS':['body','right_leg','left_leg'],'FEET':['right_leg','left_leg']};regions=[]
for mat in ['fur','fur_lined_chainmail']:
 canvas=Image.new('RGB',(1140,1120),'#555b60');draw=ImageDraw.Draw(canvas);row=0
 for slot,names in slotparts.items():
  tex=S/f'resources/assets/minecraft/textures/models/armor/frostiful_{mat}_layer_{2 if slot=="LEGS" else 1}.png';im=Image.open(tex).convert('RGBA')
  for name in names:
   part=parts[name];u,v=part['uv'];w,h,d=map(int,part['dimensions']);a=u;b=u+d;c=u+d+w;e=u+d+w+w;f=u+d+w+d;g=u+d+w+d+w;y=v+d;end=y+h
   rects={'DOWN':[b,v,c,y],'UP':[c,y,e,v],'WEST':[a,y,b,end],'NORTH':[b,y,c,end],'EAST':[c,y,f,end],'SOUTH':[f,y,g,end]}
   for col,(face,rect) in enumerate(rects.items()):
    x1,y1,x2,y2=rect;crop=im.crop((min(x1,x2),min(y1,y2),max(x1,x2),max(y1,y2)));alpha=crop.getchannel('A');x=10+col*190;yy=10+row*110
    draw.text((x,yy),slot+' '+name,fill='white');draw.text((x,yy+14),face+' '+str(rect),fill='white');k=min(6,150//crop.width,65//crop.height);large=crop.resize((crop.width*k,crop.height*k),Image.Resampling.NEAREST);canvas.paste(large,(x,yy+32),large)
    regions.append({'material':mat,'slot':slot,'part':name,'face_before_mirror':face,'mirror':part['mirror'],'ordered_uv':rect,'opaque_or_translucent_pixels':sum(a>0 for a in alpha.get_flattened_data()),'pixels':crop.width*crop.height})
   row+=1
 canvas.save(B/f'uv-context-{mat}.png')
assert len(regions)==120
save('slot-and-uv-study.json',{'bindings':bindings,'context_source':'uv-context.json','raw_source_regions_not_worn_faces':regions,'limits':['Exact Fabric default renderer body not locally attested','Base untrimmed design only; trim variants not counted','No baked wearer, seam, pose or game acceptance']})
base=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text());assert all(H(R/n)==h for n,h in base.items())
save('verification.json',{'status':'PASS_FIXED_OFFICIAL_SOURCE_ORIGINAL_IMAGES_EIGHT_SLOT_DECLARATIONS_AND_BOUNDED_UV_CONTEXT','fixed_source_entries':len(p['entries']),'whole_base_design_candidates':1,'same_series_chainmail_comparison':1,'four_slot_declarations':8,'native_armor_png_viewed':12,'raw_uv_context_regions':120,'protected_paths_unchanged':len(base),'new_validated_design_credit':0,'gate_met':False,'production_changes':0,'game_starts':0})
print((B/'verification.json').read_text())
