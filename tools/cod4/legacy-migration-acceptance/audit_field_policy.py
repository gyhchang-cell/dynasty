"""Inventory source evidence + explicitly reviewed root field policy, never a runtime copier."""
from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance'
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base='src/main/java/com/dynasty/'
rows=[]
def add(keys,typ,source,reason,status='permanent_candidate'):
    p=R/base/source
    rows.append({'keys':keys,'nbt_type':typ,'status':status,'source':base+source,'source_sha256':hashfile(p),'reason':reason})
add(['dynasty_merit','dynasty_rank','dynasty_loyalty','dynasty_rebellion'],'IntTag','DynastyStats.java','four durable character values; rank is derived but preserve its original tag alongside merit, existing RankPerks reconciliation remains authoritative')
add(['dynasty_manual_given'],'ByteTag','DynastyManual.java','one-time giveOnce handbook receipt; otherwise relog may issue again')
events=['keju','minister','army','qilin','dim_celestial','dim_underworld']
items=['dragon_crystal','xuantian_jade','dragon_emperor_seal','emperor_bone','jade','phoenix_feather','rebel_head','eunuch_token','sky_token','jade_seal','official_seal','edict','tiger_tally','blueprint','bronze_ingot','silver_ingot','refined_steel','cinnabar']
add(['dynasty_merit_evt_'+s for s in events],'ByteTag','DynastyMerit.java','onEvent switches only these six event names to positive reward, then writes once flag')
add(['dynasty_merit_seen_'+s for s in items],'ByteTag','DynastyMerit.java','onFirstObtain positive-value cases; 18 finite first-pickup receipts prevent replay')
add(['dynasty_gift_'+s for s in ['gilded_mace','supreme_sword','seven_star_saber','sunbow']],'ByteTag','DynastyWeaponGifts.java','grant once from rank/boss kinds/daytime phoenix; copy receipts without invoking grant')
add(['dynasty_boss_kinds'],'IntTag','DynastyWeaponGifts.java','durable distinct boss count, threshold five unlocks saber; coupled to list')
add(['dynasty_boss_kinds_list'],'StringTag','DynastyWeaponGifts.java','comma-separated distinct-boss set for count anti-duplication; copy together with count, do not recompute/grant here')
add(['dynasty_festival_day'],'StringTag','DynastyWorldEvents.java','latest festival:LocalDate receipt is bounded-repeat anti-replay, not an active buff/expiry; preserve existing receipt across death without triggering festival')
bosses=['dragon_emperor','undead_first_emperor','nine_heaven_general','dragon_king','rebel_general','eunuch_mastermind','phoenix','qilin','nian_beast','nine_tailed_fox']
add(['dynasty_firstkill_'+s for s in bosses],'ByteTag','DynastyBossCombat.java','root legacy first-kill receipts; current grant checks root OR PlayerPersisted and migrates receipts on check. ArmyEncounters prerequisite still reads root; retain known root receipts without writing/replacing PlayerPersisted')
add(['DynastyEventMonsterKills'],'IntTag','worldevent/DynastyWorldEventManager.java','cumulative hostile kills capped10000; xuanniao_zhige eligibility requires100, no time-window/reset shown')
add(['DynastyXuanniaoBlessing'],'IntArrayTag(UUID)','worldevent/DynastyWorldEventManager.java','last blessed event instance UUID is anti-replay receipt for equipment repair/reward effects, not effect duration; preserve receipt only, never reapply buffs','per_event_receipt_candidate')
add(['dynasty_merit_kill_window','dynasty_merit_kill_earned'],'LongTag/IntTag','DynastyMerit.java','10-minute kill income cap window, not permanent achievement; separate future policy if death-reset exploit addressed','exclude_temporary_rate_window')
add(['dynasty_rank_notice'],'IntTag','DynastyStats.java','derived next-rank reminder; no durable source-of-truth','exclude_derived')
add(['DynastyArmyPermitUntil'],'LongTag','worldevent/WorldEventItems.java','travel document sets current gameTime+12000 and checks future interval <=12000; active time-limited permit, not permanent unlocking','exclude_expiry')
add(['dynasty_injury','dynasty_injury_hit'],'IntTag/LongTag','DynastyInjury.java','distinct injury subsystem and intentional death+25; no change through this migration','exclude_other_rule')
add(['DynastyCompassNext'],'LongTag','DynastyCompassBridge.java','navigation request five-second cooldown','exclude_cooldown')
add(['PlayerPersisted'],'CompoundTag','expansion/ContentProgress.java','native and existing handlers retain this container; must not replace/merge entire container from new repair','existing_owner_no_duplicate')
add(['PlayerPersisted.dynastyCod4'],'CompoundTag','expansion/EquipmentBehaviors.java','run04 two-client native death/C2S receipt verifies lastStand/cicada/guardsUntil/guardGeneration original deadlines and no early reproc; existing owner handles this nested saved container. New root migration must never copy/replace/rebase it. Evidence armor-clone-boundary.json; local QA zero external reference credit','existing_owner_no_duplicate')
for src,reason in [('DynastySchoolProgression.java','school progression has own Clone handler'),('army/ArmyRoster.java','army roster has own Clone handler'),('DynastySlotProgression.java','slot milestones in PlayerPersisted have own Clone handler'),('cod3/SecretTracker.java','PlayerPersisted paid receipts and selected cod3_progress_8/30 own Clone policy; other challenges intentionally reset')]:
    rows.append({'source':base+src,'source_sha256':hashfile(R/base/src),'status':'existing_owner_no_duplicate','reason':reason})
scan=[]
for p in sorted((R/base).rglob('*.java')):
    if 'GameTest' in p.name:continue
    code=p.read_text()
    if 'getPersistentData(' in code:
        scan.append({'source':str(p.relative_to(R)),'sha256':hashfile(p),'direct_persistent_access_lines':[i for i,s in enumerate(code.splitlines(),1) if 'getPersistentData(' in s],'status':'search_candidate_only_not_full_semantic_review'})
legacy={'source_commit':'d0007965821c5ae65ef952a8d5faad7222795545^','progress_keys':['dq_p_'+str(i) for i in range(24)],'claim_keys':['dq_c_'+str(i) for i in range(24)],'event_keys':['dq_e_'+s for s in ['keju','rank1','minister','army','calm','dim_celestial','dim_underworld','qilin','rank9']],'types':{'dq_p_':'IntTag','dq_c_':'ByteTag','dq_e_':'ByteTag'},'scope':'known historical24quest catalog only; typed tag preservation not auto mapping to FTB tasks or granting rewards'}
result={'status':'partial_source_semantic_audit_not_all_permanent_progress','runtime_implementation_produced':False,'gate_required':1000,'source_access_candidate_files':len(scan),'explicit_field_policy':rows,'historical_quest_policy':legacy,'access_inventory':scan,'limits':['76 direct access source files are search candidates, not all semantically reviewed; aliases and wrappers may add more','DynastyXuanniaoBlessing is event receipt, separate from copying active effects; native death coverage not yet tested','unreviewed preferences/modes, NPC interactions, loaded challenge state and other wrappers remain excluded until sourced','no FTB progress index mapping verified; no realm/dungeon/bounty world-ledger restoration verified','legacy firstkill current-source migration and existing Clone ownership must be rechecked immediately before eventual production change','permanent values in this policy are proposals, not evidence all keys were present/lost in run05; run05 proves only observed fields']}
(O/'permanent-field-policy.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'direct_access_files':len(scan),'permanent_candidate_keys':sum(len(x.get('keys',[])) for x in rows if x['status']=='permanent_candidate'),'per_event_receipt_keys':1,'legacy_catalog_keys':57,'all_permanent_audited':False},ensure_ascii=False))
