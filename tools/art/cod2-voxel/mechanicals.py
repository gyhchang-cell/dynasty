"""Original four species rigs; existing IDs, action clocks and cosmetic IK contracts."""
import json
import math
from build_models import Rig, track, OUT, ASSETS

IDS=['qingtong_shuangtoushekui','xunshan_mujiaquan','bazu_digongzhu','mingsha_shixie']
SPECS=[
 (['#ffffff','#55796b','#263b37','#c0984d'],['..313..','.11111.','.21312.','..323..','.13131.','1131311','..121..']),
 (['#ffffff','#9c7644','#303c39','#c8ab69'],['.1...1.','.11311.','.12321.','..333..','.11111.','.13131.','.22.22.']),
 (['#ffffff','#675e4b','#293b38','#b99150'],['..333..','.11111.','3321233','.22122.','3211123','3.212.3','3.....3']),
 (['#ffffff','#baa06b','#46433c','#718b80'],['..333..','..323..','1.111.1','1122211','.11111.','12.2.21','2.....2']),
]

def lengths(r):
    return {k.rsplit('.',1)[1]:v['animation_length']*20 for k,v in json.loads((OUT/'source'/r.name/'original.animation.json').read_text())['animations'].items()}

def clip(r,name,channels,loop=False):r.clip(name,lengths(r)[name],channels,loop)

def wave(axis,ticks,amp,phase=0):
    return track('rotation',[(ticks*i/8,[amp*math.sin(i*math.pi/4+phase) if j==axis else 0 for j in range(3)]) for i in range(9)])

def snake(r):
    c,b=r.cube,r.bone;b('root',None,[0,0,0])
    xs=[-2,-4,-5,-3,0,3,5,4,2,0]
    for i,x in enumerate(xs):
        z=-20+i*4.5
        b('joint_'+str(i),'root' if i==0 else 'joint_'+str(i-1),[x,5,z],
          [c([x-3.5,2,z-2.5],[7,6,5]),c([x-4,1,z-2.5],[8,2,5],2),c([x-4.5,6,z-2],[9,2,4],3),c([x-1,8,z-1],[2,2,2],3)])
    b('front_head','joint_0',[-2,7,-23],[c([-7,5,-29],[10,7,9]),c([-6,5,-33],[8,4,5]),c([-8,9,-28],[12,3,7],3),c([-7,8,-30],[2,2,1],2),c([1,8,-30],[2,2,1],2),c([-4,9,-33],[4,2,2],3)])
    b('front_jaw','front_head',[-2,5,-26],[c([-6,3,-33],[8,2,9],2),c([-6,4,-32],[2,3,2],3),c([0,4,-32],[2,3,2],3)])
    b('front_horn','front_head',[-2,12,-25],[c([-5,12,-25],[2,4,3],3),c([-1,12,-25],[2,4,3],3),c([-4,15,-25],[4,2,2],3)])
    b('front_nozzle','front_head',[-2,6,-33],[c([-4,5,-34],[4,2,1],2)])
    b('rear_head','joint_9',[0,6,23],[c([-6,4,21],[12,6,8]),c([-4,4,29],[8,3,4]),c([-8,6,23],[2,4,5],3),c([6,6,23],[2,4,5],3),c([-5,7,29],[2,2,1],2),c([3,7,29],[2,2,1],2)])
    b('rear_jaw','rear_head',[0,4,26],[c([-5,2,25],[10,2,8],2),c([-4,3,31],[2,2,2],3),c([2,3,31],[2,2,2],3)])
    b('rear_horn','rear_head',[0,10,25],[c([-7,9,25],[3,3,3],3),c([4,9,25],[3,3,3],3)])
    b('rear_nozzle','rear_head',[0,5,33],[c([-2,4,33],[4,2,1],2)])
    for name in ['idle','walk','run','climb']:
        ticks=lengths(r)[name];amp={'idle':1.2,'walk':4,'run':6,'climb':4}[name]
        ch={'joint_'+str(i):wave(1,ticks,amp,i*.65) for i in range(10)}
        if name=='climb':ch['root']=track('rotation',[(0,[-30,0,0]),(ticks,[-30,0,0])])
        clip(r,name,ch,True)
    for name,end in [('attack','front'),('rear_attack','rear')]:
        ticks=lengths(r)[name];sign=-1 if end=='front' else 1
        clip(r,name,{end+'_head':{**track('position',[(0,[0,0,0]),(7,[0,1,-sign*2]),(10,[0,0,sign*5]),(14,[0,0,sign*4]),(ticks,[0,0,0])]),**track('rotation',[(0,[0,0,0]),(7,[-sign*10,0,0]),(10,[sign*8,0,0]),(ticks,[0,0,0])])},end+'_jaw':track('rotation',[(0,[0,0,0]),(7,[-sign*28,0,0]),(10,[0,0,0]),(ticks,[0,0,0])])})
    for name,end in [('fire','front'),('poison','rear')]:
        ticks=lengths(r)[name];sign=-1 if end=='front' else 1
        ch={end+'_head':track('rotation',[(0,[0,0,0]),(14,[-sign*14,0,0]),(18,[-sign*7,0,0]),(78,[-sign*7,0,0]),(ticks,[0,0,0])]),end+'_jaw':track('rotation',[(0,[0,0,0]),(16,[-sign*24,0,0]),(78,[-sign*24,0,0]),(ticks,[0,0,0])])}
        ch[end+'_nozzle']=track('scale',[(0,[1,1,1]),(18,[1.4,1.4,1]),(78,[1.4,1.4,1]),(ticks,[1,1,1])])
        clip(r,name,ch)
    clip(r,'hurt',{'joint_0':track('rotation',[(0,[0,0,0]),(2,[0,8,0]),(10,[0,0,0])])})
    clip(r,'death',{'root':track('scale',[(0,[1,1,1]),(30,[1,.55,1]),(44,[1,.55,1])]),'front_head':track('rotation',[(0,[0,0,0]),(30,[16,0,-12]),(44,[16,0,-12])]),'rear_head':track('rotation',[(0,[0,0,0]),(30,[-12,0,10]),(44,[-12,0,10])])})

def dog(r):
    c,b=r.cube,r.bone;b('root',None,[0,0,0])
    b('chest','root',[0,11,-2],[c([-6,8,-8],[12,7,13]),c([-7,12,-9],[14,4,10],3),c([-5,8,-9],[10,5,2],2)])
    b('waist','chest',[0,11,5],[c([-4,9,4],[8,5,7],2),c([-5,13,3],[10,2,9])])
    b('haunch','waist',[0,11,11],[c([-6,8,9],[12,7,8]),c([-7,12,10],[14,3,7],3)])
    for i,z in enumerate([-4,5]):b('gear_'+str(i),'chest',[0,15,z],[c([-2,15,z-2],[4,2,4],2),c([-3,16,z-1],[6,2,2],3),c([-1,16,z-3],[2,2,6],3)])
    b('neck','chest',[0,13,-8],[c([-4,11,-12],[8,7,6]),c([-5,12,-11],[10,3,3],3)])
    b('head','neck',[0,17,-12],[c([-4.5,13,-18],[9,8,8]),c([-3,13,-24],[6,4,7]),c([-3,15,-25],[6,2,2],2),c([-4.5,17.5,-19],[3,2,1],2),c([1.5,17.5,-19],[3,2,1],2),c([-5.5,19.5,-18],[11,2,8],3)])
    b('jaw','head',[0,13,-14],[c([-3.5,10,-24],[7,3,11],2),c([-3,12,-24],[2,2,2],3),c([1,12,-24],[2,2,2],3)])
    b('jaw_piston','jaw',[0,11,-14],[c([-2,9,-15],[4,2,4],3)])
    for s in [-1,1]:
        x=s*3
        b('ear_'+str(s),'head',[x,20,-12],[c([x-1.5,20,-14],[3,4,3]),c([x-1,24,-13.5],[2,2,2],2)])
    b('winding_key','chest',[0,17,6],[c([-1,16,5],[2,6,2],2),c([-5,21,5],[10,2,2],3),c([-5,18,5],[2,4,2],3),c([3,18,5],[2,4,2],3)])
    b('tail','haunch',[0,14,16],[c([-2,13,16],[4,4,7],2),c([-2.5,16,19],[5,2,4],3)])
    b('tail_tip','tail',[0,16,22],[c([-1.5,15,22],[3,4,6]),c([-1,18,26],[2,3,3],3)])
    for i,(s,z) in enumerate([(-1,-5),(1,-5),(-1,12),(1,12)]):
        x=s*5;rear=i>=2
        b('leg_'+str(i),'haunch' if rear else 'chest',[x,11,z],[c([x-2.5,5,z-2],[5,7,5]),c([x-3,9,z-3],[6,3,6],3)])
        b('knee_'+str(i),'leg_'+str(i),[x,6,z+1 if rear else z],[c([x-1.5,2,z+(1 if rear else -1)],[3,5,4],2),c([x-2,4,z],[4,2,5],3)])
        b('foot_'+str(i),'knee_'+str(i),[x,2,z],[c([x-2.5,.1,z-4],[5,2.5,7]),c([x-2,.1,z-5],[4,2,2],3)])
    clip(r,'idle',{'tail_tip':wave(1,60,8),'ear_-1':wave(2,60,3),'ear_1':wave(2,60,-3),'gear_0':wave(0,60,3)},True)
    for name in ['walk','run']:
        ticks=lengths(r)[name];ch={};amp=14 if name=='walk' else 24
        for i in range(4):
            phase=0 if i in [0,3] else math.pi
            ch['leg_'+str(i)]=wave(0,ticks,amp,phase);ch['knee_'+str(i)]=wave(0,ticks,-amp*.35,phase)
            ch['foot_'+str(i)]=wave(0,ticks,-amp*.65,phase)
        ch['tail']=wave(1,ticks,5);clip(r,name,ch,True)
    clip(r,'attack',{'neck':{**track('rotation',[(0,[0,0,0]),(6,[-12,0,0]),(8,[15,0,0]),(22,[0,0,0])]),**track('position',[(0,[0,0,0]),(6,[0,0,1]),(8,[0,0,-4]),(12,[0,0,-3]),(22,[0,0,0])])},'jaw':track('rotation',[(0,[0,0,0]),(6,[30,0,0]),(8,[0,0,0]),(22,[0,0,0])])})
    clip(r,'alarm',{'neck':track('rotation',[(0,[0,0,0]),(16,[-30,0,0]),(20,[-30,0,0]),(34,[-30,0,0]),(40,[0,0,0])]),'jaw':track('rotation',[(0,[0,0,0]),(18,[25,0,0]),(20,[32,0,0]),(32,[25,0,0]),(40,[0,0,0])]),'winding_key':wave(1,40,18),'tail':track('rotation',[(0,[0,0,0]),(16,[-20,0,0]),(34,[-20,0,0]),(40,[0,0,0])])})
    clip(r,'hurt',{'neck':track('rotation',[(0,[0,0,0]),(2,[-8,0,0]),(10,[0,0,0])])})
    clip(r,'death',{'chest':track('position',[(0,[0,0,0]),(28,[0,-5,0]),(44,[0,-5,0])]),'neck':track('rotation',[(0,[0,0,0]),(28,[24,0,0]),(44,[24,0,0])]),**{'leg_'+str(i):track('rotation',[(0,[0,0,0]),(28,[0,0,(-1 if i%2==0 else 1)*30]),(44,[0,0,(-1 if i%2==0 else 1)*30])]) for i in range(4)}})
    # Registered .85-m canine: scale authored species proportions, never change its hitbox.
    # Exact binary fractions also keep editable and exported coordinates identical.
    for bone in r.bones:
        bone['pivot']=[v*s for v,s in zip(bone['pivot'],[.75,.5,.5])]
        for cube in bone.get('cubes',[]):
            for key in ['origin','size']:cube[key]=[v*s for v,s in zip(cube[key],[.75,.5,.5])]
    for animation in r.animations.values():
        for channels in animation['bones'].values():
            if 'position' in channels:
                channels['position']={t:[v*s for v,s in zip(value,[.75,.5,.5])] for t,value in channels['position'].items()}

def spider(r):
    c,b=r.cube,r.bone;b('root',None,[0,0,0])
    b('boiler','root',[0,8,-2],[c([-6,5,-8],[12,6,10]),c([-7,9,-7],[14,3,9],3),c([-4,5,-9],[8,3,2],2)])
    b('abdomen','boiler',[0,8,3],[c([-8,5,2],[16,8,14]),c([-7,13,4],[14,2,10]),c([-9,10,4],[18,2,9],3)])
    b('head','boiler',[0,7,-8],[c([-5,4,-14],[10,5,8]),c([-6,7,-14],[12,2,5],3),c([-4,6,-15],[3,2,1],2),c([1,6,-15],[3,2,1],2)])
    for side,s in [('left',1),('right',-1)]:
        b(side+'_mandible','head',[s*3,5,-13],[c([s*3-1.5,2,-19],[3,4,6],2),c([s*3-2,2,-21],[4,2,3],3)])
    b('piston','boiler',[0,12,0],[c([-2,12,-2],[4,3,4],2),c([-3,15,-3],[6,2,6],3)])
    b('hopper','abdomen',[0,14,9],[c([-5,14,6],[10,2,7],2),c([-5,15,6],[2,3,7],3),c([3,15,6],[2,3,7],3),c([-3,15,11],[6,3,2],3)])
    b('exhaust','boiler',[0,12,-4],[c([-2,12,-6],[4,4,4],2),c([-3,15,-7],[6,2,6],3)])
    for i in range(8):
        s=1 if i<4 else -1;j=i%4;z=-7+j*6;endz=z+[-7,-3,3,7][j];x=s*6;kx=s*(15 if j in [1,2] else 13)
        # Thick stair joins, no cylinders or dense segmented fingers.
        b('hip_'+str(i),'boiler',[x,8,z],[c([min(x,kx)-1,7,z-1.5],[abs(kx-x)+2,3,3],3),c([kx-2,6,min(z,endz)-1.5],[4,4,abs(endz-z)+3])])
        b('knee_'+str(i),'hip_'+str(i),[kx,7,endz],[c([kx-2,3,endz-1.5],[4,5,3],2),c([min(kx,kx+s*4)-1.5,2,endz-1.5],[7,3,3],3)])
        b('drill_'+str(i),'knee_'+str(i),[kx+s*4,3,endz],[c([kx+s*4-2,.1,endz-2],[4,3,4],2),c([kx+s*4-3,.1,endz-3],[6,1,6],3)])
    clip(r,'idle',{'piston':track('position',[(0,[0,0,0]),(20,[0,.5,0]),(40,[0,0,0])])},True)
    for name in ['walk','run']:
        ticks=lengths(r)[name];ch={}
        for i in range(8):
            phase=(i%2)*math.pi;ch['hip_'+str(i)]=wave(1,ticks,6 if name=='walk' else 10,phase)
            ch['knee_'+str(i)]=track('position',[(ticks*k/8,[0,max(0,math.sin(k*math.pi/4+phase))*1.8,0]) for k in range(9)])
        clip(r,name,ch,True)
    attack={'piston':track('position',[(0,[0,0,0]),(9,[0,2,0]),(12,[0,-1,0]),(36,[0,0,0])])}
    for side,s in [('left',1),('right',-1)]:attack[side+'_mandible']=track('rotation',[(0,[0,0,0]),(9,[0,s*-25,0]),(12,[0,s*15,0]),(36,[0,0,0])])
    for i in [0,4]:attack['hip_'+str(i)]=track('rotation',[(0,[0,0,0]),(9,[0,0,(-1 if i==0 else 1)*20]),(12,[-15,0,0]),(36,[0,0,0])])
    clip(r,'attack',attack)
    clip(r,'drop',{'boiler':track('position',[(0,[0,0,0]),(16,[0,1,0]),(20,[0,0,0]),(40,[0,-1,0]),(70,[0,-1,0]),(100,[0,0,0])]),**{'hip_'+str(i):track('rotation',[(0,[0,0,0]),(16,[0,0,(1 if i<4 else -1)*10]),(20,[0,0,(1 if i<4 else -1)*-8]),(50,[0,0,0]),(100,[0,0,0])]) for i in range(8)}})
    clip(r,'hurt',{'boiler':track('rotation',[(0,[0,0,0]),(2,[0,0,5]),(10,[0,0,0])])})
    clip(r,'death',{'boiler':track('position',[(0,[0,0,0]),(28,[0,-3,0]),(44,[0,-3,0])]),'piston':track('scale',[(0,[1,1,1]),(28,[1,.4,1]),(44,[1,.4,1])]),**{'hip_'+str(i):track('rotation',[(0,[0,0,0]),(28,[0,0,(1 if i<4 else -1)*-18]),(44,[0,0,(1 if i<4 else -1)*-18])]) for i in range(8)}})

def scorpion(r):
    c,b=r.cube,r.bone;b('root',None,[0,0,0])
    b('carapace','root',[0,6,0],[c([-7,3,-9],[14,6,18]),c([-6,2,-7],[12,2,14],2),c([-5,5,-11],[10,4,3]),c([-4,7,-12],[2,2,1],2),c([2,7,-12],[2,2,1],2)])
    for i,z in enumerate([-6,-2,2,6]):b('shell_plate_'+str(i),'carapace',[0,9,z],[c([-7+(1 if i in [0,3] else 0),8,z-2],[14-(2 if i in [0,3] else 0),3,4]),c([-2,11,z-1],[4,2,2],3)])
    for side,s in [('right',-1),('left',1)]:
        b(side+'_claw_arm','carapace',[s*4,6,-8],[c([s*7-2,4,-14],[4,4,8],2),c([s*6-3,6,-12],[6,3,5])])
        b(side+'_claw',side+'_claw_arm',[s*7,6,-14],[c([s*8-4,3,-21],[8,7,8]),c([s*8-4.5,8,-21],[9,2,7],3)])
        b(side+'_pincer',side+'_claw',[s*7,5,-19],[c([s*8-4,4,-28],[3,4,8]),c([s*8-3,4,-30],[4,3,3],2)])
        b(side+'_pincer_tip',side+'_claw',[s*7,5,-19],[c([s*8+1,4,-27],[3,4,7]),c([s*8-1,4,-29],[4,3,3],3)])
    # Preserve the production ray IK wrappers, rest pivot lengths and neutral transforms.
    for i in range(6):
        s=-1 if i<3 else 1;z=-5+(i%3)*5;x=s*5;kx=s*10;fx=s*13
        b('leg_yaw_'+str(i),'carapace',[x,7,z])
        b('leg_ik_hip_'+str(i),'leg_yaw_'+str(i),[x,7,z])
        b('leg_thigh_'+str(i),'leg_ik_hip_'+str(i),[x,7,z],[c([min(x,kx)-1,4,z-1.5],[7,3,3]),c([x-2,6,z-2],[4,2,4],3)])
        b('leg_ik_knee_'+str(i),'leg_thigh_'+str(i),[kx,4,z])
        b('leg_shin_'+str(i),'leg_ik_knee_'+str(i),[kx,4,z],[c([min(kx,fx)-.5,.5,z-1.25],[4,3.5,2.5],2)])
        b('leg_foot_'+str(i),'leg_shin_'+str(i),[fx,.5,z],[c([fx-1.5,.1,z-2],[3,1,4])])
    coords=[(6,8),(9,11),(12,13),(15,13),(18,11),(21,7),(22,3)]
    for i,(y,z) in enumerate(coords):
        w=5 if i<3 else 4
        b('tail_'+str(i),'carapace' if i==0 else 'tail_'+str(i-1),[0,y,z],[c([-w/2,y-1,z-2],[w,4,5]),c([-w/2-.5,y+2,z-2],[w+1,1,4],2)])
    b('tail_stinger','tail_6',[0,23,2],[c([-2,21,-1],[4,4,5],3),c([-1.5,19,-3],[3,3,3],2),c([-1,17,-4],[2,3,2],2)])
    clip(r,'idle',{'tail_0':wave(1,48,2)},True)
    for name in ['walk','run']:
        ticks=lengths(r)[name];ch={}
        for i in range(6):ch['leg_yaw_'+str(i)]=wave(1,ticks,7 if name=='walk' else 11,(i%3+i//3)*math.pi)
        ch['tail_0']=wave(1,ticks,3);clip(r,name,ch,True)
    # Resource pose stays above its authored ground plane; production burrow state remains authoritative.
    clip(r,'burrow',{'carapace':{**track('scale',[(0,[1,.45,1]),(24,[1,.45,1])]),**track('position',[(0,[0,-3.3,0]),(24,[0,-3.3,0])])},**{'tail_'+str(i):track('rotation',[(0,[-6,0,0]),(24,[-6,0,0])]) for i in range(7)}} ,True)
    clip(r,'emerge',{'carapace':{**track('scale',[(0,[1,.45,1]),(18,[1,1,1]),(32,[1,1,1])]),**track('position',[(0,[0,-3.3,0]),(18,[0,0,0]),(32,[0,0,0])])},'tail_0':track('rotation',[(0,[-20,0,0]),(22,[5,0,0]),(32,[0,0,0])])})
    ch={}
    for side,s in [('right',-1),('left',1)]:
        ch[side+'_claw_arm']=track('rotation',[(0,[0,0,0]),(8,[-8,s*15,0]),(12,[0,-s*15,0]),(20,[0,-s*15,0]),(40,[0,0,0])])
        ch[side+'_pincer']=track('rotation',[(0,[0,0,0]),(8,[0,-20,0]),(12,[0,12,0]),(20,[0,12,0]),(40,[0,0,0])])
        ch[side+'_pincer_tip']=track('rotation',[(0,[0,0,0]),(8,[0,20,0]),(12,[0,-12,0]),(20,[0,-12,0]),(40,[0,0,0])])
    for i in range(7):ch['tail_'+str(i)]=track('rotation',[(0,[0,0,0]),(12,[-2,0,0]),(16,[-2,0,0]),(20,[8,0,0]),(25,[6,0,0]),(40,[0,0,0])])
    clip(r,'attack',ch)
    clip(r,'song',{'shell_plate_'+str(i):track('position',[(0,[0,0,0]),(16,[0,1.5,0]),(20,[0,0,0]),(24,[0,1,0]),(28,[0,0,0]),(32,[0,.6,0]),(38,[0,0,0]),(48,[0,0,0])]) for i in range(4)})
    clip(r,'hurt',{'carapace':track('rotation',[(0,[0,0,0]),(2,[0,0,5]),(10,[0,0,0])])})
    clip(r,'death',{'carapace':{**track('position',[(0,[0,0,0]),(30,[0,-2,0]),(44,[0,-2,0])]),**track('scale',[(0,[1,1,1]),(30,[1,.65,1]),(44,[1,.65,1])])},**{'tail_'+str(i):track('rotation',[(0,[0,0,0]),(30,[8,0,0]),(44,[8,0,0])]) for i in range(7)},**{side+'_claw_arm':track('rotation',[(0,[0,0,0]),(30,[0,s*18,0]),(44,[0,s*18,0])]) for side,s in [('right',-1),('left',1)]}})

def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--ids',nargs='+',choices=IDS,default=IDS);selected=parser.parse_args().ids
    for name in selected:
        for folder,suffix,original in [('geo','.geo.json','original.geo.json'),('animations','.animation.json','original.animation.json')]:
            # An explicit manual rerun of our own authored files is allowed; concurrent unknown changes aren't.
            current=ASSETS/f'{folder}/blueprint/{name}{suffix}'
            baseline=OUT/'source'/name/original
            own=OUT/'mechanicals-owned-hashes.json'
            import hashlib
            allowed=json.loads(own.read_text()) if own.exists() else {}
            assert current.read_bytes()==baseline.read_bytes() or hashlib.sha256(current.read_bytes()).hexdigest()==allowed.get(str(current)), 'Concurrent changes: '+name
    for name,(palette,portrait),builder in zip(IDS,SPECS,[snake,dog,spider,scorpion]):
        if name not in selected:continue
        r=Rig(name,palette,portrait);builder(r);r.save()
        print(name,len(r.bones),'bones',sum(len(b.get('cubes',[])) for b in r.bones),'cuboids',flush=True)
    from contacts import settle
    settle(selected)
    import hashlib
    previous=OUT/'mechanicals-owned-hashes.json'
    hashes=json.loads(previous.read_text()) if previous.exists() else {}
    for name in selected:
        a=ASSETS/f'animations/blueprint/{name}.animation.json'
        (OUT/'blockbench'/(name+'.animation.json')).write_bytes(a.read_bytes())
        for folder,suffix in [('geo','.geo.json'),('animations','.animation.json')]:
            p=ASSETS/f'{folder}/blueprint/{name}{suffix}';hashes[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    (OUT/'mechanicals-owned-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')

if __name__=='__main__':main()
