"""Research-only original-coordinate diagram; no texture or gameplay output."""
import json
import sys
from pathlib import Path
from zipfile import ZipFile
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parents[2]/'tools/architecture'))
from nbt_read import read
def main():
    c=json.loads((OUT/'sources.json').read_text())['candidates'][1]
    with ZipFile(c['source_archive']) as z:n=read(z.read(c['member']))
    ss={tuple(b['pos']):n['palette'][b['state']] for b in n['blocks']}
    im=Image.new('RGB',(1710,660),'#eef1f3');d=ImageDraw.Draw(im)
    d.text((15,10),'F02 original axes: +X right, +Z down. Eight lit red candle blocks surround a trapped chest; TNT below. Purpose remains unproven.',fill='black')
    glyphs={'minecraft:air':('.', '#f4f5f5'),'minecraft:tnt':('T','#ee6767'),'minecraft:red_candle':('C','#d883a0'),
        'minecraft:trapped_chest':('X','#f3b13b'),'minecraft:soul_sand':('s','#c6af75'),'minecraft:grass_block':('g','#8db279')}
    for col,y in enumerate((0,1,2)):
        left=25+col*565;top=80;d.text((left,40),f'Original layer y={y}',fill='black')
        for x in range(15):d.text((left+x*34+10,top-20),str(x),fill='black')
        for z in range(15):
            d.text((left-18,top+z*34+10),str(z),fill='black')
            for x in range(15):
                name=ss[(x,y,z)]['Name'];label,color=glyphs.get(name,('d','#9e8a70') if 'dirt' in name or 'podzol' in name else ('#','#a1a7a8'))
                a=left+x*34;b=top+z*34;d.rectangle((a,b,a+33,b+33),fill=color,outline='#798187');d.text((a+12,b+11),label,fill='black')
    d.text((15,605),'C=red candle, lit=true/candles=1; X=trapped chest; T=TNT; s=soul sand; g=grass; d=dirt variants; #=other original block; .=explicit air.',fill='black')
    d.text((15,630),'Full-cell symbols only. No entity mesh, collision, redstone execution, terrain generation, continuous route or religious/burial function is verified.',fill='black')
    im.save(OUT/'F02-original-layers.png')
if __name__=='__main__':main()
