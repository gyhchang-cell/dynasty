"""Read-only model sampling with final candidate PNG; software evidence only."""
from pathlib import Path
import sys,json,itertools,hashlib
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[3];A=R/'src/main/resources/assets/dynasty'
sys.path.insert(0,str(R/'tools/art/boss-forms'))
import texture_review as v
v.r.CATEGORY='scenic'
tex=np.array(Image.open(D/'stone_god.png').convert('RGB'));temp=np.array(Image.open(D.parent/'temporary-material-atlas.png').convert('RGB'))
def pose(t=0,lod=''):return v.r.geometry('stone_god',clip='animation.scenic.idle',tick=t,geo_path=A/f'geo/scenic/stone_god{lod}.geo.json')
q=pose();points=np.concatenate([p for p,_,_ in q]);lo=points.min(0)-[0,3,0];hi=points.max(0)+[0,3,0];frame=np.array(list(itertools.product(*zip(lo,hi))))
foot='软件预览 · 最终1024 PNG逐面最近邻采样 · 无粒子/发光 · 非实机截图'
ims={}
for yaw,label in [(180,'front'),(135,'45'),(90,'right'),(-90,'left'),(0,'back')]:
 im=v.raster(q,tex,yaw=yaw,elevation=6,size=(1100,720),mode='lit',frame_points=frame);ims[label]=v.labelled(im,'神人开山 / '+label,foot);ims[label].save(D/(label+'.png'))
for mode in ['unlit','dim','gray']:
 im=v.raster(q,tex,yaw=135,elevation=6,size=(1100,720),mode=mode,frame_points=frame);ims[mode]=v.labelled(im,'神人开山 / '+mode,foot);ims[mode].save(D/(mode+'.png'))
ims['silhouette']=v.labelled(v.raster(q,np.zeros_like(tex),yaw=135,elevation=6,size=(1100,720),mode='unlit',frame_points=frame),'神人开山 / 黑剪影',foot);ims['silhouette'].save(D/'silhouette.png')
# Show all three actual LODs under identical framing; separate distance views below.
for suffix,label in [('', 'full'),('_medium','medium'),('_far','far')]:
 lodq=pose(lod=suffix);ims[label]=v.labelled(v.raster(lodq,tex,yaw=135,elevation=6,size=(1100,720),mode='lit',frame_points=frame),'神人开山 / '+label+' LOD',foot);ims[label].save(D/(label+'.png'))
for n,dist,lod in [('near',64,''),('mid',112,'_medium'),('distant',192,'_far')]:
 # Distance argument is metres; raster converts to model units internally.
 im=v.raster(pose(lod=lod),tex,yaw=135,elevation=14,size=(1100,720),mode='lit',distance=dist);v.labelled(im,f'神人开山 / {dist}m 相同FOV',foot).save(D/(n+'-distance.png'))
# Same geometry, UVs, camera and software light for comparison with temporary flat checker.
comparison=Image.new('RGB',(2200,800))
for i,(t,label) in enumerate([(temp,'BEFORE / 交接临时色 · 非旧版游戏资产'),(tex,'AFTER / 原创像素图集')]):comparison.paste(v.labelled(v.raster(q,t,yaw=135,elevation=6,size=(1100,720),mode='lit',frame_points=frame),label,foot),(i*1100,0))
comparison.save(D/'comparison.png')
labels=['front','45','right','back','unlit','dim','gray','silhouette','medium','far'];sheet=Image.new('RGB',(1650,1600),'#d6dddf')
for i,label in enumerate(labels):sheet.paste(ims[label].resize((550,400),Image.Resampling.NEAREST),(i%3*550,i//3*400))
sheet.save(D/'overview.png')
# Model animation sampling changes no resource files.
frames=[]
for t in [0,40,80,120,160]:
 frames.append(v.labelled(v.raster(pose(t),tex,yaw=135,elevation=6,size=(660,460),mode='lit',frame_points=frame),f'神人开山 / {t}tick',foot))
frames[0].save(D/'idle.webp',save_all=True,append_images=frames[1:],duration=400,loop=0,lossless=True)
print('Final PNG sampled: five angles, unlit/dim/gray/black, three LODs,64/112/192m and five animation samples. SOFTWARE ONLY.')
