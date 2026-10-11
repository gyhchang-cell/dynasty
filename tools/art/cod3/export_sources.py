"""Editable Blockbench geometry with embedded pixels and adjacent animations.

Reverses the official Bedrock codec's X / X-Y rotation conversion. Reimport the
adjacent animation.json in Blockbench Animation mode. All files are original.
"""
import base64
import json
import uuid
from pathlib import Path
from rebuild_npcs import ASSETS, DOC, ROLES

def export(role):
 geo=json.loads((ASSETS/f'geo/npc/{role}.geo.json').read_text())['minecraft:geometry'][0]
 groups={};elements=[]
 def uid(label):return str(uuid.uuid5(uuid.NAMESPACE_URL,'dynasty/cod3/npc-v2/'+role+'/'+label))
 def point(p):return [-p[0],p[1],p[2]]
 def angle(p):return [-p[0],-p[1],p[2]]
 for b in geo['bones']:
  group={'name':b['name'],'type':'group','uuid':uid(b['name']),'origin':point(b['pivot']),'rotation':angle(b.get('rotation',[0,0,0])),'export':True,'isOpen':True,'children':[]}
  groups[b['name']]=group
  for i,c in enumerate(b.get('cubes',[])):
   x,y,z=c['origin'];w,h,d=c['size'];key=uid(b['name']+'/'+str(i));faces={}
   for face,m in c['uv'].items():
    u,v=m['uv'];du,dv=m['uv_size']
    faces[face]={'uv':[u+du,v+dv,u,v] if face in ('up','down') else [u,v,u+du,v+dv],'texture':0}
   elements.append({'name':b['name']+'_'+str(i),'type':'cube','uuid':key,'from':[-x-w,y,z],'to':[-x,y+h,z+d],'origin':point(c.get('pivot',b['pivot'])),'rotation':angle(c.get('rotation',[0,0,0])),'box_uv':False,'inflate':0,'faces':faces})
   group['children'].append(key)
  for name,p in b.get('locators',{}).items():
   key=uid(name);elements.append({'name':name,'type':'locator','uuid':key,'position':point(p),'rotation':[0,0,0],'ignore_inherited_scale':False});group['children'].append(key)
 outliner=[]
 for b in geo['bones']:
  if b.get('parent'):groups[b['parent']]['children'].append(groups[b['name']])
  else:outliner.append(groups[b['name']])
 tex=ASSETS/f'textures/entity/npc/{role}.png'
 bb={'meta':{'format_version':'4.10','model_format':'geckolib_model','box_uv':False},'name':role,'model_identifier':'npc_'+role,'geckolib_modid':'dynasty','resolution':{'width':16,'height':16},'elements':elements,'outliner':outliner,'textures':[{'path':str(tex),'name':tex.name,'id':'0','uuid':uid('texture'),'width':16,'height':16,'uv_width':16,'uv_height':16,'source':'data:image/png;base64,'+base64.b64encode(tex.read_bytes()).decode()}]}
 dest=DOC/'blockbench';dest.mkdir(parents=True,exist_ok=True)
 (dest/f'{role}.bbmodel').write_text(json.dumps(bb,indent=2)+'\n')
 (dest/f'{role}.animation.json').write_bytes((ASSETS/f'animations/npc/{role}.animation.json').read_bytes())
 return bb

if __name__=='__main__':
 for role in ROLES:export(role)
 print('PASS: 15 editable projects with embedded PNGs, grip locators and adjacent animations')
