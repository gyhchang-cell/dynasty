"""D29 source-geometry software study; no runtime or production mutation."""
from pathlib import Path
import json,re,hashlib,inspect,importlib.util
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;R=D.parents[2];BORROW=R/'tools/art/secondary-cuboid/review_models.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def geometry(g):
 bones={b['name']:b for b in g['bones']};records=[];world={};quads=[]
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
   assert set(c)<=set(['size','mirror','inflate','uv','pivot','origin','rotation']);assert isinstance(c['uv'],(list,dict))
   cp=np.array(c.get('pivot',b['pivot']));cm=mat@r.transform(cp-pv,c.get('rotation',[0,0,0]));uvs=r.face_uv(c);infl=c.get('inflate',0)
   for face,corners in r.FACES.items():
    corners=np.array(corners,dtype=float)
    if c.get('mirror'):corners[:,0]=1-corners[:,0]
    xyz=(corners*(np.array(c['size'])+2*infl)+np.array(c['origin'])-infl-cp)*[-1,1,1];xyz=(cm@np.column_stack((xyz,np.ones(4))).T).T[:,:3];quads.append((xyz,uvs[face],name))
   records.append({'bone':name,'cube_index':i,'canonical_armor_root':root(name),'source_cube':c,'software_box_uv':uvs})
 assert len(quads)==6*len(records)

 return r,records,quads

def main():
 p=json.loads((D/'provenance.json').read_text());results=[]
 for family,geoname,texname in [('crabarmor','crabarmor','crabarmortexture'),('sunrise_armor','redhigharmor','redhightexture')]:
  geo=next(a for a in p['records'] if a['entry'].endswith('/'+geoname+'.geo.json'));tex=next(a for a in p['records'] if a['entry'].endswith('/'+texname+'.png'));g=json.loads((D/geo['local']).read_text())['minecraft:geometry'][0]
  r,records,quads=geometry(g);r.TEX=D/tex['local'];r.TEX_SIZE=g['description']['texture_width'];assert g['description']['texture_width']==g['description']['texture_height']==tex['size'][0]==tex['size'][1]
  ims=[r.raster(quads,y,6,size=(300,390)) for y in [0,45,90,180]]+[r.raster(quads,0,6,size=(300,390),silhouette=True)]
  out=Image.new('RGB',(1500,470),(68,73,78));dr=ImageDraw.Draw(out);dr.text((8,8),'NATIVE GEO SOFTWARE STUDY / NOT GAME / NOT DYNASTY / '+family,font=r.font(14),fill='white')
  for i,(im,label) in enumerate(zip(ims,['FRONT','45','SIDE','BACK','BLACK'])):out.paste(im,(i*300,40));dr.text((i*300+10,438),label,font=r.font(15),fill='white')
  name=family+'-assembly.png';out.save(D/name)
  anim=next(a for a in p['records'] if a['entry'].endswith('/'+geoname+'.animation.json'));animation=json.loads((D/anim['local']).read_text())['animations'];bone_names={b['name'] for b in g['bones']};assert all(set(v.get('bones',{}))<=bone_names for v in animation.values())
  results.append({'case_key':'mokels_rpg_two:'+family,'geometry':geo,'texture':tex,'native_cubes':len(records),'cube_records':records,'source_animation':anim,'animation_clips':list(animation),'animation_bones':sorted({b for v in animation.values() for b in v.get('bones',{})}),'static_bind_pose_only':True,'software_page':{'path':name,'sha256':sha(D/name)},'canonical_roots':{b:sum(c['canonical_armor_root']==b for c in records) for b in sorted({c['canonical_armor_root'] for c in records})}})
 save('geometry-study.json',{'cases':results,'borrowed_raster':str(BORROW.relative_to(R)),'borrowed_raster_sha256':sha(BORROW),'limits':['Only bind pose software review, not Minecraft/Gecko runtime','BoxUV inflate/fractional sampling approximate; no animation playback or live slot visibility claim','All original PNG and JSON bytes preserved; no production resource writes'],'game_starts':0})
 print([(x['case_key'],x['native_cubes']) for x in results])
if __name__=='__main__':main()
