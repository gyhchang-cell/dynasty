"""Original second batch: bat anatomy, jointed skeletal fish, articulated water ghost.

See FLOATERS.md for the plan written before these assets. Existing gameplay
contracts and aliases are retained. The first batch is never regenerated here.
"""
import json
import shutil
from build_models import Rig, track, OUT, ASSETS
from contacts import settle

IDS=['youdeng_guimianfu','xueju_mangguyu','shashui_funigui']


def bat(r):
    c,b=r.cube,r.bone
    b('root',None,[0,0,0])
    b('body','root',[0,12,0],[c([-4,8,-3],[8,7,6]),c([-3,9,-4],[6,5,2],2),c([-3,8,3],[6,5,2])])
    b('head','body',[0,16,0],[c([-5,14,-4],[10,6,7]),c([-4,18,-5],[8,2,2],2),
        c([-5,19,-1],[3,4,3]),c([2,19,-1],[3,4,3]),c([-4,20,-2],[2,2,1],3),c([2,20,-2],[2,2,1],3)])
    b('face','head',[0,17,-4],[c([-4,14,-5],[8,4,1],2),c([-4,16,-6],[3,2,1]),c([1,16,-6],[3,2,1]),c([-1,14,-6],[2,2,1],3)])
    for side,s in [('left',1),('right',-1)]:
        def box(x,y,z,w,h,d,m=1):return c([min(s*x,s*(x+w)),y,z],[w,h,d],m)
        b(side+'_wing','body',[s*4,14,1],[box(4,13,0,7,2,3,2),box(5,8,2,6,5,1)],rotation=[0,0,s*8])
        # Separate coarse spars and a stepped trailing edge, not four overlapping rods.
        for i,(y,length,drop) in enumerate([(15,11,3),(13,10,5),(11,8,5),(9,5,4)]):
            b(side+'_finger_'+str(i),side+'_wing',[s*10,y,1],
                [box(10,y-1,0,length,1,2,2),box(10,y-drop,1,length-2,drop,1),
                 box(10+length-2,y-drop+2,1,2,drop-2 if drop>2 else 1,1)],rotation=[0,0,s*(10-i*8)])
    b('lantern','body',[0,7,-1],[c([-3,1,-4],[6,1,6],2),c([-3,6,-4],[6,2,6],2),c([-2,2,-3],[4,4,4]),
        c([-3,2,-4],[1,4,1],2),c([2,2,-4],[1,4,1],2),c([-3,2,1],[1,4,1],2),c([2,2,1],[1,4,1],2),
        c([-2,8,-2],[1,2,2],2),c([1,8,-2],[1,2,2],2),c([-2,9,-2],[4,1,2],2)])
    b('flame','lantern',[0,4,-1],[c([-1,2,-4],[2,4,1],3),c([-1,2,1],[2,4,1],3),c([-3,2,-2],[1,4,2],3),c([2,2,-2],[1,4,2],3)])
    # The two clasping feet follow the handle through every lift/swing pose.
    for side,s in [('left',1),('right',-1)]:
        x=1 if s==1 else -3
        b(side+'_claw','lantern',[s*2,9,0],[c([x,6,-1],[2,4,2],2),c([x,6,-3],[2,2,3],2)])
    def wings(ticks,amplitude):
        channels={}
        for side,s in [('left',1),('right',-1)]:
            channels[side+'_wing']=track('rotation',[(0,[0,0,-s*amplitude]),(ticks/2,[0,0,s*amplitude]),(ticks,[0,0,-s*amplitude])])
            for i in range(4):channels[side+'_finger_'+str(i)]=track('rotation',[(0,[0,s*4,-s*8]),(ticks/2,[0,-s*4,s*8]),(ticks,[0,s*4,-s*8])])
        return channels
    r.clip('idle',24,{**wings(24,8),'body':track('position',[(0,[0,0,0]),(12,[0,.3,0]),(24,[0,0,0])]),
        'lantern':track('rotation',[(0,[3,0,-3]),(12,[-3,0,3]),(24,[3,0,-3])])},True)
    for name,ticks,amp in [('walk',16,24),('run',10,36)]:r.clip(name,ticks,{**wings(ticks,amp),
        'body':track('rotation',[(0,[10 if name=='walk' else 20,0,0]),(ticks/2,[6 if name=='walk' else 16,0,0]),(ticks,[10 if name=='walk' else 20,0,0])]),
        'lantern':track('rotation',[(0,[-8,0,0]),(ticks/2,[8,0,0]),(ticks,[-8,0,0])])},True)
    r.clip('attack',60,{'body':track('rotation',[(0,[0,0,0]),(12,[18,0,0]),(18,[65,0,0]),(32,[48,0,0]),(40,[-15,0,0]),(60,[0,0,0])]),
        'lantern':track('rotation',[(0,[0,0,0]),(12,[-15,0,0]),(18,[-40,0,0]),(40,[18,0,0]),(60,[0,0,0])]),
        **{side+'_wing':track('rotation',[(0,[0,0,0]),(12,[0,s*45,s*45]),(18,[0,s*60,s*60]),(32,[0,s*45,s*50]),(40,[0,0,-s*20]),(60,[0,0,0])]) for side,s in [('left',1),('right',-1)]}})
    r.clip('glare',50,{'lantern':{**track('rotation',[(0,[0,0,0]),(18,[-35,0,0]),(24,[-48,0,0]),(36,[-48,0,0]),(50,[0,0,0])]),
        **track('position',[(0,[0,0,0]),(18,[0,2,-2]),(24,[0,3,-3]),(36,[0,3,-3]),(50,[0,0,0])])},
        'flame':track('scale',[(0,[1,1,1]),(20,[1.2,1,1]),(24,[1.5,1,1]),(30,[1.2,1,1]),(50,[1,1,1])]),
        **{side+'_wing':track('rotation',[(0,[0,0,0]),(18,[0,0,-s*20]),(36,[0,0,-s*20]),(50,[0,0,0])]) for side,s in [('left',1),('right',-1)]}})
    r.clip('hurt',10,{'body':track('rotation',[(0,[0,0,0]),(2,[-12,0,8]),(10,[0,0,0])])})
    r.clip('death',44,{'body':{**track('rotation',[(0,[0,0,0]),(30,[80,0,12]),(44,[80,0,12])]),**track('position',[(0,[0,0,0]),(30,[0,-7,0]),(44,[0,-7,0])])},
        **{side+'_wing':track('rotation',[(0,[0,0,0]),(24,[0,s*70,s*60]),(44,[0,s*70,s*60])]) for side,s in [('left',1),('right',-1)]},
        'flame':track('scale',[(0,[1,1,1]),(28,[1,1,1]),(44,[.1,.1,.1])])})


def fish(r):
    c,b=r.cube,r.bone;b('root',None,[0,0,0])
    b('spine_0','root',[0,12,-15],[c([-6,8,-22],[12,9,10]),c([-5,10,-24],[10,5,3]),
        c([-7,12,-19],[2,4,5]),c([5,12,-19],[2,4,5]),c([-4,13,-25],[8,2,1],2),
        c([-5,8,-23],[2,4,2]),c([3,8,-23],[2,4,2]),c([-2,10,-25],[4,2,1],3)])
    for i,(z,w,h) in enumerate([(-12,11,8),(-7,10,7),(-2,9,6),(3,8,5),(8,6,4),(13,4,3),(17,3,3)],1):
        b('spine_'+str(i),'spine_'+str(i-1),[0,12,z],
            [c([-w/2,12-h/2,z],[w,h,5],2),c([-w/2-.5,12-h/2-.5,z+1],[w+1, h+1,2]),c([-1,12,z],[2,2,5],3)])
        if i<7:
            b('dorsal_'+str(i),'spine_'+str(i),[0,12+h/2,z+2],
              [c([-1,12+h/2,z+1],[2,4 if i<4 else 3,3],3)])
            b('ribbon_'+str(i),'dorsal_'+str(i),[0,16+h/2,z+2],
              [c([-.5,15+h/2,z+2],[1,2,4],3)])
    b('jaw','spine_0',[0,9,-15],[c([-5,6,-24],[10,3,10]),c([-5,8,-24],[2,2,2]),c([3,8,-24],[2,2,2]),c([-3,6,-25],[6,2,1],2)])
    for side,s in [('left',1),('right',-1)]:
        def box(x,y,z,w,h,d,m=1):return c([min(s*x,s*(x+w)),y,z],[w,h,d],m)
        b(side+'_fin','spine_2',[s*5,11,-6],[box(5,10,-8,5,2,8),box(6,9,-4,4,1,5,3)],rotation=[0,s*12,s*-10])
        b(side+'_fin_tip',side+'_fin',[s*10,11,-4],[box(10,10,-5,4,1,5),box(10,10,0,2,1,3,3)])
    b('tail_fin','spine_7',[0,12,21],[c([-1,8,20],[2,8,3]),c([-1,5,23],[2,5,4]),c([-1,14,23],[2,5,4])])
    b('tail_tip','tail_fin',[0,12,26],[c([-.5,3,26],[1,5,3],3),c([-.5,16,26],[1,5,3],3)])
    def wave(ticks,amp):
        channels={}
        for i in range(8):
            phase=i%4;values=[amp*(1 if (phase+j)%4==1 else -1 if (phase+j)%4==3 else 0) for j in range(5)]
            channels['spine_'+str(i)]=track('rotation',[(j*ticks/4,[0,v,0]) for j,v in enumerate(values)])
        for side,s in [('left',1),('right',-1)]:channels[side+'_fin_tip']=track('rotation',[(0,[0,0,s*8]),(ticks/2,[0,0,-s*8]),(ticks,[0,0,s*8])])
        return channels
    for name,ticks,amp in [('idle',60,3),('walk',44,7),('run',32,11)]:r.clip(name,ticks,wave(ticks,amp),True)
    r.clip('attack',40,{**{'spine_'+str(i):track('rotation',[(0,[0,0,0]),(12,[0,-(4+i*2),0]),(16,[0,8+i*3,0]),(24,[0,4+i,0]),(40,[0,0,0])]) for i in range(8)},
        'tail_fin':track('rotation',[(0,[0,0,0]),(12,[0,-25,0]),(16,[0,35,0]),(26,[0,15,0]),(40,[0,0,0])])})
    r.clip('resonance',60,{'jaw':track('rotation',[(0,[0,0,0]),(24,[32,0,0]),(30,[42,0,0]),(38,[32,0,0]),(60,[0,0,0])]),
        'spine_0':track('rotation',[(0,[0,0,0]),(24,[-7,0,0]),(30,[-10,0,0]),(38,[-7,0,0]),(60,[0,0,0])]),
        **{'dorsal_'+str(i):track('rotation',[(0,[0,0,0]),(24,[-16,0,0]),(30,[-25,0,0]),(38,[-16,0,0]),(60,[0,0,0])]) for i in range(1,7)}})
    r.clip('hurt',10,{'spine_0':track('rotation',[(0,[0,0,0]),(2,[0,10,5]),(10,[0,0,0])])})
    r.clip('death',44,{'spine_0':{**track('rotation',[(0,[0,0,0]),(30,[0,0,65]),(44,[0,0,65])]),**track('position',[(0,[0,0,0]),(30,[0,-7,0]),(44,[0,-7,0])])},
        **{'spine_'+str(i):track('rotation',[(0,[0,0,0]),(30,[0,7,0]),(44,[0,7,0])]) for i in range(1,8)}})


def drowner(r):
    c,b=r.cube,r.bone;b('root',None,[0,0,0])
    # The existing renderer scales this whole subtree about ground level during pool.
    b('body','root',[0,0,0],[c([-8,0,-7],[16,2,14]),c([-6,2,-5],[12,4,10]),
        c([-8,2,-5],[3,3,3],3),c([5,2,2],[3,3,3],3),c([-5,0,-8],[4,2,2],2),c([2,0,6],[4,2,2],2)])
    b('pelvis','body',[0,9,0],[c([-4,6,-4],[8,6,8]),c([-5,7,-5],[10,3,10],3)])
    b('waist','pelvis',[0,12,0],[c([-3,11,-3],[6,5,6],2),c([-4,12,-4],[8,2,8],3)])
    b('wave_1','waist',[0,17,0],[c([-5,15,-3],[10,7,6]),c([-4,16,-5],[8,4,2],3),
        c([-2,19,-6],[4,2,1],2),c([-5,19,3],[10,2,1],2)])
    b('neck','wave_1',[0,22,0],[c([-2,21,-2],[4,3,4],3)])
    b('wave_2','neck',[0,25,0],[c([-4,23,-4],[8,6,7],3),c([-5,28,-4],[10,2,8],2),
        c([-3,26,-5],[2,2,1],2),c([1,26,-5],[2,2,1],2),c([-3,23,-5],[6,2,1],2),c([-1,25,-6],[2,2,2])])
    # Seven inherited names; chunky separate front locks and rear curtains.
    hair=[(-4,25,-5,2,5,2), (2,25,-5,2,5,2), (-5,20,-2,2,10,3), (3,20,-2,2,10,3),
          (-4,18,3,3,12,2), (1,19,3,3,11,2), (-1,25,-5,2,5,1)]
    for i,(x,y,z,w,h,d) in enumerate(hair):b('hair_'+str(i),'wave_2',[x+w/2,29,z],[c([x,y,z],[w,h,d],2)])
    for side,s in [('left',1),('right',-1)]:
        def box(x,y,z,w,h,d,m=1):return c([min(s*x,s*(x+w)),y,z],[w,h,d],m)
        b(side+'_whip_0','wave_1',[s*5,20,0],[box(5,12,-2,4,8,4),box(5,18,-3,4,3,6,3)])
        b(side+'_whip_1',side+'_whip_0',[s*7,12,0],[box(6,6,-1,3,7,3,3)])
        b(side+'_whip_2',side+'_whip_1',[s*7,6,0],[box(6,4,-3,3,3,5)])
        for i in range(3):b(side+'_spray_'+str(i),side+'_whip_2',[s*(6+i*2),5,-1],[box(5+i*2,1+i%2,-3,2,4-i%2,2,3)])
    def waves(ticks,amp):
        channels={'wave_1':track('rotation',[(0,[0,0,-amp]),(ticks/2,[0,0,amp]),(ticks,[0,0,-amp])]),
            'wave_2':track('rotation',[(0,[0,0,amp]),(ticks/2,[0,0,-amp]),(ticks,[0,0,amp])])}
        for i in range(7):channels['hair_'+str(i)]=track('rotation',[(0,[2,0,0]),(ticks/2,[-2,0,0]),(ticks,[2,0,0])])
        for side,s in [('left',1),('right',-1)]:
            channels[side+'_whip_0']=track('rotation',[(0,[-3,0,-s*5]),(ticks/2,[3,0,s*3]),(ticks,[-3,0,-s*5])])
        return channels
    for name,ticks,amp in [('idle',60,2),('walk',40,4),('run',28,6)]:r.clip(name,ticks,waves(ticks,amp),True)
    r.clip('attack',36,{'wave_1':track('rotation',[(0,[0,0,0]),(10,[0,-18,-5]),(14,[0,25,7]),(22,[0,15,3]),(36,[0,0,0])]),
        'right_whip_0':track('rotation',[(0,[0,0,0]),(10,[25,0,20]),(14,[-95,-10,-15]),(22,[-80,0,-10]),(36,[0,0,0])]),
        'right_whip_1':{**track('rotation',[(0,[0,0,0]),(10,[-70,0,0]),(14,[0,0,0]),(22,[-15,0,0]),(36,[0,0,0])]),
            **track('scale',[(0,[1,1,1]),(10,[1,.7,1]),(14,[1,2.2,1]),(18,[1,2.2,1]),(28,[1,1,1]),(36,[1,1,1])])},
        'right_whip_2':track('rotation',[(0,[0,0,0]),(10,[-30,0,0]),(14,[0,0,0]),(36,[0,0,0])])})
    r.clip('pool',104,{'wave_1':track('rotation',[(0,[0,0,0]),(18,[12,0,0]),(24,[20,0,0]),(84,[20,0,0]),(104,[0,0,0])]),
        'wave_2':track('rotation',[(0,[0,0,0]),(24,[-10,0,0]),(84,[-10,0,0]),(104,[0,0,0])]),
        **{side+'_whip_0':track('rotation',[(0,[0,0,0]),(24,[-20,0,-s*45]),(84,[-20,0,-s*45]),(104,[0,0,0])]) for side,s in [('left',1),('right',-1)]}})
    r.clip('hurt',10,{'wave_1':track('rotation',[(0,[0,0,0]),(2,[-8,0,-3]),(10,[0,0,0])])})
    r.clip('death',44,{'body':track('scale',[(0,[1,1,1]),(18,[1.4,.55,1.4]),(30,[1.8,.15,1.8]),(44,[2,.05,2])]),
        'wave_2':track('rotation',[(0,[0,0,0]),(30,[16,0,0]),(44,[16,0,0])])})


def main():
    specs=[(bat,['#ffffff','#303743','#a4b4a1','#83c989'],['.1...1.','1122211','1221221','1121211','.11111.','..232..','..232..']),
        (fish,['#ffffff','#c7c4a4','#414b4c','#af484b'],['...3...','..131..','.11111.','1211121','1213121','.11111.','..121..']),
        (drowner,['#ffffff','#c6d8da','#6e8e8a','#d5e4bc'],['..222..','..232..','..323..','.13331.','.31213.','.31113.','1111111'])]
    for name,(author,palette,portrait) in zip(IDS,specs):
        r=Rig(name,palette,portrait);author(r);r.save();print(name,len(r.bones),'bones')
    settle(IDS)
    for name in IDS:shutil.copy2(ASSETS/'animations/blueprint'/f'{name}.animation.json',OUT/'blockbench'/f'{name}.animation.json')


if __name__=='__main__':main()
