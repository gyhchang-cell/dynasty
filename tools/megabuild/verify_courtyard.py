import sys,json,hashlib,zipfile,shutil
from collections import deque
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'art'))
from read_build_world import chunks,blocks,WORLD
from export_policy import release_mod
ROOT=Path(__file__).resolve().parents[2]
FULL='--full' in sys.argv
OUT=ROOT/('build/courtyard-full-completion' if FULL else 'build/courtyard-completion')
expected={tuple(map(int,k.split(','))):s for k,s in json.loads((OUT/'blocks.json').read_text()).items()}
actual={}
for f in (OUT/'world/region').glob('*.mca'):
    for c in chunks(f.read_bytes()):
        for p,s in blocks(c):
            if p in expected:actual[p]=s
assert actual==expected,'Serialized blocks differ from blueprint'
source=json.loads((ROOT/('build/courtyard-full-reference/source-hashes.json' if FULL else 'build/courtyard-reference/source-hashes.json')).read_text())
changed=[p for p,digest in source.items() if hashlib.sha256((WORLD/p).read_bytes()).hexdigest()!=digest]
print('Original save files changed since snapshot:',len(changed))
assert not changed,'Source world changed externally; recheck before claiming preservation'
passable=('air','grass','tall_grass','fern','large_fern','lily_pad','flower_pot','spore_blossom','vine','rose_bush','peony','lilac')
def name(p):return expected.get(p,{'Name':'minecraft:grass_block' if p[1]==-60 else 'minecraft:air'})['Name'].split(':')[1]
def free(p):
    v=name(p)
    return v in passable or v.endswith('_door') or v.endswith('_carpet') or v in ('lantern','wall_torch','torch')
def stand(p):
    x,y,z=p
    return free(p) and free((x,y+1,z)) and not free((x,y-1,z)) and name((x,y-1,z))!='water'
start=(390,-59,-132);q=deque([start]);seen={start}
while q:
    x,y,z=q.popleft()
    for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)]:
        for dy in (0,1,-1):
            p=(x+dx,y+dy,z+dz)
            inside=(259<=p[0]<=400 and -190<=p[2]<=-73) if FULL else (350<=p[0]<=391 and -155<=p[2]<=-109)
            if inside and -59<=p[1]<=-30 and p not in seen and stand(p):seen.add(p);q.append(p)
targets=[('main hall',280,-132),('central court',335,-132),('northeast study',365,-172),('north study',305,-161),('south tea hall',334,-93),('garden pavilion',302,-85)] if FULL else [('main hall',359,-132),('study',371,-147),('tea room',371,-117)]
for label,x,z in targets:
    assert any((x,y,z) in seen for y in range(-59,-50)),label+' not reachable'
    print('Reachable:',label)
for filename in ['dynasty-modpack-1.4.0.zip','dynasty-1.4.0.mrpack','dynasty-1.4.0-manual.zip']:
    with zipfile.ZipFile(ROOT/'dist'/filename) as archive:
        assert all(release_mod(p) for p in archive.namelist() if p.endswith('.jar'))
        if 'modrinth.index.json' in archive.namelist():
            assert all(release_mod(e['path']) for e in json.loads(archive.read('modrinth.index.json'))['files'])
    print('No workshop mods:',filename)
print('PASS:',len(actual),'exact serialized states; original untouched; routes and exports checked')
if '--install' in sys.argv:
    destination=WORLD.parent/('徽院全境-111x101独立版' if FULL else '徽院试建-独立存档')
    assert not destination.exists(),'Never overwrite an existing world'
    shutil.copytree(OUT/'world',destination)
    for p in (OUT/'world').rglob('*'):
        if p.is_file():assert p.read_bytes()==(destination/p.relative_to(OUT/'world')).read_bytes()
    print('INSTALLED NEW SAVE:',destination)
