"""Read-only source/evidence audit. Does not repair players or grant research credits."""
from pathlib import Path
import hashlib,json,re,subprocess
R=Path(__file__).resolve().parents[3]
O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance'
E=R/'docs/cod4/audit-20261022/old-world-acceptance/run-05-death'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def top_fields(s):
    # Split only outer SNBT compounds; nested braces/arrays and escaped strings stay intact.
    assert s[0]=='{' and s[-1]=='}'
    parts=[];start=1;depth=0;quoted=False;escape=False
    for i,c in enumerate(s[1:-1],1):
        if quoted:
            if escape:escape=False
            elif c=='\\':escape=True
            elif c=='"':quoted=False
            continue
        if c=='"':quoted=True
        elif c in '{[':depth+=1
        elif c in '}]':depth-=1
        elif c==',' and depth==0:parts.append(s[start:i]);start=i+1
    parts.append(s[start:-1])
    return dict(p.split(':',1) for p in parts if p)
before=json.loads((E/'before-death.json').read_text());after=json.loads((E/'native-owner.json').read_text())
b=top_fields(before['forgeData']);a=top_fields(after['forgeData'])
fields=['dq_p_18','dynasty_merit','dynasty_rank','dynasty_loyalty','dynasty_manual_given']
assert before['uuid']==after['uuid']
assert before['inventory']==after['inventory']
assert all(k in b and k not in a for k in fields)
assert b['PlayerPersisted']==a['PlayerPersisted']
java=sorted((R/'src/main/java').rglob('*.java'))
handler_re=re.compile(r'PlayerEvent\.Clone|PlayerRespawnEvent|LivingDeathEvent')
scan=[]
for p in java:
    text=p.read_text();hits=[{'line':i,'text':s.strip()} for i,s in enumerate(text.splitlines(),1) if handler_re.search(s)]
    if hits:scan.append({'file':str(p.relative_to(R)),'sha256':sha(p),'hits':hits,'test_source':'GameTest' in p.name})
observed_sources=['DynastyStats.java','DynastyManual.java','DynastyMerit.java','DynastyRankPerks.java','DynastyInjury.java','DynastySchoolProgression.java','DynastySlotProgression.java','expansion/ContentProgress.java','expansion/ExpansionSupplies.java','army/ArmyRoster.java','cod3/SecretTracker.java']
source_hashes={str((Path('src/main/java/com/dynasty')/p)):sha(R/'src/main/java/com/dynasty'/p) for p in observed_sources}
H='d0007965821c5ae65ef952a8d5faad7222795545^'
history={}
for name in ['DynastyQuestManager.java','DynastyQuests.java','DynastyFineItems.java']:
    spec=f'{H}:src/main/java/com/dynasty/{name}'
    raw=subprocess.check_output(['git','show',spec],cwd=R)
    (O/('historical-'+name+'.txt')).write_bytes(raw)
    history[name]={'git_object':spec,'content_sha256':hashlib.sha256(raw).hexdigest()}
report={'status':'root_cause_audit_only_not_fixed','research_credit':0,
'world_write_operations':0,'production_java_write_operations':0,
'case':{'uuid':before['uuid'],'same_inventory':True,'native_connection_before':before['nativeConnection'],'native_connection_after':after['nativeConnection'],'game_time_delta':after['gameTime']-before['gameTime'],'lost_permanent_fields':{k:b[k] for k in fields},'PlayerPersisted_unchanged':True,'root_before':b,'root_after':a,'evidence_sha256':{p.name:sha(p) for p in sorted(E.iterdir()) if p.is_file()}},
'sources':source_hashes,'history':history,'event_scan':scan,
'findings':[
'Forge ServerPlayer.restoreFrom copies only PlayerPersisted before posting Clone; keepInventory branch restores inventory/XP, not arbitrary root ForgeData.',
'Current Clone handlers retain school, slots, army, PlayerPersisted, selected paid secret progress; none of the reviewed handlers copies DynastyStats root keys/manual or dq_*.',
'DynastyStats writes progression through explicit merit/loyalty/rebellion/rank methods; reviewed source has no death deduction/reset for these fields. RankPerks recomputes rank from merit, so copying rank alone is insufficient.',
'DynastyInjury.onDeath intentionally adds 25 injury. This is a distinct existing rule; do not rewrite it or add it to progression allowlist without separate scope. Do not claim no death penalty exists.',
'SecretTracker Clone explicitly resets continuous posture/underwater/timed challenges. ExpansionSupplies resets guide/warm state. Full ForgeData copy would violate those choices.',
'Historical dq_p_18 is integer kill progress for quest18 (nine_tailed_fox, need4), NOT completed/claimed. dq_c_ is boolean reward-claimed; dq_e_ boolean event facts. Preserve facts without auto-claiming FTB rewards.',
'Copy typed existing tags using independent tag copies and exact audited keys; no setters that trigger merit multipliers, rank rewards, effects or duplicate manual grants. Absent/invalid keys must not be manufactured.',
'Observed loss is structural missing Clone transfer, not evidence of an intentional merit/rank/loyalty/manual/legacyquest death punishment. This conclusion is bounded to reviewed sources and evidence.'
],
'proposed_permanent_allowlist':[
{'keys':['dynasty_merit','dynasty_rank','dynasty_loyalty','dynasty_rebellion'],'type':'IntTag','reason':'DynastyStats durable character values; preserve both merit and rank, retain existing rank reconciliation'},
{'keys':['dynasty_manual_given'],'type':'ByteTag','reason':'one-time handbook issue flag'},
{'key_family':'dq_p_0..23','type':'IntTag','reason':'historical quest integer counters; use actual catalog bounds, not arbitrary dq_ wildcard'},
{'key_family':'dq_c_0..23','type':'ByteTag','reason':'historical rewards already claimed; no new reward dispatch'},
{'keys':['dq_e_keju','dq_e_rank1','dq_e_minister','dq_e_army','dq_e_calm','dq_e_dim_celestial','dq_e_dim_underworld','dq_e_qilin','dq_e_rank9'],'type':'ByteTag','reason':'historical catalog EVENT targets; preserve only known flags'},
{'key_family':'dynasty_merit_evt_<known event> and dynasty_merit_seen_<known item>','type':'ByteTag','reason':'one-time merit anti-replay facts; finite keys from DynastyMerit, require exact enumeration before implementation'}],
'excluded_or_separate_review':['dynasty_rank_notice (derived)','dynasty_merit_kill_window / dynasty_merit_kill_earned (rate window, not permanent achievement)','dynasty_injury / dynasty_injury_hit (existing injury subsystem)','all immunity/counterattack/cooldown/pose/position state','PlayerPersisted / school / slots / army / cod3_progress_8 and 30 already owned by existing handlers; do not replace whole containers'],
'pending':['1000 valid upstream implementation research before production changes','determine typed malformed-value policy and Clone event priority without clobbering existing handlers','FTB current exact runtime registry book verification and unavailable-mod fallback','native post-fix death, relog, return-from-End and missing-ID old-world QA; current evidence remains pre-fix']}
(O/'progression-source-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'lost':report['case']['lost_permanent_fields'],'inventory_unchanged':True,'event_files_scanned':len(scan),'production_changes':0},ensure_ascii=False))
