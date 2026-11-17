from pathlib import Path
import json,re,hashlib,zipfile
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2];H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def t(n):return (D/'bytecode'/(n+'.txt')).read_text()
def method(n,s):
 ls=t(n).splitlines();a=next(i for i,l in enumerate(ls) if re.match(r'^  (public|private|protected|static)',l) and s in l);b=next((i for i in range(a+1,len(ls)) if re.match(r'^  (public|private|protected|static)',ls[i])),len(ls));return '\n'.join(ls[a:b]).split('    Code:\n',1)[1].split('      LineNumberTable:',1)[0]
def bs(n,i):return ('\n'+t(n).split('BootstrapMethods:\n',1)[1]).split('\n  '+str(i)+': ',1)[1].split('\n  '+str(i+1)+': ',1)[0]
p=json.loads((D/'provenance.json').read_text());assert H(Path(p['archive']))==p['archive_sha256']
with zipfile.ZipFile(p['archive']) as z:
 for f in p['files']:
  assert H(D/f['local'])==f['sha256']==hashlib.sha256(z.read(f['entry'])).hexdigest()
  if 'disassembly' in f:assert H(D/f['disassembly'])==f['disassembly_sha256']
reg=t('ModelProviderRegistry');rows=[]
for cap,slot,part,typ,ids in [('Head','HEAD','head','HELMET',[48,49]),('Chest','CHEST','chest','CHESTPLATE',[50,51,52]),('Legs','LEGS','legs','LEGGINGS',[53,54]),('Feet','FEET','feet','BOOTS',[55,56])]:
 blocks=reg.split('// String japanese_light_armor\n')[1:];block=next(b.split('invokestatic',1)[0] for b in blocks if 'EquipmentSlot.'+slot+':' in b.split('invokestatic',1)[0])
 assert all('InvokeDynamic #'+str(i)+':' in block for i in ids)
 model=cap+'JapaneseLightArmorModel';assert model+'."<init>":' in bs('ModelProviderRegistry',ids[0])
 assert model+'.createLayerDefinition:' in bs('ModelProviderRegistry',ids[1])
 if cap=='Chest':assert model+'.createSlimLayerDefinition:' in bs('ModelProviderRegistry',ids[2])
 item=t('ItemRegistry');assert re.search(r'// String japanese_light_armor\n[^\n]+JAPANESE_LIGHT[^\n]*\n[^\n]+ArmorItem\$Type\.'+typ+':',item)
 jpath='assets/armoroftheages/models/item/japanese_light_armor_'+part+'.json';j=json.loads((D/'source'/jpath).read_text());tex=j['textures']['layer0'];ns,path=tex.split(':');icon='assets/'+ns+'/textures/'+path+'.png';assert Image.open(D/'source'/icon).size==(16,16)
 uv={}
 for fn in ['createLayerDefinition()']+(['createSlimLayerDefinition()'] if cap=='Chest' else []):
  code=method(model,fn);assert re.search(r'bipush\s+64\n[^\n]+bipush\s+32\n[^\n]+invokestatic[^\n]+LayerDefinition',code)
  ls=code.splitlines();pairs=[]
  def val(l):
   if 'iconst_' in l:return int(re.search(r'iconst_(\d)',l).group(1))
   return int(re.search(r'(?:bipush|sipush)\s+(-?\d+)',l).group(1))
  for i,l in enumerate(ls):
   if 'invokevirtual' in l and 'm_171514_:' in l:pairs.append([val(ls[i-2]),val(ls[i-1])])
  uv[fn]=pairs
 rows.append({'id':'armoroftheages:japanese_light_armor_'+part,'equipment_slot':slot,'model_class':model,'provider_bootstraps':ids,'icon':icon,'native_icon_sha256':H(D/'source'/icon),'native_atlas':'armoroftheages:textures/models/armor/japanese_light_armor.png','alternate_atlas':'armoroftheages:textures/models/armor/japanese_light_armor_slim.png' if cap=='Chest' else None,'UV_start_pairs_only_not_full_faces':uv,'factory_dimensions':[64,32]})
assert 'DeferredRegister.register:' in method('ArmorOfTheAgesForge$ItemRegistryImpl','register(java.lang.String, net.minecraft.world.item.ArmorMaterial')
assert 'ForgeHumanoidArmorItem."<init>":' in method('ArmorOfTheAgesForge$ItemRegistryImpl','lambda$register$1(')
assert '\\u0001_\\u0001' in bs('ArmorOfTheAgesForge$ItemRegistryImpl',1)
assert 'ModelProviderRegistry.REGISTRY:' in method('HumanoidArmorItem',' getModelProvider(')
assert 'getModelProvider:' in method('ForgeHumanoidArmorItem',' getArmorTexture(') and 'ArmorModelProvider.getTexture:' in method('ForgeHumanoidArmorItem',' getArmorTexture(')
assert 'getArmorModel:' in method('ForgeHumanoidArmorItem$1',' getHumanoidArmorModel(')
assert 'textures/models/armor/\\u0001.png' in bs('ArmorModelProvider',1) and 'textures/models/armor/\\u0001_slim.png' in bs('ArmorModelProvider$MixedArmorModelProvider',1)
assert 'isSlim:' in method('ArmorModelProvider$MixedArmorModelProvider',' getTexture(')
slim=method('ArmorModelProvider',' isSlim(');assert all(s in slim for s in ['usePreferredModel','CURRENT_PREFERRED_MODEL_MAP','ignoredSynchronizedPreferredModel','// String slim'])
base=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text());assert len(base)==289 and all(H(R/n)==h for n,h in base.items())
out={'case':'armoroftheages:japanese_light_armor','group':'samurai_plate_variants_conservative','scope':'与此前长袍/甲壳整体不同的既有轻型横片甲；四件原图/专用UV起点/消费者补齐','rows':rows,'native_png_actually_viewed':6,'source_page':'whole-native-source.png','source_page_sha256':H(D/'whole-native-source.png'),'alternate_selection':'仅Chest登记MixedArmorModelProvider；isSlim先检查本地preferred开关，再检查允许的同步preferred映射，再回退玩家skin slim；不是只由皮肤宽度决定','visual_observations':['绑额以两三条米褐横块区别头盔，侧边布结比头主体小；它是额带，不可当普通全覆盖头盔范本。','胸甲用四段棕黑横片与浅腰带区分硬片/织物，肩带只保留两条窄布段；裤部短而两腿分开，靴长筒深边。','常规图集有狭长布带岛、黑棕大块胸面、横排绑片和独立脚腿条，64×32尺寸不代表原版通用甲UV。','备用图上身区域与常规不一致，不能只把肩臂UV简单平移；胸模型另有breast子件。'], 'applications':['朴素甲靠少量横片留缝、腰带和明暗面辨材料，不靠密集亮点。','布条和皮甲分区必须随真实部件UV；类似袖口问题先分模型模式/消费者再动像素。','借鉴低密度分片与颜色重心，不复制武士纹样、图像或几何；不直接给Dynasty增加身体结构。'],'limits':['仅静态注册/模型供应器/UV起点关系，不是每个方块各面已验','未执行游戏/穿戴/五视角；模型层事件实际注册与缓存构造生命周期仍待验','标准/备用图为同套适配不算两设计；四部件/19个UV起点不算设计','本套已在历史研究名录中，本轮不重复增加名称或独立信用','同族已有o_yoroi，不凭轻重、配色或饰结扩增独立设计'],'protected_paths_unchanged':289,'native_entries_verified':len(p['files']),'new_design_credit':0,'reference_gate_met':False,'production_changes':0,'game_starts':0,'checklist_deletions':0}
(D/'whole-reference-study.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('PASS 4 slots / actual provider bootstraps / 5 UV factory entries / 6 viewed PNG / 289 protected paths')
