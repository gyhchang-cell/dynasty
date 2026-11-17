"""Regression validation for QA tooling only: JDK CaseLog + synthetic JSON counterexamples, no Minecraft."""
from pathlib import Path
import copy, datetime, hashlib, importlib.util, json, subprocess
B=Path(__file__).resolve().parents[1]; R=B.parents[2]; O=R/'docs/cod4/audit-20261022/sweep-native-acceptance'
W=B/'.work'/('checks02-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')); W.mkdir(parents=True)
spec=importlib.util.spec_from_file_location('sweep_analysis',B/'analyze.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
results=[]
def check(name, truth):
    results.append(dict(name=name,pass_=bool(truth)))
    if not truth: raise AssertionError(name)
def run(cmd):
    r=subprocess.run(cmd,capture_output=True,text=True);check('command exit0: '+Path(cmd[0]).name,r.returncode==0);return r.stdout
jhome=Path('/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin');classes=W/'jdk-classes';classes.mkdir()
compile_cmd=[str(jhome/'javac'),'-J-Djava.awt.headless=true','--release','17','-d',str(classes),str(B/'src/com/dynasty/sweepqa/CaseLog.java'),str(B/'checks/CaseLogCheck.java')]
run(compile_cmd);outs=[run([str(jhome/'java'),'-Djava.awt.headless=true','-cp',str(classes),'CaseLogCheck']) for _ in range(2)]
(W/'jdk-lifecycle.log').write_text('\n'.join(outs));check('separate JDK process sessions differ',outs[0].split('session=')[1].split(',')[0]!=outs[1].split('session=')[1].split(',')[0])
E=W/'SYNTHETIC-NOT-NATIVE';E.mkdir();artifact='a'*64
actor=dict(uuid='actor-a',id=1,dimension='minecraft:overworld',health=20)
main=dict(uuid='main-a',id=2,dimension='minecraft:overworld',health=1000,invulnerable=False)
side=dict(uuid='side-a',id=3,dimension='minecraft:overworld',health=1000,invulnerable=False)
hooks=sorted(module.HOOKS)
def make(name,mode='success',view='first',base=1000):
    nonce='nonce-'+name
    def stamp(role):return dict(case=name,binding=nonce,mode=mode,capture=role+'-'+name,role=role,session=role+'-session',artifact=artifact,build='sweepqa-02')
    def event(role,kind,data,nano):return dict(stamp(role),kind=kind,data=data,nano=nano,thread=role)
    ts=copy.deepcopy([main,side])
    if mode=='invulnerable':
        for t in ts:t['invulnerable']=True
    fixture=dict(case=name,mode=mode,identity=stamp('server'),actor=actor,targets=ts)
    server=[event('server','fixture-ready',fixture,base),event('server','server-native-attack',dict(actor=actor,target=ts[0],cycle=100,cancelled=mode=='cancel-attack'),base+1)]
    packet=dict(sequence=module.CUE,entity=1,dimension=actor['dimension'],start=102,duration=6,seed=0,template=2)
    mesh=dict(sequence='mesh_weapon',entity=1,dimension=actor['dimension'],start=101,duration=8,seed=123,template=29)
    row=dict(identity=8,produced=101,consumedNow=102,age=1,actor=actor,main=dict(ts[0],health=990),health=1000,capturedLevelMatchesActor=True,capturedLevelMatchesMain=True,secondary=True,primaryDamage=True)
    for cycle in range(101,125):
        server.append(event('server','receipt-before-exact-consumer',dict(cycle=cycle,now=cycle+1,rows=[row] if mode=='success' and cycle==101 else []),base+2+(cycle-101)*2))
        server.append(event('server','receipt-after-exact-consumer',dict(cycle=cycle,now=cycle+1,rows=[]),base+3+(cycle-101)*2))
    final=copy.deepcopy(ts)
    if mode=='success':final[0]['health']-=10
    if mode=='cancel-damage':server.append(event('server','server-damage-event-not-final-hp',dict(target=ts[0],owner=actor,direct=actor,source='player',amount=10,cancelled=True),base+48))
    server.append(event('server','server-final-targets',final,base+60))
    client=[event('client','client-capture-start',dict(player=actor,observerOnly=False,view=view,cooldown=1,fixtureSHA256='pending'),base+1),event('client','actual-client-gamemode-attack',dict(player=actor,target=ts[0]),base+2)]
    for h in hooks:client.append(event('client','loaded-render-hook',h,base+3))
    if mode=='success':client.extend([event('client','actual-s2c-handle',packet,base+4),event('client','actual-s2c-handle',mesh,base+5)])
    client.append(event('client','client-capture-end',dict(reason='bounded-40-client-ticks',ticks=40),base+50))
    frames=[]
    for age in (1,40):
        f=dict(stamp('client'),serial=age,tick=100+age,ageClientTicks=age,view=module.VIEWS[view],hooks=hooks,geometry={},afterimages=[],nativePixelDelta={})
        if mode=='success' and age==1:
            f['geometry']={'FangtianSweep':[[0,1,2]]}
            f['afterimages']=[dict(item='dynasty:halberd_fangtian',actor=actor,packet=mesh)]
            f['nativePixelDelta']={'FangtianSweep':dict(nativeBefore='synthetic-before.txt',nativeAfter='synthetic-after.txt')}
        frames.append(f)
    return dict(fixture=fixture,server=server,client=client,frames=frames)
def save(name,b):
    for kind,suffix in [('fixture','-fixture.json'),('server','-server-events.json'),('client','-client-events.json'),('frames','-client-frames.json')]:
        if kind=='client':
            b['client'][0]['data']['fixtureSHA256']=module.sha(E/(name+'-fixture.json'))
        (E/(name+suffix)).write_text(json.dumps(b[kind],indent=2)+'\n')
    (E/'synthetic-before.txt').write_text('SYNTHETIC NON-IMAGE TEST DATA; NOT A RENDER')
    (E/'synthetic-after.txt').write_text('SYNTHETIC NON-IMAGE TEST DATA; NOT A RENDER')

def evaluate(name,b,mode='success',view='first',cal=None):
    save(name,b);return module.analyze(E,name,mode,view,cal)
positive=make('positive');report=evaluate('positive',positive);check('well-formed synthetic positive exercises passing mechanical path',report['mechanical_checks_pass']);check('synthetic mechanical path never grants overall acceptance',report['overall_acceptance'] is False)
for mode in ['cancel-attack','cancel-damage','invulnerable']:
    name=mode;bundle=make(name,mode,base=2000);r=evaluate(name,bundle,mode,cal='positive');check('valid calibrated synthetic '+mode,r['mechanical_checks_pass'])
    check('negative without calibration rejected: '+mode,not module.analyze(E,name,mode,'first')['mechanical_checks_pass'])
# Every mutation represents a reviewed or adjacent false-positive path, not an implementation mirror.
mutations={
 'missing-END-probes':lambda b:b.__setitem__('server',[x for x in b['server'] if not x['kind'].startswith('receipt-')]),
 'missing-render-hooks':lambda b:(b.__setitem__('client',[x for x in b['client'] if x['kind']!='loaded-render-hook']),[f.__setitem__('hooks',[]) for f in b['frames']]),
 'one-END-half-only':lambda b:b.__setitem__('server',[x for x in b['server'] if x['kind']!='receipt-after-exact-consumer']),
 'gapped-END-window':lambda b:b.__setitem__('server',[x for x in b['server'] if x['kind'] not in ('receipt-before-exact-consumer','receipt-after-exact-consumer') or x['data']['cycle']!=110]),
 'wrong-client-actor':lambda b:b['client'][1]['data'].__setitem__('player',dict(actor,uuid='other')),
 'wrong-client-main':lambda b:b['client'][1]['data'].__setitem__('target',dict(main,uuid='external')),
 'wrong-server-main':lambda b:b['server'][1]['data'].__setitem__('target',dict(main,uuid='external')),
 'wrong-server-actor':lambda b:b['server'][1]['data'].__setitem__('actor',dict(actor,uuid='other')),
 'wrong-dimension':lambda b:b['client'][1]['data'].__setitem__('target',dict(main,dimension='minecraft:the_nether')),
 'wrong-entity-id':lambda b:b['client'][1]['data'].__setitem__('target',dict(main,id=999)),
 'stale-client-case':lambda b:b['client'].append(dict(b['client'][1],case='old-case')),
 'stale-server-binding':lambda b:b['server'][1].__setitem__('binding','old-nonce'),
 'wrong-capture':lambda b:b['frames'][0].__setitem__('capture','old-capture'),
 'wrong-mode':lambda b:b['client'][1].__setitem__('mode','success'),
 'wrong-camera':lambda b:b['frames'][0].__setitem__('view','THIRD_PERSON_BACK'),
 'different-client-session':lambda b:[x.__setitem__('session','new-client-session') for x in b['client']+b['frames']],
 'different-server-session':lambda b:(b['fixture']['identity'].__setitem__('session','new-server-session'),[x.__setitem__('session','new-server-session') for x in b['server']]),
 'different-QA-artifact':lambda b:[x.__setitem__('artifact','b'*64) for x in b['client']+b['frames']],
 'unpackaged-instrumentation':lambda b:[x.__setitem__('artifact','UNPACKAGED-OFFLINE') for x in b['client']+b['frames']],
 'short-client-window':lambda b:b['client'][-1]['data'].__setitem__('ticks',6),
 'disconnect':lambda b:b['client'][-1]['data'].__setitem__('reason','disconnect'),
 'fixture-not-actually-invulnerable':lambda b:b['fixture']['targets'][0].__setitem__('invulnerable',False),
 'server-before-positive-calibration':lambda b:[x.__setitem__('nano',x['nano']-3000) for x in b['server']],
 'negative-before-positive-calibration':lambda b:[x.__setitem__('nano',x['nano']-3000) for x in b['client']],
}
for label,mutate in mutations.items():
    b=make('counterexample','invulnerable',base=2000);mutate(b);r=evaluate('counterexample',b,'invulnerable',cal='positive');check('reject '+label,not r['mechanical_checks_pass'])
# Correct both attack logs to the same external invulnerable entity: original QA-03 counterexample.
b=make('counterexample','invulnerable',base=2000);b['client'][1]['data']['target']=dict(main,uuid='external',id=99);b['server'][1]['data']['target']=dict(main,uuid='external',id=99);check('reject matching logs for wrong external target',not evaluate('counterexample',b,'invulnerable',cal='positive')['mechanical_checks_pass'])
b=make('counterexample','cancel-damage',base=2000);next(x for x in b['server'] if x['kind']=='server-damage-event-not-final-hp')['data']['owner']=dict(actor,uuid='wrong-owner');check('reject unrelated cancelled damage',not evaluate('counterexample',b,'cancel-damage',cal='positive')['mechanical_checks_pass'])
b=make('positive');next(x for x in b['server'] if x['kind']=='receipt-before-exact-consumer' and x['data']['rows'])['data']['rows'][0]['main']=dict(main,uuid='wrong-primary');check('reject positive receipt wrong main',not evaluate('positive',b)['mechanical_checks_pass'])
b=make('positive');b['frames'][0]['afterimages'][0]['actor']=dict(actor,uuid='other-actor');check('reject same-item ghost from other actor',not evaluate('positive',b)['mechanical_checks_pass'])
# Positive failures must also invalidate any negative calibration that relies on them.
for label, mutate in {
 'missing-wire-hook':lambda b:b.__setitem__('client',[x for x in b['client'] if x['kind']!='actual-s2c-handle']),
 'missing-triangle-hook':lambda b:b['frames'][0].__setitem__('geometry',{}),
 'duplicate-dedicated-cue':lambda b:b['client'].insert(-1,copy.deepcopy(next(x for x in b['client'] if x['kind']=='actual-s2c-handle' and x['data']['sequence']==module.CUE))),
 'age-zero-is-not-age-one':lambda b:next(x for x in b['server'] if x['kind']=='receipt-before-exact-consumer' and x['data']['rows'])['data']['rows'][0].__setitem__('age',0),
 'wrong-mesh-start':lambda b:b['frames'][0]['afterimages'][0].__setitem__('packet',dict(b['frames'][0]['afterimages'][0]['packet'],start=9999)),
 'wrong-cue-dimension':lambda b:next(x for x in b['client'] if x['kind']=='actual-s2c-handle' and x['data']['sequence']==module.CUE)['data'].__setitem__('dimension','minecraft:the_nether'),
}.items():
    b=make('positive');mutate(b);check('reject positive '+label,not evaluate('positive',b)['mechanical_checks_pass'])
    neg=make('counterexample','invulnerable',base=2000);check('reject calibration '+label,not evaluate('counterexample',neg,'invulnerable',cal='positive')['mechanical_checks_pass'])
# Restore calibration before testing corrupt/incomplete evidence.
evaluate('positive',make('positive'))
(E/'missing-fixture.json').write_text('{}');check('missing files fail closed',not module.analyze(E,'missing','invulnerable','first','positive')['mechanical_checks_pass'])
check('empty evidence fails closed',not module.analyze(E,'empty','success','first')['mechanical_checks_pass'])
third=make('third-positive',view='third',base=3000);check('actual third requested synthetic path',evaluate('third-positive',third,view='third')['mechanical_checks_pass']);check('cannot relabel first evidence as third',not module.analyze(E,'positive','success','third')['mechanical_checks_pass'])
receipt=dict(scope='OFFLINE TOOLING REGRESSION ONLY; SYNTHETIC JSON + JDK, NOT MINECRAFT/NATIVE/C2S/PIXEL ACCEPTANCE',status='PASS',checks=len(results),jdk_lifecycle_checks_per_process=18,jdk_processes=2,results=results,work=str(W.relative_to(R)),game_started=False,forge_or_minecraft_loaded=False,source_sha256={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [B/'analyze.py',B/'src/com/dynasty/sweepqa/CaseLog.java',B/'checks/CaseLogCheck.java',Path(__file__)]})
(O/'offline-checks02.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(status=receipt['status'],checks=len(results),work=receipt['work'],scope=receipt['scope']),indent=2))
