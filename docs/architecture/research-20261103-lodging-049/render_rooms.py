"""Original main-floor and guestroom layers; no fabricated room connections."""
import json
from pathlib import Path
import sys
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parents[2]/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR,plans,iso
from PIL import Image,ImageDraw
def main():
    c=json.loads((OUT/'sources.json').read_text())['candidates'][0]
    with ZipFile(c['source_archive']) as z:n=read(z.read(c['member']))
    cells={tuple(b['pos']):n['palette'][b['state']]['Name'] for b in n['blocks'] if n['palette'][b['state']]['Name'] not in AIR}
    for y in (4,10):plans(cells,n['size'],y,'F01 original inn').save(OUT/f'F01-y{y}.png')
    sheet=Image.new('RGB',(1520,720),'#edf0f2')
    for direction in range(2):sheet.paste(iso(cells,n['size'],direction,'F01 main-floor cutaway y<=6',6),(direction*760,0))
    ImageDraw.Draw(sheet).text((15,695),'Original stored blocks only; classification colours/full cells. Not native textures, furniture meshes, generated terrain or collision acceptance.',fill='#17252c')
    sheet.save(OUT/'F01-hall-cutaway.png')
if __name__=='__main__':main()
