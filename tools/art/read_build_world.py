"""Read a stable byte snapshot of selected region files; NEVER write to a save."""
import gzip, hashlib, json, struct, zlib
from pathlib import Path
from audit_patrol_population import nbt
ROOT=Path(__file__).resolve().parents[2]
WORLD=Path('/Users/a15356015027/Public/.minecraft/versions/Dynasty 王朝/saves/新的世界')
OUT=ROOT/'build/player-build-snapshot'

def stable(path):
    for _ in range(5):
        a=path.read_bytes();b=path.read_bytes()
        if a==b:return a
    raise RuntimeError('Save is changing: '+str(path))

def chunks(data):
    for slot in range(1024):
        off=(int.from_bytes(data[slot*4:slot*4+4],'big')>>8)*4096
        if not off:continue
        length=int.from_bytes(data[off:off+4],'big');kind=data[off+4]
        raw=data[off+5:off+4+length]
        yield nbt(zlib.decompress(raw) if kind==2 else gzip.decompress(raw) if kind==1 else raw)

def blocks(chunk):
    for section in chunk.get('sections',[]):
        states=section.get('block_states',{});palette=states.get('palette',[])
        if not palette:continue
        bits=max(4,(len(palette)-1).bit_length());per=64//bits
        raw=states.get('data',b'');words=struct.unpack('>'+str(len(raw)//8)+'Q',raw) if raw else []
        for i in range(4096):
            index=((words[i//per]>>(i%per*bits))&((1<<bits)-1)) if words else 0
            state=palette[index]
            yield (chunk['xPos']*16+i%16,section['Y']*16+i//256,chunk['zPos']*16+(i//16)%16),state

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    report={};selected={}
    for file in ['r.-1.-1.mca','r.-1.0.mca']:
        raw=stable(WORLD/'region'/file);(OUT/file).write_bytes(raw)
        report[file]={'sha256':hashlib.sha256(raw).hexdigest(),'structures':[]}
        for c in chunks(raw):
            if -30<=c['xPos']<=-19 and -12<=c['zPos']<=6:
                for k,v in c.get('structures',{}).get('starts',{}).items():
                    if k.startswith('dynasty:') and v.get('id')!='INVALID':report[file]['structures'].append(v)
                for p,s in blocks(c):
                    if 40<=p[1]<=140 and s['Name'] not in ('minecraft:air','minecraft:cave_air','minecraft:void_air'):
                        selected[','.join(map(str,p))]=s
    raw=stable(WORLD/'level.dat');(OUT/'level.dat').write_bytes(raw)
    player=nbt(gzip.decompress(raw))['Data'].get('Player',{})
    report['player']={k:player.get(k) for k in ('Pos','Dimension')}
    (OUT/'blocks.json').write_text(json.dumps(selected,ensure_ascii=False))
    (OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=lambda v:'binary'))
    print('Snapshot:',OUT,'blocks:',len(selected),'player:',report['player'])
    for k,v in report.items():
        if k!='player':
            for s in v['structures']:print(s.get('id'),[(c.get('id'),c.get('BB')) for c in s.get('Children',[])])
if __name__=='__main__':main()
