"""Bounded fixed native-source verification; never launches game/mod classes."""
from pathlib import Path
import hashlib,json,re,zipfile
from PIL import Image
B=Path(__file__).resolve().parent
ROOT=B.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(n,v): (B/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bc(n):return (B/'bytecode/net/mcreator/sonsofsins'/n).read_text()
def body(t,name):
    start=t.index(' '+name+'(')
    s=t.index('    Code:',start)
    e=t.index('      LineNumberTable:',s)
    return t[s:e]
p=json.loads((B/'provenance.json').read_text())
assert sha(Path(p['archive']))==p['sha256']
with zipfile.ZipFile(p['archive']) as z:
    for n,h in p['entries'].items():
        assert hashlib.sha256(z.read(n)).hexdigest()==h==sha(B/'source'/n)
for n,h in p['disassemblies'].items(): assert sha(B/n)==h
reg=bc('init/SonsOfSinsModItems.class.txt');static=reg[reg.index('  static {};'):reg.index('BootstrapMethods:')]
assert '// String sons_of_sins' in static and 'DeferredRegister.create:' in static
bindings=[]
for i,(part,cls,slot,texture) in enumerate([
 ('helmet','Helmet','HELMET','entities/soul_steel_helmet'),
 ('chestplate','Chestplate','CHESTPLATE','models/armor/soul_steel_layer_1'),
 ('leggings','Leggings','LEGGINGS','models/armor/soul_steel_layer_2'),
 ('boots','Boots','BOOTS','models/armor/soul_steel_layer_1')],1):
    m=re.search(r'String remnant_'+part+r'\n.*?InvokeDynamic #(\d+):get',static,re.S)
    assert int(m[1])==12+i
    boot=re.search(r'\n  '+str(12+i)+r':.*?(?=\n  \d+:|\Z)',reg[reg.index('BootstrapMethods:'):],re.S).group(0)
    assert f'.lambda$static${i}:' in boot
    ctor=body(reg,f'lambda$static${i}')
    assert f'RemnantItem${cls}."<init>"' in ctor
    t=bc(f'item/RemnantItem${cls}.class.txt')
    # Only method instructions, not merely constant-pool strings.
    own=t[t.index('\n{'):]
    assert f'ArmorItem$Type.{slot}:' in own
    tex=body(t,'getArmorTexture')
    assert f'// String sons_of_sins:textures/{texture}.png' in tex and 'areturn' in tex
    model=json.loads((B/f'source/assets/sons_of_sins/models/item/remnant_{part}.json').read_text())
    assert model['textures']['layer0']==f'sons_of_sins:item/soul_steel_{part}'
    bindings.append({'id':f'sons_of_sins:remnant_{part}','bootstrap':12+i,'supplier':f'lambda$static${i}','class':f'RemnantItem${cls}','armor_type':slot,'icon':model['textures']['layer0'],'wear_texture':f'sons_of_sins:textures/{texture}.png'})
helmet=bc('item/RemnantItem$Helmet.class.txt');ext=bc('item/RemnantItem$Helmet$1.class.txt')
assert 'Consumer.accept:' in body(helmet,'initializeClient')
extbody=body(ext,'getHumanoidArmorModel')
assert 'Modelsoul_steel_helmet.LAYER_LOCATION:' in extbody and 'Modelsoul_steel_helmet.head:' in extbody
assert extbody.count('Collections.emptyList:')==7 # root plus 6 empty body/hat/limb placeholders
mod=bc('init/SonsOfSinsModModels.class.txt')
assert re.search(r'getstatic.*Modelsoul_steel_helmet.LAYER_LOCATION:.*?InvokeDynamic #5:get:.*?registerLayerDefinition:',body(mod,'registerLayerDefinitions'),re.S)
boot5=re.search(r'\n  5:.*?(?=\n  \d+:|\Z)',mod[mod.index('BootstrapMethods:'):],re.S).group(0)
assert 'Modelsoul_steel_helmet.createBodyLayer:' in boot5 and '.CLIENT' in mod and '.MOD' in mod
model=bc('client/model/Modelsoul_steel_helmet.class.txt');factory=body(model,'createBodyLayer')
assert re.search(r'bipush\s+64\n.*bipush\s+64\n.*LayerDefinition.m_171565_',factory)
lines=factory.splitlines();uv=[]
def intpush(s):
 m=re.search(r'iconst_(\d+)',s)
 if m:return int(m[1])
 return int(re.search(r'(?:bipush|sipush)\s+(-?\d+)',s)[1])
for i,l in enumerate(lines):
 if 'CubeListBuilder.m_171514_:(II)' in l: uv.append([intpush(lines[i-2]),intpush(lines[i-1])])
assert uv==[[0,48],[32,48],[32,32],[32,48],[32,32],[32,0],[32,16],[32,16],[32,0]]
images={}
for n in p['entries']:
 if n.endswith('.png'):
  im=Image.open(B/'source'/n).convert('RGBA');images[n]={'size':list(im.size),'alpha_bbox':im.getchannel('A').getbbox()}
assert len(images)==7
anim=json.loads((B/'source/assets/sons_of_sins/textures/item/soul_steel_chestplate.png.mcmeta').read_text())
assert anim['animation']=={'frametime':16,'interpolate':True,'frames':[0,1,2]}
base=json.loads((ROOT/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text())
changed=[n for n,h in base.items() if sha(ROOT/n)!=h]
assert not changed,changed
study={'scope':'D46 existing complete Remnant set, native whole-source view and bounded consumers',
'case':'sons_of_sins:remnant','semantic_group':'complete_soul_steel_wrap_visor_green_core','registered_bindings':bindings,
'images_actually_viewed':images,'view_page':'whole-native-source.png',
'helmet_contract':{'custom_atlas':[64,64],'model_layer':'sons_of_sins:modelsoul_steel_helmet#main','event_supplier_bootstrap':5,'custom_part':'head','empty_other_parts':['hat','body','right_arm','left_arm','right_leg','left_leg'],'declared_uv_starts_not_face_acceptance':uv},
'other_slots':'Chest/boots override L1, leggings override L2; selected classes/base declare no custom armor-model extension. Default Forge path context reused from D44; runtime untested.',
'animation':anim,'visual_observations':['面罩图标是低顶平横条、多层暗灰包裹，亮部横向成簇；保留暗红轮廓，与片甲的窄肩绑带不同。','胸短宽，绿芯集中，非满图发亮；长窄护胫与短腰裤分开。只借块面节奏，不复制原图。','原生64x64头盔图集是专用稀疏岛，不能以头盔图标/原版L1头部区当穿戴依据。','胸图标16x48三帧，只算一件；穿戴L1没有因库存动画存在而自动获得同样动画。'],
'applicability':'朴素袖口可借暗布/硬片的宽窄分区；强力鸿蒙等借集中识别点，保持原版短宽胸甲而非人台。实际修复仍受适用1000门槛。',
'limits':['No complete per-face UV/culling/pose/visual wearing acceptance. UV starts are not independent references.','Layer event source declaration, not actual registered runtime or hook acceptance.','No new semantic credit: soul_steel candidate resolves existing remnant case; same complete design.','No production texture edits/game/checklist deletion.'],
'counts':{'name_families':654,'armor_name_families':640,'conservative_groups':215,'new_design_credit':0,'validated_independent_design_total':None,'reference_gate_met':False}}
emit('whole-reference-study.json',study)
emit('verification.json',{'result':'PASS_BOUNDED_STATIC_WHOLE_REFERENCE','original_entries':len(p['entries']),'png_actually_viewed':7,'four_slot_bindings':len(bindings),'custom_helmet_uv_starts':len(uv),'protected_paths_unchanged':len(base),'new_design_credit':0,'reference_gate_met':False,'runtime_acceptance':False,'production_changes':0,'game_starts':0,'checklist_deletions':0})
print('PASS 22 native entries / 7 viewed PNG / 4 slots / custom helmet 9 UV starts / 289 protected')
