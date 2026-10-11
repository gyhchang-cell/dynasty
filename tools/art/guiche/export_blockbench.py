"""Export an editable GeckoLib Blockbench project from the authored runtime rig.

Uses the Bedrock exporter coordinate convention: mirror X and invert X/Y angles.
The animation JSON is supplied alongside the project for Blockbench import.
"""
import base64
import json
import uuid
from build_model import REPO, GEO, ANIM, TEX, ID


def main():
    geo = json.loads(GEO.read_text())['minecraft:geometry'][0]
    groups, elements = {}, []
    uid = lambda key: str(uuid.uuid5(uuid.NAMESPACE_URL, 'dynasty/'+ID+'/'+key))
    for bone in geo['bones']:
        x,y,z = bone['pivot']
        rx,ry,rz = bone.get('rotation',[0,0,0])
        group = dict(name=bone['name'], type='group', uuid=uid(bone['name']),
                     origin=[-x,y,z], rotation=[-rx,-ry,rz], export=True,
                     isOpen=True, children=[])
        groups[bone['name']] = group
        for i,c in enumerate(bone.get('cubes',[])):
            x,y,z=c['origin'];w,h,d=c['size'];key=uid(bone['name']+'/'+str(i))
            faces={}
            for face,uv in c['uv'].items():
                u,v=uv['uv'];du,dv=uv['uv_size']
                faces[face]=dict(uv=[u+du,v+dv,u,v] if face in ('up','down') else [u,v,u+du,v+dv],texture=0)
            pivot=c.get('pivot',bone['pivot']);rot=c.get('rotation',[0,0,0])
            elements.append(dict(name=bone['name']+'_'+str(i),type='cube',uuid=key,
                **{'from':[-x-w,y,z],'to':[-x,y+h,z+d]},
                origin=[-pivot[0],pivot[1],pivot[2]],rotation=[-rot[0],-rot[1],rot[2]],
                inflate=c.get('inflate',0),box_uv=False,faces=faces))
            group['children'].append(key)
    roots=[]
    for bone in geo['bones']:
        if bone.get('parent'):groups[bone['parent']]['children'].append(groups[bone['name']])
        else:roots.append(groups[bone['name']])
    data=dict(meta=dict(format_version='4.10',model_format='geckolib_model',box_uv=False),
        name=ID,model_identifier=ID,geckolib_modid='dynasty',resolution=dict(width=16,height=16),
        elements=elements,outliner=roots,textures=[dict(name=TEX.name,id='0',uuid=uid('texture'),
        width=16,height=16,uv_width=16,uv_height=16,
        source='data:image/png;base64,'+base64.b64encode(TEX.read_bytes()).decode())])
    dest=REPO/'docs/art/guiche-v2/blockbench';dest.mkdir(exist_ok=True)
    (dest/(ID+'.bbmodel')).write_text(json.dumps(data,indent=2)+'\n')
    (dest/ANIM.name).write_bytes(ANIM.read_bytes())
    print(f'Exported {len(groups)} groups and {len(elements)} cubes; embedded 16x16 texture')


if __name__=='__main__':main()
