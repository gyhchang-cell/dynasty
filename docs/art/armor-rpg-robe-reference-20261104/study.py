"""D28 static material/model declarations and source geometry assembly."""
from pathlib import Path
import json,re,hashlib,math,inspect,importlib.util
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;R=D.parents[2];BORROW=R/'tools/art/secondary-cuboid/review_models.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 p=json.loads((D/'provenance.json').read_text());model=(D/'disassembly/WizardArmorModel.class.txt').read_text();verbose=(D/'disassembly/WizardArmorModel.verbose.txt').read_text();armors=(D/'disassembly/Armors.class.txt').read_text();av=(D/'disassembly/Armors.verbose.txt').read_text();ext=(D/'disassembly/WizardArmor$1.class.txt').read_text();armor=(D/'disassembly/WizardArmor.class.txt').read_text();renderer=(D/'disassembly/WizardArmorRenderer.class.txt').read_text()
 assert 'WizardArmorRenderer' in ext and 'prepForRender:' in ext and 'WizardArmorModel' in renderer and 'Consumer.accept:' in armor
 assert 'geo/wizard_robes.geo.json' in model and r'textures/armor/\u0001.png' in verbose
 anim=model.split('getAnimationResource(net.wizards.item.WizardArmor);',1)[1].split('\n  public ',1)[0];assert 'aconst_null' in anim
 controllers=armor.split(' registerControllers(',1)[1].split('\n  public ',1)[0];assert '0: return' in controllers and 'AnimationController' not in controllers
 context=next(x for x in p['geometry_context'] if '/geo/' in x['entry']);g=json.loads((D/context['local']).read_text())['minecraft:geometry'][0];bones={b['name']:b for b in g['bones']};records=[];world={};quads=[]
 spec=importlib.util.spec_from_file_location('readonly_rpg_reference',BORROW);r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
 code=inspect.getsource(r.raster).replace(".convert('RGB')",".convert('RGBA')").replace('color=np.zeros((*xx.shape,3)) if silhouette else atlas[ty,tx]*shade','mask &= atlas[ty,tx,3]>127\n            color=np.zeros((*xx.shape,3)) if silhouette else atlas[ty,tx,:3]*shade');exec(code,r.__dict__)
 def matrix(name):
  if name in world:return world[name]
  b=bones[name];pv=np.array(b['pivot']);parent=b.get('parent');pos=pv-(np.array(bones[parent]['pivot']) if parent else np.zeros(3));world[name]=(matrix(parent) if parent else np.eye(4))@r.transform(pos,b.get('rotation',[0,0,0]));return world[name]
 def root(name):
  if name in ['armorHead','armorBody','armorRightArm','armorLeftArm','armorRightLeg','armorLeftLeg','armorRightBoot','armorLeftBoot']:return name
  return root(bones[name]['parent']) if bones[name].get('parent') else None
 for name,b in bones.items():
  mat=matrix(name);pv=np.array(b['pivot'])
  for i,c in enumerate(b.get('cubes',[])):
   assert set(c)<=set(['size','mirror','inflate','uv','pivot','origin','rotation']);assert isinstance(c['uv'],list)
   cp=np.array(c.get('pivot',b['pivot']));cm=mat@r.transform(cp-pv,c.get('rotation',[0,0,0]));uvs=r.face_uv(c);infl=c.get('inflate',0)
   for face,corners in r.FACES.items():
    corners=np.array(corners,dtype=float)
    if c.get('mirror'):corners[:,0]=1-corners[:,0]
    xyz=(corners*(np.array(c['size'])+2*infl)+np.array(c['origin'])-infl-cp)*[-1,1,1];xyz=(cm@np.column_stack((xyz,np.ones(4))).T).T[:,:3];quads.append((xyz,uvs[face],name))
   records.append({'bone':name,'cube_index':i,'canonical_armor_root':root(name),'source_cube':c,'software_box_uv':uvs})
 assert len(records)==17 and len(quads)==102
 rows=[];pages=[];boot=av.split('BootstrapMethods:',1)[1];bs={int(k):v for k,v in re.findall(r'^  (\d+): (.*?)(?=^  \d+: |\Z)',boot,re.M|re.S)}
 init=armors.split('  static {};',1)[1]
 for case in p['cases']:
  family=case['case_key'].split(':')[1];tex=next(a for a in p['native_atlases'] if a['case_key']==case['case_key']);assert tex['size']==[64,64]
  match=re.search(r'(?P<excerpt>[^\n]*// String '+family+r'\n.*?Armor\$CustomMaterial\."<init>"[^\n]*\n[^\n]*// Field (?P<field>material_\w+):[^\n]*)',init,re.S);assert match
  field=match['field'];allmatches=list(re.finditer(r'// Field '+field+r':',init));assert len(allmatches)==2
  start=allmatches[1].start();segment=init[start:];bound=segment.index('Armor$Entry.armorSet:');segment=segment[:bound];indices=re.findall(r'// InvokeDynamic #(\d+):apply:',segment);assert len(indices)==1
  factory=re.search(r'REF_invokeStatic net/wizards/item/Armors\.(lambda\$static\$\d+):',bs[int(indices[0])]).group(1)
  fact=re.search(r'  private static [^\n]* '+re.escape(factory)+r'\([^\n]*\);(.*?)(?=\n  (?:public|private|protected|static)|\Z)',armors,re.S).group(1)
  fields=re.findall(r'// Field net/minecraft/class_1738\$class_8051\.(field_\d+):',fact);assert len(fields)==len(set(fields))==4 and fact.count('// class net/wizards/item/WizardArmor')==4
  rows.append({'case_key':case['case_key'],'material_field':field,'native_material_constructor_excerpt':match['excerpt'],'factory_method':factory,'factory_excerpt':fact,'distinct_intermediary_slot_type_fields':fields,'slot_type_names_not_assumed_from_order':True,'geometry_resource':'wizards:geo/wizard_robes.geo.json','source_geometry':context,'source_texture':tex,'texture_resource':'wizards:textures/armor/'+family+'.png','custom_material_name_concatenation_checked':True,'four_item_factory_declaration_checked':True,'external_Armor_Set_registration_and_live_slot_visibility_proven':False})
  r.TEX=D/tex['local'];r.TEX_SIZE=64
  ims=[r.raster(quads,y,6,size=(300,390)) for y in [0,45,90,180]]+[r.raster(quads,0,6,size=(300,390),silhouette=True)]
  out=Image.new('RGB',(1500,470),(68,73,78));dr=ImageDraw.Draw(out);dr.text((8,8),'SOFTWARE SOURCE STUDY / NOT GAME / FABRIC-AZURELIB / '+case['case_key'],font=r.font(14),fill='white')
  for j,(im,label) in enumerate(zip(ims,['FRONT','45','SIDE','BACK','BLACK'])):out.paste(im,(j*300,40));dr.text((j*300+10,438),label,font=r.font(15),fill='white')
  name=case['case_key'].replace(':','-')+'-assembly.png';out.save(D/name);pages.append({'case_key':case['case_key'],'path':name,'sha256':sha(D/name)})
 save('binding-and-geometry-study.json',{'material_cases':rows,'source_geometry':context,'geometry_grid':[64,64],'native_cubes':17,'cube_records':records,'root_descendant_cubes':{x:sum(c['canonical_armor_root']==x for c in records) for x in sorted(set(c['canonical_armor_root'] for c in records))},'borrowed_raster':str(BORROW.relative_to(R)),'borrowed_raster_sha256':sha(BORROW),'software_analysis_pages':pages,'source_animation_file_is_selected':False,'getAnimationResource_excerpt':anim,'registerControllers_excerpt':controllers,'game_starts':0,'new_design_credit':0,'limits':['Fabric/AzureLib参考不等于Forge/GeckoLib可直接加载资产','BoxUV软件观察含小数、inflate与镜像近似处理，不能证明AzureLib实际采样/可见性/接缝','外部Armor$Set注册实现及中间命名映射未据本包完全闭合，不以28图标冒充28个实机槽链','7种材料共用17体块同geo，不计7个独立模型设计；包内动画文件存在不等于当前被选用']})
 print('7 same-geometry materials, 7 declared four-item factories, 17 source cubes, no selected animation resource; zero game starts.')
if __name__=='__main__':main()
