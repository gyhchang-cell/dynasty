"""Independently check completed native interaction TCP receipts; never accept partial harness output."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[3]
run=sys.argv[1] if len(sys.argv)>1 else 'run-01'
assert re.fullmatch(r'run-\d+',run)
OUT=ROOT/'docs/cod4/audit-20261022/interaction-network-acceptance'/run
read=lambda n:json.loads((OUT/n).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
scope=read('interaction-scope.json')
assert scope['wholeStoryCompletion'] and scope['entryCases']==scope['timedRoutes']==scope['repeatedRoutes']==15
assert scope['elapsedTimersNotModified'] and not scope['sceneBlocksManuallyPlaced']
assert (OUT/'server-PASS').exists() and not (OUT/'server-PARTIAL').exists()
shared=read('shared-waterwheel-ack.json');assert shared['done'] and shared['inventoryUnchanged'] and shared['ownNativeClick']
connections=read('connections.json');assert len(connections)==2 and len({p['uuid'] for p in connections})==2
actor=next(p['uuid'] for p in connections if p['name']=='Cod4ArmorPeer')
observer=next(p['uuid'] for p in connections if p['name']=='Cod4ArmorHost')
rows=read('interaction-results.json');timed=read('interaction-timed-results.json')
acks=[r for r in rows if r['phase']=='observer_ack'];assert len(acks)==1
ack=acks[0];assert ack['id']=='broken_waterwheel' and ack['case']==shared['sequence'] and shared['player']==observer
assert read(f"server-native-use-{ack['case']}.json")['block']=='286, 92, -469'
assert ack['actorStacksBefore']==ack['actorStacksAfter']
assert len({r['case'] for r in rows})==len(rows)
entries=[r for r in rows if r['phase']=='entry'];assert len(entries)==15 and len({r['id'] for r in entries})==15
ids={r['id'] for r in entries}
assert {r['site'] for r in timed if r['phase']=='complete' and r['done']}==ids
assert {r['site'] for r in timed if r['phase']=='repeat'}==ids
for row in rows:
    assert row['observerPrivateUnchanged'] and row['observerInventoryUnchanged'] and row['observerFullStacksUnchanged']
    assert row['observerPrivateBefore']==row['observerPrivateAfter'] and row['observerStacksBefore']==row['observerStacksAfter']
    n=row['case'];native=read(f'server-native-use-{n}.json');peer=read(f'native-use-{n}.json')
    expected_actor=observer if row['phase']=='observer_ack' else actor
    assert native['player']==peer['player']==expected_actor
    role='host' if row['phase']=='observer_ack' else 'peer';assert (OUT/f'{role}-teleport-seen-{n}').exists()
    for role,uid in [('host',observer),('peer',actor)]:
        frame=read(f'{role}-interaction-frame-{n}.json')
        assert frame['localPlayer']==uid and frame['captureEvent']=='AFTER_LEVEL real rendered client'
        assert frame['language']=='zh_cn'
        assert (OUT/f'{role}-interaction-frame-{n}.png').stat().st_size>1000
    if row['phase']=='entry':
        messages=read(f'peer-interaction-frame-{n}.json')['receivedResolvedMessages']
        resolved=[m['resolved'] for m in messages]
        assert any(re.search(r'[\u3400-\u9fff]',m) for m in resolved),(row['id'],'no actual Chinese response')
        assert not any(re.search(r'(?:message|interaction|cod4)\.dynasty\.',m) for m in resolved),(row['id'],'unresolved key')
payments={'wayside_shrine':'dynasty:soul_incense','nameless_tomb':'minecraft:poppy','broken_stele':'minecraft:paper','old_bellows':'minecraft:charcoal','broken_waterwheel':'dynasty:qimen_cable','ghost_market_boat':'dynasty:cinnabar','mortuary_room':'minecraft:potion'}
rewards={'old_weapon_rack':{'dynasty:tie_jian':1},'herb_spot':{'dynasty:tea':2},'abandoned_armory':{'dynasty:qimen_gear':1},'old_bellows':{'minecraft:iron_nugget':3},'broken_stele':{'dynasty:copper_coin':2},'broken_waterwheel':{'dynasty:copper_coin':2},'battlefield_remnant':{'dynasty:copper_coin':2},'sword_scar_wall':{'dynasty:jade':1,'dynasty:copper_coin':2},'ghost_market_boat':{'dynasty:bamboo_slip':1,'dynasty:copper_coin':2},'puzzle_box':{'dynasty:blueprint':1,'dynasty:copper_coin':2},'ancient_well':{'dynasty:jade':1},'wayside_tea_stall':{'dynasty:silk':1},'mortuary_room':{'dynasty:longyuan_sword':1,'minecraft:glass_bottle':1}}
def expected_inventory(row):
    result=row['actorInventoryBefore'].copy()
    def add(item,amount):result[item]=result.get(item,0)+amount
    if row['site']=='ancient_well':add('minecraft:water_bucket',-1);add('minecraft:bucket',1)
    if row['done']:
        if row['site'] in payments:add(payments[row['site']],-1)
        for item,amount in rewards.get(row['site'],{}).items():add(item,amount)
    return {item:amount for item,amount in result.items() if amount}
for row in timed:
    assert row['originalStartPreserved']
    if row['phase']=='complete':
        assert row['worldTick']>=row['deadlineBefore']
        assert expected_inventory(row)==row['actorInventoryAfter'],row['site']
    else:
        assert row['done'] and row['countBefore']==row['countAfter']
        assert row['actorInventoryBefore']==row['actorInventoryAfter'] and row['actorStacksBefore']==row['actorStacksAfter']
        assert row['deadlineBefore']==row['deadlineAfter']
well=[r for r in timed if r['site']=='ancient_well' and r['phase']=='complete']
assert [r['countAfter'] for r in well]==list(range(1,8)) and well[-1]['worldTick']-well[-1]['start']>=3600
puzzle=[r for r in timed if r['site']=='puzzle_box' and r['phase']=='complete']
for r,facing,sneaking in zip(puzzle,['north','east','south','west'],[False,True,False,True],strict=True):
    use=read(f"server-native-use-{r['sequence']}.json");assert use['facing']==facing and use['sneaking']==sneaking
assert len(puzzle)==4 and puzzle[-1]['done'] and puzzle[-1]['worldTick']-puzzle[-1]['start']>=2400
battle=[r for r in timed if r['site']=='battlefield_remnant' and r['phase']=='complete']
assert [r['countAfter'] for r in battle]==[1,2,3]
anchors=[read(f"server-native-use-{r['sequence']}.json")['block'] for r in battle]
assert len(set(anchors))==3
sword=[r for r in timed if r['site']=='sword_scar_wall' and r['phase']=='complete'];assert len(sword)==1 and sword[0]['done']
assert sword[0]['worldTick']-sword[0]['start']>=2400
cuts=[read(f"peer-native-dance-{sword[0]['sequence']}-{i}.json") for i in range(3)]
for i,c in enumerate(cuts):
    assert c['step']==i and c['client']==actor and c['onGround'] and .35<=c['along']<=1.5 and c['across']<=.35
    assert c['worldTickObserved']>=c['deadlineObserved']
for i in range(1,3):assert cuts[i]['worldTickObserved']-cuts[i-1]['worldTickObserved']>=800
for site,choices in [('ghost_market_boat',{'talk','deliver'}),('wayside_tea_stall',{'inspect','drink','flip'})]:
    receipts=[read(f.name) for f in OUT.glob('peer-native-dialogue-*.json')]
    assert choices<={r['action'] for r in receipts if r['site']==site and r['client']==actor}
for role in ['host','peer']:
    assert (OUT/f'{role}-exit-code.txt').read_text().strip()=='0'
    assert (OUT/f'{role}-PASS').exists() and (OUT/f'{role}-COMPLETE').exists()
    manifest=read(f'{role}-manifest.json');assert manifest['total_mod_jars']==4
    log=(OUT/f'{role}-client.log').read_text(errors='replace')
    assert 'GUARD_NETWORK_QA_WINDOW visible=0 focused=0' in log and 'Stopping!' in log
    assert 'soundCategory_master:0.0' in (Path(manifest['instance'])/'options.txt').read_text()
    if role=='host':assert 'ThreadedAnvilChunkStorage: All dimensions are saved' in log
assert re.search(r'Cod4ArmorPeer\[/127\.0\.0\.1:\d+\] logged in',(OUT/'host-client.log').read_text(errors='replace'))
receipt={'status':'NATIVE_TCP_CHECKS_PASS_VISUAL_REVIEW_PENDING','natural_sites':15,'timed_routes':15,'native_repeated_use_routes':15,'actual_client_resolved_Chinese':True,'screenshots_recorded':True,'screenshots_visually_reviewed':False,'whole_todo_complete':False,'fixtures':['Private seed20261023 normal world','Two QA identities teleported to actual natural sites','Items supplied in actor inventory','Night fixed by daylight rule; native gameTime never changed','Raw iron input supplied to existing natural furnace'],'user_worlds_touched':False,'files':{f.name:sha(f) for f in OUT.iterdir() if f.is_file() and f.name!='verification.json'}}
(OUT/'verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='files'},ensure_ascii=False))
