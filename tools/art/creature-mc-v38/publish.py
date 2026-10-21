from pathlib import Path
import json,shutil,sys
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];D=R/'docs/art/creature-mc-v38';S=Path('/Users/a15356015027/Desktop/dynasty')
sys.path.insert(0,str(R/'tools/art/cod2-voxel'));from woodland_surfaces import IDS
names=['巨力赑屃傀儡','枯木树精','牧血飞颅'];runs=['bixi','tree','skull']
notes=['参考Alex鳄龟主壳、腹甲与足根关系：收薄重复盖板、连接颈根，壳面连续分区，石碑、古金甲缘与暗色活塞分开。','参考暮色傀儡外壳与连接件的材质层级，保留原有枯树和根系形态：连贯纵向树皮、枝条横向木纹、浅色断面与根部苔色，薄菌盖不再像金属箍。','参考暮色巫妖眼窝、颌部与骨色主次：收薄眼窝凸块及盔边，骨面、盔甲、颈部残躯分开；垂挂组织变细并保持原有摆动。']
overview=Image.new('RGB',(1440,400),(238,235,225));dr=ImageDraw.Draw(overview)
for i,(n,run) in enumerate(zip(IDS,runs)):
 d=D/n;im=Image.open(d/'45.png');im.thumbnail((480,360));overview.paste(im,(480*i,30));dr.text((480*i+10,10),n,fill='black')
 src=R/'docs/art/cod2-voxel-v1/native'/('creature-v38-'+run)
 native=''
 if (src/'PASS.txt').exists():
  out=d/'native';out.mkdir(exist_ok=True)
  for p in src.iterdir():
   if p.suffix=='.png' or p.name in ['PASS.txt','samples.json','client.log']:shutil.copy2(p,out/p.name)
  native='<h2>真实客户端检查</h2><p>静音隔离存档：正面、45°与资源重载。完整动作在下方软件回放，未将此次少量实机帧称为完整战斗验收。</p>'+''.join(f'<img src="native/{p.name}">' for p in sorted(out.glob('*.png')))
 html='<meta charset="utf-8"><style>body{background:#eeebe1;color:#292820;font:18px sans-serif;margin:28px;line-height:1.6}img{max-width:100%;image-rendering:pixelated}section{margin:28px 0}</style><a href="../index.html">返回</a><h1>'+names[i]+'</h1><p>'+notes[i]+'</p><p>左旧右新：共同取景范围、相同机位；逐面采样真实PNG的软件图。</p>'
 html+=''.join(f'<section><h2>{a}°对照</h2><img src="compare-{a}.png"></section>' for a in [0,45,90,180])+native
 html+='<h2>完整软件动作回放</h2>'+''.join(f'<h3>{p.stem}</h3><img src="{p.name}">' for p in sorted(d.glob('*.webp')))
 html+='<h2>实际PNG与UV</h2><a href="texture.png">原始PNG</a><img src="texture-3x.png"><img src="uv.png">';(d/'index.html').write_text(html)
overview.save(D/'overview.png');shutil.copy2(S/'build/creature-v38/references.png',D/'references.png')
shutil.copy2(R/'docs/art/cod2-voxel-v1/creature-v38-validation.json',D/'validation.json')
(D/'index.html').write_text('<meta charset="utf-8"><style>body{background:#eeebe1;font:20px sans-serif;margin:30px;line-height:1.6}img{max-width:100%}li{margin:20px}</style><h1>下一批三只：模型与贴图</h1><p>上一批八只和已上传精英保持不变。本批保留注册、骨架、动作时间轴与玩法。</p><img src="overview.png"><ul>'+''.join(f'<li><a href="{n}/index.html">{name}</a>：{note}</li>' for n,name,note in zip(IDS,names,notes))+'</ul><h2>本次实际查看的参考</h2><p>源模型灰模与原始PNG配对查看，不是参考模组的游戏截图。仅学习组织方式，没有复用外部像素。研究累计未达到1000只。</p><img src="references.png"><p><a href="https://github.com/AlexModGuy/AlexsMobs/blob/09755dade2cfbdf14839e026d3af446f9d3ff843/src/main/java/com/github/alexthe666/alexsmobs/client/model/ModelAlligatorSnappingTurtle.java">Alex鳄龟模型源码</a> · <a href="https://github.com/TeamTwilight/twilightforest">暮色森林官方资源源码</a></p><p>检查：三只23条动画软件回放、UV边界/重叠、骨架兼容、每0.25tick离地边界、生成源可复现。实机检查仅覆盖正面/45°和重载，完整自然战斗待验证。</p>')
print('Published 3 creatures')
