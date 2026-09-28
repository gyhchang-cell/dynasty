"""Convert reviewed player edits into a compact reproducible resource."""
import gzip,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
data=json.loads(gzip.decompress((ROOT/'build/player-city-20260926/player-edits.json.gz').read_bytes()))
lines=[];counts={}
for x,y,z,end,i in data['runs']:
    state=data['palette'][i];name=state['Name']
    if name=='minecraft:light':
        assert state['Properties']['level']=='15'
        kind='LIGHT'
    elif name=='minecraft:oak_stairs':kind='STAIR_'+{'north':'N','east':'E','south':'S','west':'W'}[state['Properties']['facing']]
    elif name=='minecraft:smooth_stone':kind='FLOOR'
    else:continue # leaf distance and generated container orientation are not player edits
    lines.append(f'{x} {y} {z} {end} {kind}')
    counts[kind]=counts.get(kind,0)+end-z+1
dest=ROOT/'src/main/resources/data/dynasty/structure_edits/player_city_v9.tsv.gz'
dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_bytes(gzip.compress(('\n'.join(lines)+'\n').encode(),mtime=0))
print(counts)
