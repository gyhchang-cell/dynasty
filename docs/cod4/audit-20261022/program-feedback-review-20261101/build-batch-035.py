#!/usr/bin/env python3
"""Record one bounded local projectile/observer/child-lifetime proposal; no master edits."""
import hashlib
import json
from pathlib import Path

R=Path('/Users/a15356015027/Desktop/dynasty'); H=Path(__file__).resolve().parent; A=H.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
priorp=H/'immune-reference-batch-034.json'; prior=json.loads(priorp.read_text())
assert sha(priorp.read_bytes())=='294cbff57eae34cdcb7314542f1f0c1e50305aa6b72263acaba6b01df3c7bf24'
receipt=A/'immune-feedback-research/coordinator-evilcraft-freeze-lifespan-acceptance-20261103.json'
assert sha(receipt.read_bytes())=='4f11f6fb5772b81af1f54c1e8ddde963e5b23091d0c752c169fce735e76a77b7'
mp=R/prior['provenances'][0]['manifest_path']; manifests={m['repo']:m for m in json.loads(mp.read_text())}
refs=[]
def add(repo, prefix, specs):
    m=manifests[repo]; entries={e['path']:e for e in m['files']}
    for f,bounds in specs:
        e=entries[prefix+f]; b=(R/e['source']).read_bytes(); n=len(b.decode().splitlines())
        for limits in bounds or [[1,n]]:
            refs.append({'repo':repo,'commit':m['commit'],'path':e['source'],'upstream_path':e['path'],
                'file_sha256':sha(b),'git_blob_sha1':e['source_blob'],'lines':limits,
                'reading_context':'new_actual_bounded_source_read035',
                'purpose':'Actual staff/head/observer/child/feedback path or explicit0 admission/resource/registry support. No credit by file or parameter.'})
add('CyclopsMC/EvilCraft','src/main/java/org/cyclops/evilcraft/',[
 ('entity/monster/EntityControlledZombie.java',None),('item/ItemNecromancerStaff.java',None),
 ('entity/effect/EntityNecromancersHead.java',None),('item/ItemNecromancerStaffConfig.java',None),
 ('entity/monster/EntityControlledZombieConfig.java',None),('entity/effect/EntityNecromancersHeadConfig.java',None),
 ('client/render/entity/RenderControlledZombie.java',None),('core/item/ItemBloodContainer.java',None),
 ('advancement/criterion/NecromanceTrigger.java',None),('Advancements.java',None),
 ('RegistryEntries.java',[[363,364],[393,394]])])
add('CyclopsMC/CyclopsCore','src/main/java/org/cyclops/cyclopscore/',[
 ('helper/EntityHelpers.java',[[82,97]]),('item/DamageIndicatedItemFluidContainer.java',None),
 ('inventory/PlayerExtendedInventoryIterator.java',None),('inventory/InventoryIterator.java',None),
 ('inventory/InventoryLocations.java',None),('capability/fluid/FluidHandlerItemCapacity.java',None),
 ('helper/FluidHelpers.java',[[1,100]]),('helper/AdvancementHelpers.java',[[49,61]])])
# Reuse only actually needed complete034 registration/helper ranges with exact hashes.
reuse=[x for x in prior['source_refs'] if x['repo']=='CyclopsMC/CyclopsCore' or x['upstream_path'].endswith('/EvilCraft.java')]
for old in reuse:
    assert sha((R/old['path']).read_bytes())==old['file_sha256']
    new=dict(old);new['reading_context']='unchanged034_range_reused_not_reread_or_recredited'
    new['purpose']='Previously fully read registration factory/event/helper support0; separate Core build750 binary limit unchanged.'
    refs.append(new)
lp=A/'immune-feedback-research/reviewed.json';lr=lp.read_bytes();ledger=json.loads(lr);by={x['id']:x for x in ledger}
comparisons={
 'aoa-native-summoned-minion-player-owner-damage-admission-and-owner-bound-lifetime':'Closest summon-lifetime policy binds child directly to boss alive state and age, disallows save, admits spawn only on native add true before costs/FX. Here a paid projectile becomes an observing removal-veto actor; helper-qualified reference list and original target alive govern group cleanup, while children independently persist raw TTL. No owner-life binding, no player-only incoming damage gate, no native spawn acknowledgement.',
 'pnc-native-owner-identity-qualified-permanent-retame-control':'Permanent owner replacement differs from creating new Monster children with one initial target assignment and a transient observer; no ownerUUID written on children. Controlled name is not an actual owner control policy.',
 'goety-native-lethal-capture-owner-transfer-instead-of-death-and-unshackle-release':'No lethal event cancellation or existing victim conversion here. Initial zero-hurt result ignored then new children/observer transition; no captured actor restoration or unshackle path.',
 'betweenlands-native-owned-puppet-health-delta-qualified-consumable-player-defense-and-ring-invalidation':'Existing owned puppet payment/capability and shield invalidation retains all that policy. New chain has no puppet HP-paid grant or active ring; blood use is only input context0, not proposed separate payment-credit instance. Cleanup uses observer-local references and independent childTTL.',
 'wizardry-native-separate-collision-shield-refusal-and-weak-owner-lifetime':'Existing weak-owner collision proxy refuses damage and removes on casting end. This projectile instead vetoes remove while observing its summoned children and original target, then explicitly opens removal when list empty. No weak-ref loss, player shield, reflection or hit sound receipt.',
 'evilcraft-native-beam-additive-freeze-preserves-spirit-finite-lifespan-with-synced-control-state-and-visibility-gated-renderer':'Newly accepted034 retained whole. No swapping freeze stock for life here: head removal is state-vetoed; server randomly polls child-list/target life, while each child always pre-decrements saved TTL and discards only at exactzero. Same Core helpers/registration remain0; timing constants/fields not independent credit.'}
mlp=A/'legacy-migration-acceptance/reviewed.jsonl';mlraw=mlp.read_bytes()
ml=[json.loads(l) for l in mlraw.decode().splitlines() if l.strip()]
family_screen=[{'id':x['candidate_id'],'family':x['family']} for x in ml if 'evilcraft' in x.get('family','')]
newrefs=[x for x in refs if x['reading_context']=='new_actual_bounded_source_read035']
doc={
 'schema_version':1,'owner':'program-feedback-review-035','repo':'CyclopsMC/EvilCraft','commit':manifests['CyclopsMC/EvilCraft']['commit'],
 'provenances':prior['provenances'],'status':'PENDING_INDEPENDENT_REVIEW_MAXIMUM_ONE_PROJECTILE_OBSERVER_REMOVAL_VETO_AND_CHILD_LIFETIME_POLICY',
 'research_credit':0,'maximum_proposed_credit':1,'production_changes':False,'runtime_executed':False,
 'semantic_family':'evilcraft-native-necromancer-projectile-observer-removal-veto-with-target-bound-group-cleanup-and-independent-child-ttl',
 'source_refs':refs,
 'prior_read_reuse':{'path':str(priorp.relative_to(R)),'sha256':sha(priorp.read_bytes()),'new_ranges':len(newrefs),
  'new_cited_lines':sum(x['lines'][1]-x['lines'][0]+1 for x in newrefs),'reused_ranges':len(reuse),
  'limits':'Only exact same file hash/range reused.034 already accepted; no source rerun or acceptance re-audit. Register callbacks and random efficientTick support0, no binary750 claim.'},
 'baseline':{'formal_count_observed':len(ledger),'gap_to1000':1000-len(ledger),'ledger_sha256':sha(lr),
  'accepted034_receipt_path':str(receipt.relative_to(R)),'accepted034_receipt_sha256':sha(receipt.read_bytes()),
  'limits':'Coordinator470 acceptance observed only.033 remains0; no self-merge or master edits.'},
 'dedup_snapshot':{'path':str(lp.relative_to(R)),'sha256':sha(lr),'rows':len(ledger),
  'comparisons':[{'accepted_id':k,'full_semantic_decision_read':{a:b for a,b in by[k].items() if a not in ['source_refs','auxiliary_refs']},'distinction':v} for k,v in comparisons.items()],
  'reading_order':'First5 full substantive accepted decisions read before new source.034 newly accepted full decision read before proposal as latest comparator, without rereading its29 source ranges.'},
 'migration_screen':{'path':str(mlp.relative_to(R)),'sha256':sha(mlraw),'rows':len(ml),'evilcraft_family_index':family_screen,
  'limits':'Index-only scope screen, not full migration-decision reading or semantic credit. No candidate for NBT schema/storage/Clone; all persistence here supports lifetime limits0. No assertion exhaustive unrelated-name dedup.'},
 'full_chain':[
  {'stage':'concrete registered producer','observation':'Reused actual EvilCraft.onConfigsRegister adds ItemNecromancerStaffConfig, EntityControlledZombieConfig, EntityNecromancersHeadConfig. Previously read base callbacks create/register concrete factories; entity configs select controlled renderer and native ThrownItemRenderer. New ObjectHolder declarations bind controlled_zombie and necromancers_head. Staff.use gets current hand stack, canConsume usage then calls consume ignoring returned amount, constructs/throws head, returns SUCCESS. Without canConsume, actual ItemBloodContainer.use fallback also returns SUCCESS, even no fluid change. No typed refused-summon message.'},
  {'stage':'input resource boundary, no separate credit','observation':'Own-item canDrain compares exact simulated amount. Otherwise canConsume checks only nonempty simulated drainFromOthers, not requested total. drainFromOthers cumulatively adds drained, but subtracts cumulative amount from remaining on each iteration, and its final nonempty&&empty condition is impossible. consume EXECUTE only for null player or noncreative server player; creative/client SIMULATE. Parent capability writes Fluid NBT; native Forge drain internals not read. Staff does not verify consume result, does not refund on head/child spawn failure; no full payment claim. Extended inventory iterator reads registered locations, not proof every external inventory provider semantics.'},
  {'stage':'projectile hit admission','observation':'throwNecromancersHead constructs on either side, sets mobType and shoots/adds only server; addFreshEntity return ignored. mobType field/setter unused by spawnSwarm, which always constructs ControlledZombie. Head.onHit acts only ENTITY, not observing, server. Calls target.hurt(thrown(owner),0) before qualifications and ignores result. Then requires ServerPlayer owner, hit not owner, hit LivingEntity to spawnSwarm; otherwise discard. No alive gate, source immunity result gate or final rejection receipt. Block/client/already-observing hits have no local action in override; no inherited impact behavior claimed.'},
  {'stage':'child list and target state','observation':'spawnSwarm loops random3..4, constructs each child; canAttackType override true. Copies necromancer position, moves randomXZ, calls Core EntityHelpers.spawnEntity. Helper calls Forge onFinalizeSpawn; non-null SpawnGroupData triggers world.addFreshEntity but ignores its boolean and returns true. Thus observables list means helper-qualified, not proved added entity. Regardless helper result, qualifying child then receives setTarget(original hit entity) and TTL200. After loop head stores target and enters observer mode even if list empty. No child owner UUID/reference set; target may later change via native goals. No guarantee actual mob melee since native goals/caller not expanded and MeleeAttackGoal was put in targetSelector.'},
  {'stage':'observer removal veto and cleanup','observation':'setObserverMode sets observing=true, motion0, invisible=true. Head.remove delegates to super only when !observing, vetoing any reason while flagtrue. Actual tick first super.tick then, only observing and server and efficientTick(level,10), scans list. Shared helper uses random.nextInt(10)==0 (no parameters), not every10th tick. Dead child removed from list; if original target not alive, each living child discarded and removed. When list empty, clears observing then calls remove(DISCARDED), now permitted. Target death cleanup is sampled, not instant. No explicit owner-alive, distance, dimension or owner-held-item gate. Motion set once, no noGravity flag or pre-super stop, so not guaranteed stationary observer.'},
  {'stage':'independent child lifetime and reload boundary','observation':'Child defineSynchedData TTL0; staff sets200. Child aiStep super first then server getsTTL, predecrements/stores, and discards only if result==0. Normal positive TTL reaches0; initial/missing-key0 becomes-1 and does not expire on that step, no <=0 or clamp. NBT saves/reads rawttl alongside superclass, so remaining child life survives own data roundtrip; target/owner is not custom saved here. Head observing/target/observables are plain fields with no custom NBT read/write or synced-data definition, no load reconstruction. No persistent observer-child identity/UUID linkage or restart repair demonstrated. Parent native serialization/unload semantics not expanded; veto of remove does not prove process/world unload persistence.'},
  {'stage':'actual feedback consumer and its limits','observation':'Head ItemSupplier returns skeleton skull; registered native ThrownItemRenderer receives it. Observer invokes native invisible flag but local observing/list/target have no custom network fields. Controlled renderer selects texture and delegates model aggression to entity.isAggressive; does not read TTL or emit expiration/refusal cue. Actual Advancements.NECROMANCE is registered via helper to CriteriaTriggers and test(player,target) is called after observer transition regardless empty list or world-add result; instance checks only target EntityPredicate, not number spawned/payment. Advancement UI delivery/data not inspected. No dedicated success or rejection sound/message in this chain; visual/native tracking not runtime-verified.'}
 ],
 'critical_boundaries':[
  'At most1 for the complete projectile→observer removal-veto→sampled target-bound group cleanup plus independent childTTL policy. No helper/class/parameter/child variant/persistence credit.',
  'Do not repeat staff comment claims: target death cleanup is sampled, and no-drop/low-HP claims are not established by these classes/loot sources.',
  'observables membership is not actual spawn acknowledgement. An unadded but alive constructed child could remain in list; native world-add/tick behavior not asserted or leak reproduced.',
  'remove veto covers every RemovalReason in override, but no claim it safely prevents native chunk unload/server shutdown or that it is damage immunity.',
  'TTL0 does not remove after predecrement; raw int arithmetic includes eventual wraparound, so do not claim mathematical immortality. Spawn egg config exists without custom positiveTTL initialization; native egg spawn path not expanded.',
  'No source payment proof, source damage-result proof, owner identity binding on children, guaranteed AI attack, packet ack or group cleanup atomicity.',
  'Same Core tag support boundary as034: binary build750 correspondence not independently proved. No native or upstream code executed.'
 ],
 'native_gaps':[
  {'missing':'Minecraft/Forge same-version projectile collision, AI tick/target goals, removal/unload and addFreshEntity handling.', 'impact':'Source-owned override/state branches only; no actual collision, attacks, disappearance, immortal leak or shutdown claim.'},
  {'missing':'Native tracked-data/invisibility and ThrownItemRenderer/Monster consumers.', 'impact':'Actual mod getters/setters/renderer registration present; native client delivery/pixels and TTL visibility not proved.'},
  {'missing':'Forge fluid drain and arbitrary attached inventory providers; advancement JSON and UI receipt.', 'impact':'No verified total debit, refund, exact registration runtime or visible summon-success receipt.'},
  {'missing':'Persisted head observer fields or actual reload reconstruction in fixed head source.', 'impact':'No cross-restart target/child cleanup guarantee. ChildTTL only is explicit saved policy.'}
 ],
 'static_examples_not_executed_tests':[
  {'case':'all finalize results null','assumptions':'Each Core finalize call returnsnull; no other exception.', 'derivation':'No child added to observables; target and observer flag still set, criterion tested. First later sampled observer tick clears flag/discards head. Not a child-spawn success receipt.'},
  {'case':'native add false after finalize nonnull','assumptions':'Core finalize returnsnon-null, native add returnsfalse.', 'derivation':'Helper stilltrue, so object enters observables and receives target/TTL. Whether an unadded object receives aiStep is outside source proof; membership cannot certify a live spawned child.'},
  {'case':'target dies before childTTL','assumptions':'Observer runs, list contains live child, original target is notalive.', 'derivation':'Until random poll passes no local target cleanup. Passing poll discards each live child, removes references, clears observing and permits head removal.'},
  {'case':'childTTL starts1 versus0','assumptions':'Server own aiStep TTL write executes.', 'derivation':'1 predecrements0 anddiscards;0 predecrements-1 anddoesnot discard. Exactzero condition, no <=0 fallback.'},
  {'case':'observer reload','assumptions':'A new head instance restores only native superclass data; no external custom hook.', 'derivation':'Own observing=false, targetnull, emptylist remain constructor defaults; old children have only their own savedTTL in shown code. No restoration of group observer refs established.'}
 ],
 'application':'Separate observer lifetime from child lifetime, use actual world-add acknowledgement for membership, and make cleanup state recoverable or explicitly transient. A target assignment or visual/advancement attempt does not prove control or successful creation.',
 'counting':{'formal_baseline_observed':len(ledger),'credit':0,'whole_policy_maximum_pending':1,'helpers_variants_storage_credit':0},
 'next_work':'Coordinator independently decide whole-policy scope/novelty against AoA/Wizardry/latest034; may merge0. No self-count or production before1000.'}
with (H/'immune-reference-batch-035.json').open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'ranges':len(refs),'new_ranges':len(newrefs),'new_lines':doc['prior_read_reuse']['new_cited_lines'],
    'reused_ranges':len(reuse),'formal_baseline':len(ledger),'maximum_pending':1,'credit':0}))
