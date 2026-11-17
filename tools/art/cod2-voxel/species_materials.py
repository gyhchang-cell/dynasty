"""Authored species surfaces. Geometry remains cuboid; no foreign art is used."""
import math
from PIL import Image, ImageDraw

def finish(name, geo, image):
    from guardian_surfaces import IDS as guardian_ids, finish as guardian_finish
    if name in guardian_ids: return guardian_finish(name, geo, image)
    from woodland_surfaces import IDS as woodland_ids, finish as woodland_finish
    if name in woodland_ids: return woodland_finish(name, geo, image)
    if name != 'chimu_zhuha':
        from creature_surfaces import finish as finish_other
        return finish_other(name, geo, image)
    g=geo['minecraft:geometry'][0]; bones={b['name']:b for b in g['bones']}
    def shape(n, items):
        old=bones[n].get('cubes',[])
        bones[n]['cubes']=[dict(origin=o,size=s,uv=old[min(i,len(old)-1)]['uv']) for i,(o,s) in enumerate(items)]
    # Low continuous head and back; hind haunches carry the jumping mass.
    shape('body',[([-8,3.5,-6],[16,8.5,17]),([-7,11,-3],[14,1.5,12])])
    shape('head',[([-8,4.5,-12],[16,7,10]),([-8.5,7,-10],[17,3,7]),([-7,4,-13],[14,1.25,2])])
    shape('mouth_jaw',[([-7,2.75,-13],[14,1.5,10]),([-6,4,-13.1],[12,.375,.5])])
    for side,s in [('right',-1),('left',1)]:
        shape('eye_'+side,[([s*6-2,10,-10.5],[4,4,4]),([s*6-1.5,11,-11.25],[3,2.5,1])])
        shape(side+'_front_thigh',[([s*8-2,2.5,-6],[4,5.5,5])])
        shape(side+'_front_knee',[([s*10-1.5,1,-6],[3,3,4])])
        shape(side+'_front_foot',[([s*11-2,.125,-9],[4,1,5])])
        shape(side+'_hind_thigh',[([s*8-3.5,2.5,3],[7,7,9])])
        shape(side+'_hind_knee',[([s*11-2,1.25,6],[4,3.5,5])])
        shape(side+'_hind_foot',[([s*12-2.5,.125,2],[5,1.25,7])])
    for i in range(5):
        shape('tongue_'+str(i),[([-1,4.375,-14-i],[2,.5,1])])
    # Glands remain animated but read as skin nodules, not gold blocks.
    for i in range(8):
        x=-6+(i%4)*4;z=(i//4)*5
        shape('venom_gland_'+str(i),[([x-1,11.75,z-1],[2,1.25,2])])
    atlas=Image.new('RGB',(256,256),(51,39,34)); x=y=1;row=0
    skin=(117,64,47); dark=(78,49,40); light=(147,85,55)
    for b in g['bones']:
        n=b['name']
        for ci,c in enumerate(b.get('cubes',[])):
            sx,sy,sz=c['size']; uv={}
            for face,(a,bsize) in {'north':(sx,sy),'south':(sx,sy),'east':(sz,sy),'west':(sz,sy),'up':(sx,sz),'down':(sx,sz)}.items():
                w,h=max(1,math.ceil(a)),max(1,math.ceil(bsize))
                if x+w+1>256:x=1;y+=row+2;row=0
                assert y+h+1<=256
                tile=Image.new('RGB',(w,h),skin); px=tile.load()
                belly=n in ['belly','mouth_jaw','throat_sac']
                for v in range(h):
                    for u in range(w):
                        # Inherited world coordinates make neighboring back patches continuous.
                        ox,oy,oz=c['origin']
                        X=ox+(u+.5)*sx/w if face not in ['east','west'] else ox+(sx if face=='east' else 0)
                        Z=oz+(v+.5)*sz/h if face in ['up','down'] else oz+(u+.5)*sz/w if face in ['east','west'] else oz
                        Y=oy+sy-(v+.5)*sy/h
                        color=skin
                        if face=='down':color=dark
                        if face=='up':color=light if abs(X)<2 else skin
                        if belly:color=(180,146,99) if face!='down' else (135,108,76)
                        elif face in ['east','west','north','south'] and Y<5.5:color=(155,114,75)
                        if n in ['body','head'] or 'thigh' in n:
                            if face=='up' and 3<=abs(X)<=5 and int(Z+1)%9<6:color=dark
                            if face in ['east','west'] and Y>7 and int(Z)%9 in [0,1,2]:color=dark
                            if face=='up' and 2<abs(X)<6 and (int(Z)%9 in [5,6]) and int(abs(X))%3==0:color=light
                            if face in ['east','west'] and 5.5<Y<7:color=(137,82,53)
                        if n=='head' and face=='north':
                            if 6<Y<7 and abs(X)<6:color=(137,82,53)
                            if 7.5<Y<8.5 and 3<abs(X)<5:color=(62,40,33)
                            if 9<Y<10.5 and abs(X)>5:color=dark
                            if 5<Y<5.8:color=(82,49,37)
                        if n=='mouth_jaw' and face=='north' and ci==0:
                            color=(167,128,83) if v==0 else (188,154,108)
                        if n=='throat_sac' and face in ['north','east','west']:
                            color=(161,121,78) if v==h-1 else (186,151,100)
                        if 'gland' in n:color=light if face=='up' else skin
                        if 'tongue_' in n:color=(148,57,55) if face!='down' else (90,40,43)
                        if n=='mouth_jaw' and ci==1:color=(57,36,34)
                        if n.startswith('eye_'):
                            color=dark if ci==0 else (155,64,37)
                            if ci==1 and face=='north':
                                color=(195,86,41)
                                if v==0 or v==h-1:color=(78,42,32)
                                if u==w//2:color=(30,28,26)
                        px[u,v]=color
                atlas.paste(tile,(x,y));uv[face]={'uv':[x,y],'uv_size':[w,h]};x+=w+2;row=max(row,h)
            c['uv']=uv
    height=2**math.ceil(math.log2(y+row+2));atlas=atlas.crop((0,0,256,height))
    g['description'].update(texture_width=256,texture_height=height)
    return atlas
