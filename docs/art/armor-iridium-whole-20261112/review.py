"""Source-bound whole armor study. No mod or game execution."""
from pathlib import Path
import hashlib,json,re,zipfile
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;ROOT=B.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(n,v):(B/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def body(t,name):
 s=t.index(' '+name+'(');s=t.index('    Code:',s);e=t.index('      LineNumberTable:',s);return t[s:e]
def bc(n):return (B/'bytecode/net/mcreator/terramity'/n).read_text()
p=json.loads((B/'provenance.json').read_text());assert sha(Path(p['archive']))==p['archive_sha256']
with zipfile.ZipFile(p['archive']) as z:
 for n,h in p['entries'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h==sha(B/'source'/n)
for n,h in p['disassemblies'].items():assert sha(B/n)==h
ctx=json.loads((B/'context-provenance.json').read_text());assert sha(Path(ctx['archive']))==ctx['archive_sha256']
with zipfile.ZipFile(ctx['archive']) as z:
 for n,h in ctx['entries'].items():assert hashlib.sha256(z.read(n)).hexdigest()==h==sha(B/'context'/n)
reg=bc('init/TerramityModItems.class.txt');static=reg[reg.index('  static {};'):reg.index('BootstrapMethods:')]
assert '// String terramity' in static and 'DeferredRegister.create:' in static
bindings=[]
for i,(part,cls,slot,layer) in enumerate([('helmet','Helmet','HELMET',1),('chestplate','Chestplate','CHESTPLATE',1),('leggings','Leggings','LEGGINGS',2),('boots','Boots','BOOTS',1)]):
 m=re.search(r'String iridium_armor_'+part+r'\n.*?InvokeDynamic #(\d+):get',static,re.S);assert int(m[1])==340+i
 boot=re.search(r'\n  '+str(340+i)+r':.*?(?=\n  \d+:|\Z)',reg[reg.index('BootstrapMethods:'):],re.S).group(0)
 assert f'.lambda$static${338+i}:' in boot
 ctor=body(reg,f'lambda$static${338+i}');assert f'IridiumArmorItem${cls}."<init>"' in ctor
 t=bc(f'item/IridiumArmorItem${cls}.class.txt');own=t[t.index('\n{'):]
 assert f'ArmorItem$Type.{slot}:' in own
 texture=f'terramity:textures/models/armor/iridium__layer_{layer}.png'
 assert f'// String {texture}' in body(t,'getArmorTexture')
 assert 'initializeClient(' not in own and 'getHumanoidArmorModel(' not in own
 icon=json.loads((B/f'source/assets/terramity/models/item/iridium_armor_{part}.json').read_text())
 assert icon['textures']['layer0']==f'terramity:item/iridium_{part}'
 bindings.append({'id':f'terramity:iridium_armor_{part}','bootstrap':340+i,'supplier':f'lambda$static${338+i}','class':cls,'type':slot,'texture':texture,'icon':icon['textures']['layer0']})
baseclass=bc('item/IridiumArmorItem.class.txt');assert 'extends net.minecraft.world.item.ArmorItem' in baseclass
assert 'initializeClient(' not in baseclass and 'getHumanoidArmorModel(' not in baseclass
source=(B/'context/net/minecraft/client/model/HumanoidModel.java').read_text()
parts={}
for line in source.splitlines():
 m=re.search(r'addOrReplaceChild\("(\w+)", CubeListBuilder.create\(\).texOffs\((\d+), (\d+)\)(\.mirror\(\))?\.addBox\((.+)',line)
 if not m:continue
 name,u,v,mirror,args=m.groups();args=args.split(', ');dims=[float(a.rstrip('F')) for a in args[3:6]]
 parts[name]={'uv':[int(u),int(v)],'dimensions':dims,'mirror':bool(mirror)}
assert len(parts)==7 and parts['body']['dimensions']==[8,12,4] and parts['left_arm']['mirror']
cs=(B/'context/net/minecraft/client/model/geom/ModelPart.java').read_text()
# Source-reading contract: rectangle coordinates, not world face orientation after mirrored geometry.
for direction,coords in {'DOWN':'f5, f10, f6, f11','UP':'f6, f11, f7, f10','WEST':'f4, f11, f5, f12','NORTH':'f5, f11, f6, f12','EAST':'f6, f11, f8, f12','SOUTH':'f8, f11, f9, f12'}.items():
 assert f'{coords}, p_273591_, p_273313_, p_273589_, Direction.{direction}' in cs
layer=(B/'context/net/minecraft/client/renderer/entity/layers/HumanoidArmorLayer.java').read_text()
slotparts={'HEAD':['head','hat'],'CHEST':['body','right_arm','left_arm'],'LEGS':['body','right_leg','left_leg'],'FEET':['right_leg','left_leg']}
field={'right_arm':'rightArm','left_arm':'leftArm','right_leg':'rightLeg','left_leg':'leftLeg'}
for slot,ns in slotparts.items():
 section=layer[layer.index('case '+slot+':'):];section=section.split('break;',1)[0] if slot!='FEET' else section.split('\n      }',1)[0]
 for n in ns:assert f'.{field.get(n,n)}.visible = true;' in section
faces=[];canvas=Image.new('RGB',(1140,1120),'#555b60');draw=ImageDraw.Draw(canvas)
row=0
for slot,ns in slotparts.items():
 im=Image.open(B/f'source/assets/terramity/textures/models/armor/iridium__layer_{2 if slot=="LEGS" else 1}.png').convert('RGBA')
 for name in ns:
  part=parts[name];u,v=part['uv'];w,h,d=map(int,part['dimensions'])
  f4=u;f5=u+d;f6=u+d+w;f7=u+d+w+w;f8=u+d+w+d;f9=u+d+w+d+w;f10=v;f11=v+d;f12=v+d+h
  rects={'DOWN':[f5,f10,f6,f11],'UP':[f6,f11,f7,f10],'WEST':[f4,f11,f5,f12],'NORTH':[f5,f11,f6,f12],'EAST':[f6,f11,f8,f12],'SOUTH':[f8,f11,f9,f12]}
  for col,(face,rect) in enumerate(rects.items()):
   a,b,c,e=rect;crop=im.crop((min(a,c),min(b,e),max(a,c),max(b,e)));alpha=crop.getchannel('A');x=10+col*190;y=10+row*110
   draw.text((x,y),slot+' '+name,fill='white');draw.text((x,y+14),face+' '+str(rect),fill='white')
   k=min(6,150//crop.width,65//crop.height);large=crop.resize((crop.width*k,crop.height*k),Image.Resampling.NEAREST);canvas.paste(large,(x,y+32),large)
   faces.append({'slot':slot,'part':name,'direction_label_before_mirror':face,'mirror':part['mirror'],'ordered_uv':rect,'nonzero_alpha':sum(a>0 for a in alpha.get_flattened_data()),'pixels':crop.width*crop.height})
  row+=1
canvas.save(B/'native-uv-regions.png')
cap={}
for l in [1,2]:
 im=Image.open(B/f'source/assets/terramity/textures/models/armor/iridium__layer_{l}.png').convert('RGBA')
 cap[str(l)]={}
 for n,rect in {'arm_end_cap':[48,16,52,20],'arm_side_end_west':[40,31,44,32],'arm_side_end_north':[44,31,48,32],'arm_side_end_east':[48,31,52,32],'arm_side_end_south':[52,31,56,32]}.items():
  a=im.crop(rect).getchannel('A');cap[str(l)][n]={'rect':rect,'nonzero_alpha':sum(x>0 for x in a.get_flattened_data()),'pixels':a.width*a.height}
base=json.loads((ROOT/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text())
assert all(sha(ROOT/n)==h for n,h in base.items())
images={n:list(Image.open(B/'source'/n).size) for n in p['entries'] if n.endswith('.png')};assert len(images)==6
study={'case':'terramity:iridium_armor','bindings':bindings,'native_png_actually_viewed':images,'native_model_context':parts,'uv_regions':faces,'uv_scope':'60 source rectangle crops; UP ordered V reversed retained; raw crop not a worn-face projection; left/right mirrored source not proof of world orientation or seams','sleeve_boundary_alpha':cap,'visual_review':'whole-native-source.png and native-uv-regions.png actually viewed by view_image in D47; source region sheet is not wearing acceptance','semantic_dedup':{'existing_case':True,'existing_group':'vanilla_outline_elemental_palette','new_names':0,'new_groups':0,'new_validated_design_credit':0},'observations':['短宽胸甲、倒U盔口和分开的短靴维持原版身份；粉紫主面、暗紫窄侧边和米白成片高光形成三层材料。','胸图标亮面从左肩连至胸上部，未用满图细点；裤中央通道和靴间透明区明确，主体未挤成整套人台。','穿戴胸正背与臂的亮色块更碎，原图并非全都值得借鉴；修布皮甲不应照搬金属高光或粉色。','L1臂端盖[48,16,52,20)和四侧末行均透明，材料只留肩部；与D2五套端盖16/16但四侧末行透明的情况不同，不把空端盖补成一片实色。','只学习原版比例、亮主面/暗侧面的取舍与收边；不复制作者原图，不把同模板换色当新设计。'], 'limits':['Local generated Forge source context, not upstream provenance attestation','Native rectangles and static mod consumers are not actual hook/mixin or equipment runtime acceptance','No new production; applicable1000 validated independent designs gate remains unmet']}
emit('whole-reference-study.json',study)
emit('verification.json',{'result':'PASS_BOUNDED_STATIC_CONSUMERS_AND_SOURCE_UV_REGIONS','native_entries':len(p['entries']),'viewed_whole_png':6,'slots':4,'source_uv_region_crops':len(faces),'protected_paths_unchanged':len(base),'reference_gate_met':False,'production_changes':0,'game_starts':0,'checklist_deletions':0})
print('PASS 17 native entries / four slot bindings / 60 source UV crops / 289 protected')
