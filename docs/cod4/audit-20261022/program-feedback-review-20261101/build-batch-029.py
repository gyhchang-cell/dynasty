#!/usr/bin/env python3
"""Retain actual incomplete Apoli denial study without credit."""
import hashlib
import json
from pathlib import Path

R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent;A=H.parent
B=R/'tools/cod4/legacy-migration-acceptance/helpers/halley-migration/batch-047'
sha=lambda b:hashlib.sha256(b).hexdigest()
mp=B/'source-manifest.json';m=next(x for x in json.loads(mp.read_text()) if x['repo']=='apace100/apoli')
entries={x['path']:x for x in m['files']};refs=[]
def ref(up,a=1,z=None):
 e=entries[up];raw=(R/e['source']).read_bytes();ls=raw.decode().splitlines();z=z or len(ls)
 refs.append({'path':e['source'],'upstream_path':up,'lines':[a,z],'file_sha256':sha(raw),'git_blob_sha1':e['source_blob'],
 'purpose':'Actually read relevant concrete denial/return/synchronization or registration/lifetime context; no per-file credit.',
 'reading_context':'Full file except explicit component subranges; each referenced method complete. Underlying engine/dependency behavior not assumed.'})
pre='src/main/java/io/github/apace100/apoli/'
for f in ['power/PreventEntityUsePower.java','power/PreventBeingUsedPower.java','power/InteractionPower.java','power/Power.java',
          'networking/packet/c2s/PreventedEntityInteractionC2SPacket.java','networking/ModPacketsC2S.java','networking/ModPackets.java',
          'mixin/PlayerEntityMixin.java','Apoli.java','power/factory/PowerFactories.java']:ref(pre+f)
ref(pre+'component/PowerHolderComponentImpl.java',1,238)
ref(pre+'component/PowerHolderComponent.java',151,172)
ref('src/main/resources/fabric.mod.json');ref('src/main/resources/apoli.mixins.json')
lp=A/'immune-feedback-research/reviewed.json';lr=lp.read_bytes();rows=json.loads(lr);by={x['id']:x for x in rows}
comp={
 'spellengine-final-input-and-active-item-control-gates':'Existing final active-policy cancellation/input restrictions; Apoli conditional interaction wrapper alone is not enough to count a new whole refusal/sync lifecycle.',
 'spellengine-client-cast-prediction-reconciles-denial':'Existing actual prediction begin, confirmation and timeout teardown. Apoli empty prevented-interaction server handler and absent local sender cannot be described as comparable server revalidation or reconciliation.',
 'vampirism-native-weapon-attack-refusal-explicit-actor-faction-skill-level-result':'Existing actor eligibility produces explicit reason and eventual attack cancellation. Apoli actor/recipient predicates and configured side effects have no completed explicit feedback receipt here; generic eligibility0.',
 'arcanus-native-final-disabled-component-denial-loses-void-result-before-caller-success-cooldown':'Closest existing lost-final-refusal contract family. Apoli after-return merge may replace a nonaccepted original by PASS, but this is not automatically a second whole family just because a return-merger instead of void hides denial. Need actual end-to-end native caller and power producer.',
 'create-native-cardboard-cancels-attack-but-retains-dismount-and-directed-client-knockback':'Existing refusal retains side effects and actual directed client replay. Apoli configured actions/item replacement can run before FAIL, but abstract callbacks and empty packet receiver do not close a new replay lifecycle.',
 'forbiddenarcanus-native-capture-refusal-versus-interaction-cancel-and-release-failure-settlement':'Existing outer input consumption differs from inner outcome/settlement. Apoli return merge and item actions reinforce the same distinction; not new capture or actual acceptance proof.'}
mlp=A/'legacy-migration-acceptance/reviewed.jsonl';mlr=mlp.read_bytes();ml=[json.loads(l) for l in mlr.decode().splitlines() if l.strip()]
old=next(x for x in ml if x['candidate_id']=='8bb6b4b27a63a597a5c7');keys=['candidate_id','status','family','trigger','input','output','preservation','application_limit','credit']
doc={
 'schema_version':1,'owner':'program-feedback-review-029','repo':m['repo'],'commit':m['commit'],'branch':m['branch'],
 'provenance':{'manifest_path':str(mp.relative_to(R)),'manifest_sha256':sha(mp.read_bytes()),'bare_git_path':str((B/'upstream.git').relative_to(R)),'git_tree':m['git_tree'],'acquisition':'Existing fixed local source and Git only.'},
 'status':'held_no_local_denial_packet_producer_empty_server_consumer_and_unclosed_native_return_contract',
 'research_credit':0,'maximum_proposed_credit':0,'production_changes':False,'runtime_executed':False,
 'semantic_family':'held-apoli-native-entity-interaction-denial-return-and-empty-notification-path',
 'source_refs':refs,
 'dedup_snapshot':{'path':str(lp.relative_to(R)),'sha256':sha(lr),'rows':len(rows),
  'comparisons':[{'accepted_id':k,'full_semantic_decision_read':{a:b for a,b in by[k].items() if a not in ['source_refs','auxiliary_refs']},'distinction':v} for k,v in comp.items()],
  'reading_order':'Six nearest full accepted substantive decisions read before first Apoli candidate source. Relevant migration full decision read later when holder ownership became relevant; no old underlying source reread claimed.',
  'limits':'No new whole mechanism proposed. Conditional return-value loss and generic action predicates do not defeat prior semantic owners.'},
 'migration_overlap_screen':{'path':str(mlp.relative_to(R)),'sha256':sha(mlr),'rows':len(ml),'comparisons':[{'accepted_id':old['candidate_id'],'complete_semantic_decision_read':{k:old[k] for k in keys},'distinction':'Keep full PAL legacy-source recovery owner. Holder/condition/source infrastructure reused only for current interaction context, no new persistence or ability grant credit.'}]},
 'full_chain':[
  {'stage':'actual registration','observation':'fabric.mod.json identifies Apoli main/entity-component/resource entrypoints and apoli.mixins.json containing PlayerEntityMixin. onInitialize registers actual C2S callbacks, command callback and PowerFactories. Two prevent factories registered; each configured factory fixes result FAIL, allows hand/item/bientity and outer activation conditions. Registry does not prove a concrete configured power was acquired by a real gameplay actor in this batch.'},
  {'stage':'conditional holder and exit','observation':'Static getPowers resolves optional entity holder then implementation iterates ConcurrentHashMap values and filters type plus isActive unless includeInactive. Power.isActive all-matches conditions. Exact actor-vs-target precedence is defined by wrapper loops, but order among multiple matching same-role powers is not deterministic from this map. removePower removes a source; only when source list empty invokes removed/lost and at root removes actual map entries. Generic lifecycle observed, command/datapack producer and complete CCA sync/read restoration not expanded.'},
  {'stage':'actual interaction denial and side effects','observation':'WrapOperation around Entity.interact within PlayerEntity.interact first resets shared zero-priority cache PASS and snapshots held item. Iterates actor PreventEntityUsePower first, then target PreventBeingUsedPower, returning first applying executeAction. Conditions use hand/item and pair(actor,target) in both cases, despite power being owned by different entity. executeAction requests optional bientity callback, then performActorItemStuff, then returns configured FAIL. No side guard in these shown methods and no prevention packet send in this wrapper; native client/server invocation frequency unproved.'},
  {'stage':'item mutation before refusal','observation':'performActorItemStuff obtains actual actor hand slot StackReference, applies held callback, optionally sets held slot directly to itemResult, creates another resultingStack reference from current held or itemResult.copy, applies resultItemAction to heldStack (not resultingStack), then puts/offers resultingStack when modified. Configured item result can therefore involve both direct replacement and offer/drop branch. Return value from StackReference.set ignored. No inventory payment/rollback or two-sided consistency guarantee. InventoryUtil/native inventory internals and concrete callbacks not expanded, so no runtime duplication claim.'},
  {'stage':'outer return merge boundary','observation':'Before wrapper also evaluates nonnegative ActiveInteraction powers by priority, with priority0 cached and original entity call still attempted; after hook consumes cache or tries negative powers only when original PASS. End selects original only if it is accepted while new is not, or should swing while new does not; otherwise returns new. If original is nonaccepted/nonswinging FAIL, cache PASS, no after branch runs, new stays PASS and expression chooses new. This can erase a refusal at the return layer if the native method reaches this injected return slice. Complete before/after methods read, but native PlayerEntity.interact control flow, ActionResult implementation and MixinExtras shared-local initialization on other paths are not read: do not assert observed bypass, offhand retry or side-effect duplication.'},
  {'stage':'notification chain explicitly not implemented','observation':'PreventedEntityInteractionC2SPacket encodes hand ordinal then runtime entityID and decoder directly indexes Hand.values. ModPackets old constant aliases this packet type. Apoli.onInitialize→ModPacketsC2S.register installs onPreventedEntityInteraction, whose body is empty in this exact commit. Whole cached source search for class, packet path and PREVENTED_ENTITY_USE finds only definition/codec/registration/alias, no actual gameplay sender. No resolution, state recheck, action replay, reply or expiry work is performed by that handler. External mods could send this public packet, but the local empty handler still supplies no full requested receipt lifecycle.'},
 ],
 'critical_boundaries':[
  'The packet name is not evidence of a real prevented-interaction producer or functional server consumer. This is an explicit0, not a pending+1 wrapper.',
  'Distinguish native wrapper denial from result of entire PlayerEntity.interact; source merge expression can lose a nonaccepted original. Actual native caller path remains a stated gap.',
  'No concrete configured power JSON/grant/acquisition, actual callback gameplay, CCA synchronization or final client feedback lifecycle completed. Do not substitute generic framework registration for the missing producer.',
  'Complete PlayerEntityMixin read for containing before/after methods; other method bodies are context0 and no separate control reference. Two component ranges only, not full418/221-line classes.',
  'Previous Arcanus lost-denial family and migration PAL owner unchanged. Both actor/recipient prevent variants belong to at most one future whole family, not two credits.',
 ],
 'native_gaps':[
  {'missing':'Concrete configured power acquisition and full holder synchronization/actual side-effect callbacks.', 'impact':'Conditional factory plus generic holder mutation is not closed real producer→consumer lifecycle.'},
  {'missing':'Native1.20.2 PlayerEntity.interact/ActionResult/MixinExtras return-slice semantics and final client response.', 'impact':'Return-merger conditional observation only; no verified gameplay refusal bypass.'},
  {'missing':'Local gameplay sender and nonempty prevented-interaction server handler.', 'impact':'No completed notification/reconciliation mechanism exists in the inspected local path; remain0, do not fetch other versions to fill this commit.'},
 ],
 'static_examples_not_executed_tests':[
  {'case':'lost failure predicate','assumptions':'after hook reached; original is not PASS, isAccepted=false and shouldSwingHand=false; cache PASS with ordinary PASS predicates false.', 'derivation':'newResult stays PASS; both preserve-original disjuncts false, so returns PASS. Actual runtime dispatch and enum source unverified.'},
  {'case':'actor-first priority','assumptions':'Both actor-owned prevent and recipient-owned prevent apply to the current hand/item and are active.', 'derivation':'First loop returns after actor executeAction, so recipient loop is skipped. No combined refusal reasons.'},
  {'case':'empty notification receiver','assumptions':'Well-formed packet has been dispatched to onPreventedEntityInteraction.', 'derivation':'Empty body performs no lookup, rejection replay, confirmation or lifecycle cleanup.'},
 ],
 'application':'Require a real refusal producer, explicit final return contract and actual receiver before calling a notification chain complete. Keep actions/payment and native refusal result separate; generic event or packet names are not Boss Immune evidence.',
 'counting':{'formal_baseline_observed':len(rows),'current_credit':0,'whole_family_maximum':0,'helpers_variants_packets_migration_credit':0},
 'next_work':['Continue another unread fixed-local program source; do not fill this empty receiver by borrowing another commit or count the packet wrapper.', 'Preserve conditional return-merger observation for later concrete same-version native-chain work; no current credit or production fix.'],
}
with (H/'immune-reference-batch-029.json').open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'files':len(refs),'lines':sum(x['lines'][1]-x['lines'][0]+1 for x in refs),'credit':0,'baseline':len(rows)}))
