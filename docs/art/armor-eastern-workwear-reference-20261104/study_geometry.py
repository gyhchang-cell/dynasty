"""Read-only static reference assembly; software analysis, never game acceptance."""
from pathlib import Path
import json,hashlib,importlib.util,inspect,math
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;R=D.parents[2]
BORROW=R/'tools/art/secondary-cuboid/review_models.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 spec=importlib.util.spec_from_file_location('readonly_reference_raster',BORROW);r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
 # Preserve transparent texels during analysis; originals stay byte-identical.
 code=inspect.getsource(r.raster).replace(".convert('RGB')",".convert('RGBA')")
 code=code.replace("color=np.zeros((*xx.shape,3)) if silhouette else atlas[ty,tx]*shade","mask &= atlas[ty,tx,3]>127\n            color=np.zeros((*xx.shape,3)) if silhouette else atlas[ty,tx,:3]*shade")
 exec(code,r.__dict__)
 prov=json.loads((D/'provenance.json').read_text());context=json.loads((D/'geometry-animation-context.json').read_text());facts=[]
 for a in context:
  if a['kind']!='GEOMETRY_ATLAS_CONTEXT':continue
  g=json.loads((D/a['local']).read_text())['minecraft:geometry'][0];bones={b['name']:b for b in g['bones']};world={};quads=[];records=[]
  def matrix(name):
   if name in world:return world[name]
   b=bones[name];pv=np.array(b['pivot']);parent=b.get('parent');pos=pv-(np.array(bones[parent]['pivot']) if parent else np.zeros(3))
   world[name]=(matrix(parent) if parent else np.eye(4))@r.transform(pos,b.get('rotation',[0,0,0]));return world[name]
  def armor_root(name):
   if name.startswith('armor'):return name
   p=bones[name].get('parent');return armor_root(p) if p else None
  for name,b in bones.items():
   mat=matrix(name);pivot=np.array(b['pivot'])
   for i,c in enumerate(b.get('cubes',[])):
    assert set(c)<= {'origin','size','uv','pivot','rotation'} and isinstance(c['uv'],list)
    cp=np.array(c.get('pivot',b['pivot']));cm=mat@r.transform(cp-pivot,c.get('rotation',[0,0,0]));uvs=r.face_uv(c)
    for face,corners in r.FACES.items():
     points=(np.array(corners)*np.array(c['size'])+np.array(c['origin'])-cp)*[-1,1,1]
     points=(cm@np.column_stack((points,np.ones(4))).T).T[:,:3];quads.append((points,uvs[face],name))
    records.append({'bone':name,'cube_index':i,'armor_root':armor_root(name),'origin':c['origin'],'size':c['size'],'uv':c['uv'],'faces':uvs})
  tex=next(x for x in prov['worn_textures'] if x['case_key']==a['case_key']);r.TEX=D/tex['local'];r.TEX_SIZE=g['description']['texture_width']
  actual=Image.open(r.TEX).size;assert actual[0]/r.TEX_SIZE==actual[1]/g['description']['texture_height']
  views=[r.raster(quads,y,6,size=(330,420)) for y in [0,45,90,180]]
  views.append(r.raster(quads,0,6,size=(330,420),silhouette=True))
  out=Image.new('RGB',(1650,500),(68,73,78));dr=ImageDraw.Draw(out)
  dr.text((8,8),'READ-ONLY REFERENCE ASSEMBLY / SOFTWARE / NOT GAME / '+a['case_key'],font=r.font(16),fill='white')
  for j,(im,label) in enumerate(zip(views,['FRONT','45','SIDE','BACK','BLACK'])):out.paste(im,(j*330,40));dr.text((j*330+12,467),label,font=r.font(16),fill='white')
  dest=a['case_key'].replace(':','-')+'-assembly.png';out.save(D/dest)
  # Name-independent shape signature helps find exact same geometry with a different texture.
  structural=[{k:b[k] for k in ['name','parent','pivot','rotation','cubes'] if k in b} for b in g['bones']]
  roots=sorted({x['armor_root'] for x in records if x['armor_root']})
  facts.append({'case_key':a['case_key'],'geometry_source':a,'atlas_source':tex,'uv_grid':[g['description']['texture_width'],g['description']['texture_height']],
      'native_texture_size':list(actual),'texture_to_uv_scale':actual[0]/r.TEX_SIZE,'cubes':len(records),'bones':len(bones),'armor_roots_with_cubes':roots,
      'cube_count_by_armor_root':{root:sum(x['armor_root']==root for x in records) for root in roots},
      'geometry_structure_sha256':hashlib.sha256(json.dumps(structural,sort_keys=True).encode()).hexdigest(),'cube_uv_records':records,
      'software_assembly':dest,'software_assembly_sha256':sha(D/dest),'current_player_slot_or_runtime_proven':False})
 result={'cases':facts,'borrowed_raster':str(BORROW.relative_to(R)),'borrowed_raster_sha256':sha(BORROW),
   'source_geometry_not_modified':True,'limits':['外部源模型静态组装，不是游戏截图或最终玩家姿态','全套骨骼同时显示，不证明单槽可见性、动画、穿戴姿态或接缝验收','BoxUV按现有软件查看器读取；透明像素过滤，未用预览证明真实shader采样','模型本身有完整人物/非甲部件时只作反例，不拿四个物品名当适用完整甲信用'],
   'new_design_credit':0,'game_starts':0}
 (D/'geometry-study.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'families':len(facts),'cubes':sum(x['cubes'] for x in facts),'software_analysis_sheets':len(facts),'game_starts':0}))
if __name__=='__main__':main()
