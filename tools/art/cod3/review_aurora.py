#!/usr/bin/env python3
"""Software projection of JSON emitted by the production Java mesh, never a game screenshot."""
import json,math,random,argparse
from pathlib import Path
from PIL import Image,ImageDraw

def render(rows,azimuth=0,distance=96):
 w,h=900,600;im=Image.new('RGB',(w,h),(8,17,28));d=ImageDraw.Draw(im);rng=random.Random(15)
 for i in range(180):
  x,y=rng.randrange(w),rng.randrange(h);d.rectangle((x,y,x+1,y+1),fill=(40,57,68))
 angle=math.radians(azimuth);camera=(math.sin(angle)*distance,2,-math.cos(angle)*distance);target=(0,95,0)
 def norm(v):
  n=math.sqrt(sum(a*a for a in v));return tuple(a/n for a in v)
 def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
 forward=norm(tuple(target[i]-camera[i] for i in range(3)));right=norm(cross(forward,(0,1,0)));up=cross(right,forward)
 def dot(a,b):return sum(x*y for x,y in zip(a,b))
 def project(p):
  v=tuple(p[i]-camera[i] for i in range(3));z=dot(v,forward)
  if z<1:return None
  f=w/(2*math.tan(math.radians(70)/2));return (w/2+dot(v,right)*f/z,h/2-dot(v,up)*f/z)
 def depth(q):return sum(sum((p[i]-camera[i])**2 for i in range(3)) for p in q['points'])/4
 for q in sorted(rows,key=depth,reverse=True):
  points=[project(p) for p in q['points']]
  if any(p is None for p in points):continue
  layer=Image.new('RGBA',im.size);ld=ImageDraw.Draw(layer);color=q['color'];ld.polygon(points,fill=(color>>16&255,color>>8&255,color&255,round(255*q['alpha'])));im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
 d=ImageDraw.Draw(im);d.rectangle((0,h-32,w,h),fill=(13,22,31));d.text((12,h-23),f'PRODUCTION MESH / SOFTWARE PREVIEW   angle={azimuth}   distance={distance} blocks   NOT IN-GAME',fill=(201,219,228));return im

def main():
 p=argparse.ArgumentParser();p.add_argument('mesh',type=Path);p.add_argument('output',type=Path);p.add_argument('--duration',type=int,default=1800);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 for az in [0,45,90,180]:render(json.loads((a.mesh/'lod-64.json').read_text()),az,64).save(a.output/f'angle-{az}.png')
 for dist in [24,64,128]:render(json.loads((a.mesh/f'lod-{dist}.json').read_text()),0,dist).save(a.output/f'lod-{dist}.png')
 frames=[render(json.loads((a.mesh/f'frame-{t}.json').read_text()),0,64).resize((600,400),Image.Resampling.NEAREST) for t in range(0,a.duration+1,a.duration//30)]
 frames[0].save(a.output/'motion.webp',save_all=True,append_images=frames[1:],duration=180,loop=0,lossless=True)
if __name__=='__main__':main()
