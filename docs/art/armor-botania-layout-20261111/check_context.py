"""Compare the pinned1.20 source declarations with the reused finite face contract."""
from pathlib import Path
import json,re,hashlib,collections
D=Path(__file__).resolve().parent;R=D.parents[2];P=R/'docs/art/armor-historic-binding-20261104/vanilla-source/a569a8fe46e3-ModelPart.java';C=R/'docs/art/armor-native-face-uv-20261111/native-uv-contract.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 s=P.read_text();c=json.loads(C.read_text());ctor=s.split('public Cube(',1)[1].split('public void compile(',1)[0];args=ctor.split(') {',1)[0].split(', ');names=[a.split(' ')[-1] for a in args];env={names[0]:'u',names[1]:'v',names[5]:'w',names[6]:'h',names[7]:'d'};xyz={names[2]:'x0',names[3]:'y0',names[4]:'z0','f':'x1','f1':'y1','f2':'z1'}
 vertices={}
 for var,terms in re.findall(r'ModelPart.Vertex (modelpart\$vertex\d*) = new ModelPart.Vertex\(([^)]+)\);',ctor):vertices[var]=[xyz[t.strip()] for t in terms.split(',')[:3]]
 assert len(vertices)==8;indices={var:next(int(i) for i,v in c['vertices'].items() if v==xyz) for var,xyz in vertices.items()}
 expr={}
 for var,terms in re.findall(r'float (f\d+) = ([^;]+);',ctor):
  terms=terms.replace('(float)','');ts=terms.split(' + ')
  if all(t in env for t in ts):expr[var]=dict(collections.Counter(env[t] for t in ts))
 assert len(expr)==9
 faces=[]
 for verts,rest in re.findall(r'new ModelPart.Polygon\(new ModelPart.Vertex\[\]\{([^}]+)\}, ([^;]+)\);',ctor):
  ts=rest.split(', ');direction=ts[-1].split('.')[-1];actual={'direction':direction,'vertex_indices':[indices[t.strip()] for t in verts.split(',')],'uv_rectangle':[expr[t] for t in ts[:4]]};expected=next(f for f in c['faces'] if f['direction']==direction);assert all(actual[k]==expected[k] for k in actual);faces.append(actual)
 assert len(faces)==6
 for i,uv in enumerate(['p_104365_ / p_104367_ - f, p_104364_ / p_104368_ + f1','p_104363_ / p_104367_ + f, p_104364_ / p_104368_ + f1','p_104363_ / p_104367_ + f, p_104366_ / p_104368_ - f1','p_104365_ / p_104367_ - f, p_104366_ / p_104368_ - f1']):assert f'p_104362_[{i}] = p_104362_[{i}].remap({uv});' in s
 assert 'p_104362_[i - 1 - j] = modelpart$vertex' in s and 'this.normal.mul(-1.0F, 1.0F, 1.0F)' in s and 'rotationZYX(this.zRot, this.yRot, this.xRot)' in s
 out={'source':str(P.relative_to(R)),'source_sha256':sha(P),'reused_face_contract':str(C.relative_to(R)),'reused_face_contract_sha256':sha(C),'matched1_20_faces':faces,'matched1_20_vertices':8,'matched_uv_expressions':9,'corner_order_and_mirror_declarations_match':True,'rotation_order':'ZYX','not_engine_execution':True};(D/'source-context-comparison.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('1.20 native source declarations: 6faces,8vertices,9UVexpressions,4cornerorders,mirror and ZYX matched.')
if __name__=='__main__':main()
