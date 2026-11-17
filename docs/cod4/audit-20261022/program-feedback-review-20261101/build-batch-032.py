#!/usr/bin/env python3
"""Bounded local sidestep-control lifecycle proposal. No ledger or source writes."""
import hashlib
import json
from pathlib import Path

R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent;A=H.parent
B=R/'tools/cod4/legacy-migration-acceptance/helpers/halley-migration/batch-028'
sha=lambda b:hashlib.sha256(b).hexdigest()
mp=B/'source-manifest.json';m=next(x for x in json.loads(mp.read_text()) if x['repo']=='Coders-After-Dark/Reskillable')
entries={x['path']:x for x in m['files']};pre='src/main/java/codersafterdark/reskillable/'
priorp=H/'immune-reference-batch-031.json';prior=json.loads(priorp.read_text())
priorrefs={x['upstream_path']:x for x in prior['source_refs']};refs=[]
newfiles=['skill/agility/TraitSidestep.java','network/MessageDodge.java','client/gui/handler/KeyBindings.java',
 'api/unlockable/Trait.java','api/unlockable/Unlockable.java','api/unlockable/UnlockableConfig.java',
 'network/MessageUnlockUnlockable.java','skill/SkillAgility.java','client/gui/GuiSkillInfo.java','api/event/UnlockUnlockableEvent.java']
reuse=['Reskillable.java','ReskillableRegistryHandler.java','lib/LibMisc.java','base/CommonProxy.java',
 'client/base/ClientProxy.java','client/base/ClientTickHandler.java','network/PacketHandler.java',
 'network/MessageDataSync.java','api/data/PlayerData.java','api/data/PlayerDataHandler.java',
 'api/data/PlayerSkillInfo.java','api/ReskillableAPI.java','ReskillableModAccess.java',
 'api/skill/Skill.java','api/skill/SkillConfig.java','api/data/RequirementHolder.java',
 'api/requirement/SkillRequirement.java','api/requirement/RequirementRegistry.java','api/ReskillableRegistries.java']
for f in newfiles+['client/gui/GuiSkills.java']+reuse:
 e=entries[pre+f];raw=(R/e['source']).read_bytes();n=len(raw.decode().splitlines())
 origin='new_full_file_read_in032'
 if f in reuse:
  old=priorrefs[pre+f];assert old['file_sha256']==sha(raw) and old['lines']==[1,n]
  origin='reused_complete031_read_with_unchanged_hash_not_reread_or_recredited'
 elif f=='client/gui/GuiSkills.java':
  assert priorrefs[pre+f]['lines']==[1,52] and priorrefs[pre+f]['file_sha256']==sha(raw)
  origin='031_read1_52_plus032_new_read53_182_full_class_now_covered'
 refs.append({'path':e['source'],'upstream_path':e['path'],'lines':[1,n],'file_sha256':sha(raw),'git_blob_sha1':e['source_blob'],
  'purpose':'Whole local sidestep producer/eligibility/velocity/HUD/clock path or explicit0 registration/profile/unlock context.',
  'reading_context':origin})
lp=A/'immune-feedback-research/reviewed.json';lr=lp.read_bytes();rows=json.loads(lr);by={x['id']:x for x in rows}
sid='reskillable-native-item-refusal-receipt-reconstructs-live-client-requirements-with-independent-profile-sync-and-pause-gated-expiry'
comp={
 'ars-knockback-resistance-final-motion-gate':'Existing target resistance gates externally imposed movement. Sidestep is own-client input overwriting absolute velocity with no resistance/damage event. Not a new immunity or generic setMotion wrapper; proposed distinction must be the full input recognition/two-clock/control feedback lifecycle.',
 'combatroll-client-target-bound-feedback-validation':'Existing server S2C runtime-ID roll animation receipt to client sound/animation. This source has no actual dodge send or roll receipt; local key samples directly set own velocity/cooldown and local HUD. Do not call missing authority a new server validation.',
 'spellengine-native-evasion-eligibility-with-explicit-feedback':'Existing actual native damage refusal plus explicit evasion event/animation. Sidestep does not cancel damage, set invulnerability or emit an evasion receipt; it is movement control only. Do not infer iframe protection from the name.',
 'spellengine-client-cast-prediction-reconciles-denial':'Existing server-declaration reconciliation and prediction teardown. Sidestep has no pending request/ack/nonce/timeout reconciliation. Its recognizer samples held key state using pause-gated global game ticks, while its cooldown ticks independently when END events arrive.',
 'spellengine-error-reason-vs-attempt-debounce':'Existing held-use attempt flag reset differs from sampling any KeyInputEvent while left/right held. No release edge/event key check here, and timestamp is updated before dodge motion gates. A true second key press is not required by this code.',
 sid:'Accepted031 historical refusal receipt/current detailed explanation unchanged. This batch reuses only needed registration/profile support and separately reads sidestep producer. Two clocks interact here: pause-gated ticksInGame for input recognition versus unconditional delivered-END cooldown decrement, not another40/20 HUD duration variant. Full031 accepted decision read as comparator only; no repeated acceptance audit.'}
mlp=A/'legacy-migration-acceptance/reviewed.jsonl';mlr=mlp.read_bytes();ml=[json.loads(x) for x in mlr.decode().splitlines() if x.strip()]
old=next(x for x in ml if x['candidate_id']=='7260450d617a93fcebe1')
old_snap=prior['migration_overlap_screen']['comparisons'][0]['complete_semantic_decision_read']
assert all(old[k]==v for k,v in old_snap.items())
receipt=A/'immune-feedback-research/coordinator-reskillable-live-denial-acceptance-20261103.json'
assert sha(receipt.read_bytes())=='8a4efecf3c27ab61ea69fe795354cb69d4472132e9dec6f3c68340c6d15bcecd'
doc={
 'schema_version':1,'owner':'program-feedback-review-032','repo':m['repo'],'commit':m['commit'],'branch':m['branch'],
 'provenance':{'manifest_path':str(mp.relative_to(R)),'manifest_sha256':sha(mp.read_bytes()),
  'commit_metadata_path':str((B/'provenance/Coders-After-Dark__Reskillable/commit.json').relative_to(R)),
  'tree_metadata_path':str((B/'provenance/Coders-After-Dark__Reskillable/tree.json').relative_to(R)),
  'git_tree':m['git_tree'],'acquisition':'Existing local pinned source and cached commit/tree metadata only; no network/native version substitution.'},
 'status':'pending_independent_scope_and_semantic_review_maximum_one_local_control_lifecycle_not_damage_immunity',
 'research_credit':0,'maximum_proposed_credit':1,'production_changes':False,'runtime_executed':False,
 'semantic_family':'reskillable-native-held-key-event-sidestep-velocity-control-with-pause-split-recognition-and-recharge-clocks',
 'source_refs':refs,
 'prior_read_reuse':{'path':str(priorp.relative_to(R)),'sha256':sha(priorp.read_bytes()),
  'new_full_files':len(newfiles),'new_additional_GuiSkills_lines':[53,182],'reused_full_files':len(reuse),
  'limits':'Prior accepted support reused with exact file hash/range, not newly reread, new source or added credit. GuiSkills prefix1–52 already read; remainder newly read.'},
 'dedup_snapshot':{'path':str(lp.relative_to(R)),'sha256':sha(lr),'rows':len(rows),
  'comparisons':[{'accepted_id':k,'full_semantic_decision_read':{a:b for a,b in by[k].items() if a not in ['source_refs','auxiliary_refs']},'distinction':v} for k,v in comp.items()],
  'reading_order':'Ars motion gate, CombatRoll and SpellEngine actual evasion full decisions before Sidestep. After source showed local clocks/input, complete prediction/debounce and031 final accepted semantic decision read before remaining unlock/GUI consumer context. No re-audit of031 original36 source ranges.',
  'limits':'One maximum candidate only if coordinator considers input-driven local movement-control lifecycle in original scope and semantically distinct. Otherwise retain0. No credit for constants, left/right variants, unused packet, missing authority or shared profile.'},
 'migration_overlap_screen':{'path':str(mlp.relative_to(R)),'sha256':sha(mlr),'rows':len(ml),
  'comparisons':[{'accepted_id':old['candidate_id'],'complete_semantic_decision_read':old_snap,
  'distinction':'Full semantic decision already read in031, unchanged content verified/reused. Permanent skill storage, server unlock payment/profile sync and ordinary gates remain with old migration owner; sidestep input/motion/HUD clocks are separate proposed local-control object. No new Clone/acquisition credit.'}]},
 'accepted031_update':{'receipt_path':str(receipt.relative_to(R)),'sha256':sha(receipt.read_bytes()),'formal_count_observed':len(rows),
  'clarifications':['MessageLevelUp Pre cancellation can still saveAndSync unchanged values; no success inference from sync.','GuiSkills.drawSkill reads getRank before later HUD getLevel clamp; no equivalence assumption.'],
  'limits':'Receipt observed and reused;031 not self-merged, rewritten or recredited.030 remains0 with saved same-version local gaps.'},
 'full_chain':[
  {'stage':'registered actual trait and local input hooks','observation':'Existing ReskillableRegistryHandler.registerTraits actually constructs TraitSidestep. Constructor binds agility, default cost10, agility26/defense20 requirements and registers this instance on event bus only on physical client. Trait/Unlockable obtains config and actual parent skill. This subscription is separate from PlayerData.forEachEventHandler ability dispatch and occurs without an explicit enabled guard in Sidestep. OnKeyDown later checks unlocked membership and not sneaking; no isEnabled check there. Existing disabled/unknown profile rules not changed.'},
  {'stage':'concrete acquire-and-sync context','observation':'Existing ClientProxy key-binding registration plus newly read KeyBindings opens actual GuiSkills; full remainder GuiSkills click opens GuiSkillInfo. Skill-info hover computes not-unlocked and enough-points; left click sends MessageUnlockUnlockable. Registered SERVER handler obtains current context player, registry skill/unlockable, checks not already unlocked, points, matchStats and cancelable Pre, then PlayerSkillInfo.unlock subtracts cost/adds object and calls onUnlock; Post follows. saveAndSync is after conditional, so rejected purchase can sync unchanged. Existing MessageDataSync delivers included unlock registry keys into current local profile; that same isUnlocked(this) is input gate. Sender not arbitrary abstract callback. No parent-skill validation/unknown-ID robustness or survival-economy guarantee added.'},
  {'stage':'held-state event sampling recognizer','observation':'onKeyDown returns while cd>0, otherwise dereferences current mc.player/profile without explicit null guard and skips locked/sneaking. It does not inspect which key generated event, event press/release state, currentScreen or a release edge. If left key is currently held, stores global ClientTickHandler.ticksInGame into leftDown, compares new-old<4 and calls dodge(left); else right analog. Left wins when both held. No >=0 bound or first-sample initialized flag; default last values0. Timestamp is stored before dodge checks, so failed motion attempt can prime another held-key event. This is event sampling, not proved two distinct presses.'},
  {'stage':'actual local movement write','observation':'dodge requires not flying, onGround, moveForward<0 and sprint key physically down; input caller already checks unlocked/not sneaking/cd. It computes yaw-facing horizontal unit vector, cross with vertical sign for side and scales1.25. Writes motionX/motionY/motionZ absolutely (Y0), then cd20. No target, damage cancellation, immunity interval, resistance lookup, server request, reply or motion rollback is coded in this local path. Public dodge itself lacks unlocked/sneak/cd gate, but only actual internal caller observed; no external misuse claimed.'},
  {'stage':'two different clock policies','observation':'Reused ClientTickHandler END increments ticksInGame only if no GUI or GUI does not pause. Sidestep.clientTick independently decrements cd>0 on every delivered END event, without checking screen/world/player/eligibility. Thus if END events are delivered while a pausing screen freezes ticksInGame, recharge can finish while last-input difference stays small. Native event delivery frequency under pause not inspected, so state conditional, not reproduced timing exploit. Both clocks are session objects/fields with no shown world-change reset; leftDown/rightDown andcd have no per-player dimension identity or explicit death/lock clear.'},
  {'stage':'real feedback consumer and end','observation':'Trait itself subscribes RenderGameOverlayEvent.Post ALL. If player not flying, width=min(int((cd-partialTicks)*2),40); positive width draws fixed gray track and white remaining bar via Gui.drawRect. At cd0 width nonpositive and bar suppressed; no input timestamps cleared. HUD does not require currently unlocked/enabled and has no null-player guard. Flight hides bar while cooldown continues, not a reset; there is no server feedback receipt. Buffer/color requests inspected only, no visual/game/audio execution.'},
  {'stage':'packet name is not authority or cost evidence','observation':'Full cached source search finds MessageDodge only in class/registration, no new MessageDodge or other local gameplay sender. Empty payload is registered SERVER; handler schedules, resolves sender then schedules addExhaustion0.3. It neither checks trait/CD/movement nor sets movement nor confirms action. Without actual sender cannot attribute fatigue spending to local dodge. Public external integration may send it, but this batch proves none. Not an extra packet mechanism or closed server movement-validation chain.'},
 ],
 'critical_boundaries':[
  'Maximum1 proposed for complete mod-owned local input recognition→qualified absolute motion→independent recharge→HUD hide lifecycle, not damage immunity or server reconciliation.',
  'No release edge is required by recognizer code. Conditional second delivered key event while left remains held can trigger; native actual event delivery not asserted.',
  'ClientTick ticksInGame pauses on pausing GUI; Sidestep cd lacks that guard. Do not claim wall-clock seconds or paused native engine event frequency.',
  'No actual MessageDodge producer means no verified fatigue fee, authorization, acknowledgement, replay or refund. Missing authority is a limit, not credit.',
  'KeyInputEvent and HUD paths lack explicit player/world null guards; possible unsafe invocation only, no runtime crash reproduction.',
  'Permanent trait acquisition/profile support reuses exact031 hashes and ranges only. No registry/trait/packet/method counts credit.',
  'No sound triggered by dodge source. Source-read GUI click sound call is context only; no computer/game sound enabled.',
 ],
 'native_gaps':[
  {'missing':'Minecraft1.12.2 native input event generation, client movement integration and server position correction.', 'impact':'Do not claim actual two-tap UX, net displacement, bypass, server acceptance or anti-cheat behavior. Candidate is bounded mod-owned local-control lifecycle only.'},
  {'missing':'Native paused client tick scheduling and actual HUD pixels.', 'impact':'Pause-split consequence conditional on delivered END events. Draw calls and source formula, not visual acceptance.'},
  {'missing':'Any local MessageDodge sender.', 'impact':'No actual exhaustion/authority chain established. The registered receiver is support0, never counted alone.'},
 ],
 'static_examples_not_executed_tests':[
  {'case':'second event without release edge','assumptions':'Unlocked, cd0, not sneaking/flying, grounded, backward+sprint, left held; key events arrive at ticks100 then102.', 'derivation':'First writes leftDown100; second difference2<4 calls dodge irrespective of event key, sets velocity andcd20. No release-state test.'},
  {'case':'first early-session sample','assumptions':'Default leftDown0; eligible key event while ticksInGame2.', 'derivation':'2-0<4 so source accepts one sample. No second actual press proven/required by code.'},
  {'case':'failed attempt primes retry','assumptions':'Held-left sample writes t100 but player airborne; next sample at101 now grounded and other gates pass.', 'derivation':'First dodge returns withoutCD but retains timestamp; second compares1 and sets movement/cd.'},
  {'case':'pause splits clocks','assumptions':'After a dodge20 delivered END events occur while current pausing GUI keeps ticksInGame fixed.', 'derivation':'cd reaches0 but input sampling clock and prior timestamp do not advance; after GUI close, small delta can remain. Native delivery assumption unverified.'},
 ],
 'application':'Input recognizers should distinguish real press edges from held-state samples, and use a documented consistent clock. Treat movement application, local cooldown bar and server authority as separate claims; do not infer immunity or payment from an unused message name.',
 'counting':{'formal_baseline_observed':len(rows),'current_credit':0,'whole_family_maximum':1,'variants_helpers_shared_profile_credit':0},
 'next_work':['Coordinator review bounded local control scope and semantic distinctness; accept at most1 or retain0. No ledger self-edit.', '030 native gaps remain0;031 already accepted468 baseline, no repeated review.'],
}
with (H/'immune-reference-batch-032.json').open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'files':len(refs),'cited_lines':sum(x['lines'][1] for x in refs),'new_files':len(newfiles),'new_lines':sum(len((R/entries[pre+f]['source']).read_text().splitlines()) for f in newfiles)+130,'maximum_pending':1,'credit':0,'baseline':len(rows)}))
