"""Audit whether an emitted native click used a pre-physics scheduled snapshot."""
from pathlib import Path
import json,re,bisect,sys,collections
p=Path(sys.argv[1]);frames=[];clicks=[]
for l in p.read_text().splitlines():
 t=float(l.split()[0])
 if ' FRAME ' in l:frames.append((t,json.loads(l.split(' FRAME ')[1])))
 if ' PLACE ' in l:
  m=re.search(r'target=F3Block\(x: (-?\d+), y: (-?\d+), z: (-?\d+)\)',l)
  if m:clicks.append((t,list(map(int,m.groups())),len(frames)-1))
times=[t for t,d in frames];rows=[]
for t,b,i in clicks:
 if i<0:continue
 f=frames[i][1]
 confirmation=next((u for u,d in frames[i+1:] if u>t and u-t<.16 and b in d['solid']),None)
 rows.append(dict(time=t,target=b,tick=f['tick'],ticks_due=f.get('ticksDue'),confirmation_ms=round((confirmation-t)*1000,2) if confirmation else None))
buckets={}
for due in sorted(set(x['ticks_due'] for x in rows),key=str):
 selected=[x for x in rows if x['ticks_due']==due]
 buckets[str(due)]={'clicks':len(selected),'not_confirmed_within_160ms':sum(x['confirmation_ms'] is None for x in selected)}
report=dict(log=str(p),snapshot_phase='ave.av: scheduledExecutables before elapsed game ticks and renderer',buckets=buckets,clicks=rows,caveat='Confirmation latency, not server acknowledgment or direct interception of useItem. Correlation alone does not establish causation.')
print(json.dumps(report,indent=2))
