from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;P=D.parent/'armor-hazmat-whole-20261114'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):(D/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
assert not (D/'prior-hazmat-comparison.json').exists()
paths=[]
for folder,prefix in [(P,'hazmat'),(D,'beekeeper')]:
 for s in ['helmet','chestplate','leggings','boots']:
  paths.append(folder/'source/src/main/resources/assets/thermal/textures/item'/f'{prefix}_{s}.png')
out=Image.new('RGB',(800,440),'#555b60');dr=ImageDraw.Draw(out);dr.text((8,8),'PRIOR HAZMAT / NEW BEEKEEPER / NATIVE PIXELS / NOT GAME',fill='white')
for i,p in enumerate(paths):
 im=Image.open(p).convert('RGBA').resize((160,160),Image.Resampling.NEAREST);x=i%4*200;y=40+i//4*200;out.paste(im,(x+20,y),im);dr.text((x+8,y+166),p.stem,fill='white')
out.save(D/'prior-whole-comparison.png')
rows=[]
for suffix in ['helmet','chestplate','leggings','boots']:
 a,b=[Image.open(folder/'source/src/main/resources/assets/thermal/textures/item'/f'{prefix}_{suffix}.png').convert('RGBA') for folder,prefix in [(P,'hazmat'),(D,'beekeeper')]]
 rows.append({'part':suffix,'same_size':a.size==b.size,'same_alpha':a.getchannel('A').tobytes()==b.getchannel('A').tobytes(),'rgba_equal':a.tobytes()==b.tobytes(),'changed_rgba_pixels':sum(x!=y for x,y in zip(a.get_flattened_data(),b.get_flattened_data()))})
for layer in [1,2]:
 a,b=[Image.open(folder/'source/src/main/resources/assets/thermal/textures/models/armor'/f'{prefix}_layer_{layer}.png').convert('RGBA') for folder,prefix in [(P,'hazmat'),(D,'beekeeper')]]
 rows.append({'part':f'layer{layer}','same_alpha':a.getchannel('A').tobytes()==b.getchannel('A').tobytes(),'changed_rgba_pixels':sum(x!=y for x,y in zip(a.get_flattened_data(),b.get_flattened_data()))})
im=Image.open(D/'source/src/main/resources/assets/thermal/textures/models/armor/beekeeper_layer_1.png').convert('RGBA');face=im.crop((8,8,16,16));partial=[(x,y) for y in range(im.height) for x in range(im.width) if 0<im.getpixel((x,y))[3]<255]
save('prior-hazmat-comparison.json',{'rows':rows,'new_credit':0,'not_inferred_from_difference':'Byte/alpha difference does not establish independent whole-design credit','face_rectangle':[8,8,16,16],'face_alpha':{'transparent':sum(v==0 for v in face.getchannel('A').get_flattened_data()),'opaque':sum(v==255 for v in face.getchannel('A').get_flattened_data())},'partial_alpha_values':sorted({im.getpixel(x)[3] for x in partial}),'partial_alpha_pixels':partial,'runtime_blending_verified':False})
sources=[P/'source/gradle.properties',P/'dependency/gradle.properties',P/'source/src/main/java/cofh/thermal/core/init/registries/TCoreItems.java',P/'source/src/main/java/cofh/thermal/lib/util/ThermalIDs.java',P/'source/src/main/java/cofh/thermal/core/util/RegistrationHelper.java',P/'source/src/main/java/cofh/thermal/core/ThermalCore.java',P/'dependency/src/main/java/cofh/core/common/item/ArmorItemCoFH.java',P/'dependency/src/main/java/cofh/lib/common/item/ArmorMaterialCoFH.java',P/'dependency/src/main/java/cofh/core/client/renderer/entity/model/ArmorFullSuitModel.java',P/'dependency/src/main/java/cofh/core/CoFHCore.java']
save('reused-consumer-context.json',{'inputs':[{'path':str(p),'sha256':sha(p)} for p in sources], 'scope':'Exact fixed sources already actually read in D76; same model selector reread in new BeekeeperArmorItem; no new implementation credit for repeated shared code','published_binary_identity_verified':False})
print('Comparison saved; transparent net pixels:',sum(v==0 for v in face.getchannel('A').get_flattened_data()))
