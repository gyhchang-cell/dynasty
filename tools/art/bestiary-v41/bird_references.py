from pathlib import Path
import urllib.request,urllib.parse,json,re,hashlib,concurrent.futures
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];D=R/'build/bestiary-v41/research/birds';D.mkdir(parents=True,exist_ok=True)
names='African Pygmy Falcon|Barn Owl|Eagle Owl|Golden Eagle|Gyrfalcon|Osprey|Red Kite|Secretarybird|Steller’s Sea Eagle|Conure|Kakapo|Lorikeet|Lovebird|Bunting|Bushtit|Chickadee|Cock of the Rock|Fairywren|Finch|Magpie|Laughingthrush|Raven|Robin|Sparrow|Starling|Swallow|Tanager|Booby|Crane|Cormorant|Goose|Peafowl|Ibis|Mandarin Duck|Pelican|Pygmy Goose|Seagull|Skua|Spoonbill|Whistling Duck|Wild Duck|Wood Duck|Capercaillie|Dove|Monal|Pheasant|Avocet|Ground Hornbill|Frigate|Kingfisher|Lapwing|Marabou Stork|Penguin|Puffin|Rail|Roller Bird|Shoebill|Stilt|Stork'.split('|')
def get(url):return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Dynasty-art-reference/1.0'}),timeout=30).read()
def page(name):
 slug=name.replace(' ','-').replace('’',"'");url='https://raw.githubusercontent.com/wiki/frikinzi/frikinzis_fauna/'+urllib.parse.quote(slug)+'.md'
 try:
  p=D/(slug+'.md')
  if not p.exists():p.write_bytes(get(url))
  txt=p.read_text();rows=[]
  # Exclude hearts, item icons and banners; only author body illustrations with >=150 display width or markdown images.
  links=re.findall(r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>',txt)
  for link in dict.fromkeys(links):
   if not ('imgur.com' in link or 'postimg.cc' in link):continue
   tag=next((t for t in re.findall(r'<img[^>]*>',txt) if link in t),'');w=re.search(r'width\s*=\s*["\']?(\d+)',tag)
   if w and int(w[1])<150:continue
   f='image-'+hashlib.sha256(link.encode()).hexdigest()[:18]+'.img';p=D/f
   try:
    if not p.exists():p.write_bytes(get(link))
    im=Image.open(p)
    if min(im.size)<60:continue
    rows.append({'identity':name,'mod':'Frikinzis Fauna','source':'https://github.com/frikinzi/frikinzis_fauna/wiki/'+urllib.parse.quote(slug),'url':link,'file':f,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':list(im.size),'viewed':False})
   except Exception:pass
  return rows
 except Exception:return []
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
 for result in ex.map(page,names):rows+=result
seen=set();rows=[r for r in rows if r['sha256'] not in seen and not seen.add(r['sha256'])]
for i,r in enumerate(rows):r['index']=i+1
(D/'candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
for start in range(0,len(rows),12):
 sheet=Image.new('RGB',(1800,1250),'#ecece4');dr=ImageDraw.Draw(sheet)
 for j,r in enumerate(rows[start:start+12]):
  im=Image.open(D/r['file']).convert('RGBA');im.thumbnail((580,264));x=j%3*600;y=j//3*310;sheet.paste(im,(x+(580-im.width)//2,y),im);dr.text((x+8,y+267),str(r['index'])+' '+r['identity'],fill='black')
 sheet.save(D/f'sheet-{start//12+1:02}.jpg',quality=90)
print('Bird model-texture illustrations',len(rows),'named identities',len({r['identity'] for r in rows}),flush=True)
