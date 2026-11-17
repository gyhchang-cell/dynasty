import json,sys
from pathlib import Path
from collections import deque,Counter
P=Path(__file__).resolve().parent;R=P.parents[2];sys.path.insert(0,str(R/'tools/architecture'))
from whole_building_candidates import AIR,color
from PIL import Image,ImageDraw
def ld(n):return json.loads((P/n).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
d=ld('F02-original.json');pal=d['palette'];b={tuple(x['pos']):x for x in d['blocks']}
regions=[]
for name,xs,ys,zs in [('main-work-service',range(17,26),range(0,4),range(10,16)),('deep-work-service',range(1,9),range(2,6),range(37,43)),('shaft-interface',range(19,24),range(46,48),range(2,7))]:
 rows=[dict(y=y,z_rows=[[b.get((x,y,z),{}).get('state',-1)for x in xs]for z in zs])for y in ys]
 regions.append(dict(name=name,x=[xs.start,xs.stop-1],y=[ys.start,ys.stop-1],z=[zs.start,zs.stop-1],rows=rows))
 print(name,json.dumps(rows,separators=(',',':')))
put('F02-critical-state-matrices.json',regions)
air={p for p,v in b.items()if pal[v['state']]['Name']in AIR}
def path(s,t):
 if s not in air or t not in air:return None
 q=deque([s]);prev={s:None}
 while q:
  p=q.popleft()
  if p==t:
   out=[]
   while p is not None:out.append(p);p=prev[p]
   return out[::-1]
  for a in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
   n=tuple(p[i]+a[i]for i in range(3))
   if n in air and n not in prev:prev[n]=p;q.append(n)
 return None
paths=[]
for s,t in [((20,47,4),(23,2,13)),((23,2,13),(4,4,40))]:
 p=path(s,t);paths.append(dict(start=s,target=t,path=p,step_count=None if p is None else len(p)-1,meaning='6-neighbor explicit-air adjacency ONLY; no collision/standing support/headroom/door/processor/native NPC route proof'))
 print('AIR_PATH',s,t,p)
put('air-adjacency-not-navigation.json',paths)
special=[dict(pos=list(p),state=pal[v['state']],**({'nbt':v['nbt']}if 'nbt'in v else {}))for p,v in b.items()if any(t in pal[v['state']]['Name']for t in ['brewing_stand','dispenser','tripwire','piston','redstone','observer','water','lava','stone_button','crafting_table'])]
put('devices-original-states.json',special)
# A vertical section exposes the unbuilt, air-only tunnel below the upper shaft.
im=Image.new('RGB',(1520,900),'#edf0f2');dr=ImageDraw.Draw(im)
for j,(axis,loc,w) in enumerate([('x',21,45),('z',39,26)]):
 ox=j*760+60;oy=55;step=15;dr.text((ox,20),f'F02 {axis}={loc}; y0..47; WHITE air / BLACK omitted',fill='black')
 for y in range(48):
  for a in range(w):
   p=(loc,y,a)if axis=='x'else(a,y,loc);v=b.get(p);n=pal[v['state']]['Name']if v else None;c='#151a24'if n is None else '#ffffff'if n in AIR else color(n)
   dr.rectangle((ox+a*step,oy+(47-y)*step,ox+(a+1)*step,oy+(48-y)*step),fill=c,outline='#a9afb5')
 for y in range(0,48,5):dr.text((ox-25,oy+(47-y)*step),str(y),fill='black')
im.save(P/'F02-vertical.png')
