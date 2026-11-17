"""D29 exact registration/factory/client/model declarations; no class execution."""
from pathlib import Path
import json,re
D=Path(__file__).resolve().parent
def read(n):return (D/'disassembly'/n).read_text()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 reg=read('MokelsRpgTwoModItems.class.txt');v=read('MokelsRpgTwoModItems.verbose.txt');boot=v.split('BootstrapMethods:',1)[1];bs={int(k):s for k,s in re.findall(r'^  (\d+): (.*?)(?=^  \d+: |\Z)',boot,re.M|re.S)};rows=[];families=[]
 geo=json.loads((D/'geometry-study.json').read_text())['cases'];decl=json.loads((D/'declarations.json').read_text())
 for family,cls,renderer,model in [('crabarmor','CrabarmorItem','CrabarmorArmorRenderer','CrabarmorModel'),('sunrise_armor','SunriseArmorItem','SunriseArmorArmorRenderer','SunriseArmorModel')]:
  it=read(cls+'.class.txt');ext=read(cls+'$2.class.txt');ren=read(renderer+'.class.txt');mod=read(model+'.class.txt');g=next(c for c in geo if c['case_key'].endswith(':'+family))
  init=re.search(r'  public void initializeClient\(.*?(?=\n  (?:public|private|protected)|\Z)',it,re.S).group(0);assert cls+'$2' in init and 'Consumer.accept:' in init
  assert renderer in ext and 'GeoArmorRenderer.prepForRender:' in ext and model in ren
  assert all('// String '+b in ren for b in g['canonical_roots'])
  for a in [g['geometry'],g['texture'],g['source_animation']]:assert '// String '+a['entry'].split('assets/mokels_rpg_two/')[1] in mod
  assert '// String idle' in it and 'RawAnimation.thenLoop:' in it and 'ControllerRegistrar.add:' in it
  # retain entire predicate because it checks equipment before continuing; not universal playback.
  pred=re.search(r'  private [^\n]* predicate\(.*?(?=\n  (?:public|private|protected)|\Z)',it,re.S).group(0)
  families.append({'case_key':'mokels_rpg_two:'+family,'item_class':cls,'client_extension':cls+'$2','renderer':renderer,'model':model,'canonical_roots_declared':list(g['canonical_roots']),'source_geometry':g['geometry'],'source_texture':g['texture'],'source_animation':g['source_animation'],'idle_predicate_excerpt':pred,'runtime_playback_proven':False})
  for part in ['helmet','chestplate','leggings','boots']:
   name=family+'_'+part;m=re.search(r'// String '+name+r'\n.*?// InvokeDynamic #(\d+):get:.*?DeferredRegister.register:.*?// Field ([A-Z_]+):',reg,re.S);assert m
   fac=re.search(r'REF_invokeStatic net/mcreator/mokelsrpgtwo/init/MokelsRpgTwoModItems\.(lambda\$static\$\d+):',bs[int(m[1])]).group(1)
   method=re.search(r'  private static [^\n]* '+re.escape(fac)+r'\(\);(.*?)(?=\n  (?:public|private|protected|static)|\Z)',reg,re.S).group(1)
   assert '// class net/mcreator/mokelsrpgtwo/item/'+cls in method and 'ArmorItem$Type.'+part.upper()+':' in method
   source=next(x for x in decl if x['case_key'].endswith(':'+family) and x['part']==part)
   roots={'helmet':['armorHead'],'chestplate':['armorBody','armorRightArm','armorLeftArm'],'leggings':['armorRightLeg','armorLeftLeg'],'boots':['armorRightBoot','armorLeftBoot']}[part];assert all(g['canonical_roots'][r]>0 for r in roots)
   rows.append({'case_key':'mokels_rpg_two:'+family,'registry_name':'mokels_rpg_two:'+name,'registry_field':m[2],'bootstrap_index':int(m[1]),'factory':fac,'factory_excerpt':method,'explicit_type':part.upper(),'source_icon_declaration':source,'root_descendant_cubes':{r:g['canonical_roots'][r] for r in roots},'static_chain_checked':True,'live_slot_visibility_proven':False})
 assert len(rows)==8
 save('static-binding-study.json',{'families':families,'slot_chains':rows,'method':'javap static bytecode, bootstrap implementation and literal resources only','limits':['Eight static registration-to-type-to-class/client/model/texture declarations checked, NOT actual equipped-slot QA','Source predicate has equipment/armor-stand conditions; idle declaration not claimed universally running','Body child cubes and cape/horns in software full assembly do not prove live slot filtering'], 'game_starts':0})
 print('Eight explicit static slot chains; original source animation/controller declarations only.')
if __name__=='__main__':main()
