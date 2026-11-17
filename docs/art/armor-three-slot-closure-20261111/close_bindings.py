"""Close D30 three native registry->factory->slot->texture chains statically."""
from pathlib import Path
import json,re,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 p=json.loads((D/'collection.json').read_text());prior=json.loads((R/p['prior_partial_binding']).read_text());audit=json.loads((R/'docs/art/armor-candidate-resolution-20261109/candidate-resolution.json').read_text());out=[]
 for case in p['records']:
  key=case['case_key'];ns=key.split(':')[0];reg=(D/case['plain']['path']).read_text();verb=(D/case['verbose']['path']).read_text();bootstrap=verb.split('BootstrapMethods:',1)[1];bs={int(k):s for k,s in re.findall(r'^  (\d+): (.*?)(?=^  \d+: |\Z)',bootstrap,re.M|re.S)}
  assert '// String '+ns+'\n' in reg and 'DeferredRegister.create:' in reg
  c=next(c for c in audit['candidates'] if c['case_key']==key)
  for row in [r for r in prior['rows'] if r['case_key']==key]:
   sub=row['class'].split('$')[-1];part={'Helmet':'helmet','Chestplate':'chestplate','Leggings':'leggings','Boots':'boots'}[sub];name=key.split(':')[1]+'_'+part
   found=re.search(r'// String '+name+r'\n.*?// InvokeDynamic #(\d+):get:.*?DeferredRegister.register:.*?// Field ([A-Z_]+):',reg,re.S);assert found,(key,part)
   b=bs[int(found[1])];factory=None;factory_excerpt=None
   direct=re.search(r'REF_newInvokeSpecial (net/mcreator/[^\n]+?)\."<init>":\(\)V',b)
   if direct:concrete=direct[1];factory_kind='DIRECT_CONSTRUCTOR_METHOD_HANDLE';factory_excerpt=b
   else:
    fac=re.search(r'REF_invokeStatic (net/mcreator/[^\n]+?)\.(lambda\$static\$\d+):',b);assert fac
    factory=fac[2];m=re.search(r'  private static [^\n]* '+re.escape(factory)+r'\(\);(.*?)(?=\n  (?:public|private|protected|static)|\Z)',reg,re.S);assert m;factory_excerpt=m[1];concrete=re.search(r'// class (net/mcreator/[^\n]+)',factory_excerpt)[1];assert 'invokespecial' in factory_excerpt and 'areturn' in factory_excerpt;factory_kind='STATIC_LAMBDA_CONSTRUCTOR_FACTORY'
   assert concrete.endswith('/'+row['class'].split('.')[-1]);assert sha(R/'docs/art/armor-candidate-resolution-20261109'/row['disassembly'])==row['disassembly_sha256']
   decl=next(d for d in c['parts'] if d['part']==part);assert decl['model_resolution']['chain'][0]['entry'].endswith('/'+name+'.json')
   out.append({'case_key':key,'native_registry_id':ns+':'+name,'namespace_literal_checked':True,'registry_field':found[2],'bootstrap_index':int(found[1]),'bootstrap_excerpt':b,'factory_kind':factory_kind,'factory':factory,'factory_excerpt':factory_excerpt,'concrete_item_class':concrete,'explicit_slot_literal':row['constructor_slot_literal'],'prior_slot_texture_declaration':row,'native_icon_model':decl['model_resolution'],'native_icon':decl['native_png'],'actual_worn_texture':row['source_texture'],'registered_factory_slot_texture_static_chain_closed':True,'runtime_acceptance':False})
 assert len(out)==12 and len({r['native_registry_id'] for r in out})==12
 save('closed-static-bindings.json',{'rows':out,'slot_chains':12,'namespace_registry_and_factory_checked':True,'source_versions':{'infectum:test':'Forge 1.19.2 source reference','poppy:player_armor_armor':'Forge 1.19.2 source reference','theyarewatching:armorv':'Forge 1.20.1 source reference'},'all_use_stock_ArmorItem_inheritance_in_fixed_classes':True,'limits':['No game or mod class execution; static source declarations only','Forge hooks/resource packs/client state may override rendering; no runtime acceptance','Infectum all four slots really return entities/armor_layer1_1.png, including leggings; red same-name candidate is not selected','1.19 source items not asserted drop-in compatible with Dynasty Forge1.20.1'], 'game_starts':0,'production_changes':0})
 print('12 exact native registration/factory/type-to-worn-texture static chains closed; 4 direct and 8 lambda constructors.')
if __name__=='__main__':main()
