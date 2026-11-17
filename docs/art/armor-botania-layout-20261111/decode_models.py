"""Finite reader for this pinned source's literal Cuboid builder declarations; never eval Java."""
from pathlib import Path
import json,hashlib,re,ast,math,operator
D=Path(__file__).resolve().parent;R=D.parents[2];P=R/'docs/art/armor-botania-reference-20261111'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def num(text):
 text=re.sub(r'(?<=\d)[fF]\b','',text.strip()).replace('Mth.PI',str(math.pi));node=ast.parse(text,mode='eval').body
 def solve(n):
  if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)):return n.value
  if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.USub,ast.UAdd)):return (-1 if isinstance(n.op,ast.USub) else 1)*solve(n.operand)
  if isinstance(n,ast.BinOp) and type(n.op) in {ast.Add,ast.Sub,ast.Mult,ast.Div}:return {ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv}[type(n.op)](solve(n.left),solve(n.right))
  raise ValueError(ast.dump(n))
 return solve(node)
def main():
 prov=json.loads((P/'provenance.json').read_text());models={}
 for material,klass in [('manasteel','ManasteelArmorModel'),('elementium','ElementiumArmorModel'),('terrasteel','TerrasteelArmorModel'),('manaweave','ManaweaveRobeModel')]:
  record=next(a for a in prov['sources'] if a['path'].endswith('/'+klass+'.java'));path=P/record['local'];assert sha(path)==record['sha256'];src=path.read_text();stages={}
  for stage,method in [('inner','createInsideMesh'),('outer','createOutsideMesh')]:
   body=re.search(rf'public static MeshDefinition {method}\(\) \{{(.*?)return mesh;',src,re.S).group(1);body=re.sub(r'//[^\n]*','',body);decls=[];vars={'root':'root'}
   for stmt in body.split(';'):
    stmt=' '.join(stmt.split())
    if '.addOrReplaceChild(' not in stmt:continue
    a=re.fullmatch(r'(?:var (\w+) = )?(\w+)\.addOrReplaceChild\("([^"]+)", (CubeListBuilder\.create\(\).*), (PartPose\..*)\)',stmt);assert a,stmt
    var,parent,name,builder,pose=a.groups();assert parent in vars,parent;parent=vars[parent];uv=[0,0];mirror=False;cubes=[]
    calls=re.findall(r'\.(create|texOffs|mirror|addBox)\(([^()]*)\)',builder)
    # Reject unrecognized builder tokens rather than quietly omitting any geometry.
    remainder=re.sub(r'\.(?:create|texOffs|mirror|addBox)\([^()]*\)','',builder);assert remainder.strip()=='CubeListBuilder',remainder
    for call,args in calls:
     vals=[s.strip() for s in args.split(',')] if args else []
     if call=='texOffs':uv=[num(v) for v in vals];assert len(uv)==2
     if call=='mirror':assert not vals;mirror=True
     if call=='addBox':
      assert len(vals) in (6,7),vals;data=[num(v) for v in vals[:6]];deformation=.01 if len(vals)==7 and vals[6]=='deformation' else 0;assert len(vals)==6 or vals[6]=='deformation';cubes.append({'origin':data[:3],'size':data[3:],'uv':uv.copy(),'mirror':mirror,'deformation':deformation})
    if pose=='PartPose.ZERO':xyzrot=[0]*6
    else:
     pa=re.fullmatch(r'PartPose\.(offset|rotation|offsetAndRotation)\((.*)\)',pose);assert pa,pose;kind,args=pa.groups();values=[num(v) for v in args.split(',')];xyzrot=values+[0]*3 if kind=='offset' else [0]*3+values if kind=='rotation' else values;assert len(xyzrot)==6
    decls.append({'name':name,'parent':parent,'pose':xyzrot,'cubes':cubes,'source_declaration':stmt+';'});
    if var:vars[var]=name
   assert len(decls)==body.count('.addOrReplaceChild(');assert sum(len(n['cubes']) for n in decls)==body.count('.addBox(');stages[stage]={'nodes':decls,'cube_count':sum(len(n['cubes']) for n in decls)}
  models['botania:'+material]={'source':str(path.relative_to(R)),'source_sha256':sha(path),'stages':stages,'texture':str((P/f'source/Xplat/src/main/resources/assets/botania/textures/model/armor_{material}.png').relative_to(R))}
 out={'models':models,'source_commit':prov['commit'],'method':'All addOrReplaceChild/addBox declarations consumed; arithmetic AST limited to numeric constants,+,-,*,/ and Mth.PI; no JVM/mod execution','game_acceptance':False};(D/'decoded-models.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print({k:{s:v['cube_count'] for s,v in a['stages'].items()} for k,a in models.items()})
if __name__=='__main__':main()
