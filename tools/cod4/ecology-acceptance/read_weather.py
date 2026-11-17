"""Read ONLY the QA world's actual gzip NBT save; never changes weather or time."""
from pathlib import Path
import gzip,struct,json,datetime
R=Path(__file__).resolve().parents[3]
WORLD=R/'tools/cod4/ecology-acceptance/.work/live-run1/world/level.dat'
def read_weather():
 b=gzip.decompress(WORLD.read_bytes());i=0
 def take(n):
  nonlocal i
  v=b[i:i+n];i+=n;return v
 def num(fmt):return struct.unpack('>'+fmt,take(struct.calcsize('>'+fmt)))[0]
 def string():return take(num('H')).decode('utf-8',errors='replace')
 def value(t):
  if 1<=t<=6:return num({1:'b',2:'h',3:'i',4:'q',5:'f',6:'d'}[t])
  if t==7:return take(num('i'))
  if t==8:return string()
  if t==9:
   kind=num('b');return [value(kind) for _ in range(num('i'))]
  if t==10:
   result={}
   while True:
    kind=num('b')
    if not kind:return result
    key=string();result[key]=value(kind)
  if t in (11,12):return [num('i' if t==11 else 'q') for _ in range(num('i'))]
  raise ValueError('Unknown NBT type '+str(t))
 kind=num('b');string();data=value(kind)['Data']
 return {'read_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'Private QA normal world level.dat (native autosave, may lag live tick)','source_mtime':WORLD.stat().st_mtime,**{k:data.get(k) for k in ['Time','DayTime','raining','rainTime','thundering','thunderTime','clearWeatherTime']}}
if __name__=='__main__':
 result=read_weather();d=R/'docs/cod4/audit-20261022/ecology-acceptance/live-run1';(d/'saved-world-weather.json').write_text(json.dumps(result,indent=2)+'\n')
 with (d/'weather-observations.jsonl').open('a') as f:f.write(json.dumps(result)+'\n')
 print(json.dumps(result))
