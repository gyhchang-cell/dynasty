from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent
RES=D/'source/Xplat/src/main/resources/assets/botania'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 pages=[]
 for m in ['manasteel','elementium','terrasteel','manaweave']:
  out=Image.new('RGB',(1080,660),(75,80,85));dr=ImageDraw.Draw(out);dr.text((12,12),'REFERENCE ORIGINAL PNG / NOT DYNASTY ART / NOT GAME / Botania:'+m,fill='white');rows=[]
  for i,s in enumerate(['helmet','chestplate','leggings','boots']):
   p=RES/f'textures/item/{m}_{s}.png';im=Image.open(p).convert('RGBA');rows.append({'path':str(p.relative_to(D)),'sha256':sha(p),'size':list(im.size),'role':'item_icon'});im=im.resize((im.width*10,im.height*10),Image.Resampling.NEAREST);out.paste(im,(15+i*175,55),im);dr.text((15+i*175,225),s,fill='white')
  p=RES/f'textures/model/armor_{m}.png';im=Image.open(p).convert('RGBA');rows.append({'path':str(p.relative_to(D)),'sha256':sha(p),'size':list(im.size),'role':'custom_worn_atlas'});scale=min(4,570//im.height);im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST);out.paste(im,(760,55),im);dr.text((760,630),'NATIVE CUSTOM UV ATLAS',fill='white');name=f'{m}-native-source-page.png';out.save(D/name);pages.append({'case_key':'botania:'+m,'path':name,'sha256':sha(D/name),'sources':rows,'runtime_acceptance':False})
 (D/'source-pages.json').write_text(json.dumps({'pages':pages,'method':'Original RGBA PNG research pages; nearest integer display enlargement only; source bytes unchanged','new_artwork':0,'game_starts':0},ensure_ascii=False,indent=2)+'\n');print('Four source pages,16icons and4custom worn atlases.')
if __name__=='__main__':main()
