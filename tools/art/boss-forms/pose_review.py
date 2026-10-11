"""Preview the exported animation keyframes without starting a JVM or Minecraft."""
import json
import numpy as np
from PIL import Image,ImageDraw
from review import r,D,A,view,label,font
ms=json.loads((D/'forms.json').read_text());report={}
for i,m in enumerate(ms):
 prefix='' if i<3 else 'animation.'+m['id']+'.'
 animations=json.loads((A/'animations/boss_forms'/f"{m['id']}.animation.json").read_text())['animations']
 checks={}
 for clip,a in animations.items():
  limits=[]
  for t in np.linspace(0,a['animation_length'],17):
   vs=np.concatenate([q[0] for q in r.geometry(m['id'],clip=clip,tick=float(t*20))]);limits.append(float(vs[:,1].min()))
  checks[clip]={'minY':round(min(limits),3),'finalMinY':round(limits[-1],3)}
 report[m['id']]=checks
 samples=[('idle',20),('walk',animations[prefix+'walk']['animation_length']*5),('walk',animations[prefix+'walk']['animation_length']*15),(['attack','cast','attack','roar','net','sweep','fire','slam'][i],[8,14,12,24,14,20,20,28][i]),('death',animations[prefix+'death']['animation_length']*10),('death',animations[prefix+'death']['animation_length']*20)]
 out=Image.new('RGB',(1860,864),(238,235,225));ImageDraw.Draw(out).text((18,10),m['name']+' · 实际动画采样 · 软件预览（非游戏画面）',font=font(24),fill=(35,40,45))
 for j,(clip,tick) in enumerate(samples):
  im=label(view(m,45,False,clip=prefix+clip,tick=tick,scale=3.),f'{clip} · tick {tick:.1f}');out.paste(im,(j%3*620,60+j//3*402))
 out.save(D/(m['id']+'-motion.png'))
death=Image.new('RGB',(1240,1673),(238,235,225));ImageDraw.Draw(death).text((18,14),'实际导出动画 · 落地死亡姿态 · 非游戏截图',font=font(24),fill=(35,40,45))
for i,m in enumerate(ms):
 prefix='' if i<3 else 'animation.'+m['id']+'.';clip=prefix+'death';a=json.loads((A/'animations/boss_forms'/f"{m['id']}.animation.json").read_text())['animations'][clip]
 death.paste(label(view(m,45,False,clip=clip,tick=a['animation_length']*20,scale=3.),m['name']),(i%2*620,65+i//2*402))
death.save(D/'death-overview.png')
(D/'pose-report.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
