from pathlib import Path
import sys,json,shutil,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];D=R/'docs/art/creature-mc-v37';sys.path.insert(0,str(R/'tools/art/cod2-voxel'));from creature_surfaces import IDS
LANG=json.loads((R/'src/main/resources/assets/dynasty/lang/zh_cn.json').read_text())
notes={
'baimu_mowu':'收薄腹侧板、足端和口钳，背眼重新贴合甲壳；背甲与腹面分区，足根用角质色。参考甲虫的主体/足根主次与Alex洞穴蜈蚣甲节。',
'bishui_xuanjiao_youzi':'延长相邻躯段的重叠，收薄鳍根和尖牙；青鳞、浅腹与角须分开。参考Alex响尾蛇的躯干递减与背腹连续纹样。',
'qingtong_shuangtoushekui':'减少每节厚金边与突起，保留双首机关；青铜壳、暗连接和喷口分明，金色不再盖住脸。借鉴蛇类连续躯段，不把机关改成活蛇。',
'xunshan_mujiaquan':'减薄肩臀盖板与脚掌，保留发条和机械关节；沿木构件长轴绘纹，铁轴与铜箍分离。参考Alex鬃狼口鼻、躯干与四肢的识别关系。',
'bazu_digongzhu':'减薄足端与外扩盖板，腿的粗细有主次；木腹、铜前躯、铁关节与夹口分材质。参考暮色甲虫大腹/小头/细足结构。',
'mingsha_shixie':'收薄螯尖、足端和重复背甲边，保留尾针；背脊、腹面和夹击内面分层。参考Alex龙虾的螯与细足比例。',
'youdeng_guimianfu':'减薄翼膜与翼骨，收小面部凸起；暗紫翼膜、灰毛、浅面具与绿灯分开。参考Alex蜜袋鼯薄膜和身体大块色区，保留鬼面蝠身份。',
'xueju_mangguyu':'用真实开放肋架替换实心暗块，收薄鳍；骨面、骨缝、残肉与鳍膜分区。参考Alex Skelewag骨架与薄鳍的分离关系。'}
overview=Image.new('RGB',(1440,1200),(238,235,225));draw=ImageDraw.Draw(overview)
validation=json.loads((R/'docs/art/cod2-voxel-v1/creature-v37-validation.json').read_text())
(D/'validation.json').write_text(json.dumps(validation,indent=2))
runs=['creature-v37-beasts','creature-v37-mechanicals','creature-v37-floaters'];native={}
for run in runs:
 src=R/'docs/art/cod2-voxel-v1/native'/run
 if not (src/'PASS.txt').exists():continue
 dest=D/'native-evidence'/run;dest.mkdir(parents=True,exist_ok=True)
 for filename in ['PASS.txt','samples.json','client.log']:
  if (src/filename).exists():shutil.copy2(src/filename,dest/filename)
 for name in IDS:
  shots=sorted(src.glob('*-'+name+'-*.png'))
  if shots:
   native[name]={'run':run,'views':len(shots),'runtimeManifest':str(src/'runtime-manifest.json')}
   out=D/name/'native';out.mkdir(exist_ok=True)
   for shot in shots:shutil.copy2(shot,out/shot.name)
for i,name in enumerate(IDS):
 title=LANG.get('entity.dynasty.'+name,name);d=D/name
 im=Image.open(d/'45.png');im.thumbnail((480,350));overview.paste(im,((i%3)*480,(i//3)*400+35));draw.text(((i%3)*480+10,(i//3)*400+12),name,fill='black')
 html='<meta charset="utf-8"><style>body{background:#eeebe1;color:#262722;font:18px sans-serif;margin:28px}img{max-width:100%;image-rendering:pixelated}section{margin:26px 0}</style><a href="../index.html">返回总览</a><h1>'+title+'</h1><p>'+notes[name]+'</p><p>软件对照：左旧右新，相同相机与共同取景范围。以下所有软件模型均逐面采样实际PNG。</p>'
 html+=''.join(f'<section><h2>{angle}°</h2><img src="compare-{angle}.png"></section>' for angle in [0,45,90,180])
 html+='<h2>完整动作软件回放</h2>'+''.join('<h3>'+p.stem+'</h3><img src="'+p.name+'">' for p in sorted(d.glob('*.webp')))
 html+='<h2>实际PNG与UV检查</h2><img src="texture-3x.png"><img src="uv.png">'
 if name in native:
  html+='<h2>真实Forge客户端</h2><p>隔离静音测试存档；验证加载、原动作与重载，不代表自然战斗或多人验收。</p>'
  html+=''.join('<section><p>'+p.stem+'</p><img src="native/'+p.name+'"></section>' for p in sorted((d/'native').glob('*.png')))
 (d/'index.html').write_text(html)
overview.save(D/'overview.png');(D/'native-checks.json').write_text(json.dumps(native,indent=2))
(D/'index.html').write_text('<meta charset="utf-8"><style>body{background:#eeebe1;font:20px sans-serif;margin:30px;line-height:1.6}img{max-width:100%}li{margin:16px}</style><h1>八只剩余生物：模型＋贴图</h1><p>已上传V35精英资源逐文件核对，保持不变。既有骨架、动画字节、技能和碰撞未改。</p><img src="overview.png"><ul>'+''.join('<li><a href="'+n+'/index.html">'+LANG.get('entity.dynasty.'+n,n)+'</a>：'+notes[n]+'</li>' for n in IDS)+'</ul><p>检查：真实PNG尺寸/逐面UV/编辑源/动作循环/每0.25tick离地边界。参考研究尚未达到1000个，未把重复换皮计入。</p><h2>实际查看的模型与原始贴图</h2><p>参考模型源的灰色结构与原始PNG成对查看；下图不是对方游戏实拍，不冒充完整贴图渲染。外部像素没有用于Dynasty资源。</p><img src="reference-study.png"><p><a href="https://github.com/TeamTwilight/twilightforest">暮色森林官方源码</a> · <a href="https://github.com/AlexModGuy/AlexsMobs">Alex’s Mobs官方源码</a></p>')
print('published',len(IDS),'models;',len(native),'with native evidence')
