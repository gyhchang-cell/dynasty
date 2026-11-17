"""Strict finite literal decoding of the pinned1.19.2 stock createMesh; no Java execution."""
from pathlib import Path
import json,re,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def constants(s,yoffset=0):
 out=[]
 for line in s.splitlines():
  m=re.search(r'^\s*\d+: (\S+)(.*)',line)
  if not m:continue
  op,arg=m.groups()
  if op.startswith(('iconst_','fconst_')):out.append(float(op.split('_')[-1].replace('m1','-1')))
  elif op in ['bipush','sipush']:out.append(float(arg.strip().split()[0]))
  elif op in ['ldc','ldc_w'] and '// float ' in arg:out.append(float(arg.split('// float ')[1].strip().rstrip('f')))
  elif op=='fload_1':out.append(float(yoffset))
  elif op=='fadd':v=out.pop();out[-1]+=v
 return out

def main():
 c=json.loads((D/'native-source-collection.json').read_text());entry=next(e for e in c['classes'] if e['name']=='net.minecraft.client.model.HumanoidModel');s=(D/entry['disassembly']).read_text();m=next(x for x in re.split(r'(?=\n  (?:public|private|protected|static) )',s) if 'public static ' in x and '// String head' in x);assert ' if' not in m and 'goto' not in m
 blocks=re.findall(r'// String (head|hat|body|right_arm|left_arm|right_leg|left_leg)\n(.*?)(?=// String |\n[^\n]*areturn)',m,re.S);assert len(blocks)==7
 # Mapping ties obfuscated APIs to texOffs,addBox,mirror,extend,offset,addOrReplaceChild.
 names={e['name']:e for e in c['classes']};builder=names['net.minecraft.client.model.geom.builders.CubeListBuilder'];deform=names['net.minecraft.client.model.geom.builders.CubeDeformation'];pose=names['net.minecraft.client.model.geom.PartPose'];bd=builder['obfuscated_name'];df=deform['obfuscated_name'];ps=pose['obfuscated_name'];assert 'texOffs(int,int) -> a' in builder['mapping_excerpt'] and 'mirror() -> a' in builder['mapping_excerpt'] and 'extend(float) -> a' in deform['mapping_excerpt'] and 'offset(float,float,float) -> a' in pose['mapping_excerpt']
 records=[]
 for name,block in blocks:
  t=block.index('// Method '+bd+'.a:(II)L'+bd+';');uv=constants(block[:t]);assert len(uv)==2
  g=block.index('// Method '+bd+'.a:(FFFFFFL'+df+';)L'+bd+';');middle=block[t:g];nums=constants(middle);extra=nums[6:];assert len(nums)==(7 if name=='hat' else 6)
  offset=block[g:];end=offset.index('// Method '+ps+'.a:(FFF)L'+ps+';');pos=constants(offset[:end]);assert len(pos)==3,(name,pos)
  records.append({'part':name,'uv':uv,'origin':nums[:3],'size':nums[3:6],'mirrored':('// Method '+bd+'.a:()L'+bd+';') in middle,'hat_deformation_extension':extra[0] if extra else 0,'pivot':pos,'deformation_from_argument':True,'method_excerpt':block})
 layer=names['net.minecraft.client.model.geom.LayerDefinitions'];ls=(D/layer['disassembly']).read_text();init=ls[ls.rfind('\n  static {};'):];assert 'fconst_1' in init and '// float 0.5f' in init and 'Field b:L'+df+';' in init and 'Field c:L'+df+';' in init
 assert 'OUTER_ARMOR_DEFORMATION -> b' in layer['mapping_excerpt'] and 'INNER_ARMOR_DEFORMATION -> c' in layer['mapping_excerpt']
 old=json.loads((R/'docs/art/armor-three-slot-closure-20261111/layout-study.json').read_text());comparison=[]
 for row in records:
  native_name=row['part'];prior_name={'right_leg':'right_leg_inner','left_leg':'left_leg_inner'}.get(native_name,native_name);o=next(x for x in old['mesh_declarations'] if x[0]==prior_name)
  assert row['origin']==o[1] and row['size']==o[2] and row['uv']==o[3] and row['mirrored']==o[4] and row['pivot']==o[5]
  comparison.append({'part':native_name,'origin_size_uv_mirror_pose_equal':True,'outer_deformation_1_19_2':1+(row['hat_deformation_extension']),'inner_deformation_1_19_2':.5+row['hat_deformation_extension'],'outer_deformation_1_20_1':.9 if 'leg' in native_name else 1+row['hat_deformation_extension'],'inner_deformation_1_20_1':.4 if 'leg' in native_name else .5+row['hat_deformation_extension'],'difference':'leg .1 smaller in1.20 armor-specific mesh' if 'leg' in native_name else 'none for this local declaration'})
 save('native-layout-comparison.json',{'native_version':'1.19.2','decoded_mesh_parts':records,'comparison_to_D31_1_20_context':comparison,'native_outer_deformation':1.0,'native_inner_deformation':.5,'native_leg_deformation_extension':0.0,'newer_HumanoidArmorModel_absent':True,'native_createMesh_excerpt':m,'native_LayerDefinitions_static_excerpt':init,'mapping_sources':{n:e['mapping_excerpt'] for n,e in names.items()},'limits':['Only fixed native mesh declarations compared, not Forge patched renderer/hooks/resource pack behavior','Polygon sampler UV orientation still reused from pinned1.20 ModelPart source context, not claimed independently decoded1.19 native cube polygons','Source context not in-game rendering/animation/seams acceptance; no independent design credit'],'game_starts':0,'production_changes':0,'reference_credit':0})
 print('Seven native1.19.2 mesh parts exactly decoded; dimensions/UV/mirror/pose same; leg deformation difference0.1 recorded.')
if __name__=='__main__':main()
