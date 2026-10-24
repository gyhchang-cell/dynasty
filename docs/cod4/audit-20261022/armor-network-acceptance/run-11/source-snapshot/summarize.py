"""Merge fixed-denominator native evidence without discarding failed attempts or equating completion to PASS."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3];D=R/'docs/cod4/audit-20261022/armor-network-acceptance'
read=lambda p:json.loads(p.read_text())
rows=[];used=set()
for n in range(84):
 candidates=[]
 for run in ['run-03','run-05','run-06','run-07','run-08','run-09','run-10']:
  p=D/run/f'case-result-{n}.json'
  if p.exists() and all((D/run/f'{role}-case-{n}.json').exists() for role in ['host','peer']):candidates.append((run,read(p)))
 assert candidates,('missing actual server/host/peer',n)
 passed=[x for x in candidates if x[1]['passed']];run,x=(passed or candidates)[-1];used.add(run)
 clients={r:read(D/run/f'{r}-case-{n}.json') for r in ['host','peer']}
 assert all('AFTER_LEVEL' in c['captureEvent'] for c in clients.values())
 row={'case':n,'set':x['set'],'pieces':x['pieces'],'mechanismPassed':x['passed'],'selectedRun':run,'serverResult':f'{run}/case-result-{n}.json','actualClients':{r:f'{run}/{r}-case-{n}.json' for r in ['host','peer']},'equippedFrameAvailable':{r:(D/run/f'{r}-equipped-frame-{n}.json').exists() for r in ['host','peer']},'checks':x['checks'],'triggerMode':x['triggerMode'],'attempts':[{'run':r,'passed':v['passed']} for r,v in candidates]}
 if n==8 and (D/'defect-unprovoked-guard.json').exists():row['additionalOwnershipFailure']='defect-unprovoked-guard.json: unprovoked actual other network player attacked by owner-tagged crab.'
 rows.append(row)
receipt={'status':'COMPLETE_DENOMINATOR_WITH_EXPLICIT_RESIDUALS','uniqueSets':28,'uniqueTierCases':84,'nativeMechanismPassed':sum(x['mechanismPassed'] for x in rows),'completeCaseFailures':[{'case':x['case'],'set':x['set'],'pieces':x['pieces']} for x in rows if not x['mechanismPassed'] or 'additionalOwnershipFailure' in x],'productionSha256':'ce92592ecd1e1e6e5584cfb05646fb8e82e3275b4d81b235910a1e996ec2458b','scope':'Two actual automated Minecraft clients; host native local channel and separate offline UUID peer real TCP. Four mods with Forge, not full modpack, two humans, headless GameTests or survival acquisition. Supplied gear/environments and original native hurt/physical arrows are labeled per case.','coverage':{'nativeC2SEquipment':'All84 cases actual InventoryScreen + MultiPlayerGameMode.handleInventoryMouseClick equip/unequip; original server LivingEquipmentChange thresholds.','nativeSources':'Actual peer primary attacks, host primary shield blocks, sleep wake C2S, original enchantment menu buttons, minister interact, exam/flute use and original physical arrows where indicated. Fire/incoming lethal/native boss encounter ledger and random trials are QA supplied fixtures, not all C2S.','clients':'All selected cases have server result plus both AFTER_LEVEL rendered client captures. Some legacy cases capture after unequip only; per-row equippedFrameAvailable is explicit.','nativeLongClock':'run03 real6000tick lastStand and3600tick cicada, plus600tick draco lease; no gameTime writes. DayTime environmental changes are separate. QilinShield/taiyiGlow initial deadlines verified, actual6000tick expiration not separately waited.','death':'receipt-death.json: actual both death screens/C2S respawn preserve lastStand/cicada/guard lease/generation, no early life-save bypass. Root permanent progress whitelist is outside scope.','restart':'run11 existing-world native JVM restart if present; no reset fixture in restart mode.'},'todo':{'wholeRowsSafeToDelete':[],'retain65':'Cannot claim full28×2/3/4 completion while leather4 native sound cancellation remains unproved (unless final selected mechanism passes); draco4 cross-player defect also requires repair. Completed individual behavior evidence can narrow wording.','retain66':'Confirmed guard/bystander targeting defect. Repeated real re-equip stat stacking and complete native Boss AI battle with all long cooldown boundaries not fully covered. Existing fixed-UUID/headless63 checks are not rebranded as real network tests.'},'rows':rows,'usedRuns':sorted(used)}
if (D/'run-11/restart-result.json').exists():receipt['restartResult']=read(D/'run-11/restart-result.json')
(D/'result-matrix.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
(D/'receipt-matrix.json').write_text(json.dumps({k:v for k,v in receipt.items() if k!='rows'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ['uniqueSets','uniqueTierCases','nativeMechanismPassed','completeCaseFailures','usedRuns']},ensure_ascii=False))
