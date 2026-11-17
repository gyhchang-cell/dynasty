"""Finite symbolic reading of fixed1.19.2 Cube/Polygon UV declarations; no Java execution."""
from pathlib import Path
import json,re,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def insns(s):
 return [(int(a),op,arg.strip()) for a,op,arg in re.findall(r'^\s*(\d+): (\S+)([^\n]*)',s,re.M)]
def local(op,arg):return int(op.split('_')[-1]) if '_' in op else int(arg.split()[0])
def main():
 c=json.loads((D/'collection.json').read_text());p=json.loads((R/c['prior_native_collection']).read_text());cube=next(a for a in p['classes'] if a['name'].endswith('$Cube'));text=(R/Path(c['prior_native_collection']).parent/cube['disassembly']).read_text();ctor=text.split('  public void ',1)[0];ops=insns(ctor)
 polygon=next(a for a in c['classes'] if a['name'].endswith('$Polygon'));pt=(D/polygon['disassembly']).read_text();vertex=next(a for a in c['classes'] if a['name'].endswith('$Vertex'));vt=(D/vertex['disassembly']).read_text();direction=next(a for a in c['classes'] if a['name']=='net.minecraft.core.Direction');mapping=direction['mapping_excerpt'];fields={f:label for label,f in re.findall(r'net.minecraft.core.Direction ([A-Z]+) -> (\w+)',mapping)};assert len(fields)>=6
 # Linear UV expressions of texture offsets and undeformed dimensions.
 first=next(i for i,x in enumerate(ops) if x[0]==271);last=next(i for i,x in enumerate(ops) if x[0]==355);stack=[];locals={1:{'u':1},2:{'v':1},6:{'w':1},7:{'h':1},8:{'d':1}}
 for pc,op,arg in ops[first:last]:
  if op.startswith(('iload','fload')):stack.append(dict(locals[local(op,arg)]))
  elif op=='i2f':pass
  elif op=='fadd':
   b=stack.pop();a=stack.pop();v=dict(a)
   for k,n in b.items():v[k]=v.get(k,0)+n
   stack.append(v)
  elif op.startswith('fstore'):locals[local(op,arg)]=stack.pop()
  else:raise AssertionError((pc,op,arg))
 assert not stack and all(k in locals for k in range(26,35))
 # Eight position declarations, before any polygon-specific UV remap.
 vertex_blocks=re.findall(r'new\s+#[^\n]*// class '+re.escape(vertex['obfuscated_name'])+r'\n(.*?invokespecial[^\n]*// Method '+re.escape(vertex['obfuscated_name'])+r'\."<init>":\(FFFFF\)V\n\s*\d+: astore\s+(\d+))',ctor,re.S);assert len(vertex_blocks)==8
 axis={3:'x0',4:'y0',5:'z0',15:'x1',16:'y1',17:'z1'};vertices={}
 for block,stored in vertex_blocks:
  loads=[local(op,arg) for _,op,arg in insns(block) if op.startswith('fload')];assert len(loads)==3;vertices[int(stored)-18]=[axis[n] for n in loads]
 assert sorted(vertices)==list(range(8))
 # The fixed mirror conditional swaps min/max X before vertex construction.
 mirror_ops=[(op,arg.split('//')[0].strip()) for pc,op,arg in ops if 116<=pc<131];assert mirror_ops==[('iload','12'),('ifeq','131'),('fload','15'),('fstore','18'),('fload_3',''),('fstore','15'),('fload','18'),('fstore_3','')]
 # Six polygon declarations and their explicit vertex arrays, symbolic UV rectangles and directions.
 starts=[i for i,x in enumerate(ops) if x[1]=='getfield' and '// Field g:[' in x[2]];assert len(starts)==6;faces=[]
 for start in starts:
  end=next(i for i in range(start,len(ops)) if ops[i][1]=='invokespecial' and '// Method '+polygon['obfuscated_name']+'."<init>"' in ops[i][2]);segment=ops[start+1:end];indexop=segment[0];assert indexop[1].startswith('iconst_');face_index=int(indexop[1].split('_')[-1]);vids=[local(op,arg)-18 for _,op,arg in segment if op.startswith('aload')];assert len(vids)==4 and all(v in vertices for v in vids)
  floads=[local(op,arg) for _,op,arg in segment if op.startswith('fload')];assert len(floads)==6 and floads[-2:]==[13,14];rect=[locals[x] for x in floads[:4]];d=next(arg for _,op,arg in segment if op=='getstatic');field=re.search(r'// Field '+re.escape(direction['obfuscated_name'])+r'\.(\w+):',d)[1];faces.append({'array_index':face_index,'direction':fields[field],'vertex_indices':vids,'uv_rectangle':rect,'native_excerpt':'\n'.join(f'{pc}: {op} {arg}' for pc,op,arg in ops[start:end+1])})
 assert {f['direction'] for f in faces}=={'DOWN','UP','WEST','EAST','NORTH','SOUTH'}
 # Polygon's remap uses u1,v0 / u0,v0 / u0,v1 / u1,v1 with zero edge epsilon.
 po=insns(pt);call_indices=[i for i,x in enumerate(po) if x[1]=='invokevirtual' and '// Method '+vertex['obfuscated_name']+'.a:(FF)' in x[2]];assert len(call_indices)==4;last=0;orders=[]
 for i in call_indices:
  ns=[local(op,arg) for _,op,arg in po[last:i] if op.startswith('fload')];orders.append([n for n in ns if n in [2,3,4,5]]);last=i+1
 assert orders==[[4,3],[2,3],[2,5],[4,5]],orders
 assert pt.count('fconst_0')>=2 and 'arraylength' in pt and 'isub' in pt and 'iinc          13, 1' in pt and '// float -1.0f' in pt
 assert 'remap(float,float) -> a' in vertex['mapping_excerpt'] and 'Field a:Lk;' in vt
 result={'native_version':'1.19.2','cube_source':cube,'cube_source_base':str(Path(c['prior_native_collection']).parent),'helper_sources':c['classes'],'vertices':vertices,'uv_local_linear_expressions':{str(n):locals[n] for n in range(26,35)},'faces':faces,'polygon_pixel_uv_corner_order':[['u1','v0'],['u0','v0'],['u0','v1'],['u1','v1']],'mirror_rule':{'pre_vertex_swap_x':True,'post_remap_reverse_vertices_and_uv_together':True,'normal_x_multiplier':-1},'native_constructor_excerpt':ctor,'native_polygon_excerpt':pt,'native_vertex_excerpt':vt,'method':'Fixed-source symbolic linear-expression/array declaration reading; no JVM or mod execution','limits':['Bytecode declared face coordinates/mirror closed; not Forge patched hook or actual equipped runtime evidence','Float32 engine rounding vs Python double and software raster precision are not game pixel acceptance'],'game_starts':0,'production_changes':0,'reference_credit':0}
 save('native-uv-contract.json',result);print('Six1.19.2 faces,8vertices,9symbolicUVexpressions,4cornerUVorders and mirror rule read.')
if __name__=='__main__':main()
