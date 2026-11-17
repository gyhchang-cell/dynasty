"""Drive the private real client; preserve every native event/state/frame and fail honestly."""
from pathlib import Path
import json,os,sys,time
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/cod4/audit-20261022/food-client-acceptance'/sys.argv[1]
def load(p):return json.loads(p.read_text())
def wait(name,timeout=300):
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        if (OUT/name).exists():return load(OUT/name)
        if (OUT/'exit-code.txt').exists():raise RuntimeError('Own client exited: '+(OUT/'exit-code.txt').read_text())
        if (OUT/'STARTUP-FAIL.json').exists():raise RuntimeError('Native startup failed')
        time.sleep(.25)
    raise TimeoutError(name)
def command(case):
    pending=OUT/'command.pending';pending.write_text(json.dumps(case));os.replace(pending,OUT/'command.json')
    deadline=time.monotonic()+150
    while time.monotonic()<deadline:
        failed=OUT/(case['id']+'-FAIL.json')
        if failed.exists():raise RuntimeError(load(failed))
        result=OUT/(case['id']+'-result.json')
        if result.exists():return load(result)
        time.sleep(.25)
    raise TimeoutError(case['id'])

if __name__=='__main__':
    wait('READY.json',600);denom=load(OUT.parent/'denominator.json');cases=[]
    for camera in ['FIRST_PERSON','THIRD_PERSON_FRONT']:
        for item in denom['foods']:
            cases.append(dict(id=('first-' if camera=='FIRST_PERSON' else 'third-')+item,op='case',kind='food',item='dynasty:'+item,camera=camera))
        if camera=='FIRST_PERSON':
            for item in denom['existing_talismans']:cases.append(dict(id='first-'+item,op='case',kind='talisman',item='dynasty:'+item,camera=camera))
    for item in ['regen_pill','marching_wine']:
        cases.append(dict(id='offhand-'+item,op='case',kind='food',item='dynasty:'+item,camera='FIRST_PERSON',offhand=True))
    cases.append(dict(id='warm-marching_wine',op='case',kind='food',item='dynasty:marching_wine',camera='FIRST_PERSON',warm=True))
    if len(sys.argv)>2 and sys.argv[2]=='camera-audit':
        cases=[dict(id=prefix+item,op='case',kind='food',item='dynasty:'+item,camera=camera) for prefix,camera in [('front-','THIRD_PERSON_FRONT'),('back-','THIRD_PERSON_BACK')] for item in denom['foods']]
    (OUT/'planned-cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n')
    results=[]
    for case in cases:
        r=command(case);results.append({'case':case['id'],'native_input_executed':r['native_input_executed'],'captures':len(r['captures'])})
        print(case['id'],len(r['captures']),'captures; native input complete',flush=True)
        (OUT/'driver-progress.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    (OUT/'DRIVER-COMPLETE.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print('All native input cases complete; own client remains open until visual review finishes.',flush=True)
