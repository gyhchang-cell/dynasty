#!/usr/bin/env python3
"""Pixel-hard software inspection of production geometry; not an in-game screenshot."""
import argparse,json,math
from pathlib import Path
from PIL import Image,ImageDraw

def render(quads):
    im=Image.new('RGBA',(800,600),(117,166,230,255))
    for q in sorted(quads,key=lambda q:q['points'][0][1],reverse=True):
        pts=[(400+x*550/y,300-z*550/y) for x,y,z in q['points']]
        layer=Image.new('RGBA',im.size);c=q['color']
        ImageDraw.Draw(layer).polygon(pts,fill=(c>>16&255,c>>8&255,c&255,round(q['alpha']*255)))
        im=Image.alpha_composite(im,layer)
    d=ImageDraw.Draw(im);d.rectangle((391,291,409,309),fill=(255,255,238))
    d.rectangle((0,566,800,600),fill=(22,35,48));d.text((12,578),'SOLAR FRAME / PRODUCTION MESH / SOFTWARE PREVIEW - NOT IN-GAME',fill=(230,235,235))
    return im.convert('RGB')

def main():
    p=argparse.ArgumentParser();p.add_argument('mesh',type=Path);p.add_argument('output',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    frames=[render(json.loads((a.mesh/f'frame-{t}.json').read_text())) for t in range(0,601,20)]
    frames[15].save(a.output/'solar-frame.png')
    frames[0].save(a.output/'motion.webp',save_all=True,append_images=frames[1:],duration=180,loop=0,lossless=True)
if __name__=='__main__':main()
