#!/usr/bin/env python3
"""Review production reverse waterfall; this is a software projection."""
import json,math,argparse
from pathlib import Path
from PIL import Image,ImageDraw

def render(rows,angle=0,close=False,silhouette=False):
    w,h=1000,600;im=Image.new('RGBA',(w,h),(210,210,210,255) if silhouette else (35,44,43,255));d=ImageDraw.Draw(im)
    camera=(math.sin(math.radians(angle))*76,26,-math.cos(math.radians(angle))*76);target=(0,25,0)
    if close:
        rows=rows[:4];target=tuple(sum(p[i] for q in rows for p in q['points'])/16 for i in range(3))
        a,b,c=rows[0]['points'][:3];u=[b[i]-a[i] for i in range(3)];v=[c[i]-b[i] for i in range(3)];normal=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);length=math.sqrt(sum(n*n for n in normal));camera=tuple(target[i]+normal[i]/length*1.7 for i in range(3))
    def norm(v):
        m=math.sqrt(sum(x*x for x in v));return tuple(x/m for x in v)
    def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
    f=norm(tuple(target[i]-camera[i] for i in range(3)));right=norm(cross(f,(0,1,0)));up=cross(right,f)
    def project(p):
        v=tuple(p[i]-camera[i] for i in range(3));z=sum(x*y for x,y in zip(v,f))
        if z<.1:return None
        return (w/2+sum(x*y for x,y in zip(v,right))*600/z,h/2-sum(x*y for x,y in zip(v,up))*600/z)
    def depth(q):return sum(sum((p[i]-camera[i])**2 for i in range(3)) for p in q['points'])
    for q in sorted(rows,key=depth,reverse=True):
        points=[project(p) for p in q['points']]
        if any(p is None for p in points):continue
        layer=Image.new('RGBA',im.size);c=0 if silhouette else q['color'];ImageDraw.Draw(layer).polygon(points,fill=(c>>16&255,c>>8&255,c&255,255 if silhouette else round(q['alpha']*255)));im=Image.alpha_composite(im,layer)
    d=ImageDraw.Draw(im);d.rectangle((0,h-30,w,h),fill=(20,27,27));d.text((12,h-21),f'PRODUCTION REVERSE WATERFALL / SOFTWARE PREVIEW - NOT IN-GAME / {angle} degrees',fill=(230,224,199));return im.convert('RGB')
def main():
    p=argparse.ArgumentParser();p.add_argument('mesh',type=Path);p.add_argument('output',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    rows=json.loads((a.mesh/'frame-600.json').read_text())
    for angle in [0,45,90,180]:render(rows,angle).save(a.output/f'angle-{angle}.png')
    render(rows,angle=45).save(a.output/'water-detail.png')
    render(rows,angle=45,silhouette=True).save(a.output/'water-silhouette.png')
    frames=[render(json.loads((a.mesh/f'frame-{t}.json').read_text())).resize((600,360),Image.Resampling.NEAREST) for t in range(0,1201,40)]
    frames[0].save(a.output/'motion.webp',save_all=True,append_images=frames[1:],duration=180,loop=0,lossless=True)
if __name__=='__main__':main()
