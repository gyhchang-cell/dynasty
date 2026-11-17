"""Species-specific sculpt/UV pass. No random noise or borrowed pixels."""
import math
from PIL import Image
IDS=('baimu_mowu','bishui_xuanjiao_youzi','qingtong_shuangtoushekui','xunshan_mujiaquan','bazu_digongzhu','mingsha_shixie','youdeng_guimianfu','xueju_mangguyu')

def shrink(c, factors, floor=False):
    old=c['size'][:];new=[round(a*b,4) for a,b in zip(old,factors)]
    c['origin']=[round(v+(a-b)/2,4) for v,a,b in zip(c['origin'],old,new)]
    if floor:c['origin'][1]-=(old[1]-new[1])/2
    c['size']=new;c.pop('inflate',None)

def forms(name,g):
    for b in g['bones']:
        n=b['name'];cs=b.get('cubes',[])
        if name=='baimu_mowu':
            if n.startswith('segment_'):
                # One armored tergite sits over the softer ventral strip.
                for j,c in enumerate(cs):
                    if j==1:shrink(c,[.94,.55,1.15])
                    if j==2:shrink(c,[.9,.55,1.05])
            elif '_leg_' in n:
                for c in cs:shrink(c,[1,.55,.65])
                if n.endswith('_foot'):
                    for c in cs:shrink(c,[.65,.65,.65],True)
            elif n.startswith('eye_'):
                for c in cs:
                    shrink(c,[.8,.5,.8]);c['origin'][1]=8.25
            elif n=='head':
                for c in cs:shrink(c,[.85,.85,1])
            elif 'jaw' in n:
                for c in cs:shrink(c,[.65,.7,1])
        elif name=='bishui_xuanjiao_youzi':
            if n.startswith('spine_'):
                for j,c in enumerate(cs):
                    if j==0:shrink(c,[1,1,1.15])
                    else:shrink(c,[.93,.55,1.1])
            elif n.startswith('fin_') and cs:
                for c in cs:shrink(c,[.35,.7,1.2],True)
            elif n=='head':
                for j,c in enumerate(cs):
                    if j in [2,3]:shrink(c,[.75,.6,.85])
            elif n=='jaw':
                for j,c in enumerate(cs):
                    if j:shrink(c,[.5,.6,.75])
            elif n.startswith('pectoral_'):
                for c in cs:shrink(c,[1,.4,1])
        elif name=='qingtong_shuangtoushekui':
            if n.startswith('joint_'):
                for j,c in enumerate(cs):
                    if j==0:shrink(c,[1,1,1.1])
                    if j==1:shrink(c,[.88,.6,1])
                    if j==2:shrink(c,[.85,.5,1.1])
                    if j==3:shrink(c,[.5,.4,.6])
            elif 'head' in n:
                for j,c in enumerate(cs):
                    if j==2:shrink(c,[.9,.7,1])
            elif 'horn' in n:
                for c in cs:shrink(c,[.7,.85,.8])
        elif name=='xunshan_mujiaquan':
            if n in ['chest','haunch']:
                for j,c in enumerate(cs):
                    if j==1:shrink(c,[.88,.55,.9])
            elif n=='waist':
                shrink(cs[0],[1.1,1.1,1.1])
            elif n=='head':
                shrink(cs[-1],[.82,.5,.82])
            elif n.startswith('leg_'):
                if len(cs)>1:shrink(cs[1],[.8,.65,.85])
            elif n.startswith('foot_'):
                for c in cs:shrink(c,[.9,.7,.8],True)
            elif n.startswith('ear_'):
                for c in cs:shrink(c,[.85,1,.6])
        elif name=='bazu_digongzhu':
            if n=='abdomen':
                if len(cs)>2:shrink(cs[2],[.88,.5,1])
            elif n=='boiler':
                if len(cs)>1:shrink(cs[1],[.9,.65,1])
            elif n.startswith('hip_'):
                for c in cs:shrink(c,[1,.7,.7])
            elif n.startswith('knee_'):
                for j,c in enumerate(cs):shrink(c,[.7 if j==0 else 1,.8,.65])
            elif n.startswith('drill_'):
                for j,c in enumerate(cs):shrink(c,[.7,.8 if j==0 else .6,.7],True)
            elif 'mandible' in n:
                for c in cs:shrink(c,[.65,.7,1])
        elif name=='mingsha_shixie':
            if n.startswith('tail_') and n!='tail_stinger':
                if len(cs)>1:shrink(cs[1],[.86,.5,1])
            elif n.startswith('shell_plate_'):
                shrink(cs[0],[.96,.5,1.1])
                if len(cs)>1:shrink(cs[1],[.65,.45,.8])
            elif n.endswith('_claw'):
                shrink(cs[0],[.9,.75,1.1]);shrink(cs[1],[.75,.5,1])
            elif 'pincer' in n:
                for c in cs:shrink(c,[.75,.7,1])
            elif n.startswith('leg_thigh_') or n.startswith('leg_shin_'):
                for c in cs:shrink(c,[1,.65,.7])
            elif n.startswith('leg_foot_'):
                for c in cs:shrink(c,[.7,.6,.7],True)
        elif name=='youdeng_guimianfu':
            if n=='head':
                shrink(cs[0],[.85,.9,1])
                for c in cs[2:4]:shrink(c,[.8,1,.7])
            elif n=='face':
                for c in cs[1:3]:shrink(c,[1,1,.5])
                shrink(cs[3],[.6,.65,.5])
            elif '_finger_' in n:
                for j,c in enumerate(cs):
                    if j==0:shrink(c,[1,.7,.6])
                    else:shrink(c,[1,1,.25])
            elif n.endswith('_wing'):
                for j,c in enumerate(cs):
                    if j==1:shrink(c,[1,1,.35])
        elif name=='xueju_mangguyu':
            if n.startswith('spine_') and n!='spine_0':
                shaft,rib,core=cs
                shrink(shaft,[.3,.3,1.05])
                x,y,z=rib['origin'];w,h,d=rib['size']
                # Actual open rib cage, not a painted dark box.
                def part(o,s):return dict(origin=o,size=s,uv=rib['uv'])
                b['cubes']=[shaft,part([x,y,z],[1,h,d]),part([x+w-1,y,z],[1,h,d]),part([x,y+h-1,z],[w,1,d]),core]
            elif n.startswith('dorsal_') or n.startswith('ribbon_'):
                for c in cs:shrink(c,[.35,1,1])
            elif 'fin' in n or n=='tail_tip':
                for c in cs:shrink(c,[.5 if n.startswith('tail') else 1,.5 if not n.startswith('tail') else 1,1])
    return g

# The painters deliberately use different anatomical coordinates and material rules.
def centipede(n,j,f,u,v,w,h,c):
    top=f=='up';bottom=f=='down';col=(62,75,53)
    if n.startswith('segment_'):
        i=int(n.split('_')[-1]);col=(69,86,58) if j==0 else (93,109,66) if j==1 else (47,54,39)
        if j==1:
            if top and v>=h-1:col=(48,61,41)
            if top and abs(u-(w-1)/2)<1:col=(124,131,77)
            if top and v in [1,2] and 1<u<w-2:col=(80,96,58)
        if j==0 and f in ['east','west'] and v>h*.6:col=(49,60,42)
    elif '_leg_' in n or 'antenna' in n:col=(126,103,61) if top else (88,77,48)
    elif 'jaw' in n:col=(49,44,36) if v>h/2 else (107,83,48)
    elif n.startswith('eye_'):col=(183,139,65) if top else (63,63,39)
    elif n=='head':
        col=(76,90,54)
        if j in [2,3]:col=(191,147,68) if f=='north' and u!=w//2 else (34,37,28)
        if j==4:col=(47,42,33)
        if j==0 and f=='north' and v<h/3:col=(52,65,41)
    return col

def serpent(n,j,f,u,v,w,h,c):
    if n.startswith('fin_') or 'pectoral' in n:
        return (59,102,100) if (u%3==0 if w>h else v%3==0) else (88,136,124)
    if 'horn' in n or 'whisker' in n:return (181,173,122) if f=='up' else (128,136,96)
    if n=='jaw':return (178,172,125) if j==0 else (211,202,157)
    if n=='head' and j in [4,5]:return (212,166,68) if f=='north' and u!=w//2 else (24,45,43)
    if n=='head' and j==6:return (35,61,57)
    if n.startswith('spine_') and j==1:return (149,164,117) if v>0 else (109,140,109)
    col=(48,106,96) if f=='up' else (57,119,104) if f!='down' else (105,142,111)
    if f in ['east','west'] and v>h*.65:col=(108,151,120)
    # Broken scale rows follow length, while the belly stays broad and clean.
    if f=='up' and v%4==3 and (u+(v//4)*2)%5<3:col=(35,83,79)
    if f in ['east','west'] and v<h*.6 and (u+v*2)%6 in [0,1]:col=(45,99,91)
    if n=='head' and f=='north' and j in [0,1] and v==h-1:col=(35,65,59)
    return col

def bronze(n,j,f,u,v,w,h,c):
    core=n.startswith('joint_') and j in [0,1]
    if core:
        col=(49,78,68) if j==0 else (36,54,48)
        if f=='up' and j==0 and v>=h-1:col=(77,103,80)
        return col
    col=(135,110,62) if f=='up' else (106,87,52)
    if n.startswith('joint_') and j==2:
        if f in ['north','south']:col=(75,71,48)
        if f=='up' and u==w//2 and v>0:col=(170,140,78)
    if 'nozzle' in n:return (38,52,43) if 0<u<w-1 else (129,109,60)
    if 'head' in n:
        col=(62,103,86) if j==0 else col
        if j in ([3,4] if n.startswith('front') else [4,5]):col=(200,160,72) if f in ['north','south'] and v==0 else (29,47,42)
        if j==0 and f in ['east','west'] and v>h*.6:col=(42,73,62)
    if 'jaw' in n:col=(54,70,56) if j==0 else (171,145,85)
    return col

def dog(n,j,f,u,v,w,h,c):
    wood=n in ['chest','haunch','neck','head','tail_tip'] and j==0 or n.startswith('leg_') and j==0 or n.startswith('foot_') and j==0 or n.startswith('ear_') and j==0
    if wood:
        col=(132,91,49) if f=='up' else (106,72,42)
        long_u=c['size'][2]>c['size'][1] if f in ['east','west'] else c['size'][0]>c['size'][1]
        cross=v if long_u else u;along=u if long_u else v
        if cross%5==2 and along>1:col=(83,57,36)
        if cross%5==3 and 2<along<max(w,h)-2:col=(146,101,53)
        return col
    if n=='head' and j in [3,4]:return (155,174,109) if f=='north' and u==w//2 else (35,47,39)
    if n=='head' and j==2:return (38,48,43)
    iron=n.startswith('knee_') or n in ['waist','jaw','jaw_piston'] or n.startswith('gear_') and j==0
    if iron:return (50,65,59) if f!='up' else (78,91,74)
    col=(156,121,62) if f=='up' else (117,91,48)
    if 'ear' in n:col=(58,66,47)
    if n=='head' and j==5 and f=='north' and u==w//2:col=(183,151,84)
    return col

def spider(n,j,f,u,v,w,h,c):
    wood=n=='abdomen' and j<2 or n.startswith('hip_') and j==1
    if wood:
        col=(104,71,43) if f!='down' else (65,50,36)
        if f in ['east','west'] and v%5==2 and u>1:col=(72,53,35)
        if f=='up' and u%5==2 and v>1:col=(135,91,49)
        return col
    dark=n.startswith('knee_') or n.startswith('drill_') or n in ['exhaust','piston'] and j==0
    if dark:return (57,67,62) if f!='up' else (89,100,84)
    col=(130,106,59) if f=='up' else (97,81,50)
    if n=='head' and j in [2,3]:return (184,145,63) if f=='north' and v==0 else (34,45,36)
    if n=='boiler' and j==2:return (43,57,48) if u%3!=0 else (100,110,79)
    if n=='abdomen' and j==2 and f=='up' and u in [2,w-3]:col=(169,137,74)
    if 'mandible' in n:col=(72,83,68) if f!='up' else (132,140,101)
    return col

def scorpion(n,j,f,u,v,w,h,c):
    col=(164,137,82) if f=='up' else (134,111,69) if f!='down' else (88,78,54)
    if 'leg_' in n:col=(117,100,64) if f!='down' else (78,73,53)
    if n.startswith('tail_') and f in ['east','west'] and v>h*.6:col=(107,94,63)
    if n.startswith('shell_plate_') and j==0:
        if f=='up' and v==h-1:col=(105,94,63)
        if f=='up' and abs(u-(w-1)/2)<2:col=(181,153,91)
        if f=='up' and 2<abs(u-(w-1)/2)<4 and v==h-1:col=(120,105,67)
    if 'pincer' in n and f in ['east','west']:col=(98,87,58) if u<w/3 else (168,147,91)
    if n=='carapace' and j in [3,4]:return (33,41,35)
    if n=='carapace' and j==1:return (83,80,57)
    if n.endswith('stinger') or 'sting' in n:return (64,67,48)
    return col

def bat(n,j,f,u,v,w,h,c):
    if 'finger' in n or n.endswith('_wing'):
        if j==0:return (50,47,57) if f!='up' else (80,70,80)
        col=(77,59,77)
        if v>=h-1:col=(53,45,59)
        if u<w*.35 and v<h*.5:col=(101,74,91)
        return col
    if n=='face':
        if j==0:
            if f=='north' and (u in [w//2-1,w//2]) and v>h//2:return (82,95,85)
            return (172,187,157) if v<h-1 else (124,145,124)
        if j in [1,2]:return (32,44,40) if u!=w//2 or v==0 else (136,161,110)
        return (80,103,84)
    if n=='flame':return (163,200,115) if v>h//2 else (106,166,105)
    if n=='lantern':
        if j==2:return (111,154,100) if f!='down' else (65,95,66)
        return (67,83,68) if f!='up' else (110,123,85)
    if n.endswith('_claw'):return (94,104,81)
    if n=='head' and j in [4,5]:return (115,88,102)
    col=(63,62,73) if f!='down' else (43,46,56)
    if n=='body' and j==1:col=(92,92,99)
    if f in ['north','south'] and v>h*.6 and u%3==1:col=(52,54,64)
    return col

def fish(n,j,f,u,v,w,h,c):
    if n.startswith('spine_') and n!='spine_0':
        if j==0:return (113,123,108) if f!='down' else (76,88,82)
        if j==4:return (132,64,65) if f=='up' else (83,47,51)
        return (177,179,144) if f=='up' else (139,150,125) if v>0 else (190,191,154)
    if n=='spine_0':
        if j==4:return (39,54,52)
        if j==7:return (114,59,61)
        col=(174,178,146) if f!='down' else (106,124,110)
        if j==0 and f in ['east','west'] and w*.25<u<w*.6 and h*.2<v<h*.6:col=(46,66,63)
        if j in [2,3] and f in ['east','west']:col=(89,110,96) if v>0 else (161,171,139)
        return col
    if n=='jaw':return (166,175,144) if j!=3 else (54,72,66)
    if 'dorsal' in n or 'ribbon' in n:return (132,73,74) if v<h/2 else (87,60,65)
    if 'fin' in n or n=='tail_tip':
        return (126,135,113) if (u%3==0 if w>h else v%3==0) else (74,95,87)
    return (141,156,126)

PAINTERS=dict(zip(IDS,[centipede,serpent,bronze,dog,spider,scorpion]))

PAINTERS.update(youdeng_guimianfu=bat,xueju_mangguyu=fish)

def finish(name,geo,image):
    if name not in IDS:return image
    g=forms(name,geo['minecraft:geometry'][0]); density=2 if name=='xunshan_mujiaquan' else 1
    faces=[]
    for b in g['bones']:
        for j,c in enumerate(b.get('cubes',[])):
            sx,sy,sz=c['size'];c['uv']={}
            for f,(a,z) in {'north':(sx,sy),'south':(sx,sy),'east':(sz,sy),'west':(sz,sy),'up':(sx,sz),'down':(sx,sz)}.items():
                w,h=max(1,math.ceil(a*density)),max(1,math.ceil(z*density));faces.append((h,w,b['name'],j,c,f))
    faces.sort(key=lambda v:(-v[0],-v[1]));width=256;atlas=Image.new('RGB',(width,1024),(31,35,29));x=y=1;row=0
    for h,w,n,j,c,f in faces:
        if x+w+1>width:x=1;y+=row+2;row=0
        tile=Image.new('RGB',(w,h));tile.putdata([PAINTERS[name](n,j,f,u,v,w,h,c) for v in range(h) for u in range(w)])
        atlas.paste(tile,(x,y));c['uv'][f]={'uv':[x,y],'uv_size':[w,h]};x+=w+2;row=max(row,h)
    height=2**math.ceil(math.log2(y+row+2));assert height<=1024
    atlas=atlas.crop((0,0,width,height));g['description'].update(texture_width=width,texture_height=height)
    return atlas
