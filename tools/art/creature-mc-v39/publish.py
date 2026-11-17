from pathlib import Path
import json,shutil,sys
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];D=R/'docs/art/creature-mc-v39';S=Path('/Users/a15356015027/Desktop/dynasty')
sys.path.insert(0,str(R/'tools/art/cod2-voxel'));from guardian_surfaces import IDS
names=['巨臂石敢当','铜臂飞天夜叉','煞水浮溺鬼'];runs=['guardians-final','guardians-final','silt']
notes=['参考暮色巨魔的大躯干/面部主次与Alex Rocky Roller的岩层分区。收薄重复包边、加强腰体连接；连续石层、拳面磨损、顶面苔色与旧金铭文分开。','参考Alex白头海雕薄翼和长向羽纹，仅借鉴翼面组织，不改成鹰。收薄翼骨与羽面、铜臂节边；铜臂保留大体量，暗色身体、浅角爪与观察中心形成主次。','参考Alex Guster在分段躯体上组织连续运动纹样的方法。保留原有水鬼与泥潭结构，连贯青绿流纹、暗色湿发、浅眼和底部沉积物分区，减少衣服镶边感。']
overview=Image.new('RGB',(1440,400),(238,235,225));dr=ImageDraw.Draw(overview)
for i,(n,run) in enumerate(zip(IDS,runs)):
 d=D/n;im=Image.open(d/'45.png');im.thumbnail((480,360));overview.paste(im,(480*i,30));dr.text((480*i+10,10),n,fill='black')
 src=R/'docs/art/cod2-voxel-v1/native'/('creature-v39-'+run);native=''
 if (src/'PASS.txt').exists():
  out=d/'native';out.mkdir(exist_ok=True)
  for p in src.iterdir():
   if (p.suffix=='.png' and n in p.name) or p.name in ['PASS.txt','samples.json','client.log']:shutil.copy2(p,out/p.name)
  native='<h2>真实客户端检查</h2><p>静音隔离存档；守卫批次检查正侧背、移动、攻击接触、特殊动作、受伤、倒地与重载。水鬼批次同样检查上述动作和重载。不是自然副本或多人战斗验收。</p>'+''.join(f'<p>{p.stem}</p><img src="native/{p.name}">' for p in sorted(out.glob('*.png')))
 html='<meta charset="utf-8"><style>body{background:#eeebe1;color:#292820;font:18px sans-serif;margin:28px;line-height:1.6}img{max-width:100%;image-rendering:pixelated}section{margin:28px 0}</style><a href="../index.html">返回</a><h1>'+names[i]+'</h1><p>'+notes[i]+'</p><p>左旧右新：共同取景范围、相同机位；逐面采样真实PNG的软件图。</p>'
 html+=''.join(f'<section><h2>{a}°对照</h2><img src="compare-{a}.png"></section>' for a in [0,45,90,180])+native
 html+='<h2>完整软件动作回放</h2>'+''.join(f'<h3>{p.stem}</h3><img src="{p.name}">' for p in sorted(d.glob('*.webp')))
 html+='<h2>实际PNG与UV</h2><a href="texture.png">原始PNG</a><img src="texture-3x.png"><img src="uv.png">';(d/'index.html').write_text(html)
overview.save(D/'overview.png');shutil.copy2(S/'build/creature-v39/references.png',D/'references.png')
shutil.copy2(R/'docs/art/cod2-voxel-v1/creature-v39-validation.json',D/'validation.json')
(D/'index.html').write_text('<meta charset="utf-8"><style>body{background:#eeebe1;font:20px sans-serif;margin:30px;line-height:1.6}img{max-width:100%}li{margin:20px}</style><h1>继续三只：石体、铜翼与泥水灵体</h1><p>此前认可的V37八只、V38三只和上传精英保持不变。保留本批注册、骨架、动作时间轴与玩法。</p><img src="overview.png"><ul>'+''.join(f'<li><a href="{n}/index.html">{name}</a>：{note}</li>' for n,name,note in zip(IDS,names,notes))+'</ul><h2>本次实际查看的参考</h2><p>源模型灰模与原始PNG配对查看，不是参考模组的游戏截图。仅学习形体与纹样组织，没有复用外部像素。累计研究未达到1000只。</p><img src="references.png"><p><a href="https://github.com/AlexModGuy/AlexsMobs">Alex’s Mobs官方源码</a> · <a href="https://github.com/TeamTwilight/twilightforest">暮色森林官方资源源码</a></p><p>检查：21条动画软件回放、UV边界/重叠、骨架兼容、每0.25tick离地边界、制作源可重复导出。</p>')
print('Published 3 creatures')
