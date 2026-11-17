#!/usr/bin/env python3
"""Record actual denial-to-live-client-explanation chain; coordinator decides credit."""
import hashlib
import json
from pathlib import Path

R=Path('/Users/a15356015027/Desktop/dynasty'); H=Path(__file__).resolve().parent; A=H.parent
B=R/'tools/cod4/legacy-migration-acceptance/helpers/halley-migration/batch-028'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
mp=B/'source-manifest.json'; m=next(x for x in json.loads(mp.read_text()) if x['repo']=='Coders-After-Dark/Reskillable')
entries={x['path']:x for x in m['files']}; refs=[]
pre='src/main/java/codersafterdark/reskillable/'
def ref(f,a=1,z=None):
 e=entries[pre+f];raw=(R/e['source']).read_bytes();z=z or len(raw.decode().splitlines())
 refs.append({'path':e['source'],'upstream_path':e['path'],'lines':[a,z],'file_sha256':sha(raw),'git_blob_sha1':e['source_blob'],
 'purpose':'Concrete refusal producer, payload, actual live HUD consumer and lifecycle; shared skill persistence/registry/render helpers context0.',
 'reading_context':'Full file unless explicit bounded GuiSkills prefix through complete drawSkill. Existing migration semantic decision compared; its underlying sources only reread where explicitly listed here.'})
for f in ['base/LevelLockHandler.java','network/MessageLockedItem.java','network/PacketHandler.java',
 'client/base/HUDHandler.java','Reskillable.java','base/CommonProxy.java','client/base/ClientProxy.java',
 'client/base/ClientTickHandler.java','api/data/RequirementHolder.java','api/requirement/SkillRequirement.java',
 'api/requirement/AdvancementRequirement.java','api/requirement/TraitRequirement.java','network/MessageDataSync.java',
 'api/data/PlayerData.java','api/data/PlayerDataHandler.java','api/requirement/RequirementRegistry.java',
 'base/ConfigHandler.java','api/data/ItemInfo.java','api/data/PlayerSkillInfo.java','ReskillableModAccess.java',
 'lib/LibMisc.java','ReskillableRegistryHandler.java','api/ReskillableAPI.java','skill/SkillAttack.java',
 'api/skill/Skill.java','api/skill/SkillConfig.java','api/data/NBTLockKey.java','api/data/FuzzyLockKey.java',
 'api/data/ModLockKey.java','api/data/GenericNBTLockKey.java','api/data/GenericLockKey.java','api/data/LockKey.java',
 'api/ReskillableRegistries.java','client/base/RenderHelper.java','network/MessageLevelUp.java']: ref(f)
ref('client/gui/GuiSkills.java',1,52)
lp=A/'immune-feedback-research/reviewed.json';lr=lp.read_bytes();rows=json.loads(lr);by={x['id']:x for x in rows}
comp={
 'aether-slider-native-tool-room-refusal-explicit-reason-shared-cooldown':'Existing boss-owned reason/cooldown sends explicit invalid/too-far reason. Here no server cooldown and no failed-requirement witness; client recomputes current requirements from a stack. Four message categories do not earn4.',
 'ars-native-cast-refusal-chat-replacement-ignores-channel':'Existing server-produced textual failure delivered to chat signature replacement. Here packet omits condition list/state and HUD independently reconstructs it from local config and separately synced current skill data. Single slot/replacement alone is overlapping support, not proposed distinction.',
 'vampirism-native-weapon-attack-refusal-explicit-actor-faction-skill-level-result':'Existing actor qualification final denial submits first explicit reason. Reskillable actor eligibility also generic and not new credit alone; proposed distinction is a complete item-only receipt consumed as live local explanation rather than server-reason snapshot.',
 'tf-denial-hint-native-time-window-and-visibility':'Existing failure-driven world hint with source-owned shared1200-tick cadence and visibility attempts. Here static screen HUD and unconditional per-message40 reset; neither time value nor translation/category earns credit.',
 'spellengine-client-cast-prediction-reconciles-denial':'Existing prediction lifecycle matches server declaration and expires unconfirmed casts. Reskillable display has no nonce/declaration reconciliation, no server clearance and no cancellation upon successful retry; hiding is only client clock or replacement.',
 'arcanus-native-final-disabled-component-denial-loses-void-result-before-caller-success-cooldown':'Existing final denial lost before success settlement. Here genericEnforce really cancels its event; possible green requirements under a red rejection header are live client re-evaluation, not evidence that server denial was lost or action succeeded.',
 'spellengine-hud-error-single-slot-lifetime-and-release-reset':'Closest single-slot HUD owner already covers overwrite/tick/fade/world-key absence. Do not count those again or40 versus20. Possible new whole family is actual server refusal serialized as item+category, combined on every render with independently synced current skill state/local lock definitions, including omitted requirement types. If coordinator treats that as same family, merge0.',
 'spellengine-error-reason-vs-attempt-debounce':'Existing reason production separated from attempt debounce. Reskillable has no server attempt throttler and every decoded packet resets HUD; lack of debounce is a limit, not new credit.'}
mlp=A/'legacy-migration-acceptance/reviewed.jsonl';mlr=mlp.read_bytes();ml=[json.loads(x) for x in mlr.decode().splitlines() if x.strip()]
old=next(x for x in ml if x['candidate_id']=='7260450d617a93fcebe1')
keys=['candidate_id','status','family','trigger','input','output','preservation','application_limit','credit']
scan=H/'batch-030-native-source-availability.json';sd=json.loads(scan.read_text())
doc={
 'schema_version':1,'owner':'program-feedback-review-031','repo':m['repo'],'commit':m['commit'],'branch':m['branch'],
 'provenance':{'manifest_path':str(mp.relative_to(R)),'manifest_sha256':sha(mp.read_bytes()),
  'commit_metadata_path':str((B/'provenance/Coders-After-Dark__Reskillable/commit.json').relative_to(R)),
  'tree_metadata_path':str((B/'provenance/Coders-After-Dark__Reskillable/tree.json').relative_to(R)),
  'git_tree':m['git_tree'],'acquisition':'Existing fixed local source and cached commit/tree metadata only. No network, game, archive code execution or1.20.1 substitution.'},
 'status':'pending_independent_semantic_review_maximum_one_live_client_reconstructed_denial_explanation_family',
 'research_credit':0,'maximum_proposed_credit':1,'production_changes':False,'runtime_executed':False,
 'semantic_family':'reskillable-native-item-refusal-receipt-reconstructs-live-client-requirements-with-independent-profile-sync-and-pause-gated-expiry',
 'source_refs':refs,
 'dedup_snapshot':{'path':str(lp.relative_to(R)),'sha256':sha(lr),'rows':len(rows),
  'comparisons':[{'accepted_id':k,'full_semantic_decision_read':{a:b for a,b in by[k].items() if a not in ['source_refs','auxiliary_refs']},'distinction':v} for k,v in comp.items()],
  'reading_order':'First six full substantive accepted decisions plus full migration semantic decision read before candidate source. After HUD path found, full SpellEngine HUD and debounce decisions read before remaining profile/registration/render support source. No old source reread except listed references.',
  'limits':'Maximum1 pending. Single-slot timeout, generic skill gates, four refusal strings, eight skills, helper methods and existing permanent-skill migration all0 additional. Independent reviewer may merge with existing HUD family.'},
 'migration_overlap_screen':{'path':str(mlp.relative_to(R)),'sha256':sha(mlr),'rows':len(ml),'comparisons':[{
  'accepted_id':old['candidate_id'],'complete_semantic_decision_read':{k:old[k] for k in keys},
  'distinction':'Permanent skill-profile rehydration and real gameplay gates already accepted; retain that owner and all migration0. This study proposes only missing actual denial-packet→HUD live reconstruction→client clock suppression lifecycle. Existing migration evidence path screen found no HUDHandler/ClientTickHandler/MessageLockedItem/GuiSkills entry; path absence alone is not semantic proof.'}]},
 'prior_gap_followup':{'batch':30,'evidence_path':str(scan.relative_to(R)),'sha256':sha(scan.read_bytes()),
  'roots':[s['root'] for s in sd['scans']],
  'conclusion':'No exact required1.12.2 native Java source hit in listed workspace/Gradle cache paths or successfully opened archives. Some archives failed to open and are recorded. Bounded negative search, not global absence.030 stays0; no unrelated version used.'},
 'full_chain':[
  {'stage':'registered concrete producer','observation':'Reskillable @Mod constructor installs API/provider; preInit dispatches sided proxy. CommonProxy registers LevelLockHandler/PlayerData events, initializes config and PacketHandler; postInit setupLocks builds actual keys. Registry subscriber creates/registers skills including concrete attack. Default config includes iron_sword wildcard attack5. Skill enabled/default cap32 and default PlayerSkillInfo level1 establish a concrete conditional denial example with that config, not only abstract callbacks. ItemInfo equality ignores metadata in hash but honors wildcard in equality, matching actual sword metadata; NBT/mod lock helpers fully read as context0.'},
  {'stage':'actual qualification refusal','observation':'LivingAttackEvent with true source EntityPlayer reads that actor current MAINHAND at damage event time, not necessarily original projectile weapon. genericEnforce skips noncancelable/null/empty/creative; default enforceFakePlayers includes fake denial but suppresses fake feedback, alternative skips fake. PlayerData.matchStats returnsfalse at first unmet requirement. Event is canceled and tellPlayer sends only to EntityPlayerMP. Default branch cancels before send; alternate sends before cancel. Other block/use/armor routes share categories but are not additional families. Current armor route is not canceling event; it copies/returns or drops invalid armor, clears armor slot then sends. No final aggregate result after every other mod handler is claimed.'},
  {'stage':'item plus category transport','observation':'MessageLockedItem constructor stores stack reference, not copy; byte codec serializes ItemStack and UTF8 message key only. No failing requirement, threshold, server level, target UUID, world, nonce or action generation. PacketHandler registers actual CLIENT handler. onMessage schedules on Minecraft task queue, handleMessage calls HUDHandler.setLockMessage. No local player/world/current item revalidation before updating static slot. ByteBufUtils/native network scheduling internals not expanded; do not assert enqueue-time immutable stack snapshot.'},
  {'stage':'separate live profile data','observation':'Login PlayerData.sync→API→ReskillableModAccess sends MessageDataSync with saveToNBT snapshot of SkillLevels. Client scheduled handler resolves current player through ClientProxy and loadFromNBT→PlayerSkillInfo overwrites level/points/unlocks for included skills. MessageLevelUp actual server handler can levelUp then saveAndSync after its gates; exact XP-helper internals not expanded or credited. No action ID binds these data packets to a particular MessageLockedItem. ConfigHandler reads local lock configuration; config-change load only replaces pending configLocks and does not itself call setupLocks. No same-time configuration/version field in refusal packet.'},
  {'stage':'real client consumer recomputes explanation','observation':'ClientProxy registers HUDHandler and ClientTickHandler. On overlay ALL while lockTime>0, HUD reads current local player data and LevelLockHandler.getSkillLock(lockedItem) every render. Draws translated refusal category header red, then skill icons and requested level numbers red/green according to current local skill level. GuiSkills.drawSkill uses current profile rank and texture; RenderHelper submits concrete textured quad. Thus packet reports rejection category/item while detailed condition explanation is reconstructed from current local definitions and independently synced profile, not server failure witness. It lists all local skill/advancement requirements, not only the one that failed.'},
  {'stage':'render coverage and early exit boundaries','observation':'RequirementRegistry supports skill, adv and trait; HUD separates only SkillRequirement and AdvancementRequirement. Trait/custom requirements still contribute restriction count/box size but are absent from shown detail list. Advancement icons/text show no achieved-state color check. An unresolved advancement causes return after outer pushMatrix and before matching final popMatrix; null display has no guard. This is a static incomplete-restore path, not a runtime graphics failure claim. Ordinary main skill text calls font renderer; translation resources/nativeGL/pixels not evaluated. No asset changed.'},
  {'stage':'explicit lifespan and exits','observation':'setLockMessage replaces static item/message and sets40 on every receipt, with no dedup or throttle. END client tick decrements only when currentScreen null or doesGuiPauseGame false. World-null branch only PlayerDataHandler.cleanup; no HUD clear, dimension/actor key, dead-player clear, successful retry clear or item-switch clear. lockTime<=0 prevents drawing; stored item/message refs are retained. Last<10 uses partialTicks alpha clamped minimum0.05. Repeated receipts can prolong display; pausing can preserve remaining clock. Rendering is not explicitly filtered Pre/Post beyond ElementType.ALL, so do not assert exactly one draw per frame.'},
 ],
 'critical_boundaries':[
  'Proposed distinction is split authority: real server denial plus client-reconstructed current detailed explanation. Not another single-slot/fade/cooldown value reference.',
  'A green local requirement under refusal header is not proof server allowed action or target is immune. No server failed-condition snapshot is transmitted.',
  'Actor eligibility is not Boss target immunity. No actual immune grey-text/audio implementation claimed; ordinary constitution rules unchanged.',
  'Profile synchronization is separate and lacks refusal correlation; do not claim network reorder observed, config mismatch reproduced or guaranteed delivery.',
  'No real server admission bypass demonstrated. LivingAttackEvent cancellation is actual mod action but native Forge dispatch/cross-mod uncancel policy not exhaustively expanded.',
  '40-tick lifetime is pause-gated client ticks, not a wall-clock guarantee or server rate limit. Slots retained after hidden, no world cleanup in searched classes/callers.',
  'Config-change callback load does not rebuild live lock map; do not assert immediate runtime config mutation from editing a file.',
  'Advancement-null restore and missing trait rendering are concrete bounded source observations, not independent credits or production patches.',
  'Copied RenderHelper explicitly attributes Botania; shared rendering helper context0, not a new author/source family.',
 ],
 'native_gaps':[
  {'missing':'Native1.12.2 Forge event dispatch, SimpleNetworkWrapper/ByteBufUtils and Minecraft/font/GL implementations.', 'impact':'Complete mod-owned caller→registered codec/receiver→actual drawing calls and clock read, but no verified network transport, pixels, final cross-mod action outcome or same-version engine internals.'},
  {'missing':'Actual translation/texture assets and default runtime configuration observation.', 'impact':'Only concrete default source entry and render requests claimed, not shipped Chinese wording, icon quality or runtime setup.'},
  {'missing':'Complete XP helper and concrete unlock gameplay paths for arbitrary traits.', 'impact':'Not a survival-acquisition/transaction or full permanent-skill migration proposal. Concrete skill denial example suffices only for this feedback path.'},
 ],
 'static_examples_not_executed_tests':[
  {'case':'concrete iron-sword refusal','assumptions':'Default lock built, enabled attack skill, noncreative real server player attack level1, nonempty iron sword, cancelable LivingAttack event.', 'derivation':'attack1<5 → canPlayerUseItemfalse → canceled plus itemLocked packet. Client local attack1/configsame draws red5.'},
  {'case':'profile update while old denial slot remains','assumptions':'Refusal slot lockTime>0 and later independent profile packet sets current local attack5; no new refusal.', 'derivation':'Header remains old red refusal, current level comparison renders requirement5 green. HUD does not clear upon requirement becoming satisfied.'},
  {'case':'second item overwrites and pause extends','assumptions':'Existing slot remaining1; second decoded refusal received; current screen pauses.', 'derivation':'Second stack/key replace first and time becomes40. Paused client tick skips decrement; no two-item history or per-target isolation.'},
  {'case':'supported trait requirement omitted from detail','assumptions':'A live lock contains enabled TraitRequirement through registered trait handler.', 'derivation':'Server achievedByPlayer participates in refusal; HUD list filters ignore that type although total count sizes box. Actual configured trait-specific scene not exercised.'},
 ],
 'application':'Carry the authoritative failed-condition receipt when explanation must match rejection time. If showing current requirements instead, explicitly distinguish them and scope lifecycle by actor/world/action; do not mistake HUD timeout for transport throttling.',
 'counting':{'formal_baseline_observed':len(rows),'current_credit':0,'whole_family_maximum':1,'helpers_variants_shared_payment_migration_credit':0},
 'next_work':['Independent coordinator semantic review may accept at most one or merge0 with existing HUD/migration scope; no master edit by worker.', 'Continue unread original program source under fixed-local constraints;030 gaps remain0 and027 is not redone.'],
}
with (H/'immune-reference-batch-031.json').open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'files':len(refs),'lines':sum(x['lines'][1]-x['lines'][0]+1 for x in refs),'credit':0,'maximum_pending':1,'baseline':len(rows)}))
