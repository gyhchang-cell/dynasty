"""Compare native read-only use ray with camera-yaw and head-yaw geometry."""
from pathlib import Path
import json,math,sys

def ray(p,a,blocks,eye):
    yaw,pitch=map(math.radians,a);o=[p[0],p[1]+eye,p[2]]
    d=[-math.sin(yaw)*math.cos(pitch),-math.sin(pitch),math.cos(yaw)*math.cos(pitch)];best=None
    for b in blocks:
        near=-1e99;far=1e99;face=None
        for i in range(3):
            if abs(d[i])<1e-9:
                if o[i]<b[i] or o[i]>b[i]+1:far=-1e99
                continue
            q=(b[i]-o[i])/d[i];r=(b[i]+1-o[i])/d[i];enter=min(q,r)
            if enter>near:near=enter;face=[['west','east'],['down','up'],['north','south']][i][d[i]<0]
            far=min(far,max(q,r))
        if 0<=near<=far and near<4.5 and (best is None or near<best[0]):best=(near,b,face)
    return (best[1],best[2]) if best else (None,'')

if __name__=='__main__':
    p=Path(sys.argv[1]);n=0;camera=[];head=[]
    for l in p.read_text().splitlines():
        if ' FRAME ' not in l:continue
        t=float(l.split()[0]);d=json.loads(l.split(' FRAME ')[1]);expected=(d['logical'],d['logical_face']);n+=1
        if ray(d['p'],d['angle'],d['solid'],d.get('eyeHeight',1.62))!=expected:camera.append(t)
        if ray(d['p'],[d.get('headYaw',d['angle'][0]),d['angle'][1]],d['solid'],d.get('eyeHeight',1.62))!=expected:head.append(t)
    report={'log':str(p),'frames':n,'camera_yaw_mismatches':len(camera),'head_yaw_mismatches':len(head),'head_mismatch_times':head,'caveat':'Double-precision trigonometry; vanilla uses a float sine lookup. Full cubes only.'}
    print(json.dumps(report,ensure_ascii=False,indent=2))
