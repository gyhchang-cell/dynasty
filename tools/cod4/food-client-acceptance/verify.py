"""Verify recorded native clients; never promote screenshot existence to visual review."""
from pathlib import Path
import collections, datetime, hashlib, json, re, sys, zipfile

ROOT = Path(__file__).resolve().parents[3]
DOC = ROOT / 'docs/cod4/audit-20261022/food-client-acceptance'
PRIOR = ROOT / 'tools/cod4/journey-acceptance/evidence/routes/routes-05'
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return str(p.relative_to(ROOT))
def save(name, value): (DOC / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

checks = []
def check(name, ok, detail=None):
    checks.append(dict(check=name, passed=bool(ok), detail=detail))

den = read(DOC / 'denominator.json')
expected = {'dynasty:' + x for x in den['foods'] + den['existing_talismans']}
check('original request expanded to 15 unique registries', len(expected) == 15)
request = (ROOT / 'docs/cod4/request.txt').read_text()
check('eight named foods remain present in original request', all(' | '+x+' | ' in request for x in den['foods']))
check('original grouped talisman row retained', '火符/雷符/御风/隐身/金刚/摄魂/归乡' in request)
all_cases = []
for run, total in [('run-02', 26), ('run-03', 16)]:
    folder = DOC / run
    plan = read(folder / 'planned-cases.json')
    completed = read(folder / 'DRIVER-COMPLETE.json')
    check(run + ': complete planned native cases', len(plan) == total == len(completed))
    check(run + ': no QA failure artifacts', not list(folder.glob('*FAIL*.json')))
    check(run + ': own client exited cleanly after release', (folder/'exit-code.txt').read_text().strip()=='0' and not read(folder/'FINISHED.json')['keyUseDown'])
    manifest = read(folder / 'manifest.json')
    check(run + ': production JAR pinned', manifest['added_jars']['dynasty-1.4.0.jar'] == '0e1fbac34942714cd90a18ec1b404303b5d4d5bf96ce7c96277e16e561fe5c27')
    for case in plan:
        p = folder / (case['id'] + '-result.json')
        d = read(p); name = run + '/' + case['id']
        b, c, a = [d[k] for k in ['before', 'afterCancelOrTap', 'after']]
        key = 'offCount' if case.get('offhand') else 'mainCount'
        events = collections.defaultdict(list)
        for e in d['serverEvents']: events[e['kind']].append(e)
        caps = {x['label']:x for x in d['captures']}
        counts = {side:[x[side][key] for x in [b,c,a]] for side in ['client','server']}
        check(name + ': actual connected LocalPlayer/ServerPlayer', all(x['client']['class'] == 'net.minecraft.client.player.LocalPlayer' and x['server']['class'] == 'net.minecraft.server.level.ServerPlayer' and x['client']['uuid'] == x['server']['uuid'] for x in [b,c,a]))
        check(name + ': own profile and native input', d['native_input_executed'] and a['instance'] == manifest['instance'] and '/tools/cod4/food-client-acceptance/.work/' in a['instance'])
        check(name + ': release reached both sides', not a['keyUseDown'] and not a['client']['using'] and not a['server']['using'])
        check(name + ': expected camera', b['camera'] == a['camera'] == case['camera'])
        record = dict(run=run, case=case['id'], item=d['item'], kind=d['kind'], result=rel(p), result_sha256=sha(p), counts=counts, animation=b['nativeAnimation'], native_duration=b['nativeDuration'], qa_items_supplied=True)
        tick_path = folder/(case['id']+'-ticks.json')
        record['native_tick_evidence'] = dict(path=rel(tick_path), sha256=sha(tick_path))
        if case['kind'] == 'food':
            starts, stops, finishes = [events[k] for k in ['native_use_start','native_use_stop','native_use_finish']]
            check(name + ': two native starts, one cancel, one finish', len(starts)==2 and len(stops)==1 and len(finishes)==1)
            check(name + ': 32 native ticks', b['nativeDuration']==32 and all(s['durationRemaining']==32 for s in starts) and finishes[0]['state']['useTicks']==32 and finishes[0]['state']['worldTime']-starts[-1]['state']['worldTime']==32)
            check(name + ': original native animation', b['nativeAnimation']==('DRINK' if d['item'].endswith('wine') else 'EAT'))
            check(name + ': cancel no cost, finish exactly one cost on both sides', counts == {'client':[3,3,2], 'server':[3,3,2]})
            check(name + ': server cancelled before completion', 0 < stops[0]['durationRemaining'] < 32)
            check(name + ': sustained native use sampled', all(caps[k]['state']['client']['using'] and caps[k]['state']['keyUseDown'] for k in ['held-mid','held-late']))
            s = finishes[0]['state']; effect = {e['id']:e for e in s['effects']}; t=s['worldTime']; item=d['item'].split(':')[1]
            if item=='regen_pill': benefit=s['health']==52 and effect.get('minecraft:regeneration',{}).get('duration')==100
            elif item=='qi_pill': benefit=s['qiUntil']-t==200 and s['rage']==2 and effect.get('dynasty:yang_qi',{}).get('duration')==100
            elif item=='antidote_pill': benefit=s['antidoteUntil']-t==600 and 'minecraft:poison' not in effect and any(e['id']=='minecraft:poison' for e in b['server']['effects'])
            elif item=='zhuangyuan_wine': benefit=s['examWineUntil']-t==1200 and s['examAnswerMillis']==36000 and b['server']['examAnswerMillis']==30000
            elif item=='marching_wine':
                benefit=effect.get('dynasty:yang_qi',{}).get('duration')==100 and effect.get('minecraft:nausea',{}).get('duration')==80
                if case.get('warm'): benefit=benefit and s['warmUntil']-t==1200 and 'dynasty:frost_vein' not in effect
            elif item=='soul_incense': benefit=not {'dynasty:yin_qi','dynasty:soul_burn'} & set(effect) and len(s['targets'])==1 and not s['targets'][0]['targetIsPlayer']
            elif item=='guide_incense': benefit='Target:' in s['guide'] and int(re.search(r'Until:(\d+)L',s['guide'])[1])-t==1200
            elif item=='army_ration': benefit=s['food']==20 and effect.get('minecraft:saturation',{}).get('duration')==200
            else: benefit=False
            check(name + ': current original benefit actually applied', benefit)
            record.update(finish_state=s, server_cancel_remaining=stops[0]['durationRemaining'], full_use_server_ticks=32)
        else:
            check(name + ': existing instant contract', b['nativeDuration']==0 and b['nativeAnimation']=='NONE' and not any(events[k] for k in ['native_use_start','native_use_stop','native_use_finish']))
            check(name + ': one tap and four held repeats paid', counts=={'client':[16,15,11], 'server':[16,15,11]} and len(events['native_server_right_click'])==5)
            s=c['server']; effect={e['id']:e for e in s['effects']}; item=d['item'].split(':')[1]
            target=s['targets'][0]
            if item=='fire_talisman': benefit=target['health']<5000 and target['fireTicks']>0
            elif item=='thunder_talisman': benefit=target['health']<5000 and {'minecraft:slowness','minecraft:weakness'} <= {e['id'] for e in target['effects']}
            elif item=='wind_talisman': benefit={'minecraft:speed','minecraft:jump_boost','minecraft:slow_falling'} <= set(effect) and target['health']<5000
            elif item=='stealth_talisman': benefit={'minecraft:invisibility','minecraft:night_vision','minecraft:speed'} <= set(effect) and not target['targetIsPlayer']
            elif item=='vajra_talisman': benefit={'minecraft:resistance','minecraft:strength','minecraft:fire_resistance'} <= set(effect)
            elif item=='soul_talisman': benefit=target['health']<5000 and {'minecraft:blindness','minecraft:weakness'} <= {e['id'] for e in target['effects']}
            elif item=='return_talisman': benefit=s['position']!=b['server']['position'] and 'minecraft:poison' not in effect
            else: benefit=False
            check(name + ': instant effect actually applied', benefit)
            record['after_tap_state']=s
        for cap in d['captures']:
            image=folder/cap['file']
            check(name + ':' + cap['label'] + ': raw framebuffer PNG exists', image.exists() and image.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n')
            if run=='run-03':
                st=cap['state']; uid=st['client']['uuid']
                check(name+':'+cap['label']+': camera entity is actual player', all(st[k]['uuid']==uid and st[k]['type']=='minecraft:player' for k in ['cameraEntity','renderCameraEntity','playerEntity']) and st['camera']==case['camera'])
        record['screenshots']=[dict(file=rel(folder/x['file']),sha256=sha(folder/x['file']),label=x['label']) for x in d['captures']]
        if run=='run-03': record['camera_samples']=[dict(label=x['label'],**{k:x['state'][k] for k in ['camera','cameraEntity','renderCameraEntity','renderCameraPosition','playerEntity']}) for x in d['captures']]
        all_cases.append(record)

check('all15 original registries actually used on client', {x['item'] for x in all_cases}==expected)
prior=read(PRIOR/'native-results.json'); previous={x['case'][5:]:x for x in prior if x['case'].startswith('food_')}
check('eight prior native lifetime/Build tests passed', set(previous)==set(den['foods']) and all(x['pass'] for x in previous.values()))
old_hashes=read(PRIOR/'source-hashes.json'); source_records=[]
for sub in ['com/dynasty/expansion/ExpansionSupplies.java','com/dynasty/TalismanCharmItem.java','com/dynasty/expansion/EquipmentBehaviors.java','com/dynasty/expansion/ExpansionEffects.java','com/dynasty/DynastyKeju.java','com/dynasty/DynastyTrinketOnHit.java']:
    p=ROOT/'src/main/java'/sub; f=ROOT/'build/cod4-audit-20261022/frozen/src/main/java'/sub
    source_records.append(dict(path=rel(p),current_sha256=sha(p),verified_build_source_sha256=sha(f),previous_route_sha256=old_hashes.get(rel(p))))
    check(sub+': same relevant implementation as production baseline and prior server tests', sha(p)==sha(f)==old_hashes.get(rel(p)))
baseline=ROOT/'build/cod4-audit-20261022/verified-gradle/libs/dynasty-1.4.0.jar'
tested=ROOT/'build/cod4-pack-20261022/language-repair/dynasty-1.4.0.jar'
with zipfile.ZipFile(baseline) as a,zipfile.ZipFile(tested) as b:
    changed=[n for n in set(a.namelist())|set(b.namelist()) if n not in a.namelist() or n not in b.namelist() or a.read(n)!=b.read(n)]
check('reused production JAR differs only in existing JEI repair', set(changed)=={'com/dynasty/workshop/WorkshopJei.class','com/dynasty/workshop/WorkshopJei$Category.class','com/dynasty/workshop/WorkshopJei$TalismanInfo.class'})

visual_file=DOC/'visual-review.json'
visual=read(visual_file) if visual_file.exists() else {'records':[]}
check('manual visual review covers all15, not just PNG existence', {x['item'] for x in visual['records'] if x.get('pass')}==expected)
for row in visual['records']:
    for proof in row['reviewed_images']:
        check('visual review pinned: '+proof['file'], sha(ROOT/proof['file'])==proof['sha256'])
for proof in visual.get('extra_reviewed_images', []):
    check('extra visual review pinned: '+proof['file'], sha(ROOT/proof['file'])==proof['sha256'])
failed=[x for x in checks if not x['passed']]
report=dict(status='PASS_SCOPED_COD4_9_CLIENT_ACCEPTANCE' if not failed else 'OPEN_EVIDENCE_GAPS',generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),original_request='docs/cod4/request.txt:283-298',original_registry_denominator=15,original_table_rows=9,full_client_cases=26,camera_supplement_cases=16,unique_foods=8,unique_existing_talismans=7,qa_supplied_items=True,natural_acquisition=False,checks_total=len(checks),checks_passed=len(checks)-len(failed),failed_checks=failed,cases=all_cases,reused_server_evidence=dict(path=rel(PRIOR/'native-results.json'),sha256=sha(PRIOR/'native-results.json'),scope='Detached native ServerPlayer lifetime and Build tests only. Client proof comes exclusively from food-client-acceptance run02/03.',records=[dict(item='dynasty:'+i,case=x['case'],native_test=x['native_test'],passed=x['pass'],measurements=x['food_measurements']) for i,x in previous.items()],assertion_source=rel(PRIOR/'JourneySupplyGameTests.java'),assertion_source_sha256=sha(PRIOR/'JourneySupplyGameTests.java')),implementation_binding=source_records,early_run_excluded='run01 third-person frames are occluded by the QA zombie and excluded; no run01 visual is needed for final acceptance. Some run03 completed/settled PNGs contain a stale held frame and are excluded from end-pose/count/timing proof. Native event clocks are separate from manually reviewed visible gestures.',todo_candidate=dict(exact_text='实机验收药品/酒/香/军粮的使用动作、持续时长与对应 Build 收益；已完成的物品注册和普通配方不重复制作。',can_close_in_requested_native_client_scope=not failed,todo_modified=False),limits=['QA supplied items/status/targets, floating normal-world fixture; no natural survival acquisition or actual six-stage survival timing claim. Human participation is not an acceptance prerequisite.','Actual automated production Minecraft client and integrated server; dedicated multiplayer and audio were not tested.','Eight lifetime/expiry and Build tests are reused and explicitly marked server-only.','Existing talismans are instant and repeat while held; no invented32tick or refund contract. Their effect expiry is not claimed newly measured here.','Frame captures can be stale relative to capture metadata; PNGs prove reviewed appearance only, not exact tick/consumption/end-pose timing.','Only tested immutable production JAR and bound relevant implementations; unrelated shared workspace changes are outside this QA.'])
report['visual_review'] = dict(path=rel(visual_file), sha256=sha(visual_file), scope='Manually reviewed all15 native appearance/instant feedback; independent from native timing checks.')
save('native-verification.json',dict(checks=checks))
save('final-acceptance.json',report)
for row in den['records']:
    row['client_status']='PASS' if not failed else 'NATIVE_COMPLETE_FINAL_GAPS'
    row['native_result']='run-02/first-'+row['item'].split(':')[1]+'-result.json'
den['scope']='Actual independent production Minecraft client and integrated server, QA supplied items/world; not natural acquisition or actual six-stage survival timing. No detached player accepted as client proof; no human participation prerequisite.'
den['status']=report['status'];den['extra_cases']='8 third-person in run02; 2 offhand; 1 tagged warm wine; 16 front/back camera-identity cases in run03. These do not enlarge original15 denominator.'
save('denominator.json',den)
print(json.dumps({k:report[k] for k in ['status','original_registry_denominator','full_client_cases','camera_supplement_cases','checks_total','checks_passed','failed_checks']},ensure_ascii=False,indent=2))
sys.exit(bool(failed))
