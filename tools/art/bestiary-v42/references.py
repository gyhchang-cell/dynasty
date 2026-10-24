"""Pinned author material studies. External files stay in ignored build cache.

The 100 Steve appearances are reused studies, NOT 100 new independent models.
The ghost studies are counted separately and never padded with costume variants.
"""
from pathlib import Path
import json, sys, importlib.util, concurrent.futures, urllib.request, hashlib, html
from PIL import Image, ImageDraw, ImageFont
from build_models import ROOT, OUT

CACHE=ROOT/'build/bestiary-v42/references';CACHE.mkdir(exist_ok=True)
FONT='/System/Library/Fonts/STHeiti Medium.ttc'
def font(n):return ImageFont.truetype(FONT,n)
def fetch(row):
    p=CACHE/(row['sha256']+'.png')
    if not p.exists():p.write_bytes(urllib.request.urlopen(row['url'],timeout=35).read())
    im=Image.open(p).convert('RGBA')
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    return row,p,im

def main():
    source=json.loads((ROOT/'docs/art/royal-detail-v24/reference-100.json').read_text())
    rows=list(concurrent.futures.ThreadPoolExecutor(10).map(fetch,source['items']))
    for page in range(5):
        sheet=Image.new('RGB',(1400,1040),'#e9ebe4');d=ImageDraw.Draw(sheet)
        d.text((15,8),f'Steve外观研究 {page+1}/5 · 原始PNG/服装层，不称100套独立骨架',font=font(21),fill='#283936')
        for j,(row,p,im) in enumerate(rows[page*20:page*20+20]):
            x=(j%5)*280;y=45+(j//5)*245
            factor=max(1,min(200//im.width,190//im.height));pic=im.resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST)
            sheet.paste(pic,(x+8,y+4),pic)
            d.text((x+8,y+198),f'{row["number"]:03} {row["project"]}',font=font(15),fill='#283936')
            d.text((x+8,y+220),row['label'][-28:],font=font(12),fill='#283936')
        sheet.save(CACHE/f'human-{page+1}.png')
    # Concrete author anatomy + its real atlas, not a recoloured reference model.
    spec=importlib.util.spec_from_file_location('reference_geometry',ROOT/'tools/art/steve-fighters-v25/nonhuman_references.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    library=ROOT/'build/creature-reference-1000'
    studies=[]
    for repo,model,tex,note in [
      ('TeamTwilight__twilightforest','WraithModel','wraith.png','浅面与暗袍分离；前伸双臂和衣料整体组织。'),
      ('TeamTwilight__twilightforest','KnightPhantomModel','phantomskeleton.png','主躯与细连接分级；不将所有部件等量加粗。'),
      ('Polarice3__Goety-2','WraithModel','wraith/wraith.png','兜帽暗内层、浅骨面、袖口骨手与拖布的分层。')]:
        base=library/repo;meta=json.loads((base/'source.json').read_text())
        src=next(base.rglob(model+'.java'));texture=next(p for p in base.rglob(Path(tex).name) if '/textures/entity/' in str(p) and str(p).endswith('/'+tex))
        text=src.read_text();parts,warnings=g.parse_tf(text)
        # Twilight inherits the canonical mesh; reconstruct those inherited boxes explicitly.
        if 'HumanoidModel.createMesh' in text:
            for n,o,s,p in [('head',[-4,-8,-4],[8,8,8],[0,0,0]),('body',[-4,0,-2],[8,12,4],[0,0,0]),('right_leg',[-2,0,-2],[4,12,4],[-1.9,12,0]),('left_leg',[-2,0,-2],[4,12,4],[1.9,12,0])]:
                if n not in parts:parts[n]=dict(parent='root',pos=p,rot=[0,0,0],boxes=[dict(origin=o,size=s)])
        faces,points=g.geometry(parts);gray=g.render(faces,points,35,size=(400,390));atlas=Image.open(texture).convert('RGBA')
        factor=max(1,min(380//atlas.width,380//atlas.height));atlas=atlas.resize((atlas.width*factor,atlas.height*factor),Image.Resampling.NEAREST)
        card=Image.new('RGB',(900,510),'#e9ebe4');card.paste(gray,(0,45));card.paste(atlas,(450,45),atlas);d=ImageDraw.Draw(card)
        d.text((15,8),repo.split('__')[0]+' / '+model,font=font(22),fill='#283936')
        d.text((15,442),'源码灰模复原（非游戏截图） + 作者原始图集',font=font(18),fill='#283936');d.text((15,475),note,font=font(17),fill='#283936')
        file=f'{repo}-{model}.png';card.save(CACHE/file)
        studies.append(dict(repo=meta['repo'],commit=meta['sha'],model_url=f'https://github.com/{meta["repo"]}/blob/{meta["sha"]}/{src.relative_to(base)}',texture_url=f'https://github.com/{meta["repo"]}/blob/{meta["sha"]}/{texture.relative_to(base)}',study=file,observation=note,limitations='Literal bind-pose reconstruction, no native author animation/equipment rendering; not a full game screenshot',parser_warnings=warnings))
    ledger=dict(human_studies=source['items'],human_scope=source['scope'],human_reused_from='royal-detail-v24',specific_ghost_studies=studies,applied={
      'jade_guard':'Steve六主体块；半覆面眼带与玉色札甲，压低下肢对比；HumanCompanions人物服装的脸/衣/装备分区。',
      'thunder_envoy':'保留Steve基础，区别于面罩守卫的完整脸、短须与头巾；Wizardry人物的领口/袖口/服装主次，不复制帽袍。',
      'merfolk':'仍为Steve基础的鲛人；鱼肤腹面、侧鳃与贴背鳍形成海族识别，保持陆行能力。',
      'soul_soldier':'暮色/Goety Wraith的浅脸暗袍和袖口骨手关系；原创真空腔与错长拖布，无正常腿。'},
      limitations=['100份人形外观复查，包含共享骨架的皮肤及MCA服装图层，不能称100套独立建模。','本轮具体亡灵结构仅3例，未完成每只100个相似独立模型的研究要求。','外部原图与源码仅研究，未进入运行资源或JAR。'])
    (OUT/'references.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
    print('Prepared 5 x20 raw human appearance sheets and 3 specific ghost anatomy+atlas cards; not yet marked visually inspected')

if __name__=='__main__':main()
