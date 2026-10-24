from pathlib import Path
import json,sys,html
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/weapon-visual-acceptance'
rows=[]
for run in sys.argv[1:]:
 p=O/run
 for q in sorted(p.glob('*-frames.json')):
  fs=json.loads(q.read_text());name=q.name[:-12];shot=[(i,f) for i,f in enumerate(fs) if 'screenshot'in f]
  if not shot:continue
  def score(pair):return sum(v['changedPixels'] for k,v in pair[1].get('nativePixelDelta',{}).items() if k!='Cod3Vfx')+sum(len(v) for v in pair[1]['geometry'].values())
  selected=sorted(shot,key=score,reverse=True)[:1]
  selected+=shot[len(shot)//2:len(shot)//2+1]
  rows.append('<section><h2>'+html.escape(run+' / '+name)+'</h2>')
  for i,f in selected:
   rows.append('<figure><a href="'+run+'/'+f['screenshot']+'"><img loading="lazy" src="'+run+'/'+f['screenshot']+'"></a><figcaption>'+html.escape(json.dumps({'frame_index':i,'serial':f['frameSerial'],'tick':f['tick'],'partial':f['partialTick'],'geometry':{k:len(v) for k,v in f['geometry'].items()},'nativePixelDelta':f.get('nativePixelDelta',{})},ensure_ascii=False))+'</figcaption></figure>')
  rows.append('<a href="'+run+'/'+q.name+'">原始同帧数据</a></section>')
(O/'gallery.html').write_text('<!doctype html><meta charset="utf-8"><title>COD4 武器原生验收帧</title><style>body{background:#151821;color:#eceff6;font:15px system-ui;margin:24px}section{margin:24px 0;padding:18px;border:1px solid #545e70}figure{display:inline-block;width:46%;vertical-align:top;margin:1%}img{width:100%}figcaption{overflow-wrap:anywhere;font-size:12px}a{color:#8fdad1}</style><h1>原生截图与同帧记录</h1><p>自动选帧索引，仍需视觉审查；几何提交和非零像素均不直接等于整条验收通过。图片均为客户端原始截图，无合成或效果补发。</p>'+''.join(rows))
