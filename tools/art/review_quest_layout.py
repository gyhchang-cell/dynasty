"""Static coordinate review of exported quests, not native FTB acceptance.

FTB QuestPanel renders straight center-to-center dependency lines. Review their
geometry against unrelated buttons before trying the real client. Icons here
are local texture thumbnails; block/vanilla fallback symbols are not game renders.
"""
import argparse
import json
import math
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]


from quest_layout_geometry import visible_edges, penetrates, crossings, audit


def plain(text):
    return re.sub(r'&[0-9a-fk-or]', '', text)


def icon_texture(q):
    match = re.search(r'id:\s*"([^\"]+)"', q['icon'])
    if not match:
        return None
    namespace, name = match[1].split(':',1)
    model = ROOT/'src/main/resources/assets'/namespace/'models/item'/f'{name}.json'
    if model.is_file():
        info = json.loads(model.read_text())
        texture = info.get('textures', {}).get('layer0')
        if texture and ':' in texture:
            ns, path = texture.split(':', 1)
            candidate = ROOT/'src/main/resources/assets'/ns/'textures'/f'{path}.png'
            if candidate.is_file():
                return candidate
    candidate = ROOT/'src/main/resources/assets'/namespace/'textures/item'/f'{name}.png'
    return candidate if candidate.is_file() else None


def render(chapter, output, section=None):
    nodes = [q for q in chapter['quests'] if section is None or q.get('section') == section]
    selected = {q['id'] for q in nodes}
    labels=[im for im in chapter.get('images',[]) if section is None or im.get('click','').lstrip('#') in selected]
    bounds = [min([q[a]-1.3 for q in nodes]+[im[a]-im[dim]/2 for im in labels]) for a,dim in (('x','width'),('y','height'))]
    upper = [max([q[a]+1.3 for q in nodes]+[im[a]+im[dim]/2 for im in labels]) for a,dim in (('x','width'),('y','height'))]
    scale = 70
    width, height = [math.ceil((upper[i]-bounds[i])*scale)+40 for i in (0,1)]
    image = Image.new('RGB',(width,height+65),'#142628')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',13)
    titlefont = ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',20)
    def point(q):
        return ((q['x']-bounds[0])*scale+20,(q['y']-bounds[1])*scale+65)
    draw.text((20,16),'静态坐标审查 · '+plain(chapter['title'])+' · 非游戏截图',font=titlefont,fill='#e5d1a0')
    for label in labels:
        p=ROOT/'src/main/resources/assets'/label['image'].replace(':','/',1)
        if p.is_file():
            x,y=point(label);w=round(label['width']*scale);h=round(label['height']*scale)
            with Image.open(p) as source:thumbnail=source.convert('RGB').resize((w,h))
            image.paste(thumbnail,(round(x-w/2),round(y-h/2)))
    for a,b in visible_edges(chapter):
        if a['id'] not in selected or b['id'] not in selected:
            continue
        start,end = point(a),point(b)
        draw.line((start,end),fill='#799b94',width=3)
        theta = math.atan2(end[1]-start[1],end[0]-start[0])
        x,y = end[0]-math.cos(theta)*38,end[1]-math.sin(theta)*38
        draw.polygon([(x,y),(x-10*math.cos(theta-.5),y-10*math.sin(theta-.5)),
                     (x-10*math.cos(theta+.5),y-10*math.sin(theta+.5))],fill='#bdd5c5')
    for q in nodes:
        x,y=point(q);half=q.get('size',1.)*23
        box=(x-half,y-half,x+half,y+half)
        color='#ad8f54' if q.get('section_header') else '#598877' if q.get('for_quest') else '#96747b'
        if q.get('shape') == 'circle':
            draw.ellipse(box,fill='#263b3c',outline=color,width=2)
        elif q.get('shape') == 'diamond':
            draw.polygon([(x,y-half),(x+half,y),(x,y+half),(x-half,y)],fill='#263b3c',outline=color,width=2)
        else:
            draw.rectangle(box,fill='#263b3c',outline=color,width=2)
        texture=icon_texture(q)
        if texture:
            with Image.open(texture) as source:
                thumb=source.convert('RGBA');thumb.thumbnail((32,32),Image.Resampling.NEAREST)
            image.paste(thumb,(round(x-thumb.width/2),round(y-thumb.height/2)),thumb)
        else:
            draw.text((x-7,y-7),'读' if q['kind']=='checkmark' else '物',font=font,fill='#e8ede2')
        title=plain(q.get('display_title',q['title']))
        lines=[title[i:i+8] for i in range(0,min(len(title),24),8)]
        for i,line in enumerate(lines):
            draw.text((x-draw.textlength(line,font=font)/2,y+half+4+i*16),line,font=font,fill='#e8ede2')
        if q.get('hide_dependency_lines'):
            draw.text((x+half-4,y-half-4),'↗',font=font,fill='#e5d1a0')
    output.parent.mkdir(parents=True,exist_ok=True)
    image.save(output)
    return str(output)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--book',type=Path,default=ROOT/'docs/quests-remaster/book.json')
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();book=json.loads(args.book.read_text())
    args.out.mkdir(parents=True,exist_ok=True)
    report={'scope':'Static exported geometry; not native rendering/hover validation',
            'chapters':[audit(c) for c in book]}
    (args.out/'geometry.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    for chapter,section in [('dynasty_c1',None),('dynasty_c1','dynasty_cod4_workshop'),
                            ('dynasty_c10',None),('dynasty_c10','dynasty_accessory_charm')]:
        c=next(c for c in book if c['file']==chapter)
        render(c,args.out/f'{section or chapter}.png',section)
    print(json.dumps({c['chapter']:{'visible_edges':c['visible_edges'],
          'button_penetrations':len(c['button_penetrations']),'edge_crossings':len(c['edge_crossings'])}
          for c in report['chapters']},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
