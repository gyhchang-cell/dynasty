#!/usr/bin/env python3
"""Save the actually read fixed-local PlayerRevive chain; no ledger mutation."""
import hashlib
import json
from pathlib import Path

ROOT = Path('/Users/a15356015027/Desktop/dynasty')
HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent
BASE = ROOT / 'tools/cod4/legacy-migration-acceptance/helpers/halley-migration/batch-045'
sha = lambda raw: hashlib.sha256(raw).hexdigest()

def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}

manifest_path = BASE / 'source-manifest.json'
manifest = next(x for x in json.loads(manifest_path.read_text()) if x['repo'] == 'CreativeMD/PlayerRevive')
purposes = {
    'PlayerRevive.java': 'Actual @Mod construction, Forge server/client event registration, capability and packet registration, permission-gated alternative revive command.',
    'PlayerReviveConfig.java': 'Complete defaults and separate client/server settings: initial damage grace, source categories, cooperative progress, optional item requirement and bleed-time pause.',
    'api/IBleeding.java': 'Full concrete state interface; INBTSerializable declaration alone does not establish disk recovery.',
    'api/CombatTrackerClone.java': 'Full original damage attribution snapshot and restoration immediately before terminal die call; not player Clone migration.',
    'api/event/PlayerBleedOutEvent.java': 'Actual pre-kill event declaration; no @Cancelable declaration in this class.',
    'api/event/PlayerRevivedEvent.java': 'Actual event declaration; misleading before-revive comment checked against real post-state-write call.',
    'cap/Bleeding.java': 'Full knockOut, helper-pruning tick, cooperative progress and bleed timer, revived/bledOut predicates, force terminal state and reset.',
    'client/ReviveEventClient.java': 'Full helper/victim overlay consumption and state exit, UUID lookup, client input denial and give-up timer. Audio/shader engine outcome unclaimed.',
    'client/TensionSound.java': 'Full sound wrapper: empty tick and protected stop; presentation support0, no sound-engine lifetime claim.',
    'mixin/PlayerMixin.java': 'Full state-qualified enemy visibility and push refusal hooks; no blanket invulnerability claim.',
    'mixin/ServerPlayerMixin.java': 'Full optional permission-level override; contextual0, not Dynasty policy.',
    'mixin/CombatTrackerAccessor.java': 'Full tracker field accessors used by snapshot/restore.',
    'mixin/LocalPlayerAccessor.java': 'Full handsBusy accessor used by client downed presentation and cleanup.',
    'mixin/MinecraftAccessor.java': 'Full missTime accessor used by client downed presentation.',
    'packet/GiveUpPacket.java': 'Complete server recheck and terminal dispatch; client hold duration not enforced by this receiver.',
    'packet/HelperPacket.java': 'Complete helper UI start/stop UUID state setter; no server action.',
    'packet/ReviveUpdatePacket.java': 'Complete server state snapshot and current-client-world UUID consumer, standing reset on nonbleeding state.',
    'server/PlayerReviveServer.java': 'Complete actual start, revive, kill, reset and remove-helper implementations, including asymmetric notifications.',
    'server/ReviveEventServer.java': 'Complete native death/hurt/tick/interact/logout/command listeners and actual capability attachment.',
}
refs = []
for entry in manifest['files']:
    up = entry['path']
    key = up.removeprefix('src/main/java/team/creative/playerrevive/')
    if key in purposes:
        purpose = purposes[key]
    elif up in ['gradle.properties', 'src/main/resources/playerrevive.mixins.json', 'src/main/resources/META-INF/mods.toml']:
        purpose = 'Full fixed revision version/dependency or actual mixin binding declaration; support0.'
    else:
        continue
    raw = (ROOT / entry['source']).read_bytes()
    refs.append({'path': entry['source'], 'upstream_path': up,
                 'lines': [1, len(raw.decode().splitlines())],
                 'file_sha256': sha(raw), 'git_blob_sha1': entry['source_blob'],
                 'purpose': purpose,
                 'reading_context': 'Full file actually read in bounded tool output during027, not inferred from the earlier migration review.'})

ledger_path = AUDIT / 'immune-feedback-research/reviewed.json'
ledger_raw = ledger_path.read_bytes()
ledger = json.loads(ledger_raw)
by_id = {x['id']: x for x in ledger}
distinctions = {
    'enigmatic-revive-self-delayed-world-ready-feedback': 'Old family owns local-world-readiness delayed revive feedback.027 is teammate-membership-driven downed release, not delayed event rendering; local overlays and packets are support0.',
    'vampirism-native-down-not-dead-refusal-and-control-state': 'Closest old family owns vampire eligibility, terminal-source exceptions and a self-countdown DBNO.027 generic first-death refusal alone would be duplicate0. Proposed distinction is external helper membership controlling both suspension of the terminal timer and additive release progress, with actual entry/removal and release-before-expiry arbitration. The entire cooperative downed mechanism is one proposal, never a second generic DBNO entry.',
    'vampirism-native-dbno-client-presentation-edge-and-authority-recheck': 'Old family owns attachment-driven DBNO opening edges and self-resurrection authority recheck.027 helper start state and victim UUID snapshots are independent inputs, and helper removal has asymmetric client teardown. These are supporting boundaries of cooperative state, not a separately counted UI/network family.',
    'relics-native-environment-leaf-budget-lethal-truncation-and-deferred-consumption': 'Old leaf environment budget reserves no resources and truncates immediate damage before deferred leaf operations.027 enters a continuing downed state, then live helper count controls both deadlines and release; not an environment resource threshold or scalar variant.',
    'goety-native-arca-qualified-death-refusal-teleport-result-not-checked': 'Old anchor/resource/lich eligibility cancels terminal death and attempts teleport.027 cooperative release depends on subsequent participant membership across ticks rather than an anchor or immediate resource payment. No teleport/payment success claim.',
    'goety-native-member-qualified-servant-death-cancel-with-wounded-rearm-exclusion': 'Old servant belongs to an external idol member set at death and wounds prevent rearm.027 helpers are active contributions after the target becomes downed, one helper switched between targets, with pausing countdown and accumulating progress. Both use membership, but the membership roles, time of use and final consumers differ. Not a species/config variant.',
    'occultism-native-target-uuid-support-success-gated-receipt-cooldown': 'Old support goal throttles accepted effect application per recipient UUID;027 does not use success-gated effect receipt or per-recipient cooldown. Helper UI shows a state snapshot, not successful healing/effect admission.',
    'icefire-cockatrice-native-group-stare-control-admission-versus-client-beam-target-cache': 'Old group count changes effect strength under mutual stare;027 group size integrates rescue progress and freezes a competing terminal countdown after death refusal. Generic group aggregation and visual target caching do not earn credit.',
    'icefire-native-scepter-bidirectional-target-membership-cleanup-and-release-accounting': 'Old two-sided caster/target IDs track channel attacks and deferred weapon wear.027 single target helper list controls recovery and bleed expiry, while client helper UUID is a separate acknowledgement. Asymmetric cleanup is a shared design hazard, not itself new credit.',
    'alexscaves-native-quorum-ritual-windup-versus-victim-owned-committed-capture-lifecycle': 'Old NPC quorum arms an independent victim timer and dismount does not necessarily cancel it.027 actual player helper count is re-used each target tick for continuous progress and bleed pause; helpers do not arm an independent future victim conversion. No claim helpers remain valid in all dimensions/conditions.',
}
comparisons = [{'accepted_id': k,
                'full_semantic_decision_read': {a:b for a,b in by_id[k].items() if a not in ['source_refs','auxiliary_refs']},
                'distinction': v} for k,v in distinctions.items()]
migration_path = AUDIT / 'legacy-migration-acceptance/reviewed.jsonl'
migration_raw = migration_path.read_bytes()
migration = [json.loads(x) for x in migration_raw.decode().splitlines() if x.strip()]
old = next(x for x in migration if x['candidate_id'] == '4d0e2e0a1891d4b6793b')
mkeys = ['candidate_id','status','family','trigger','input','output','preservation','application_limit','credit']

chain = [
 ('registration and real state producer', 'Actual @Mod common setup registers ReviveEventServer and all three packets; player AttachCapabilities provides LazyOptional<Bleeding>. HIGHEST LivingDeath on server requires active configuration (creative exception, singleplayer flag or published server) and non-bypass source. A first qualifying death removes the player from helper lists, sends helper-stop, calls knockOut via startBleeding, dismounts if needed, cancels death, adjusts hunger and health. knockOut initializes bleeding/progress/downedTime/timeLeft and saves source/tracker. Already-bleeding death clears current helpers and returns without cancelling; bypass sources skip this entire block. Native Forge listener composition is not verified.'),
 ('actual damage refusal while downed', 'LivingHurt first checks bleeding, then lets bypass sources through. Otherwise bledOut, downedTime <= initialDamageCooldown, and independently configured player/mob/other source categories can setCanceled(true). Initial grace is inclusive; flags do not form universal invulnerability. Nonbleeding helper damage optionally removes helper membership. Death/Hurt and active-check conditions differ; hurt listener has no isReviveActive condition. PlayerMixin visibility and optional push refusal read the same state. These generic predicates are support0 under the one cooperative mechanism.'),
 ('helper admission and membership transfer', 'Server EntityInteract targeting a bleeding player cancels the interaction. Optional required item checks helper main hand; first consumptive admission shrinks one unless creative, sets inventory changed and target itemConsumed. Once itemConsumed is true, later admissions still enter the else-if ingredient check, but do not shrink again. After these checks, removePlayerAsHelper removes the helper from every current server player list, then adds it to this target and sends HelperPacket(targetUUID,true). The handler itself has no explicit helper-alive/nonbleeding, distance, same-dimension or line-of-sight guard; native interaction pipeline constraints not expanded. Failed item check leaves old membership unchanged. Removal-before-add prevents ordinary repeated interaction from accumulating duplicate entries, not arbitrary API mutations.'),
 ('competing progress and bleed timer consumer', 'Server START PlayerTick requires active configuration and alive target, then ticks only bleeding state. Bleeding.tick forces swimming when current pose differs, removes helpers whose numeric distance is >maxDistance and sends stop to those helpers. It does not separately check level identity, alive, current held item, sustained button hold or current bleeding state. If no helpers OR haltBleedTime=false, decrement timeLeft; if none AND resetProgress=true, zero progress. Then add remaining helper count * progressPerPlayer, increment downedTime, and request configured helper food exhaustion. Parent sends snapshots every five downed ticks and applies configured effects/hunger before checking revived progress first, then bledOut. If both predicates true that tick, revive wins. Effects admission results ignored; progress does not depend on hunger payment success.'),
 ('authoritative release and terminal path', 'revive clears Bleeding state first, requests configured effects, resetPlayer sends stop to current helpers and clears list/PersistentData flag, syncs, writes healthAfter, requests revived sound, posts PlayerRevivedEvent, syncs again, releases forced pose. Event comment says before revived but actual call follows state/health writes. kill posts PlayerBleedOutEvent (not used as a returned veto), restores original combat snapshot, writes HP0, forceBledOut, calls die(saved/fallback source), clears helpers/flag with an intermediate snapshot, then clears Bleeding state and forced pose and sends final snapshot. Marking bleeding/time0 before die prevents its own first-death rescue branch from rearming. The native die result/cross-mod cancellation is not certified; reset occurs even if native death is intercepted. Logout bleeding calls kill; permission2 command directly revives bleeding targets. Optional upstream ban policy is read as context only and is never proposed for Dynasty.'),
 ('actual consumer and acknowledgement boundary', 'ReviveUpdatePacket snapshots target UUID and serialized timeLeft/progress/bleeding/consumed. Client execution looks up that UUID in current Minecraft level, drops absent target, deserializes into capability and forces STANDING if false. HelperPacket independently writes static helpActive/helpTarget. Registered RenderGuiOverlayEvent.Post consumer shows helper target time/progress if helper is not bleeding, helpActive, GUI visible, no screen and target UUID resolves. It does not test target.isBleeding or actual helper membership. Victim overlay reads own state, applies pose/handsBusy/missTime and local jump effect; on nonbleeding overlay it restores post effect, clears jump/handsBusy and explicitly stops owned sound. Low-level CreativeCore delivery, native graphics/shader/audio engine internals are not expanded; no visual/audio success claim.'),
 ('incomplete notification coverage is an observed chain property', 'removePlayerAsHelper only removes from server lists and sends no HelperPacket. Damage abort calls only that helper. Therefore under abortOnDamage=true, a removed helper can retain helpActive=true and a resolved old target overlay: later target reset iterates remaining helpers, so it does not notify the removed one. Distance pruning does send stop; switching targets sends a new start; first knockOut of the helper sends stop; target normal revive/kill sends stop to helpers still present. A bypass-source death skips the playerDied helper cleanup, and already-bleeding non-bypass death only clears helpers there, not all bleeding state. These are static branch observations, not runtime reproduced defects. No claim every death/logout/dimension change is covered.'),
 ('give-up and client lifecycle boundaries', 'Client END tick increments a local hold counter while bleeding and attack held; sends GiveUpPacket only when prior counter > seconds*20 then resets it. Server checks only sender bleeding before kill, not hold duration. Render callback has no per-overlay-type filter here, so do not infer one call per frame. Helper static fields have no disconnect/session reset in the complete local Java files; target lookup includes current world but packet carries no dimension/session/sequence and no queue. If player is null, render cleanup does not run; absence of a drawn target is not clearing helpActive. Audio TensionSound tick is empty, so owned sound stop must not be inferred from that wrapper alone. These are support limits, not extra UI/transport credits.'),
]
doc = {
 'schema_version': 1, 'owner': 'program-feedback-review-027',
 'repo': manifest['repo'], 'branch': manifest['branch'], 'commit': manifest['commit'],
 'provenance': {'manifest_path': str(manifest_path.relative_to(ROOT)), 'manifest_sha256': sha(manifest_path.read_bytes()),
                'bare_git_path': str((BASE/'upstream.git').relative_to(ROOT)), 'git_tree': manifest['git_tree'],
                'acquisition': 'Existing fixed local manifest and cached Git objects only; no download, checkout or upstream execution.'},
 'status': 'candidate_whole_cooperative_downed_release_chain_pending_independent_review',
 'research_credit': 0, 'maximum_proposed_credit': 1,
 'production_changes': False, 'runtime_executed': False,
 'semantic_family': 'playerrevive-native-helper-membership-pauses-terminal-bleed-clock-and-integrates-authoritative-release-with-asymmetric-helper-feedback-exit',
 'source_refs': refs,
 'dedup_snapshot': {'path': str(ledger_path.relative_to(ROOT)), 'sha256': sha(ledger_raw), 'rows': len(ledger),
                    'comparisons': comparisons,
                    'reading_order': 'Before any candidate source: six full nearest accepted death/DBNO decisions and full rejected PlayerRevive migration decision. After full source revealed continuous helper membership: four full group/membership/support decisions. No claim to rereading their old source files.',
                    'limits': 'One proposed whole cooperative state mechanism. First-death cancellation, timer arithmetic, packet wrappers, helper counts, source categories, overlays and cleanup defects cannot be split for credits. Independent novelty decision pending.'},
 'migration_overlap_screen': {'path': str(migration_path.relative_to(ROOT)), 'sha256': sha(migration_raw), 'rows': len(migration),
                              'comparisons': [{'accepted_id': old['candidate_id'], 'complete_semantic_decision_read': {k:old[k] for k in mkeys},
                                               'distinction': 'Existing migration rejection0 remains intact. Same fixed files now actually read for a current-session cooperative refusal/release mechanism. NBT sync, persistent flag and CombatTrackerClone do not become durable recovery or new migration credit.'}]},
 'full_chain': [{'stage':s, 'observation':o} for s,o in chain],
 'critical_boundaries': [
     'Candidate final mod-owned writes are event cancellation, state clear, health and forced-pose requests, reached from actual registered death/interact/tick/logout/command paths. No need to invent a missing native particle lifetime as in026; this family is authoritative cooperative state, not a new sound/particle rendering family.',
     'Only scoped original program research; no UI recheck, background/button edits, assets, model/building work, production source change, shared Jar, runtime/game/Java/Gradle, network acquisition, master ledger/session/active/checklist mutation or messages.',
     'Helpers are sampled by numeric distance only in this local tick; do not call them continuously valid, mutually consenting, same-dimension, alive or hunger-payment-qualified participants. Server event admission depends on external native constraints not read here.',
     'State snapshots and helper acknowledgement are separate packet streams. No transaction, initial tracking bootstrap, session identity, packet ordering or stale-helper healing guarantee.',
     'No source method, config option, default value, presentation wrapper or arithmetic example earns independent credit. Ten semantic comparators were actually read in full fields, not ten source implementations reread.',
     'Old migration rejection is unchanged; no disk read/Clone recovery evidence added. Source-tree/hash verification checks provenance only, not semantic acceptance or gameplay correctness.',
 ],
 'native_gaps': [
     {'missing': 'Exact CreativeCore2.11.20 packet serialization/transport and native Forge dispatch, interaction reach, cancel composition and engine death outcome.', 'impact': 'Actual mod registration and request/consumer implementations read; no transport guarantee or proof other listeners preserve cancellation/death.'},
     {'missing': 'Native Minecraft graphics/audio/shader/effect and pose lifecycle internals.', 'impact': 'Only mod-owned overlay consumer and explicit cleanup decisions observed; no rendered pixels, sound playback, successful status admission or complete native presentation lifetime claimed. Presentation is support0.'},
 ],
 'static_examples_not_executed_tests': [
     {'case': 'release wins on expiry tie', 'assumptions': 'Bleeding target; progress99/timeLeft1; one retained helper; progressPerPlayer1/required100/haltBleedTime=false.', 'derivation': 'tick makes progress100/time0. Parent revived() is checked before bledOut(), so this source calls revive, not kill.'},
     {'case': 'last helper leaves', 'assumptions': 'Only helper now distance>maxDistance; haltBleedTime=true/resetProgress=true.', 'derivation': 'Prune sends stop and removes helper first; time decreases and progress resets in the same target tick.'},
     {'case': 'damage abort stale helper display', 'assumptions': 'Nonbleeding helper, abortOnDamage=true, subscribed hurt callback reaches removal; client previously received help start; target remains resolvable.', 'derivation': 'Server membership removed without stop packet. Client overlay checks helpActive and target lookup, not membership/target bleeding. Later target reset excludes removed helper, so that path cannot clear its old UI state.'},
     {'case': 'consumed item is not free later admission', 'assumptions': 'needReviveItem=true/consumeReviveItem=true and target itemConsumed=true.', 'derivation': 'A later helper still must pass the else-if main-hand ingredient check, while no further shrink is performed in that branch.'},
 ],
 'application': 'Separate temporary refusal state, ongoing participant qualification, authoritative release and presentation acknowledgements. Every helper-removal path should have an explicit feedback exit when applicable. Boss Immune still requires a final actual control-refusal reason; this rescue system and its ordinary UI are not a Dynasty feature proposal or ordinary-constitution gray text.',
 'counting': {'formal_baseline_observed': len(ledger), 'current_credit': 0, 'whole_family_maximum': 1, 'helpers_variants_packets_migration_credit': 0},
 'next_work': ['Coordinator independently compare this whole cooperative family against the ten bound decisions and accept at most1 or reject0; no automatic ledger increment.', 'Keep026 held0, no renewed missing-particle acquisition; choose another fixed local program source for028 after saving this checkpoint.'],
}
path = HERE / 'immune-reference-batch-027.json'
with path.open('x') as stream:
    json.dump(doc, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'proposal': binding(path), 'source_files': len(refs), 'source_lines': sum(x['lines'][1] for x in refs), 'baseline':len(ledger), 'current_credit':0,'maximum_proposed_credit':1}, indent=2))
