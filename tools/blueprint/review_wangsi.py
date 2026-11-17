#!/usr/bin/env python3
"""Production-cuboid connectivity, clipping, blade clearance and software plan review."""
import json,re,hashlib
from collections import deque
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from build_wangsi import ROOT,DOC,JAVA,W,H,D,outputs,AIR,WATER,CHAIN,IRON

def grid():
    source,manifest=outputs()
    assert JAVA.read_text()==source,'Generated Java differs from editable source'
    # Parse actual generated Java integer rows independently of geometry.json.
    rows=re.findall(r'\{(\d+,\d+,\d+,\d+,\d+,\d+,\d+)\}',JAVA.read_text())
    data=np.zeros((H,D,W),dtype=np.uint8)
    for row in rows:
        a,b,c,d,e,f,m=map(int,row.split(','));data[b:e+1,c:f+1,a:d+1]=m
    return data,manifest

def reachable(data,start):
    # Conservative full-block walking, 1-high risers, two-air-block head space.
    # Water, fences/chains, dynamic traps are not counted as walkable air.
    stand=(data[1:-1]==AIR)&(data[2:]==AIR)&~np.isin(data[:-2],[0,AIR,WATER,CHAIN,IRON])
    seen={start};q=deque([start])
    def valid(x,y,z):return 0<=x<W and 1<=y<H-1 and 0<=z<D and bool(stand[y-1,z,x])
    assert valid(*start),('Invalid route start',start)
    while q:
        x,y,z=q.popleft()
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            for dy in (0,1,-1):
                p=(x+dx,y+dy,z+dz)
                if p in seen or not valid(*p):continue
                # A step-up requires space above the original player's head.
                if dy==1 and data[y+2,z,x]!=AIR:continue
                if dy==-1 and data[y+1,z+dz,x+dx]!=AIR:continue
                seen.add(p);q.append(p)
    return seen

def render(data):
    colors=np.array([[30,33,40],[36,40,49],[71,77,82],[214,216,202],[91,66,48],
        [37,40,46],[117,49,54],[222,231,199],[48,93,111],[125,131,132],[141,146,143]],dtype=np.uint8)
    # Cut away cavern roof/walls, preserving actual architecture underneath.
    cut=data.copy();cut[34:]=0;cut[:,:,0:3]=0;cut[:,:,-3:]=0
    valid=~np.isin(cut,[0,AIR]);height=np.where(valid,np.arange(H)[:,None,None],-1).max(axis=0)
    top=np.take_along_axis(cut,np.maximum(height,0)[None],axis=0)[0]
    topcolors=colors[top].astype(float)*(0.6+np.maximum(height,0)[:,:,None]/65)
    plan=Image.fromarray(np.uint8(np.clip(topcolors,0,255))).resize((576,768),Image.Resampling.NEAREST)
    section=Image.fromarray(colors[data[:,:,48]][::-1]).resize((768,288),Image.Resampling.NEAREST)
    canvas=Image.new('RGB',(1400,850),(22,26,33));canvas.paste(plan,(20,56));canvas.paste(section,(620,56))
    d=ImageDraw.Draw(canvas);d.text((20,16),'WANGSI — PRODUCTION VOXELS / SOFTWARE CUTAWAY (NOT IN-GAME)',fill='white')
    for z,t in [(12,'ENTRY'),(38,'GHOST MARKET'),(73,'RIVER + ARCH'),(94,'GUILLOTINES'),(111,'COURT HALL'),(123,'DOCK')]:
        d.text((22,56+z*6),t,fill=(255,211,115))
    d.text((620,365),'x=48 longitudinal section | each pixel = one block',fill='white')
    d.text((620,395),'Bridge, reversible entrance stair, 3-wide guillotine aisle.',fill='white')
    canvas.save(DOC/'layout-review.png')
    # Isometric gray/material-colour review of the SAME exported occupied voxels.
    # Remove only enclosing cavern shell for this software cutaway, no scenic assets.
    iso=data.copy();iso[:11]=0;iso[35:]=0
    iso[:,:,0:3]=0;iso[:,:,-3:]=0;iso[:,:3,:]=0;iso[:,-3:,:]=0
    occupied=~np.isin(iso,[0,AIR])
    faces=[]
    for y,z,x in np.argwhere(occupied):
        for direction,dy,dz,dx in [('top',1,0,0),('west',0,0,-1),('north',0,-1,0)]:
            yy,zz,xx=y+dy,z+dz,x+dx
            if not (0<=yy<H and 0<=zz<D and 0<=xx<W) or not occupied[yy,zz,xx]:
                faces.append((x,z,y,direction,int(iso[y,z,x])))
    view=Image.new('RGB',(1200,880),(28,32,39));draw=ImageDraw.Draw(view)
    def project(x,y,z):return (int(650+(x-z)*4.2),int(805-(x+z)*2.1-y*6.2))
    for x,z,y,direction,palette in sorted(faces,key=lambda f:-(f[0]+f[1]-.6774*f[2])):
        if direction=='top':corners=[(x,y+1,z),(x+1,y+1,z),(x+1,y+1,z+1),(x,y+1,z+1)];shade=1.05
        elif direction=='west':corners=[(x,y,z),(x,y+1,z),(x,y+1,z+1),(x,y,z+1)];shade=.68
        else:corners=[(x,y,z),(x+1,y,z),(x+1,y+1,z),(x,y+1,z)];shade=.83
        color=tuple(int(min(255,c*shade)) for c in colors[palette])
        draw.polygon([project(*p) for p in corners],fill=color)
    draw.text((24,20),'WANGSI — ACTUAL EXPORTED VOXELS / CAVERN CUT AWAY',fill='white')
    draw.text((24,43),'Software geometry review. Not an in-game screenshot; textures and lighting not simulated.',fill=(191,199,207))
    view.save(DOC/'isometric-review.png')

def main():
    data,m=grid();seen=reachable(data,(48,41,3));checks=[]
    targets={'market':(48,13,43),'bridge':(48,17,75),'court':(48,17,101),'hall':(48,17,110),'dock':(48,17,123),'pump':(9,13,80)}
    for x,z in m['houses']:
        targets[f'house {x},{z}']=(x+6,13,z+6)
        targets[f'loft {x},{z}']=(x+6,19,z+6)
        targets[f'roof {x},{z}']=(x+6,26,z+6)
    for name,p in targets.items():checks.append({'name':name,'pass':p in seen,'position':p})
    for z in (92,96):
        checks.append({'name':f'blade {z} clear swept volume','pass':bool(np.all(data[17:20,z,47:50]==AIR))})
        checks.append({'name':f'blade {z} supported ceiling','pass':bool(np.all(data[21,z,47:50]!=AIR))})
    drained=data.copy();drained[6:9,94:100,14:17]=AIR
    drained[6:9,95,13]=AIR;drained[6:9,100,14:17]=AIR
    after=reachable(drained,(9,13,80))
    for p in [(11,6,95),(15,6,97),(15,6,106),(17,17,100),(24,17,101)]:
        checks.append({'name':f'drained shortcut {p}','pass':p in after})
    checks.append({'name':'exactly 54 isolated sump water cells','pass':int(np.count_nonzero(data[6:9,94:100,14:17]==WATER))==54})
    # Clipped column union, tested at positive and negative world origins.
    for ox,oz in [(0,0),(-112,-144),(1024,-2048)]:
        occupied=set()
        for cx in range(6):
            for cz in range(8):
                for x in range(cx*16,cx*16+16):
                    for z in range(cz*16,cz*16+16):occupied.add((ox+x,oz+z))
        checks.append({'name':f'48-column coverage {ox},{oz}','pass':len(occupied)==W*D})
    report={'java_executed':False,'gameplay_verified':False,'checks':checks,'walkable_reached':len(seen),'sha256':hashlib.sha256(JAVA.read_bytes()).hexdigest()}
    DOC.mkdir(parents=True,exist_ok=True);render(data)
    (DOC/'geometry-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    failed=[c for c in checks if not c['pass']]
    print(json.dumps({'checks':len(checks),'failed':failed,'walkable_reached':len(seen)},ensure_ascii=False))
    return 1 if failed else 0

if __name__=='__main__':raise SystemExit(main())
