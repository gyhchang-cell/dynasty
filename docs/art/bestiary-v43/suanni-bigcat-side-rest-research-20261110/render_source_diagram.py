"""Rasterize this batch's gray geometry plot; no texture or user image editing."""
from PIL import Image,ImageDraw
import xml.etree.ElementTree as ET
from pathlib import Path
b=Path(__file__).resolve().parent
im=Image.new('RGB',(1200,620),'#f1f1ed');d=ImageDraw.Draw(im)
for e in ET.parse(b/'bigcat-side-rest.svg').getroot():
 tag=e.tag.rsplit('}',1)[-1];a=e.attrib
 if tag=='polygon':
  pts=[tuple(map(float,p.split(','))) for p in a['points'].split()];d.polygon(pts,fill=a['fill']);d.line(pts+[pts[0]],fill=a['stroke'],width=1)
 elif tag=='line':d.line([float(a[k]) for k in ['x1','y1','x2','y2']],fill=a['stroke'])
 elif tag=='text':d.text((float(a['x']),float(a['y'])-14),e.text,fill='#222222')
im.save(b/'bigcat-side-rest.png')
