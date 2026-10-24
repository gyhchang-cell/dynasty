"""Drive only the private helper in its own production client; native results are retained."""
from pathlib import Path
import json,time,sys,os
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/pack-acceptance'/sys.argv[1]
def load(p):return json.loads(p.read_text())
def wait_file(name,timeout=240):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  if (O/name).exists():return load(O/name)
  if (O/'exit-code.txt').exists():raise RuntimeError('Client exited: '+(O/'exit-code.txt').read_text())
  time.sleep(.25)
 raise TimeoutError(name)
def command(id,op,**args):
 p=O/'command.pending';p.write_text(json.dumps(dict(id=id,op=op,**args)));os.replace(p,O/'command.json')
 end=time.monotonic()+240
 while time.monotonic()<end:
  if (O/(id+'-FAIL.json')).exists():raise RuntimeError(load(O/(id+'-FAIL.json')))
  if (O/(id+'-result.json')).exists():return load(O/(id+'-result.json'))
  if (O/'exit-code.txt').exists():raise RuntimeError('Client exited')
  time.sleep(.25)
 raise TimeoutError(id)
if __name__=='__main__':
 wait_file('READY.json',600);print('Actual full-pack world ready',flush=True)
 ids=['fire_talisman','thunder_talisman','wind_talisman','stealth_talisman','vajra_talisman','soul_talisman','return_talisman']
 report={'jei':[],'bow':[],'scope':'Automated production client and integrated server, not human multiplayer'}
 for lang in ['zh_cn','en_us']:
  if lang!='zh_cn':command('language-'+lang,'language',lang=lang)
  command(lang+'-talismans','talismans')
  for id in ids:
   for role in ['INPUT','OUTPUT']:
    key=lang+'-'+id+'-'+role.lower();s=command(key,'jei',item='dynasty:'+id,role=role)
    report['jei'].append({'capture':key,'state':s});print(key,s.get('jeiScreen',{}).get('category'),flush=True)
   key=lang+'-'+id+'-info';s=command(key,'info',item='dynasty:'+id);report['jei'].append({'capture':key,'state':s})
   # Escape uses the actual JEI Screen key handler to return to the inventory.
   s=command(lang+'-'+id+'-escape','key',key=256);report['jei'].append({'capture':lang+'-'+id+'-escape','state':s})
  (O/'driver-partial.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 command('bow-language-zh','language',lang='zh_cn')
 cases=[('rapid-'+id,'dynasty:'+id,{}) for id in ['lie_gong','chang_gong','shenbi_bow','luoyan_bow','tianlang_bow']]
 cases += [('standard-dragon','dynasty:dragon_bow',{}),('standard-zhuxing','dynasty:zhuxing_bow',{}),('standard-fengling','dynasty:fengling_bow',{}),('offhand','dynasty:lie_gong',{'offhand':True}),('third-back','dynasty:lie_gong',{'camera':'THIRD_PERSON_BACK'}),('third-front','dynasty:dragon_bow',{'camera':'THIRD_PERSON_FRONT'}),('gui-covered','dynasty:lie_gong',{'variant':'gui'}),('hide-gui','dynasty:lie_gong',{'variant':'hideGui'}),('swap-cancel','dynasty:lie_gong',{'variant':'swap'}),('negative-vanilla','minecraft:bow',{})]
 for name,item,opts in cases:
  command('start-bow-'+name,'bow',name='bow-'+name,item=item,**opts)
  s=wait_file('bow-'+name+'-result.json');report['bow'].append({'case':name,'state':s});print('Bow case',name,'completed',flush=True)
  (O/'driver-partial.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 (O/'DRIVER-COMPLETE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print('All scripted inputs complete; client left open for inspection and follow-up',flush=True)
