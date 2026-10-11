"""Small production check for texture-only exports; no Java/Gradle processes."""
import json,hashlib,subprocess,copy
from PIL import Image
from build import A,R,IDS
from retexture import D,shape

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(scope=False):
 report={}
 for id in IDS+['hammer_chain']:
  path=A/'geo/boss_forms'/(id+'.geo.json');geo=json.loads(path.read_text());old=json.loads((D/'before'/(id+'.geo.json')).read_text())
  assert shape(geo)==shape(old),(id,'approved shape changed')
  animation=A/'animations/boss_forms'/(id+'.animation.json');assert animation.read_bytes()==(D/'before'/(id+'.animation.json')).read_bytes(),(id,'timeline changed')
  g=geo['minecraft:geometry'][0];im=Image.open(A/'textures/entity/boss_forms'/(id+'.png'));assert im.size==(g['description']['texture_width'],g['description']['texture_height']);assert im.mode=='RGB'
  boxes=[];minratio=2;maxratio=0;nonflat=0;area=0
  for b in g['bones']:
   for c in b['cubes']:
    sx,sy,sz=c['size'];assert set(c['uv'])=={'north','south','west','east','up','down'}
    for f,v in c['uv'].items():
     x,y=v['uv'];w,h=v['uv_size'];target=(sx,sz) if f in ['up','down'] else (sz,sy) if f in ['east','west'] else (sx,sy)
     assert all(isinstance(n,int) for n in [x,y,w,h]) and min(x,y,w,h)>=1 and x+w<im.width and y+h<im.height
     assert [w,h]==[max(1,round(t)) for t in target]
     ratios=[v/t for v,t in zip([w,h],target)];minratio=min(minratio,*ratios);maxratio=max(maxratio,*ratios)
     for X,Y,W,H in boxes:assert x+w<=X or X+W<=x or y+h<=Y or Y+H<=y,(id,'UV overlap')
     boxes.append((x,y,w,h));a=w*h;area+=a
     if len(im.crop((x,y,x+w,y+h)).getcolors(a))>1:nonflat+=a
  info={'atlas':list(im.size),'faces':len(boxes),'uniqueIslands':len(set(boxes)),'pixelsPerBlock':16,'roundingDensityMinMax':[round(minratio*16,2),round(maxratio*16,2)],'nonflatSurfaceAreaPercent':round(nonflat/area*100,1),'paletteColors':len(im.getcolors(im.width*im.height)),'geometryAndRigUnchanged':True,'animationBytesUnchanged':True,'pngSha256':digest(A/'textures/entity/boss_forms'/(id+'.png'))}
  if id in IDS:
   assert (D/id/'texture.png').read_bytes()==(A/'textures/entity/boss_forms'/(id+'.png')).read_bytes()
   assert (D/id/'uv-checker.png').read_bytes()!=(A/'textures/entity/boss_forms'/(id+'.png')).read_bytes()
   bb=json.loads((R/'docs/art/boss-forms-v2/blockbench'/(id+'.bbmodel')).read_text());import base64
   assert base64.b64decode(bb['textures'][0]['source'].split(',')[1])==(A/'textures/entity/boss_forms'/(id+'.png')).read_bytes()
  report[id]=info
 # Runtime path resolution is checked against the real registration, not guessed from filenames.
 renderer=(R/'src/main/java/com/dynasty/client/BossFormsRenderer.java').read_text();bindings=(R/'src/main/java/com/dynasty/client/BossEightArtBindings.java').read_text()
 assert 'folder+"/boss_forms/"+id+suffix' in renderer and 'resource("textures/entity",".png")' in renderer
 assert all(id in bindings for id in IDS[:3])
 for cls,id in zip(['HeadlessGeneral','Mechanist','Jinwu','FoxMatron','HammerGuardian'],IDS[3:]):
  assert cls+'.ID' in bindings
  source=(R/f'src/main/java/com/dynasty/blueprint/elite/{cls}.java').read_text();assert 'ID = \"'+id+'\"' in source or 'ID=\"'+id+'\"' in source
 base=json.loads((D/'baseline.json').read_text())['baseCommit']
 if scope:
  assert not subprocess.check_output(['git','diff',base,'--','src/main/java','src/main/resources/assets/dynasty/animations/boss_forms']), 'Code/collision/timeline changed'
 assert (A/'textures/entity/boss_forms/hammer_chain.png').read_bytes()==(A/'textures/entity/boss_forms'/f'{IDS[7]}.png').read_bytes()
 result={'status':'PASS_TEXTURE_OFFLINE_ONLY','build':'NOT_RUN_USER_EXAM_JAVA_HOLD','nativeMinecraft':'NOT_RUN_USER_EXAM_JAVA_HOLD','previewLighting':'unlit or neutral software diffuse; not native lighting','runtimeBinding':'8 existing IDs -> BossFormsRenderer.Model -> boss_forms/<id>.png, no entity scale multiplier','externalPixelsUsed':False,'models':report}
 (D/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='models'},ensure_ascii=False));return result
if __name__=='__main__':
 import sys
 run('--scope-check' in sys.argv)
