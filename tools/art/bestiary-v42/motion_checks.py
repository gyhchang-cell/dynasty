"""Readable filmstrips from the exported actual-native animation movies."""
from PIL import Image,ImageDraw,ImageFont
from build_models import IDS,TITLES,OUT

def main():
 font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',18)
 for id,title in zip(IDS,TITLES):
  clips=['idle','walk'] if id=='minister' else ['walk','attack']
  sheet=Image.new('RGB',(1550,1210),'#e8eae2');d=ImageDraw.Draw(sheet)
  for row,clip in enumerate(clips):
   d.text((10,row*605+5),title+' / '+clip+' · 原生动画连续帧，离线',font=font,fill='#283936')
   with Image.open(OUT/id/(clip+'.gif')) as movie:
    for i in range(10):
     index=i*4 if clip=='idle' else i
     movie.seek(index);frame=movie.convert('RGB').resize((310,282),Image.Resampling.NEAREST)
     sheet.paste(frame,((i%5)*310,row*605+35+(i//5)*282))
  sheet.save(OUT/id/'motion-strip.png')
 print('Six continuous-phase motion sheets written from native movies')
if __name__=='__main__':main()
