from pathlib import Path
import json,sys,time
R=Path(__file__).resolve().parents[3];D=R/'docs/cod4/audit-20261022/accessory-visual-acceptance'/sys.argv[1]
def wait(p,timeout=600):
 end=time.time()+timeout
 while time.time()<end:
  if p.exists():return json.loads(p.read_text())
  fs=list(D.glob('*-FAIL.json'))
  if fs:raise RuntimeError(fs[-1].read_text())
  if (D/'exit-code.txt').exists():raise RuntimeError('own client exited')
  time.sleep(.3)
 raise TimeoutError(p)
cases=[]
for item,slot,camera in [('jade_cicada','charm','BACK'),('jade_bi_disc','necklace','BACK'),('moon_pendant','necklace','BACK'),('qilin_horn_charm','necklace','BACK'),('silk_pouch','belt','FRONT'),('jade_pendant','necklace','FRONT'),('gold_seal_charm','charm','FRONT'),('dragon_scale_charm','charm','FRONT'),('phoenix_feather_charm','head','BACK'),('fox_tail_charm','charm','BACK')]:
 cases.append(dict(id=item+'-native',item=item,slot=slot,camera='THIRD_PERSON_'+camera,pixels=True,duration=1200 if item=='fox_tail_charm' else 130))
if len(sys.argv)>2 and sys.argv[2]=='front':cases=[c for c in cases if c['item'] in ['jade_pendant','gold_seal_charm','dragon_scale_charm','silk_pouch']]
if len(sys.argv)>2 and sys.argv[2]=='silk':cases=[c for c in cases if c['item']=='silk_pouch']
wait(D/'READY.json')
while not (D/'peer-READY.json').exists():time.sleep(.3)
for c in cases:
 if (D/(c['id']+'-result.json')).exists():continue
 p=D/'command.tmp';p.write_text(json.dumps(c));p.replace(D/'command.json');r=wait(D/(c['id']+'-result.json'),240)
 es=json.loads((D/(c['id']+'-events.json')).read_text());fs=json.loads((D/(c['id']+'-frames.json')).read_text())
 print(c['id'],'frames',len(fs),'geometry',sorted({k for f in fs for k in f['geometry']}),'wire',sorted({e['data']['sequence'] for e in es if e['kind']=='actual-s2c-handle'}),'heals',sum(e['kind']=='native-heal' for e in es),flush=True)
(D/'DRIVER-COMPLETE.json').write_text(json.dumps(cases,indent=2));p=D/'command.tmp';p.write_text(json.dumps(dict(id='finish-accessory',op='finish')));p.replace(D/'command.json')
