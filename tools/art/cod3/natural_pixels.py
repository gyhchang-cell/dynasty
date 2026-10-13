"""Original NPC pixels: face-scale eyes, directional hair, seams, leather, wood and metal.

References are visual studies, never source pixels. Atlas packing reserves two
pixels around every island; all painting is integer rectangles without filters.
"""
import math
from PIL import Image, ImageDraw

SKINS = {'huang_laohan': ('#b98661','#936448','#d7ad80'),
         'ba_tu': ('#bf916b','#986848','#dbb289'),
         'hei_po': ('#c3a18a','#9c7f6a','#dfc0a4'),
         'xiaoyuanzi': ('#dfb997','#bf9478','#efd3b0'),
         'chu_nongyu': ('#ddbaa5','#b8917c','#efcfb6'),
         'hong_ling': ('#d7ae91','#b28370','#ebc9ae')}

def palette(role, cloth):
    skin, skin_dark, skin_light = SKINS.get(role, ('#cfa883','#ab8161','#e7c3a0'))
    base = tuple(int(cloth[i:i+2],16) for i in (1,3,5))
    # Discrete palette entries only: no interpolated/blurred shading in the PNG.
    shift = lambda delta: '#%02x%02x%02x' % tuple(max(0,min(255,c+delta)) for c in base)
    return dict(skin=skin,skin_dark=skin_dark,skin_light=skin_light,
                cloth=cloth,cloth_dark=shift(-18),cloth_light=shift(22),
                hair='#3b302a',hair_dark='#252423',hair_light='#5a493b',
                linen='#ded4b8',linen_dark='#aea48e',eye='#eee9da',iris='#3f5553',
                leather='#79563c',leather_dark='#4b382c',leather_light='#a28057',
                wood='#b48a52',wood_dark='#795a37',wood_light='#d4b17b',
                metal='#919fa5',metal_dark='#505e65',metal_light='#c4cdd0',
                brass='#b99853',brass_dark='#806839',brass_light='#ddc080')

def material(bone,index,old,role):
    if bone=='head':return 'face' if index==0 else 'skin'
    if bone=='hair':return 'hair'
    if bone in ('pack','basket','medicine_basket','straw_hat','pole','bamboo_pole','abacus','banner','zither','gourd','scroll','shovel','hammer','bow'):
        return 'wood' if old=='skin' else 'metal' if old=='light' else 'leather' if old=='dark' else 'cloth'
    if old=='skin':return 'skin'
    if old=='light':return 'metal' if role in ('han_chong','mo_jizi') or any(x in bone for x in ('sword','blade','claw','shovel')) else 'linen'
    if old=='dark':
        if bone=='hat' and role in ('yan_chifeng','huang_laohan'):return 'wood'
        if bone=='hat' or any(x in bone for x in ('braid','beard','bun')):return 'hair'
        if any(x in bone for x in ('foot','shin','thigh','wrist','waist','pelvis')):return 'leather'
        return 'metal' if role=='han_chong' else 'cloth_dark'
    return 'cloth'

def paint(role,key,w,h,p):
    mat,region,side=key
    if mat=='face':
        mat='hair' if side=='south' else 'skin'
    colors={'face':'skin','cloth_dark':'cloth_dark'}
    base=colors.get(mat,mat)
    tile=Image.new('RGB',(w,h),p[base]);d=ImageDraw.Draw(tile)
    def rect(x0,y0,x1,y1,col):
        x0=max(0,min(w-1,x0));x1=max(0,min(w-1,x1));y0=max(0,min(h-1,y0));y1=max(0,min(h-1,y1))
        if x0<=x1 and y0<=y1:d.rectangle((x0,y0,x1,y1),fill=p[col])
    if region=='head' and key[0]=='face':
        # 8x8 face proportions, with side/back hair and a clean forehead/hairline.
        if side=='north':
            rect(0,0,w-1,1,'hair');rect(0,2,0,3,'hair');rect(w-1,2,w-1,3,'hair')
            if role not in ('chu_nongyu','sai_banxian'):
                rect(1,4,2,4,'eye');rect(w-3,4,w-2,4,'eye')
                rect(2,4,2,4,'iris');rect(w-3,4,w-3,4,'iris')
                rect(1,3,2,3,'hair');rect(w-3,3,w-2,3,'hair')
            else:rect(0,3,w-1,4,'linen' if role=='chu_nongyu' else 'hair_dark')
            rect(3,5,4,5,'skin_dark');rect(3,6,4,6,'skin_dark')
            rect(1,5,1,6,'skin_light');rect(w-2,5,w-2,6,'skin_light')
            if role=='lao_chen':
                rect(1,4,2,4,'hair_dark');rect(1,6,w-2,7,'hair');rect(3,6,4,6,'skin_dark')
            if role=='han_chong':rect(1,5,1,6,'skin_dark')
            if role in ('hei_po','sai_banxian','huang_laohan'):
                rect(1,6,2,6,'skin_dark');rect(w-3,6,w-2,6,'skin_dark')
        elif side in ('east','west'):
            rect(0,0,w-1,1,'hair');rect(w-3,2,w-1,h-1,'hair');rect(2,4,2,5,'skin_dark')
        elif side=='up':rect(0,0,w-1,h-1,'hair')
        return tile
    if mat=='skin':
        if w>=3 and h>=3:rect(0,h-2,w-1,h-1,'skin_dark');rect(1,0,w-2,0,'skin_light')
    elif mat=='hair':
        if w>=3:rect(1,0,1,h-1,'hair_dark');rect(w-2,1,w-2,max(1,h-2),'hair_light')
        if role in ('hei_po','huang_laohan') and region in ('hair','braid','beard'):
            rect(0,0,w-1,h-1,'linen_dark');rect(1,0,max(1,w-2),h-1,'linen')
    elif mat.startswith('cloth'):
        dark='cloth_dark';light='cloth_light'
        rect(0,0,0,h-1,dark);rect(w-1,0,w-1,h-1,dark)
        if w>=4 and h>=4:rect(1,1,1,h-2,light)
        if region=='chest' and side=='north':
            # Folded collar descends toward the waist. Back does not repeat the collar.
            for y in range(min(4,h)):rect(min(w-2,1+y),y,min(w-2,2+y),y,'linen')
            rect(w//2,h-1,w//2,h-1,'brass')
        if 'forearm' in region:rect(0,h-2,w-1,h-1,'linen_dark')
        if region in ('pelvis','waist'):rect(0,h-1,w-1,h-1,'leather')
        if 'skirt' in region or region=='robe':
            rect(0,h-2,w-1,h-1,'cloth_dark')
            if w>=6:rect(w//2,1,w//2,h-3,'cloth_dark')
    elif mat in ('linen','leather','wood','metal','brass'):
        dark=mat+'_dark';light=mat+'_light' if mat!='linen' else 'linen'
        rect(0,h-1,w-1,h-1,dark)
        if w>=3:rect(1,0,w-2,0,light)
        if mat=='wood' and w>=4:rect(w//2,1,w//2,h-1,dark)
        if mat=='leather' and w>=4 and h>=4:rect(1,h//2,w-2,h//2,'leather_dark')
        if mat=='metal' and w>=5 and h>=5:rect(1,2,w-2,2,'metal_dark')
    return tile

def atlas(bones,materials,role,cloth):
    tiles={};requests=[];p=palette(role,cloth)
    for b in bones:
        for i,c in enumerate(b.get('cubes',[])):
            mat=material(b['name'],i,materials[b['name']][i],role)
            for face in c['uv']:
                a,z=c['size'][0],c['size'][2];height=c['size'][1]
                dims=(a,z) if face in ('up','down') else (z,height) if face in ('east','west') else (a,height)
                w,h=(max(1,min(16,math.ceil(v))) for v in dims)
                if mat=='face':w=h=8
                # Named face islands, directional trim and no averaged-color proxy.
                region=b['name'] if mat in ('face','cloth','cloth_dark','hair') else mat
                side=face if mat=='face' or region=='chest' else 'surface'
                key=(mat,region,side,w,h)
                tiles.setdefault(key,paint(role,key[:3],w,h,p));requests.append((c,face,key))
    size=128
    while True:
        im=Image.new('RGB',(size,size),'#292b2c');coords={};x=y=2;row=0
        for key,tile in tiles.items():
            w,h=tile.size
            if x+w+2>size:x=2;y+=row+4;row=0
            if y+h+2>size:break
            im.paste(tile,(x,y));coords[key]=(x,y);x+=w+4;row=max(row,h)
        else:break
        size*=2;assert size<=256
    # Extend edge pixels into the two-pixel gutter so ordinary mipmaps cannot sample another material.
    d=ImageDraw.Draw(im)
    for key,tile in tiles.items():
        x,y=coords[key];w,h=tile.size
        for xx in range(-2,w+2):
            for yy in range(-2,h+2):
                if xx<0 or xx>=w or yy<0 or yy>=h:
                    d.point((x+xx,y+yy),fill=tile.getpixel((max(0,min(w-1,xx)),max(0,min(h-1,yy)))))
    for c,face,key in requests:c['uv'][face]={'uv':list(coords[key]),'uv_size':list(tiles[key].size)}
    return im,{'atlas':size,'islands':len(tiles),'palette':len(im.getcolors(size*size)),'style':'original hard-edge face/cloth/leather/wood/metal pixels'}
