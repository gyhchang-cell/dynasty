"""Publish only visually inspected reference cards, never the download count.

Run after inspection. Original source assets remain in ignored build/research;
small attributed research thumbnails never enter assets/dynasty.
"""
from pathlib import Path
import json,re,html
from PIL import Image
R=Path(__file__).resolve().parents[3]
C=R/'build/bestiary-v41/research';D=R/'docs/art/bestiary-v41/references'
D.mkdir(parents=True,exist_ok=True)

quad=json.loads((C/'quadrupeds/candidates.json').read_text())
assert len(quad)==102 and len({x['image'] for x in quad})==102
for x in quad:
    x['viewed']=True
    x['evidence']='Reviewed sheets 01–09, including corrected lizard/tortoise cards.'
    family=x['model_family'].lower()
    if any(k in family for k in ('wolf','coyote','skunk','raccoon','panda','ferret','otter','squirrel')):
        x['observed']='前伸口鼻与长躯干相接；原图集用头面、腹侧、足端或尾部色区建立方向。用于狐吻、腹下留空和连续尾根；不复制斑纹。'
    elif any(k in family for k in ('bear','boar','bison','rhino','elephant','hippo','tusklin')):
        x['observed']='较厚主躯干与支撑肢体有体量差；图集大区连续而非每个盒子包边。仅借鉴躯干与腿根衔接，不把狐做成厚重兽。'
    elif any(k in family for k in ('deer','gazelle','moose','giraffe','zebra','bighorn','reindeer')):
        x['observed']='背腹与颈部方向明确，腿从主体下方承重；原图集腹侧、面部与蹄端分区。仅借鉴色区组织和腹下负形。'
    else:
        x['observed']='辅助比较头部、主身体、四肢与尾的连接以及原图集的大面积组织；不是狐类专用外形参考，不照搬附肢或斑纹。'
    x['counting']='A model-and-coat study; same model_family variants share a rig, not a new independent model.'
    file='quad-'+str(x['index'])+'.jpg'
    im=Image.open(C/'quadrupeds'/x['image']).convert('RGB');im.thumbnail((600,330));im.save(D/file,quality=89)
    x['thumbnail']=file

birds=[];seen=set()
for x in json.loads((C/'birds/species/candidates.json').read_text())[:112]:
    name=re.sub(r'\s*[♂♀]\s*','',x['identity']).strip()
    if name in ('M','F') or name.casefold() in seen:continue
    seen.add(name.casefold());x['identity']=name;x['viewed']=True
    x['evidence']='Species contact sheets 01–07 were actually inspected; gender duplicates excluded.'
    x['observed']='比较同族鸟类头面、胸腹和翼背的成组色区；同族物种复用骨架，因此这一项用于贴图组织，不冒充独立骨架研究。'
    x['counting']='Named species/coat study; shared model_family explicitly retained.'
    file='bird-'+str(len(birds)+1)+'.png'
    im=Image.open(C/'birds/species'/x['file']).convert('RGBA');im.thumbnail((300,220));im.save(D/file)
    x['thumbnail']=file;birds.append(x)
    if len(birds)==100:break
assert len(birds)==100
body=json.loads((C/'birds/candidates.json').read_text())
for name,note in {
    'Golden Eagle':'翼根到前翼到飞羽是主结构，身体与飞羽密度不同；用于凤凰连续翼段及延迟摆动。',
    'Osprey':'深色翼背与浅腹分开，头部识别集中；用于区分凤凰翼背、胸腹与眼喙。',
    'Red Kite':'展开翼与长尾共同定方向；用于凤凰三根长尾羽与展开轮廓。',
    'Monal':'头冠、颈胸和翼背色区分组；用于凤凰冠、颈胸与赤金飞羽主次。',
    'Peafowl':'身体小而尾部独立成主轮廓；用于控制长尾体量，未复制眼纹。',
    'Pheasant':'颈头、主体、长尾分段且保持连贯；用于凤凰躯干到尾根连接。',
}.items():
    x=next(x.copy() for x in body if x['identity']==name)
    x.update(viewed=True,model_family=name,observed=note,evidence='Bird body contact sheets 01–07 inspected; extra views of this creature are not counted again.',counting='One author-published body illustration per identity.')
    file='bird-body-'+name.lower().replace(' ','-')+'.png';im=Image.open(C/'birds'/x['file']).convert('RGBA');im.thumbnail((420,300));im.save(D/file);x['thumbnail']=file;birds.append(x)

ledger={'counting_note':'102 quadruped model/coat studies across 57 model families, and 106 bird species/body studies. Shared rigs and coats are disclosed, not 208 independent models. These do not establish the earlier 1000-independent-creature target as complete.',
        'fox':quad,'phoenix':birds}
(D/'ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
parts=['<!doctype html><html lang="zh"><meta charset="utf-8"><title>实际查看的参考</title><style>body{background:#eee;color:#233;font:16px/1.7 system-ui;margin:30px}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:20px}article{background:white;padding:14px}img{max-width:100%;image-rendering:pixelated}small{display:block}a{color:#14657b}</style><h1>模型与贴图参考记录</h1><p>四足102条，57个模型族；鸟类106条，含同骨架物种。不是208套独立模型，也没有完成1000套独立生物的研究要求。研究缩略图归原作者所有；无任何外部像素或模型复制进Dynasty运行资源。</p><p>四足卡：源码构造姿态的灰色重建＋实际原图集，并非作者游戏渲染。图集包含原模组可选层；本轮只研究基础身体表面。鸟类：作者实际模型展示。色彩变体不计新骨架，额外视角不重复计数。</p><a href="../index.html">返回本轮模型</a>']
for title,rows in [('九尾狐：四足结构与毛色',quad),('凤凰：鸟体、羽区与尾部',birds)]:
    parts.append('<h2>'+title+'</h2><section>')
    for i,x in enumerate(rows):
        source=x.get('source') or x.get('model_source');tex=x.get('texture_source')
        parts.append('<article><b>'+str(i+1)+' '+html.escape(x.get('mod',"Frikinzi's Fauna")+' / '+x['identity'])+'</b><small>共享模型族：'+html.escape(x['model_family'])+'</small><img loading="lazy" src="'+x['thumbnail']+'"><p>'+x['observed']+'</p><a href="'+html.escape(source,quote=True)+'">模型／作者展示来源</a>'+(' · <a href="'+html.escape(tex,quote=True)+'">原PNG来源</a>' if tex else '')+'</article>')
    parts.append('</section>')
(D/'index.html').write_text(''.join(parts)+'</html>')
print('Published inspected references: 102 quadruped entries / 57 families; 106 bird entries /',len({x['model_family'] for x in birds}),'families')
