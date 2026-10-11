"""Check every exported runtime rig against its editable Blockbench source."""
import base64,hashlib,json
import numpy as np
from build_models import OUT,REPO
from resource_paths import resource_paths
ids=json.loads((REPO/'tools/art/cod2-voxel/owned-models.json').read_text())['ids']
results=[]
for name in ids:
 gp,ap,tp=resource_paths(name);bbp=OUT/'blockbench'/(name+'.bbmodel');bap=OUT/'blockbench'/(name+'.animation.json')
 g=json.loads(gp.read_text())['minecraft:geometry'][0];bb=json.loads(bbp.read_text());groups={};parents={}
 def visit(nodes,parent=None):
  for node in nodes:
   if isinstance(node,dict):
    assert node['name'] not in groups;groups[node['name']]=node;parents[node['name']]=parent;visit(node['children'],node['name'])
 visit(bb['outliner'])
 assert set(groups)=={b['name'] for b in g['bones']}
 for b in g['bones']:
  v=groups[b['name']];assert parents[b['name']]==b.get('parent')
  assert np.allclose(v['origin'],np.array(b['pivot'])*[-1,1,1])
  assert np.allclose(v['rotation'],np.array(b.get('rotation',[0,0,0]))*[-1,-1,1])
 assert base64.b64decode(bb['textures'][0]['source'].split(',',1)[1])==tp.read_bytes()
 assert bap.read_bytes()==ap.read_bytes(),'Independent animation source out of date: '+name
 results.append(dict(id=name,paths=[str(p.relative_to(REPO)) for p in [gp,ap,tp,bbp,bap]],sha256={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [gp,ap,tp,bbp,bap]}))
(OUT/'editable-source-validation.json').write_text(json.dumps(dict(passed=True,models=results,files=len(results)*5,check='All runtime/source bones, parent topology, axes, embedded PNGs, independent animation bytes and SHAs'),indent=2)+'\n')
print('PASS',len(results),'models /',len(results)*5,'runtime and editable files')
