"""Read-only world snapshot and normalized delta extraction; never writes into saves."""
import gzip,json,hashlib,shutil,sys,struct,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'art'))
from read_build_world import chunks,blocks,stable
from audit_patrol_population import nbt
ROOT=Path(__file__).resolve().parents[2]
WORLD=Path('/Users/a15356015027/Public/.minecraft/versions/Dynasty 王朝/saves/新的世界')
OUT=ROOT/'build/player-city-20260926'
ORIGIN=(-80,-60,-96)
SIZE=176
def rotate(state,n,mirror=False):
    s={'Name':state['Name']}
    if 'Properties' in state:
        p=state['Properties'].copy()
        if p.get('facing') in ('north','east','south','west'):
            ring=['north','east','south','west'];p['facing']=ring[(ring.index(p['facing'])+n)%4]
            if mirror:p['facing']={'north':'south','south':'north'}.get(p['facing'],p['facing'])
        s['Properties']=p
    return s
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    snapshot=OUT/'original-save'
    if snapshot.exists():raise RuntimeError('Snapshot exists; do not replace baseline')
    manifest={}
    for src in WORLD.rglob('*'):
        if not src.is_file() or src.name=='session.lock':continue
        raw=stable(src);dst=snapshot/src.relative_to(WORLD);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw)
        manifest[str(src.relative_to(WORLD))]=hashlib.sha256(raw).hexdigest()
    (OUT/'snapshot-sha256.json').write_text(json.dumps(manifest,indent=2))
    baseline_path=ROOT/'src/main/resources/data/dynasty/structures/tiangong_citadel.nbt'
    shutil.copy2(baseline_path,OUT/'baseline-v8.nbt')
    t=nbt(gzip.decompress(baseline_path.read_bytes()));palette=t['palette']
    baseline={tuple(b['pos']):palette[b['state']] for b in t['blocks']}
    # Normalize 180-degree workshop copy back to blueprint coordinates.
    actual={};entities=[]
    for f in ['r.-1.-1.mca','r.-1.0.mca','r.0.-1.mca','r.0.0.mca']:
        for c in chunks((snapshot/'region'/f).read_bytes()):
            if not(-5<=c['xPos']<=5 and -6<=c['zPos']<=4):continue
            c['sections']=[s for s in c.get('sections',[]) if -4<=s['Y']<=-1]
            for (x,y,z),state in blocks(c):
                x-=ORIGIN[0];y-=ORIGIN[1];z-=ORIGIN[2]
                if 0<=x<SIZE and 0<=z<SIZE and 0<=y<56:
                    actual[(175-x,y,175-z)]=rotate(state,2)
            entities.extend(c.get('block_entities',[]))
    air={'Name':'minecraft:air'};edits={};counts=collections.Counter();matching=0;stairs=collections.Counter()
    for p,state in actual.items():
        base=baseline.get(p,air)
        # Existing piece mirrored stairs in world. Treat that bug as baseline, not a player edit.
        expected=rotate(base,0,True)
        if state==expected:matching+=state['Name']!='minecraft:air';continue
        if base['Name']=='minecraft:chest' and state['Name']=='lootr:lootr_chest':continue
        if state['Name'] in ('minecraft:exposed_cut_copper','minecraft:weathered_cut_copper','minecraft:oxidized_cut_copper') and base['Name']=='minecraft:cut_copper':continue
        edits[p]=state;counts[state['Name']]+=1
        if 'stairs' in state['Name']:stairs[json.dumps(state,sort_keys=True)]+=1
    # Compress vertical edits into z-runs with exact block states, including deletions.
    states=[];index={};runs=[]
    for x in range(SIZE):
        for y in range(56):
            z=0
            while z<SIZE:
                state=edits.get((x,y,z))
                if state is None:z+=1;continue
                key=json.dumps(state,sort_keys=True)
                if key not in index:index[key]=len(states);states.append(state)
                end=z+1
                while end<SIZE and edits.get((x,y,end))==state:end+=1
                runs.append([x,y,z,end-1,index[key]]);z=end
    report={'origin':ORIGIN,'rotation':2,'matchedNonAir':matching,'editCount':len(edits),'counts':dict(counts),'stairs':dict(stairs),'runs':len(runs)}
    (OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    raw=json.dumps({'palette':states,'runs':runs},separators=(',',':')).encode()
    (OUT/'player-edits.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
