"""Source-derived offline face/edge audit. Never changes production artwork."""
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import subprocess
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont

D=Path(__file__).resolve().parent
R=D.parents[2]
A=R/'src/main/resources/assets/dynasty'
JAR=Path('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar')
SOURCES={
 'HumanoidModel':('net/minecraft/client/model/HumanoidModel.java',[59,69]),
 'HumanoidArmorModel':('net/minecraft/client/model/HumanoidArmorModel.java',[19,24]),
 'ModelPart':('net/minecraft/client/model/geom/ModelPart.java',[212,329]),
 'LayerDefinitions':('net/minecraft/client/model/geom/LayerDefinitions.java',[111,119]),
 'HumanoidArmorLayer':('net/minecraft/client/renderer/entity/layers/HumanoidArmorLayer.java',[81,101,129,134,161,180]),
}
NORMALS={'DOWN':(0,-1,0),'UP':(0,1,0),'WEST':(-1,0,0),'NORTH':(0,0,-1),'EAST':(1,0,0),'SOUTH':(0,0,1)}
# Model Y increases downward. DOWN is min-Y (the physical top) before render scale.
# Only these actual cube definitions are used; no model is added to the game.
PARTS={
 'head':((0,0),(8,8,8),False),
 'hat':((32,0),(8,8,8),False),
 'body':((16,16),(8,12,4),False),
 'right_arm':((40,16),(4,12,4),False),
 'left_arm':((40,16),(4,12,4),True),
 'right_leg':((0,16),(4,12,4),False),
 'left_leg':((0,16),(4,12,4),True),
}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,data): (D/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def cube_faces(part):
    (u,v),(w,h,d),mirror=PARTS[part]
    x0,x1=(w,0) if mirror else (0,w)
    vertices=[(x0,0,0),(x1,0,0),(x1,h,0),(x0,h,0),(x0,0,d),(x1,0,d),(x1,h,d),(x0,h,d)]
    f4,f5,f6,f7,f8,f9=u,u+d,u+d+w,u+d+2*w,u+2*d+w,u+2*d+2*w
    f10,f11,f12=v,v+d,v+d+h
    specs=[('DOWN',[5,4,0,1],(f5,f10,f6,f11)),('UP',[2,3,7,6],(f6,f11,f7,f10)),('WEST',[0,4,7,3],(f4,f11,f5,f12)),('NORTH',[1,0,3,2],(f5,f11,f6,f12)),('EAST',[5,1,2,6],(f6,f11,f8,f12)),('SOUTH',[4,5,6,7],(f8,f11,f9,f12))]
    out=[]
    for name,ids,rect in specs:
        u0,v0,u1,v1=rect
        uv=[(u1,v0),(u0,v0),(u0,v1),(u1,v1)]
        points=[vertices[i] for i in ids]
        normal=list(NORMALS[name])
        if mirror: points.reverse();uv.reverse();normal[0]*=-1
        a=[points[1][i]-points[0][i] for i in range(3)]
        b=[points[2][i]-points[1][i] for i in range(3)]
        cross=(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
        assert sum(cross[i]*normal[i] for i in range(3))>0,'Wrong winding or mirrored normal'
        out.append({'direction':name,'normal':normal,'xyz':points,'uv':uv,'rect':rect,'mirror':mirror})
    return out

def face_edges(faces):
    edges=defaultdict(list)
    for f in faces:
        for i in range(4):
            p,q=f['xyz'][i],f['xyz'][(i+1)%4]
            a,b=f['uv'][i],f['uv'][(i+1)%4]
            if p>q:p,q,a,b=q,p,b,a
            edges[(p,q)].append((f,a,b))
    assert len(edges)==12 and all(len(v)==2 for v in edges.values())
    return edges

def inside_samples(image,f,a,b):
    # Exact texel-center samples one half texel inside either face; not exterior padding.
    length=int(round(math.dist(a,b)))
    cx=sum(v[0] for v in f['uv'])/4
    cy=sum(v[1] for v in f['uv'])/4
    mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
    delta=(cx-mid[0],cy-mid[1]);norm=math.hypot(*delta)
    offset=tuple(v/norm*.5 for v in delta)
    pts=[];pixels=[]
    for n in range(length):
        t=(n+.5)/length
        p=(math.floor(a[0]+(b[0]-a[0])*t+offset[0]),math.floor(a[1]+(b[1]-a[1])*t+offset[1]))
        assert 0<=p[0]<64 and 0<=p[1]<32
        pts.append(p);pixels.append(image.getpixel(p))
    return pts,pixels

def main():
    D.mkdir(parents=True,exist_ok=True)
    paths=sorted((A/'textures/models/armor').glob('*.png'))
    assert len(paths)==56
    subprocess.run([sys.executable,str(R/'tools/art/snapshot_texture_requirements.py'),'--batch-dir',str(D),'--targets',*[f'dynasty:textures/models/armor/{p.name}' for p in paths],'--application','只读检查56张穿戴贴图的实际HumanoidArmorModel面/镜像/边对应与朝向；保护全部112库存图标及生产模型，不改PNG、Java、人物、实例、共享Jar或清单；离线面检查不等同实机验收。'],check=True,capture_output=True)
    source_records={}
    with zipfile.ZipFile(JAR) as z:
        source_text={k:z.read(e).decode() for k,(e,_) in SOURCES.items()}
        for k,(e,lines) in SOURCES.items():
            source_records[k]={'jar':str(JAR),'entry':e,'sha256':hashlib.sha256(z.read(e)).hexdigest(),'inspected_lines':lines}
    assert 'texOffs(40, 16).mirror()' in source_text['HumanoidModel']
    assert 'texOffs(0, 16).mirror()' in source_text['HumanoidArmorModel']
    assert 'new CubeDeformation(1.0F)' in source_text['LayerDefinitions']
    assert 'new CubeDeformation(0.5F)' in source_text['LayerDefinitions']
    assert 'case HEAD:' in source_text['HumanoidArmorLayer'] and '.hat.visible = true' in source_text['HumanoidArmorLayer']
    contract={'version':'Minecraft 1.20.1 / Forge 47.4.10 mapped official','sources':source_records,'jar_sha256':sha(JAR),'coordinates':'Undeformed cuboid-local coordinates express UV topology only, not world positions. Model +Y points down, front is NORTH/minZ; renderer scale(-1,-1,1) changes world interpretation. DOWN face is minY/top; UP is maxY/bottom.','parts':{p:{'offset':v[0],'size':v[1],'mirrored':v[2],'faces':cube_faces(p)} for p,v in PARTS.items()},'slot_parts':{'HEAD':['head','hat'],'CHEST':['body','right_arm','left_arm'],'FEET':['right_leg','left_leg'],'LEGS':['body','right_leg','left_leg']},'layer_for_slot':{'HEAD':1,'CHEST':1,'FEET':1,'LEGS':2},'deformation':{'outer':1.0,'inner':.5,'leg_addition':-.1,'hat_addition':.5},'left_parts_share_uv':True,'winding_normals_verified':True,'limits':['No game renderer executed; source-derived coordinate correspondence only.','Joint gaps, deformed geometry intersections and posed animation are not covered by local UV topology.','Third-party client extensions/resource-pack overrides not tested.']}
    save('uv-contract.json',contract)
    baseline=json.loads((R/'docs/art/armor-continuation-20261102/source-baseline.json').read_text())
    for p in ['src/main/java/com/dynasty/DynastyGear.java','src/main/java/com/dynasty/DynastyArmorMaterials.java']:
        baseline[p]=sha(R/p)
    handoff=R/'docs/cod4/audit-20261022/attachment-interface-handoff-20261102.json'
    handoff_data=json.loads(handoff.read_text())
    baseline[str(handoff.relative_to(R))]=sha(handoff)
    for row in handoff_data['entries']:
        for p,h in row['inputs'].items():
            assert sha(R/p)==h,'Attachment changed since handoff; do not assume an old interface'
            baseline[p]=h
    target=D/'source-baseline.json'
    if target.exists():assert json.loads(target.read_text())==baseline,'Refuse to reset existing batch baseline'
    else:save('source-baseline.json',baseline)
    entries=[];all_seams=[];errors=[]
    for path in paths:
        im=Image.open(path).convert('RGBA');assert im.size==(64,32)
        layer=int(path.stem[-1]);material=path.stem.removesuffix(f'_layer_{layer}')
        part_names=list(PARTS) if layer==1 else ['body','right_leg','left_leg']
        row={'material':material,'layer':layer,'path':str(path.relative_to(R)),'sha256':sha(path),'parts':[]}
        for part in part_names:
            faces=cube_faces(part);stats=[]
            for f in faces:
                rect=f['rect'];box=(min(rect[0],rect[2]),min(rect[1],rect[3]),max(rect[0],rect[2]),max(rect[1],rect[3]))
                if not(0<=box[0]<box[2]<=64 and 0<=box[1]<box[3]<=32):errors.append((material,layer,part,f['direction'],'UV_OUT_OF_BOUNDS'))
                pixels=list(im.crop(box).get_flattened_data());visible=[p for p in pixels if p[3]>=26]
                stats.append({'direction':f['direction'],'normal':f['normal'],'uv_corners':f['uv'],'model_corners':f['xyz'],'crop':box,'visible_pixels':len(visible),'total_pixels':len(pixels),'color_count':len({p[:3] for p in visible}),'fully_transparent':not visible})
            seams=[]
            for n,(edge,pair) in enumerate(face_edges(faces).items()):
                a,b=pair;pa,ca=inside_samples(im,*a);pb,cb=inside_samples(im,*b)
                assert len(ca)==len(cb)
                alpha_diff=sum((x[3]>=26)!=(y[3]>=26) for x,y in zip(ca,cb))
                visible_pairs=[(x,y) for x,y in zip(ca,cb) if x[3]>=26 and y[3]>=26]
                max_delta=max([max(abs(x[k]-y[k]) for k in range(3)) for x,y in visible_pairs],default=0)
                seam={'key':f'{material}/L{layer}/{part}/edge{n:02}','part':part,'layer':layer,'material':material,'xyz_endpoints':edge,'face_a':a[0]['direction'],'face_b':b[0]['direction'],'texels_a':pa,'texels_b':pb,'rgba_a':ca,'rgba_b':cb,'length':len(ca),'alpha_disagreement':alpha_diff,'both_visible':len(visible_pairs),'max_rgb_delta':max_delta,'interpretation':'Review signal only; material shading/cutout borders can legitimately differ. Not an automatic seam failure.'}
                seams.append(seam);all_seams.append(seam)
            row['parts'].append({'part':part,'mirrored':PARTS[part][2],'faces':stats,'seams':seams})
        entries.append(row)
    save('face-and-seam-inventory.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'entries':entries,'face_count':sum(len(p['faces']) for r in entries for p in r['parts']),'seam_pair_count':len(all_seams),'errors':errors,'game_acceptance':False,'note':'Mirrored parts remain separate geometry faces but are not independent source design references.'})
    draw_faces(entries)
    draw_seams(all_seams)
    draw_mirrors(entries)
    draw_icon_match(entries)
    summary={'source_png':len(paths),'geometry_face_instances':sum(len(p['faces']) for r in entries for p in r['parts']),'geometry_edge_pairs':len(all_seams),'bounds_errors':len(errors),'face_pages':14,'seam_pages':7,'game_starts':0,'production_mutations':0,'checklist_deletions':0}
    save('generated-evidence.json',summary);print(json.dumps(summary))
    assert not errors

def front_in_model_xy(image,part):
    f=next(f for f in cube_faces(part) if f['direction']=='NORTH')
    w,h,_=PARTS[part][1];out=Image.new('RGBA',(w,h))
    p0,p1,p3=f['xyz'][0],f['xyz'][1],f['xyz'][3]
    uv0,uv1,uv3=f['uv'][0],f['uv'][1],f['uv'][3]
    ax,ay=p1[0]-p0[0],p1[1]-p0[1]
    bx,by=p3[0]-p0[0],p3[1]-p0[1];det=ax*by-ay*bx
    for y in range(h):
        for x in range(w):
            qx,qy=x+.5-p0[0],y+.5-p0[1]
            s=(qx*by-qy*bx)/det;t=(ax*qy-ay*qx)/det
            u=uv0[0]+s*(uv1[0]-uv0[0])+t*(uv3[0]-uv0[0])
            v=uv0[1]+s*(uv1[1]-uv0[1])+t*(uv3[1]-uv0[1])
            out.putpixel((x,y),image.getpixel((math.floor(u),math.floor(v))))
    return out

def draw_mirrors(entries):
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',14)
    mats=sorted({r['material'] for r in entries});checks=[]
    for page,start in enumerate(range(0,len(mats),7),1):
        selected=mats[start:start+7];im=Image.new('RGB',(1080,85+len(selected)*110),(68,73,78));d=ImageDraw.Draw(im)
        d.text((8,8),'NORTH FACES in increasing local X / mirrored left UV from actual corners / NOT GAME',font=font,fill='white')
        labels=['R arm L1','L arm L1','R boot L1','L boot L1','R leg L2','L leg L2']
        for j,s in enumerate(labels):d.text((210+j*140,40),s,font=font,fill='white')
        for i,mat in enumerate(selected):
            y=75+i*110;d.text((8,y+20),mat,font=font,fill='white')
            for pair,(layer,stem) in enumerate([(1,'arm'),(1,'leg'),(2,'leg')]):
                row=next(r for r in entries if r['material']==mat and r['layer']==layer)
                tex=Image.open(R/row['path']).convert('RGBA')
                right=front_in_model_xy(tex,'right_'+stem);left=front_in_model_xy(tex,'left_'+stem)
                equal=left.tobytes()==right.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes();assert equal
                checks.append({'material':mat,'layer':layer,'part_pair':stem,'north_faces_exact_horizontal_mirror':equal})
                for side,crop in enumerate([right,left]):
                    crop=crop.resize((crop.width*6,crop.height*6),Image.Resampling.NEAREST);im.paste(crop,(210+(pair*2+side)*140,y),crop)
        im.save(D/f'mirrors-{page:02}.png')
    save('mirror-correspondence.json',{'checks':checks,'count':len(checks),'status':'PASS_SOURCE_DERIVED_NORTH_FACE_MIRROR','limits':'Exact local UV correspondence, not posed wrist/leg or world rendering acceptance.'})

def draw_icon_match(entries):
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',15)
    sets=['bamboo','brocade','cinnabar','qilin','hongmeng','ziwei','beidou','hunyuan','qinglong','zhuque','xuanwu','baihu','tiangang']
    for page,start in enumerate(range(0,len(sets),5),1):
        chosen=sets[start:start+5];im=Image.new('RGB',(1160,55+len(chosen)*170),(68,73,78));d=ImageDraw.Draw(im)
        d.text((8,8),'CURRENT APPROVED ICONS vs CURRENT WORN SOURCE FACES / thumbnails only / NOT GAME',font=font,fill='white')
        for i,s in enumerate(chosen):
            y=48+i*170;d.text((8,y+10),s,font=font,fill='white')
            for j,slot in enumerate(['helmet','chestplate','leggings','boots']):
                a=Image.open(A/f'textures/item/{s}_{slot}.png').convert('RGBA');a.thumbnail((128,128),Image.Resampling.NEAREST)
                im.paste(a,(130+j*145,y),a);d.text((130+j*145,y+136),slot,font=font,fill='white')
            for j,(layer,box) in enumerate([(1,(8,8,16,16)),(1,(20,20,28,32)),(2,(4,20,8,32)),(1,(4,20,8,32))]):
                a=Image.open(A/f'textures/models/armor/{s}_layer_{layer}.png').convert('RGBA').crop(box)
                a=a.resize((a.width*8,a.height*8),Image.Resampling.NEAREST);im.paste(a,(730+j*100,y),a)
                d.text((730+j*100,y+136),['head','chest','pants','boots'][j],font=font,fill='white')
        im.save(D/f'approved-icon-worn-match-{page:02}.png')

def draw_faces(entries):
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',15)
    little=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',12)
    mats=sorted({r['material'] for r in entries});order=['DOWN','NORTH','WEST','EAST','SOUTH','UP']
    # Raw source crops show exact texels, with normals/UV corners in the JSON.
    for page,start in enumerate(range(0,len(mats),2),1):
        canvas=Image.new('RGB',(1040,1660),(68,73,78));d=ImageDraw.Draw(canvas)
        d.text((10,8),'SOURCE FACE CROPS x6 / model Y down / NOT GAME / cap labels = ModelPart directions',font=font,fill='white')
        for k,mat in enumerate(mats[start:start+2]):
            y0=40+k*805;d.text((10,y0),mat,font=font,fill='#ffe4a6')
            for j,direction in enumerate(order):d.text((240+j*128,y0),direction,font=font,fill='white')
            display=[(1,p) for p in ['head','hat','body','right_arm','right_leg']]+[(2,'body'),(2,'right_leg')]
            for i,(layer,part) in enumerate(display):
                row=next(r for r in entries if r['material']==mat and r['layer']==layer)
                p=next(p for p in row['parts'] if p['part']==part);im=Image.open(R/row['path']).convert('RGBA');y=y0+28+i*108
                d.text((10,y+16),f'L{layer} {part}',font=font,fill='white')
                for j,dr in enumerate(order):
                    f=next(f for f in p['faces'] if f['direction']==dr);crop=im.crop(f['crop']);big=crop.resize((crop.width*6,crop.height*6),Image.Resampling.NEAREST)
                    x=240+j*128;canvas.paste(big,(x,y),big)
                    d.text((x,y+76),f"{f['visible_pixels']}/{f['total_pixels']} alpha",font=little,fill='#cfdbdf')
        canvas.save(D/f'faces-{page:02}.png')

def draw_seams(seams):
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',13)
    mats=sorted({s['material'] for s in seams})
    # For each set: select the two largest RGB and two largest alpha signals.
    selected=[]
    for mat in mats:
        local=[s for s in seams if s['material']==mat and not s['part'].startswith('left') and s['part']!='hat']
        color=sorted(local,key=lambda s:(s['max_rgb_delta'],s['both_visible']),reverse=True)[:2]
        alpha=sorted(local,key=lambda s:(s['alpha_disagreement']/s['length'],s['alpha_disagreement']),reverse=True)[:2]
        selected.extend({s['key']:s for s in color+alpha}.values())
    save('seam-review-selection.json',{'policy':'Per material: top two RGB and top two alpha-disagreement signals; dedup exact edge keys. These are inspection prompts, not automatically defects.','seams':selected})
    for page,start in enumerate(range(0,len(mats),4),1):
        sub=mats[start:start+4];rows=[s for s in selected if s['material'] in sub]
        im=Image.new('RGB',(1040,50+len(rows)*66),(68,73,78));d=ImageDraw.Draw(im)
        d.text((10,8),'CORRESPONDING SURFACE EDGES / exact RGBA source / colors may differ legitimately / NOT GAME',font=font,fill='white')
        for i,s in enumerate(rows):
            y=40+i*66;d.text((8,y),s['key'],font=font,fill='white');d.text((8,y+19),f"{s['face_a']} / {s['face_b']} alpha diff {s['alpha_disagreement']} RGB max {s['max_rgb_delta']}",font=font,fill='#cfdbdf')
            for j,pix in enumerate([s['rgba_a'],s['rgba_b']]):
                strip=Image.new('RGBA',(len(pix),1));strip.putdata([tuple(c) for c in pix]);strip=strip.resize((len(pix)*16,16),Image.Resampling.NEAREST)
                im.paste(strip,(690,y+j*20),strip)
        im.save(D/f'seams-{page:02}.png')

if __name__=='__main__':main()
