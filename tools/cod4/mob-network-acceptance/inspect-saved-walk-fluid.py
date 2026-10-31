"""Read-only saved block context for a native walk; never opens Minecraft or changes a world."""
from pathlib import Path
import importlib.util,json,hashlib,zlib,gzip,math
R=Path(__file__).resolve().parents[3]
O=R/'docs/cod4/audit-20261022/mob-network-acceptance/run-12'
world=next((R/'build/cod4-mob-network-20261023/run-12/host/saves').glob('mob-qa-*'))
cache=R/'tools/cod4/mob-network-acceptance/.work/readonly-region-extract';cache.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('saved_nbt',R/'tools/cod4/ecology-acceptance/read_saved_nbt.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={};chunks={}
def block(x,y,z):
 cx,cz=x//16,z//16
 if (cx,cz) not in chunks:
  p=world/'region'/f'r.{cx//32}.{cz//32}.mca';b=p.read_bytes();inputs[str(p.relative_to(R))]=sha(p);idx=(cz%32)*32+cx%32;offset=int.from_bytes(b[idx*4:idx*4+3],'big')*4096;assert offset>0
  size=int.from_bytes(b[offset:offset+4],'big');compression=b[offset+4];assert not compression&128;raw=b[offset+5:offset+4+size];raw=zlib.decompress(raw) if compression==2 else gzip.decompress(raw) if compression==1 else raw if compression==3 else None;assert raw is not None
  extracted=cache/f'{cx}-{cz}.nbt';extracted.write_bytes(raw);chunks[cx,cz]=module.read_saved_nbt(extracted)
 n=chunks[cx,cz];sec=next(s for s in n['sections'] if s['Y']==y//16);states=sec['block_states'];palette=states['palette'];index=(y%16)*256+(z%16)*16+x%16
 if len(palette)==1:k=0
 else:
  bits=max(4,(len(palette)-1).bit_length());per=64//bits;value=states['data'][index//per]&((1<<64)-1);k=(value>>((index%per)*bits))&((1<<bits)-1)
 return palette[k]
case=json.loads((O/'result-001.json').read_text());rows=[]
for after in case['after']['players']:
 before=next(p for p in case['before']['players'] if p['uuid']==after['uuid']);vec=lambda p:[float(a) for a in p['pos'].strip('()').split(',')];a,b=vec(before),vec(after);x,y,z=map(math.floor,b)
 samples=[{'pos':[x,yy,z],'state':block(x,yy,z)} for yy in [y-1,y,y+1]]
 rows.append({'uuid':after['uuid'],'name':after['name'],'before':a,'after':b,'horizontal_distance':math.hypot(b[0]-a[0],b[2]-a[2]),'vertical_delta':b[1]-a[1],'onGround_raw':after['onGround'],'saved_blocks':samples,'saved_feet_block_is_water':samples[1]['state']['Name']=='minecraft:water'})
assert all(sha(R/p)==digest for p,digest in inputs.items()),'Private saved world changed during read-only audit'
report={'status':'READ_ONLY_SAVED_WATER_CONTEXT_CONFIRMED' if all(v['saved_feet_block_is_water'] for v in rows) else 'WATER_CONTEXT_NOT_CONFIRMED','case':'run-12/result-001.json','raw_QA_movement_assertions_pass':False,'world':str(world.relative_to(R)),'players':rows,'input_region_sha256':inputs,'all_input_region_hashes_unchanged':True,'game_clients_or_servers_started':0,'world_files_written':0,'scope':'Saved water blocks at exact native end coordinates, not a live isInWater telemetry claim; original movement predicate additionally required ground. Horizontal native movement is independent of vertical fall distance. No gameplay assertion silently replaced.'}
(O/'saved-water-context.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
