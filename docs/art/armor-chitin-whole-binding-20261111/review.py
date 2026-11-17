"""Finite original-class disassembly correspondence; never loads mod code."""
from pathlib import Path
import json,re,hashlib
from PIL import Image
D=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return (D/'bytecode'/n).read_text()
def method(t,signature):
 lines=t.splitlines(); start=next(i for i,l in enumerate(lines) if l.startswith('  ') and not l.startswith('   ') and signature in l)
 end=next((i for i in range(start+1,len(lines)) if re.match(r'^  (public|private|protected|static)\b',lines[i])),len(lines))
 return '\n'.join(lines[start:end])
def code(t):return t.split('    Code:\n',1)[1].split('      LineNumberTable:',1)[0]
reg=load('PathogenModItems.class.txt');static=method(reg,'static {};')
assert re.search(r'// String pathogen\n[^\n]+DeferredRegister.create:',static)
rows=[]
expected={'Helmet':('HEAD',{'head':'Head'}),'Chestplate':('CHEST',{'body':'Body','left_arm':'LeftArm','right_arm':'RightArm'}),'Leggings':('LEGS',{'left_leg':'LeftLeg','right_leg':'RightLeg'}),'Boots':('FEET',{'left_leg':'leftBoot','right_leg':'rightBoot'})}
keys={'head','hat','body','right_arm','left_arm','right_leg','left_leg'}
for index,(part,(slot,parts)) in enumerate(expected.items()):
 suffix=part.lower();rid='hardened_chitin_armor_aquatic_'+suffix;b=102+index;lam=101+index
 assert re.search(r'// String '+rid+r'\n[^\n]+InvokeDynamic #'+str(b)+r':get:.*\n[^\n]+DeferredRegister.register:',static)
 bootstrap=reg.split('\n  '+str(b)+': ',1)[1].split('\n  '+str(b+1)+': ',1)[0]
 assert 'REF_invokeStatic en/predator/pathogenmonsterplague/init/PathogenModItems.lambda$static$'+str(lam)+':' in bootstrap
 supplier=method(reg,'lambda$static$'+str(lam)+'(')
 assert 'HardenedChitinArmorAquaticItem$'+part+'."<init>":()V' in code(supplier)
 cl=load('HardenedChitinArmorAquaticItem$'+part+'.class.txt')
 ctor=method(cl,'HardenedChitinArmorAquaticItem$'+part+'();')
 assert 'EquipmentSlot.'+slot+':' in code(ctor)
 client=code(method(cl,' initializeClient('))
 assert 'HardenedChitinArmorAquaticItem$'+part+'$1' in client and 'Consumer.accept:' in client
 wear=code(method(cl,' getArmorTexture('));atlas='pathogen:textures/entities/armor_hardened_aquatic.png'
 assert atlas in wear and 'areturn' in wear and 'if' not in wear
 ext=load('HardenedChitinArmorAquaticItem$'+part+'$1.class.txt');model=code(method(ext,' getHumanoidArmorModel('))
 actual={};matches=list(re.finditer(r'// String (head|hat|body|right_arm|left_arm|right_leg|left_leg)\n',model))
 for i,m in enumerate(matches):
  chunk=model[m.end():matches[i+1].start() if i+1<len(matches) else model.index('InterfaceMethod java/util/Map.of:')]
  fields=re.findall(r'getfield[^\n]+Modelhardened_chitin_armor\.([A-Za-z]+):',chunk)
  if fields:
   assert len(fields)==1 and 'EntityModelSet.m_171103_:' in chunk and 'Modelhardened_chitin_armor.LAYER_LOCATION:' in chunk
   actual[m.group(1)]=fields[0]
  else:assert 'Collections.emptyList:' in chunk and 'Collections.emptyMap:' in chunk
 assert set(m.group(1) for m in matches)==keys and actual==parts
 path='assets/pathogen/models/item/'+rid+'.json';j=json.loads((D/'source'/path).read_text());tex=j['textures']['layer0'];ns,name=tex.split(':');png='assets/'+ns+'/textures/'+name+'.png';assert Image.open(D/'source'/png).size==(16,16)
 rows.append({'registered_id':'pathogen:'+rid,'bootstrap':b,'supplier':'lambda$static$'+str(lam),'class':'HardenedChitinArmorAquaticItem$'+part,'equipment_slot':slot,'icon_model':path,'native_icon':png,'native_icon_size':[16,16],'model_parts':actual,'empty_humanoid_parts':sorted(keys-actual.keys()),'wear_texture':atlas,'disassembly': 'bytecode/HardenedChitinArmorAquaticItem$'+part+'.class.txt','extension_disassembly':'bytecode/HardenedChitinArmorAquaticItem$'+part+'$1.class.txt'})
model=load('Modelhardened_chitin_armor.class.txt');layer=code(method(model,'static {};'));assert all('// String '+s in layer for s in ['pathogen','modelhardened_chitin_armor','main'])
body=code(method(model,' createBodyLayer('));assert re.search(r'sipush\s+128\n[^\n]+sipush\s+128\n[^\n]+LayerDefinition.m_171565_',body)
assert Image.open(D/'source/assets/pathogen/textures/entities/armor_hardened_aquatic.png').size==(128,128)
registry=load('PathogenModModels.class.txt');mr=code(method(registry,' registerLayerDefinitions('))
assert re.search(r'Modelhardened_chitin_armor.LAYER_LOCATION:.*\n[^\n]+InvokeDynamic #1:get:.*\n[^\n]+registerLayerDefinition:',mr)
assert 'net.minecraftforge.eventbus.api.SubscribeEvent' in registry and 'Bus;.MOD' in registry and 'Dist;.CLIENT' in registry
bs=registry.split('\n  1: ',1)[1].split('\n  2: ',1)[0];assert 'REF_invokeStatic en/predator/pathogenmonsterplague/client/model/Modelhardened_chitin_armor.createBodyLayer:' in bs
out={'scope':'既有甲壳族 aquatic 代表整套绑定补齐；1.19.2参考不当1.20.1运行证明','case':'pathogen:hardened_chitin_armor_aquatic','group':'complete_chitin_rib_shell_flared_hip','slots':rows,'model_layer':'pathogen:modelhardened_chitin_armor#main','layer_dimensions':[128,128],'layer_registration':'PathogenModModels CLIENT/MOD SubscribeEvent -> bootstrap1 -> createBodyLayer','visual_review':{'page':'aquatic-whole-native-source.png','actually_viewed':True,'newly_created_artwork':False,'native_pixels_previously_reviewed':True,'observations':['头盔图标以深色甲壳形成紧凑面罩、顶部阶梯棱角；青色亮簇集中在额面，不铺满主体。','胸甲短宽，肩部横向阶梯与胸部三条断开的亮甲肋可辨；裤装上下有明显宽窄变化，双腿仍分开。','靴图标细长直立，左右分离，各有一块亮青簇；不能照图标推定原版靴UV。','128图集使用暗绿大面积基底，青绿离散甲片亮部；此处只看原图，不虚构各面实际映射或穿戴效果。'],'application':['材质亮部围绕结构集中分区，不把噪点撒满甲面。','先取实际分槽部件再判断袖口、腰腿接缝；此例靴部与腿部独立，不能套原版L1/L2。','仅学习像素簇/层级方法，不复制第三方原图、几何或UV。']},'limits':['未逐方块/逐面恢复全部模型UV','未实机穿戴/五视角验收','八环境色不拆八个独立设计','未运行mod类或游戏；javap只读字节码','PNC root bridge及额外wear consumer缺口不由本轮补齐'],'new_name_families':0,'new_conservative_groups':0,'new_validated_independent_design_credit':0,'reference_gate_met':False,'production_changes':0}
(D/'static-whole-bindings.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('PASS four slots, original icon links, custom 128 atlas/model layer, dedicated boot parts')
