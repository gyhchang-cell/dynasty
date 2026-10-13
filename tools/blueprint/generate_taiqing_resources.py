#!/usr/bin/env python3
"""Original world sword case and temple data, sharing the actual15-cube native Zhanlu sword."""
from pathlib import Path
import copy,json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];A=R/'src/main/resources/assets/dynasty';D=R/'src/main/resources/data/dynasty';ID='taiqing_ancient_sword_case'
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
uv={'jade':[3,3,7,7],'bronze':[9,3,13,7],'wood':[3,9,7,13]}
def faces(material):return {f:{'texture':'#all','uv':uv[material]} for f in ('up','down','north','south','west','east')}
def cuboid(lo,hi,material):return {'from':lo,'to':hi,'faces':faces(material)}
body=[cuboid([2,0,-4],[14,1,28],'wood'),cuboid([2,1,-4],[4,9,28],'wood'),cuboid([12,1,-4],[14,9,28],'wood'),cuboid([4,1,-4],[12,9,-2],'bronze'),cuboid([4,1,26],[12,9,28],'bronze')]
mesh=json.loads((A/'models/item/zhanlu_rendao_bamian_jian_mesh.json').read_text())['elements'];assert len(mesh)==15
sword=[]
# Lay the authoritative native held sword flat with a true90deg basis conversion.
# Export rotations still use only Minecraft's supported -45deg element rotations.
def place(v):x,y,z=v;return [x,13-z,y-4]
for original in mesh:
 e=copy.deepcopy(original);lo=place(original['from']);hi=place(original['to']);e['from']=[min(a,b) for a,b in zip(lo,hi)];e['to']=[max(a,b) for a,b in zip(lo,hi)]
 for f in e['faces'].values():f['texture']='#sword'
 if 'rotation' in e:
  rotation=e['rotation'];assert rotation['axis']=='y' and rotation['angle']==-45;rotation['axis']='z';rotation['origin']=place(rotation['origin'])
 assert all(-16<=v<=32 for v in e['from']+e['to']);sword.append(e)
textures={'all':'dynasty:block/'+ID,'sword':'dynasty:entity/blueprint/artifact/zhanlu_rendao_bamian_jian','particle':'dynasty:block/'+ID}
write(A/f'models/block/{ID}.json',{'textures':textures,'elements':body+sword+[cuboid([2,9,-4],[14,10,28],'bronze')]})
write(A/f'models/block/{ID}_ready.json',{'textures':textures,'elements':body+sword+[cuboid([14,8,-4],[26,10,28],'bronze')]})
write(A/f'models/block/{ID}_open.json',{'textures':textures,'elements':body+[cuboid([14,8,-4],[26,10,28],'bronze')]})
write(A/f'blockstates/{ID}.json',{'variants':{'trial_state=0':{'model':'dynasty:block/'+ID},'trial_state=1':{'model':'dynasty:block/'+ID+'_ready'},'trial_state=2':{'model':'dynasty:block/'+ID+'_open'}}})
im=Image.new('RGB',(16,16),'white');draw=ImageDraw.Draw(im)
for name,color in {'jade':'#253F3C','bronze':'#817650','wood':'#7A5440'}.items():x,y,x1,y1=uv[name];draw.rectangle((x,y,x1-1,y1-1),fill=color)
p=A/f'textures/block/{ID}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
write(D/f'loot_tables/blocks/{ID}.json',{'type':'minecraft:block','pools':[]})
biomes=['minecraft:plains','minecraft:forest','minecraft:birch_forest','minecraft:windswept_forest']
write(D/'worldgen/structure/taiqing_hidden_temple.json',{'type':'dynasty:taiqing_hidden_temple','biomes':biomes,'step':'surface_structures','terrain_adaptation':'none','spawn_overrides':{}})
write(D/'worldgen/structure_set/taiqing_hidden_temple.json',{'structures':[{'structure':'dynasty:taiqing_hidden_temple','weight':1}],'placement':{'type':'minecraft:random_spread','spacing':48,'separation':24,'salt':18374923}})
write(D/'tags/worldgen/structure/blueprint/taiqing_trials.json',{'replace':False,'values':['dynasty:taiqing_hidden_temple']})
messages={'begin':['太清问道：全程不得受伤或主动攻击。先在左前方青石上静立两秒凝神。','Taiqing trial: remain unharmed and refrain from attacking. Stand still on the front-left green stone for two seconds.'],'stage2':['玉清履道：从右前方白石起，循白石依次到五个转折点，不得离道或跃过。','Jade Purity: follow the white path from the front-right shrine through its five turns. Keep your feet on the white stones.'],'stage3':['上清止戈：空出双手，在左后方青色光阵中坚持六秒，避开四次红色扇区。','High Purity: empty both hands and stay in the rear-left cyan ring for six seconds. Avoid its four red sectors.'],'ready':['三清已悟。空手触动中央古剑匣，湛卢只在本世界认主一次。','Three Purities understood. Touch the central case with an empty hand. Zhanlu is granted once per player in this world.'],'failed':['参悟中断。空手触动古剑匣，可从太清凝神重新开始。','Trial interrupted. Touch the sword case with an empty hand to begin again.'],'claimed':['湛卢已经认你为主，本世界不能再次领取。','Zhanlu has already accepted you. It cannot be claimed again in this world.'],'sword':['仁道八面剑已解封。湛卢入手，古匣长存。','The sword is unsealed. Zhanlu is yours; the ancient case remains.'],'inventory':['请靠近古剑匣，并留出一个物品栏空位。','Move closer to the case and leave one inventory slot free.'],'unregistered':['剑匣尚未认主，或你已在另一座太清观完成试炼。','This case is not yet recognized, or you have already completed the trial at another temple.']}
for lang,index in [('zh_cn',0),('en_us',1)]:
 p=A/f'lang/{lang}.json';content=json.loads(p.read_text());content['block.dynasty.'+ID]=['太清古剑匣','Taiqing Ancient Sword Case'][index]
 for k,v in messages.items():content['message.dynasty.taiqing_'+k]=v[index]
 write(p,content)
assert im.size==(16,16) and len(set(im.get_flattened_data()))==4
print('Exported original2m sword case and15real sword cubes, native temple/trial resources; no Java')
