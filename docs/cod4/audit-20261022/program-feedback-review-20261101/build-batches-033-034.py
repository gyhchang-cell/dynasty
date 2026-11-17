#!/usr/bin/env python3
"""Save bounded fixed-local research only. No master or production writes."""
import hashlib
import json
import subprocess
from pathlib import Path

R = Path('/Users/a15356015027/Desktop/dynasty')
H = Path(__file__).resolve().parent
A = H.parent
sha = lambda b: hashlib.sha256(b).hexdigest()

def save(name, value):
    with (H/name).open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')

def pinned(batch, repo):
    base = R/f'tools/cod4/legacy-migration-acceptance/helpers/halley-migration/batch-{batch:03}'
    mp = base/'source-manifest.json'
    m = next(x for x in json.loads(mp.read_text()) if x['repo'] == repo)
    return m, {
        'repo':repo, 'commit':m['commit'], 'branch':m.get('branch'), 'tag':m.get('tag'),
        'manifest_path':str(mp.relative_to(R)), 'manifest_sha256':sha(mp.read_bytes()),
        'commit_metadata_path':str((base/'provenance'/repo.replace('/', '__')/'commit.json').relative_to(R)),
        'tree_metadata_path':str((base/'provenance'/repo.replace('/', '__')/'tree.json').relative_to(R)),
        'git_tree':m['git_tree'],
        'acquisition':'Existing fixed local sources and cached Git commit/tree metadata. No network or upstream execution.'}

def refs(m, prefix, specifications, purpose):
    entries = {e['path']:e for e in m['files']}
    result = []
    for name, ranges in specifications:
        e = entries[prefix+name]
        raw = (R/e['source']).read_bytes()
        total = len(raw.decode().splitlines())
        for bounds in ranges or [[1,total]]:
            assert 1 <= bounds[0] <= bounds[1] <= total
            result.append({'repo':m['repo'], 'commit':m['commit'], 'path':e['source'],
                'upstream_path':e['path'], 'lines':bounds, 'file_sha256':sha(raw),
                'git_blob_sha1':e['source_blob'], 'purpose':purpose,
                'reading_context':'Actual source read this work interval; full file only if range1..EOF; bounded ranges otherwise. No credit by file/line/helper.'})
    return result

lp=A/'immune-feedback-research/reviewed.json'
lr=lp.read_bytes(); rows=json.loads(lr); by={x['id']:x for x in rows}
def comparisons(mapping, order):
    return {'path':str(lp.relative_to(R)), 'sha256':sha(lr), 'rows':len(rows),
        'reading_order':order,
        'comparisons':[{'accepted_id':key,
            'full_semantic_decision_read':{k:v for k,v in by[key].items() if k not in ['source_refs','auxiliary_refs']},
            'distinction':value} for key,value in mapping.items()]}

receipt=A/'immune-feedback-research/coordinator-reskillable-held-input-sidestep-acceptance-20261103.json'
assert sha(receipt.read_bytes())=='6552a228ee829cb863e122f9e0de0db128b9400f6cd0eac4d7a6edcb4bc1cc94'
baseline={'formal_count_observed':len(rows), 'gap_to1000':1000-len(rows),
    'ledger_path':str(lp.relative_to(R)), 'ledger_sha256':sha(lr),
    'accepted032_receipt_path':str(receipt.relative_to(R)), 'accepted032_receipt_sha256':sha(receipt.read_bytes()),
    'clarification':'Coordinator corrected omitted30 already-read source_refs without new credit. Both purchase GUIs return doesGuiPauseGame=false; pause split requires another actually pausing GUI with delivered END events. No032 re-audit or self-merge.'}

rq,rqp=pinned(38,'Ladysnake/Requiem')
rqrefs=refs(rq,'src/main/java/ladysnake/requiem/',[
 ('common/possession/item/OverrideFailure.java',None),
 ('common/possession/item/OverrideCheckResult.java',None),
 ('common/possession/item/CureItemOverride.java',None),
 ('common/possession/item/HealingItemOverride.java',[[35,132]]),
 ('common/possession/item/PossessionItemOverrideWrapper.java',[[35,184]]),
 ('mixin/common/possession/gameplay/ItemStackMixin.java',None),
 ('common/possession/item/InstancedItemOverride.java',[[35,58]]),
 ('common/possession/item/PossessionItemOverride.java',[[35,51]]),
 ('common/possession/item/OverridableItemStack.java',[[35,52]]),
 ('common/RequiemRegistries.java',[[35,76]]),
 ('common/VanillaRequiemPlugin.java',[[436,498]]),
 ('common/entity/SkeletonBoneComponent.java',[[35,124]])],
 'Bounded uncredited item override framework, containing methods, concrete action implementation and actual Mixin caller; missing rule data/transport remain gaps.')
inventory=subprocess.run(['rg','--files','--hidden','-g','!.git','tools','docs'],cwd=R,text=True,capture_output=True,check=True)
paths=inventory.stdout.splitlines()
hits=[p for p in paths if ('requiem' in p.lower() and (p.lower().endswith(('.jar','.zip','.tar.gz')) or 'mob_items' in p.lower() or 'mixins.json' in p.lower() or 'fabric.mod.json' in p.lower())) or ('blabber' in p.lower() and p.endswith('.java'))]
availability={'command':['rg','--files','--hidden','-g','!.git','tools','docs'],
    'working_directory':str(R),'paths_scanned':len(paths),'inventory_sha256':sha(inventory.stdout.encode()),
    'filename_filter':'Requiem paths with archive/JAR, mob_items, mixins.json or fabric.mod.json; or Blabber Java paths.',
    'matches':hits,'network_requests':0,
    'limits':'Bounded filename inventory only; no claim about outside roots, ignored files, embedded archive members or differently named dependency sources. Git tree metadata alone is not actual JSON rule content.'}
save('batch-033-local-rule-availability.json',availability)
doc33={'schema_version':1,'owner':'program-feedback-review-033','repo':rq['repo'],'commit':rq['commit'],
    'provenances':[rqp],'status':'HELD_ZERO_MISSING_CONCRETE_RULE_DATA_MIXIN_REGISTRATION_AND_EXTERNAL_REGISTRY_TRANSPORT',
    'research_credit':0,'maximum_proposed_credit':0,'production_changes':False,'runtime_executed':False,
    'source_refs':rqrefs,'baseline':baseline,
    'availability':{'path':str((H/'batch-033-local-rule-availability.json').relative_to(R)), 'sha256':sha((H/'batch-033-local-rule-availability.json').read_bytes())},
    'dedup_snapshot':comparisons({
        'wizardry-possession-native-melee-capability-refusal':'Possessed item override is not native melee capability denial; no credit for possession name or proxy wrapper.',
        'wizardry-possession-control-release-restores-native-actor':'No proven complete possession release/restoration lifecycle in this bounded item selection read.',
        'vampirism-native-action-denial-result-and-side-effect-order':'PASS/FAIL and side-effect order are already general nearby concerns. Missing concrete rule producer prevents a new closed instance.',
        'forbiddenarcanus-native-capture-refusal-versus-interaction-cancel-and-release-failure-settlement':'Do not confuse interaction result with capture/release settlement; separate cure-on-entity RETURN mixin is context only.',
        'arcanus-native-final-disabled-component-denial-loses-void-result-before-caller-success-cooldown':'Finish maps result value and may set cooldown independently of success, but without concrete registry data this remains an uncredited framework observation.'},
        'Five complete nearest semantic decisions read before source. No migration novelty claimed or old source acceptance rerun.'),
    'observations':[
        'tryUse and tryFinishUsing each clear transient use-time override, get current possessed host, and select from current registry again. No retained selected rule links start and finish. Stream sorted descending priority; first shortCircuits result wins, otherwise first fallback retained. Enabled flag and mob predicate precede test.',
        'ItemStackMixin use HEAD returns present non-PASS override. finishUsing HEAD applies only player, maps any non-PASS result to its value, and cancels native finish even for FAIL. PASS filtered out, restoring native path. This is code behavior, not a delivered runtime interaction.',
        'Tooltip selection keeps non-short-circuit fallbacks until a short-circuit entry replaces them with only its optional tooltip or empty. It is not necessarily the same visible feedback as use-time selection.',
        'Cure tests canCure/reagent/possessed state, sets duration48 and use hand, then finish calls a helper that rechecks canCure before curing/debit. Healing tests item and wounded host, chooses immediate or timed finish; finish calls usage then independently applies configured cooldown if positive. Heal-with-food and replace-bone return typed success/failure with effects/debit ordering inspected.',
        'SkeletonBoneComponent replacement increments counter/heals before optional conversion; failed conversion is not rollback. No concrete component-attachment or item rule producer established here. OverrideCheckResult enum is context, not proof it is the active selector.',
        'RequiemRegistries registers mob_items through external BlabberDynamicMetaregistry.registerSynced. CODEC/NETWORK_CODEC bodies present, but no concrete mob_items rule JSON, Mixin registration, or Blabber synchronization sender/receiver read. Plugin action-type registration does not substitute for those actual data entries.'
    ],
    'native_gaps':['Concrete enabled rule JSON targeting actual item/mob and its priority.', 'Mixin configuration and actual loading context.', 'External Blabber registry synchronization delivery and client reload.', 'Native ItemStack invocation/runtime result handling and component attachment.'],
    'counting':'0 held. No helper/enum/action/priority/timing variants counted. Continue only if missing fixed-local evidence becomes available; do not download or manufacture data.'}
save('immune-reference-batch-033.json',doc33)

ec,ecp=pinned(2,'CyclopsMC/EvilCraft'); core,cp=pinned(2,'CyclopsMC/CyclopsCore')
ecfiles=[('entity/monster/EntityVengeanceSpirit.java',None),('entity/effect/EntityAntiVengeanceBeam.java',None),
 ('item/ItemVengeanceFocus.java',None),('entity/monster/EntityVengeanceSpiritSyncedData.java',None),
 ('entity/monster/EntityVengeanceSpiritData.java',None),('item/ItemAbstractFocus.java',None),
 ('item/ItemVengeanceFocusConfig.java',None),('entity/effect/EntityAntiVengeanceBeamConfig.java',None),
 ('entity/monster/EntityVengeanceSpiritConfig.java',None),('client/render/entity/RenderVengeanceSpirit.java',None),
 ('core/monster/EntityNoMob.java',None),('EvilCraft.java',[[95,428]]),
 ('RegistryEntries.java',[[155,164],[365,392]])]
corefiles=[('helper/WorldHelpers.java',[[1,50]]),('helper/MinecraftHelpers.java',[[105,151]]),
 ('config/extendedconfig/EntityConfig.java',None),('config/extendedconfig/ItemConfig.java',None),
 ('init/ModBase.java',[[60,150],[222,295]]),('config/ConfigHandler.java',None),
 ('config/configurabletypeaction/ConfigurableTypeActionForge.java',None),
 ('config/extendedconfig/ExtendedConfigForge.java',None),('config/configurabletypeaction/EntityAction.java',None),
 ('init/ModBaseVersionable.java',None),('config/configurabletypeaction/ConfigurableTypeAction.java',None),
 ('config/extendedconfig/ExtendedConfig.java',None),('config/ConfigurableType.java',None),
 ('config/configurabletypeaction/ItemAction.java',None)]
allrefs=refs(ec,'src/main/java/org/cyclops/evilcraft/',ecfiles,'Actual focus producer, beam admission/hit, native spirit counters/motion, synced-data consumer and registered renderer. Other class content context0.')
allrefs+=refs(core,'src/main/java/org/cyclops/cyclopscore/',corefiles,'Separately pinned support0: actual registration callbacks/factories, success result and random efficientTick. Binary build750 correspondence not independently proven.')
mlp=A/'legacy-migration-acceptance/reviewed.jsonl'; mlraw=mlp.read_bytes()
ml=[json.loads(x) for x in mlraw.decode().splitlines() if x.strip()]
old=next(x for x in ml if x['candidate_id']=='155dd2bfebd2e1979e1b')
oldkeys=['candidate_id','status','family','trigger','input','output','preservation','application_limit','credit']
doc34={'schema_version':1,'owner':'program-feedback-review-034','repo':ec['repo'],'commit':ec['commit'],
 'provenances':[ecp,cp],'status':'PENDING_INDEPENDENT_REVIEW_MAXIMUM_ONE_WHOLE_NATIVE_CONTROL_AND_FINITE_LIFETIME_POLICY',
 'research_credit':0,'maximum_proposed_credit':1,'production_changes':False,'runtime_executed':False,
 'semantic_family':'evilcraft-native-beam-additive-freeze-preserves-spirit-finite-lifespan-with-synced-control-state-and-visibility-gated-renderer',
 'source_refs':allrefs,'baseline':baseline,
 'dedup_snapshot':comparisons({
  'alexscaves-native-orbiting-spirit-consumption-refusal-and-fading-exclusion':'Prior damage-refusal charge consumption/fading availability differs from a projectile-fed immobilization stock that delays finite lifespan. Spirit naming and isInvulnerableTo allowlist here are context0.',
  'draconic-native-crystal-refusal-recharge-cue-and-destabilization-window':'Prior refusal/recharge/activation cue policy, not native additive freeze stock preserving remaining entity life. Do not count another damage source whitelist.',
  'vampirism-dracula-native-burst-triggered-mist-refusal':'Prior damage accumulation-triggered mist refusal. This flow has no hurt-success threshold or damage-triggered transition; actual beam onHit directly adds frozen time.',
  'tf-snowqueen-multipart-shield-native-refusal-sound':'Multipart defense cue is unrelated to continuous focus admission and native finite-life suspension. Beam base sound is not a success/refusal receipt.',
  'mowzie-freeze-native-release-and-restoration-lifecycle':'Prior controller dismount/restored AI/pose cleanup differs from isImmobile/zero-motion and exchanging frozen ticks for delayed remainingLife decrements. No controller or stored motion restoration claimed.',
  'icefire-native-frozen-admission-and-server-fire-death-expiry-release-versus-shell':'Prior overwrite effect clock and fire/death expiry with shell differs from per-hit addition and mutually exclusive life/freeze countdown. Do not count generic freeze timer or renderer alone.',
  'playerrevive-native-helper-membership-pauses-terminal-bleed-clock-and-integrates-authoritative-release-with-asymmetric-helper-feedback-exit':'Closest life-clock pause comparator: membership-owned helper set with revive progress/cancel/death differs from projectile-added finite immobilization stock consumed one per aiStep, zeroing velocity and automatically resuming entity life when stock empty. Preserved-lifetime principle alone is not credit; coordinator may merge if whole policy not distinct.',
  'mowzie-freeze-native-eligibility-to-bound-control-receipt':'Prior hurt-success accumulation→threshold effect→tracked S2C receipt→controller/AI pose binding. Here spirit is nonpickable, custom server search assigns candidate, server-player-owned hit directly adds3..6, watched counters consumed by native motion/life and renderer, no bespoke client hit receipt. Nearest admission decision additionally read after complete source before proposal.'},
  'First four full semantic decisions before source; freeze/lifespan discovery followed by complete Mowzie release, IceFire and PlayerRevive decisions before remaining producer/readers. Mowzie admission additionally read before proposal. No old source re-audit.'),
 'migration_overlap_screen':{'path':str(mlp.relative_to(R)),'sha256':sha(mlraw),'rows':len(ml),
  'comparisons':[{'accepted_id':old['candidate_id'],'complete_semantic_decision_read':{k:old[k] for k in oldkeys},
   'distinction':'Whole prior spirit box capture/selective serialization/release owner retains all NBT and box semantics. Current proposal solely actual focus→beam→native freeze/life clock→current renderer; same frozen/lifetime fields and support helpers are not extra migration credit. No reread/recount of its47 accepted source contexts.'}]},
 'full_chain':[
  {'stage':'actual registration','observation':'EvilCraft @Mod constructor extends ModBaseVersionable→ModBase; base constructs ConfigHandler, subscribes mod events, calls virtual onConfigsRegister. EvilCraft actually adds focus, spirit and anti-beam configs. ConfigurableType ITEM/ENTITY route registration callbacks to queued registerToRegistry; RegisterEvent calls registry.register(name, config.getInstance()), lazily invoking actual supplied constructors. Common setup loadSetup calls onRegistered; EntityConfig calls EntityRenderers.register using actual overridden getRender. Native Forge event delivery/ObjectHolder injection not executed or independently source-expanded; registry anti-beam field generic type is EntityAttackVengeanceBeam despite anti-beam builder class, so no compiled type validation claimed.'},
  {'stage':'concrete item use and server spawn','observation':'ItemAbstractFocus.use rejects if max(0,getTicksUsingItem()-getUseItemRemainingTicks())>0, otherwise startUsingItem and explicit SUCCESS helper. This odd formula is preserved without interpreting native elapsed-use semantics. onUseTick computes MAX_INT-remaining, after6 invokes efficientTick(level,3,entityId), which actually compares random.nextInt(3) against abs(id)%3, not fixed modulo game-time cadence. When selected, actual ItemVengeanceFocus creates EntityAntiVengeanceBeam on either side but only server shoots/adds entity. Spawn return ignored; no item debit, energy cost or guaranteed projectile creation receipt.'},
  {'stage':'admission and authoritative hit','observation':'Generic beam ray filters spectator/alive/pickable/not owner; spirit isPickable=false. Separate server scan of moved/inflated beam box considers spirits, calls ProjectileUtil inside each candidate inflated box with unrestricted predicate and uses returned distance to select candidate entity1. Returned hit entity need not equal candidate in this code. If chosen, replaces generic result. Native helper intersection/occlusion/order not proven. onHit applies effect only server-side ENTITY hit with ServerPlayer owner; non-spirit/other-owner hit applies no freeze, and beam is discarded regardless. applyHitEffect calls actual spirit.onHit and adds owner to entanglingPlayers. No damage result gate or refusal message.'},
  {'stage':'additive control stock and lifespan suspension','observation':'Spirit.onHit adds random3..6 to frozenDuration. Data.addFrozenDuration uses get+amount without clamp; isFrozen is >0. Spirit isImmobile returns frozen OR buildup>0. aiStep invokes superclass first, then decrements positive buildup, then frozen branch sets delta movement0 and decrements freeze; only else decrements remainingLife and removes KILLED at<=0. Therefore a positive stock freezes post-super motion and suspends finite-life consumption, including last1→0 tick. Repeated hit extends stock rather than overwrite. When empty, freeze-based immobile gate ends and next aiStep spends life; no old velocity/AI restoration transaction. Buildup alone can still block mobility but does not pause life. Counters tick on both sides with no side guard in this method.'},
  {'stage':'state carrier and actual render consumer','observation':'Entity defines SynchedEntityData accessors and constructs EntityVengeanceSpiritSyncedData; its getters/setters for frozenDuration and remainingLife read/write the same watched data. @Delegate exposes these to spirit; base addFrozen/isFrozen dispatch through overridden accessors. Renderer reads spirit.isFrozen on current client entity, and for visible, non-swarm, non-null inner entity substitutes energySwirl buffer UV using (tickCount+partial)*.01 when frozen,1 otherwise. This is source-level watched-state producer/consumer, not independently verified native packet serialization/delivery. Visibility gated by vengeance/creative option/spectral glasses; no universal feedback guarantee.'},
  {'stage':'feedback and expiry boundaries','observation':'Actual beam path invokes spirit.onHit only server-side, so its client-only showBurstParticles branch is not triggered by this hit route. Synced-data update alone does not call onHit. Beam client tick particles/base sound happen without hit success. Spirit removal emits smoke/sound only client and visible, and does not distinguish all removal reasons as actual death. At freeze zero rendering uses unfrozen UV but entity can remain immobile due to buildup. Native tracking removal and superclass post-remove tick behavior not inspected. Entangling player set is appended on hits and has no local expiry clear in spirit; it is box/advancement context0, not a guaranteed control-session cleanup.'}
 ],
 'critical_boundaries':[
  'At most1 whole mod-owned projectile-fed immobilization plus finite-life preservation policy pending scope/semantic review. All class/helper/sound/timer/allowlist variants0.',
  'No generic effect-immunity repair, cancellation of hurt, boss exemption, server fee or refund derived from beam/frozen names.',
  'isImmobile override and post-super zero velocity are actual writes, not a proof of every native movement/collision outcome.',
  'Actual efficientTick uses randomness. No deterministic three-tick cadence or wall-clock latency claim.',
  'Negative/corrupt/int-overflow freeze values are not clamped; positive-only branch can be bypassed. Conditional raw arithmetic observation, no exploit reproduced.',
  'World spawn return, target filtering native semantics, packet delivery and client/server timing remain unverified. No game, Java, build, rendering, sound or live-network execution.'
 ],
 'native_gaps':[
  {'missing':'Pinned Core tag binary correspondence to EvilCraft declared build750.', 'impact':'Core is separately fixed source support only; not proof the exact deployed binary executes these helper/registry methods.'},
  {'missing':'Same-version native SynchedEntityData tracker sender/packet receiver and Forge event/ObjectHolder implementation.', 'impact':'Document actual mod-owned watched field writers/readers and registration requests; do not claim delivered packet or compiled/runtime wiring acceptance.'},
  {'missing':'Native ProjectileUtil, ThrowableProjectile.tick and LivingEntity movement/aiStep caller.', 'impact':'No guaranteed nearest target, occlusion handling, displacement, no double processing or packet timing. Custom scan conditional behavior preserved.'},
  {'missing':'A client delivery for spirit.onHit burst on actual anti-beam path.', 'impact':'No per-hit burst receipt proven. Existing ongoing renderer reads state only.'}
 ],
 'static_examples_not_executed_tests':[
  {'case':'last frozen tick','assumptions':'Before aiStep own branch: frozen1, remainingLife1, no new hits.', 'derivation':'Frozen branch writes motion0 and freeze0, keeps life1. Next own branch takes else, life0 and removal. Superclass effects/actual timing not simulated.'},
  {'case':'repeat hit','assumptions':'Frozen2 and an accepted server hit adds selected random4 before own branch.', 'derivation':'Stock becomes6 then next own branch5 with unchanged life. No overwrite or max-duration cap.'},
  {'case':'buildup without freeze','assumptions':'Freeze0, buildup10 and life2.', 'derivation':'isImmobile true; own aiStep reduces buildup9 and life1. Immobilization alone is not lifespan pause; positive freeze stock is exact gate.'},
  {'case':'no client impact burst','assumptions':'Actual beam onHit executes normally on server; later watched data is received by client.', 'derivation':'Server calls spirit.onHit with client conditionfalse; data setter path does not invoke that method, so this route proves no client burst. Renderer may see frozen state if visible.'}
 ],
 'application':'Keep authoritative control stock, finite lifetime and display state distinct. Spell out whether control consumes or suspends terminal timers; expose actual state to feedback and do not treat ambient projectile effects as success receipts.',
 'counting':{'formal_baseline_observed':len(rows),'credit':0,'maximum_pending_whole_policy':1,'shared_NBT_helpers_variants_credit':0},
 'next_work':'Coordinator independently decide full native-control policy scope/novelty against PlayerRevive and freeze families. May merge0. Do not self-add or start production before required evidence gate.'}
save('immune-reference-batch-034.json',doc34)
print(json.dumps({'033_ranges':len(rqrefs),'034_ranges':len(allrefs),'034_unique_files':len({x['path'] for x in allrefs}),
 '033_credit':0,'034_credit':0,'034_maximum_pending':1,'formal_baseline':len(rows)}))
