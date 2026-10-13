"""Review actual PNG and six-block geometry. Software views are labelled honestly."""
from create import *
sys.path.insert(0,str(R/'tools/art/boss-forms'))
import texture_review as v
v.r.CATEGORY='boss_cuboid'
P=D/ID
def q(clip='idle',t=0):return v.r.geometry(ID,clip,t*20)
def blank(qs,col=(151,156,157)):return [(p,{'uv':[0,0],'uv_size':[1,1],'_tex':np.array([[col]],dtype=np.uint8)},n) for p,uv,n in qs]
def run():
 tx=np.array(Image.open(P/'texture.png'));idle=q();refs=v.references(np.array([-30,0,5]));scene=idle+refs
 frame=np.concatenate([p for p,_,_ in scene])
 def draw(qs,tex,title,yaw=35,mode='lit',size=(900,760),fr=None):
  return v.labelled(v.raster(qs,tex,yaw,elevation=4,size=size,mode=mode,frame_points=fr),title)
 for yaw,name in [(0,'front'),(45,'45'),(90,'side'),(180,'back')]:
  for mode in ['unlit','lit']:draw(idle,tx,'九霄天将 / '+name+' / '+mode,yaw,mode).save(P/f'{name}-{mode}.png')
  draw(blank(idle),tx,'六主体块＋小饰件＋大戟 / '+name,yaw).save(P/f'gray-{name}.png')
 draw(scene,tx,'九霄天将 / 1.8m玩家、1m石砖木材',35,fr=frame).save(P/'player-scale.png')
 # Equal scale overlay: exact canonical Steve six Cuboids, uniform factor 1.35.
 core=[x for x in idle if x[2] in ['chest','head','right_arm','left_arm','right_leg','left_leg']]
 # Thigh plates are excluded by regenerating bare geometry from authoritative six cubes.
 geo=json.loads(TARGETS[0].read_text());bare=copy.deepcopy(geo)
 for b in bare['minecraft:geometry'][0]['bones']:
  if b['name'] in ['right_leg','left_leg']:b['cubes']=b['cubes'][:1]
  elif b['name'] in ['weapon','crest']:b['cubes']=[]
 (P/'bare-steve.geo.json').write_text(json.dumps(bare,indent=2)+'\n')
 bareq=v.r.geometry(ID,'idle',0,geo_path=P/'bare-steve.geo.json')
 allframe=np.concatenate([p for p,_,_ in idle])
 board=Image.new('RGB',(2700,840))
 for i,(qs,tex,title) in enumerate([(blank(bareq),tx,'放大Steve / 六主体块原比例'),(blank(idle),tx,'小饰件＋原创大戟 / 当前灰模'),(idle,tx,'原创天将纹理 / 相同尺度')]):
  board.paste(draw(qs,tex,title,30,fr=allframe),(900*i,0))
 board.save(D/'overview.png')
 # Previous rejected sample shown at same model/world scale, no independent camera zoom.
 old=D.parent/'boss-steve-v14/nine_heaven_general';oq=v.r.geometry(ID,geo_path=old/f'{ID}.geo.json',animation_path=old/f'{ID}.animation.json')
 fr=np.concatenate([p for qs in [oq,idle] for p,_,_ in qs]);bd=Image.new('RGB',(1800,840))
 for i,(qs,title) in enumerate([(oq,'V14 / 肩胸手臂改动过多'),(idle,'V15 / 保留Steve主体比例')]):bd.paste(draw(blank(qs),tx,title,30,fr=fr),(900*i,0))
 bd.save(D/'before-after.png')
 draw(blank(bareq,(0,0,0)),tx,'裸主体剪影 / 六块Steve结构',0,'unlit',fr=allframe).save(P/'body-silhouette.png')
 draw(blank(idle,(0,0,0)),tx,'完成剪影 / 主要增量是武器',0,'unlit',fr=allframe).save(P/'silhouette.png')
 for title,bones in [('face',['head','crest']),('weapon',['weapon','right_arm']),('body',['chest','left_leg','right_leg'])]:
  draw([x for x in idle if x[2] in bones],tx,'原色近景 / '+title,15,'unlit',(760,650)).save(P/f'close-{title}.png')
 for mode in ['gray','dim']:draw(idle,tx,'材质层级 / '+mode,35,mode).save(P/(mode+'.png'))
 for distance in [8,16]:
  v.labelled(v.raster(scene,tx,25,distance=distance,mode='lit',size=(1000,760)),'正常视高 / '+str(distance)+'m').save(P/f'distance-{distance}.png')
 # Direction/checker is review only; never exported into running mod resources.
 v.D=D;check=v.checker(ID)
 draw(idle,check,'UV编号与方向 / 临时检查图',35,'unlit').save(P/'uv-direction.png')
 animation=json.loads(TARGETS[1].read_text())['animations']
 for clip,a in animation.items():
  times=np.linspace(0,a['animation_length'],24);poses=[q(clip,float(t)) for t in times]
  fp=np.concatenate([p for qs in poses for p,_,_ in qs]);frames=[]
  for t,qs in zip(times,poses):frames.append(draw(qs,tx,f'{clip} / {t*20:.2f} tick',30,'lit',(560,500),fp))
  frames[0].save(P/f'{clip}.webp',save_all=True,append_images=frames[1:],duration=max(15,round(a['animation_length']*1000/23)),loop=0,lossless=True)
  bd=Image.new('RGB',(1680,1160))
  for j,i in enumerate([0,5,9,12,18,23]):bd.paste(frames[i],(j%3*560,j//3*580))
  bd.save(P/f'{clip}-phases.png')
 print('Rendered actual per-face PNG, directions, player scale, six complete animation clips.')
if __name__=='__main__':run()
