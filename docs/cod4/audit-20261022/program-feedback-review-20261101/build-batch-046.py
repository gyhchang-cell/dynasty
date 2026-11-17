"""Fixed-local Roots nondetection whole-policy proposal; no upstream execution."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

R = Path('/Users/a15356015027/Desktop/dynasty')
H = Path(__file__).resolve().parent
A = H.parent
sha = lambda b: hashlib.sha256(b).hexdigest()
def ref(p):
    return {'path': str(p.relative_to(R)), 'sha256': sha(p.read_bytes())}
def seal(name, value):
    p = H / name
    with p.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')
    return ref(p)

prior_path = H / 'immune-reference-batch-044-screen.json'
assert ref(prior_path)['sha256'] == '95e9841e45b8898c88078f7dd55e42929d8c6afdeddddff35d83e74724146070'
prior = json.loads(prior_path.read_text())
provenance = prior['provenances'][0]
manifest_path = R / provenance['manifest_path']
assert ref(manifest_path)['sha256'] == provenance['manifest_sha256']
m = next(x for x in json.loads(manifest_path.read_text()) if x['repo'] == 'MysticMods/Roots')
assert m['commit'] == '27dc32ecf4dfffbc67790bc69ed0b405137dee2f'
entries = {x['path']: x for x in m['files']}
prefix = 'src/main/java/epicsquid/roots/'

def source(name, ranges=None, context='actual_read046'):
    e = entries[prefix + name]
    raw = (R / e['source']).read_bytes()
    assert sha(raw) == e['sourceSha256']
    lines = raw.decode().splitlines()
    result = []
    for a, b in ranges or [[1, len(lines)]]:
        assert 1 <= a <= b <= len(lines)
        result.append({'repo': m['repo'], 'commit': m['commit'], 'path': e['source'],
                       'upstream_path': e['path'], 'lines': [a, b], 'file_sha256': sha(raw),
                       'git_blob_sha1': e['source_blob'],
                       'range_text_sha256': sha('\n'.join(lines[a-1:b]).encode()),
                       'reading_context': context,
                       'purpose': 'One nondetection producer/visibility/target-assignment policy; whole methods and support, never per-file credit.'})
    return result

refs = source('spell/SpellExtension.java') + source('init/ModPotions.java')
refs += source('event/MappingsEvent.java', [[1, 40]])
new_refs = list(refs)
exploratory_reused = []
for x in prior['exploratory_reads']:
    if x['upstream_path'].endswith(('event/SneakHandler.java', 'potion/PotionNondetection.java')):
        y = dict(x)
        y.update(reading_context='044_full_exploratory_read_reused_and_reread046',
                 purpose='Now connected to full SpellExtension producer; unrelated quiver branch0.')
        exploratory_reused.append(y)
refs += exploratory_reused
support = {
    'Roots.java', 'RegistryManager.java', 'proxy/CommonProxy.java', 'spell/SpellRegistry.java',
    'item/ItemStaff.java', 'spell/info/StaffSpellInfo.java', 'spell/info/storage/StaffSpellStorage.java',
    'util/ServerHerbUtil.java', 'util/types/RegistryItem.java', 'spell/SpellBase.java',
    'modifiers/instance/staff/StaffModifierInstanceList.java',
    'modifiers/instance/staff/ModifierSnapshot.java', 'init/ModSounds.java', 'init/ModItems.java',
}
for x in prior['source_refs']:
    if x['upstream_path'].removeprefix(prefix) not in support:
        continue
    assert sha((R / x['path']).read_bytes()) == x['file_sha256']
    y = dict(x)
    y.update(reading_context='exact044_already_read_generic_producer_support_reused',
             purpose='Registration/staff/resource/cooldown/snapshot context0; prior complete-method reading retained.')
    refs.append(y)

ledger_path = A / 'immune-feedback-research/reviewed.json'
ledger_raw = ledger_path.read_bytes()
ledger = json.loads(ledger_raw)
index = {x['semantic_dedup_key']: x for x in ledger}
distinctions = {
    'wizardry-native-mindtrick-pre-admission-target-null-and-attack-attempt-release':
        'MindTrick targets the affected mob, clears immediately before potion admission and releases on attack attempt. Roots affects the protected player, only clears EntityMob on later target assignment, independently alters visibility using a conditionally refreshed player snapshot, and has no attack-release branch in its consumer. No shared Ray, target owner or immediate cast cleanup.',
    'reliquary-native-ambient-light-qualified-target-refusal-independent-of-invisibility':
        'Cloak uses current inventory/light for both target event and tick cleanup independently of visual invisibility. Roots uses a timed potion for assignment cleanup but a separate, possibly stale modifier snapshot for visibility0/999; no periodic cleanup, light lookup or cloak toggle.',
    'reliquary-native-charm-target-denial-cache-versus-kill-resource-receipt-lifecycle':
        'Charm uses type-specific inventory/pedestal eligibility, tick cache, brain reset and kill-consumption HUD. Roots has timed player potion plus conditional spell snapshot; no kill budget, per-type cache, brain clearing or target-refusal receipt.',
    'botania-native-persistent-ai-pacification-change-qualified-target-cue-and-reload-restore':
        'TigersEye rewrites Creeper goals persistently and only changed goal state pays/emits target cue. Roots does not edit goals or persist pacified mob state; assignment clears two fields while player potion exists, with no successful-denial packet.',
    'bumblezone-native-combat-revokes-offhand-pacification-and-target-clearing-budget':
        'CalmingEssence owns offhand budget, periodic scan and combat revocation. Roots has cast-once potion lifetime, no shown combat revoke and no periodic target scan; visibility reads a separate spell snapshot whose update is not coupled to nondetection application.',
}
cmps = []
for key, distinction in distinctions.items():
    row = index[key]
    cmps.append({'accepted_id': row['id'],
                 'complete_semantic_decision_read': {k: v for k, v in row.items() if k != 'source_refs'},
                 'distinction': distinction})
migration_path = A / 'legacy-migration-acceptance/reviewed.jsonl'
migration_raw = migration_path.read_bytes()
migration = {x['candidate_id']: x for x in map(json.loads, migration_raw.decode().splitlines())}
nine = ['candidate_id', 'status', 'family', 'trigger', 'input', 'output', 'preservation', 'application_limit', 'credit']
migration_cmps = []
for ident in ['30cdabca3ee13fdaf65f', 'd163d771f89ee9b86e84']:
    migration_cmps.append({'accepted_id': ident,
                          'complete_semantic_decision_read': {k: migration[ident][k] for k in nine},
                          'distinction': 'Existing owner covers pouch/staff migration and consumption/support; staff owner explicitly includes LightDrifter (044excluded). Neither saved judgment includes nondetection visibility/assignment split with conditional Extension snapshot. Shared staff storage, seven alias remaps, herb IO and MissingMappings are0 new credit; review whole policy separately, never re-award support.'})

accept_path = A / 'immune-feedback-research/coordinator-astral-vortex-acceptance-20261103.json'
accept = json.loads(accept_path.read_text())
review_path = R / accept['independent_review']['path']
assert ref(review_path)['sha256'] == '700994eddcd66865e80f9c1e1d9ea64bef17a5f548eab22370a577d1abcd32d6'
assert accept['after_count'] == len(ledger) == 477
assert sha(ledger_raw) == accept['after_ledger_sha256']
policy = 'roots-native-nondetection-target-assignment-denial-with-conditionally-refreshed-visibility-snapshot'
assert policy not in index
doc = {
    'schema_version': 1, 'owner': 'program-feedback-review-046',
    'created_utc': datetime.now(timezone.utc).isoformat(),
    'status': 'ONE_WHOLE_NONDETECTION_POLICY_PENDING_INDEPENDENT_REVIEW',
    'research_credit': 0, 'maximum_proposed_credit': 1,
    'repo': m['repo'], 'commit': m['commit'], 'semantic_dedup_key': policy,
    'provenances': [provenance], 'source_refs': refs,
    'prior_read_reuse': {'evidence': ref(prior_path), 'new_ranges': len(new_refs),
                        'new_cited_lines': sum(x['lines'][1]-x['lines'][0]+1 for x in new_refs),
                        'prior_exploratory_ranges_now_connected': len(exploratory_reused),
                        'generic_support_ranges': len(refs)-len(new_refs)-len(exploratory_reused),
                        'reread_credit': 0,
                        'reading_recovery': 'Initial oversized SpellExtension/search output clipped; complete95-225,226-410,411-420 recovered. Header1-94 was visible before clipping. Oversized ledger output excluded; five whole semantic judgments re-read without source-ref arrays. Mappings only1-40 claimed.'},
    'baseline': {'accepted045_receipt': ref(accept_path), 'accepted045_review': ref(review_path),
                 'formal_count_observed': 477, 'gap_to1000': 523,
                 'old476_complete_objects_unchanged': accept['old476_complete_objects_unchanged'],
                 'existing_ledger_verification': 'Coordinator PASS_ONCE reused; not rerun.',
                 'coordinator_additional045_scope': 'Coordinator43ranges/38files/31whole/3748lines; VortexContext32, DataTimeFreezeEffects181, TimeStopEffectHelper102-200 read by coordinator. Helper101 is not EOF and there is no missing-method defect. Supplement is not specialist new reading/credit; original045 sealed unchanged.'},
    'dedup_snapshot': {'path': str(ledger_path.relative_to(R)), 'sha256': sha(ledger_raw),
                       'rows': len(ledger), 'comparisons': cmps,
                       'scope': 'Five complete saved semantic judgments, not only titles/keywords; source arrays not re-reviewed here.'},
    'migration_overlap_screen': {'path': str(migration_path.relative_to(R)), 'sha256': sha(migration_raw),
                                'rows': len(migration), 'comparisons': migration_cmps,
                                'scope': 'Both closest complete nine-field Roots owner judgments read; generic support not new credit.'},
    'whole_chain_observation': [
        'Registered SpellExtension is INSTANTANEOUS, declared cooldown350, basewildroot0.450; NONDETECTION modifier adds moonglowleaf0.6. These are declared defaults; actual Property/config/cost modifiers may differ. Native ItemStaff right-click gates selected spell/cooldown/costs, calls cast, then noncreative server enacts costs and updates selected info. No transactional rollback of already-applied potion on cost failure. StaffSpellInfo.use stores cooldownTotal and stopTime; ordinary CastResult.modifyCooldown returns0 offset, NOT zero actual cooldown.',
        'Full SpellExtension.cast always attempts NIGHT_VISION, and if current StaffModifierInstanceList.has(NONDETECTION) attempts nondetection for configured night_vision duration (default800), amplifier0, ambientfalse, showParticlesfalse. Calls addPotionEffect without inspecting admission/result; cast returns true (also early success path for absent scanbox). No nearby old-target sweep or explicit effect replacement/removal in this producer.',
        'Only SENSE_ANIMALS or SENSE_DANGER branches write entityData[spell cached registry name] = info.toArray(). NONDETECTION alone and NONDETECTION+SENSE_PLANTS do not refresh this snapshot. getCachedName is registry ResourceLocation string roots:spell_extension. toArray includes only enabled/applied/nonconflicting cores; has() checks applied/enabled but not conflicts, so current branch choice and stored snapshot are not identical predicates. NONDETECTION.addConflict(SENSE_PLANTS) is commented, not an active prohibition.',
        'Snapshot reader requires INT_ARRAY; absent/wrong type returns empty ModifierSnapshot. Snapshot has() checks modifier core integer, no duration/session/caster/source generation. Within reviewed producer/consumers no snapshot expiry deletion. Conditional oldsnapshot→currentcast mismatch follows: old SENSE_PLANTS saved through animals/danger may cause999 even later nondetection cast omits plants; fresh nondetection+plants without animal/danger can produce0. This is source-level state analysis, not an executed reproduction or claim of client synchronization.',
        'SneakHandler native PlayerEvent.Visibility, default priority, first requires nondetection currently active; then snapshot SENSE_PLANTS submits modifyVisibility(999), otherwise modifyVisibility(0). It does not consult actual held staff, current info.has, movement/sneak or light. External Forge aggregation/AI consumers not read, so these are submitted modifiers, not a guaranteed final visibility/detection radius or actual mob acquisition outcome.',
        'Separate native LivingSetAttackTargetEvent LOWEST requires target EntityPlayer and attacker EntityMob. If player currently has nondetection, attacker.setRevengeTarget(null) then direct attacker.attackTarget=null, independently of snapshot, plants, visibility value, distance, damage, owner or source. No event cancel or success return, no explicit side guard, no boss-specific gate. This does not necessarily affect non-EntityMob living entities or AI using other memory/direct damage paths.',
        'Target consumer is assignment-triggered only: application does not clear pre-existing targets immediately, and shown class has no periodic target cleanup. No shown attacking-player/potion-revoke branch. Once effect absent, both hooks skip their own intervention; no restoration of previous revenge/attack target or proactive reacquisition exists here. Potion expiration, cure, death/clone/save/relogin and external target assignment ordering are native/unexpanded, not proven lifecycle restores.',
        'PotionNondetection is beneficial, always isReady true but defines no performEffect override; shouldRender true and statusIcon index(1,2) uses roots potion atlas. Producer suppresses potion particles, does not set invisible/disableDamage. This is potion icon intent, not pixel evidence, actual damage immunity or successful AI rejection receipt. ModPotions binds roots:nondetection; MissingMappings maps old roots:invulnerability to it, which does not imply current damage immunity. Rename is support0.',
        'Generic SpellBase.cast on successful cast at initial tick may submit configured Extension sound server-side, independently of any mob assignment or actual potion admission. SneakHandler denial branches send no target-result packet/text/particles and have no per-target feedback throttle. Other cast branches can send home/resource-location SenseFX to caster; these are observation search results, not nondetection acceptance or refusal receipt. Their renderer is outside this policy.',
        'Nondetection duration and player entityData modifier snapshot have separate lifetimes and update conditions. Event consumer reads active potion plus optional snapshot each call; it never owns a particular hostile caster/entity identity or a persistent mob pacification state. No source-leases, generation IDs, acknowledgments or shared-target arbitration in these handlers. Other event handlers can later alter fields/visibility; LOWEST registration does not prove final global arbitration.',
        'Herb server submission and selected-spell cooldown are shared preexisting support. Existing migration pouch/staff owners retain that credit. This candidate proposes at most one whole dual-consumer control policy with conditional snapshot lifetime, not separate credits for two events, modifiers, potion icon, registration, old-ID remap, resource payment or snapshot case.'
    ],
    'critical_boundaries': [
        'Fixed Roots1.12.2 commit only. No external acquisition, Forge/native engine execution, network delivery, game startup, source compilation, texture generation, pixel/sound QA or current Dynasty behavior proof.',
        'No damage immunity established by old name invulnerability, beneficial potion, status icon, visibility0, spell returntrue or successful herb payment.',
        'Other sensing branches fully read as containing cast context but not separate research; no full native AABB/ore/packet consumer claims. Sanctuary remains exploratory0 and is not proposed.',
        'No production code/test/asset/Jar/instance changes, no main session/ledger/pending edits, no task deletion or hours claim. Applicable accepted1000 gate remains unmet.',
        'Native potion lifecycle, Forge visibility multiplication/clamping and LivingSetAttackTarget dispatch/reentrancy not expanded. Conditional snapshot analysis must not be promoted to a runtime exploit or universal Boss protection.'
    ],
    'application': 'Boss免控反馈应由实际拒控入口给出，不能以药水图标、施法成功或可见度替代。若多个控制入口共享资格快照，更新与失效须有同一明确版本，旧快照不应改变当前提示；原普通阴阳type9不增加灰字。只研究，不移植。',
    'counting': {'whole_policies_proposed': 1, 'accepted_credit': 0, 'native_acceptance': 0},
    'next_work': 'Independent whole-policy review and semantic overlap decision; continue different original-program source mechanism without waiting for repeated dispatch.',
    'production_changes': False, 'runtime_executed': False, 'network_requests': 0,
    'master_changes': False, 'checklist_deletions': 0, 'hours_claimed': 0,
}
covered = {}
for x in refs:
    a, b = x['lines']
    now = set(range(a, b+1))
    previous = covered.setdefault(x['path'], set())
    assert not now.intersection(previous)
    previous.update(now)
doc.update(source_ranges=len(refs), unique_files=len(covered),
           full_files=sum(len(v) == len((R/k).read_text().splitlines()) for k, v in covered.items()),
           cited_lines=sum(map(len, covered.values())))
result = seal('immune-reference-batch-046.json', doc)
print(json.dumps({'evidence': result, 'ranges': len(refs), 'files': doc['unique_files'],
                  'lines': doc['cited_lines'], 'credit': 0, 'maximum_pending': 1}, ensure_ascii=False))
