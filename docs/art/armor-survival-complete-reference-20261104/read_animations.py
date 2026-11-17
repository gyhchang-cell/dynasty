"""Read exact metadata and frame slots for the one animated source icon; analysis only."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent
def main():
 rows=json.loads((D/'animation-candidates.json').read_text());assert len(rows)==1
 a=rows[0];meta=json.loads((D/a['metadata']['local']).read_text())['animation'];im=Image.open(D/a['source']['local']).convert('RGBA')
 assert a['case_key']=='sons_of_sins:remnant' and im.size==(16,48)
 assert meta=={'frametime':16,'interpolate':True,'frames':[0,1,2]}
 out=Image.new('RGB',(720,190),(68,73,78));dr=ImageDraw.Draw(out);font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',13)
 dr.text((8,10),'SOURCE ICON THREE FRAMES / 16 ticks, interpolate / ONE design / NOT GAME',font=font,fill='white');frames=[]
 for i in range(3):
  fr=im.crop((0,i*16,16,(i+1)*16));out.paste(fr.resize((96,96),Image.Resampling.NEAREST),(30+i*225,50),fr.resize((96,96),Image.Resampling.NEAREST));dr.text((30+i*225,155),f'frame {i}',font=font,fill='white');frames.append({'index':i,'rgba_sha256':hashlib.sha256(fr.tobytes()).hexdigest()})
 out.save(D/'animation-frames.png')
 data={'source':a,'metadata':meta,'source_frame_slots':3,'frames':frames,'design_credit_from_frames':0,'source_pixels_modified':False,'chart':'animation-frames.png'}
 (D/'animation-source.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('Three source frames / one animated icon / no extra design credit')
if __name__=='__main__':main()
