"""Finite source-derived local cube bake audit; does not execute Java or render equipped armor."""
from pathlib import Path
import json,hashlib,math,zipfile
D=Path(__file__).resolve().parent;R=D.parents[2];S=D/'source/software/bernie/geckolib';A=R/'docs/art/armor-ars-reference-20261111'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
# Named vertex order copied from BakedModelFactory.VertexSet, not vanilla ModelPart.
ORDER={'west':[3,2,0,1],'east':[4,5,7,6],'north':[2,4,6,0],'south':[5,3,1,7],'up':[3,5,4,2],'down':[0,6,7,1]}
def bake(b,c,w,h):
 size=c['size'];o=c['origin'];inf=c.get('inflate',b.get('inflate',0)) or 0;f=inf/16;origin=[-(o[0]+size[0])/16,o[1]/16,o[2]/16];sv=[v/16 for v in size];x,y,z=origin;sx,sy,sz=sv
 vertices=[[x-f,y-f,z-f],[x-f,y-f,z+sz+f],[x-f,y+sy+f,z-f],[x-f,y+sy+f,z+sz+f],[x+sx+f,y+sy+f,z-f],[x+sx+f,y+sy+f,z+sz+f],[x+sx+f,y-f,z-f],[x+sx+f,y-f,z+sz+f]]
 mirror=c.get('mirror') is True;uv=c['uv'];box=isinstance(uv,list);quads=[]
 for direction in ORDER:
  route=direction
  if mirror:
   if direction in ['west','east']:route='east' if direction=='west' else 'west'
   if not box and direction in ['up','down']:route='down' if direction=='up' else 'up'
  if box:
   u,v=uv;xx,yy,zz=map(math.floor,size)
   data={'west':([u+zz+xx,v+zz],[zz,yy]),'east':([u,v+zz],[zz,yy]),'north':([u+zz,v+zz],[xx,yy]),'south':([u+zz+xx+zz,v+zz],[xx,yy]),'up':([u+zz,v],[xx,zz]),'down':([u+zz+xx,v+zz],[xx,-zz])};coord,extent=data[direction];rotation=0
  else:
   face=uv.get(direction)
   if face is None:continue
   coord,extent=face['uv'],face['uv_size'];rotation=face.get('uv_rotation',0);assert rotation in [0,90,180,270]
  u,v=coord;du,dv=extent;um=(u+du)/w;vm=(v+dv)/h;u/=w;v/=h
  if not mirror:u,um=um,u
  corners=[[u,v],[um,v],[um,vm],[u,vm]];shift=rotation//90;corners=corners[shift:]+corners[:shift]
  quads.append({'direction':direction,'vertex_route':route,'vertices':[vertices[i] for i in ORDER[route]],'normalized_uv':corners,'uv_rotation':rotation,'normal_x_flipped':mirror})
 p=c.get('pivot',[0,0,0]);rot=c.get('rotation',[0,0,0])
 return {'local_origin_blocks':origin,'inflate_blocks':f,'cube_mirror':mirror,'bone_mirror_not_inherited_by_builtin_cube':b.get('mirror'),'pivot_pixels':[-p[0],p[1],p[2]],'rotation_radians':[math.radians(-rot[0]),math.radians(-rot[1]),math.radians(rot[2])],'quads':quads}
def main():
 col=json.loads((D/'collection.json').read_text());archive=D/'geckolib-4.8.4-sources.jar';assert hashlib.sha1(archive.read_bytes()).hexdigest()==(D/'upstream.sha1').read_text().strip().split()[0]
 with zipfile.ZipFile(archive) as z:
  sources=[]
  for p in sorted((D/'source').rglob('*.java')):
   entry=p.relative_to(D/'source').as_posix();assert p.read_bytes()==z.read(entry);sources.append({'entry':entry,'path':str(p.relative_to(R)),'sha256':sha(p)})
 # Guard source conditions that differ materially from the old generic helper.
 conditions={'loading/object/BakedModelFactory.java':['boolean mirror = cube.mirror() == Boolean.TRUE;','cube.inflate() != null ? cube.inflate() / 16f','origin = new Vec3(-(origin.x + size.x) / 16d','mirror && !boxUv ? quadDown() : quadUp()','Math.floor(uvSize[0])'],'cache/object/GeoQuad.java':['if (!mirror)','normal.mul(-1, 1, 1);','uvRotation.rotateUvs'],'cache/object/GeoBone.java':['setChildrenHidden(hidden);'],'renderer/GeoRenderer.java':['if (bone.isHidden())','if (bone.isHidingChildren())','RenderUtils.rotateMatrixAroundCube(poseStack, cube);'],'renderer/GeoArmorRenderer.java':['if (!(this.currentEntity instanceof GeoAnimatable))','applyBoneVisibilityBySlot(this.currentSlot);','poseStack.scale(-1, -1, 1);'],'util/RenderUtils.java':['Axis.ZP.rotation(bone.getRotZ())','Axis.YP.rotation(bone.getRotY())','Axis.XP.rotation(bone.getRotX())']}
 excerpts=[]
 for path,tokens in conditions.items():
  lines=(S/path).read_text().splitlines()
  for token in tokens:
   hits=[i+1 for i,l in enumerate(lines) if token in l];assert hits,(path,token);excerpts.append({'source':path,'lines':hits,'text':token})
 rows=[];geos=[]
 slots={'HEAD':['armorHead'],'CHEST':['armorBody','armorRightArm','armorLeftArm'],'LEGS':['armorRightLeg','armorLeftLeg'],'FEET':['armorRightBoot','armorLeftBoot']}
 for name in ['light','medium','heavy']:
  file=A/f'source/src/main/resources/assets/ars_nouveau/geo/{name}_armor.geo.json';g=json.loads(file.read_text())['minecraft:geometry'][0];bones=g['bones'];by={b['name']:b for b in bones};w=g['description']['texture_width'];h=g['description']['texture_height'];counts={};visible={}
  for slot,roots in slots.items():
   included=[]
   for b in bones:
    current=b;anc=[]
    while current:
     anc.append(current['name']);current=by.get(current.get('parent'))
    if any(n.lower() in ['armorrightarmslim','armorleftarmslim'] for n in anc):continue
    if any(n in roots for n in anc):included.append(b['name'])
   visible[slot]=included;counts[slot]=sum(len(by[n].get('cubes',[])) for n in included)
  for b in bones:
   for i,c in enumerate(b.get('cubes',[])):
    row={'model':name,'bone':b['name'],'cube_index':i,'source_cube':c,'source_bone_inflate':b.get('inflate'),'source_bone_mirror':b.get('mirror'),'bake':bake(b,c,w,h)}
    for q in row['bake']['quads']:assert all(-1e-8<=u<=1+1e-8 and -1e-8<=v<=1+1e-8 for u,v in q['normalized_uv'])
    rows.append(row)
  geos.append({'model':name,'geo':str(file.relative_to(R)),'sha256':sha(file),'slot_visible_bones_assuming_base_parts_visible':visible,'slot_cube_counts_assuming_base_parts_visible':counts,'bone_count':len(bones),'source_bone_rotations':[{'bone':b['name'],'rotation':b['rotation']} for b in bones if any(b.get('rotation',[0,0,0]))]})
 assert len(rows)==61 and sum(sum(g['slot_cube_counts_assuming_base_parts_visible'].values()) for g in geos)==49
 save('source-contract.json',{'artifact':col['artifact'],'archive_sha256':sha(archive),'upstream_sha1_verified':True,'sources':sources,'checked_source_conditions':excerpts,'source_read_scope':'BakedModelFactory/GeoQuad/GeoCube/Cube/Bone/UVUnion/UVFaces/FaceUV full; GeoBone constructor and visibility; GeoRenderer recursive/cubes/child/cube; GeoArmorRenderer preRender/actuallyRender/slot/base-transform; RenderUtils matrix and match methods; JsonUtil numeric defaults','rules':['cube mirror only; bone mirror stored but not inherited by Builtin.constructCube','inflate cube override else bone; divide by16; enlarge vertices not UV','origin X negates origin+width; pivot X and rotation X/Y negated; angles radians','boxUV floor original uninflated size; down UV size negative Z; per-face missing faces omitted','mirror swaps east/west vertex routes; per-face also up/down; GeoQuad not-mirror swaps U; mirror flips normal X; no vanilla winding reversal','matrix bone translate/pivot/Z/Y/X/scale/unpivot; cube pivot/Z/Y/X/unpivot; hierarchy retained','setHidden hides children too; Ars recursive equalsIgnoreCase removes slim subtrees','non-GeoAnimatable entity slot gating; GeoAnimatable branch requires caller-specific validation'],'engine_execution':False})
 save('local-bake-study.json',{'geometries':geos,'cubes':rows,'cube_count':61,'non_slim_all_slot_cube_count':49,'local_source_derived_numerics_only':True,'full_equipped_world_transform_or_actual_render_acceptance':False,'runtime_animation_and_external_hooks_pending':True})
 print(json.dumps({'sources':len(sources),'cube_count':len(rows),'slot_counts':{g['model']:g['slot_cube_counts_assuming_base_parts_visible'] for g in geos}},ensure_ascii=False))
if __name__=='__main__':main()
