#!/usr/bin/env python3
"""Offline vanilla HumanoidArmorModel chest-slot UV preview, not a game render.

Pillow is used only for rendering QA, never to author/modify the armor texture.
Geometry/UV definitions verified against local Forge 1.20.1-47.4.10 mapped
official sources: HumanoidModel, HumanoidArmorModel, HumanoidArmorLayer,
LayerDefinitions, ModelPart.Cube/Polygon, AnimationUtils, LivingEntityRenderer.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
JAR=Path('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar')
SOURCES={
 'HumanoidModel':'net/minecraft/client/model/HumanoidModel.java',
 'HumanoidArmorModel':'net/minecraft/client/model/HumanoidArmorModel.java',
 'HumanoidArmorLayer':'net/minecraft/client/renderer/entity/layers/HumanoidArmorLayer.java',
 'LayerDefinitions':'net/minecraft/client/model/geom/LayerDefinitions.java',
 'ModelPart':'net/minecraft/client/model/geom/ModelPart.java',
 'AnimationUtils':'net/minecraft/client/model/AnimationUtils.java',
 'LivingEntityRenderer':'net/minecraft/client/renderer/entity/LivingEntityRenderer.java',
}
NORMALS={'down':(0,-1,0),'up':(0,1,0),'west':(-1,0,0),'north':(0,0,-1),'east':(1,0,0),'south':(0,0,1)}

def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def normal(a):
    length=math.sqrt(dot(a,a))
    return tuple(v/length for v in a)

def transform(v,offset,angle=0,point=True):
    # Resting EMPTY arm bob at ageInTicks=0: right zRot=+.1, left=-.1.
    c,s=math.cos(angle),math.sin(angle)
    x,y,z=v[0]*c-v[1]*s,v[0]*s+v[1]*c,v[2]
    if point: x,y,z=x+offset[0],y+offset[1],z+offset[2]
    # LivingEntityRenderer applies scale(-1,-1,1); y now points upward.
    return (-x,-y,z)

def cube(offset_uv,start,size,deform,offset,mirror=False,angle=0,texture=None):
    """Direct transcription of ModelPart.Cube and Polygon UV assignment.

    Texture corners are assigned before mirrored vertex-order reversal.
    Mirror swaps min/max X AND flips X normal, exactly as vanilla does.
    """
    u,v=offset_uv
    w,h,d=size
    x0,y0,z0=[start[i]-deform for i in range(3)]
    x1,y1,z1=[start[i]+size[i]+deform for i in range(3)]
    if mirror: x0,x1=x1,x0
    vertices=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
              (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    f4,f5,f6,f7,f8,f9=u,u+d,u+d+w,u+d+w+w,u+d+w+d,u+d+w+d+w
    f10,f11,f12=v,v+d,v+d+h
    specs=[
        ('down',[5,4,0,1],(f5,f10,f6,f11)),
        ('up',[2,3,7,6],(f6,f11,f7,f10)),
        ('west',[0,4,7,3],(f4,f11,f5,f12)),
        ('north',[1,0,3,2],(f5,f11,f6,f12)),
        ('east',[5,1,2,6],(f6,f11,f8,f12)),
        ('south',[4,5,6,7],(f8,f11,f9,f12)),
    ]
    result=[]
    for name,indices,(u0,v0,u1,v1) in specs:
        uv=[(u1,v0),(u0,v0),(u0,v1),(u1,v1)]
        points=[(*transform(vertices[i],offset,angle),*t) for i,t in zip(indices,uv)]
        n=list(NORMALS[name])
        if mirror:
            points.reverse()
            n[0]*=-1
        n=transform(n,(0,0,0),angle,False)
        result.append((points,n,texture))
    return result

def scene(armor):
    neutral=Image.new('RGBA',(64,32),(130,134,137,255))
    parts=[
        # Only a neutral mannequin: no helmet, leggings, boots or item models.
        ((0,0),(-4,-8,-4),(8,8,8),(0,0,0),False,0),
        ((16,16),(-4,0,-2),(8,12,4),(0,0,0),False,0),
        ((40,16),(-3,-2,-2),(4,12,4),(-5,2,0),False,.1),
        ((40,16),(-1,-2,-2),(4,12,4),(5,2,0),True,-.1),
        ((0,16),(-2,0,-2),(4,12,4),(-1.9,12,0),False,0),
        ((0,16),(-2,0,-2),(4,12,4),(1.9,12,0),True,0),
    ]
    quads=[]
    for uv,start,size,offset,mirror,angle in parts:
        quads+=cube(uv,start,size,0,offset,mirror,angle,neutral)
    # CHEST slot visibility from HumanoidArmorLayer: body + both arms only.
    for uv,start,size,offset,mirror,angle in parts[1:4]:
        quads+=cube(uv,start,size,1.0,offset,mirror,angle,armor)
    return quads

def render(armor,eye,size=(180,220),scale=6):
    toward=normal(eye)
    right=normal(cross((0,1,0),toward))
    up=cross(toward,right)
    image=Image.new('RGBA',size,(0,0,0,0))
    pixels=image.load()
    depths=[-math.inf]*(size[0]*size[1])
    def project(p):
        centered=(p[0],p[1]+8,p[2])
        return (size[0]/2+scale*dot(centered,right),size[1]/2-scale*dot(centered,up),dot(centered,toward),p[3],p[4])
    for quad,n,texture in scene(armor):
        if dot(n,toward)<1e-9: continue
        vertices=[project(v) for v in quad]
        tex=texture.load()
        # Constant directional shade for readability; never baked into assets.
        shade=.80+.17*max(0,n[1])-.12*abs(n[0])-.18*max(0,-n[1])
        for ids in [(0,1,2),(0,2,3)]:
            a,b,c=[vertices[i] for i in ids]
            denom=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(denom)<1e-9: continue
            for y in range(max(0,math.floor(min(a[1],b[1],c[1]))),min(size[1]-1,math.ceil(max(a[1],b[1],c[1])))+1):
                for x in range(max(0,math.floor(min(a[0],b[0],c[0]))),min(size[0]-1,math.ceil(max(a[0],b[0],c[0])))+1):
                    px,py=x+.5,y+.5
                    wa=((b[1]-c[1])*(px-c[0])+(c[0]-b[0])*(py-c[1]))/denom
                    wb=((c[1]-a[1])*(px-c[0])+(a[0]-c[0])*(py-c[1]))/denom
                    wc=1-wa-wb
                    if min(wa,wb,wc)<-1e-8: continue
                    depth=wa*a[2]+wb*b[2]+wc*c[2]
                    pos=y*size[0]+x
                    if depth<depths[pos]-1e-7: continue
                    u=wa*a[3]+wb*b[3]+wc*c[3]
                    v=wa*a[4]+wb*b[4]+wc*c[4]
                    rgba=tex[max(0,min(63,math.floor(u))),max(0,min(31,math.floor(v)))]
                    # armorCutoutNoCull: tiny/partial-alpha edges are not blended.
                    if rgba[3]<26: continue
                    pixels[x,y]=tuple(round(value*shade) for value in rgba[:3])+(255,)
                    depths[pos]=depth
    return image

def font(size):
    return ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',size)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--before',type=Path,default=HERE/'dark_iron_layer_1_before.png')
    ap.add_argument('--candidate',type=Path,default=ROOT/'candidate/assets/dynasty/textures/models/armor/dark_iron_layer_1.png')
    args=ap.parse_args()
    before=Image.open(args.before).convert('RGBA')
    candidate=Image.open(args.candidate).convert('RGBA')
    assert before.size==candidate.size==(64,32),'Actual layer_1 must remain 64x32'
    views=[('FRONT',(0,0,-1)),('BACK',(0,0,1)),('THREE-QUARTER',(-1,.24,-1.6))]
    canvas=Image.new('RGB',(1176,1080),(238,237,230))
    d=ImageDraw.Draw(canvas)
    d.text((20,15),'DARK IRON CHESTPLATE | OFFLINE UV PREVIEW / NOT IN GAME',font=font(22),fill=(35,44,49))
    d.text((20,48),'Vanilla body + mirrored arms; 64x32 layer 1; standard 1.0 outer-armor deformation.',font=font(14),fill=(68,72,73))
    d.text((20,70),'Neutral mannequin. Empty hands. Native texels + nearest raster. No added shoulder geometry.',font=font(14),fill=(68,72,73))
    for row,(name,tex) in enumerate([('BEFORE',before),('CANDIDATE',candidate)]):
        for col,(view,eye) in enumerate(views):
            x,y=18+col*386,110+row*470
            d.text((x+10,y),f'{name} / {view}',font=font(17),fill=(38,44,49))
            rgba=render(tex,eye)
            rgba.save(HERE/f'chestplate_{name.lower()}_{view.lower()}.png')
            enlarged=rgba.resize((360,440),Image.Resampling.NEAREST)
            panel=Image.new('RGB',(360,440),(210,213,210))
            panel.paste(enlarged,(0,0),enlarged)
            canvas.paste(panel,(x+7,y+26))
    d.text((20,1058),'Verified from local Forge 1.20.1 sources. Orthographic QA only; game lighting/animation not tested.',font=font(13),fill=(60,68,72))
    canvas.save(HERE/'chestplate-worn-comparison.png')
    # Independently verify all pixels outside the actual chest/arm UV footprints.
    allowed=set()
    for uv,w,h,depth in [((16,16),8,12,4),((40,16),4,12,4)]:
        u,v=uv
        for x in range(u,u+2*depth+2*w):
            for y in range(v+depth,v+depth+h): allowed.add((x,y))
        for x in range(u+depth,u+depth+2*w):
            for y in range(v,v+depth): allowed.add((x,y))
    changed=[(x,y) for y in range(32) for x in range(64) if before.getpixel((x,y))!=candidate.getpixel((x,y))]
    outside=[p for p in changed if p not in allowed]
    report={
      'status':'offline only / not in game','source_jar':str(JAR),'source_classes':SOURCES,
      'sources_sha256':hashlib.sha256(JAR.read_bytes()).hexdigest(),
      'before':str(args.before),'candidate':str(args.candidate),'layer_size':[64,32],
      'visible_armor_parts':['body','right_arm','left_arm'],'deformation':1.0,
      'pose':'resting at ageInTicks=0: arm Z rotations +0.1 / -0.1 rad, no hand-held item',
      'mirror':'left_arm swaps X bounds, reverses polygon vertex order, flips X normal; shares right-arm UV',
      'body_uv':{'front':[20,20,28,32],'back':[32,20,40,32],'top':[20,16,28,20]},
      'arm_uv':{'front':[44,20,48,32],'back':[52,20,56,32],'top':[44,16,48,20]},
      'changed_pixel_count':len(changed),'changes_outside_chest_arm_uv':outside,
      'limitations':['offline orthographic raster','constant directional preview shading','no game/light/animation validation'],
    }
    (HERE/'chestplate-uv-qa.json').write_text(json.dumps(report,indent=2)+'\n')
    assert not outside,f'Candidate changes {len(outside)} pixels outside chest/arm UV footprint'
    print(json.dumps({'preview':str(HERE/'chestplate-worn-comparison.png'),'changed_pixels':len(changed),'outside_uv':len(outside)}))

if __name__=='__main__': main()
