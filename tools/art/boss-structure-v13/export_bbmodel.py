"""Editable source with the same geometry, per-face UV and numeric animation channels.
Coordinate inversions follow Blockbench's Bedrock parseCube/parseBone implementation.
"""
import json,uuid,base64
from pathlib import Path
from create import D,IDS
out=D/'blockbench';out.mkdir(exist_ok=True)
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'dynasty:boss_structure_v13:'+s))
def vector(v,sign):return [x*y for x,y in zip(v,sign)]
for id in IDS:
 geo=json.loads((D/'candidates'/id/f'{id}.geo.json').read_text())['minecraft:geometry'][0];bones=geo['bones'];desc=geo['description'];groups={};elements=[]
 for b in bones:
  n=b['name'];group={'name':n,'type':'group','uuid':uid(id+n),'origin':vector(b['pivot'],[-1,1,1]),'rotation':vector(b.get('rotation',[0,0,0]),[-1,-1,1]),'export':True,'isOpen':True,'children':[]};groups[n]=group
  for j,c in enumerate(b.get('cubes',[])):
   eid=uid(id+n+str(j));o=c['origin'];size=c['size'];start=[-o[0]-size[0],o[1],o[2]];faces={}
   for f,v in c['uv'].items():
    x,y=v['uv'];w,h=v['uv_size'];uv=[x,y,x+w,y+h]
    if f in ['up','down']:uv=uv[2:]+uv[:2]
    faces[f]={'uv':uv,'texture':0}
   elements.append({'name':n+'_'+str(j),'type':'cube','uuid':eid,'from':start,'to':[start[k]+size[k] for k in range(3)],'origin':vector(c.get('pivot',b['pivot']),[-1,1,1]),'rotation':vector(c.get('rotation',[0,0,0]),[-1,-1,1]),'box_uv':False,'faces':faces});group['children'].append(eid)
 roots=[]
 for b in bones:
  if b.get('parent'):groups[b['parent']]['children'].append(groups[b['name']])
  else:roots.append(groups[b['name']])
 animations=[]
 for name,a in json.loads((D/'candidates'/id/f'{id}.animation.json').read_text())['animations'].items():
  anim={'uuid':uid(id+name),'name':name,'loop':'loop' if a.get('loop') is True else 'hold' if a.get('loop') == 'hold_on_last_frame' else 'once','override':False,'length':a['animation_length'],'snapping':20,'animators':{}}
  for bn,channels in a['bones'].items():
   keyframes=[]
   for channel,track in channels.items():
    for t,v in ({'0':track} if isinstance(track,list) else track).items():
     sign=[-1,-1,1] if channel=='rotation' else [-1,1,1] if channel=='position' else [1,1,1];v=vector(v,sign)
     keyframes.append({'channel':channel,'data_points':[dict(zip(['x','y','z'],[str(x) for x in v]))],'uuid':uid(id+name+bn+channel+t),'time':float(t),'color':-1,'interpolation':'linear'})
   anim['animators'][groups[bn]['uuid']]={'name':bn,'type':'bone','keyframes':keyframes}
  animations.append(anim)
 texture=(D/'candidates'/id/'gray.png').read_bytes();bb={'meta':{'format_version':'4.10','model_format':'geckolib_model','box_uv':False},'name':id,'model_identifier':id,'geckolib_modid':'dynasty','resolution':{'width':desc['texture_width'],'height':desc['texture_height']},'elements':elements,'outliner':roots,'animations':animations,'textures':[{'name':'gray.png','id':'0','uuid':uid(id+'texture'),'width':desc['texture_width'],'height':desc['texture_height'],'uv_width':desc['texture_width'],'uv_height':desc['texture_height'],'source':'data:image/png;base64,'+base64.b64encode(texture).decode()}]}
 (out/(id+'.bbmodel')).write_text(json.dumps(bb,ensure_ascii=False,indent=2)+'\n')
print('Three structural candidates include grey material and motion samples; not production animations.')
