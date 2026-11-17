"""Bounded static read of existing robe reference; no mod execution."""
from pathlib import Path
import json,re,hashlib
from PIL import Image
D=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def text(n):return (D/'bytecode'/(n+'.txt')).read_text()
def meth(n,s):
 ls=text(n).splitlines();a=next(i for i,l in enumerate(ls) if re.match(r'^  (public|private|protected|static)',l) and s in l);b=next((i for i in range(a+1,len(ls)) if re.match(r'^  (public|private|protected|static)',ls[i])),len(ls));t='\n'.join(ls[a:b]);return t.split('    Code:\n',1)[1].split('      LineNumberTable:',1)[0]
def bs(n,i):return ('\n'+text(n).split('BootstrapMethods:\n',1)[1]).split('\n  '+str(i)+': ',1)[1].split('\n  '+str(i+1)+': ',1)[0]
items=meth('Items','static {};');a=items.index('// String robe');b=items.index('Field ROBE_ARMOR:',a);robe=items[a:b];assert 'registerDyeableSet:' in robe and 'int 11546150' in robe
reg=meth('Items',' registerDyeableSet(');register=meth('Items',' register(java');assert '// String immersive_armors' in register and 'Registration.register:' in register
slots=[]
for i,part in enumerate(['helmet','chestplate','leggings','boots']):
 assert '\\u0001_'+part in bs('Items',i*2)
 assert 'InvokeDynamic #'+str(i*2)+':makeConcatWithConstants:' in reg and 'InvokeDynamic #'+str(i+8)+':get:' in reg
 assert 'REF_invokeStatic immersive_armors/Items.lambda$registerDyeableSet$'+str(i+14)+':' in bs('Items',i+8)
 sup=meth('Items','lambda$registerDyeableSet$'+str(i+14)+'(');assert 'ArmorItem$Type.'+part.upper()+':' in sup and 'DyeableExtendedArmorItem."<init>":' in sup
 p='assets/immersive_armors/models/item/robe_'+part+'.json';j=json.loads((D/'source'/p).read_text());pngs=[]
 for key,ref in j['textures'].items():
  ns,path=ref.split(':');png='assets/'+ns+'/textures/'+path+'.png';assert Image.open(D/'source'/png).size==(16,16);pngs.append({'layer':key,'path':png})
 slots.append({'requested_registered_id':'immersive_armors:robe_'+part,'registration_boundary':'Registration.register request; platform implementation not executed','armor_type':part.upper(),'supplier':'lambda$registerDyeableSet$'+str(i+14),'icon_layers':pngs})
client=text('ItemsClient');block=client[client.index('// Field immersive_armors/Items.ROBE_ARMOR:'):];block=block[:block.index('// Field immersive_armors/Items.SLIME_ARMOR:')]
assert block.count('.colored:()')==4
pieces=[]
for cls,stem,factory,params in [('LowerLeggingsLayerPiece','leggings_lower','lower',[.125,.125]),('LowerBodyLayerPiece','body_lower','upper',[.25,.55]),('MiddleLeggingsLayerPiece','leggings_middle','lower',[.5,.5]),('MiddleBodyLayerPiece','body_middle','upper',[.75,.9])]:
 assert cls in block and 'ExtendedArmorMaterial.'+factory+':' in block
 assert '// String '+stem in meth(cls,cls+'();')
 static=meth(cls,'static {};');assert 'buildDilatedModel:' in static
 for f in set(params):assert '// float '+str(f)+'f' in static
 paths=['assets/immersive_armors/textures/models/armor/robe/'+stem+s+'.png' for s in ['', '_overlay']]
 assert all(Image.open(D/'source'/p).size==(64,32) for p in paths)
 pieces.append({'class':cls,'texture_pair':paths,'material_slot_method':factory,'slots':['LEGS'] if factory=='lower' else ['HEAD','CHEST','FEET'],'dilation_parameters_body_head':params})
upper=meth('ExtendedArmorMaterial',' upper(');lower=meth('ExtendedArmorMaterial',' lower(')
for s in ['head','chest','feet']:assert 'Method '+s+':' in upper
assert 'Method legs:' in lower
for s,slot in [('head','HEAD'),('chest','CHEST'),('legs','LEGS'),('feet','FEET')]:assert 'EquipmentSlot.'+slot+':' in meth('ExtendedArmorMaterial',' '+s+'(')
texture=meth('Piece',' getTexture(immersive');assert 'getMaterial:' in texture and 'getTexture:' in texture and '// String _overlay' in texture
assert 'immersive_armors:textures/models/armor/\\u0001/\\u0001\\u0001.png' in bs('Piece',0)
r=meth('LayerPiece',' void render(');assert 'DyeableLeatherItem.m_41121_:' in r and r.count('Method renderParts:')==3
assert re.search(r'fconst_1\n[^\n]+fconst_1\n[^\n]+fconst_1\n[^\n]+iconst_1\n[^\n]+invokevirtual[^\n]+renderParts:',r)
mix=meth('MixinArmorFeatureRenderer',' renderPieces(');assert 'ExtendedArmorMaterial.getPieces:' in mix and 'List.forEach:' in mix
assert 'Piece.render:' in meth('MixinArmorFeatureRenderer','lambda$renderPieces$0(')
assert 'MixinArmorFeatureRenderer' in json.loads((D/'source/immersive_armors.mixins.json').read_text())['client']
bake=meth('LayerPiece','buildDilatedModel(float, float)');assert re.search(r'bipush\s+64\n[^\n]+bipush\s+32\n[^\n]+invokestatic[^\n]+LayerDefinition',bake)
color=meth('DyeableExtendedArmorItem',' m_41121_(');assert '// String display' in color and '// String color' in color and 'getColor:' in color
ic=meth('ClientMain','lambda$postLoad$0(');assert 'ifle' in ic and 'iconst_m1' in ic and 'm_41121_:' in ic
out={'case':'immersive_armors:robe','scope':'既有完整长袍原图重读及四附加贴图片消费者静态补齐，不计新设计','prior_semantic_group':'immersive_robe_open_front','icon_registration_requests':slots,'extra_wear_pieces':pieces,'extra_wear_texture_pattern':'immersive_armors:textures/models/armor/{material}/{piece}{_overlay_if_true}.png','dimensions':[64,32],'color':{'default_material_color_decimal':11546150,'display_color_overrides':True,'extra_wear_base':'DyeableLeatherItem RGB channels /255','extra_wear_overlay':'white RGB, overlay=true','icon':'tintIndex>0 returns -1, otherwise item color','not_game_capture':True},'actually_viewed_pages':['native-source-01.png','native-source-02.png','native-source-03.png'],'actually_viewed_png':19,'visual_observations':['头图是短而圆角阶梯罩帽，灰白底与金色短拱覆盖分开；只学开口和领边分层，不仿制图形。','胸图是敞开的两侧衣襟，两条细长金边在overlay；裤图仍两条直腿，双靴为窄筒黑边。','body_lower有完整上身灰阶布面与下缘区域；body_middle只留一条灰白下摆。对应overlay主要金色领边、竖襟、横腰带。','leggings_lower保留腰腿灰白布面；leggings_middle原生底图全透明，overlay仍有金色边段。空底不等于整个附加层无用。','多数灰度区域使用细碎布纹，作为后续不照搬之处；Dynasty应保留更大的像素簇和少量离散折面。'],'applicable_principles':['布料染色与固定金属/边饰分层；不能烘焙后再全图染色。','独立下摆的UV和扩张参数应跟实际消费者匹配；仅两张常规甲图不代表全部穿戴表面。','清楚敞襟身份通过少量竖边表达，不靠密纹和大肩饰。'],'limits':['只读反汇编和原图，不执行模组/游戏','四件注册闭至跨平台Registration.register请求；Forge实现/加载生命周期未独立闭合','minecraft命名空间robe_layer_1/2四图已查看，普通原版主层consumer未在本轮独立读完','混入注解含原开发映射签名，refmap与目标实际匹配未验证，不推断失效','未逐面UV或五视角/真人穿戴；中层透明底保留原像素，不删除','未做默认染色合成或软件图冒充游戏'],'new_name_families':0,'new_design_credit':0,'reference_gate_met':False,'production_changes':0}
(D/'static-piece-consumers.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('PASS bounded 4 registration requests / 4 extra pieces / 8 wear PNG consumers; native main layer remains pending')
