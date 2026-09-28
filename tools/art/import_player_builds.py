"""Convert a read-only snapshot delta into small reusable structure overrides."""
import json,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];SNAP=ROOT/'build/player-build-snapshot'
def state(v):
    props=v.get('Properties',{})
    return v['Name']+('['+','.join(k+'='+str(props[k]) for k in sorted(props))+']' if props else '')
def main():
    world={tuple(map(int,k.split(','))):v for k,v in json.loads((SNAP/'blocks.json').read_text()).items()}
    out=ROOT/'src/main/resources/data/dynasty/build_overrides';out.mkdir(parents=True,exist_ok=True)
    summary={}
    for name,x,y,z in [('academy',-415,64,30),('gate',-407,65,-93)]:
        path=SNAP/(name+'-baseline.json');baseline=json.loads(path.read_text());changes=[]
        # Include AIR changes (player removals), but never copy randomized chests or terrain.
        allowed={'minecraft:air','minecraft:light','minecraft:bookshelf','minecraft:glass_pane'}
        for key,old in baseline.items():
            a,b,c=map(int,key.split(','));new=state(world.get((x+a,y+b,z-c),{'Name':'minecraft:air'}))
            if old.split('[')[0]==new.split('[')[0] or new.startswith('lootr:') or 'chest' in new:continue
            if new.split('[')[0] not in allowed and not new.startswith('dynasty:'):continue
            if old.startswith('minecraft:air') and new.startswith('minecraft:air'):continue
            changes.append({'pos':[a,b,c],'before':old,'state':new})
        (out/(name+'.json')).write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')
        summary[name]={'origin':[x,y,z],'changes':len(changes),'kinds':dict(collections.Counter(c['state'].split('[')[0] for c in changes))}
    doc=ROOT/'docs/art/build-feedback-v5';doc.mkdir(parents=True,exist_ok=True)
    (doc/'player-build-delta.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()
