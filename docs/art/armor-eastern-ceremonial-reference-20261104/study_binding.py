"""Resolve actual four-slot factories and client renderer resources statically."""
from pathlib import Path
import json,re,hashlib
D=Path(__file__).resolve().parent
def read(n):return (D/'disassembly'/n).read_text()
def main():
 text=read('JinghuiModItems.verbose.txt');boot=text.split('BootstrapMethods:',1)[1]
 bs={int(k):v for k,v in re.findall(r'^  (\d+): (.*?)(?=^  \d+: |\Z)',boot,re.M|re.S)}
 code=text.split('  static {};',1)[1].split('BootstrapMethods:',1)[0]
 p=json.loads((D/'provenance.json').read_text());decls=json.loads((D/'resource-declarations.json').read_text());geometry=json.loads((D/'geometry-study.json').read_text())['cases']
 resources=json.loads((D/'static-declarations.json').read_text());geo=json.loads((D/'geometry-animation-context.json').read_text())
 slots={'helmet':('HELMET',['armorHead']),'chestplate':('CHESTPLATE',['armorBody','armorRightArm','armorLeftArm']),'leggings':('LEGGINGS',['armorRightLeg','armorLeftLeg']),'boots':('BOOTS',['armorRightBoot','armorLeftBoot'])}
 switch=read('GeoArmorRenderer$2.class.txt');base=read('GeoArmorRenderer.class.txt')
 for n,s in enumerate(['HEAD','CHEST','LEGS','FEET'],1):
  assert re.search(r'EquipmentSlot\.'+s+r':[^\n]+\n[^\n]*ordinal:[^\n]+\n[^\n]*iconst_'+str(n)+r'\n[^\n]*iastore',switch)
 method=base.split('  protected void applyBoneVisibilityBySlot(',1)[1].split('  protected ',1)[0]
 assert 'setAllBonesVisible:' in method
 # Fixed4.8.4 switch labels in actual method, not enum ordinals guessed from game knowledge.
 for low,high,fields in [(44,62,['head']),(62,110,['body','rightArm','leftArm']),(110,143,['rightLeg','leftLeg']),(143,176,['rightBoot','leftBoot'])]:
  for f in fields:
   lines=[l for l in method.splitlines() if re.match(r'\s*\d+:',l) and low<=int(l.strip().split(':')[0])<high]
   assert any('// Field '+f+':' in l for l in lines)
 rows=[]
 for c in p['cases']:
  family=c['case_key'].split(':')[1];name=family[0].upper()+family[1:];item=read(name+'Item.class.txt');ext=read(name+'Item$2.class.txt');renderer=read(name+'ArmorRenderer.class.txt');model=read(name+'Model.class.txt')
  assert 'new ' in item and f'// class net/mcreator/jinghui/item/{name}Item$2' in item and 'Consumer.accept:' in item
  assert f'// class net/mcreator/jinghui/client/renderer/{name}ArmorRenderer' in ext and 'GeoArmorRenderer.prepForRender:' in ext
  assert f'// class net/mcreator/jinghui/item/model/{name}Model' in renderer
  roots=set(re.findall(r'// String (armor\w+)',renderer));assert len(roots)==8
  facts=next(a for a in geometry if a['case_key']==c['case_key'])
  raw=json.loads((D/facts['geometry_source']['local']).read_text())['minecraft:geometry'][0]
  rawbones={b['name']:b for b in raw['bones']}
  def ancestry(n):
   out=[]
   while n:
    assert n not in out
    out.append(n);n=rawbones[n].get('parent')
   return out
  counts={root:sum(len(b.get('cubes',[])) for b in raw['bones'] if root in ancestry(b['name'])) for root in roots}
  noncanonical={b['name']:b.get('parent') for b in raw['bones'] if b['name'].startswith('armor') and b['name'] not in roots}
  for part,(typ,bones) in slots.items():
   reg=re.search(r'(?P<excerpt>[^\n]*// String '+family+'_'+part+r'\n[^\n]*// InvokeDynamic #(?P<index>\d+):get:[^\n]*\n[^\n]*DeferredRegister.register:[^\n]*\n[^\n]*// Field (?P<field>\w+):[^\n]*)',code)
   assert reg
   bsblock=bs[int(reg['index'])];factory=re.search(r'REF_invokeStatic net/mcreator/jinghui/init/JinghuiModItems\.(lambda\$static\$\d+):',bsblock).group(1)
   fact=re.search(r'  private static [^\n]* '+re.escape(factory)+r'\(\);(.*?)(?=\n  (?:public|private|protected|static)|\Z)',text,re.S).group(1)
   assert f'// class net/mcreator/jinghui/item/{name}Item' in fact
   assert f'ArmorItem$Type.{typ}:' in fact
   declaration=next(d for d in decls if d['case_key']==c['case_key'] and d['part']==part)
   assert set(bones)<=roots
   absent=[b for b in bones if b not in rawbones]
   empty=[b for b in bones if b in rawbones and counts[b]==0]
   rows.append({'case_key':c['case_key'],'item_id':c['case_key']+'_'+part,'slot_type':typ,'label':declaration['label'],
     'registry_field':reg['field'],'registry_instructions':reg['excerpt'],'factory_bootstrap_index':int(reg['index']),'factory_method':factory,'factory_instructions':fact,
     'item_class':name+'Item','client_extension':name+'Item$2','renderer':name+'ArmorRenderer','geo_model':name+'Model',
     'geometry_source':facts['geometry_source'],'texture_source':facts['atlas_source'],'relevant_armor_roots':bones,
     'native_item_model':declaration['model'],'native_item_icon':declaration['texture'],
     'canonical_root_descendant_cube_counts':{b:counts[b] for b in bones},'missing_expected_geometry_roots':absent,'empty_expected_geometry_roots':empty,'noncanonical_armor_bones':noncanonical,'geometry_slot_correspondence_complete':not(absent or empty),'declared_chain_checked':True,'current_live_render_or_slot_visibility_proven':False})
 assert len(rows)==24
 out={'slot_chains':rows,'four_slot_cases':6,'geckolib_context':'fixed 4.8.4 class/switch, external pack runtime version not assumed',
  'scope':'Static item factory → client extension → concrete renderer → GeoModel resources → relevant armor roots; not current game acceptance.',
  'limits':['原始模型整套同时组装不等于每槽最终显示','GeoArmorRenderer按当前HumanoidModel可见性控制槽骨，可能受其他模组与实际版本影响','同一几何8个根节点或24条槽位不算24套独立设计'],
  'incomplete_geometry_slot_chains':[x['item_id'] for x in rows if not x['geometry_slot_correspondence_complete']],'new_design_credit_from_binding':0,'game_starts':0}
 (D/'binding-study.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('24 fixed native item/slot/client/model chains checked, not live render acceptance.')
if __name__=='__main__':main()
