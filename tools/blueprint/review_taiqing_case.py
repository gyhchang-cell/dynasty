#!/usr/bin/env python3
"""Inspect actual native case elements at their world scale; never starts Java."""
from pathlib import Path
import ast,json,numpy as np,math
from PIL import Image
R=Path(__file__).resolve().parents[2];A=R/'src/main/resources/assets/dynasty';D=R/'docs/blueprint-cod1/evidence/zhanlu-sword-v1';p=R/'tools/blueprint/review_taoyan_cauldrons.py';ns={'__file__':str(p)};exec(p.read_text().split('\nreport={}\n',1)[0],ns);ns['sheet'].__globals__['D']=D;r=ns['r'];images=[];top_images=[];checks={}
for state in ('','_ready','_open'):
 name='taiqing_ancient_sword_case'+state;model=json.loads((A/f'models/block/{name}.json').read_text());q=[];allpts=[];swordpts=[]
 for element in model['elements']:
  lo=np.array(element['from'],float);hi=np.array(element['to'],float)
  for face,corners in r.FACES.items():
   points=lo+np.array(corners)*(hi-lo)
   if element.get('rotation'):
    rotation=element['rotation'];assert rotation['axis']=='z' and rotation['angle']==-45;theta=math.radians(-45);m=np.array([[math.cos(theta),-math.sin(theta),0],[math.sin(theta),math.cos(theta),0],[0,0,1]]);pivot=np.array(rotation['origin']);points=(points-pivot)@m.T+pivot
   source=element['faces'][face];tex=A/'textures'/('block/taiqing_ancient_sword_case.png' if source['texture']=='#all' else 'entity/blueprint/artifact/zhanlu_rendao_bamian_jian.png');u,v,u1,v1=source['uv'];texture=np.array(Image.open(tex).convert('RGB'));assert len({tuple(x) for x in texture[int(v):int(v1),int(u):int(u1)].reshape(-1,3)})==1
   q.append((points,{'uv':[u,v],'uv_size':[u1-u,v1-v],'_tex':texture},name));allpts.append(points)
   if source['texture']=='#sword':swordpts.append(points)
 points=np.concatenate(allpts);checks[name]={'nativeElements':len(model['elements']),'dimensionsMetres':((points.max(0)-points.min(0))/16).tolist(),'swordCubes':len(swordpts)//6}
 if swordpts:
  s=np.concatenate(swordpts);assert abs((s[:,2].max()-s[:,2].min())/16-1.4)<1e-8;assert s[:,0].min()>=4 and s[:,0].max()<=12 and s[:,1].min()>=1 and s[:,1].max()<=9 and s[:,2].min()>=-2 and s[:,2].max()<=26
 top_images.append(ns['raster'](q+ns['references'](45),np.array(Image.open(A/'textures/block/taiqing_ancient_sword_case.png').convert('RGB')),yaw=45,elevation=65,size=(1000,700),mode='lit'))
 images.append(ns['raster'](q+ns['references'](45),np.array(Image.open(A/'textures/block/taiqing_ancient_sword_case.png').convert('RGB')),yaw=45,elevation=25,size=(1000,700),mode='lit'))
ns['sheet'](images+top_images,['封匣：实际15块剑体封存于木壁铜盖内','试炼完成：滑盖后展示实际1.4m剑体','领取后：空匣与滑盖留存','封匣俯视','解封俯视：核对内部剑体','领取后俯视：核对空匣'],'真实原生模型 / 2m匣与1.4m同源剑 / 固定5.5px每单位与1.8m人、1m石参照 / 软件非游戏','taiqing-case-states.png',cols=3)
(D/'taiqing-case-software.json').write_text(json.dumps({'staticChecks':'PASS_SOURCE_SOFTWARE_ONLY','nativeChecks':'NOT_RUN_USER_EXAM_JAVA_PAUSE','models':checks},ensure_ascii=False,indent=2)+'\n');print(checks)
