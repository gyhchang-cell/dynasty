#!/usr/bin/env python3
"""Selected original/rigid-joined planes; do not infer collision or route completion."""
from collections import defaultdict
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent;BASE=OUT.parent
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 detail=module('detail',BASE/'research-20261101-dungeons-002/inspect_details.py');detail.OUT=OUT
 detail.SPECS={'F01':(9,41,12,8)};detail.main()
 body=json.loads((OUT/'sources.json').read_text())['candidates'][0]
 with ZipFile(body['source_archive'])as z:d=detail.read(z.read(body['member']))
 pal=d.get('palette')or d['palettes'][0]
 body_states={tuple(b['pos']):pal[b['state']]for b in d['blocks']}
 composite={tuple(e['position']):e['state']for e in json.loads((OUT/'assembly-original-states.json').read_text())['states']}
 cuts=[('y',6,18,18),('y',50,18,18),('x',8,18,58),('z',7,18,58)]
 sheet=Image.new('RGB',(1440,1480),'#edf0f2');draw=ImageDraw.Draw(sheet)
 for i,(axis,fixed,width,height)in enumerate(cuts):
  left=(i%2)*720+45;top=(i//2)*710+60;step=min(640/width,620/height)
  draw.text((left,top-40),f'A01 {axis}={fixed}; '+('+X right / +Z down'if axis=='y'else'height up'),fill='#17252c')
  for v in range(height):
   for h in range(width):
    p=(h,fixed,v)if axis=='y'else(fixed,v,h)if axis=='x'else(h,v,fixed)
    row=v if axis=='y'else height-1-v;x,y=left+h*step,top+row*step
    draw.rectangle((x,y,x+step,y+step),fill=detail.shade(composite.get(p)),outline='#bfc6ca')
  for h in range(0,width,5):draw.text((left+h*step,top-17),str(h),fill='#17252c')
  for v in range(0,height,5):
   row=v if axis=='y'else height-1-v;draw.text((left-23,top+row*step),str(v),fill='#17252c')
 draw.text((20,1433),'CYAN ladder / two exact source modules / final connectors replaced by authored air / classification colours',fill='#17252c')
 draw.text((20,1453),'RESEARCH / no collision, terrain projection, path-finding or native jigsaw execution',fill='#17252c')
 sheet.save(OUT/'A01-details.png')
 ladders=defaultdict(list)
 for p,s in composite.items():
  if s['Name']=='minecraft:ladder':ladders[(p[0],p[2])].append(p[1])
 supplemental=dict(id='A01',image='A01-details.png',cuts=[dict(axis=a,coordinate=f,width=w,height=h)for a,f,w,h in cuts],
  ladder_runs=[dict(x=x,z=z,ys=sorted(ys))for(x,z),ys in sorted(ladders.items())],native_routes_verified=False)
 out=json.loads((OUT/'detail-evidence.json').read_text());out['assembly_entries']=[supplemental]
 (OUT/'detail-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 planes=[]
 for ident,states,ys in [('F01',body_states,[9,41]),('A01',composite,[6,50])]:
  planes.append(dict(id=ident,planes=[dict(y=y,original_or_rigid_translated_states=[dict(position=list(p),state=s)for p,s in states.items()if p[1]==y])for y in ys],
   source_limit='F01 preserves original stored air vs absence; A01 contains translated nonair only with authored connector air excluded.'))
 (OUT/'selected-plane-states.json').write_text(json.dumps(dict(entries=planes,building_credit=0),ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
