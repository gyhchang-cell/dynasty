"""Actual PNG/UV software inspection, explicitly separate from native QA."""
import base64
import copy
import json
import uuid
import math
import numpy as np
from pathlib import Path
from PIL import Image
import review_models as view
from material_atlas import IDS
from build_models import ASSET, REPO

OUT=REPO/'docs/art/secondary-materials-v2'
BEFORE=REPO/'build/maintenance/secondary-materials-v2/before'
TITLE='Original nonhuman rigs / actual PNG + UV / SOFTWARE ONLY'
GRAY=REPO/'build/maintenance/secondary-materials-v2/gray.png'


def source(id):
    g=json.loads((ASSET/f'geo/secondary/{id}.geo.json').read_text())['minecraft:geometry'][0]
    groups={};elements=[]
    uid=lambda label:str(uuid.uuid5(uuid.NAMESPACE_URL,'dynasty/secondary-material-v2/'+id+'/'+label))
    point=lambda p:[-p[0],p[1],p[2]]
    angle=lambda p:[-p[0],-p[1],p[2]]
    for b in g['bones']:
        group={'name':b['name'],'type':'group','uuid':uid(b['name']),
               'origin':point(b['pivot']),'rotation':angle(b.get('rotation',[0,0,0])),
               'export':True,'isOpen':True,'children':[]}
        groups[b['name']]=group
        for i,c in enumerate(b.get('cubes',[])):
            x,y,z=c['origin'];w,h,d=c['size'];key=uid(b['name']+'/'+str(i));faces={}
            for face,m in c['uv'].items():
                u,v=m['uv'];du,dv=m['uv_size']
                faces[face]={'uv':[u+du,v+dv,u,v] if face in ('up','down') else [u,v,u+du,v+dv],'texture':0}
            elements.append({'name':b['name']+'_'+str(i),'type':'cube','uuid':key,
                'from':[-x-w,y,z],'to':[-x,y+h,z+d],
                'origin':point(c.get('pivot',b['pivot'])),
                'rotation':angle(c.get('rotation',[0,0,0])),
                'box_uv':False,'inflate':0,'faces':faces})
            group['children'].append(key)
    roots=[]
    for b in g['bones']:
        if b.get('parent'):groups[b['parent']]['children'].append(groups[b['name']])
        else:roots.append(groups[b['name']])
    tp=ASSET/f'textures/entity/secondary/{id}.png';w=g['description']['texture_width'];h=g['description']['texture_height']
    bb={'meta':{'format_version':'4.10','model_format':'geckolib_model','box_uv':False},
        'name':id,'model_identifier':'secondary_'+id,'geckolib_modid':'dynasty',
        'resolution':{'width':w,'height':h},'elements':elements,'outliner':roots,
        'textures':[{'name':tp.name,'id':'0','uuid':uid('texture'),'width':w,'height':h,
            'uv_width':w,'uv_height':h,'source':'data:image/png;base64,'+base64.b64encode(tp.read_bytes()).decode()}]}
    dest=OUT/'blockbench';dest.mkdir(parents=True,exist_ok=True)
    (dest/f'{id}.bbmodel').write_text(json.dumps(bb,indent=2)+'\n')
    (dest/f'{id}.animation.json').write_bytes((ASSET/f'animations/secondary/{id}.animation.json').read_bytes())


def main():
    view.OUT=OUT;images=[];labels=[];compare=[];clabels=[]
    views=OUT/'software';views.mkdir(parents=True,exist_ok=True)
    gray=GRAY;gray.parent.mkdir(parents=True,exist_ok=True)
    Image.new('RGB',(64,64),'#b5b8b3').save(gray)
    meshes=[view.geometry(id) for id in sorted(IDS)]
    meshes.extend(view.geometry(id,geo_path=BEFORE/f'geo/secondary/{id}.geo.json') for id in sorted(IDS))
    points=np.concatenate([p for q in meshes for p,_,_ in q])
    def bounds(yaw):
        yaw=math.radians(yaw);elevation=math.radians(6)
        toward=np.array([math.sin(yaw)*math.cos(elevation),math.sin(elevation),-math.cos(yaw)*math.cos(elevation)])
        right=np.array([math.cos(yaw),0,math.sin(yaw)]);up=np.cross(toward,right)
        if up[1]<0:up=-up
        projected=points@np.vstack((right,up,toward)).T
        return projected.min(0),projected.max(0)
    for id in sorted(IDS):
        source(id)
        q=view.geometry(id)
        for name,yaw,black in [('front',0,False),('45',45,False),('side',90,False),('left',-90,False),('back',180,False),('silhouette',45,True)]:
            im=view.raster(q,yaw,6,size=(340,320),silhouette=black,frame_bounds=bounds(yaw))
            im.save(views/f'{id}-{name}.png');images.append(im);labels.append(id+' '+name)
        view.TEX=gray
        im=view.raster(q,45,6,size=(340,320),frame_bounds=bounds(45));im.save(views/f'{id}-gray.png')
        # Same geometry, camera, scale and light on before/after comparisons.
        before=view.geometry(id,geo_path=BEFORE/f'geo/secondary/{id}.geo.json')
        view.TEX=BEFORE/f'textures/entity/secondary/{id}.png'
        compare.append(view.raster(before,45,6,size=(340,320),frame_bounds=bounds(45)));clabels.append(id+' before')
        after=view.geometry(id)
        compare.append(view.raster(after,45,6,size=(340,320),frame_bounds=bounds(45)));clabels.append(id+' after')
        for clip,tick in [('wander',6),('attack',5),('special',10)]:
            posed=view.geometry(id,clip,tick)
            view.raster(posed,45,6,size=(340,320)).save(views/f'{id}-{clip}-{tick}.png')
    view.sheet(images,labels,'software-views.png',TITLE,6)
    view.sheet(compare,clabels,'software-before-after.png','Before / after - same scale - SOFTWARE',2)
    print('Generated editable projects and real-UV software inspection; native QA remains separate')


if __name__=='__main__':main()
