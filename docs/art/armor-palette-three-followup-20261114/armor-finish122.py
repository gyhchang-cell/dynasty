from pathlib import Path
import json,hashlib,runpy,ast
from PIL import Image
r=Path.cwd();H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();finish=runpy.run_path('/tmp/armor-finish-common-v3.py')['finish'];prior='armor-aquamirae-three-bolt-whole-20261114';state='D121_AQUAMIRAE_THREE_BOLT_NATIVE_WHOLE_REFERENCE_SAVED'
dimensions={}
for key,color,source in [('gravitite','明亮洋红、深紫边与近白高光','原生四件配方使用aether:processed/gravitite，祭坛修复时间1500；另查到黄金/白银地牢奖励表'),('obsidian','近黑主体、低亮紫边和克制紫色亮簇','本批原生JSON未查到直接配方/掉落，不据稀有度字段猜测获取难度或阶段'),('zanite','紫罗兰主体、暗紫轮廓与浅紫亮簇','原生四件配方使用aether:gems/zanite，祭坛修复时间750；另查到青铜地牢奖励表')]:
 dimensions[key]={
 'silhouette':'四个16×16原生图标是紧凑倒U头盔、短宽胸、腰连直腿与分开双靴，不是人物人台。与本批另外两套全部六PNG的透明掩码相同，不能把名称当独立设计。',
 'proportion':'盔顶一格阶梯，胸肩止于短方肩，双靴筒直且鞋尖短；穿戴用默认方块人体积，没有从图标虚构冠饰或侧翼。四槽体块比例稳定。',
 'material_identity':color+'，大块离散明暗而非渐变。'+source+'；JSON声明不是实际获取验收。',
 'pixel_clusters':'胸中央留大色块，肩端/头前左上局部高光，背部横向明暗带与胸前不相同。重力晶与紫晶六张图均可逐色替换对应，黑曜石裤图和穿戴局部不是严格单色映射，但不因此另算独立整套。',
 'negative_space':'原图透明底保留倒U面孔、双腿与双靴间隙；64×32外层hat六来源区域全透明。头前30/64、背52/64，胸前76/96、背74/96；腰层前后40/96，不当成缺图补满。',
 'slot_uv_consumers':'AetherItems四工厂实际AetherArmorItem(对应材料,HELMET/CHESTPLATE/LEGGINGS/BOOTS)；普通ArmorItem只声明构造和getArmorTexture，LEGS选layer2、其余layer1，显式aether域，材质getName返回name。复用固定Forge默认64×32消费者上下文；本批图标4基础+40trim JSON，trim外部原版图层仍HOLD0。',
 'applicability_dedup':'可学原版甲基本比例与大色簇；三套仍归既有vanilla_outline_elemental_palette组，与既有海神文字/UV统计作具体对照，不重新打开已通过原图。局部变化、四槽与trim不计新设计，保留既有认可，新增独立信用0。'}
for key,num in [('gravitite',122),('obsidian',123),('zanite',124)]:
 b=r/'docs/art'/('armor-'+key+'-whole-20261114');assert not list(b.glob('bounded-receipt*'));put=lambda n,x:(b/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');p=json.loads((b/'provenance.json').read_text());d=json.loads(next((b/'decode').glob('*__AetherItems.class.json')).read_text());inst=next(m['instructions'] for m in d['methods'] if m['name']=='<clinit>');chains=[]
 for slot in ['helmet','chestplate','leggings','boots']:
  i=next(i for i,x in enumerate(inst) if x.get('constant')==key+'_'+slot);bid=ast.literal_eval(inst[i+1]['constant'])[1];boot=d['bootstrap_methods'][bid];name=next(x for x in boot['arguments'] if 'lambda$static$' in x).split(' / ')[1];method=next(m for m in d['methods'] if m['name']==name);assert any('AetherArmorItem / <init>' in x.get('constant','') for x in method['instructions']);assert any('/ '+key.upper()+' /' in x.get('constant','') for x in method['instructions']);assert any('/ '+{'helmet':'HELMET','chestplate':'CHESTPLATE','leggings':'LEGGINGS','boots':'BOOTS'}[slot]+' /' in x.get('constant','') for x in method['instructions']);chains.append({'item':'aether:'+key+'_'+slot,'declaration':inst[i:i+4],'bootstrap':boot,'factory':method,'wear_texture':'aether:textures/models/armor/'+key+'_layer_'+('2' if slot=='leggings' else '1')+'.png'})
 put('native-four-slot-factory-chains.json',chains)
 item=json.loads(next((b/'decode').glob('*AetherArmorItem.class.json')).read_text());mat=json.loads(next((b/'decode').glob('*AetherArmorMaterials.class.json')).read_text());put('native-wear-consumer-methods.json',{'item_class':item['class'],'super':item['super'],'interfaces':item['interfaces'],'all_item_methods':item['methods'],'material_get_name':[m for m in mat['methods'] if m['name']=='m_6082_'],'scope':'all direct armor item methods read; unrelated effect abilities not claimed as renderer'})
 refs=[];external=[]
 for e in p['entries']:
  if '/models/item/' not in e['entry']:continue
  q=json.loads((b/e['local']).read_text())
  for layer,value in q.get('textures',{}).items():
   ns,path=value.split(':');f=b/'source/assets'/ns/'textures'/(path+'.png')
   if ns=='aether':assert f.exists(),value
   else:external.append({'model':e['entry'],'layer':layer,'texture':value,'status':'external minecraft trim atlas dependency, not extracted image or added design'})
  for override in q.get('overrides',[]):
   ns,path=override['model'].split(':');assert (b/'source/assets'/ns/'models'/(path+'.json')).exists()
  refs.append({'source':e['local'],'sha256':e['sha256'],'data':q})
 put('native-icon-model-binding.json',{'models':refs,'external_trim_layers':external,'new_design_credit':0,'external_trim_visual_acceptance':'HOLD0 outside base untrimmed design scope' if external else 'no base trim overrides'})
 alpha=[]
 for e in p['entries']:
  if e['entry'].endswith('.png'):
   im=Image.open(b/e['local']).convert('RGBA');hist=im.getchannel('A').histogram();alpha.append({'source':e['local'],'sha256':e['sha256'],'size':im.size,'alpha_histogram':{str(i):n for i,n in enumerate(hist) if n}})
 put('alpha-inventory.json',alpha)
 loot=[]
 for e in p['entries']:
  if '/loot_tables/' in e['entry'] or e['entry'].startswith('data/aether/recipes/'):loot.append({'source':e['local'],'sha256':e['sha256'],'data':json.loads((b/e['local']).read_text()),'scope':'native recipe/loot declaration; actual obtaining not executed; no guessed obsidian route'})
 put('native-acquisition-data.json',loot)
 put('seven-dimension-mc-review.json',{'dimensions':dimensions[key],'dimension_count':7,'case':'aether:'+key,'new_validated_credit':0,'scope':'base untrimmed native original and default consumer context, not game or final all-pack visual'})
 target=r/'docs/art/armor-current-bindings-20261113/unclosed-targets.json';t=json.loads(target.read_text());assert len(t)==28 and not any(x['redraw_authorized_by_audit'] for x in t);put('current-target-check.json',{'path':str(target),'sha256':H(target),'items':28,'redraw_authorized':0,'new_never_redrawn_and_crude_evidence':False})
 pending=['Main整套语义去重与适用性独立验收','精确激活的模型扩展/全局mod与用户资源包覆盖','完整五视图、原版模型面向和接缝未实机验收','原版trim纹理及动态穿戴/glint等不在基础原图验收内','1000独立设计总数及准确缺口未核定']
 bindings={'factory_chains':'native-four-slot-factory-chains.json','texture':'AetherArmorItem.getArmorTexture chooses LEGS=2 else1, explicit aether domain; type argument not used','item':'AetherArmorItem extends ordinary ArmorItem; only ctor and getArmorTexture declared, no DyeableLeatherItem or custom-model method','consumer':'consumer-provenance.json fixed Forge1.20.1-47.4.10 source context; actual runtime not asserted','default_model':'64×32 HumanoidArmorModel, base inner0.5/outer1.0 context; legs extend -0.1, head hat extra0.5; default IClientItemExtensions returns original','tint_overlay':'ordinary ArmorItem default branch renders white RGB once; no dyeable overlay branch. Trim and glint separate','hat':'native-hat-source-rectangles.json six base default hat UV rectangles alpha0','raw_uv':'raw-uv-study.png viewed; source rectangles not signed-face seam proof','source_metadata':'Jar filename says neoforge; actual mods.toml declares javafml, Forge[47.1.0,), MC1.20.1, assets all rights reserved. Research only, no copying','dedup':'within-batch-concrete-dedup.json and prior-family-comparison.json; all six masks identical, gravitite-zanite exact palette substitution; zero new credit','seven_dimensions':'seven-dimension-mc-review.json','base_design_scope_complete':'Four native icons/two wearable atlases and direct item factory/texture contracts read; runtime and external trimming not complete'}
 status='D'+str(num)+'_'+key.upper()+'_NATIVE_WHOLE_REFERENCE_SAVED';finish(b.name,prior,'D'+str(num),state,status,'latest_'+key+'_whole',list(dimensions[key].values()),bindings,pending);prior=b.name;state=status
