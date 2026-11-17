from pathlib import Path
import json,hashlib,sys,statistics
R=Path(__file__).resolve().parents[3]; O=R/'docs/cod4/audit-20261022/weapon-visual-acceptance'/sys.argv[1]
out=[]
for p in sorted(O.glob('*-result.json')):
 name=p.name[:-12];c=json.loads((O/(name+'-command.json')).read_text());fs=json.loads((O/(name+'-frames.json')).read_text());es=json.loads((O/(name+'-events.json')).read_text())
 wires=[e['data'] for e in es if e['kind']=='actual-s2c-handle'];damage=[e['data'] for e in es if e['kind']=='native-server-damage'];shots=[]
 for idx,f in enumerate(fs):
  if 'screenshot' not in f:continue
  im=O/f['screenshot']
  shots.append(dict(file=f['screenshot'],sha256=hashlib.sha256(im.read_bytes()).hexdigest(),frame_index=idx,frameSerial=f['frameSerial'],tick=f['tick'],partialTick=f['partialTick'],geometry_counts={k:len(v) for k,v in f['geometry'].items()},afterimages=len(f['afterimages'])))
 intervals=[f['frameIntervalMs'] for f in fs[1:] if f['frameIntervalMs']>0]
 counts={k:max(len(f['geometry'].get(k,[])) for f in fs) for f in fs for k in f['geometry']}
 r=dict(case=name,configuration=c,actual_server_attacks=sum(e['kind']=='native-server-attack' for e in es),actual_damage=[dict(tick=d['tick'],amount=d['amount'],source=d['source'],weapon=d['originalWeapon'],target=d['target']['type']) for d in damage],wire_sequences=sorted({w['sequence'] for w in wires}),geometry_max_counts=counts,ghost_frame_count=sum(bool(f['afterimages']) for f in fs),frame_interval_ms=dict(median=statistics.median(intervals) if intervals else 0,p95=sorted(intervals)[int(len(intervals)*.95)] if intervals else 0),screenshots=shots,classification='Captured; visual review and per-item completeness still required')
 r['actual_pixel_changes']={k:[dict(frame_index=i,frameSerial=f['frameSerial'],tick=f['tick'],partialTick=f['partialTick'],**f['nativePixelDelta'][k]) for i,f in enumerate(fs) if k in f.get('nativePixelDelta',{})] for f in fs for k in f.get('nativePixelDelta',{})}
 r['actual_arrow_sources']=[e['data'] for e in es if e['kind']=='native-server-arrow']
 r['actual_projectile_impacts']=[e['data'] for e in es if e['kind']=='native-projectile-impact']
 out.append(r)
(O/'case-index.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
for r in out:print(r['case'],r['actual_server_attacks'],len(r['actual_damage']),r['geometry_max_counts'],'ghostFrames',r['ghost_frame_count'],'screens',len(r['screenshots']),'median ms',round(r['frame_interval_ms']['median'],1))
