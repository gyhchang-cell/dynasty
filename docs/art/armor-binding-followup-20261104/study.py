"""Reconstruct only static registry/material/base-resource chains; no runtime or new design credit."""
from pathlib import Path
import json,re,hashlib
D=Path(__file__).resolve().parent; R=D.parents[2]; OLD=R/'docs/art/armor-binding-reference-20261103'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def text(p): return p.read_text()
def method(t,name):
 b=t[t.index('\n{\n')+3:];hs=list(re.finditer(r'^  [^ \n].*\n',b,re.M)); matches=[]
 for i,h in enumerate(hs):
  if (' '+name+'(' in h.group()) or name=='static {}' and h.group().startswith('  static {};'):
   matches.append(b[h.start():hs[i+1].start() if i+1<len(hs) else len(b)].split('      LineNumberTable:')[0].split('      StackMapTable:')[0])
 assert len(matches)==1,(name,len(matches));return matches[0]
def main():
 dis=D/'disassembly'; cp=read(D/'class-provenance.json'); np=read(D/'nested-class-provenance.json')
 reg=text(dis/'spellblademod/ModItems.txt');mat=text(dis/'spellblademod/ModArmorMaterials.txt');fs119=text(dis/'forge1192/HumanoidArmorLayer.txt'); fs120=text(D/'sources/forge1201/HumanoidArmorLayer.java')
 enum=method(mat,'static {}'); assert 'String diamond_warding' in enum and 'Field DIAMOND_WARDING:' in enum
 assert r'spellblademod:\u0001' in mat and 'Field name:Ljava/lang/String;' in method(mat,'m_6082_')
 renderer=method(fs119,'getArmorResource');assert '%s:textures/models/armor/%s_layer_%d%s.png' in renderer and 'ForgeHooksClient.getArmorTexture:' in renderer
 assert 'EquipmentSlot.LEGS:' in method(fs119,'m_117128_')
 assert 'usesInnerModel(slot) ? 2 : 1' in fs120 and 'ForgeHooksClient.getArmorTexture(entity, stack, s1, slot, type)' in fs120
 old_cp=read(OLD/'binding-class-provenance.json'); reuse={}
 for name in ['WardArmorItem','VirtualGoldArmorItem','VirtualGoldArmorItem$1','VGArmorModel']:
  a=next(a for a in old_cp['classes'] if Path(a['entry']).stem==name);reuse[name]={'path':str((OLD/a['disassembly']).relative_to(R)),'sha256':sha(OLD/a['disassembly'])}
 ward=text(R/reuse['WardArmorItem']['path']); assert 'extends net.minecraft.world.item.ArmorItem' in ward and 'getArmorTexture(' not in ward and 'initializeClient(' not in ward
 cc=text(dis/'celestial_core/CCMaterials.txt');ccitems=text(dis/'celestial_core/CCItems.txt');ccmain=text(dis/'celestial_core/CelestialCore.txt'); gen=text(dis/'l2damagetracker/GenItemVanillaType.txt'); am=text(dis/'l2damagetracker/ArmorMat.txt');generic=text(dis/'l2damagetracker/GenericArmorItem.txt')
 assert 'String celestial_core' in method(ccmain,'static {}') and 'GenItemVanillaType."<init>"' in method(ccmain,'static {}')
 assert 'CCMaterials.values:' in method(ccitems,'static {}') and 'GenItemVanillaType.genItem:' in method(ccitems,'static {}')
 assert r'celestial_core:\u0001' in cc and 'Field id:Ljava/lang/String;' in method(cc,'armorPrefix')
 constructor=method(cc,'com.xiaoyue.celestial_core.register.CCMaterials'); assert 'Method armorPrefix:' in constructor and 'class dev/xkmc/l2damagetracker/contents/materials/api/ArmorMat' in constructor
 assert 'Field name:Ljava/lang/String;' in method(am,'m_6082_')
 genreg=method(gen,'lambda$genItem$3');assert 'L2Registrate.item:' in genreg and r'\u0001_\u0001' in gen
 factory=method(gen,'lambda$genItem$1');assert 'getArmorConfig:' in factory and 'ArmorConfig.sup:' in factory and 'ArmorFactory.get:' in factory
 genericfactory=method(gen,'lambda$static$0');assert 'class dev/xkmc/l2damagetracker/contents/materials/generic/GenericArmorItem' in genericfactory and 'getArmorMaterial:' in genericfactory
 assert 'getArmorTexture(' not in generic
 # ExtraArmorConfig does not expose a texture override in the inspected declaration chain.
 assert 'getArmorTexture(' not in text(dis/'l2damagetracker/ExtraArmorConfig.txt')
 vg=text(R/reuse['VirtualGoldArmorItem']['path']); vgext=text(R/reuse['VirtualGoldArmorItem$1']['path']);vgmodel=text(R/reuse['VGArmorModel']['path'])
 assert 'initializeClient' in vg and 'VIRTUAL_GOLD_ARMOR_INNER_LAYER' in vgext and 'VIRTUAL_GOLD_ARMOR_OUTER_LAYER' in vgext
 assert 'VGArmorModel' in vgext and 'bipush        64' in vgmodel
 decls=read(OLD/'resource-declarations.json');prov=read(OLD/'provenance.json');chains=[];snippets={}
 for name,txt,names in [('ward_registry',reg,['static {}','lambda$static$12','lambda$static$13','lambda$static$14','lambda$static$15']),('ward_material',mat,['m_6082_','static {}']),('forge1192',fs119,['getArmorResource','m_117128_']),('celestial_material',cc,['armorPrefix','getArmorMaterial','getArmorConfig','static {}']),('generated_registry',gen,['genItem','lambda$genItem$3','lambda$genItem$1','lambda$static$0'])]:
  snippets[name]={n:method(txt,n) for n in names}
 for case in ['spellblademod:warding','celestial_core:guardian_ocean','celestial_core:sakura','celestial_core:virtual_gold']:
  ns,family=case.split(':'); rows=[a for a in decls if a['case_key']==case];assert len(rows)==4
  for a in rows:
   part=a['part'];slot={'helmet':'HEAD','chest':'CHEST','chestplate':'CHEST','leggings':'LEGS','boots':'FEET'}[part];layer=2 if slot=='LEGS' else 1
   itemid=Path(a['model']['entry']).stem
   if ns=='spellblademod':
    assert itemid=='warding_'+part
    index={'helmet':12,'chest':13,'leggings':14,'boots':15}[part];fbody=method(reg,f'lambda$static${index}')
    assert 'ModArmorMaterials.DIAMOND_WARDING:' in fbody and f'EquipmentSlot.{slot}:' in fbody and 'class com/cleannrooster/spellblademod/items/WardArmorItem' in fbody
    static=method(reg,'static {}');s=static.index('String '+itemid+'\n');block=static[s:s+700];assert f'InvokeDynamic #{index}:get:' in block and 'DeferredRegister.register:' in block
    assert re.search(rf'^  {index}:.*\n(?:.*\n){{0,5}}.*ModItems.lambda\$static\${index}:',reg,re.M)
    material='spellblademod:diamond_warding';path=f'spellblademod:textures/models/armor/diamond_warding_layer_{layer}.png';factoryname=f'ModItems.lambda$static${index}';itemclass='WardArmorItem';custom=False
   else:
    assert itemid==family+'_'+part and part in ['helmet','chestplate','leggings','boots']
    assert f'String {family}\n' in method(cc,'static {}') and f'Field {family.upper()}:' in method(cc,'static {}')
    assert f'String {part}\n' in method(gen,'genItem') and f'ArmorItem$Type.{part.upper()}:' in method(gen,'genItem')
    material='celestial_core:'+family;path=f'{material.split(":")[0]}:textures/models/armor/{family}_layer_{layer}.png';custom=family=='virtual_gold'
    itemclass='VirtualGoldArmorItem' if custom else 'GenericArmorItem';factoryname='VirtualGoldArmorItem.lambda$static$0' if custom else 'GenItemVanillaType.lambda$static$0'
    assert ('VirtualGoldArmorItem.ARMOR_GEN:' if custom else 'GenItemVanillaType.ARMOR_GEN:') in method(cc,'static {}')
   atlas=next((w for w in prov['worn_textures'] if w['entry']=='assets/'+path.replace(':','/',1)),None)
   if atlas is None: assert case=='celestial_core:guardian_ocean'

   chains.append({'case_key':case,'registered_item':ns+':'+itemid,'declared_slot':slot,'declared_material_name':material,'factory':factoryname,'item_class':itemclass,'item_model':a['model'],'inventory_texture':a['texture'],'base_worn_location_before_forge_hook':path,'native_atlas':atlas,'default_target_found_in_prior_atlases':atlas is not None,'custom_64x64_model':custom,'standard_dynasty_uv_assumed':False,'evidence_level':'STATIC_REGISTRY_MATERIAL_DEFAULT_RESOURCE_CHAIN_BEFORE_FORGE_HOOK','forge_version_evidence':'1.19.2-43.3.2 installed client bytecode' if ns=='spellblademod' else '1.20.1-47.4.10 mapped Forge sources','global_renderer_override_excluded':False,'game_acceptance':False})
 assert len(chains)==16
 save('method-excerpts.json',snippets)
 save('static-binding-study.json',{'chains':chains,'reused_prior_disassembly':reuse,'resolved_default_resource_name_families':4,'resolved_default_resource_item_chains':16,'default_target_entries_corresponding_to_prior_atlases':12,'default_paths_without_prior_candidate_match':['celestial_core:textures/models/armor/guardian_ocean_layer_1.png','celestial_core:textures/models/armor/guardian_ocean_layer_2.png'],'fresh_reference_design_credit':0,'final_hook_overrides_excluded':False,'native_or_game_acceptance':False,'scope':'仅关闭D12静态注册/材料/默认资源路径缺口。Forge hook全局覆盖未排除，虚金自定义64×64未证明适用Dynasty；不关闭实穿/目标UV验收。'})
 print('16 registry/material/default-resource chains / four prior name families / zero new design credit')
if __name__=='__main__':main()
