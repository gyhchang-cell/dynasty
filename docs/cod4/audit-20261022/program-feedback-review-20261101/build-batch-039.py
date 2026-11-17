#!/usr/bin/env python3
"""Record actual fixed-local-source reading. Writes specialist evidence only."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

R = Path('/Users/a15356015027/Desktop/dynasty')
H = Path(__file__).resolve().parent
A = H.parent
sha = lambda b: hashlib.sha256(b).hexdigest()
rel = lambda p: str(p.relative_to(R))
def receipt(p):
    return {'path': rel(p), 'sha256': sha(p.read_bytes())}

mp = R/'tools/cod4/legacy-migration-acceptance/helpers/halley-migration/batch-005/source-manifest.json'
m = next(x for x in json.loads(mp.read_text()) if x['repo'] == 'TheIllusiveC4/Champions')
pb = mp.parent/'provenance/TheIllusiveC4__Champions'
prov = dict(repo=m['repo'], commit=m['commit'], branch=m['branch'], tag=m.get('tag'),
    manifest_path=rel(mp), manifest_sha256=sha(mp.read_bytes()),
    commit_metadata_path=rel(pb/'commit.json'), tree_metadata_path=rel(pb/'tree.json'),
    git_tree=m['git_tree'], acquisition='Existing fixed local cache only; no network or upstream execution.')
files = {x['path']: x for x in m['files']}
prefix = 'src/main/java/top/theillusivec4/champions/'
specs = {
    'common/affix/ShieldingAffix.java': 'Whole random-toggle state producer, incoming attack refusal, sound submission, sync reader/writer and client particle consumer.',
    'common/affix/core/BasicAffix.java': 'Whole tracking-entity sync sender, identifier and registration helpers; targeting methods are context only0.',
    'common/affix/core/AffixData.java': 'Whole side-specific data access and fresh BooleanData serialization; IntegerData support0.',
    'common/network/SPacketSyncAffixData.java': 'Whole actual packet codec and queued client lookup/application; no retry queue or lifecycle identity.',
    'common/network/SPacketSyncChampion.java': 'Whole tracking snapshot codec/application; carries affix IDs but no per-affix mode.',
    'common/network/NetworkHandler.java': 'Actual registration for both packet types.',
    'common/ChampionEventsHandler.java': 'Whole registered server/client update and attack consumer; other event methods read as context0.',
    'Champions.java': 'Whole mod constructor and setup registration; config/plugin/egg/command portions context0.',
    'common/capability/ChampionCapability.java': 'Whole side-specific owner/data maps and capability factory; disk guard belongs to existing migration owner0.',
    'common/affix/core/AffixManager.java': 'Actual ShieldingAffix registration and complete optional selection settings; other affix names0.',
    'common/capability/CapabilityEventHandler.java': 'Whole capability attachment, spawn, conversion and StartTracking producer; conversion persistence owner0.',
    'api/IAffix.java': 'Default empty initial/spawn methods: no hidden inherited shielding-mode initialization or initial sync here.',
    'api/impl/ChampionsApiImpl.java': 'Actual affix registry insertion and ID/category lookup.',
    'common/util/ChampionBuilder.java': 'Whole native spawn/preset selection, installed-affix list and initial callback; rank plugins not expanded.',
    'common/util/ChampionHelper.java': 'Whole actual LivingEntity+Enemy qualification and spawn potential checks; external stage gate unexpanded.'
}
refs = []
for name, purpose in specs.items():
    e = files[prefix+name]; raw = (R/e['source']).read_bytes(); lines = raw.decode().splitlines()
    refs.append(dict(repo=m['repo'], commit=m['commit'], path=e['source'], upstream_path=e['path'],
        lines=[1, len(lines)], file_sha256=sha(raw), git_blob_sha1=e['source_blob'],
        range_text_sha256=sha('\n'.join(lines).encode()), purpose=purpose,
        reading_context='Actual full-file reading in039 before interruption retained; no source reread credited on resume.'))

lp = A/'immune-feedback-research/reviewed.json'
lr = lp.read_bytes(); rows = json.loads(lr); by = {x['id']: x for x in rows}
distinctions = {
 'malum-native-aegis-incoming-denial-transformed-capacity-and-postattack-window': 'Prior consumes charge on each qualifying incoming attack. Here a tick-sampled boolean holds through any number of attacks and changes only on later successful random toggle; no hit resource, health threshold or postattack timer.',
 'undergarden-native-first-positive-hit-refusal-with-los-and-idle-qualified-rearm': 'Prior first positive hit consumes hidden state and rearm needs cooldown/navigation/LOS. Here hits neither consume nor rearm the shield, no amount>0 check, no navigation/LOS condition; a continuing random process toggles both directions.',
 'dungeonsmobs-native-shared-shield-overflow-tick-cascade-versus-regeneration': 'Prior shared HP debt cascades through shield inventory and timed regeneration. Here no shield count/damage debt; attack size and number do not alter toggled state.',
 'bumblezone-native-aggregate-health-versus-elapsed-time-shield-admission-and-current-state-layer': 'Prior cross-target health progress maps to a deterministic arena schedule and synced entity shield. Here an individual actor tick samples RNG to invert a retained affix boolean; duration has no deterministic deadline, and initial affix-name snapshot omits the mode.',
 'enigmatic-native-cube-underlimit-random-cancel-retaliation-not-success-gated': 'Prior rolls on each incoming qualifying hit with damage threshold/retaliation. Here RNG runs in server update independently of attacks, retaining correlated acceptance across all hits until another successful inversion; no reflection or debuff.',
 'occultism-native-mummy-random-damage-cancellation-assignment-and-conditional-criterion': 'Prior directly assigns cancellation from each damage roll and can assign false. Shielding instead returns false while retained mode true, and caller only sets cancellation true; false-mode cannot uncancel previous target-affix veto. No per-hit chance or criterion.',
 'botania-gaia-trueplayer-authority-and-phase-timer': 'Prior true-player admission plus deterministic dedicated invulnerability countdown and combat phase. Here no attacker identity condition, only exact OUT_OF_WORLD object exception and independently sampled mode; random failures preserve either state without finite expiry guarantee.',
 'cat-scripted-animation-phase-invulnerability-family': 'Prior authored animation states determine phase refusal. This candidate has no attack animation/phase transition driving shield; periodic stochastic inversion with state-only client packet versus separate per-attempt sound is the whole policy, not an animation ID variant.',
 'vampirism-dracula-invulnerability-hud-clock-and-transition': 'Prior HUD has wall-clock change/flash leases and initial snapshot state. Here client emits particles each update only from local received mode; no wall clock, transition animation, hit flash or initial mode snapshot. Feedback is not an additional credit.'
}
comparisons = [dict(accepted_id=k, full_semantic_decision_read={a:v for a,v in by[k].items() if a not in ['source_refs','auxiliary_refs']},
    distinction=v) for k,v in distinctions.items()]
mlp = A/'legacy-migration-acceptance/reviewed.jsonl'; mlraw = mlp.read_bytes()
mr = [json.loads(l) for l in mlraw.decode().splitlines() if l.strip()]
mk = ['candidate_id','status','family','trigger','input','output','preservation','application_limit','credit']
old = next(x for x in mr if x['candidate_id']=='28be6a664f825b0ccaa0')
accepted = A/'immune-feedback-research/coordinator-evilcraft-lightning-protection-acceptance-20261103.json'
ac = json.loads(accepted.read_text())
assert ac['decision']=='ACCEPTED_ONE_RESEARCH_REFERENCE_ONLY' and ac['after_count']==473

doc = {
 'schema_version':1, 'owner':'program-feedback-review-039', 'created_utc':datetime.now(timezone.utc).isoformat(),
 'repo':m['repo'], 'commit':m['commit'], 'provenances':[prov],
 'status':'PENDING_INDEPENDENT_REVIEW_MAXIMUM_ONE_RANDOM_TICK_LATCHED_SHIELD_ADMISSION_AND_PARTIAL_SNAPSHOT_FEEDBACK_POLICY',
 'research_credit':0, 'maximum_proposed_credit':1, 'production_changes':False, 'runtime_executed':False,
 'semantic_family':'champions-native-periodic-random-toggle-latches-attack-refusal-with-mode-change-only-tracking-sync-and-independent-per-hit-sound',
 'source_refs':refs, 'full_files_actually_read':len(refs), 'cited_lines':sum(x['lines'][1] for x in refs),
 'baseline':{'accepted037_receipt':receipt(accepted), 'formal_count_observed':len(rows), 'gap_to1000':1000-len(rows),
     'prior038':receipt(H/'immune-reference-batch-038-screen.json'), 'prior038_credit':0},
 'dedup_snapshot':{'path':rel(lp),'sha256':sha(lr),'rows':len(rows),'comparisons':comparisons,
     'scope':'473-row identifier/selected semantic metadata discovery, nine complete nearest decisions read. Not a claim of rereading all473 source chains. Three phase/HUD comparisons completed after resume; six other comparisons and source reading retained from pre-interruption039.'},
 'migration_overlap_screen':{'path':rel(mlp),'sha256':sha(mlraw),'rows':len(mr),'comparisons':[
     {'accepted_id':old['candidate_id'],'complete_semantic_decision_read':{k:old[k] for k in mk},
      'distinction':'Existing owner is affix rank/data persistence, conversion and Adaptable consecutive damage memory. Shielding runtime toggle/admission/tracking feedback was explicitly outside its all-affix claims. Existing hasUUID-vs-compound mismatch, conversion, NBT, generic data maps/packet/registry helpers earn0 here. The proposal must stand as one different live combat policy.'}]},
 'full_chain':[
  'Actual @Mod constructor registers common setup; setup calls ChampionCapability.register, NetworkHandler.register and AffixManager.register. Capability.register registers both native event handlers. AffixManager registers concrete ShieldingAffix into ChampionsApiImpl ID/category maps. Capability attach is limited to LivingEntity implementing Enemy.',
  'Actual server SpecialSpawn or JoinWorld with no rank calls ChampionBuilder.spawn. It respects existing ChampionData preset read or selects rank/affixes; createAffixes adds presets and filters random options by optional entity/affix settings, canApply and compatibility, then installs the list and calls initial callbacks. Shielding inherits empty initial/spawn defaults. Natural roll/config/plugin details are not claimed certified; the combat policy is conditional on the real installed shielding affix.',
  'ChampionEventsHandler.onLivingUpdate calls server affixes only when actor.tickCount%10==0. Shielding further requires tickCount%40==0 and actor RNG float<0.5; only then it reads side-specific BooleanData, inverts mode, saves it and sends its current tag to TRACKING_ENTITY. Failed samples leave either current mode unchanged. No hit, health, target, charge, cooldown reset or maximum-duration rule is involved.',
  'Server LivingAttackEvent asks every target affix onAttacked; Shielding returns true for the exact DamageSource.OUT_OF_WORLD object. Otherwise current saved mode true submits PLAYER_ATTACK_NODAMAGE at the target and returns false; caller setsCanceled(true). It does not consume state, roll RNG, reduce amount, require positive amount or check source owner. False-mode returns true but does not uncancel another affix. The foreach does not short-circuit after target veto; when complete and canceled, attacker-side onAttack callbacks are skipped.',
  'BasicAffix.sync emits SPacketSyncAffixData(entity integer ID, affix string ID, CompoundTag). Registered codec/handler enqueues client work, checks current world, resolves current entity by ID, valid champion capability and currently mapped affix ID, then calls concrete readSyncTag and saves to client data. The packet does not contain UUID/dimension/generation or retain/retry missed work. Actual transport scheduling/delivery and native entity lifetime are not executed.',
  'Actual StartTracking sends SPacketSyncChampion only: tier/default color/affix ID set, no mode. Its consumer sets client rank and affix list. No Shielding onSpawn/initial override sends a mode. Fresh client data therefore has no authoritative shielding value from this snapshot; only the subsequent mode-change packet supplies it in the shown chain. The registry/list packet and state packet are separate and can be absent at the consumer; no guarantee of initial state equivalence.',
  'Client LivingUpdateEvent calls every installed client affix each delivered update. Shielding emits one white ENTITY_EFFECT particle at randomized body position when local mode true. The rank showParticles condition is later and governs rank particles, not this affix particle. Particle existence is local state display, not a per-hit acknowledgment. Rejection sound is submitted before outer cancellation and on each qualified onAttacked invocation, with no local throttle or dedicated reason/text packet.',
  'A later successful server sample toggles true to false and synchronizes release; another success can reactivate. Failed samples can preserve either phase arbitrarily long; no fixed two-second shield duration or deterministic expiry follows from the 40-tick sampling condition. Entity removal ends this actor callbacks. Conversion installs affixes on a different capability and calls empty shield initial callback without copying the old private mode; disk compound/UUID guard is the already-owned migration limitation, not fresh credit or a tested reset guarantee.'
 ],
 'critical_boundaries':[
  'One stochastic stateful admission/feedback lifecycle at most1. Not one credit each for NBT, packet, source exception, particles, sound, registry, random parameter or side maps.',
  'Shielding is damage attack cancellation, not blanket movement/control/effect immunity. OUT_OF_WORLD identity bypass is local to this affix, not proof every other affix or native gate accepts.',
  'Conditional negative example: server mode already true and a fresh observer receives only the affix-name snapshot. The client has no true mode to display until an applicable later state packet. The next successful inversion is false, so receiving that packet can leave it visually off through the whole unseen true phase. No claim of guaranteed live reproduction or bounded wait.',
  'Client.setAffixes clears the visible list but not idToAffix/data. A previously mapped removed affix can still accept an ID packet and retain data; it is no longer ticked if absent from list. Integer entity ID alone does not authenticate the old actor lifetime. These are contextual limitations, not separate proposals.',
  'Affine data getter reflection can return null on construction error; callers lack null handling. Normal BooleanData missing mode uses native getBoolean behavior, whose implementation was not expanded in this batch.',
  'No shield initial-on state or startup sync inferred from registration; Shielding inherits empty callbacks. No active phase finite upper bound, hit-count limit, authoritative particle receipt or sound delivery guarantee.',
  'Cached branch1.18.x/commit source only. Forge event dispatch, native damage pipeline, tickCount lifecycle, CompoundTag internals, SimpleChannel scheduling and sound/particle transport not expanded. No claim of matching Dynasty1.20.1 API or runtime.',
  'Generic persistence mismatch and conversion remain migration owner28be6a; full helper files read for concrete chain context, not recounted. Other affix implementations, RankManager, EntityManager, GameStages/ScalingHealth and ChampionData deep paths are not certified by imports/calls.'
 ],
 'static_examples_not_executed_tests':[
  {'condition':'mode true; two non-OUT_OF_WORLD attacks between successful samples','expected_local_code':'Both callbacks submit no-damage sound and return false. Neither spends the mode. No per-hit independent RNG.'},
  {'condition':'qualifying sample RNG>=0.5','expected_local_code':'No mode write or packet. Existing vulnerability/protection remains; 40 ticks is a sampling interval, not guaranteed expiration.'},
  {'condition':'mode true; exact OUT_OF_WORLD source','expected_local_code':'Shielding returns true before sound. Caller can still be canceled by another target affix.'},
  {'condition':'mode true; successful later sample','expected_local_code':'Save false then send state packet; subsequent shielding callback returns true without sound. Client changes only if the packet reaches a matching mapped affix.'},
  {'condition':'client state packet arrives while world/entity/affix is unavailable','expected_local_code':'Handler has no pending replay structure; checks can skip application. setPacketHandled does not establish successful mode application.'}
 ],
 'application':'Boss拒控回执需绑定实际裁决原因；持续防护状态与每次拒绝音效分别管理。初始追踪应带当前状态，增量消息需绑定实体生命周期；不能用客户端粒子有无推断权威免疫，或把随机采样周期当状态持续时长。普通阴阳不新增灰字。只研究，不移植。',
 'counting':{'whole_candidate':1,'accepted_credit':0,'helper_or_variant_credit':0,'feedback_separate_credit':0,'migration_overlap_credit':0,'production_or_native_acceptance':0},
 'next_work':'Coordinator independently reads and decides whole-policy novelty, maximum1 or merge0. Do not change master ledger or rerun037 acceptance. Continue only existing original-program scope.'
}
out = H/'immune-reference-batch-039.json'
with out.open('x') as f:
    json.dump(doc,f,ensure_ascii=False,indent=2); f.write('\n')
print(json.dumps({'path':rel(out),'sha256':sha(out.read_bytes()),'files':len(refs),'lines':doc['cited_lines'],'maximum_pending':1},ensure_ascii=False))
