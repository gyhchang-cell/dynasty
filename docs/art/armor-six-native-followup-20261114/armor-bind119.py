from pathlib import Path
import json,ast,hashlib
r=Path.cwd();H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for key,base,slots,layer,bi in [('abyssal','AbyssalArmorItem',['Heaume','Brigantine','Leggings','Boots'],'ABYSSAL_ARMOR',8),('terrible','TerribleArmorItem',['Helmet','Chestplate','Leggings','Boots'],'TERRIBLE_ARMOR',3),('three-bolt','ThreeBoltArmorItem',['Helmet','Chestplate','Leggings','Boots'],'THREE_BOLT_ARMOR',11)]:
 b=r/'docs/art'/f'armor-aquamirae-{key}-whole-20261114'; put=lambda n,x:(b/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');ds={json.load(open(f))['class'].split('/')[-1]:(f,json.load(open(f))) for f in (b/'decode').glob('*.json')}
 def method(cl,name):return next(x for x in ds[cl][1]['methods'] if x['name']==name)
 reg=ds['AquamiraeItems'][1];ri=method('AquamiraeItems','<clinit>')['instructions'];chains=[]
 names=[key.replace('-','_')+'_'+s.lower() for s in slots]
 if key=='three-bolt':names[1]='three_bolt_suit'
 pairs=list(zip(names,[base+'$'+s for s in slots],['HEAD','CHEST','LEGS','FEET']))
 if key=='abyssal':pairs.append(('abyssal_tiara','AbyssalArmorExtraItem$Tiara','HEAD'))
 for item,cl,slot in pairs:
  i=next(i for i,x in enumerate(ri) if x.get('constant')==item);bootstrap=reg['bootstrap_methods'][ast.literal_eval(ri[i+1]['constant'])[1]]
  ctor=method(cl,'<init>');assert any('/ '+slot+' /' in x.get('constant','') for x in ctor['instructions'])
  init=method(cl,'initializeClient');wrap=method(cl+'$1','getHumanoidArmorModel');tex=method(cl,'getArmorTexture');texture=next(x['constant'] for x in tex['instructions'] if x['op']=='ldc');ns,path=texture.split(':');assert (b/'source/assets'/ns/path).exists()
  selected=[x['constant'].split(' / ')[1] for x in wrap['instructions'] if x['op']=='getfield' and 'Model'+('ThreeBolt' if key=='three-bolt' else key.title())+'Armor / ' in x.get('constant','')]
  chains.append({'id':'aquamirae:'+item,'slot':slot,'registry_declaration':ri[i:i+4],'registry_bootstrap':bootstrap,'ctor':ctor,'initialize_client':init,'wrapper':wrap,'selected_native_parts':selected,'texture_method':tex,'texture':texture})
 put('native-slot-texture-model-chains.json',{'chains':chains,'scope':'direct native declarations and client extension methods; no global event activation/runtime validation','source_decode_sha256':{k:H(v[0]) for k,v in ds.items() if k!='AquamiraeItems'}})
 lay=ds['AquamiraeLayers'][1];mi=method('AquamiraeLayers','registerLayerDefinitions')['instructions'];i=next(i for i,x in enumerate(mi) if '/ '+layer+' /' in x.get('constant',''));boot=lay['bootstrap_methods'][bi];assert 'createBodyLayer' in str(boot);ci=method('AquamiraeLayers','<clinit>')['instructions'];j=next(i for i,x in enumerate(ci) if x['op']=='putstatic' and '/ '+layer+' /' in x.get('constant',''))
 put('native-layer-definition-chain.json',{'field':layer,'register_layer_method_slice':mi[i:i+3],'bootstrap':boot,'static_field_initializer':ci[max(0,j-2):j+1],'register_location_method':method('AquamiraeLayers','register'),'scope':'direct registration method body, annotation subscriber activation and exact runtime not validated'})
 put('raw-uv-scope-correction.json',{'generic_crop_page_actually_viewed':True,'warning':'raw-uv-study labels are generic base-layout context only; these custom models are64x64 and those labels do not identify actual anatomical faces. Do not use page as custom model UV proof.','custom_model_evidence':'native-geometry-literal-study.json','complete_original_atlases':'source-study.png','actual_signed_faces_and_poses_validated':False})
 print(key,'slots',[(c['id'],c['slot'],c['selected_native_parts'],c['texture']) for c in chains]);print('LAYER',boot)
