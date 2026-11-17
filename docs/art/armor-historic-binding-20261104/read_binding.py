"""Static declared chains only; never instantiate foreign game classes."""
from pathlib import Path
import json,re,hashlib
D=Path(__file__).resolve().parent; R=D.parents[2]
P=R/'docs/art/armor-historic-compact-reference-20261104'
def read(n):return (D/'disassembly'/f'{n}.class.txt').read_text()
def body(t):return t.split('\n{\n',1)[1].split('\n}\n',1)[0]
def boot(t):
    text=t.split('BootstrapMethods:',1)[1]
    return {int(k):v for k,v in re.findall(r'^  (\d+): (.*?)(?=^  \d+: |\Z)',text,re.M|re.S)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ctx=json.loads((D/'context.json').read_text());selected=set(ctx['selected_complete_families'])
    reg=read('ModelProviderRegistry');b=boot(reg)
    item=read('ItemRegistry');factory=read('ArmorOfTheAgesForge$ItemRegistryImpl')
    provider=read('ArmorModelProvider');mixed=read('ArmorModelProvider$MixedArmorModelProvider')
    humanoid=read('HumanoidArmorItem');forge=read('ForgeHumanoidArmorItem')
    client=read('ArmorOfTheAgesClientForge')
    # Read exact concat recipes, not a matching path elsewhere in the constant pool.
    for text,index,recipe in [(reg,0,r'\u0001_\u0001'),(humanoid,0,r'\u0001_\u0001'),(factory,1,r'\u0001_\u0001'),(provider,1,r'textures/models/armor/\u0001.png'),(mixed,1,r'textures/models/armor/\u0001_slim.png')]:
        assert recipe in boot(text)[index]
        assert re.search(r'// InvokeDynamic #'+str(index)+r':makeConcatWithConstants:',body(text))
    assert 'ForgeHumanoidArmorItem.lambda$register$1' not in boot(factory)[2]
    assert 'ItemRegistryImpl.lambda$register$1:' in boot(factory)[2]
    assert 'class org/dawnoftime/armoroftheages/item/ForgeHumanoidArmorItem' in body(factory)
    assert 'DeferredRegister.register:' in body(factory)
    assert 'Field armorPartName:' in body(humanoid) and 'HashMap.get:' in body(humanoid)
    assert 'ArmorModelProvider.getTexture:' in body(forge)
    assert 'Field slimResourceLocation:' in body(mixed) and 'Method isSlim:' in body(mixed)
    assert 'ArmorModelProvider.createLayer:' in boot(client)[1]
    assert 'MixedArmorModelProvider.createSlimLayer:' in boot(client)[2]
    assert 'RegisterLayerDefinitions.registerLayerDefinition:' in body(client)
    decls=json.loads((P/'resource-declarations.json').read_text())
    textures=json.loads((P/'provenance.json').read_text())['worn_textures']
    study=json.loads((D/'uv-call-study.json').read_text())
    # Actual constructor instructions carry material + Type, not a family-name guess.
    pat=r'// String (\w+_armor)\n[^\n]*// Field [^\n]*DoTArmorMaterial\.(\w+):[^\n]*\n[^\n]*// Field net/minecraft/world/item/ArmorItem\$Type\.(\w+):[^\n]*\n[^\n]*// Method register:'
    factory_calls=re.findall(pat,body(item));assert len(factory_calls)==40
    type_slot={'HELMET':'HEAD','CHESTPLATE':'CHEST','LEGGINGS':'LEGS','BOOTS':'FEET'}
    factory_map={(name,type_slot[typ]):mat for name,mat,typ in factory_calls}
    code=body(reg).split('  static {};',1)[1]
    blocks=re.findall(r'(?P<block>[^\n]*// String (?P<name>\w+_armor)\n[^\n]*// Field net/minecraft/world/entity/EquipmentSlot\.(?P<slot>HEAD|CHEST|LEGS|FEET):.*?// Method register:[^\n]*)',code,re.S)
    rows=[]
    for block,name,slot in blocks:
        ids=[int(n) for n in re.findall(r'// InvokeDynamic #(\d+):',block)]
        assert len(ids) in [2,3]
        targets=[]
        for i in ids:
            targets.append(re.search(r'REF_(?:newInvokeSpecial|invokeStatic) (org/dawnoftime/armoroftheages/client/models/[^\s]+)',b[i]).group(1))
        cls=targets[0].split('."<init>"')[0]
        assert targets[1].startswith(cls+'.createLayerDefinition:')
        if name in selected:assert f'/models/{name}/' in cls
        if len(ids)==3:assert targets[2].startswith(cls+'.createSlimLayerDefinition:')
        assert (name,slot) in factory_map
        declaration=next(x for x in decls if x['case_key']=='armoroftheages:'+name and x['source_slot']==slot.lower())
        normal=next(x for x in textures if x['case_key']==declaration['case_key'] and x['variant']=='normal')
        slim=next(x for x in textures if x['case_key']==declaration['case_key'] and x['variant']=='slim') if len(ids)==3 else None
        assert normal['entry']==f'assets/armoroftheages/textures/models/armor/{name}.png'
        if slim:assert slim['entry']==f'assets/armoroftheages/textures/models/armor/{name}_slim.png'
        row={'family':name,'slot':slot,'item_type':next(t for t,s in type_slot.items() if s==slot),'material_enum':factory_map[name,slot],
             'item_id':'armoroftheages:'+name+'_'+slot.lower(),'provider_key':name+'_'+slot.lower(),
             'localized_label':declaration['label'],'item_model':declaration['model'],'item_icon':declaration['texture'],
             'provider_kind':'MixedArmorModelProvider' if slim else 'ArmorModelProvider','supplier_bootstrap_indices':ids,
             'supplier_targets':targets,'registry_instructions':block.splitlines(),
             'normal_texture':normal,'slim_texture_if_selected':slim,'geometry_source_read':name in selected,
             'current_runtime_registry_or_visual_acceptance':False}
        if name in selected:
            ms=[m for m in study['models'] if m['family']==name and m['slot'].upper()==slot]
            assert len(ms)==(2 if slim else 1)
            for m in ms:
                assert m['source_class']['entry']==cls+'.class'
                assert m['texture_source']==(slim if 'Slim' in m['method'] else normal)
            row['geometry_methods']=[{'method':m['method'],'grid':m['declared_grid'],'raw_source_calls':m['source_addbox_call_count']} for m in ms]
        rows.append(row)
    assert len(rows)==40 and len({r['provider_key'] for r in rows})==40
    selected_rows=[r for r in rows if r['family'] in selected]
    assert len(selected_rows)==12
    assert all((r['slim_texture_if_selected'] is not None)==(r['slot']=='CHEST') for r in selected_rows)
    output={'scope':'STATIC_DECLARED_BINDING_NOT_LIVE_RENDER','slot_chains':rows,'selected_geometry_family_names':sorted(selected),
        'selected_complete_slot_chains':12,'all_family_slot_chains':40,'new_names':0,'new_design_credit':0,
        'slim_selection':'Mixed provider only: local configured preference, synced preference, then player skin model according to isSlim; not a global texture switch.',
        'limits':['40条为静态注册/路径/supplier对应；仅选定3套12类15方法读过几何UV','未执行模组、未验证当前运行覆盖/可见性/动画/接缝','材料数值取配置，不从外观或中文翻译推断获取阶段与强度','常规/细臂和4槽仍是同一套，不新增独立设计信用'],
        'source_sha256':{n:sha(D/'disassembly'/f'{n}.class.txt') for n in ['ModelProviderRegistry','ItemRegistry','ArmorOfTheAgesForge$ItemRegistryImpl','ArmorModelProvider','ArmorModelProvider$MixedArmorModelProvider','HumanoidArmorItem','ForgeHumanoidArmorItem','ArmorOfTheAgesClientForge']}}
    (D/'binding-study.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in output.items() if k not in ['slot_chains','source_sha256']},ensure_ascii=False))
if __name__=='__main__':main()
